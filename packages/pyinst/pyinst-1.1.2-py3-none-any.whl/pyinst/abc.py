"""
This module provides abstract base classes to describe different kinds of 
instruments.

`BaseInstrument` is the base class of all the Instrument Model classes. 
`VisaInstrument` and `RawSerialInstrument` are classes based on 
`BaseInstrument` to describe VISA compatible instruments and serial-port based 
instruments.

There are many other abstract classes to describe a kind of instrument that 
has some particular functions. For example, `OpticalFrequencySetter` defines 
the interfaces of an instrument which has optical frequency/wavelength 
setting function.

Among these ABCs are *Instrument Type* classes. An *Instrument Type* class 
defines the interfaces of a specific instrument type. It always starts with 
a prefix `Type`, for example, `TypeVOA` or `TypeOPM`.

An *Instrument Model* class will inherit at least one of these *Instrument 
Type* classes, and implement the abstract methods inherited. So the 
interfaces of the same type of instruments can be unified.

Besides the standard methods defined by the *Instrument Type* class, a 
*Instrument Model* class may also define its unique methods.
"""
from __future__ import annotations
from typing_extensions import Self
from abc import ABC, abstractmethod, ABCMeta
from typing import Any, Callable, Iterable, Sequence, Tuple, Optional, \
    Mapping, List, Type
import time

import pyvisa
import serial

from .constants import (
    LIGHTSPEED, VI_READ_TERMINATION, VI_WRITE_TERMINATION, VI_OPEN_TIMEOUT, 
    VI_TIMEOUT, VI_QUERY_DELAY,
    SERIAL_READ_TERMINATION, SERIAL_WRITE_TERMINATION, SERIAL_QUERY_DELAY, 
    SERIAL_READ_TIMEOUT, SERIAL_WRITE_TIMEOUT,
    InstrumentType, TemperatureSourceType, TemperatureUnit, OpticalPowerUnit, 
    OpticalBandwidthUnit, SerialByteSize, SerialParity, SerialStopBits)
from .errors import InstrIOError
from .utils import bw_in_ghz_to_nm, bw_in_nm_to_ghz, w_to_dbm, dbm_to_w


class InstrumentMeta(ABCMeta):
    """The meta class of BaseInstrument."""

    @property
    def ins_type(cls: type) -> InstrumentType:
        """The instrument type flag of the specific instrument model."""
        value = 0
        for base in cls.mro()[2:]:
            value |= getattr(base, 'ins_type', 0)
        return value


class BaseInstrument(metaclass=InstrumentMeta):
    """ABC of all the instrument model classes."""

    brand = None
    """The brand/manufactory of the instrument."""

    model = None
    """The model name of the instrument."""
    
    details = {}
    """A map of information to describe the instrument."""

    params = []
    """
    A list of dict to define parameters required for object creation.

    This is mainly used for upper level (e.g. GUI) to render options.

    dict fields:

    - `name (str)`: Required. The name of the param, exactly the same in 
    `__init__` method.

    - `type (str)`: Required. options: `int` | `str` | `bool`.

    - `options (list)`: Optional. Valid options.

    + `min (int)`: Optional. For type `int` only.

    + `max (int)`: Optional. For type `int` only.
    
    Examples:
    ``` python
    [
        {
        "name": "slot",
        "type": "int",
        "min": 1,
        "max": 10
        },
        {
            "name": "range_level",
            "type": "str",
            "options": ["HIGH", "LOW"]
        }
    ]
    ```
    """

    def __init__(self, resource_name: str):
        """
        Args:
            resource_name: The instrument resource name. Please refer to 
                `resource_name` property for more information.
        """
        self.__resource_name = resource_name
        super(BaseInstrument, self).__init__()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__!r}({self.resource_name!r})>"

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @abstractmethod
    def close(self) -> None:
        """Release the instrument resource."""

    @property
    def resource_name(self) -> str:
        """
        - For VISA compatible instruments, it is the resource name or alias of 
        the VISA resource.
        - For other instruments connected with serial port, it is the port 
        name.
        - For other instruments connected with USB, it is the S/N of the 
        instrument or USB chip.
        """
        return self.__resource_name
    
    @abstractmethod
    def _check_communication(self) -> None:
        """Check if the connection is OK and able to communicate.
        
        Sometimes, the communication port of an instrument is open does not 
        mean the communication is OK. 

        For example, a raw serial com-port can be opened even if there is 
        nothing connected to it. So this method should be used to check if 
        the communication is working well. If the communication check failed, 
        an `InstrIOError` will be raised.

        This method should be performed at the end of the `__init__` method 
        of the specific Instrument Model classes.
        
        Raises:
            [InstrIOError][pyinst.errors.InstrIOError]
        """

    @classmethod
    def create(cls, *args: Any, **kwargs: Any) -> Optional[Self]:
        """Create an instance of the instrument model. If an exception is 
        raised during the instance creation, return None.
        
        Args:
            *args: Directly passed to the `__init__` method.
            **kwargs: Directly passed to the `__init__` method.

        Returns:
            The created instrument model instance, or None if the creation failed.
        """
        try:
            instance = cls(*args, **kwargs)
        except:
            instance = None
        return instance


class VisaInstrument(BaseInstrument):
    """Base class of VISA compatible instruments that use message based 
    communication.

    VisaInstrument creates a proxy object with `pyvisa` to communicate with 
    VISA compatible instruments.

    Refer to [PyVISA Documents](https://pyvisa.readthedocs.io/en/latest/index.html) 
    for more information.
    """

    def __init__(
            self, 
            resource_name: str, 
            read_termination: str = VI_READ_TERMINATION, 
            write_termination: str = VI_WRITE_TERMINATION, 
            timeout: int = VI_TIMEOUT, 
            open_timeout: int = VI_OPEN_TIMEOUT, 
            query_delay: float = VI_QUERY_DELAY, 
            encoding: str = "ascii",
            **kwargs: Any
        ):
        """
        Args:
            resource_name: Resource name or alias of the VISA resource to open.
            read_termination: Read termination character.
            write_termination: Write termination character.
            timeout: Timeout in milliseconds for all resource I/O operations.
            open_timeout: If the access_mode parameter requests a lock, then this 
                parameter specifies the absolute time period (in milliseconds) 
                that the resource waits to get unlocked before this operation 
                returns an error.
            query_delay: Delay in seconds between write and read operations.
            encoding: Encoding used for read and write operations.
            **kwargs: Directly passed to `rm.open_resource`.
        """
        super().__init__(resource_name=resource_name)
        rm = pyvisa.ResourceManager()
        self._inst: pyvisa.resources.MessageBasedResource = rm.open_resource(
            resource_name, read_termination=read_termination, 
            write_termination=write_termination, open_timeout=open_timeout, 
            timeout=timeout, query_delay=query_delay, encoding=encoding, **kwargs)
        self._check_communication()

    @property
    def resource_info(self) -> pyvisa.highlevel.ResourceInfo:
        """Get the (extended) information of the VISA resource."""
        return self._inst.resource_info

    @property
    def idn(self) -> str:
        """Returns a string that uniquely identifies the instrument."""
        return self.query('*IDN?')

    @property
    def opc(self) -> str:
        """Operation complete query."""
        return self.query('*OPC?')

    def close(self) -> None:
        """
        Closes the VISA session and marks the handle as invalid.
        """
        self._inst.close()

    def _check_communication(self) -> None:
        """Check if the connection is OK and able to communicate.

        Raises:
            [InstrIOError][pyinst.errors.InstrIOError]
        """
        try:
            idn = self.idn
            if not idn:
                raise ValueError("Empty IDN.")
        except pyvisa.VisaIOError as e:
            raise InstrIOError("Check communication failed.")

    def command(self, message: str) -> int:
        """
        Write a VISA command without read back.

        Alias of write(message).

        Args:
            message: The message to be sent.
        
        Returns:
            Number of bytes written.
        """
        return self.write(message)

    def write(
        self,
        message: str,
        termination: Optional[str] = None,
        encoding: Optional[str] = None,
    ) -> int:
        """Write a string message to the device.

        The write_termination is always appended to it.

        Args:
            message: The message to be sent.
            termination: Alternative character termination to use. If None, 
                the value of write_termination passed to `__init__` method is 
                used. Defaults to None.
            encoding: Alternative encoding to use to turn str into bytes. If 
                None, the value of encoding passed to `__init__` method is 
                used. Defaults to None.

        Returns:
            Number of bytes written.
        """
        return self._inst.write(message, termination, encoding)

    def read(
        self, termination: Optional[str] = None, encoding: Optional[str] = None
    ) -> str:
        """Read a string from the device.

        Reading stops when the device stops sending (e.g. by setting
        appropriate bus lines), or the termination characters sequence was
        detected.  Attention: Only the last character of the termination
        characters is really used to stop reading, however, the whole sequence
        is compared to the ending of the read string message.  If they don't
        match, a warning is issued.

        Args:
            termination: Alternative character termination to use. If None, 
                the value of write_termination passed to `__init__` method is 
                used. Defaults to None.
            encoding: Alternative encoding to use to turn bytes into str. If 
                None, the value of encoding passed to `__init__` method is 
                used. Defaults to None.

        Returns:
            Message read from the instrument and decoded.
        """
        return self._inst.read(termination, encoding)

    def query(self, message: str, delay: Optional[float] = None) -> str:
        """A combination of write(message) and read()

        Args:
            message: The message to send.
            delay: Delay in seconds between write and read operations. If 
                None, defaults to query_delay passed to `__init__` method.

        Returns:
            Answer from the device.

        """
        return self._inst.query(message, delay)

    def read_binary_values(
        self,
        datatype: pyvisa.util.BINARY_DATATYPES = "f",
        is_big_endian: bool = False,
        container: Type | Callable[[Iterable], Sequence] = list,
        header_fmt: pyvisa.util.BINARY_HEADERS = "ieee",
        expect_termination: bool = True,
        data_points: int = 0,
        chunk_size: Optional[int] = None,
    ) -> Sequence[int | float]:
        """Read values from the device in binary format returning an iterable
        of values.

        Args:
            datatype: Format string for a single element. See struct module. 
                'f' by default.
            is_big_endian: Are the data in big or little endian order. 
                Defaults to False.
            container: Container type to use for the output data. Possible 
                values are: list, tuple, np.ndarray, etc, Default to list.
            header_fmt: Format of the header prefixing the data. Defaults to 
                'ieee'.
            expect_termination: When set to False, the expected length of the 
                binary values block does not account for the final termination 
                character (the read termination). Defaults to True.
            data_points: Number of points expected in the block. This is used 
                only if the instrument does not report it itself. This will be 
                converted in a number of bytes based on the datatype. Defaults 
                to 0.
            chunk_size: Size of the chunks to read from the device. Using 
                larger chunks may be faster for large amount of data.

        Returns:
            Data read from the device.
        """
        return self._inst.read_binary_values(
            datatype, is_big_endian, container, header_fmt, 
            expect_termination, data_points, chunk_size)

    def query_binary_values(
        self,
        message: str,
        datatype: pyvisa.util.BINARY_DATATYPES = "f",
        is_big_endian: bool = False,
        container: Type | Callable[[Iterable], Sequence] = list,
        delay: Optional[float] = None,
        header_fmt: pyvisa.util.BINARY_HEADERS = "ieee",
        expect_termination: bool = True,
        data_points: int = 0,
        chunk_size: Optional[int] = None,
    ) -> Sequence[int | float]:
        """Query the device for values in binary format returning an iterable
        of values.

        Args:
            message: The message to send.
            datatype: Format string for a single element. See struct module. 
                'f' by default.
            is_big_endian: Are the data in big or little endian order. 
                Defaults to False.
            container: Container type to use for the output data. Possible 
                values are: list, tuple, np.ndarray, etc, Default to list.
            delay: Delay in seconds between write and read operations. If 
                None, defaults to query_delay passed to `__init__` method.
            header_fmt: Format of the header prefixing the data. Defaults to 
                'ieee'.
            expect_termination: When set to False, the expected length of the 
                binary values block does not account for the final termination 
                character (the read termination). Defaults to True.
            data_points: Number of points expected in the block. This is used 
                only if the instrument does not report it itself. This will be 
                converted in a number of bytes based on the datatype. Defaults 
                to 0.
            chunk_size: Size of the chunks to read from the device. Using 
                larger chunks may be faster for large amount of data.

        Returns:
            Data read from the device.

        """
        return self._inst.query_binary_values(
            message, datatype, is_big_endian, container, delay, 
            header_fmt, expect_termination, data_points, chunk_size)

    def set_visa_attribute(
        self, name: pyvisa.constants.ResourceAttribute, state: Any
    ) -> pyvisa.constants.StatusCode:
        """Set the state of an attribute in this resource.

        One should prefer the dedicated descriptor for often used attributes
        since those perform checks and automatic conversion on the value.

        Args:
            name: Attribute for which the state is to be modified.
            state: The state of the attribute to be set for the specified object.

        Returns:
            Return value of the library call.
        """
        return self._inst.set_visa_attribute(name, state)

    def get_visa_attribute(self, name: pyvisa.constants.ResourceAttribute) -> Any:
        """Retrieves the state of an attribute in this resource.

        One should prefer the dedicated descriptor for often used attributes
        since those perform checks and automatic conversion on the value.

        Args:
            name: Resource attribute for which the state query is made.

        Returns:
            The state of the queried attribute for a specified resource.
        """
        return self._inst.get_visa_attribute(name)


class RawSerialInstrument(BaseInstrument):
    """Instrument based on raw serial communication.

    Compared to VISA compatible instruments, SerialRawInstrument do not have a 
    common application architecture. It depends on the manufactory.

    SerialRawInstrument creates a proxy object using pySerial to communicate 
    with instruments.

    Refer to [pySerial Documents](https://pythonhosted.org/pyserial/index.html) 
    for more information.
    """
    def __init__(
            self, 
            resource_name: str, 
            baudrate: int,
            bytesize: SerialByteSize = SerialByteSize.EIGHTBITS,
            parity: SerialParity = SerialParity.NONE,
            stopbits: SerialStopBits = SerialStopBits.ONE,
            read_termination: str = SERIAL_READ_TERMINATION, 
            write_termination: str = SERIAL_WRITE_TERMINATION, 
            read_timeout: int = SERIAL_READ_TIMEOUT, 
            write_timeout: int = SERIAL_WRITE_TIMEOUT,
            query_delay: float = SERIAL_QUERY_DELAY, 
            encoding: str = "ascii",
            **kwargs
        ):
        """
        Args:
            resource_name: Serial port name.
            baudrate: Baud rate such as 9600 or 115200 etc..
            bytesize: Number of data bits.
            parity: Parity checking.
            stopbits: Number of stop bits.
            read_termination: Read termination character.
            write_termination: Write termination character.
            read_timeout: Timeout in milliseconds for read operations.
            write_timeout: Timeout in milliseconds for write operations.
            query_delay: Delay in seconds between write and read operations.
            encoding: Encoding used for read and write operations.
        """
        __serial = serial.Serial(
            port=resource_name,
            baudrate=baudrate,
            bytesize=bytesize.value,
            parity=parity.value,
            stopbits=stopbits.value,
            timeout=read_timeout,
            write_timeout=write_timeout,
        )

        self.__serial = __serial
        self.__read_termination = read_termination
        self.__write_termination = write_termination
        self.__encoding = encoding
        self.__query_delay = query_delay

        super().__init__(resource_name=resource_name)

    @property
    def _serial(self) -> serial.Serial:
        return self.__serial
    
    def close(self) -> None:
        """Close the serial port immediately."""
        self.__serial.close()

    def command(self, message: str) -> int:
        """
        Write a serial command without read back.

        Alias of write(message).

        Args:
            message: message to be sent.
        
        Returns:
            Number of bytes written.
        """
        return self.write(message)

    def write(
        self,
        message: str,
        termination: Optional[str] = None,
        encoding: Optional[str] = None,
    ) -> int:
        """Write a string message to the device.

        The write_termination is always appended to it.

        Args:
            message: message to be sent.
            termination: Alternative character termination to use. If None, 
                the value of write_termination passed to `__init__` method is 
                used. Defaults to None.
            encoding: Alternative encoding to use to turn str into bytes. If 
                None, the value of encoding passed to `__init__` method is 
                used. Defaults to None.

        Returns:
            Number of bytes written.
        """
        tx_str = '{message}{term}'.format(
            message=message,
            term=termination or self.__write_termination
        )
        tx_bytes = tx_str.encode(encoding or self.__encoding)
        # clear input buffer so the data buffered before command is cleared
        self.__serial.reset_input_buffer()
        return self.__serial.write(tx_bytes)

    def read(
        self, termination: Optional[str] = None, encoding: Optional[str] = None
    ) -> str:
        """Read a string from the device.

        Reading stops when the device stops sending, or the termination characters sequence was
        detected.

        Args:
            termination: Alternative character termination to use. If None, 
                the value of write_termination passed to `__init__` method is 
                used. Defaults to None.
            encoding: Alternative encoding to use to turn bytes into str. If 
                None, the value of encoding passed to `__init__` method is 
                used. Defaults to None.

        Returns:
            Message read from the instrument and decoded.
        """
        buffer = bytes()
        term = termination or self.__read_termination
        encoding = encoding or self.__encoding

        while True:
            rx = self.__serial.read()
            if not rx:
                raise InstrIOError('Timeout before read_termination received.')
            
            buffer += rx
            if buffer.endswith(term.encode(encoding)):
                break
        
        return buffer.decode(encoding).rstrip(term)
          
    def query(self, message: str, delay: Optional[float] = None) -> str:
        """A combination of write(message) and read()

        Args:
            message: The message to send.
            delay: Delay in seconds between write and read operations. If 
                None, defaults to query_delay passed to `__init__` method.

        Returns:
            Answer from the device.

        """
        self.write(message)
        time.sleep(delay or self.__query_delay)
        return self.read()


class OpticalFrequencySetter(ABC):
    """Instrument with optical frequency/wavelength setting."""

    @property
    @abstractmethod
    def min_frequency(self) -> float:
        """The minimum settable optical frequency value in THz."""
        return LIGHTSPEED/self.max_wavelength
    
    @property
    @abstractmethod
    def max_frequency(self) -> float:
        """The maximum settable optical frequency value in THz."""
        return LIGHTSPEED/self.min_wavelength
    
    @property
    @abstractmethod
    def min_wavelength(self) -> float:
        """The minimum settable optical wavelength value in nm."""
        return LIGHTSPEED/self.max_frequency
    
    @property
    @abstractmethod
    def max_wavelength(self) -> float:
        """The maximum settable optical wavelength value in nm."""
        return LIGHTSPEED/self.min_frequency

    @abstractmethod
    def get_frequency(self) -> float:
        """
        Queries the optical frequency setting of the instrument in THz.

        Returns:
            The optical frequency setting value in THz.
        """
        return round(LIGHTSPEED/self.get_wavelength(), 6)

    @abstractmethod
    def set_frequency(self, frequency: int | float) -> None:
        """Set optical frequency.

        Args:
            frequency: The optical frequency setting in THz.
        """
        wavelength = round(LIGHTSPEED/frequency, 6)
        self.set_wavelength(wavelength)

    @abstractmethod
    def get_wavelength(self) -> float:
        """Queries the optical wavelength setting of the instrument in nm.

        Returns:
            The optical wavelength setting value in nm.
        """
        return round(LIGHTSPEED/self.get_frequency(), 6)
        
    @abstractmethod
    def set_wavelength(self, wavelength: int | float) -> None:
        """Set optical wavelength.

        Args:
            wavelength: The optical wavelength setting in nm.
        """
        frequency = round(LIGHTSPEED/wavelength, 6)
        self.set_frequency(frequency)


class TypeOPM(OpticalFrequencySetter):
    """ABC to define the interfaces of an Optical Power Meter."""
    
    ins_type = InstrumentType.OPM

    @property
    @abstractmethod
    def min_avg_time(self) -> float:
        """The minimum averaging time in ms."""

    @property
    @abstractmethod
    def max_avg_time(self) -> float:
        """The maximum averaging time in ms."""

    @property
    @abstractmethod
    def min_pow_cal(self) -> float:
        """The minimum power calibration value in dB."""

    @property
    @abstractmethod
    def max_pow_cal(self) -> float:
        """The maximum power calibration value in dB."""

    @abstractmethod
    def get_power_value(self) -> float:
        """Fetch the value of measured optical power in current unit setting.

        The measured value includes the power calibration.

        Measured value (dBm) = the actual measured value (dBm) + power calibration (dB)

        Refer to `get_pow_cal` and `set_pow_cal` to operate with the power calibration.

        Note:
            It is possible that some OPM models defined the power calibration 
            opposite in sign, but it is normalized in pyinst. Please refer to 
            the math function above.

        Returns:
            The value of the optical power.
        """

    @abstractmethod
    def get_power_unit(self) -> OpticalPowerUnit:
        """Get optical power unit setting.

        Returns:
            The unit of the optical power.
        """

    @abstractmethod
    def set_power_unit(self, unit: OpticalPowerUnit) -> None:
        """Set the unit of optical power.

        Args:
            unit: The unit of the optical power.
        """

    def get_power(self) -> Tuple[float, OpticalPowerUnit]:
        """Queries the measured optical power value and unit.

        Returns:
            value: The value of the optical power.
            unit: The unit of the optical power.
        """
        return self.get_power_value(), self.get_power_unit()

    def get_dbm_value(self) -> float:
        """Returns the optical power value measured in dBm.

        If the power unit setting is W, a math conversion will be 
        performed.

        Returns:
            The value of the optical power in dBm.
        """
        unit = self.get_power_unit()
        value = self.get_power_value()
        if unit == OpticalPowerUnit.DBM:
            return value
        else:
            return w_to_dbm(value)

    def get_w_value(self) -> float:
        """Returns the optical power value measured in W.

        If the power unit setting is dBm, a math conversion will be 
        performed.

        Returns:
            The value of the optical power in W.
        """
        unit = self.get_power_unit()
        value = self.get_power_value()
        if unit == OpticalPowerUnit.W:
            return value
        else:
            return dbm_to_w(value)

    @abstractmethod
    def get_pow_cal(self) -> float:
        """
        Get the power calibration offset in dB.

        Returns:
            The power calibration offset in dB.
        """

    @abstractmethod
    def set_pow_cal(self, value: int | float) -> None:
        """
        Set the power calibration offset in dB.

        Args:
            value: The power calibration offset in dB.
        """

    @abstractmethod
    def get_avg_time(self) -> float:
        """
        Get the averaging time in ms.

        Returns:
            The averaging time in ms.
        """

    @abstractmethod
    def set_avg_time(self, value: int | float) -> None:
        """
        Set the averaging time in ms.

        Args:
            value: The averaging time in ms.
        """


class TypeVOA(OpticalFrequencySetter):
    """
    ABC to define the interfaces of a Variable Optical Attenuator.
    """

    ins_type = InstrumentType.VOA
    
    @property
    @abstractmethod
    def min_att(self) -> float:
        """Minimum settable attenuation in dB.

        The minimum settable attenuation = 0 dB + the optical attenuation 
        offset value.
        """

    @property
    @abstractmethod
    def max_att(self) -> float:
        """Maximum settable attenuation in dB.

        The maximum settable attenuation = The maximum attenuation + the 
        optical attenuation offset value.
        """

    @property
    @abstractmethod
    def min_att_offset(self) -> float:
        """Minimum attenuation offset value in dB."""

    @property
    @abstractmethod
    def max_att_offset(self) -> float:
        """Maximum attenuation offset value in dB."""

    @abstractmethod
    def enable(self, en: bool = True) -> None:
        """
        Enable (disable) the optical output.
        
        Args:
            en: True = Enable, False = Disable.
        """

    @abstractmethod
    def disable(self) -> None:
        """Disable the optical output."""

    @abstractmethod
    def is_enabled(self) -> bool:
        """
        Returns:
            Whether the optical output is enabled.
        """

    @abstractmethod
    def get_att(self) -> float:
        """
        Get the current attenuation value in dB.
        
        Includes the attenuation offset.

        Queried attenuator = the actual attenuator value + attenuator offset

        Use `get_att_offset` and `set_att_offset` to operate with the 
        attenuator offset.

        Note:
            It is possible that some VOA models defined the attenuation offset 
            opposite in sign. But it is normalized in pyinst to align with the 
            math function above.

        Returns:
            The attenuation value in dB.
        """

    @abstractmethod
    def set_att(self, att: int | float) -> None:
        """
        Set attenuation value in dB.

        Includes the attenuation offset. Refer to `get_att` for more 
        information.

        Args:
            att: The attenuation value in dB.
        """

    @abstractmethod
    def get_att_offset(self) -> float:
        """
        Get the attenuation offset value in dB.

        Returns:
            The attenuation offset in dB.
        """

    @abstractmethod
    def set_att_offset(self, offset: int | float) -> None:
        """
        Set the attenuation offset value in dB.

        Args:
            offset: The attenuation offset in dB.
        """
 

class TypeOMA(OpticalFrequencySetter):
    """ABC to define the interfaces of an Optical Modulation Analyzer.

    The operating logic is different between vendors/models, so limited 
    methods are defined here.
    """

    ins_type = InstrumentType.OMA

    @abstractmethod
    def run(self, _run: bool = True) -> None:
        """
        Run (or stop) OMA.

        Args:
            _run: True = run, False = stop.
        """

    @abstractmethod
    def stop(self) -> None:
        """Stop OMA."""


class TypeOSA(OpticalFrequencySetter):
    """ABC to define the interfaces of an Optical Spectrum Analyzer.

    The operating logic is different between vendors/models, so no common 
    methods are defined here.
    """

    ins_type = InstrumentType.OSA

    @abstractmethod
    def run(self, _run: bool = True) -> None:
        """
        Start repeat sweep.

        Args:
            _run: True = run, False = stop.
        """

    @abstractmethod
    def stop(self) -> None:
        """Stop sweep."""

    @abstractmethod
    def single(self) -> None:
        """Perform single sweep."""

    @abstractmethod
    def get_osnr(self) -> float:
        """Get the measured OSNR in dB.
        
        Returns:
            The OSNR value in dB.
        """


class TypeWM(ABC):
    """
    ABC to define the interfaces of an Optical Wavelength Meter.
    """

    ins_type = InstrumentType.WM

    @abstractmethod
    def get_frequency(self) -> float:
        """
        Queries the measured optical frequency in THz.

        Returns:
            The measured optical frequency value.
        """
        return round(LIGHTSPEED/self.get_wavelength(), 6)

    @abstractmethod
    def get_wavelength(self) -> float:
        """Queries the mearured optical wavelength in nm.

        Returns:
            The measured optical wavelength value.
        """
        return round(LIGHTSPEED/self.get_frequency(), 6)

    @abstractmethod
    def run(self, _run: bool = True) -> None:
        """
        Start repeat measurement.

        Args:
            _run: True = run, False = stop.
        """

    @abstractmethod
    def stop(self) -> None:
        """Stop repeat measurement."""

    @abstractmethod
    def single(self) -> None:
        """Perform single measurement."""

    @abstractmethod
    def is_running(self) -> bool:
        """
        Get the measurement state of the wavemeter.

        Returns:
            True = reapeat measurement, False = stopped.
        """


class TypeOTF(OpticalFrequencySetter):
    """ABC to define the interfaces of an Optical Tunable Filter."""

    ins_type = InstrumentType.OTF
    
    @property
    @abstractmethod
    def min_bandwidth_in_nm(self) -> float:
        """The minimum bandwidth in nm."""
        return bw_in_ghz_to_nm(self.min_bandwidth_in_ghz, self.get_frequency())

    @property
    @abstractmethod
    def max_bandwidth_in_nm(self) -> float:
        """The maximum bandwidth in nm."""
        return bw_in_ghz_to_nm(self.max_bandwidth_in_ghz, self.get_frequency())

    @property
    @abstractmethod
    def min_bandwidth_in_ghz(self) -> float:
        """The minimum bandwidth in GHz."""
        return bw_in_nm_to_ghz(self.min_bandwidth_in_nm, self.get_wavelength())

    @property
    @abstractmethod
    def max_bandwidth_in_ghz(self) -> float:
        """The maximum bandwidth in GHz."""
        return bw_in_nm_to_ghz(self.max_bandwidth_in_nm, self.get_wavelength())

    def get_bandwidth(self, unit: OpticalBandwidthUnit) -> float:
        """
        Get the filter bandwidth value in specified unit.

        Args:
            unit: The unit for the bandwidth value.
    
        Returns:
            The bandwidth value in specified unit.
        """
        unit = OpticalBandwidthUnit(unit)
        if unit == OpticalBandwidthUnit.GHZ:
            return self.get_bandwidth_in_ghz()
        else:
            return self.get_bandwidth_in_nm()

    def set_bandwidth(self, value: int | float, unit: OpticalBandwidthUnit) -> None:
        """
        Set the filter bandwidth in specified unit.
        
        Args:
            value: The bandwidth value in specified unit.
            unit: The unit of the bandwidth value.
        """
        unit = OpticalBandwidthUnit(unit)
        if unit == OpticalBandwidthUnit.GHZ:
            return self.set_bandwidth_in_ghz(value)
        else:
            return self.set_bandwidth_in_nm(value)

    @abstractmethod
    def get_bandwidth_in_nm(self) -> float:
        """
        Get the filter bandwidth in nm.

        Returns:
            The bandwidth value in nm.
        """
        bw_ghz = self.get_bandwidth_in_ghz()
        return round(bw_in_ghz_to_nm(bw_ghz, self.get_frequency()), 6)

    @abstractmethod
    def set_bandwidth_in_nm(self, value: int | float) -> None:
        """
        Set the filter bandwidth in nm.

        Args:
            value: The bandwidth value in nm.
        """
        bw_ghz = round(bw_in_nm_to_ghz(value, self.get_wavelength()), 6)
        self.set_bandwidth_in_ghz(bw_ghz)
    
    @abstractmethod
    def get_bandwidth_in_ghz(self) -> float:
        """
        Get the filter bandwidth in GHz.

        Returns:
            The bandwidth value in GHz.
        """
        bw_nm = self.get_bandwidth_in_nm()
        return round(bw_in_nm_to_ghz(bw_nm, self.get_wavelength()), 6)

    @abstractmethod
    def set_bandwidth_in_ghz(self, value: int | float) -> None:
        """
        Set the filter bandwidth in GHz.

        Args:
            value: The bandwidth value in GHz.
        """
        bw_nm = round(bw_in_ghz_to_nm(value, self.get_frequency()), 6)
        self.set_bandwidth_in_nm(bw_nm)


class TypeTS(ABC):
    """ABC to define the interfaces of a Temperature Source.

    A temperature source is an instrument that has the ability to control 
    environment temperature, including chamber, TEC (Thermo Electric Cooler), 
    thermo-stream, and so on.

    Each TypeTS class has a `ts_type` property to indicate the type of the 
    thermostream. It is a member of `TemperatureSourceType` enum.
    """

    ins_type = InstrumentType.TS
    
    @property
    def ts_type(self) -> TemperatureSourceType:
        """The type of the temperature source."""
        return TemperatureSourceType.UNDEFINED

    @abstractmethod
    def set_target_temp(self, value: int | float) -> None:
        """
        Set the target temperature.

        Args:
            value: The target temperature value.
        """

    @abstractmethod
    def get_target_temp(self) -> float:
        """
        Get the target temperature setting.

        Returns:
            The target temperature setting value.
        """

    @abstractmethod
    def get_current_temp(self) -> float:
        """
        Queries the current monitored temperature.

        Returns:
            The current temperature monitor value.
        """

    @abstractmethod
    def set_temp_unit(self, unit: TemperatureUnit) -> None:
        """
        Set the temperature unit.

        Args:
            unit: The temperature unit.
        """

    @abstractmethod
    def get_temp_unit(self) -> TemperatureUnit:
        """
        Get the temperature unit setting.

        Returns:
            The temperature unit. 
        """


class TypeSW(ABC):
    """ABC to define the interfaces of an Optical Switch."""

    ins_type = InstrumentType.SW

    @abstractmethod
    def set_channel(self, channel: int) -> None:
        """
        Switch to the specified channel route.

        Args:
            channel: The channel number.
        """

    @abstractmethod
    def get_channel(self) -> int:
        """
        Queries the current channel route of the switch.

        Returns:
            The channel number of current route.
        """


class TypeMSW(ABC):
    """ABC to define the interfaces of an Optical Matrix Switch."""

    ins_type = InstrumentType.MSW

    @abstractmethod
    def connect(self, port1: int, port2: int, enable: bool = True) -> None:
        """
        Sets a new optical connection.

        Note that this method will delete any existing connections using 
        port1 or port2.

        Use `check` to confirm whether either port is already in use.

        Args:
            port1: The valid port at one end of the path.
            port2: The valid port at the other end of the path.
            enable: Whether to enable the connection.
        """

    @abstractmethod
    def connected_with(self, port: int) -> Optional[int]:
        """
        Returns connection information of the specified port. 
        
        If the port is connected, return the port number at the other end of 
        the connection. If no connection exists for the port, return None.

        Args:
            port: The port number to check connection information.
        
        Returns:
            Connection information for the specified port.

            None = No connection exists.
            
            int N = Port number at other end of the connection.
        """

    @abstractmethod
    def clear(self, port: int) -> None:
        """
        Clears a configured optical connection connected to the specified port.

        Args:
            port: The port at either end of the configured connection.
        """

    @abstractmethod
    def clear_all(self) -> None:
        """Clears all configured optical connections."""

    @abstractmethod
    def check(self, port1: int, port2: int) -> bool:
        """
        To check if port1 and port2 are both not in use.

        Args:
            port1: The port at one end of the path.
            port2: The port at the other end of the path.

        Returns:
            True = Both ports available (not in use).

            False = Conflict; one or both ports already in use.
        """

    @abstractmethod
    def enable(self, port: int, enable: bool = True) -> None:
        """
        Sets the connection state of a configured optical connection.

        Args:
            port: The port at either end of the connection.
            enable: True = Enable | False = Disable.
        """

    @abstractmethod
    def disable(self, port: int) -> None:
        """
        Disable the connection of a configured optical connection.

        Args:
            port: The port at either end of the connection.
        """

    @abstractmethod
    def is_enabled(self, port: int) -> bool:
        """
        Returns the connection state of a configured optical connection.

        Returns:
            True = Enabled | False = Disabled
        """


class TypePS(ABC):
    """ABC to define the interfaces of a Power Supply."""

    ins_type = InstrumentType.PS

    @property
    @abstractmethod
    def min_voltage(self) -> float:
        """The minimum programmable voltage level in V."""

    @property
    @abstractmethod
    def max_voltage(self) -> float:
        """The maximum programmable voltage level in V."""

    @property
    @abstractmethod
    def min_current(self) -> float:
        """The minimum programmable current level in A."""

    @property
    @abstractmethod
    def max_current(self) -> float:
        """The maximum programmable current level in A."""

    @abstractmethod
    def enable(self, en: bool = True) -> None:
        """
        Enables (or disables) the outputs of the power supply.

        Args:
            en: `True` = Enable, `False` = Disable.
        """

    @abstractmethod
    def disable(self) -> None:
        """Disables the output of the power supply."""

    @abstractmethod
    def is_enabled(self) -> bool:
        """
        Queries whether the output of the power supply is enabled.

        Returns:
            `True` = Enabled, `False` = Disabled
        """

    @abstractmethod
    def set_voltage_limit(self, value: int | float) -> None:
        """
        Sets the immediate voltage level of the power supply.

        Args:
            value: The voltage level in V.
        """

    @abstractmethod
    def get_voltage_limit(self) -> float:
        """
        Queries the immediate voltage level of the power supply.

        Returns:
            The voltage level in V.
        """

    @abstractmethod
    def measure_voltage(self) -> float:
        """Queries the voltage measured at the sense terminals of the power 
        supply.

        Returns:
            The voltage measured in V.
        """

    @abstractmethod
    def set_current_limit(self, value: int | float) -> None:
        """
        Sets the immediate current level of the power supply.

        Args:
            value: The current level in A.
        """

    @abstractmethod
    def get_current_limit(self) -> float:
        """
        Queries the immediate current level of the power supply.

        Returns:
            The current level in A.
        """

    @abstractmethod
    def measure_current(self) -> float:
        """Queries the current measured across the current sense resistor 
        inside the power supply.

        Returns:
            The current measured in A.
        """


class TypePSwithOvpOcpFunctions(TypePS):
    """ABC to define the interfaces of a Power Supply with OCP & OVP 
    functions.
    """

    @abstractmethod
    def set_ocp_level(self, level: int | float) -> None:
        """
        Sets the current level at which the overcurrent protection (OCP) 
        circuit will trip. If the peak output current exceeds the OCP level, 
        then the output current is programmed to zero.

        You can use `is_ocp_tripped()` to query if the OCP circuit is tripped. 
        An overcurrent condition can be cleared with the `clear_ocp()` method 
        after the condition that caused the OCP trip is removed. 

        Args:
            level: The OCP level in A.
        """

    @abstractmethod
    def get_ocp_level(self) -> float:
        """Returns the overcurrent protection trip level presently programmed.

        See `set_ocp_level()` for more details.

        Returns:
            The OCP level in A.
        """

    @abstractmethod
    def enable_ocp(self, enable: bool = True) -> None:
        """Enables (or disables) the overcurrent protection function of the 
        power supply.

        Args:
            enable: `True` = Enable, `False` = Disable.
        """

    @abstractmethod
    def disable_ocp(self) -> None:
        """Disables the overcurrent protection function of the power supply.
        """

    @abstractmethod
    def is_ocp_enabled(self) -> bool:
        """Queries whether the overcurrent protection function of the power 
        supply is enabled.

        Returns:
            Whether the OCP function is enabled.
        """

    @abstractmethod
    def is_ocp_tripped(self) -> bool:
        """Queries if the overcurrent protection circuit is tripped and not 
        cleared.

        Returns:
            If the overcurrent protection circuit is tripped and not cleared.
        """

    @abstractmethod
    def clear_ocp(self) -> None:
        """This method causes the overcurrent protection circuit to be 
        cleared. Before using this method, lower the output current below the 
        trip OCP point, or raise the OCP trip level above the output setting.

        Note:
            Note that the overcurrent condition caused by an external source 
            must be removed first before proceeding this method.
        """

    @abstractmethod
    def set_ovp_level(self, level: int | float) -> None:
        """
        Sets the voltage level at which the overvoltage protection (OVP) 
        circuit will trip. If the peak output voltage exceeds the OVP level, 
        then the power supply output is shorted by an internal SCR.

        You can use `is_ovp_tripped()` to query if the OVP circuit is tripped. 
        An overvoltage condition can be cleared with the `clear_ovp()` method 
        after the condition that caused the OVP trip is removed. 

        Args:
            level: The OVP level in V.
        """

    @abstractmethod
    def get_ovp_level(self) -> float:
        """Returns the overvoltage protection trip level presently programmed.

        See `set_ovp_level()` for more details.

        Returns:
            The OVP level in V.
        """

    @abstractmethod
    def enable_ovp(self, enable: bool = True) -> None:
        """Enables (or disables) the overvoltage protection function of the 
        power supply.

        Args:
            enable: `True` = Enable, `False` = Disable.
        """

    @abstractmethod
    def disable_ovp(self) -> None:
        """Disables the overvoltage protection function of the power supply.
        """

    @abstractmethod
    def is_ovp_enabled(self) -> bool:
        """Queries whether the overvoltage protection function of the power 
        supply is enabled.

        Returns:
            Whether the OVP function is enabled.
        """

    @abstractmethod
    def is_ovp_tripped(self) -> bool:
        """Queries if the overvoltage protection circuit is tripped and not 
        cleared.

        Returns:
            If the overvoltage protection circuit is tripped and not cleared.
        """

    @abstractmethod
    def clear_ovp(self) -> None:
        """This method causes the overvoltage protection circuit to be 
        cleared. Before sending this method, lower the output voltage below 
        the trip OVP point, or raise the OVP trip level above the output
        setting.

        Note:
            Note that the overvoltage condition caused by an external source 
            must be removed first before proceeding this method.
        """


class TypePDLE(OpticalFrequencySetter):
    """ABC to define the interfaces of a PDL Emulator."""

    ins_type = InstrumentType.PDLE

    @property
    @abstractmethod
    def min_pdl(self) -> float:
        """The minimum settable PDL value."""

    @property
    @abstractmethod
    def max_pdl(self) -> float:
        """The maximum settable PDL value."""

    @abstractmethod
    def get_pdl_value(self) -> float:
        """
        Returns:
            The PDL setting value in dB.
        """

    @abstractmethod
    def set_pdl_value(self, value: int | float) -> None:
        """
        Args:
            value: The PDL setting value in dB.
        """


class TypePOLC(OpticalFrequencySetter):
    """ABC to define the interfaces of a Polarization Controller/Scrambler."""

    ins_type = InstrumentType.POLC
    
    @abstractmethod
    def start_scrambling(self, mode: str, rate: int | float, **params: Any) -> None:
        """
        Start scrambling with the specified mode and rate.

        Args:
            mode: Scrambling mode. Valid options depends on specific model.
            rate: Scrambling rate. Different mode may have different units.
            **params: Additional scrambling params if any.
        """
    
    @abstractmethod
    def stop_scrambling(self) -> None:
        """Stop scrambling."""


class TypePMDE(OpticalFrequencySetter):
    """ABC to define the interfaces of a PMD Emulator."""

    ins_type = InstrumentType.PMDE
    
    @abstractmethod
    def set_pmd_value(self, pmd: int | float, sopmd: int | float) -> None:
        """
        Set PMD (DGD) and SOPMD (Second Order PMD) target value.

        Args:
            pmd: The DGD value in ps.
            sopmd: The 2nd order pmd in ps**2.
        """

    @abstractmethod
    def get_pmd_value(self) -> Tuple[float, float]:
        """
        Get PMD (DGD) and SOPMD (Second Order PMD) target value.

        Returns:
            pmd: The DGD value in ps.
            sopmd: The 2nd order pmd in ps**2.
        """
