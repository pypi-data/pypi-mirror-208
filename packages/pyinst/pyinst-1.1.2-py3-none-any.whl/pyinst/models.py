"""
*Instrument Model* classes are types to drive specific instrument models.

An *Instrument Model* class always starts with a prefix `Model`, for example: 
`ModelAQ6370`, `ModelOTF980`. 

All *Instrument Model* classes can be directly imported from `pyinst` name space.

The *Instrument Model* is immediately opened on object creation. The first 
parameter of the `__init__` method is always `resource_name`:

- For VISA compatible instruments, it is the VISA resource name or alias.
- For other instruments connected with serial port, it is the port name.
- For other instruments connected with USB, it is the S/N of the 
instrument/USB chip.

For more details, please refer to the specific *Instrument Model* class.

Examples:
    >>> from pyinst import ModelN7744A
    >>> opm = ModelN7744A('GPIB1::1::INSTR', slot=2)
    >>> opm.get_power_value()
    -10.85
    >>> opm.close() # release the instrument resource

Note:
    An *Instrument Model* object is a function component in logic, does not 
    correspond with the physical topography of the real-world instrument. 

    For example, for OPM N7744A, it has 4 slots of OPM function components. 
    Each slot can be considered as an independent `ModelN7744A` object.

*Instrument Model* classes also support context management, so you can use 
the "with" statement to ensure that the instrument resource is closed after 
usage.

Examples:
    >>> with ModelN7744A('GPIB1::1::INSTR', slot=2) as opm:
    >>>     opm.get_power_value()
    >>> 
    -10.85
"""

from __future__ import annotations
from abc import abstractmethod
from functools import wraps
import time
import os
import re
from typing import Any, Dict, List, Literal, Optional, Tuple, Callable
from decimal import Decimal
import warnings
import serial
import ctypes

import ftd2xx as ftd

from .abc import (
    BaseInstrument, VisaInstrument, RawSerialInstrument, 
    TypeOMA, TypeOPM, TypeOTF, TypeVOA, TypeOSA, TypeWM, TypeTS, TypeSW, 
    TypeMSW, TypePS, TypePSwithOvpOcpFunctions, TypePDLE, TypePMDE, TypePOLC)
from .errors import InstrIOError, InstrWarning, Error
from .constants import (
    LIGHTSPEED, ChamberOperatingMode, SerialByteSize, SerialParity, SerialStopBits, OpticalPowerUnit, 
    TemperatureUnit, TemperatureSourceType)
from .utils import bw_in_ghz_to_nm, bw_in_nm_to_ghz, signed_to_unsigned, unsigned_to_signed, calc_check_sum
from .libs.neo_usb_device import NeoUsbDevice


class BaseModelN77xx(VisaInstrument):
    """
    Base class for Keysight N77xx Series:

    - N7744A, N7745A, N7747A and N7748A Optical Multiport Power Meters

    - N7751A and N7752A Variable Optical Attenuators and 2-Channel Optical Power Meter

    - N7761A, N7762A and N7764A Variable Optical Attenuators

    """

    def __init__(self, resource_name: str, slot: int, **kwargs: Any):
        """
        Args:
            resource_name: Resource name or alias of the VISA resource to open.
            slot: The slot number in the frame.
            **kwargs: Directly passed to `VisaInstrument.__init__`
        """
        if not 1 <= slot <= self._max_slot:
            raise ValueError(f'Parameter slot is out of range: {slot!r}. The max slot number is {self._max_slot}.')
        self.__slot = slot
        super().__init__(resource_name, **kwargs)

    @property
    @abstractmethod
    def _max_slot(self) -> int:
        """The max valid slot number for the specific instrument model.
        
        Defined by specific Instrument Model classes.
        """

    @property
    def _slot(self) -> int:
        return self.__slot


class BaseModelN77xx_OPM(BaseModelN77xx, TypeOPM):

    @property
    def min_frequency(self) -> float:
        """The minimum settable optical frequency value in THz."""
        return super().min_frequency
    
    @property
    def max_frequency(self) -> float:
        """The maximum settable optical frequency value in THz."""
        return super().max_frequency

    @property
    def min_wavelength(self) -> float:
        """The minimum settable optical wavelength value in nm."""
        cmd = ":SENS{slot:d}:POW:WAV? MIN".format(slot=self._slot)
        wl = float(Decimal(self.query(cmd)) * 10**9)
        return wl

    @property
    def max_wavelength(self) -> float:
        """The maximum settable optical wavelength value in nm."""
        cmd = ":SENS{slot:d}:POW:WAV? MAX".format(slot=self._slot)
        wl = float(Decimal(self.query(cmd)) * 10**9)
        return wl
    
    @property
    def min_avg_time(self) -> float:
        """The minimum averaging time in ms."""
        return 0.001 # 1us

    @property
    def max_avg_time(self) -> float:
        """The maximum averaging time in ms."""
        return 10000.0 # 10s

    @property
    def min_pow_cal(self) -> float:
        """The minimum power calibration value in dB."""
        return -200.0 # dB

    @property
    def max_pow_cal(self) -> float:
        """The maximum power calibration value in dB."""
        return 200.0 # dB

    def get_frequency(self) -> float:
        """
        Queries the optical frequency setting of the instrument in THz.

        Returns:
            The optical frequency setting value in THz.
        """
        return super().get_frequency()

    def set_frequency(self, frequency: int | float) -> None:
        """Set optical frequency.

        Args:
            frequency: The optical frequency setting in THz.
        """
        return super().set_frequency(frequency)

    def get_wavelength(self) -> float:
        """Queries the optical wavelength setting of the instrument in nm.

        Returns:
            The optical wavelength setting value in nm.
        """
        cmd = ":SENS{slot:d}:POW:WAV?".format(slot=self._slot)
        wl = float(Decimal(self.query(cmd)) * 10**9)
        return wl

    def set_wavelength(self, wavelength: int | float) -> None:
        """Set optical wavelength.

        Args:
            wavelength: The optical wavelength setting in nm.
        """
        if not self.min_wavelength <= wavelength <= self.max_wavelength:
            raise ValueError(f"Parameter wavelength is out of range: {wavelength!r}")
        cmd = ":SENS{slot:d}:POW:WAV {value:f}NM".format(slot=self._slot, value=wavelength)
        self.command(cmd)
    
    def get_power_value(self) -> float:
        """Fetch the value of measured optical power in current unit setting.

        The measured value includes the power calibration.

        Measured value (dBm) = the actual measured value (dBm) + power calibration (dB)

        Refer to `get_pow_cal` and `set_pow_cal` to operate with the power calibration.

        Returns:
            The value of the optical power.
        """
        cmd = ":FETC{slot:d}:POW?".format(slot=self._slot)
        power_value = float(self.query(cmd))
        return power_value
    
    def get_power_unit(self) -> OpticalPowerUnit:
        """Get optical power unit setting.

        Returns:
            The unit of the optical power.
        """
        cmd = ":SENS{slot:d}:POW:UNIT?".format(slot=self._slot)
        unit_int = int(self.query(cmd))
        return OpticalPowerUnit(unit_int)

    def set_power_unit(self, unit: OpticalPowerUnit) -> None:
        """Set the unit of optical power.

        Args:
            unit: The unit of the optical power.
        """
        unit = OpticalPowerUnit(unit)
        cmd = ":SENS{slot:d}:POW:UNIT {unit:d}".format(slot=self._slot, unit=unit)
        self.command(cmd)

    def get_pow_cal(self) -> float:
        """
        Get the power calibration offset in dB.

        Note:
            The power calibration value defined here is opposite in sign 
            with the instrument display value. This is to unify the 
            definition of power calibration across different models of OPMs. 
            Please refer to `get_power_value` for the math equation.

        Returns:
            The power calibration offset in dB.
        """
        cmd = ":SENS{slot:d}:CORR?".format(slot=self._slot)
        cal = -float(self.query(cmd))
        return cal
    
    def set_pow_cal(self, value: int | float) -> None:
        """
        Set the power calibration offset in dB.

        Args:
            value: The power calibration offset in dB.
        """
        if not self.min_pow_cal <= value <= self.max_pow_cal:
            raise ValueError("param value out of range: {value}".format(value=value))
        cmd = ":SENS{slot}:CORR {value}DB".format(slot=self._slot, value=-value)
        self.command(cmd)
    
    def get_avg_time(self) -> float:
        """
        Get the averaging time in ms.

        Returns:
            The averaging time in ms.
        """
        cmd = ":SENS{slot:d}:POW:ATIM?".format(slot=self._slot)
        avg_t = float(Decimal(self.query(cmd)) * 10**3)
        return avg_t
    
    def set_avg_time(self, value: int | float) -> None:
        """
        Set the averaging time in ms.

        Args:
            value: The averaging time in ms.
        """
        if not self.min_avg_time <= value <= self.max_avg_time:
            raise ValueError("param value out of range: {value}".format(value=value))
        cmd = ":SENS{slot}:POW:ATIM {value}MS".format(slot=self._slot, value=value)
        self.command(cmd)


class BaseModelN77xx_VOA_with_OPM(BaseModelN77xx, TypeVOA, TypeOPM):

    @property
    def min_frequency(self) -> float:
        """The minimum settable optical frequency value in THz."""
        return super().min_frequency

    @property
    def max_frequency(self) -> float:
        """The maximum settable optical frequency value in THz."""
        return super().max_frequency
    
    @property
    def min_wavelength(self) -> float:
        """The minimum settable optical wavelength value in nm."""
        cmd = ":INPut{slot:d}:WAVelength? MIN".format(slot=self._slot)
        wl = float(Decimal(self.query(cmd)) * 10**9)
        return wl
    
    @property
    def max_wavelength(self) -> float:
        """The maximum settable optical wavelength value in nm."""
        cmd = ":INPut{slot:d}:WAVelength? MAX".format(slot=self._slot)
        wl = float(Decimal(self.query(cmd)) * 10**9)
        return wl
    
    @property
    def min_avg_time(self) -> float:
        """The minimum averaging time in ms."""
        return 2.0

    @property
    def max_avg_time(self) -> float:
        """The maximum averaging time in ms."""
        return 10000.0

    @property
    def min_pow_cal(self) -> float:
        """The minimum power calibration value in dB."""
        return -200.0

    @property
    def max_pow_cal(self) -> float:
        """The maximum power calibration value in dB."""
        return 200.0
    
    @property
    def min_att(self) -> float:
        """Minimum settable attenuation in dB.

        The minimum settable attenuation = 0 dB + the optical attenuation 
        offset value.
        """
        cmd = ":INP{slot:d}:ATT? MIN".format(slot=self._slot)
        att = float(self.query(cmd))
        return att
    
    @property
    def max_att(self) -> float:
        """Maximum settable attenuation in dB.

        The maximum settable attenuation = The maximum attenuation + the 
        optical attenuation offset value.
        """
        cmd = ":INP{slot:d}:ATT? MAX".format(slot=self._slot)
        att = float(self.query(cmd))
        return att

    @property
    def min_att_offset(self) -> float:
        """Minimum attenuation offset value in dB."""
        cmd = ":INP{slot}:OFFS? MIN".format(slot=self._slot)
        offset = float(self.query(cmd))
        return offset
    
    @property
    def max_att_offset(self) -> float:
        """Maximum attenuation offset value in dB."""
        cmd = ":INP{slot}:OFFS? MAX".format(slot=self._slot)
        offset = float(self.query(cmd))
        return offset

    def get_frequency(self) -> float:
        """
        Queries the optical frequency setting of the instrument in THz.

        Returns:
            The optical frequency setting value in THz.
        """
        return super().get_frequency()

    def set_frequency(self, frequency: int | float) -> None:
        """Set optical frequency.

        Args:
            frequency: The optical frequency setting in THz.
        """
        return super().set_frequency(frequency)
    
    def get_wavelength(self) -> float:
        """Queries the optical wavelength setting of the instrument in nm.

        Returns:
            The optical wavelength setting value in nm.
        """
        cmd = ":INPut{slot:d}:WAVelength?".format(slot=self._slot)
        wl = float(Decimal(self.query(cmd)) * 10**9)
        return wl
    
    def set_wavelength(self, wavelength: int | float) -> None:
        """Set optical wavelength.

        Args:
            wavelength: The optical wavelength setting in nm.
        """
        if not self.min_wavelength <= wavelength <= self.max_wavelength:
            raise ValueError(f"Parameter wavelength is out of range: {wavelength}")
        cmd = ":INPut{slot:d}:WAVelength {wl}NM".format(slot=self._slot, wl=wavelength)
        self.command(cmd)
    
    def get_power_value(self) -> float:
        """Fetch the value of measured optical power in current unit setting.

        The measured value includes the power calibration.

        Measured value (dBm) = the actual measured value (dBm) + power calibration (dB)

        Refer to `get_pow_cal` and `set_pow_cal` to operate with the power calibration.

        Returns:
            The value of the optical power.
        """
        cmd = ":FETC{slot:d}:POW?".format(slot=self._slot)
        power_value = float(self.query(cmd))
        return power_value
    
    def get_power_unit(self) -> OpticalPowerUnit:
        """Get optical power unit setting.

        Returns:
            The unit of the optical power.
        """
        cmd = ":OUTPut{slot:d}:POWer:UNit?".format(slot=self._slot)
        unit_int = int(self.query(cmd))
        return OpticalPowerUnit(unit_int)

    def set_power_unit(self, unit: OpticalPowerUnit) -> None:
        """Set the unit of optical power.

        Args:
            unit: The unit of the optical power.
        """
        unit = OpticalPowerUnit(unit)
        cmd = ":OUTPut{slot:d}:POWer:UNit {unit:d}".format(slot=self._slot, unit=unit)
        self.command(cmd)
    
    def get_pow_cal(self) -> float:
        """
        Get the power calibration offset in dB.

        Note:
            The power calibration value defined here is opposite in sign 
            with the instrument display value. This is to unify the 
            definition of power calibration across different models of OPMs. 
            Please refer to `get_power_value` for the math equation.

        Returns:
            The power calibration offset in dB.
        """
        cmd = ":OUTPut{slot:d}:POWer:OFFSet?".format(slot=self._slot)
        cal = -float(self.query(cmd))
        return cal
    
    def set_pow_cal(self, value: int | float) -> None:
        """
        Set the power calibration offset in dB.

        Args:
            value: The power calibration offset in dB.
        """
        if not self.min_pow_cal <= value <= self.max_pow_cal:
            raise ValueError(f"Parameter value is out of range: {value!r}")
        cmd = ":OUTPut{slot:d}:POWer:OFFSet {value}DB".format(slot=self._slot, value=-value) # opposite sign
        self.command(cmd)

    def get_avg_time(self) -> float:
        """
        Get the averaging time in ms.

        Returns:
            The averaging time in ms.
        """
        cmd = ":OUTPut{slot:d}:ATIMe?".format(slot=self._slot)
        atime = float(Decimal(self.query(cmd)) * 10**3)
        return atime
    
    def set_avg_time(self, value: int | float) -> None:
        """
        Set the averaging time in ms.

        Args:
            value: The averaging time in ms.
        """
        if not self.min_avg_time <= value <= self.max_avg_time:
            raise ValueError(f"Parameter value is out of range: {value!r}")
        cmd = ":OUTPut{slot:d}:ATIMe {value}MS".format(slot=self._slot, value=value)
        self.command(cmd)

    def enable(self, en: bool = True) -> None:
        """
        Enable (disable) the optical output.
        
        Args:
            en: True = Enable, False = Disable.
        """
        if not isinstance(en, bool):
            raise TypeError(f"Parameter en must be a bool, not '{type(en).__name__}'.")
        cmd = ":OUTP{slot:d} {status:d}".format(slot=self._slot, status=en)
        self.command(cmd)
    
    def disable(self) -> None:
        """Disable the optical output."""
        self.enable(False)
    
    def is_enabled(self) -> bool:
        """
        Returns:
            Whether the optical output is enabled.
        """
        cmd = ":OUTP{slot:d}?".format(slot=self._slot)
        status = bool(int(self.query(cmd)))
        return status
    
    def get_att(self) -> float:
        """
        Get the current attenuation value in dB.
        
        Includes the attenuation offset.

        Queried attenuator = the actual attenuator value + attenuator offset

        Use `get_att_offset` and `set_att_offset` to operate with the 
        attenuator offset.

        Returns:
            The attenuation value in dB.
        """
        cmd = ":INP{slot:d}:ATT?".format(slot=self._slot)
        att = float(self.query(cmd))
        return att
    
    def set_att(self, att: int | float) -> None:
        """
        Set attenuation value in dB.

        Includes the attenuation offset. Refer to `get_att` for more 
        information.

        Args:
            att: The attenuation value in dB.
        """
        if not self.min_att <= att <= self.max_att:
            raise ValueError(f'Parameter att is out of range: {att!r}')
        cmd = ":INP{slot:d}:ATT {value:.3f}DB".format(slot=self._slot, value=att)
        self.command(cmd)

    def get_att_offset(self) -> float:
        """
        Get the attenuation offset value in dB.

        Returns:
            The attenuation offset in dB.
        """
        cmd = ":INP{slot:d}:OFFS?".format(slot=self._slot)
        offset = float(self.query(cmd))
        return offset
    
    def set_att_offset(self, offset: int | float) -> None:
        """
        Set the attenuation offset value in dB.

        Args:
            offset: The attenuation offset in dB.
        """
        if not self.min_att_offset <= offset <= self.max_att_offset:
            raise ValueError(f"Parameter offset is out of range: {offset!r}")
        self.command(":INP{slot:d}:OFFS {value:.3f}DB".format(slot=self._slot, value=offset))


class ModelN7744A(BaseModelN77xx_OPM):
    """Keysight N7744A multi-channel optical power meter."""

    brand = "Keysight"

    model = "N7744A"

    details = {
        "Wavelength Range": "1250 ~ 1625 nm",
        "Input Power Range": "-80 ~ +10 dBm",
        "Safe Power": "+16 dBm",
        "Averaging Time": "1 us ~ 10 s",
    }

    params = [
        {
            "name": "slot",
            "type": "int",
            "options": [1, 2, 3, 4],
        }
    ]

    @property
    def _max_slot(self) -> int:
        return 4


class ModelN7752A(BaseModelN77xx_VOA_with_OPM, BaseModelN77xx_OPM):
    """Keysight N7752A 2-channel optical attenuator and 2-channel power meter.
    """

    brand = "Keysight"

    model = "N7752A"

    details = {
        "Wavelength Range": "1260~1640 nm",
        "(slot 1~4) Att Range": "0 ~ 45 dB",
        "(slot 1~4) Safe Power": "+23 dBm",
        "(slot 5~6) Input Power Range": "-80 ~ +10 dBm",
        "(slot 5~6) Safe Power": "+16 dBm",
        "Averaging Time": "2 ms ~ 10 s",
    }

    params = [
        {
            "name": "slot",
            "type": "int",
            "options": [1, 3, 5, 6]
        }
    ]

    def __init__(self, resource_name: str, slot: int, **kwargs: Any):
        """
        Args:
            resource_name: Resource name or alias of the VISA resource to open.
            slot: The slot number in the frame.
            **kwargs: Directly passed to `VisaInstrument.__init__`.
        """
        super(ModelN7752A, self).__init__(resource_name, slot, **kwargs)
        
        __topology = {
            1: 'voa_with_opm',
            2: 'voa_with_opm',
            3: 'voa_with_opm',
            4: 'voa_with_opm',
            5: 'opm',
            6: 'opm',
        }
        
        self.__slot_type = __slot_type = __topology[slot]
        self.__Base = BaseModelN77xx_OPM if __slot_type == 'opm' else BaseModelN77xx_VOA_with_OPM

    def __raise_NotImplementedError(self) -> None:
        raise NotImplementedError(f"This function is not implemented for slot {self._slot}.")

    @property
    def _max_slot(self) -> int:
        return 6

    @property
    def min_frequency(self) -> float:
        """The minimum settable optical frequency value in THz."""
        return super().min_frequency

    @property
    def max_frequency(self) -> float:
        """The maximum settable optical frequency value in THz."""
        return super().max_frequency

    @property
    def min_wavelength(self) -> float:
        """The minimum settable optical wavelength value in nm."""
        return self.__Base.min_wavelength.__get__(self)

    @property
    def max_wavelength(self) -> float:
        """The maximum settable optical wavelength value in nm."""
        return self.__Base.max_wavelength.__get__(self)

    @property
    def min_avg_time(self) -> float:
        """The minimum averaging time in ms."""
        return 2.0  # 2ms

    @property
    def max_avg_time(self) -> float:
        """The maximum averaging time in ms."""
        return 10000.0  # 10s

    @property
    def min_pow_cal(self) -> float:
        """The minimum power calibration value in dB."""
        return self.__Base.min_pow_cal.__get__(self)

    @property
    def max_pow_cal(self) -> float:
        """The maximum power calibration value in dB."""
        return self.__Base.max_pow_cal.__get__(self)

    @property
    def min_att(self) -> float:
        """Minimum settable attenuation in dB.

        The minimum settable attenuation = 0 dB + the optical attenuation 
        offset value.
        """
        if self.__slot_type == 'opm':
            self.__raise_NotImplementedError()
        return super().min_att

    @property
    def max_att(self) -> float:
        """Maximum settable attenuation in dB.

        The maximum settable attenuation = The maximum attenuation + the 
        optical attenuation offset value.
        """
        if self.__slot_type == 'opm':
            self.__raise_NotImplementedError()
        return super().max_att

    @property
    def min_att_offset(self) -> float:
        """Minimum attenuation offset value in dB."""
        if self.__slot_type == 'opm':
            self.__raise_NotImplementedError()
        return super().min_att_offset

    @property
    def max_att_offset(self) -> float:
        """Maximum attenuation offset value in dB."""
        if self.__slot_type == 'opm':
            self.__raise_NotImplementedError()
        return super().max_att_offset
    
    def get_frequency(self) -> float:
        """
        Queries the optical frequency setting of the instrument in THz.

        Returns:
            The optical frequency setting value in THz.
        """
        return super().get_frequency()
    
    def set_frequency(self, frequency: int | float) -> None:
        """Set optical frequency.

        Args:
            frequency: The optical frequency setting in THz.
        """
        return super().set_frequency(frequency)

    def get_wavelength(self) -> float:
        """Queries the optical wavelength setting of the instrument in nm.

        Returns:
            The optical wavelength setting value in nm.
        """
        return self.__Base.get_wavelength(self)

    def set_wavelength(self, wavelength: int | float) -> None:
        """Set optical wavelength.

        Args:
            wavelength: The optical wavelength setting in nm.
        """
        return self.__Base.set_wavelength(self, wavelength)

    def get_power_value(self) -> float:
        """Fetch the value of measured optical power in current unit setting.

        The measured value includes the power calibration.

        Measured value (dBm) = the actual measured value (dBm) + power calibration (dB)

        Refer to `get_pow_cal` and `set_pow_cal` to operate with the power calibration.

        Returns:
            The value of the optical power.
        """
        return self.__Base.get_power_value(self)

    def get_power_unit(self) -> OpticalPowerUnit:
        """Get optical power unit setting.

        Returns:
            The unit of the optical power.
        """
        return self.__Base.get_power_unit(self)

    def set_power_unit(self, unit: OpticalPowerUnit) -> None:
        """Set the unit of optical power.

        Args:
            unit: The unit of the optical power.
        """
        return self.__Base.set_power_unit(self, unit)

    def get_pow_cal(self) -> float:
        """
        Get the power calibration offset in dB.

        Note:
            The power calibration value defined here is opposite in sign 
            with the instrument display value. This is to unify the 
            definition of power calibration across different models of OPMs. 
            Please refer to `get_power_value` for the math equation.

        Returns:
            The power calibration offset in dB.
        """
        return self.__Base.get_pow_cal(self)
        
    def set_pow_cal(self, value: int | float) -> None:
        """
        Set the power calibration offset in dB.

        Args:
            value: The power calibration offset in dB.
        """
        return self.__Base.set_pow_cal(self, value)

    def get_avg_time(self) -> float:
        """
        Get the averaging time in ms.

        Returns:
            The averaging time in ms.
        """
        return self.__Base.get_avg_time(self)

    def set_avg_time(self, value: int | float) -> None:
        """
        Set the averaging time in ms.

        Args:
            value: The averaging time in ms.
        """
        return self.__Base.set_avg_time(self, value)

    def enable(self, en: bool = True) -> None:
        """
        Enable (disable) the optical output.
        
        Args:
            en: True = Enable, False = Disable.
        """
        if self.__slot_type == 'opm':
            self.__raise_NotImplementedError()
        return super().enable(en)

    def disable(self) -> None:
        """Disable the optical output."""
        if self.__slot_type == 'opm':
            self.__raise_NotImplementedError()
        self.enable(False)

    def is_enabled(self) -> bool:
        """
        Returns:
            Whether the optical output is enabled.
        """
        if self.__slot_type == 'opm':
            self.__raise_NotImplementedError()
        return super().is_enabled()

    def get_att(self) -> float:
        """
        Get the current attenuation value in dB.
        
        Includes the attenuation offset.

        Queried attenuator = the actual attenuator value + attenuator offset

        Use `get_att_offset` and `set_att_offset` to operate with the 
        attenuator offset.

        Returns:
            The attenuation value in dB.
        """
        if self.__slot_type == 'opm':
            self.__raise_NotImplementedError()
        return super().get_att()

    def set_att(self, att: int | float) -> None:
        """
        Set attenuation value in dB.

        Includes the attenuation offset. Refer to `get_att` for more 
        information.

        Args:
            att: The attenuation value in dB.
        """
        if self.__slot_type == 'opm':
            self.__raise_NotImplementedError()
        return super().set_att(att)

    def get_att_offset(self) -> float:
        """
        Get the attenuation offset value in dB.

        Returns:
            The attenuation offset in dB.
        """
        if self.__slot_type == 'opm':
            self.__raise_NotImplementedError()
        return super().get_att_offset()

    def set_att_offset(self, offset: int | float) -> None:
        """
        Set the attenuation offset value in dB.

        Args:
            offset: The attenuation offset in dB.
        """
        if self.__slot_type == 'opm':
            self.__raise_NotImplementedError()
        return super().set_att_offset(offset)

class ModelN7764A(BaseModelN77xx_VOA_with_OPM):
    """Keysight N7764A 4-channel variable optical attenuator with built-in power meter."""

    brand = "Keysight"

    model = "N7764A"

    details = {
        "Wavelength Range": "1260~1640 nm",
        "Att Range": "0 ~ 45 dB",
        "Safe Power": "+23 dBm",
        "Averaging Time": "2 ms ~ 10 s",
    }

    params = [
        {
            "name": "slot",
            "type": "int",
            "options": [1, 3, 5, 7]
        }
    ]

    def __init__(self, resource_name: str, slot: int, **kwargs: Any):
        """
        Args:
            resource_name: Resource name or alias of the VISA resource to open.
            slot: The slot number in the frame.
            **kwargs: Directly passed to `VisaInstrument.__init__`
        """
        super(ModelN7764A, self).__init__(resource_name, slot)

    @property
    def _max_slot(self) -> int:
        return 8


class BaseModelAQ2200_VOA(VisaInstrument, TypeVOA):
    """The base class of AQ2200 Series, application type ATTN, without 
    built-in OPM."""

    def __init__(self, resource_name: str, slot: int, channel: int, **kwargs: Any) -> None:
        """
        Args:
            resource_name: Resource name or alias of the VISA resource to open.
            slot: The slot number in the frame.
            channel: The channel number.
            **kwargs: Directly passed to `VisaInstrument.__init__`
        """
        super().__init__(resource_name, read_termination='', **kwargs)
        self._slot = slot
        self._channel = channel

    @property
    def min_frequency(self) -> float:
        """The minimum settable optical frequency value in THz."""
        return super().min_frequency

    @property
    def max_frequency(self) -> float:
        """The maximum settable optical frequency value in THz."""
        return super().max_frequency

    @property
    def min_wavelength(self) -> float:
        """The minimum settable optical wavelength value in nm."""
        cmd = ":INP{slot:d}:CHAN{channel:d}:WAV? MIN".format(slot=self._slot, channel=self._channel)
        wl_str = self.query(cmd)
        wl = float(Decimal(wl_str)*10**9)
        return wl

    @property
    def max_wavelength(self) -> float:
        """The maximum settable optical wavelength value in nm."""
        cmd = ":INP{slot:d}:CHAN{channel:d}:WAV? MAX".format(slot=self._slot, channel=self._channel)
        wl_str = self.query(cmd)
        wl = float(Decimal(wl_str)*10**9)
        return wl

    @property
    def min_att(self) -> float:
        """Minimum settable attenuation in dB.

        The minimum settable attenuation = 0 dB + the optical attenuation 
        offset value.
        """
        cmd = ":INP{slot:d}:CHAN{channel:d}:ATT? MIN".format(slot=self._slot, channel=self._channel)
        att = float(self.query(cmd))
        return att

    @property
    def max_att(self) -> float:
        """Maximum settable attenuation in dB.

        The maximum settable attenuation = The maximum attenuation + the 
        optical attenuation offset value.
        """
        cmd = ":INP{slot:d}:CHAN{channel:d}:ATT? MAX".format(slot=self._slot, channel=self._channel)
        att = float(self.query(cmd))
        return att

    @property
    def min_att_offset(self) -> float:
        """Minimum attenuation offset value in dB."""
        cmd = ":INP{slot:d}:CHAN{channel:d}:OFFS? MIN".format(slot=self._slot, channel=self._channel)
        offset = float(self.query(cmd))
        return offset
        
    @property
    def max_att_offset(self) -> float:
        """Maximum attenuation offset value in dB."""
        cmd = ":INP{slot:d}:CHAN{channel:d}:OFFS? MAX".format(slot=self._slot, channel=self._channel)
        offset = float(self.query(cmd))
        return offset

    def get_frequency(self) -> float:
        """
        Queries the optical frequency setting of the instrument in THz.

        Returns:
            The optical frequency setting value in THz.
        """
        return super().get_frequency()

    def set_frequency(self, frequency: int | float) -> None:
        """Set optical frequency.

        Args:
            frequency: The optical frequency setting in THz.
        """
        return super().set_frequency(frequency)

    def get_wavelength(self) -> float:
        """Queries the optical wavelength setting of the instrument in nm.

        Returns:
            The optical wavelength setting value in nm.
        """
        cmd = ":INP{slot:d}:CHAN{channel:d}:WAV?".format(slot=self._slot, channel=self._channel)
        wl_str = self.query(cmd)
        wl = float(Decimal(wl_str)*10**9)
        return wl

    def set_wavelength(self, wavelength: int | float) -> None:
        """Set optical wavelength.

        Args:
            wavelength: The optical wavelength setting in nm.
        """
        if not self.min_wavelength <= wavelength <= self.max_wavelength:
            raise ValueError(f'Parameter wavelength is out of range: {wavelength!r}')
        cmd = ":INP{slot:d}:CHAN{channel:d}:WAV {wl:f}NM".format(slot=self._slot, channel=self._channel, wl=wavelength)
        self.command(cmd)

    def enable(self, en: bool = True) -> None:
        """
        Enable (disable) the optical output.
        
        Args:
            en: True = Enable, False = Disable.
        """
        if not isinstance(en, bool):
            raise TypeError(f"Parameter en must be a bool, not '{type(en).__name__}'.")
        cmd = ":OUTP{slot:d}:CHAN{channel:d} {en:d}".format(slot=self._slot, channel=self._channel, en=en)
        self.command(cmd)

    def disable(self) -> None:
        """Disable the optical output."""
        self.enable(False)

    def is_enabled(self) -> bool:
        """
        Returns:
            Whether the optical output is enabled.
        """
        cmd = ":OUTP{slot:d}:CHAN{channel:d}?".format(slot=self._slot, channel=self._channel)
        return bool(int(self.query(cmd)))

    def get_att(self) -> float:
        """
        Get the current attenuation value in dB.
        
        Includes the attenuation offset.

        Queried attenuator = the actual attenuator value + attenuator offset

        Use `get_att_offset` and `set_att_offset` to operate with the 
        attenuator offset.

        Returns:
            The attenuation value in dB.
        """
        cmd = ":INP{slot:d}:CHAN{channel:d}:ATT?".format(slot=self._slot, channel=self._channel)
        att = float(self.query(cmd))
        return att

    def set_att(self, att: int | float) -> None:
        """
        Set attenuation value in dB.

        Includes the attenuation offset. Refer to `get_att` for more 
        information.

        Args:
            att: The attenuation value in dB.
        """
        if not self.min_att <= att <= self.max_att:
            raise ValueError(f'Parameter att is out of range: {att!r}')
        cmd = ":INP{slot:d}:CHAN{channel:d}:ATT {att:.3f}dB".format(slot=self._slot, channel=self._channel, att=att)
        self.command(cmd)

    def get_att_offset(self) -> float:
        """
        Get the attenuation offset value in dB.

        Returns:
            The attenuation offset in dB.
        """
        cmd = ":INP{slot:d}:CHAN{channel:d}:OFFS?".format(slot=self._slot, channel=self._channel)
        offset = float(self.query(cmd))
        return offset

    def set_att_offset(self, offset: int | float) -> None:
        """
        Set the attenuation offset value in dB.

        Args:
            offset: The attenuation offset in dB.
        """
        if not self.min_att_offset <= offset <= self.max_att_offset:
            raise ValueError(f"Parameter offset is out of range: {offset!r}")
        cmd = ":INP{slot:d}:CHAN{channel:d}:OFFS {offset:.3f}dB".format(slot=self._slot, channel=self._channel, offset=offset)
        self.command(cmd)


class BaseModelAQ2200_VOA_with_OPM(BaseModelAQ2200_VOA, TypeOPM):
    """The base class of AQ2200 Series, application type ATTN, with 
    built-in OPM.
    """

    @property
    def min_avg_time(self) -> float:
        """The minimum averaging time in ms."""
        return 10.0   # 10ms

    @property
    def max_avg_time(self) -> float:
        """The maximum averaging time in ms."""
        return 10000.0  # 10s
    
    @property
    def min_pow_cal(self) -> float:
        """The minimum power calibration value in dB."""
        cmd = ":OUTP{slot:d}:CHAN{channel:d}:POW:OFFS? MIN".format(slot=self._slot, channel=self._channel)
        cal = float(self.query(cmd))
        return cal

    @property
    def max_pow_cal(self) -> float:
        """The maximum power calibration value in dB."""
        cmd = ":OUTP{slot:d}:CHAN{channel:d}:POW:OFFS? MAX".format(slot=self._slot, channel=self._channel)
        cal = float(self.query(cmd))
        return cal

    def get_power_value(self) -> float:
        """Fetch the value of measured optical power in current unit setting.

        The measured value includes the power calibration.

        Measured value (dBm) = the actual measured value (dBm) + power calibration (dB)

        Refer to `get_pow_cal` and `set_pow_cal` to operate with the power calibration.

        Returns:
            The value of the optical power.
        """
        cmd = ":FETC{slot}:CHAN{channel}:POW?".format(slot=self._slot, channel=self._channel)
        power = float(self.query(cmd))
        return power

    def get_power_unit(self) -> OpticalPowerUnit:
        """Get optical power unit setting.

        Returns:
            The unit of the optical power.
        """
        cmd = ":OUTP{slot:d}:CHAN{channel:d}:POW:UNIT?".format(slot=self._slot, channel=self._channel)
        unit_int = int(self.query(cmd))
        unit = OpticalPowerUnit(unit_int)
        return unit
    
    def set_power_unit(self, unit: OpticalPowerUnit) -> None:
        """Set the unit of optical power.

        Args:
            unit: The unit of the optical power.
        """
        unit = OpticalPowerUnit(unit)
        cmd = ":OUTP{slot:d}:CHAN{channel:d}:POW:UNIT {unit:d}".format(slot=self._slot, channel=self._channel, unit=unit)
        self.command(cmd)
    
    def get_pow_cal(self) -> float:
        """
        Get the power calibration offset in dB.

        Returns:
            The power calibration offset in dB.
        """
        cmd = ":OUTP{slot:d}:CHAN{channel:d}:POW:OFFS?".format(slot=self._slot, channel=self._channel)
        cal = float(self.query(cmd))
        return cal

    def set_pow_cal(self, value: int | float) -> None:
        """
        Set the power calibration offset in dB.

        Args:
            value: The power calibration offset in dB.
        """
        if not self.min_pow_cal <= value <= self.max_pow_cal:
            raise ValueError(f"Parameter value is out of range: {value!r}")
        cmd = ":OUTP{slot:d}:CHAN{channel:d}:POW:OFFS {value:.3f}DB".format(slot=self._slot, channel=self._channel, value=value)
        self.command(cmd)
    
    def get_avg_time(self) -> float:
        """
        Get the averaging time in ms.

        Returns:
            The averaging time in ms.
        """
        cmd = ":OUTP{slot:d}:CHAN{channel:d}:ATIM?".format(slot=self._slot, channel=self._channel)
        avg_t = float(Decimal(self.query(cmd)) * 1000)
        return avg_t

    def set_avg_time(self, value: int | float) -> None:
        """
        Set the averaging time in ms.

        Args:
            value: The averaging time in ms.
        """
        if not self.min_avg_time <= value <= self.max_avg_time:
            raise ValueError(f"Parameter value is out of range: {value!r}")
        cmd = ":OUTP{slot:d}:CHAN{channel:d}:ATIM {value:d}MS".format(slot=self._slot, channel=self._channel, value=value)
        self.command(cmd)


class BaseModelAQ2200_OPM(VisaInstrument, TypeOPM):
    """Base Model of AQ2200 Series, application type Sensor."""

    def __init__(self, resource_name: str, slot: int, channel: int, **kwargs: Any) -> None:
        """
        Args:
            resource_name: Resource name or alias of the VISA resource to open.
            slot: The slot number in the frame.
            channel: The channel number.
            **kwargs: Directly passed to `VisaInstrument.__init__`
        """
        super(BaseModelAQ2200_OPM, self).__init__(resource_name, read_termination='', **kwargs)
        self._slot = slot
        self._channel = channel

    @property
    def min_frequency(self) -> float:
        """The minimum settable optical frequency value in THz."""
        return super().min_frequency

    @property
    def max_frequency(self) -> float:
        """The maximum settable optical frequency value in THz."""
        return super().max_frequency
    
    @property
    def min_wavelength(self) -> float:
        """The minimum settable optical wavelength value in nm."""
        cmd = ":SENS{slot:d}:CHAN{slot:d}:POW:WAV? MIN".format(slot=self._slot, channel=self._channel)
        wl = float(Decimal(self.query(cmd)) * 10**9)
        return wl
    
    @property
    def max_wavelength(self) -> float:
        """The maximum settable optical wavelength value in nm."""
        cmd = ":SENS{slot:d}:CHAN{slot:d}:POW:WAV? MAX".format(slot=self._slot, channel=self._channel)
        wl = float(Decimal(self.query(cmd)) * 10**9)
        return wl

    @property
    def min_avg_time(self) -> float:
        """The minimum averaging time in ms."""
        return 0.1 # 100us
    
    @property
    def max_avg_time(self) -> float:
        """The maximum averaging time in ms."""
        return 10000.0 # 10s
    
    @property
    def avg_time_table(self) -> tuple:
        """
        AQ-2200 Series OPM only support discrete averaging values. 
        This table contains all the valid averaging time value.

        If the averaging time value set with self.set_avg_time() is not 
        valid, a warning will be displayed and the value will fall back to 
        the closest value in this table. No exception will be raised.
        """
        return (
            0.1, 0.2, 0.5,
            1, 2, 5,
            10, 20, 50,
            100, 200, 500,
            1000, 2000, 5000, 10000,
        )

    @property
    def min_pow_cal(self) -> float:
        """The minimum power calibration value in dB."""
        return -180.0
    
    @property
    def max_pow_cal(self) -> float:
        """The maximum power calibration value in dB."""
        return 200.0

    def get_frequency(self) -> float:
        """
        Queries the optical frequency setting of the instrument in THz.

        Returns:
            The optical frequency setting value in THz.
        """
        return super().get_frequency()

    def set_frequency(self, frequency: int | float) -> None:
        """Set optical frequency.

        Args:
            frequency: The optical frequency setting in THz.
        """
        return super().set_frequency(frequency)

    def get_wavelength(self) -> float:
        """Queries the optical wavelength setting of the instrument in nm.

        Returns:
            The optical wavelength setting value in nm.
        """
        cmd = ":SENS{slot:d}:CHAN{channel:d}:POW:WAV?".format(slot=self._slot, channel=self._channel)
        wl = float(Decimal(self.query(cmd)) * 10 ** 9)
        return wl

    def set_wavelength(self, wavelength: int | float) -> None:
        """Set optical wavelength.

        Args:
            wavelength: The optical wavelength setting in nm.
        """
        if not self.min_wavelength <= wavelength <= self.max_wavelength:
            raise ValueError(f"Parameter wavelength is out of range: {wavelength!r}")
        cmd = ":SENS{slot:d}:CHAN{channel:d}:POW:WAV {wl}NM".format(slot=self._slot, channel=self._channel, wl=wavelength)
        self.command(cmd)

    def get_power_value(self) -> float:
        """Fetch the value of measured optical power in current unit setting.

        The measured value includes the power calibration.

        Measured value (dBm) = the actual measured value (dBm) + power calibration (dB)

        Refer to `get_pow_cal` and `set_pow_cal` to operate with the power calibration.

        Returns:
            The value of the optical power.
        """
        cmd = ":FETC{slot}:CHAN{channel}:POW?".format(slot=self._slot, channel=self._channel)
        power = float(self.query(cmd))
        return power

    def get_power_unit(self) -> OpticalPowerUnit:
        """Get optical power unit setting.

        Returns:
            The unit of the optical power.
        """
        cmd = ":SENS{slot:d}:CHAN{channel:d}:POW:UNIT?".format(slot=self._slot, channel=self._channel)
        unit_int = int(self.query(cmd))
        return OpticalPowerUnit(unit_int)

    def set_power_unit(self, unit: OpticalPowerUnit) -> None:
        """Set the unit of optical power.

        Args:
            unit: The unit of the optical power.
        """
        unit = OpticalPowerUnit(unit)
        cmd = ":SENS{slot:d}:CHAN{channel:d}:POW:UNIT {unit:d}".format(slot=self._slot, channel=self._channel, unit=unit)
        self.command(cmd)

    def get_pow_cal(self) -> float:
        """
        Get the power calibration offset in dB.

        Returns:
            The power calibration offset in dB.
        """
        cmd = ":SENS{slot:d}:CHAN{channel:d}:CORR?".format(slot=self._slot, channel=self._channel)
        cal = float(self.query(cmd))
        return cal

    def set_pow_cal(self, value: int | float) -> None:
        """
        Set the power calibration offset in dB.

        Args:
            value: The power calibration offset in dB.
        """
        if not self.min_pow_cal <= value <= self.max_pow_cal:
            raise ValueError(f"Parameter value is out of range: {value!r}")
        cmd = ":SENS{slot:d}:CHAN{channel:d}:CORR {value:.4f}DB".format(slot=self._slot, channel=self._channel, value=value)
        self.command(cmd)

    def get_avg_time(self) -> float:
        """
        Get the averaging time in ms.

        Returns:
            The averaging time in ms.
        """
        cmd = ":SENS{slot:d}:CHAN{channel:d}:POW:ATIM?".format(slot=self._slot, channel=self._channel)
        avg_t = float(Decimal(self.query(cmd)) * 1000)
        return avg_t

    def set_avg_time(self, value: int | float) -> None:
        """
        Set the averaging time in ms.

        Args:
            value: The averaging time in ms.
        """
        if not self.min_avg_time <= value <= self.max_avg_time:
            raise ValueError(f"Parameter value is out of range: {value!r}")
        
        value = round(value, 1)
        if value in self.avg_time_table:
            valid_value = value
        else:
            l = list(self.avg_time_table)
            l.sort(key = lambda x: abs(x-value))
            valid_value = l[0]
            warnings.warn(
                "Averaging time value {value} not valid. "
                "Fall back to the closest valid value {valid_value}.".format(
                    value=value, valid_value=valid_value), InstrWarning)

        if valid_value < 1:
            v = round(valid_value*1000)
            u = "US"
        else:
            v = valid_value
            u = "MS"

        cmd = ":SENS{slot:d}:CHAN{channel:d}:POW:ATIM {value:d}{unit}".format(
            slot=self._slot, channel = self._channel, value=v, unit=u)
        self.command(cmd)


class ModelAQ2200_215(BaseModelAQ2200_OPM):
    """Yokogawa AQ2200-215 optical power meter."""

    model = "AQ2200-215"

    brand = "Yokogawa"

    details = {
        "Wavelength Range": "970 ~ 1660 nm",
        "Input Power Range": "-70 ~ +30 dBm",
        "Averaging Time": "100us ~ 10s",
    }

    params = [
        {
            "name": "slot",
            "type": "int",
            "min": 1,
            "max": 10
        }
    ]

    def __init__(self, resource_name: str, slot: int, **kwargs: Any) -> None:
        """
        Args:
            resource_name: Resource name or alias of the VISA resource to open.
            slot: The slot number in the frame
            **kwargs: Directly passed to `VisaInstrument.__init__`
        """
        super().__init__(resource_name, slot, channel=1, **kwargs)


class ModelAQ2200_221(BaseModelAQ2200_OPM):
    """Yokogawa AQ2200-221 2-channel optical power meter."""

    model = "AQ2200-221"

    brand = "Yokogawa"

    details = {
        "Wavelength Range": "800 ~ 1700 nm",
        "Input Power Range": "-70 ~ +10 dBm",
        "Averaging Time": "200us ~ 10s",
    }

    params = [
        {
            "name": "slot",
            "type": "int",
            "min": 1,
            "max": 10
        },
        {
            "name": "channel",
            "type": "int",
            "options": [1, 2]
        }
    ]

    @property
    def min_wavelength(self) -> float:
        """The minimum settable optical wavelength value in nm."""
        return 800.0

    @property
    def max_wavelength(self) -> float:
        """The maximum settable optical wavelength value in nm."""
        return 1700.0

    @property
    def min_avg_time(self) -> float:
        """The minimum averaging time in ms."""
        return 0.2
    
    @property
    def avg_time_table(self) -> tuple:
        """
        AQ-2200 Series OPM only support discrete averaging values. 
        This table contains all the valid averaging time value.

        If the averaging time value set with self.set_avg_time() is not 
        valid, a warning will be displayed and the value will fall back to 
        the closest value in this table. No exception will be raised.
        """
        return (
            0.2, 0.5,
            1, 2, 5,
            10, 20, 50,
            100, 200, 500,
            1000, 2000, 5000, 10000,
        )


class ModelAQ2200_311(BaseModelAQ2200_VOA):
    """Yokogawa AQ2200-311 variable optical attenuator."""

    model = "AQ2200-311"

    brand = "Yokogawa"

    details = {
        "Wavelength Range": "1200 ~ 1700 nm",
        "Max Att": "60 dB",
        "Max Safe Input Power": "+23 dBm",
        "Averaging Time": "100 us ~ 10 s",
    }

    params = [
        {
            "name": "slot",
            "type": "int",
            "min": 1,
            "max": 10
        }
    ]
    
    def __init__(self, resource_name: str, slot: int, **kwargs: Any) -> None:
        """
        Args:
            resource_name: Resource name or alias of the VISA resource to open.
            slot: The slot number in the frame
            **kwargs: Directly passed to `VisaInstrument.__init__`
        """
        super().__init__(resource_name, slot, channel=1, **kwargs)


class ModelAQ2200_311A(BaseModelAQ2200_VOA):
    """Yokogawa AQ2200-311A variable optical attenuator."""

    model = "AQ2200-311A"

    brand = "Yokogawa"

    details = {
        "Wavelength Range": "1200 ~ 1700 nm",
        "Max Att": "60 dB",
        "Max Safe Input Power": "+23 dBm",
        "Averaging Time": "100 us ~ 10 s",
    }

    params = [
        {
            "name": "slot",
            "type": "int",
            "min": 1,
            "max": 10
        }
    ]

    def __init__(self, resource_name: str, slot: int, **kwargs: Any) -> None:
        """
        Args:
            resource_name: Resource name or alias of the VISA resource to open.
            slot: The slot number in the frame
            **kwargs: Directly passed to `VisaInstrument.__init__`
        """
        super().__init__(resource_name, slot, channel=1, **kwargs)


class ModelAQ2200_331(BaseModelAQ2200_VOA_with_OPM):
    """Yokogawa AQ2200-331 variable optical attenuator with built-in power meter."""

    model = "AQ2200-331"

    brand = "Yokogawa"

    details = {
        "Wavelength Range": "1200 ~ 1700 nm",
        "Max Att": "60 dB",
        "Max Safe Input Power": "+23 dBm",
        "Averaging Time": "100 us ~ 10 s",
    }

    params = [
        {
            "name": "slot",
            "type": "int",
            "min": 1,
            "max": 10
        }
    ]

    def __init__(self, resource_name: str, slot: int, **kwargs: Any) -> None:
        """
        Args:
            resource_name: Resource name or alias of the VISA resource to open.
            slot: The slot number in the frame
            **kwargs: Directly passed to `VisaInstrument.__init__`
        """
        super().__init__(resource_name, slot, channel=1, **kwargs)


class ModelAQ2200_342(BaseModelAQ2200_VOA_with_OPM):
    """Yokogawa AQ2200-342 variable optical attenuator with built-in power meter."""

    model = "AQ2200-342"

    brand = "Yokogawa"

    details = {
        "Wavelength Range": "1260 ~ 1640 nm",
        "Max Att": "40 dB Min",
        "Max Safe Input Power": "+23 dBm",
        "Averaging Time": "100 us ~ 10 s",
    }

    params = [
        {
            "name": "slot",
            "type": "int",
            "min": 1,
            "max": 10
        },
        {
            "name": "channel",
            "type": "int",
            "options": [1, 2]
        }
    ]


class BaseModel815x_VOA(VisaInstrument, TypeVOA):
    """Base class of Keysight 815x variable optical attenuators."""

    def __init__(self, resource_name: str, slot: int, channel: int, **kwargs: Any):
        """
        Args:
            resource_name: Resource name or alias of the VISA resource to open.
            slot: The slot number in the frame.
            channel: The channel number.
            **kwargs: Directly passed to `VisaInstrument.__init__`
        """
        super().__init__(resource_name, **kwargs)
        self._slot = slot
        self._channel = channel

    @property
    def min_frequency(self) -> float:
        """The minimum settable optical frequency value in THz."""
        return super().min_frequency

    @property
    def max_frequency(self) -> float:
        """The maximum settable optical frequency value in THz."""
        return super().max_frequency

    @property
    def min_wavelength(self) -> float:
        """The minimum settable optical wavelength value in nm."""
        cmd = ":INPut{slot:d}:CHANnel{channel:d}:WAVelength? MIN".format(slot=self._slot, channel=self._channel)
        wl = float(Decimal(self.query(cmd)) * 10**9)
        return wl

    @property
    def max_wavelength(self) -> float:
        """The maximum settable optical wavelength value in nm."""
        cmd = ":INPut{slot:d}:CHANnel{channel:d}:WAVelength? MAX".format(slot=self._slot, channel=self._channel)
        wl = float(Decimal(self.query(cmd)) * 10**9)
        return wl
    
    @property
    def min_att(self) -> float:
        """Minimum settable attenuation in dB.

        The minimum settable attenuation = 0 dB + the optical attenuation 
        offset value.
        """
        cmd = ":INPut{slot:d}:CHANnel{channel:d}:ATTenuation? MIN".format(slot=self._slot, channel=self._channel)
        att = float(self.query(cmd))
        return att

    @property
    def max_att(self) -> float:
        """Maximum settable attenuation in dB.

        The maximum settable attenuation = The maximum attenuation + the 
        optical attenuation offset value.
        """
        cmd = ":INPut{slot:d}:CHANnel{channel:d}:ATTenuation? MAX".format(slot=self._slot, channel=self._channel)
        att = float(self.query(cmd))
        return att
    
    @property
    def min_att_offset(self) -> float:
        """Minimum attenuation offset value in dB."""
        cmd = ":INPut{slot:d}:CHANnel{channel:d}:OFFSet? MIN".format(slot=self._slot, channel=self._channel)
        offset = float(self.query(cmd))
        return offset
    
    @property
    def max_att_offset(self) -> float:
        """Maximum attenuation offset value in dB."""
        cmd = ":INPut{slot:d}:CHANnel{channel:d}:OFFSet? MAX".format(slot=self._slot, channel=self._channel)
        offset = float(self.query(cmd))
        return offset
    
    def get_frequency(self) -> float:
        """
        Queries the optical frequency setting of the instrument in THz.

        Returns:
            The optical frequency setting value in THz.
        """
        return super().get_frequency()

    def set_frequency(self, frequency: int | float) -> None:
        """Set optical frequency.

        Args:
            frequency: The optical frequency setting in THz.
        """
        return super().set_frequency(frequency)

    def get_wavelength(self) -> float:
        """Queries the optical wavelength setting of the instrument in nm.

        Returns:
            The optical wavelength setting value in nm.
        """
        cmd = ":INPut{slot:d}:CHANnel{channel:d}:WAVelength?".format(slot=self._slot, channel=self._channel)
        wl = float(Decimal(self.query(cmd)) * 10**9)
        return wl
    
    def set_wavelength(self, wavelength: int | float) -> None:
        """Set optical wavelength.

        Args:
            wavelength: The optical wavelength setting in nm.
        """
        if not self.min_wavelength <= wavelength <= self.max_wavelength:
            raise ValueError(f"Parameter wavelength is out of range: {wavelength!r}")
        cmd = ":INPut{slot:d}:CHANnel{channel:d}:WAVelength {wl:.4f}NM".format(slot=self._slot, channel=self._channel, wl=wavelength)
        self.command(cmd)
    
    def enable(self, en: bool = True) -> None:
        """
        Enable (disable) the optical output.
        
        Args:
            en: True = Enable, False = Disable.
        """
        if not isinstance(en, bool):
            raise TypeError(f"Parameter en must be a bool, not '{type(en).__name__}'.")
        cmd = ":OUTPut{slot:d}:CHANnel{channel:d}:STATe {state:d}".format(slot=self._slot, channel=self._channel, state=en)
        self.command(cmd)

    def disable(self) -> None:
        """Disable the optical output."""
        self.enable(False)

    def is_enabled(self) -> bool:
        """
        Returns:
            Whether the optical output is enabled.
        """
        cmd = ":OUTPut{slot:d}:CHANnel{channel:d}:STATe?".format(slot=self._slot, channel=self._channel)
        status = bool(int(self.query(cmd)))
        return status
    
    def get_att(self) -> float:
        """
        Get the current attenuation value in dB.
        
        Includes the attenuation offset.

        Queried attenuator = the actual attenuator value + attenuator offset

        Use `get_att_offset` and `set_att_offset` to operate with the 
        attenuator offset.

        Returns:
            The attenuation value in dB.
        """
        cmd = ":INPut{slot:d}:CHANnel{channel:d}:ATTenuation?".format(slot=self._slot, channel=self._channel)
        att = float(self.query(cmd))
        return att
    
    def set_att(self, att: int | float) -> None:
        """
        Set attenuation value in dB.

        Includes the attenuation offset. Refer to `get_att` for more 
        information.

        Args:
            att: The attenuation value in dB.
        """
        if not self.min_att <= att <= self.max_att:
            raise ValueError(f'Parameter att is out of range: {att!r}')
        cmd = ":INPut{slot:d}:CHANnel{channel:d}:ATTenuation {att:.3f}DB".format(slot=self._slot, channel=self._channel, att=att)
        self.command(cmd)
    
    def get_att_offset(self) -> float:
        """
        Get the attenuation offset value in dB.

        Returns:
            The attenuation offset in dB.
        """
        cmd = ":INPut{slot:d}:CHANnel{channel:d}:OFFSet?".format(slot=self._slot, channel=self._channel)
        offset = float(self.query(cmd))
        return offset
    
    def set_att_offset(self, offset: int | float) -> None:
        """
        Set the attenuation offset value in dB.

        Args:
            offset: The attenuation offset in dB.
        """
        if not self.min_att_offset <= offset <= self.max_att_offset:
            raise ValueError(f"Parameter offset is out of range: {offset!r}")
        cmd = ":INPut{slot:d}:CHANnel{channel:d}:OFFSet {offset:.3f}DB".format(slot=self._slot, channel=self._channel, offset=offset)
        self.command(cmd)


class Model81571A(BaseModel815x_VOA):
    """Keysight 81571A variable optical attenuator plug-in module."""

    model = "81571A"

    brand = "Keysight"

    details = {
        "Wavelength Range": "1200 ~ 1700 nm",
        "Att Range": "0 ~ 60 dB",
        "Max Safe Input Power": "+33 dBm"
    }

    params = [
        {
            "name": "slot",
            "type": "int",
            "options": [1, 2, 3, 4]
        }
    ]

    def __init__(self, resource_name: str, slot: int, **kwargs: Any):
        """
        Args:
            resource_name: Resource name or alias of the VISA resource to open.
            slot: The slot number in the frame.
            **kwargs: Directly passed to `VisaInstrument.__init__`
        """
        super().__init__(resource_name, slot, channel=1, **kwargs)


class BaseModel816x_OPM(VisaInstrument, TypeOPM):
    """Base class of Keysight 816x optical power meters.
    
    Note:
        For the Keysight 81635A Dual Power Sensor and Keysight 81619A Dual
        Optical Head Interface module, channel 1 is the primary channel and
        channel 2 is the secondary channel. The primary and secondary channels
        share the same software and hardware triggering system. For some 
        methods, setting parameters for the primary channel sets the 
        parameters for the secondary channel. For these methods, setting for 
        the secondary channel is not allowed.

        Currently, these methods are:

        - `set_avg_time()`

    """

    def __init__(self, resource_name: str, slot: int, channel: int, **kwargs: Any):
        """
        Args:
            resource_name: Resource name or alias of the VISA resource to open.
            slot: The slot number in the frame.
            channel: The channel number.
            **kwargs: Directly passed to `VisaInstrument.__init__`
        """
        super().__init__(resource_name, **kwargs)
        self._slot = slot
        self._channel = channel

    @property
    def min_frequency(self) -> float:
        """The minimum settable optical frequency value in THz."""
        return super().min_frequency

    @property
    def max_frequency(self) -> float:
        """The maximum settable optical frequency value in THz."""
        return super().max_frequency

    @property
    def min_wavelength(self) -> float:
        """The minimum settable optical wavelength value in nm."""
        cmd = ":SENSe{slot:d}:CHANnel{channel:d}:POWer:WAVelength? MIN".format(slot=self._slot, channel=self._channel)
        wl = float(Decimal(self.query(cmd)) * 10**9)
        return wl

    @property
    def max_wavelength(self) -> float:
        """The maximum settable optical wavelength value in nm."""
        cmd = ":SENSe{slot:d}:CHANnel{channel:d}:POWer:WAVelength? MAX".format(slot=self._slot, channel=self._channel)
        wl = float(Decimal(self.query(cmd)) * 10**9)
        return wl

    @property
    def min_avg_time(self) -> float:
        """The minimum averaging time in ms."""
        return 0.1 # 100us

    @property
    def max_avg_time(self) -> float:
        """The maximum averaging time in ms."""
        return 10000 # 10s

    @property
    def min_pow_cal(self) -> float:
        """The minimum power calibration value in dB."""
        return -200

    @property
    def max_pow_cal(self) -> float:
        """The maximum power calibration value in dB."""
        return 200

    def get_frequency(self) -> float:
        """
        Queries the optical frequency setting of the instrument in THz.

        Returns:
            The optical frequency setting value in THz.
        """
        return super().get_frequency()

    def set_frequency(self, frequency: int | float) -> None:
        """Set optical frequency.

        Args:
            frequency: The optical frequency setting in THz.
        """
        return super().set_frequency(frequency)

    def get_wavelength(self) -> float:
        """Queries the optical wavelength setting of the instrument in nm.

        Returns:
            The optical wavelength setting value in nm.
        """
        cmd = ":SENSe{slot:d}:CHANnel{channel:d}:POWer:WAVelength?".format(slot=self._slot, channel=self._channel)
        wl = float(Decimal(self.query(cmd)) * 10**9)
        return wl

    def set_wavelength(self, wavelength: int | float) -> None:
        """Set optical wavelength.

        Args:
            wavelength: The optical wavelength setting in nm.
        """
        if not self.min_wavelength <= wavelength <= self.max_wavelength:
            raise ValueError(f"Parameter wavelength is out of range: {wavelength!r}")
        cmd = ":SENSe{slot:d}:CHANnel{channel:d}:POWer:WAVelength {wl:.4f}NM".format(slot=self._slot, channel=self._channel, wl=wavelength)
        self.command(cmd)

    def get_power_value(self) -> float:
        """Fetch the value of measured optical power in current unit setting.

        The measured value includes the power calibration.

        Measured value (dBm) = the actual measured value (dBm) + power calibration (dB)

        Refer to `get_pow_cal` and `set_pow_cal` to operate with the power calibration.

        Returns:
            The value of the optical power.
        """
        cmd = ":FETCh{slot:d}:CHANnel{channel:d}:POWer?".format(slot=self._slot, channel=self._channel)
        value = float(Decimal(self.query(cmd)))
        return value

    def get_power_unit(self) -> OpticalPowerUnit:
        """Get optical power unit setting.

        Returns:
            The unit of the optical power.
        """
        cmd = ":SENSe{slot:d}:CHANnel{channel:d}:POWer:UNIT?".format(slot=self._slot, channel=self._channel)
        unit_int = int(self.query(cmd))
        return OpticalPowerUnit(unit_int)

    def set_power_unit(self, unit: OpticalPowerUnit) -> None:
        """Set the unit of optical power.

        Args:
            unit: The unit of the optical power.
        """
        unit = OpticalPowerUnit(unit)
        cmd = ":SENSe{slot:d}:CHANnel{channel:d}:POWer:UNIT {unit:d}".format(slot=self._slot, channel=self._channel, unit=unit)
        self.command(cmd)

    def get_pow_cal(self) -> float:
        """
        Get the power calibration offset in dB.

        Returns:
            The power calibration offset in dB.
        """
        cmd = ":SENSe{slot:d}:CHANnel{channel:d}:CORRection?".format(slot=self._slot, channel=self._channel)
        cal = float(self.query(cmd))
        return cal

    def set_pow_cal(self, value: int | float) -> None:
        """
        Set the power calibration offset in dB.

        Args:
            value: The power calibration offset in dB.
        """
        if not self.min_pow_cal <= value <= self.max_pow_cal:
            raise ValueError(f"Parameter value is out of range: {value!r}")
        cmd = ":SENSe{slot:d}:CHANnel{channel:d}:CORRection {value:.4f}DB".format(slot=self._slot, channel=self._channel, value=value)
        self.command(cmd)

    def get_avg_time(self) -> float:
        """
        Get the averaging time in ms.

        Returns:
            The averaging time in ms.
        """
        cmd = ":SENSe{slot:d}:CHANnel{channel:d}:POWer:ATIMe?".format(slot=self._slot, channel=self._channel)
        avg_t = float(Decimal(self.query(cmd)) * 1000)
        return avg_t
    
    def set_avg_time(self, value: int | float) -> None:
        """
        Set the averaging time in ms. 

        Note:
            Can only be sent to primary channel, and secondary channel is 
            also affected.

        Args:
            value: The averaging time in ms.
        """
        if not self.min_avg_time <= value <= self.max_avg_time:
            raise ValueError(f"Parameter value is out of range: {value!r}")
        cmd = ":SENSe{slot:d}:CHANnel{channel:d}:POWer:ATIMe {value:.4f}".format(slot=self._slot, channel=self._channel, value=value)
        self.command(cmd)


class Model81635A(BaseModel816x_OPM):
    """Keysight 81635A optical power meter plug-in module."""

    brand = "Keysight"

    model = "81635A"

    details = {
        "Wavelength Range": "800 ~ 1650 nm",
        "Input Power Range": "-80 ~ +10 dBm",
        "Max Safe Input Power": "+16 dBm",
        "Averaging Time": "100 us ~ 10 s",
    }

    params = [
        {
            "name": "slot",
            "type": "int",
            "options": [1, 2, 3, 4]
        },
        {
            "name": "channel",
            "type": "int",
            "options": [1, 2]
        }
    ]


# Review paused here
class BaseModelVSA89600(VisaInstrument):
    """The base class of instrument models based on Keysight 89600 VSA software."""

    def __init__(self, resource_name: str, encoding: str = 'latin1', **kwargs: Any):
        """
        Args:
            resource_name: Resource name or alias of the VISA resource to open.
            encoding: The encoding of the VISA IO string.
            **kwargs: Directly passed to `VisaInstrument.__init__`.
        """
        super().__init__(resource_name, encoding=encoding, **kwargs)
        self.__custom_measurement_demod_filters = { "None", "Rectangular", "RootRaisedCosine", "Gaussian", "LowPass" }
        self.__custom_reference_demod_filters = { "Rectangular", "RaisedCosine", "RootRaisedCosine", "Gaussian", "HalfSine" }

    @property
    def CUSTOM_DEMOD_MEASUREMENT_FILTERS(self) -> set:
        """Options for custom demod measurement filter types."""
        return self.__custom_measurement_demod_filters

    @property
    def CUSTOM_DEMOD_REFERENCE_FILTERS(self) -> set:
        """Options for custom demod reference filter types."""
        return self.__custom_reference_demod_filters

    def run(self, _run: bool = True) -> None:
        """Resume or stop the measurement.
        
        Args:
            _run: `True` = Run the measurement. `False` = Stops the 
                measurement and clears all measurement data.
        """
        if _run:
            self.command(":INITiate:RESume")
        else:
            self.command(":INITiate:ABORt")
        
    def stop(self) -> None:
        """Stops the measurement and clears all measurement data."""
        self.run(False)

    def pause(self) -> None:
        """Causes the measurement to transition to the Paused state."""
        self.command(":INITiate:PAUSe")

    def restart(self) -> None:
        """Causes the measurement to restart. The Average count is reset to 0 
        and the measurement transitions to the Running State.
        """
        self.command(":INITiate:RESTart")
    
    def get_data_table_names(self, trace: int) -> List[str]:
        """
        Returns a list of all names in the data table for the specified trace.

        Args:
            trace: The index of trace, 1 based from A. For example, A->1, E->5
        
        Returns:
            A list of all parameter names in the data table.
        """
        if not trace >= 1:
            raise ValueError(f'Parameter trace must start from 1, got {trace!r}')
        name_str = self.query(":TRACe{trace:d}:DATA:TABLe:NAME?".format(trace=trace))
        name_list = list(map(lambda x: x.strip('"'), name_str.split(",")))
        return name_list

    def get_data_table_values(self, trace: int) -> List[int | float | str]:
        """Gets a list of values from a data table. Enum values are returned 
        as enum indexes (`int` type). Numeric values are returned as `int` or 
        `float`. Other values are returned as `str`.

        Args:
            trace: The index of trace, 1 based from A. For example, A->1, E->5

        Returns:
            A list of all parameter values in the data table.
        """
        if not trace >= 1:
            raise ValueError(f'Parameter trace must start from 1, got {trace!r}')
        value_str = self.query(":TRACe{trace:d}:DATA:TABLe?".format(trace=trace))
        raw_values = value_str.strip().split(",")
        values = []
        for r_val in raw_values:
            try:
                val = int(r_val)
            except ValueError:
                try:
                    val = float(r_val)
                except:
                    val = r_val
            values.append(val)
        return values

    def get_data_table_units(self, trace: int) -> List[str]:
        """
        Get all the units in the data table of the specified trace.

        Args:
            trace: The index of trace, 1 based from A. For example, A->1, E->5

        Returns:
            A list of all parameter units in the data table.
        """
        if not trace >= 1:
            raise ValueError(f'Parameter trace must start from 1, got {trace!r}')
        unit_str = self.query(':TRACe{trace:d}:DATA:TABLe:UNIT?'.format(trace=trace))    
        unit_list = list(map(lambda x: x.strip('"'), unit_str.split(",")))
        return unit_list

    def get_data_table(self, trace: int) -> Dict[str, Tuple[int | float | str, str]]:
        """
        Get formatted data including table item names, values, and units.

        Args:
            trace: The index of trace, 1 based from A. For example, A->1, E->5

        Returns:
            A dict represents the data table. The format is:

            name => (value, unit)
        """
        names = self.get_data_table_names(trace)
        values = self.get_data_table_values(trace)
        units = self.get_data_table_units(trace)
        if len(names) == len(values) == len(units):
            i_len = len(names)
        else:
            raise IndexError('Numbers of names, values and units do not match.')
        data = {}
        for i in range(i_len):
            data[names[i]] = (values[i], units[i])
        return data

    def get_custom_demod_measurement_filter(
            self) -> Literal["None", "Rectangular", "RootRaisedCosine", 
            "Gaussian", "LowPass"]:
        """Queries the measurement filter applied during the digital demodulation 
        measurement.

        Returns:
            The custom demod measurement filter type. Options: "None", 
                "Rectangular", "RootRaisedCosine", "Gaussian", "LowPass"
        """
        cmd = ":CDEMod:FILTer?"
        filter_type = self.query(cmd).strip().strip('"')
        return filter_type

    def set_custom_demod_measurement_filter(
            self, filter_type: Literal["None", "Rectangular", 
            "RootRaisedCosine", "Gaussian", "LowPass"]) -> None:
        """Sets the measurement filter applied during the digital demodulation 
        measurement.

        Args:
            filter_type: The custom demod measurement filter type. Options: 
                "None", "Rectangular", "RootRaisedCosine", "Gaussian", "LowPass"
        """
        if filter_type not in self.CUSTOM_DEMOD_MEASUREMENT_FILTERS:
            raise ValueError('Invalid filter_type: {filter!r}'.format(filter=filter_type))
        cmd = ":CDEMod:FILTer \"{filter}\"".format(filter=filter_type)
        self.command(cmd)

    def get_custom_demod_reference_filter(
            self) -> Literal["Rectangular", "RaisedCosine", 
            "RootRaisedCosine", "Gaussian", "HalfSine"]:
        """Queries the reference filter applied during the digital demodulation 
        measurement.

        Returns:
            The custom demod reference filter type. Options: "Rectangular", 
                "RaisedCosine", "RootRaisedCosine", "Gaussian", "HalfSine"
        """
        cmd = ':CDEMod:FILTer:REFerence?'
        filter_type = self.query(cmd).strip().strip('"')
        return filter_type

    def set_custom_demod_reference_filter(self, filter_type: str) -> None:
        """Sets the reference filter applied during the digital demodulation 
        measurement.

        Args:
            filter_type: The custom demod reference filter type. Options: 
                "Rectangular", "RaisedCosine", "RootRaisedCosine", 
                "Gaussian", "HalfSine"
        """
        if filter_type not in self.CUSTOM_DEMOD_REFERENCE_FILTERS:
            raise ValueError('Invalid filter_type: {filter!r}'.format(filter=filter_type))
        cmd = ":CDEMod:FILTer:REFerence \"{filter}\"".format(filter=filter_type)
        self.command(cmd)

    def get_custom_demod_filter_abt(self) -> float:
        """Queries the α (alpha) or BT (bandwidth time product) parameter for 
        custom demod measurement and reference filters.

        Returns:
            The α (alpha) or BT (bandwidth time product) parameter.
        """
        cmd = ':CDEMod:FILTer:ABT?'
        abt = float(self.query(cmd))
        return abt

    def set_custom_demod_filter_abt(self, abt: int | float) -> None:
        """Sets the α (alpha) or BT (bandwidth time product) parameter for 
        custom demod measurement and reference filters.

        Args:
            abt: The α (alpha) or BT (bandwidth time product) parameter.
        """
        cmd = ':CDEMod:FILTer:ABT {value:f}'.format(value=round(abt, 6))
        self.command(cmd)

    def get_custom_demod_equalization_state(self) -> bool:
        """Queries a value indicating whether the equalization filter is enabled.

        Returns:
            Whether the equalization filter is enabled.
        """
        cmd = ':CDEMod:COMPensate:EQUalize?'
        state = bool(int(self.query(cmd)))
        return state

    def set_custom_demod_equalization_state(self, enable: bool) -> None:
        """
        Enables or disables the equalization filter.

        Args:
            enable: True = enable, False = disable
        """
        if not isinstance(enable, bool):
            raise TypeError(f"Parameter enable must be a bool, not '{type(enable).__name__}'.")
        cmd = ':CDEMod:COMPensate:EQUalize {state:d}'.format(state=enable)
        self.command(cmd)

    def get_custom_demod_equalization_length(self) -> int:
        """Queries the length of the equalization filter in symbols.
        
        Returns:
            The length of the equalization filter in symbols.
        """
        cmd = ':CDEMod:COMPensate:EQUalize:LENGth?'
        rpl = self.query(cmd)
        return int(rpl)

    def set_custom_demod_equalization_length(self, symbols: int) -> None:
        """Sets the length of the equalization filter in symbols.
        
        Args:
            symbols: The length of the equalization filter in symbols.
        """
        if not symbols >= 3:
            raise ValueError('Parameter symbols should >= 3, got {symbols!r}'.format(symbols=symbols))
        cmd = ':CDEMod:COMPensate:EQUalize:LENGth {value:d}'.format(value=symbols)
        self.command(cmd)
        
    def get_custom_demod_equalization_convergence(self) -> float:
        """Queries the convergence parameter for the Adaptive Equalizer.
        
        Returns:
            The equalization convergence parameter.
        """
        cmd = ":CDEMod:COMPensate:EQUalize:CONVergence?"
        return float(self.query(cmd))

    def set_custom_demod_equalization_convergence(self, value: int | float) -> None:
        """Sets the convergence parameter for the Adaptive Equalizer.
        
        Args:
            value: The equalization convergence parameter.
        """
        if not 1E-8 <= value <= 1e-6:
            raise ValueError(f'Invalid value for EQ convergence: {value!r}, must be between 1E-6 and 1E-8.')
        cmd = ':CDEMod:COMPensate:EQUalize:CONVergence {value:.4E}'.format(value=value)
        self.command(cmd)

    def get_custom_demod_equalizer_run_mode(self) -> Literal["Run", "Hold"]:
        """
        Queries the run mode of the Adaptive Equalizer.

        Returns:
            The run mode. Options: "Run" | "Hold".
        """
        cmd = ':CDEMod:COMPensate:EQUalize:MODE?'
        mode = self.query(cmd).strip().strip('"')
        return mode

    def set_custom_demod_equalizer_run_mode(self, mode: Literal["Run", "Hold"]) -> None:
        """
        Sets the run mode of the Adaptive Equalizer.

        Args:
            mode: The run mode. Options: "Run" | "Hold".
        """
        MODES = { "Run", "Hold" }
        if mode not in MODES:
            raise ValueError('Invalid value for Custom Demod EQ run mode: {vlaue!r}'.format(mode))
        cmd = ':CDEMod:COMPensate:EQUalize:MODE "{value}"'.format(value=mode)
        self.command(cmd)

    def reset_custom_demod_equalizer(self) -> None:
        """Reset the custom demod equalizer filter."""
        cmd = ':CDEMod:COMPensate:EQUalize:RESet'
        self.command(cmd)

    def get_custom_demod_result_length(self) -> int:
        """Queries the demodulation measurement result length (in symbols).

        Returns:
            The result length in symbols.
        """
        cmd = ':CDEMod:RLENgth?'
        l = int(self.query(cmd))
        return l

    def set_custom_demod_result_length(self, length: int) -> None:
        """Sets the demodulation measurement result length (in symbols).

        Args:
            length: The result length in symbols.
        """
        cmd = ':CDEMod:RLENgth {v:d}'.format(v=length)
        self.command(cmd)

    def get_custom_demod_reference(self) -> str:
        """Queries the reference used for normalization of IQ traces and EVM 
        calculations.

        Returns:
            The reference type. Possible return values: 
                `ConstellationMaximum` | `ReferenceRms`
        """
        cmd = f':CDEMod:COMPensate:NREFerence?'
        return self.query(cmd).strip()

    def set_custom_demod_reference(self, ref_type: str) -> None:
        """Sets the reference used for normalization of IQ traces and EVM 
        calculations.

        Args:
            ref_type: The reference type. Options: 
                `ConstellationMaximum` | `ReferenceRms`
        """
        if ref_type not in {"ConstellationMaximum", "ReferenceRms"}:
            raise ValueError(f"Invaild ref_type: {ref_type!r}")
        cmd = f':CDEMod:COMPensate:NREFerence "{ref_type}"'
        return self.command(cmd)


class BaseModelVSA89600_OMA(BaseModelVSA89600, TypeOMA):
    """Base class for Keysight OMA models based on VSA 89600 software:
    
    - M8290A
    - N4392A
    """

    @property
    def DEMOD_FORMATS(self):
        """Valid options for demod format."""
        options = (
            "Qam8", "Qam16", "Qam32", "Qam64", "Qam256", "Qpsk", 
            "DifferentialQpsk", "Pi4DifferentialQpsk", 
            "OffsetQpsk", "Bpsk", "Psk8", "Msk", "Msk2", 
            "Fsk2", "Fsk4", "DvbQam16", "DvbQam32", 
            "DvbQam64", "Vsb8", "Vsb16", "Edge", "Fsk8", 
            "Fsk16", "Qam128", "DifferentialPsk8", 
            "Qam512", "Qam1024", "Apsk16", "Apsk16Dvb", 
            "Apsk32", "Apsk32Dvb", "DvbQam128", 
            "DvbQam256", "Pi8DifferentialPsk8", "CpmFM", 
            "Star16Qam", "Star32Qam", "CustomApsk", 
            "ShapedOffsetQpsk", "Ask4"
        )
        return options

    @property
    def POLARIZATIONS(self):
        """Valid options for polarization configuration."""
        options = ("Single", "Dual", "Auto")
        return options

    def get_frequency(self) -> float:
        """
        Queries the optical frequency setting of the instrument in THz.

        Returns:
            The optical frequency setting value in THz.
        """
        cmd = ":OMA:SMartSEtup:CarrierFrequency:FRErequency?"
        freq = float(Decimal(self.query(cmd)) / 10**12)
        return freq

    def set_frequency(self, frequency: int | float) -> None:
        """Set optical frequency.

        Args:
            frequency: The optical frequency setting in THz.
        """
        self.smart_setup(frequency=frequency, pre_set_layout=False)

    def get_wavelength(self) -> float:
        """Queries the optical wavelength setting of the instrument in nm.

        Returns:
            The optical wavelength setting value in nm.
        """
        cmd = ":OMA:SMartSEtup:CarrierFrequency:WaVeLength?"
        wl = float(self.query(cmd))
        return wl

    def set_wavelength(self, wavelength: int | float) -> None:
        """Set optical wavelength.

        Args:
            wavelength: The optical wavelength setting in nm.
        """
        self.smart_setup(wavelength=wavelength, pre_set_layout=False)

    def smart_setup(
        self,
        execute: bool = True,
        *,
        frequency: Optional[int | float] = None, 
        wavelength: Optional[int | float] = None,
        symbol_rate: Optional[int | float] = None, 
        fine_tune_symbol_rate: Optional[bool] = None, 
        modulation_format: Optional[str] = None, 
        polarization: Optional[str] = None, 
        pre_set_layout: Optional[bool] = None, 
        compensate_cd: Optional[bool] = None, 
        compensate_pmd: Optional[bool] = None):
        """Perform smart setup of the OMA. Use parameter `execute` to choose 
        whether to execute the changed settings or not. If a setting parameter 
        is not explicitly given (default as None), the old setting will be 
        kept.

        Args:
            execute: Whether to execute smart setup with the new settings. If 
                set to False, the settings of smart setup will be changed, 
                but the OMA will not execute smart setup.
            frequency: The carrier frequency in THz.
            wavelength: The carrier wavelength in nm. This parameter could not be set if frequency is set.
            symbol_rate: The symbol rate in GHz.
            fine_tune_symbol_rate: Whether the system should try to fine tune the symbol rate.
            modulation_format: The selected digital demodulation format. 
                Refer to `DEMOD_FORMATS` for options.
            polarization: The expected polarization or if auto detection should be used. 
                options: `"Single"` | `"Dual"` | `"Auto"`.
            pre_set_layout: Whether a preset of the trace layout should be performed.
            compensate_cd: A value indicating whether CD should be compensated.
            compensate_pmd: A value indicating whether PMD should be compensated.
        """
        if frequency is not None and wavelength is not None:
            raise ValueError('You could not set both frequency and wavelength at the same time.')

        if frequency is not None:
            if not self.min_frequency <= frequency <= self.max_frequency:
                raise ValueError(f"Parameter frequency is out of range: {frequency!r}")
            self.command(':OMA:SMartSEtup:CarrierFrequency:FRErequency {value:d}'.format(value=round(frequency * 10**12)))

        if wavelength is not None:
            if not self.min_wavelength <= wavelength <= self.max_wavelength:
                raise ValueError(f"Parameter wavelength is out of range: {wavelength!r}")
            self.command(f":OMA:SMartSEtup:CarrierFrequency:WaVeLength {wavelength:.4f}")

        if symbol_rate is not None:
            self.command(':OMA:SMartSEtup:SYMBRate {value:d}'.format(value=round(symbol_rate*10**9)))

        if fine_tune_symbol_rate is not None:
            if not isinstance(fine_tune_symbol_rate, bool):
                raise TypeError(f"Parameter fine_tune_symbol_rate must be a bool, not '{type(fine_tune_symbol_rate).__name__}'.")
            self.command(':OMA:SMartSEtup:FINetuneSymbolRate {enable:d}'.format(enable=fine_tune_symbol_rate))

        if modulation_format is not None:
            if modulation_format not in self.DEMOD_FORMATS:
                raise ValueError('Invalid modulation demodulation format: {format!r}'.format(format=modulation_format))
            self.command(':OMA:SMartSEtup:FORMat "{format}"'.format(format=modulation_format))

        if polarization is not None:
            if not polarization in self.POLARIZATIONS:
                raise ValueError('Invalid polarization: {pol!r}'.format(pol=polarization))
            self.command(':OMA:SMartSEtup:POLarization "{pol}"'.format(pol=polarization))

        if pre_set_layout is not None:
            if not isinstance(pre_set_layout, bool):
                raise TypeError(f"Parameter pre_set_layout must be a bool, not '{type(pre_set_layout).__name__}'.")
            self.command(':OMA:SMartSEtup:PREsetLAyout {enable:d}'.format(enable=pre_set_layout))

        if compensate_cd is not None:
            if not isinstance(compensate_cd, bool):
                raise TypeError(f"Parameter compensate_cd must be a bool, not '{type(compensate_cd).__name__}'.")
            self.command(':OMA:SMartSEtup:COmpensateCD {:d}'.format(compensate_cd))

        if compensate_pmd is not None:
            if not isinstance(compensate_pmd, bool):
                raise TypeError(f"Parameter compensate_pmd must be a bool, not '{type(compensate_pmd).__name__}'.")
            self.command(':OMA:SMartSEtup:COmpensatePMD {:d}'.format(compensate_pmd))

        if execute:
            self.command(':OMA:SMartSEtup:PERformProposedActions')


class ModelN4392A(BaseModelVSA89600_OMA):
    """N4392A Optical Modulation Analyzer."""

    model = "N4392A"

    brand = "Keysight"

    details = {
        "Maximum detectable baud rate": "46 Gbaud",
        "Optical frequency range": "196.25 ~ 190.95 THz",
        "External LO input power range": "-3 ~ +16 dBm",
    }

    def __init__(self, resource_name: str, **kwargs: Any):
        """
        Args:
            resource_name: Resource name or alias of the VISA resource to open.
            **kwargs: Directly passed to `VisaInstrument.__init__`.
        """
        super(ModelN4392A, self).__init__(resource_name, **kwargs)

    @property
    def min_frequency(self) -> float:
        """The minimum settable optical frequency value in THz."""
        return 190.95

    @property
    def max_frequency(self) -> float:
        """The maximum settable optical frequency value in THz."""
        return 196.25

    @property
    def min_wavelength(self) -> float:
        """The minimum settable optical wavelength value in nm."""
        return super().min_wavelength

    @property
    def max_wavelength(self) -> float:
        """The maximum settable optical wavelength value in nm."""
        return super().max_wavelength


class ModelM8292A(BaseModelVSA89600_OMA):
    """M8292A Optical Modulation Analyzer"""

    model = "M8292A"

    brand = "Keysight"

    details = {
        "Maximum detectable symbol rate": "74 GBd",
        "Optical frequency range": "196.25 ~ 190.95 THz",
        "Max signal input power": "+14.5 dBm",
        "External LO input power": "+17 dBm",
    }

    def __init__(self, resource_name: str, **kwargs: Any):
        """
        Args:
            resource_name: Resource name or alias of the VISA resource to open.
            **kwargs: Directly passed to `VisaInstrument.__init__`.
        """
        super(ModelM8292A, self).__init__(resource_name, **kwargs)

    @property
    def min_frequency(self) -> float:
        """The minimum settable optical frequency value in THz."""
        return 190.95

    @property
    def max_frequency(self) -> float:
        """The maximum settable optical frequency value in THz."""
        return 196.25

    @property
    def min_wavelength(self) -> float:
        """The minimum settable optical wavelength value in nm."""
        return super().min_wavelength

    @property
    def max_wavelength(self) -> float:
        """The maximum settable optical wavelength value in nm."""
        return super().max_wavelength


class BaseModelAQ63xx(VisaInstrument, TypeOSA):
    """
    Optical Spectrum Analyzer AQ6360 and AQ6370 series from Yokogawa.
    """

    ANALYSIS_CATEGORIES = (
        "SWTHRESH",
        "DFBLD",
        "SMSR",
        "WDM",
    )

    SWEEP_MODES = ("AUTO", "REPEAT", "SINGLE", "STOP")

    MARKER_NUMBERS = (0, 1, 2, 3, 4)

    X_SCALES = ("WAV", "FREQ")

    WL_UNITS = ("NM", "THZ")

    _resolution_table = {
        'NM': [],
        'GHZ': []
    }

    _x_span_range = {
        'NM': [],
        'GHZ': []
    }

    def __init__(self, resource_name: str, **kwargs: Any):
        """
        Args:
            resource_name: Resource name or alias of the VISA resource to open.
            **kwargs: Directly passed to `VisaInstrument.__init__`.
        """
        super(BaseModelAQ63xx, self).__init__(resource_name, **kwargs)
        self.command(':FORMat:DATA ASCii')  # set data format to ascii

    @property
    def min_frequency(self) -> float:
        """The minimum settable optical frequency value in THz."""
        return super().min_frequency

    @property
    def max_frequency(self) -> float:
        """The maximum settable optical frequency value in THz."""
        return super().max_frequency

    def get_x_scale(self) -> Literal["WAV", "FREQ"]:
        """Queries the horizontal scale.

        Returns:
            `WAV` = Wavelength, `FREQ` = Frequency
        """
        cmd = ":UNIT:X?"
        scale = self.X_SCALES[int(self.query(cmd))]
        return scale

    def set_x_scale(self, scale: Literal["WAV", "FREQ"]) -> None:
        """Sets the horizontal scale.
        
        Args:
            scale: `WAV` = Wavelength, `FREQ` = Frequency
        """
        if scale not in self.X_SCALES:
            raise ValueError(f"Invalid value for parameter scale: {scale!r}")
        cmd = f":UNIT:X {scale}"
        self.command(cmd)

    def get_resolution_bandwidth(self) -> float:
        """Queries the measurement resolution bandwidth.

        Returns:
            The resolution bandwidth. If x scale is "WAV", returns the 
                resolution in nm. If x scale is "FREQ", returns the 
                resolution in GHz.

                Please refer to `get_x_scale` for more information.
        """
        cmd = ":SENSe:BANDwidth?"
        if "WAV" == self.get_x_scale():
            res = float(Decimal(self.query(cmd)) * 10**9)
        else:
            res = float(Decimal(self.query(cmd)) / 10**9)
        return res

    def set_resolution_bandwidth(self, bandwidth: int | float) -> None:
        """Sets the measurement resolution bandwidth.

        Note that only particular values could be set. If the setting value 
        is not contained in these values, it will set to the nearest valid 
        value.

        You can get these values for both x scale via `_resolution_table` 
        property.

        Please refer to `get_x_scale` for more information.

        Args:
            bandwidth: The resolution bandwidth. If x scale is "WAV", the 
                unit is nm. If x scale is "FREQ", the unit is GHz.
        """
        unit = "NM" if self.get_x_scale() == "WAV" else "GHZ"
        min_bw = self._resolution_table[unit][0]  # first in table
        max_bw = self._resolution_table[unit][-1] # last in table
        if not min_bw <= bandwidth <= max_bw:
            raise ValueError(f"Parameter bandwidth must be in range [{min_bw}, {max_bw}], got {bandwidth!r}")
        cmd = ":SENSe:BANDwidth {bandwidth:.6f}{unit}".format(bandwidth=bandwidth, unit=unit)
        self.command(cmd)

    def set_center(self, value: int | float, unit: str) -> None:
        """Sets the measurement center wavelength/frequency.
        
        Args:
            value: The center wavelength in nm or frequency in THz.
            unit: `NM` or `THZ`.
        """
        if unit.upper() not in self.WL_UNITS:
            raise ValueError('Invalid option for unit: {unit!r}.'.format(unit=unit))
        cmd = ":SENSe:WAVelength:CENTer {value:.4f}{unit}".format(value=value, unit=unit)
        self.command(cmd)

    def set_wavelength(self, wavelength: int | float) -> None:
        """Set optical wavelength.

        Args:
            wavelength: The optical wavelength setting in nm.
        """
        if not self.min_wavelength <= wavelength <= self.max_wavelength:
            raise ValueError(f"Parameter wavelength is out of range: {wavelength!r}")
        self.set_center(wavelength, 'NM')
    
    def set_frequency(self, frequency: int | float) -> None:
        """Set optical frequency.

        Args:
            frequency: The optical frequency setting in THz.
        """
        if not self.min_frequency <= frequency <= self.max_frequency:
            raise ValueError(f"Parameter frequency is out of range: {frequency!r}")
        return self.set_center(frequency, 'THZ')

    def get_center(self) -> float:
        """
        Queries the measurement center wavelength/frequency.
        
        Returns:
            The of center frequency/wavelength value. If x scale is 
                "WAV", returns the center wavelength in nm. If x scale is 
                "FREQ", returns the center frequency in THz.

                Please refer to `get_x_scale` for more information.
        """
        cmd = ":SENSe:WAVelength:CENTer?"
        if "WAV" == self.get_x_scale():
            center = float(Decimal(self.query(cmd)) * 10**9)
        else:
            center = float(Decimal(self.query(cmd)) / 10**12)
        return center

    def get_wavelength(self) -> float:
        """Queries the optical wavelength setting of the instrument in nm.

        Returns:
            The optical wavelength setting value in nm.
        """
        if "WAV" == self.get_x_scale():
            cmd = ":SENSe:WAVelength:CENTer?"
            wl = float(Decimal(self.query(cmd)) * 10**9)
        else:
            wl = super().get_wavelength()
        return wl

    def get_frequency(self) -> float:
        """
        Queries the optical frequency setting of the instrument in THz.

        Returns:
            The optical frequency setting value in THz.
        """
        if "FREQ" == self.get_x_scale():
            cmd = ":SENSe:WAVelength:CENTer?"
            freq = float(Decimal(self.query(cmd)) / 10**12)
        else:
            freq = super().get_frequency()
        return freq

    def set_span(self, value: int | float) -> None:
        """Sets the measurement condition measurement span.

        If the horizontal scale is "WAV", the span unit is nm. If the 
        horizontal scale is "FREQ", the span unit is GHz.

        Please refer to `get_x_scale` for more information.

        Args:
            value: The value of measurement span. The unit depends on the 
                horizontal setting.
        """
        unit = "NM" if self.get_x_scale() == "WAV" else "GHZ"
        min_span, max_span = self._x_span_range[unit]
        if not min_span <= value <= max_span:
            raise ValueError(f"Parameter value must be in range [{min_span}, {max_span}], got {value!r}")
        cmd = ":SENSe:WAVelength:SPAN {value:.2f}{unit}".format(value=value, unit=unit)
        self.command(cmd)

    def get_span(self) -> float:
        """Queries the measurement condition measurement span in specified unit.
        
        If the horizontal scale is "WAV", the span unit is nm. If the 
        horizontal scale is "FREQ", the span unit is GHz.

        Please refer to `get_x_scale` for more information.

        Returns:
            The value of measurement span. The unit depends on the horizontal 
                setting.
        """
        cmd = ":SENSe:WAVelength:SPAN?"
        if "WAV" == self.get_x_scale():
            span = float(Decimal(self.query(cmd)) * 10**9)
        else:
            span = float(Decimal(self.query(cmd)) / 10**9)
        
        return span

    def get_start_wavelength(self) -> float:
        """Queries the measurement start wavelength in nm.
        
        Returns:
            The start wavelength in nm.
        """
        if "WAV" == self.get_x_scale():
            cmd = ":SENSe:WAVelength:STARt?"
            wl = float(Decimal(self.query(cmd)) * 10**9)
        else:
            cmd = ":SENSe:WAVelength:STOP?"
            wl = LIGHTSPEED/(float(self.query(cmd)) / 10**12)
        return wl

    def set_start_wavelength(self, wavelength: int | float) -> None:
        """Sets the measurement start wavelength in nm.
        
        Args:
            wavelength: The start wavelength in nm.
        """
        if not self.min_wavelength <= wavelength <= self.max_wavelength:
            raise ValueError(f"Parameter wavelength is out of range: {wavelength!r}")
        if "WAV" == self.get_x_scale():
            cmd = ":SENSe:WAVelength:STARt {wl:.6f}NM".format(wl=wavelength)
        else:
            cmd = ":SENSe:WAVelength:STOP {wl:.6f}NM".format(wl=wavelength)
        self.command(cmd)

    def get_stop_wavelength(self) -> float:
        """Queries the measurement stop wavelength in nm.
        
        Returns:
            The stop wavelength in nm.
        """
        if "WAV" == self.get_x_scale():
            cmd = ":SENSe:WAVelength:STOP?"
            wl = float(Decimal(self.query(cmd)) * 10**9)
        else:
            cmd = ":SENSe:WAVelength:STARt?"
            wl = LIGHTSPEED/(float(self.query(cmd)) / 10**12)
        return wl

    def set_stop_wavelength(self, wavelength: int | float) -> None:
        """Sets the measurement stop wavelength in nm.
        
        Args:
            wavelength: The stop wavelength in nm.
        """
        if not self.min_wavelength <= wavelength <= self.max_wavelength:
            raise ValueError(f"Parameter wavelength is out of range: {wavelength!r}")
        if "WAV" == self.get_x_scale():
            cmd = ":SENSe:WAVelength:STOP {wl:.6f}NM".format(wl=wavelength)
        else:
            cmd = ":SENSe:WAVelength:STARt {wl:.6f}NM".format(wl=wavelength)
        self.command(cmd)

    def get_start_frequency(self) -> float:
        """Queries the measurement start frequency in THz.
        
        Returns:
            The start frequency in THz.
        """
        if "FREQ" == self.get_x_scale():
            cmd = ":SENSe:WAVelength:STARt?"
            f = float(Decimal(self.query(cmd)) / 10**12)
        else:
            cmd = ":SENSe:WAVelength:STOP?"
            f = LIGHTSPEED/(float(self.query(cmd)) * 10**9)
        return f

    def set_start_frequency(self, frequency: int | float) -> None:
        """Sets the measurement start frequency in THz.
        
        Args:
            frequency: The start frequency in THz.
        """
        if not self.min_frequency <= frequency <= self.max_frequency:
            raise ValueError(f"Parameter frequency is out of range: {frequency!r}")
        if "FREQ" == self.get_x_scale():
            cmd = ":SENSe:WAVelength:STARt {freq:.6f}THZ".format(freq=frequency)
        else:
            cmd = ":SENSe:WAVelength:STOP {freq:.6f}THZ".format(freq=frequency)
        self.command(cmd)

    def get_stop_frequency(self) -> float:
        """Queries the measurement stop frequency in THz.
        
        Returns:
            The stop frequency in THz.
        """
        if "FREQ" == self.get_x_scale():
            cmd = ":SENSe:WAVelength:STOP?"
            f = float(Decimal(self.query(cmd)) / 10**12)
        else:
            cmd = ":SENSe:WAVelength:STARt?"
            f = LIGHTSPEED/(float(self.query(cmd)) * 10**9)
        return f

    def set_stop_frequency(self, frequency: int | float) -> None:
        """Sets the measurement stop frequency in THz.
        
        Args:
            frequency: The stop frequency in THz.
        """
        if not self.min_frequency <= frequency <= self.max_frequency:
            raise ValueError(f"Parameter frequency is out of range: {frequency!r}")
        if "FREQ" == self.get_x_scale():
            cmd = ":SENSe:WAVelength:STOP {freq:.6f}THZ".format(freq=frequency)
        else:
            cmd = ":SENSe:WAVelength:STARt {freq:.6f}THZ".format(freq=frequency)
        self.command(cmd)

    def sweep(self, mode: str = "REPEAT") -> None:
        """Sets the sweep mode and makes a sweep. For information about the 
        sweep modes, please refer to documentation of the instrument.
        
        Args:
            mode: Sweep mode. `AUTO` | `REPEAT` | `SINGLE` | `STOP`.
        """
        if mode not in self.SWEEP_MODES:
            raise ValueError(f"Invalid value for parameter mode: {mode!r}")
        if mode == "STOP":
            self.command(':ABOR')
        else:
            self.command(f':INIT:SMOD {mode};:INIT')

    def run(self) -> None:
        """Makes a REPEAT sweep."""
        self.command(':INIT:SMOD REPEAT;:INIT')

    def stop(self) -> None:
        """Stops sweep."""
        self.command(':ABOR')

    def single(self) -> None:
        """Makes a SINGLE sweep."""
        self.command(':INIT:SMOD SINGLE;:INIT')

    def get_sweep_speed(self) -> int:
        """
        Queries the sweep speed.

        Returns:
            0 = Standard speed (1x), 
            1 = Twice as fast as standard (2x)
        """
        cmd = ":SENSE:SWEEP:SPEED?"
        return int(self.query(cmd))

    def set_sweep_speed(self, speed: int) -> None:
        """
        Sets the sweep speed.

        Args:
            speed: 0 = Standard speed (1x), 
                1 = Twice as fast as standard (2x)
        """
        if speed not in {0, 1}:
            raise ValueError("The value of parameter speed must be 0 or 1")
        cmd = f":SENSE:SWEEP:SPEED {speed:d}"
        self.command(cmd)

    def set_auto_zero(self, enable: bool) -> None:
        """Sets whether to enable the auto zeroing of the level.
        
        Args:
            enable: Whether to enable the auto zeroing of the level.
        """
        if not isinstance(enable, bool):
            raise TypeError(f"Parameter status must be a bool, not '{type(enable).__name__}'.")
        cmd = f":CALibration:ZERO {enable:d}"
        self.command(cmd)

    def get_auto_zero(self) -> bool:
        """Queries whether the auto zeroing of the level is enabled.
        
        Returns:
            Whether the auto zeroing is enabled.
        """
        cmd = ":CALibration:ZERO?"
        status = bool(int(self.query(cmd)))
        return status

    def zero_once(self) -> None:
        """Perform zeroing of the level once."""
        self.command(":CALibration:ZERO ONCE")

    def set_auto_analysis(self, enable: bool) -> None:
        """Sets whether to enable the automatic analysis function.
        
        Args:
            enable: Whether to enable automatic analysis function.
        """
        if not isinstance(enable, bool):
            raise TypeError(f"Parameter enable must be a bool, not '{type(enable).__name__}'.")
        cmd = ":CALCulate:AUTO {enable:d}".format(enable=enable)
        self.command(cmd)

    def get_auto_analysis(self) -> bool:
        """Queries if the automatic analysis function is enabled.
        
        Returns:
            Whether the automatic analysis function is enabled.
        """
        cmd = ":CALCulate:AUTO?"
        enabled = bool(int(self.query(cmd)))
        return enabled

    def set_analysis_category(self, category: str) -> None:
        """Sets the analysis category.

        Args:
            category: The type of analysis.

                - `SWTHRESH`: Spectrum width analysis (THRESH)
                - `DFBLD`: DFB-LD parameter analysis
                - `SMSR`: SMSR analysis
                - `WDM`: WDM analysis
        """
        if category not in self.ANALYSIS_CATEGORIES:
            raise ValueError('Invalid option of category: %r' % category)
        cmd = ":CALCulate:CATegory {cat}".format(cat=category)
        self.command(cmd)

    def get_analysis_category(self) -> str:
        """Queries the type of analysis.
        
        Returns:
            The type of analysis. `SWTHRESH` | `DFBLD` | `SMSR` | `WDM`. 
                Please refer to `set_analysis_category` for detail.
        """
        cat_dict = {0: "SWTHRESH", 5: "DFBLD", 8: "SMSR", 11: "WDM"}
        cmd = ":CALCulate:CATegory?"
        cat = cat_dict[int(self.query(cmd))]
        return cat

    def set_wdm_threshold(self, threshold: int | float) -> None:
        """
        Set the threshold level of channel detection for the WDM analysis 
        function.

        The range of the threshold: 0.1 <= threshold <= 99.9

        Args:
            threshold: The threshold level value in dB.
        """
        if not 0.1 <= threshold <= 99.9:
            raise ValueError(f'Parameter threshold must be in range [0.1, 99.9], got {threshold!r}')
        cmd = ":CALCulate:PARameter:WDM:TH {th:.2f}DB".format(th=threshold)
        self.command(cmd)

    def get_wdm_threshold(self) -> float:
        """
        Queries the threshold level of channel detection for the WDM analysis 
        function.
        
        Returns:
            The threshold level value in dB.
        """
        cmd = ":CALCulate:PARameter:WDM:TH?"
        th = float(self.query(cmd))
        return th

    def set_wdm_mdiff(self, mdiff: int | float) -> None:
        """
        Sets the peak bottom difference of channel detection for the WDM 
        analysis function.

        The range of the mdiff: 0.01 <= mdiff <= 50

        Args:
            mdiff: The peak-bottom difference in dB.
        """
        if not 0.01 <= mdiff <= 50:
            raise ValueError(f'Parameter mdiff must be in range [0.01, 50], got {mdiff!r}')
        cmd =":CALCulate:PARameter:WDM:MDIFf {mdiff:.2f}DB".format(mdiff=mdiff)
        self.command(cmd)

    def get_wdm_mdiff(self) -> float:
        """
        Queries the peak bottom difference of channel detection for the WDM 
        analysis function.

        Returns:
            The peak-bottom difference in dB.
        """
        cmd =":CALCulate:PARameter:WDM:MDIFf?"
        mdiff = float(self.query(cmd))
        return mdiff

    def set_wdm_dmask(self, dmask: int | float) -> None:
        """
        Sets the channel display mask threshold level for the WDM analysis function.

        The range of the dmask: -100 <= dmask <= 0.

        Set dmask to -999 will turn off the display mask.

        Args:
            dmask: The channel mask threshold level in dB.
        """
        if dmask != -999 and not -100 <= dmask <= 0:
            raise ValueError(f'Parameter dmask must be in range [-100, 0], got {dmask!r}')
        cmd = ":CALCulate:PARameter:WDM:DMASk {dmask:.2f}DB".format(dmask=dmask)
        self.command(cmd)

    def get_wdm_dmask(self) -> float:
        """
        Queries the channel display mask threshold level for the WDM analysis function.

        If the display mask is turned off, `-999.0` will be returned

        Returns:
            The channel mask threshold level in dB.
        """
        cmd = ":CALCulate:PARameter:WDM:DMASk?"
        dmask = float(self.query(cmd))
        return dmask

    def set_wdm_nalgo(self, algo: str) -> None:
        """
        Sets the measurement algorithm applied to noise level measurements 
        made by the WDM analysis function.

        Options of algorithms:

        - `AFIX` = AUTO FIX
        - `MFIX` = MANUAL FIX
        - `ACEN` = AUTO CENTER
        - `MCEN` = MANUAL CENTER
        - `PIT` = PIT
        
        Args:
            algo: The name of algorithm. Refer to options above.
        """
        algo_options = ["AFIX", "MFIX", "ACEN", "MCEN", "PIT"]
        if algo.upper() not in algo_options:
            raise ValueError("Invalid value for algo: {value!r}".format(value=algo))
        cmd = ":CALCulate:PARameter:WDM:NALGo {algo}".format(algo=algo)
        self.command(cmd)

    def get_wdm_nalgo(self) -> str:
        """
        Queries the measurement algorithm applied to noise level measurements 
        made by the WDM analysis function.

        Bug:
            For model AQ6370B, this method can not get a valid reply. This
            is caused by the corresponding issue of the instrument firmware. 
            This issue still exists even we upgrade the instrument firmware to
            the latest version `R03.04`. Since AQ6370B is out of date, this issue
            might never be fixed.

            But `set_wdm_nalgo` works normally.

            Other sub-models of AQ6370 (such as AQ6370C, AQ6370D) are not 
            affected.

        Options of algorithms:

        - `AFIX` = AUTO FIX
        - `MFIX` = MANUAL FIX
        - `ACEN` = AUTO CENTER
        - `MCEN` = MANUAL CENTER
        - `PIT` = PIT
        
        Returns:
            The name of algorithm. Refer to options above.
        """
        algo_options = ["AFIX", "MFIX", "ACEN", "MCEN", "PIT"]
        cmd = ":CALCulate:PARameter:WDM:NALGo?"
        algo = algo_options[int(self.query(cmd))]
        return algo

    def set_wdm_narea(self, narea: int | float) -> None:
        """Sets the measuring range applied to noise level measurements 
        made by the WDM analysis function.
        
        The range of the narea: 0.01 <= narea <= 10

        Args:
            narea: The range in nm.
        """
        if not 0.01 <= narea <= 10:
            raise ValueError(f'Parameter narea must be in range [0.01, 10], got {narea!r}')
        cmd = ":CALCulate:PARameter:WDM:NARea {narea:.2f}NM".format(narea=narea)
        self.command(cmd)

    def get_wdm_narea(self) -> float:
        """Quereis the measuring range applied to noise level measurements 
        made by the WDM analysis function.
        
        Returns:
            The range in nm.
        """
        cmd = ":CALCulate:PARameter:WDM:NARea?"
        narea = float(Decimal(self.query(cmd)) * 10**9)
        return narea

    def set_wdm_marea(self, marea: int | float) -> None:
        """Sets the mask range during level measurement applied to noise level 
        measurements made by the WDM analysis function.
        
        The range of the marea: 0.01 <= marea <= 10

        Args:
            marea: The mask range in nm.
        """
        if not 0.01 <= marea <= 10:
            raise ValueError(f'Parameter marea must be in range [0.01, 10], got {marea!r}')
        cmd = ":CALCulate:PARameter:WDM:MARea {marea:.2f}NM".format(marea=marea)
        self.command(cmd)

    def get_wdm_marea(self) -> float:
        """Queries the mask range during level measurement applied to noise 
        level measurements made by the WDM analysis function.
        
        Returns:
            The mask range in nm.
        """
        cmd = ":CALCulate:PARameter:WDM:MARea?"
        marea = float(Decimal(self.query(cmd)) * 10**9)
        return marea

    def set_wdm_falgo(self, algo: str) -> None:
        """Sets the fitting function during level measurement applied to 
        noise level measurements made by the WDM analysis function.
        
        Options of algorithms:

        - `LIN` = LINEAR
        - `GAUS` = GAUSS
        - `LOR` = LORENZ
        - `3RD` = 3RD POLY
        - `4TH` = 4TH POLY
        - `5TH` = 5TH POLY

        Args:
            algo: The name of the algorithm. Refer to options above.
        """
        algo_options = ["LIN", "GAUS", "LOR", "3RD", "4TH", "5TH"]
        if algo.upper() not in algo_options:
            raise ValueError("Invalid value for algo: {value!r}".format(value=algo))
        cmd = ":CALCulate:PARameter:WDM:FALGo {algo}".format(algo=algo)
        self.command(cmd)

    def get_wdm_falgo(self) -> str:
        """Queries the fitting function during level measurement applied to 
        noise level measurements made by the WDM analysis function.
        
        Options of algorithms:

        - `LIN` = LINEAR
        - `GAUS` = GAUSS
        - `LOR` = LORENZ
        - `3RD` = 3RD POLY
        - `4TH` = 4YH POLY
        - `5TH` = 5TH POLY

        Returns:
            The name of the algorithm. Refer to options above.
        """
        algo_options = ["LIN", "GAUS", "LOR", "3RD", "4TH", "5TH"]
        cmd = ":CALCulate:PARameter:WDM:FALGo?"
        algo = algo_options[int(self.query(cmd))]
        return algo

    def set_wdm_nbw(self, nbw: int | float) -> None:
        """Sets the noise bandwidth for the WDM analysis function.

        The range of the nbw: 0.01 <= nbw <= 1.0

        Args:
            nbw: The noise bandwidth in nm.
        """
        if not 0.01 <= nbw <= 1.0:
            raise ValueError(f'Parameter nbw must be in range [0.01, 1.0], but got {nbw!r}')
        cmd = ":CALCulate:PARameter:WDM:NBW {nbw:.2f}NM".format(nbw=nbw)
        self.command(cmd)
    
    def get_wdm_nbw(self) -> float:
        """Queries the noise bandwidth for the WDM analysis function.

        Returns:
            The noise bandwidth in nm.
        """
        cmd = ":CALCulate:PARameter:WDM:NBW?"
        nbw = float(Decimal(self.query(cmd)) * 10**9)
        return nbw

    def set_smsr_mask(self, mask: int | float) -> None:
        """Set the mask value for the SMSR analysis function.
        
        The range of the mask: 0.01 <= mask <= 99.99

        Args:
            mask: The mask value in nm.
        """
        if not 0 <= mask <= 99.99:
            raise ValueError(f'Parameter mask must be in range [0.01, 99.99], but got {mask!r}')
        cmd = ":CALCulate:PARameter:SMSR:MASK {mask:.2f}NM".format(mask=mask)
        self.command(cmd)

    def get_smsr_mask(self) -> None:
        """Quereis the mask value for the SMSR analysis function.
        
        Returns:
            The mask value in nm.
        """
        cmd = ":CALCulate:PARameter:SMSR:MASK?"
        mask = float(Decimal(self.query(cmd)) * 10**9)
        return mask

    def set_smsr_mode(self, mode: str) -> None:
        """Sets the analysis mode for the SMSR analysis function.

        Note:
            AQ6370B has no SMSR3/SMSR4 mode.

        Args:
            mode: The analysis mode, `SMSR1`|`SMSR2`|`SMSR3`|`SMSR4`.
        """
        options = ["SMSR1", "SMSR2", "SMSR3", "SMSR4"]
        if mode not in options:
            raise ValueError("Invalid option for mode: {mode!r}".format(mode=mode))
        cmd = ":CALCulate:PARameter:SMSR:MODE {mode}".format(mode=mode)
        self.command(cmd)

    def get_smsr_mode(self) -> str:
        """Sets the analysis mode for the SMSR analysis function.

        Returns:
            The analysis mode, `SMSR1`|`SMSR2`|`SMSR3`|`SMSR4`.
        """
        cmd = ":CALCulate:PARameter:SMSR:MODE?"
        mode = self.query(cmd).strip()
        return mode

    def set_dfbld_parameter(self, item: str, parameter: str, data: str) -> None:
        """Sets parameters for the DFB-LD analysis function. For more 
        information, please refer to the documents provided by instument 
        vendor.
        
        Args:
            item: Analytical item that sets parameter(s).
            parameter: Parameter to be set.
            data: Setting data.

        |`<item>`|`<parameter>`|`<data>`|
        |--------|-------------|--------|
        |SWIDth |ALGO   |`ENVelope|THResh|RMS|PKRMs`|
        |       |TH     |`<NRf>[DB]`|
        |       |TH2    |`<NRf>[DB]`|
        |       |K      |`<NRf>`|
        |       |MFIT   |`OFF|ON|0|1`|
        |       |MDIFf  |`<NRf>[DB]`|
        |SMSR   |SMODe  |`SMSR1|SMSR2|SMSR3|SMSR4`|
        |       |SMASk  |`<NRf>[M]`|
        |       |MDIFf  |`<NRf>[DB]`|
        |RMS    |ALGO   |`RMS|PKRMs`|
        |       |TH     |`<NRf>[DB]`|
        |       |K      |`<NRf>`|
        |       |MDIFf  |`<NRf>[DB]`|
        |POWer  |SPAN   |`<NRf>[M]`|
        |OSNR   |MDIFf  |`<NRf>[DB]`|
        |       |NALGo  |`AFIX|MFIX|ACENter|MCENter|PIT|0|1|2|3|4`|
        |       |NARea  |`<NRf>[M]`|
        |       |MARea  |`<NRf>[M]`|
        |       |FALGo  |`LINear|GAUSs|LORenz|3RD|4TH|5TH|0|1|2|3|4|5`|
        |       |NBW    |`<NRf>[M]`|
        |       |SPOWer |`PEAK|INTegral|0|1`|
        |       |IRANge |`<NRf>`|

        """
        cmd = ":CALCulate:PARameter:DFBLd {item},{parameter},{data}".format(item=item, parameter=parameter, data=data)
        self.command(cmd)

    def get_dfbld_parameter(self, item: str, parameter: str) -> str:
        """Sets parameters for the DFB-LD analysis function. For more 
        information, please refer to the documents provided by instument 
        vendor.

        Args:
            item: Analytical item that sets parameter(s).
            parameter: Parameter to be set.
        
        Returns:
            A string of the value of parameter. Please refer to 
                `set_dfbld_parameter` for detail.
        """
        cmd = ":CALCulate:PARameter:DFBLd? {item},{parameter}".format(item=item, parameter=parameter)
        return self.query(cmd)

    def set_swthresh_k(self, k: int | float) -> None:
        """Sets the magnification of the THRESH method-based spectrum width 
        analysis function.
        
        The range of the k: 1.0 <= k <= 10.0

        Args:
            k: The magnification.
        """
        if not 1.0 <= k <= 10.0:
            raise ValueError(f'Parameter k must be in range [1.0, 10.0], but got {k!r}')
        cmd = ":CALCulate:PARameter:SWTHResh:K {k:.2f}".format(k=k)
        self.command(cmd)

    def get_swthresh_k(self) -> float:
        """Sets the magnification of the THRESH method-based spectrum width 
        analysis function.
        
        Returns:
            The magnification.
        """
        cmd = ":CALCulate:PARameter:SWTHResh:K?"
        k = float(self.query(cmd))
        return k

    def set_swthresh_mfit(self, en: bool) -> None:
        """Sets whether to enable the mode fit of the THRESH method-based 
        spectrum width analysis function.

        Args:
            en: Whether to enable the mode fit.
        """
        if not isinstance(en, bool):
            raise TypeError(f"Parameter en must be a bool, not '{type(en).__name__}'.")
        cmd = ":CALCulate:PARameter:SWTHresh:MFIT {en:d}".format(en=en)
        self.command(cmd)

    def get_swthresh_mfit(self) -> bool:
        """Queries whether to enable the mode fit of the THRESH method-based 
        spectrum width analysis function.
        
        Returns:
            Whether to enable the mode fit.
        """
        cmd = ":CALCulate:PARameter:SWTHresh:MFIT?"
        en = bool(int(self.query(cmd)))
        return en

    def set_swthresh_th(self, th: int | float) -> None:
        """Sets the threshold level of the THRESH method-based spectrum width 
        analysis function.
        
        The range of the th: 0.01 <= th <= 50.0

        Args:
            th: The threshold level in dB.
        """
        if not 0.01 <= th <= 50.0:
            raise ValueError(f'Parameter th must be in range [0.01, 50.0], but got {th!r}')
        cmd = ":CALCulate:PARameter:SWTHresh:TH {th:.2f}DB".format(th=th)
        self.command(cmd)

    def get_swthresh_th(self) -> float:
        """Queries the threshold level of the THRESH method-based spectrum 
        width analysis function.
        
        Returns:
            The threshold level in dB.
        """
        cmd = ":CALCulate:PARameter:SWTHresh:TH?"
        th = float(self.query(cmd))
        return th

    def get_analysis_data(self) -> str:
        """Queries the analysis results from the last time analysis was 
        executed.

        For the output formats of analysis results, please refer to documents 
        from the instrument vendor.

        Returns:
            The analysis data.
        """
        return self.query(':CALC:DATA?')

    def get_osnr(self) -> float:
        """Queries the SNR value from the last time WDM analysis was executed.
        
        Note that only under WDM analysis category, the return value is valid.
        Otherwise, 0 is returned.

        Returns:
            The value of the OSNR in dB.
        """
        cmd = ":CALCulate:DATA:CSNR?"
        osnr = float(self.query(cmd).split(",")[0])
        return osnr

    def get_marker_x_scale(self) -> str:
        """Queries the horizontal scale for the marker values.

        Note that when the measurement x scale is set, the marker x scale will
        be set to the same option automatically. So the marker x scale will be
        consistent with the measurement x scale if it is not set explicitly. 
        Please refer to `set_x_scale` for more information.
        
        Returns:
            The horizontal scale. `"WAV"` | `"FREQ"`.
        """
        cmd = ":CALCulate:MARKer:UNIT?"
        scale = self.X_SCALES[int(self.query(cmd))]
        return scale

    def set_marker_x_scale(self, scale: str) -> None:
        """Sets the units of display for the marker values.

        Note that when the measurement x scale is set, the marker x scale will
        be set to the same option automatically. So the marker x scale will be
        consistent with the measurement x scale if it is not set explicitly. 
        Please refer to `set_x_scale` for more information.
        
        Args:
            scale: The unit of marker X. `"WAV"` | `"FREQ"`.
        """
        if scale not in self.X_SCALES:
            raise ValueError(f"Invalid value for parameter scale: {scale!r}")
        cmd = f":CALCulate:MARKer:UNIT {scale}"
        self.command(cmd)

    def get_marker_active_state(self, marker: int) -> bool:
        """Queries the active state of a specified marker. A marker should be 
        set into active state before further operations.

        Note that you should set the moving marker (marker number 0) active 
        before you set any of the fixed markers active (marker number 1 to 4).
        
        Args:
            marker: Marker number. `0` | `1` | `2` | `3` | `4`. `0` represents
                to the moving marker.
        
        Returns:
            `True` = active, `False` = inactive.
        """
        if marker not in self.MARKER_NUMBERS:
            raise ValueError("Invalid value for marker: {marker!r}".format(marker=marker))
        cmd = ":CALCulate:MARKer:STATe? {marker:d}".format(marker=marker)
        state = bool(int(self.query(cmd)))
        return state

    def set_marker_active_state(self, marker: int, state: bool) -> None:
        """Set the active state of a specified marker. A marker should be set 
        into active state before further operations.

        Note that you should set the moving marker (marker number 0) active 
        before you set any of the fixed markers active (marker number 1 to 4).
        
        Args:
            marker: Marker number. `0` | `1` | `2` | `3` | `4`. `0` represents
                to the moving marker.
            state: `True` = active, `False` = inactive.
        """
        if marker not in self.MARKER_NUMBERS:
            raise ValueError("Invalid value for marker: {marker!r}".format(marker=marker))
        if not isinstance(state, bool):
            raise TypeError(f"Parameter state must be a bool, not '{type(state).__name__}'.")
        cmd = f":CALCULATE:MARKER:STATE {marker:d},{state:d}"
        self.command(cmd)

    def set_marker_x(self, marker: int, x: int | float) -> None:
        """Places a specified marker in a specified position.

        Note:
            This method only takes effect when:

            1. A measurement sweep must be performed.
            2. The sweep should be completed and stoped.

        Args:
            marker: The marker number.  `0` | `1` | `2` | `3` | `4`. `0` 
                represents to the moving marker.
            x: The X value of the specified marker. The unit depends on the 
                current setting of marker x scale. If the marker x 
                scale is "WAV", sets the x value in nm. If marker x scale 
                is "FREQ", sets the x value in THz.

                Please refer to `get_marker_x_scale` for information.
        """
        if marker not in self.MARKER_NUMBERS:
            raise ValueError("Invalid marker: {marker!r}".format(marker=marker))
        unit = "NM" if self.get_marker_x_scale() == "WAV" else "THZ"
        cmd = ":CALCulate:MARKer:X {marker:d},{x:.6f}{unit}".format(marker=marker, x=x, unit=unit)
        self.command(cmd)

    def get_marker_x(self, marker: int) -> float:
        """Queries the X value of the specified marker.

        Args:
            marker: The marker number.  `0` | `1` | `2` | `3` | `4`. `0` 
                represents to the moving marker.
        
        Returns:
            The X value of the specified marker. The unit depends on the 
                current setting of marker x scale. If the marker x scale 
                is "WAV", returns the x value in nm. If marker x scale is 
                "FREQ", returns the x value in THz.

                Please refer to `get_marker_x_scale` for information.
        """
        if marker not in self.MARKER_NUMBERS:
            raise ValueError("Invalid marker: {marker!r}".format(marker=marker))
        cmd = ":CALCulate:MARKer:X? {marker:d}".format(marker=marker)
        if "WAV" == self.get_marker_x_scale():
            x = float(Decimal(self.query(cmd)) * 10**9)
        else:
            x = float(Decimal(self.query(cmd)) / 10**12)
        return x

    def get_marker_y(self, marker: int) -> float:
        """Queries the Y value of the specified marker.

        This unit of the marker level to be queried is dependent on the 
        Y-axis unit of the active trace.

        Args:
            marker: The marker number.  `0` | `1` | `2` | `3` | `4`. `0` 
                represents to the moving marker.

        Returns:
            The y value of the marker.
        """
        if marker not in self.MARKER_NUMBERS:
            raise ValueError("Invalid marker: {marker!r}".format(marker=marker))
        cmd = ":CALCulate:MARKer:Y? {marker:d}".format(marker=marker)
        y = float(self.query(cmd))
        return y

    def set_y_scale_mode(self, mode: str) -> None:
        """Sets the scale mode of the main scale of the level axis.
        
        Args:
            mode: The scale mode of level axis. 
                `"LOG"` = Logarighmic, `"LIN"` = Linear.
        """
        if mode not in ("LOG", "LIN"):
            raise ValueError("Invalid mode: {mode!r}".format(mode=mode))
        cmd = ":DISPlay:TRACe:Y1:SPACing {mode}".format(mode=mode)
        self.command(cmd)

    def get_y_scale_mode(self) -> str:
        """Queries the scale mode of the main scale of the level axis.
        
        Returns:
            mode: The scale mode of level axis. 
                `"LOG"` = Logarighmic, `"LIN"` = Linear.
        """
        cmd = ":DISPlay:TRACe:Y1:SPACing?"
        mode = ["LOG", "LIN"][int(self.query(cmd))]
        return mode

    def set_peak_to_center(self) -> None:
        """Detects the peak wavelength and sets it as the measurement center 
        waveform.
        """
        cmd = ":CALCulate:MARKer:MAXimum:SCENter"
        self.command(cmd)

    def set_ref_level(self, value: int | float, unit: str) -> None:
        """Sets the reference level of the main scale of the level axis. 

        Args:
            value: The value of the ref level.
            unit: The unit of the ref level. `"DBM"` | `"W"` | `"MW"`.
        """
        if unit not in ['DBM', 'W', 'MW']:
            raise ValueError('Invalid unit: {unit!r}'.format(unit=unit))
        cmd = ":DISPlay:TRACe:Y1:RLEVel {value:.6E}{unit}".format(value=value, unit=unit)
        self.command(cmd)

    def get_ref_level(self) -> float:
        """Sets/queries the reference level of the main scale of the level 
        axis.
        
        Returns:
            The value of the ref level in unit dBm or W depends on the Y scale 
                mode. Please refer to `get_y_scale_mode` for information.
        """
        cmd = ":DISPlay:TRACe:Y1:RLEVel?"
        level = float(self.query(cmd))
        return level

    def set_peak_to_ref(self) -> None:
        """Detects the peak level and sets it for the reference level."""
        cmd = ":CALCulate:MARKer:MAXimum:SRLevel"
        self.command(cmd)

    def set_auto_ref_level(self, enable: bool) -> None:
        """Sets ON/OFF of the function to automatically detect the peak level 
        and sets it as the reference level.
        
        Args:
            enable: Whether to enable auto ref level.
        """
        if not isinstance(enable, bool):
            raise TypeError(f"Parameter enable must be a bool, not '{type(enable).__name__}'.")
        cmd = ":CALCulate:MARKer:MAXimum:SRLevel:AUTO {enable:d}".format(enable=enable)
        self.command(cmd)
    
    def get_auto_ref_level(self) -> bool:
        """Queries ON/OFF of the function to automatically detect the peak 
        level and sets it as the reference level.
        
        Returns:
            If this function is enabled.
        """
        cmd = ":CALCulate:MARKer:MAXimum:SRLevel:AUTO?"
        enabled = bool(int(self.query(cmd)))
        return enabled

    def clear_all_markers(self) -> None:
        """Clears all markers."""
        self.command(':CALCulate:MARKer:AOFF')

    def set_active_trace(self, trace_name: str) -> None:
        """Sets the active trace.
        
        Args:
            trace_name: `TRA` | `TRB` | `TRC` | `TRD` | `TRE` | `TRF` | `TRG`
        """
        if trace_name not in ['TRA', 'TRB', 'TRC', 'TRD', 'TRE', 'TRF', 'TRG']:
            raise ValueError('Invalid trace_name: {name!r}'.format(name=trace_name))
        cmd = ':TRACe:ACTive {trace_name}'.format(trace_name=trace_name)
        self.command(cmd)

    def get_active_trace(self) -> str:
        """Queries the active trace.
        
        Returns:
            The trace name, `TRA` | `TRB` | `TRC` | `TRD` | `TRE` | `TRF` | `TRG`.
        """
        if trace_name not in ['TRA', 'TRB', 'TRC', 'TRD', 'TRE', 'TRF', 'TRG']:
            raise ValueError('Invalid trace_name: {name!r}'.format(name=trace_name))
        cmd = ':TRACe:ACTive?'
        trace_name = self.query(cmd).strip()
        return trace_name

    def set_trace_attribute(self, trace_name: str, attribute: str) -> None:
        """Sets the attributes of the specified trace. 
        
        Args:
            trace_name: `TRA` | `TRB` | `TRC` | `TRD` | `TRE` | `TRF` | `TRG`
            attribute: `WRIT` | `FIX` | `MAX` | `MIN` | `RAVG` | `CALC`
        """
        if trace_name not in ['TRA', 'TRB', 'TRC', 'TRD', 'TRE', 'TRF', 'TRG']:
            raise ValueError('Invalid trace_name: {name!r}'.format(name=trace_name))
        if attribute not in ['WRIT', 'FIX', 'MAX', 'MIN', 'RAVG', 'CALC']:
            raise ValueError('Invalid attribute: {attr!r}'.format(attr=attribute))
        cmd = ':TRACe:ATTRibute:{trace} {attribute}'.format(trace=trace_name, attribute=attribute)
        self.command(cmd)

    def get_trace_attribute(self, trace_name: str) -> str:
        """Queries the attributes of the specified trace. 
        
        Args:
            trace_name: `TRA` | `TRB` | `TRC` | `TRD` | `TRE` | `TRF` | `TRG`
        
        Returns:
            attribute: `WRIT` | `FIX` | `MAX` | `MIN` | `RAVG` | `CALC`
        """
        if trace_name not in ['TRA', 'TRB', 'TRC', 'TRD', 'TRE', 'TRF', 'TRG']:
            raise ValueError('Invalid trace_name: {name!r}'.format(name=trace_name))
        cmd = ':TRACe:ATTRibute:{trace}?'.format(trace=trace_name)
        ATTRS = ['WRIT', 'FIX', 'MAX', 'MIN', 'RAVG', 'CALC']
        attr = ATTRS[int(self.query(cmd))]
        return attr

    def set_trace_display_status(self, trace_name: str, display: bool) -> None:
        """Sets the display status of the specified trace. 
        
        Args:
            trace_name: `TRA` | `TRB` | `TRC` | `TRD` | `TRE` | `TRF` | `TRG`
            display: Whether to display the trace.
        """
        if trace_name not in ['TRA', 'TRB', 'TRC', 'TRD', 'TRE', 'TRF', 'TRG']:
            raise ValueError('Invalid trace_name: {name!r}'.format(name=trace_name))
        if not isinstance(display, bool):
            raise TypeError(f"Parameter display must be a bool, not '{type(display).__name__}'.")
        cmd = ':TRACe:STATe:{trace_name} {display:d}'.format(trace_name=trace_name, display=display)
        self.command(cmd)

    def get_trace_display_status(self, trace_name: str) -> bool:
        """Queries the display status of the specified trace.
        
        Args:
            trace_name: `TRA` | `TRB` | `TRC` | `TRD` | `TRE` | `TRF` | `TRG`
        
        Returns:
            Whether the trace is displayed.
        """
        if trace_name not in ['TRA', 'TRB', 'TRC', 'TRD', 'TRE', 'TRF', 'TRG']:
            raise ValueError('Invalid trace_name: {name!r}'.format(name=trace_name))
        cmd = ':TRACe:STATe:{trace_name}?'.format(trace_name=trace_name)
        displayed = bool(int(self.query(cmd)))
        return displayed

    def clear_trace(self, trace_name: str) -> None:
        """Deletes the data of a specified trace.

        Args:
            trace_name: `TRA` | `TRB` | `TRC` | `TRD` | `TRE` | `TRF` | `TRG`
        """
        if trace_name not in ['TRA', 'TRB', 'TRC', 'TRD', 'TRE', 'TRF', 'TRG']:
            raise ValueError('Invalid trace_name: {name!r}'.format(name=trace_name))
        cmd = ':TRACe:DELete {trace_name}'.format(trace_name=trace_name)
        self.command(cmd)

    def clear_all_traces(self) -> None:
        """Clears the data for all traces. """
        self.command(':TRACe:DELete:ALL')

    def get_trace_data_x(self, trace_name: str) -> List[float]:
        """Queries the wavelength axis data of the specified trace. 
        
        Data is output in the unit of wavelength value (nm), regardless of 
        whether this unit is in the wavelength mode or in the frequency mode.

        Note:
            The unit of data will not affected by the method `set_x_scale`.
            So even if we set the x scale to 'FREQ', the data is output in 
            nm as well.

        Args:
            trace_name: `TRA` | `TRB` | `TRC` | `TRD` | `TRE` | `TRF` | `TRG`

        Returns:
            A list of the x axis data in nm.
        """
        if trace_name not in ['TRA', 'TRB', 'TRC', 'TRD', 'TRE', 'TRF', 'TRG']:
            raise ValueError('Invalid trace_name: {name!r}'.format(name=trace_name))
        cmd = f':TRACe:DATA:X? {trace_name}'
        result = [float(i)*10**9 for i in self.query(cmd).split(',')]
        return result

    def get_trace_data_y(self, trace_name: str) -> List[float]:
        """Queries the level axis data of specified trace.
        
        The data is output in order of its wavelength from the shortest level 
        to the longest, irrespective of the wavelength/frequency mode.

        When the level scale is LOG, data is output in LOG values.

        When the level scale is Linear, data is output in linear values.
        
        Args:
            trace_name: `TRA` | `TRB` | `TRC` | `TRD` | `TRE` | `TRF` | `TRG`
        
        Returns:
            A list of the y axis data in nm.
        """
        if trace_name not in ['TRA', 'TRB', 'TRC', 'TRD', 'TRE', 'TRF', 'TRG']:
            raise ValueError('Invalid trace_name: {name!r}'.format(name=trace_name))
        cmd = f':TRACe:DATA:Y? {trace_name}'
        result = [float(i) for i in self.query(cmd).split(',')]
        return result

    def capture_screen(self) -> bytes:
        """Capture the screen and returns the BMP iamge data as bytes.

        Returns:
            The image data of the screen capture.
        """
        # create a unique name with nearly no chance to conflict
        temp_filename = 'tmp-{timestamp:X}'.format(timestamp=int(time.time()*10**6))
        # save image to internal memory
        self.command(':MMEMORY:STORE:GRAPHICS COLOR,BMP,"{filename}",INTERNAL'.format(filename=temp_filename))
        self.opc
        bin_data = self.query_binary_values(':MMEMORY:DATA? "{filename}.BMP",internal'.format(filename=temp_filename), datatype='B')
        bytes_data = bytes(bin_data)
        # delete temp file from internal memory
        self.command(':MMEMORY:DELETE "{filename}.BMP",internal'.format(filename=temp_filename))
        return bytes_data

    def save_screen(self, file_path: str) -> None:
        """Capture the screen and save as a .bmp file.

        Bug:
            For model AQ6360, this method takes rather long time 
            (about 60 sec) to return. We are contacting with Yokogawa to see 
            if this issue could be solved.
        
        Args:
            file_path: The file path to save the screen capture.
        """
        data = self.capture_screen()
        if os.path.exists(file_path):
            raise PermissionError('The file path {path} already exists.'.format(path=file_path))
        with open(file_path, 'wb') as f:
            f.write(data)

class ModelAQ6360(BaseModelAQ63xx):
    """
    Optical Spectrum Analyzer AQ6360 series from Yokogawa.
    """

    model = "AQ6360"

    brand = "Yokogawa"
    
    details = {
        "Wavelength Range": "700 ~ 1650 nm",
        "Max. Resolution": "0.1 nm"
    }

    _resolution_table = {
        'NM': [0.1, 0.2, 0.5, 1, 2],
        'GHZ': [20, 40, 100, 200, 400]
    }

    _x_span_range = {
        'NM': [0, 950],
        'GHZ': [0, 246]
    }
    
    @property
    def min_wavelength(self) -> float:
        """The minimum settable optical wavelength value in nm."""
        return 700.0

    @property
    def max_wavelength(self) -> float:
        """The maximum settable optical wavelength value in nm."""
        return 1650.0

class ModelAQ6370(BaseModelAQ63xx):
    """
    Optical Spectrum Analyzer AQ6370 series from Yokogawa, including AQ6370, AQ6370B, AQ6370C, AQ6370D, etc.
    """

    model = "AQ6370"

    brand = "Yokogawa"
    
    details = {
        "Wavelength Range": "600 ~ 1700 nm",
        "Max. Resolution": "0.02 nm"
    }

    _resolution_table = {
        'NM': [0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0],
        'GHZ': [4, 10, 20, 40, 100, 200, 400]
    }

    _x_span_range = {
        'NM': [0, 1100],
        'GHZ': [0, 330]
    }
    
    @property
    def min_wavelength(self) -> float:
        """The minimum settable optical wavelength value in nm."""
        return 600.0

    @property
    def max_wavelength(self) -> float:
        """The maximum settable optical wavelength value in nm."""
        return 1700.0

class ModelAQ6150(VisaInstrument, TypeWM):
    model = "AQ6150"
    brand = "Yokogawa"
    details = {
        "Wavelength Range": "1270 ~ 1650 nm",
        "Input Power Range": "-30 ~ 10 dBm",
        "Safe Max Input Power": "+18 dBm"
    }

    def __init__(self, resource_name, **kwargs: Any):
        super(ModelAQ6150, self).__init__(resource_name, **kwargs)

    def run(self, state: bool = True) -> None:
        """
        Executes (stops) repeat measurement.

        Args:
            state: `True` = Execute, `False` = Stop.
        """
        if not isinstance(state, bool):
            raise TypeError(f"Parameter state must be a bool, not '{type(state).__name__}'.")
        cmd = ':INITiate:CONTinuous {state:d}'.format(state=state)
        self.command(cmd)

    def single(self) -> None:
        """Executes a single measurement."""
        cmd = ':INITiate'
        self.command(cmd)

    def stop(self) -> None:
        """
        Stops repeat measurement.
        """
        self.run(False)

    def is_running(self) -> bool:
        """
        Queries the repeat measurement state.
        
        Returns:
            `True` = Execute, `False` = Stop.
        """
        cmd = ':INITiate:CONTinuous?'
        state = bool(int(self.query(cmd)))
        return state

    def measure_frequency(self) -> float:
        """Performs a single measurement and queries the peak frequency in single view mode with a single measurement.
        
        Returns:
            The peak frequency in THz.
        """
        cmd = ":MEASure:POWer:FREQuency?"
        freq = float(Decimal(self.query(cmd))/10**12)
        if freq == 0:
            raise ValueError('No optical input signal.')
        return freq

    def measure_wavelength(self) -> float:
        """Performs a single measurement and queries the peak wavelength in single view mode in single measurement.

        Returns:
            The peak wavelength in nm.
        """
        cmd = ":MEASure:POWer:WAVelength?"
        wl = float(Decimal(self.query(cmd))*10**9)
        if wl == 0:
            raise ValueError('No optical input signal.')
        return wl

    def get_frequency(self) -> float:
        """Queries the peak frequency in single view mode with a single measurement.
        
        Returns:
            The peak frequency in THz.
        """
        cmd = ":FETCh:POWer:FREQuency?"
        freq = float(Decimal(self.query(cmd))/10**12)
        if freq == 0:
            raise ValueError('No optical input signal.')
        return freq

    def get_wavelength(self) -> float:
        """Queries the peak wavelength in single view mode in single measurement.

        Returns:
            The peak wavelength in nm.
        """
        cmd = ":FETCh:POWer:WAVelength?"
        wl = float(Decimal(self.query(cmd))*10**9)
        if wl == 0:
            raise ValueError('No optical input signal.')
        return wl

class BaseModelEspecOld(BaseInstrument, TypeTS):
    """The base class for old chamber models by Espec:
    
    - MC-711
    - MT3065

    Note:
        In order to communicate, corresponding configurations must be made on the chamber.

        - Device ID: Correspond with the dev_id in the `__init__` method. 
            Defaults to 0.
    """
    brand = "Espec"
    params = [
        {
            "name": "dev_id",
            "type": "int",
            "min": 0,
            "max": 15
        }
    ]

    def __init__(self, resource_name: str, dev_id: int = 0, baudrate: int = 19200, read_timeout: int | float = 0.5, **kwargs: Any):
        """
        Args:
            resource_name: The serial port name.
            dev_id: The device ID of the chamber.
            baudrate: Baud rate such as 9600 or 115200 etc..
            read_timeout: Timeout in milliseconds for read operations.
            **kwargs: Directly passed to `serial.Serial()`.
        """
        super(BaseModelEspecOld, self).__init__(resource_name)
        if dev_id not in range(16):
            raise ValueError('Device ID must be between 0 and 15')
        self.__dev_id = dev_id
        self.__serial = serial.Serial(port=resource_name, baudrate=baudrate, timeout=read_timeout, **kwargs)
        self.__serial.setRTS()
        self.__serial.setDTR()
        self.__serial.reset_input_buffer()
        self.__resource_name = resource_name
        self._check_communication()

    @property
    def resource_name(self) -> str:
        """The serial port name."""
        return self.__resource_name

    @property
    def ts_type(self) -> TemperatureSourceType:
        """The temperature source type."""
        return TemperatureSourceType.CHAMBER

    def close(self) -> None:
        """Close the chamber connection and release the instrument resource."""
        self.__serial.close()

    def _write(self, cmd: str) -> None:
        # Write command
        PREFIX = b'\x05'
        cmd_body = f'{self.__dev_id:02X}{cmd}'
        checksum = (sum(cmd_body.encode()) & 0xFF)
        t_msg = PREFIX + f'{cmd_body}{checksum:02X}'.encode()
        self.__serial.reset_input_buffer()
        self.__serial.write(t_msg)

    def command(self, cmd: str) -> None:
        self._write(cmd)
        # Read reply
        r = self.__serial.read(5)
        if r != b'\x0600FF':
            raise ValueError(f'Unexpected reply from the chamber: {r!r}')

    def query(self, cmd: str) -> str:
        self._write(cmd)
        # Read reply
        PREFIX = b'\x02'
        TERMINATOR = b'\x03'
        r = self.__serial.read(1)
        if r != PREFIX:
            raise ValueError(f'Unexpected reply from the chamber: {r!r}')
        dev_id = int(self.__serial.read(2).decode(), 16)
        if dev_id != self.__dev_id:
            raise ValueError(f'Device ID mismatch: expected={self.__dev_id!r}, reply={dev_id!r}')
        r = self.__serial.read(2)
        data = b''
        while True:
            r = self.__serial.read(1)
            if r == TERMINATOR:
                checksum_bytes = self.__serial.read(2)
                checksum = int(checksum_bytes.decode(), 16)
                break
            else:
                data += r
        reply_body = f'{dev_id:02X}'.encode() + b'FF' + data + TERMINATOR 
        full_reply = PREFIX + reply_body + checksum_bytes
        if sum(reply_body) & 0xFF != checksum:
            raise ValueError(f'Invalid checksum of reply: {full_reply}')
        return data.decode()

    def _check_communication(self) -> None:
        try:
            self.get_target_temp()
        except Exception as e:
            raise InstrIOError("Check communication failed.") from e

    def run(
        self,
        mode: ChamberOperatingMode = ChamberOperatingMode.CONSTANT,
        p_num: Optional[int] = None,
        step_num: Optional[int] = None,
    ):
        """Run the chamber in selected mode and params, or stops the chamber.

        Args:
            mode: The operating mode to run the chamber.
            p_num: The program number. Integers from 0 to 39.
            step_num: The step number to start the program running. Integers from 0.
        """
        if mode == ChamberOperatingMode.OFF:
            self.command('FFWW0D110601000A')
        else:
            if mode == ChamberOperatingMode.PROGRAM:
                if not 0 <= p_num <= 39:
                    raise ValueError(f"Parameter p_num is out of range: {p_num!r}")
                if not step_num >= 0:
                    raise ValueError(f"Parameter step_num is out of range: {step_num!r}")
                self._select_program(p_num, step_num)
            mode_code = 1 if mode == ChamberOperatingMode.CONSTANT else 0
            self.command(f'FFWW0D110901{mode_code:04d}')
            self.command('FFWW0D110701000A')

    def _select_program(self, p_num: int, step_num: int) -> None:
        """
        Select the program number and start step for program mode.

        Args:
            p_num: The number of the program to run. Only used in program mode.
            step_num: The number of the step/section at witch to start the 
                program running. Only used in program mode.
        """
        self.command(f'FFWW0D144302{p_num:04d}{step_num:04d}')

    def stop(self) -> None:
        """Stops the chamber."""
        self.run(mode=ChamberOperatingMode.OFF)
    
    def _get_state(self) -> Tuple[bool, bool, bool]:
        cmd = 'FFWR0D112201'
        data = self.query(cmd)
        raw = int(data, 16)
        running = bool(raw & 1)
        in_program = bool((raw >> 1) & 1)
        in_error = bool((raw >> 2) & 1)
        return running, in_program, in_error

    def is_running(self) -> bool:
        """Queries whether the chamber is running.
        
        Returns:
            Whether the chamber is runing.
        """
        return self._get_state()[0]

    def get_operating_mode(self) -> ChamberOperatingMode:
        """Queries the chamber operating mode.
        
        Returns:
            The chamber operating mode.
        """
        running, in_program, _ = self._get_state()
        if not running:
            mode = ChamberOperatingMode.OFF
        else:
            mode = ChamberOperatingMode.PROGRAM if in_program else ChamberOperatingMode.CONSTANT
        return mode

    def in_error(self) -> bool:
        return self._get_state()[2]

    def set_target_temp(self, value: int | float) -> None:
        """
        Set the target temperature.

        Args:
            value: The target temperature value.
        """
        value = round(value*10)
        if value < 0:
            value = 65536 + value
        cmd = 'FFWW0D119705{temp:04X}0000000000000000'.format(temp=value)
        self.command(cmd)

    def get_target_temp(self) -> float:
        """
        Get the target temperature setting.

        Returns:
            The target temperature setting value.
        """
        cmd = 'FFWR0D111401'
        data = self.query(cmd)
        raw = int(data, 16)
        signed_val = (raw - 65536) if raw >= 65536/2 else raw
        return signed_val/10

    def get_current_temp(self) -> float:
        """
        Queries the current monitored temperature.

        Returns:
            The current temperature monitor value.
        """
        cmd = 'FFWR0D111701'
        data = self.query(cmd)
        raw = int(data, 16)
        signed_val = (raw - 65536) if raw >= 65536/2 else raw
        return signed_val/10

    def set_temp_unit(self, unit: TemperatureUnit) -> None:
        """
        Set the temperature unit.

        Args:
            unit: The temperature unit.
        """
        if unit != TemperatureUnit.C:
            raise ValueError('The temperature unit of this Chamber is fixed to C.')

    def get_temp_unit(self) -> TemperatureUnit:
        """
        Get the temperature unit setting.

        Returns:
            The temperature unit. 
        """
        return TemperatureUnit.C


class ModelMC711(BaseModelEspecOld):
    """See base class"""

    model = "MC-711"


class ModelMT3065(BaseModelEspecOld):
    """See base class"""

    model = "MT3065"


class ModelMC811(RawSerialInstrument, TypeTS):
    """MC-811 is a chamber model by GWS.
    
    Note:
        In order to communicate, corresponding configurations must be made on the chamber.

        - Communication: Serial
        - Protocol: STEN
        - Baudrate/Parity/Bytesize/Stopbits/Termination: Correspond with the 
            settings in the `__init__` method. Default values:
            - baudrate = 19200
            - parity = NONE
            - Bytesize = 8 bits
            - Stopbits: 1 bit
            - Termination: `<CR><LF>`
        - Device ID: None
    """
    model = "MC-811"
    brand = "GWS"

    def __init__(
            self, 
            resource_name: str, 
            baudrate: int = 19200, 
            bytesize: SerialByteSize = SerialByteSize.EIGHTBITS, 
            parity: SerialParity = SerialParity.NONE, 
            stopbits: SerialStopBits = SerialStopBits.ONE, 
            termination: str = '\r\n', 
            **kwargs: Any):
        """
        Args:
            resource_name: The serial port name.
            baudrate: Baud rate such as 9600 or 115200 etc..
            bytesize: SerialByteSize = SerialByteSize.EIGHTBITS,
            parity: SerialParity = SerialParity.NONE,
            stopbits: SerialStopBits = SerialStopBits.ONE,
            termination: The write and read termination character.
            **kwargs: Directly passed to `RawSerialInstrument.__init__`.
        """
        super().__init__(
            resource_name, 
            baudrate=baudrate,
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits,
            write_termination=termination, 
            read_termination=termination, 
            **kwargs)
        self.__fix_cmd_issue()

    def __fix_cmd_issue(self):
        # The chamber always reports CMD ERROR for the first cmd after 
        # serial connected. So this method should be called in the __init__ 
        # method
        try:
            self.get_target_temp()
        except Exception:
            pass

    @property
    def ts_type(self) -> TemperatureSourceType:
        """The temperature source type."""
        return TemperatureSourceType.CHAMBER

    def _check_communication(self) -> None:
        try:
            self.get_target_temp()
        except Exception as e:
            raise InstrIOError("Check communication failed.") from e

    def run(
        self, 
        mode: ChamberOperatingMode = ChamberOperatingMode.CONSTANT,
        p_num: Optional[int] = None,
        step_num: Optional[int] = None,
    ):
        """Run the chamber in selected mode and params, or stops the chamber.

        Args:
            mode: The operating mode to run the chamber.
            p_num: The program number. Integers from 1 to 20.
            step_num: The step number to start the program running. Integers from 1.
        """
        if mode == ChamberOperatingMode.OFF:
            cmd = 'MODE, OFF'
            self.command(cmd)
        elif mode == ChamberOperatingMode.CONSTANT:
            cmd = 'MODE, CONSTANT'
            self.command(cmd)
        elif mode == ChamberOperatingMode.PROGRAM:
            if not 0 <= p_num <= 19:
                raise ValueError(f"Parameter p_num out of range: {p_num!r}")
            elif not step_num >= 0:
                raise ValueError(f"Parameter step_number should be a positive integer.")
            cmd = f"PRGM, RUN, RAM:{p_num+1:d}, STEP{step_num+1:d}" # the number show on the chamber is 1 larger
            self.command(cmd)
        else:
            raise ValueError(f"Invalid operating mode: {mode!r}")

    def stop(self) -> None:
        """Stops the chamber."""
        self.run(mode=ChamberOperatingMode.OFF)

    def _get_state(self) -> str:
        cmd = 'MODE?'
        state = self.query(cmd).strip()
        return state
    
    def is_running(self) -> bool:
        """Queries whether the chamber is running.
        
        Returns:
            Whether the chamber is running.
        """
        return self._get_state in {'CONSTANT', 'RUN'}

    def get_operating_mode(self) -> ChamberOperatingMode:
        """Queries the chamber operating mode.
        
        Returns:
            The chamber operating mode.
        """
        state = self._get_state()
        if self.is_running():
            if state == 'CONSTANT':
                mode = ChamberOperatingMode.CONSTANT
            elif state == 'RUN':
                mode = ChamberOperatingMode.PROGRAM
        else:
            mode = ChamberOperatingMode.OFF
        return mode

    def set_target_temp(self, value: int | float) -> None:
        """
        Set the target temperature.

        Args:
            value: The target temperature value.
        """
        value = round(value, 1)
        cmd = 'TEMP, S{value:.1f}'.format(value=value)
        self.command(cmd)

    def get_target_temp(self) -> float:
        """
        Get the target temperature setting.

        Returns:
            The target temperature setting value.
        """
        cmd = 'TEMP?'
        temp = float(self.query(cmd).split(',')[1])
        return temp

    def get_current_temp(self) -> float:
        """
        Queries the current monitored temperature.

        Returns:
            The current temperature monitor value.
        """
        cmd = 'TEMP?'
        temp = float(self.query(cmd).split(',')[0])
        return temp

    def set_temp_unit(self, unit: TemperatureUnit) -> None:
        """
        Set the temperature unit.

        Args:
            unit: The temperature unit.
        """
        if unit != TemperatureUnit.C:
            raise ValueError('The temperature unit of this Chamber is fixed to C.')
    
    def get_temp_unit(self) -> TemperatureUnit:
        """
        Get the temperature unit setting.

        Returns:
            The temperature unit. 
        """
        return TemperatureUnit.C


class ModelATS535(VisaInstrument, TypeTS):
    """ATS-535 is a thermo-stream model by Temptronic.
    
    Note that before operating with temperature directly (means not in Cycle 
    mode), you should set the thermo-stream to the Operator screen, and make 
    sure the test head is lower down, and the air flow is on.
    
    Examples:
        ```python
        ts = ModelATS535('<resource-name>')
        ts.reset_operator()
        # check the test head is down
        if not ts.is_head_down():
            raise OperationalError('The thermo-stream test head is up.')
        # turn on the air flow
        ts.flow()
        # operate with the temperature directly
        ts.set_target_temp(35)
        t = ts.get_current_temp()
        ```
    """
    model = "ATS-535"
    brand = "Temptronic"

    def __init__(self, resource_name: str, **kwargs: Any):
        """
        Args:
            resource_name: Resource name or alias of the VISA resource to open.
            **kwargs: directly passed to `VisaInstrument.__init__`
        """
        super(ModelATS535, self).__init__(resource_name, **kwargs)

    @property
    def ts_type(self) -> TemperatureSourceType:
        """The temperature source type."""
        return TemperatureSourceType.THERMO_STREAM
    
    def head_up(self) -> None:
        """Raise up the test head."""
        self.command('HEAD 0')

    def head_down(self) -> None:
        """Lower down the test head."""
        self.command('HEAD 1')

    def is_head_down(self) -> bool:
        """Queries if the test head is lowered down.
        
        Returns:
            If the test head is lowered down.
        """
        is_down = bool(int(self.query('HEAD?')))
        return is_down

    def flow(self, on: bool = True) -> None:
        """Turn the main nozzle air flow on or off.
        
        Args:
            on: `True` = turn on, `False` = turn off.
        """
        cmd = 'FLOW {:d}'.format(on)
        self.command(cmd)

    def enable_dut_mode(self, en: bool = True) -> None:
        """Enable (disable) DUT mode.
        
        Args:
            en: True = DUT mode on (DUT control); False = DUT mode off (air control).
        """
        if not isinstance(en, bool):
            raise TypeError(f"Parameter en must be a bool, not '{type(en).__name__}'.")
        cmd = 'DUTM {en:d}'.format(en=en)
        self.command(cmd)

    def is_dut_mode(self) -> bool:
        """Queries if DUT mode is on.
        
        Returns:
            True = DUT mode on (DUT control); False = DUT mode off (air control).
        """
        state = bool(int(self.query('DUTM?')))
        return state

    def disable_dut_mode(self) -> None:
        """Disable DUT mode."""
        self.enable_dut_mode(False)

    def reset_operator(self) -> None:
        """Reset (force) the System to the Operator screen."""
        self.command('RSTO')
        time.sleep(0.3)

    def set_ramp(self) -> None:
        """Enter Ramp/Cycle."""
        self.command('RMPC 1')

    def set_n(self, n: int) -> None:
        """Select a setpoint to be the current setpoint.
        
        Args:
            n:
                - n is 0 - 17 when on the Cycle screen.
                - n is 0 to 2 when on the Operator screen (0=hot, 1=ambient, 2=cold).
        """
        return self.command('SETN %d' % n)

    def set_p(self, p: int | float) -> None:
        """Set the currently selected setpoint's temperature."""
        return self.command('SETP %.1f' % p)
    
    def get_p_setting(self) -> float:
        """Read the current temperature setpoint."""
        p = float(self.query('SETP?'))
        return p
    
    def set_ramp(self, ramp: int | float) -> None:
        """Set the ramp rate for the currently selected setpoint, in °C per 
        minute.
        
        Args:
            ramp: The ramp rate in °C per minute.
        """
        if 0<= ramp <= 99.9:
            t = '{:.1f}'.format(ramp)
        elif 99.9 < ramp <= 9999:
            t = '{:d}'.format(ramp)
        else:
            raise ValueError('Parameter ramp out of range.')
        return self.command('RAMP {}'.format(t))

    def get_ramp(self) -> float:
        """Read the setting of RAMP.
        
        Returns:
            The ramp rate in °C per minute.
        """
        cmd = 'RAMP?'
        ramp = float(self.query(cmd))
        return ramp

    def set_target_temp(self, value: int | float) -> None:
        """
        Set the target temperature.

        Args:
            value: The target temperature value.
        """
        if value < 20:
            n = 2
        elif 20 <= value <= 30:
            n = 1
        else:
            n = 0
        self.set_n(n)
        self.set_p(value)
        
    def get_target_temp(self) -> float:
        """
        Get the target temperature setting.

        Returns:
            The target temperature setting value.
        """
        return self.get_p_setting()

    def get_current_temp(self) -> float:
        """
        Queries the current monitored temperature.

        Returns:
            The current temperature monitor value.
        """
        temp = float(self.query('TEMP?'))
        if temp > 400:
            raise ValueError('Invalid current temperature.')
        return temp

    def set_temp_unit(self, unit: TemperatureUnit) -> None:
        """
        Set the temperature unit.

        Args:
            unit: The temperature unit.
        """
        if unit != TemperatureUnit.C:
            raise ValueError('The temperature unit of this thermo-stream is fixed to C.')
    
    def get_temp_unit(self) -> TemperatureUnit:
        """
        Get the temperature unit setting.

        Returns:
            The temperature unit. 
        """
        return TemperatureUnit.C


class ModelTC3625(RawSerialInstrument, TypeTS):
    """TC-36-25 is a TEC model by TE Technology. You may have to configure 
    some parameters via the GUI provided by the vendor before your first use, 
    this class will only perform the temperature control.
    """
    model = "TC-36-25"
    brand = "TE Technology"

    def __init__(
        self,
        resource_name: str,
        baudrate: int = 9600,
        read_termination: str = '^',
        write_termination: str = '\r',
        **kwargs: Any
    ):
        """
        Args:
            resource_name: Serial port name.
            baudrate: Baud rate such as 9600 or 115200 etc..
            read_termination: Read termination character.
            write_termination: Write termination character.
        """
        super(ModelTC3625, self).__init__(
            resource_name, baudrate=baudrate, read_termination=read_termination, 
            write_termination=write_termination, **kwargs)
        self._check_communication()

    @property
    def ts_type(self) -> TemperatureSourceType:
        """The temperature source type."""
        return TemperatureSourceType.TEC

    def formatted_query(self, cmd_code: int, value: int = 0) -> int:
        """
        Send a formated command to the TEC and return the result value.

        Args:
            cmd_code: Comand code is an int between 0 and 0xFF.
            value: An int value sent with the command. Defaults to 0 if it is 
                not needed. Between -0x80000000 and 0x7FFFFFFF.
        
        Returns:
            The 
        """
        if not 0 <= value <= 0xFF:
            raise ValueError('Parameter cmd_code out of range: {!r}'.format(cmd_code))
        if not -0x80000000 <= value <= 0x7FFFFFFF:
            raise ValueError('Parameter value out of range: {!r}'.format(value))
        
        STX = '*' # Start of text character that always prepend to the cmd.
        ADDR = 0 # The address of this device is fixed to 0

        cmd_body = '{addr:02x}{cmd_code:02x}{val:08x}'.format(addr=ADDR, cmd_code=cmd_code, val=signed_to_unsigned(value, byte_count=4))
        check_sum = calc_check_sum(cmd_body.encode())
        cmd = '{pre}{cmd_body}{check_sum:02x}'.format(pre=STX, cmd_body=cmd_body, check_sum=check_sum)
        result = self.query(cmd)[1:]
        result_content = result[0:-2]
        result_check_sum = int(result[-2:], base=16)
        calculated_check_sum = calc_check_sum(result_content.encode())
        if result_check_sum != calculated_check_sum:
            raise ValueError("Mismatched checksum of the reply.")
        if result_content == "X"*8:
            raise ValueError("Mismatched checksum of the command.")
        result_value = unsigned_to_signed(int(result_content, base=16), 4)
        return result_value

    def _check_communication(self) -> None:
        try:
            self.get_target_temp()
        except Exception as e:
            raise InstrIOError("Check communication failed.") from e

    def set_target_temp(self, value: int | float) -> None:
        """
        Set the target temperature.

        Args:
            value: The target temperature value.
        """
        cmd_value = round(value*100)
        rtn_value = self.formatted_query(0x1c, cmd_value)
        if cmd_value != rtn_value:
            raise ValueError('The return value mismatched with the cmd value: {!r}/{!r}'.format(rtn_value, cmd_value))

    def get_target_temp(self) -> float:
        """
        Get the target temperature setting.

        Returns:
            The target temperature setting value.
        """
        rtn_value = self.formatted_query(0x03)
        t = rtn_value/100
        return t

    def get_current_temp(self) -> float:
        """
        Queries the current monitored temperature.

        Returns:
            The current temperature monitor value.
        """
        rtn_value = self.formatted_query(0x01)
        t = rtn_value/100
        return t

    def set_temp_unit(self, unit: TemperatureUnit) -> None:
        """
        Set the temperature unit.

        Args:
            unit: The temperature unit.
        """
        unit = TemperatureUnit(unit)
        rtn_value = self.formatted_query(0x32, unit.value)
        if rtn_value != unit.value:
            raise ValueError('The return value mismatched with the cmd value: {!r}/{!r}'.format(rtn_value, unit))

    def get_temp_unit(self) -> TemperatureUnit:
        """
        Get the temperature unit setting.

        Returns:
            The temperature unit. 
        """
        rtn_value = self.formatted_query(0x4b)
        return TemperatureUnit(rtn_value)


class BaseModelSantecBandwidthTunableFilter(VisaInstrument, TypeOTF):

    def __init__(
        self, resource_name: str, read_termination: str = '\r\n', 
        write_termination: str = '\r\n', **kwargs: Any
    ):
        """
        Args:
            resource_name: Resource name or alias of the VISA resource to open.
            read_termination: Read termination character.
            write_termination: Write termination character.
        """
        super().__init__(resource_name, read_termination=read_termination, 
                         write_termination=write_termination, **kwargs)

    @property
    def min_frequency(self) -> float:
        """The minimum settable optical frequency value in THz."""
        cmd = ':FREQuency? MIN'
        freq = float(Decimal(self.query(cmd)) / 10**12)
        return freq

    @property
    def max_frequency(self) -> float:
        """The maximum settable optical frequency value in THz."""
        cmd = ':FREQuency? MAX'
        freq = float(Decimal(self.query(cmd)) / 10**12)
        return freq

    @property
    def min_wavelength(self) -> float:
        """The minimum settable optical wavelength value in nm."""
        cmd = ':WAVelength? MIN'
        wl = float(Decimal(self.query(cmd)) * 10**9)
        return wl
    
    @property
    def max_wavelength(self) -> float:
        """The maximum settable optical wavelength value in nm."""
        cmd = ':WAVelength? MAX'
        wl = float(Decimal(self.query(cmd)) * 10**9)
        return wl
    
    @property
    def min_bandwidth_in_nm(self) -> float:
        """The minimum bandwidth in nm."""
        cmd = ':BANDwidth? MIN'
        bw = float(Decimal(self.query(cmd)) * 10**9)
        return bw

    @property
    def max_bandwidth_in_nm(self) -> float:
        """The maximum bandwidth in nm."""
        cmd = ':BANDwidth? MAX'
        bw = float(Decimal(self.query(cmd)) * 10**9)
        return bw
    
    @property
    def min_bandwidth_in_ghz(self) -> float:
        """The minimum bandwidth in GHz."""
        return super().min_bandwidth_in_ghz
    
    @property
    def max_bandwidth_in_ghz(self) -> float:
        """The maximum bandwidth in GHz."""
        return super().max_bandwidth_in_ghz

    def get_frequency(self) -> float:
        """
        Queries the optical frequency setting of the instrument in THz.

        Returns:
            The optical frequency setting value in THz.
        """
        cmd = ':FREQuency?'
        freq = float(Decimal(self.query(cmd)) / 10**12)
        return freq
    
    def set_frequency(self, frequency: int | float) -> None:
        """Set optical frequency.

        Args:
            frequency: The optical frequency setting in THz.
        """
        if not self.min_frequency <= frequency <= self.max_frequency:
            raise ValueError(f"Parameter frequency is out of range: {frequency!r}")
        cmd = ':FREQuency {freq:.5f}THz'.format(freq=frequency)
        self.command(cmd)

    def get_wavelength_state(self) -> bool:
        """Queries if the optical frequency/wavelength setting is still operating.

        Returns:
            If the wavelength setting is still operating. True = operating, False = idle
        
        Bug:
            The wavelength setting operation actually ends a little later 
            after this method reports idle. So it is suggested to wait at 
            least 0.1 second after that.

            This is important if you want to set bandwidth after the 
            operation.

            For example:

            ```py
            otf.set_frequency(191.3)
            while otf.get_wavelength_state():
                pass
            time.sleep(0.3)
            otf.set_bandwidth_in_ghz(75)
            ```

            This is a bug of the OTF-980 model and not expected to be fixed.
        """
        cmd = ':WAVelength:STATe?'
        return bool(int(self.query(cmd)))

    def get_wavelength(self) -> float:
        """Queries the optical wavelength setting of the instrument in nm.

        Returns:
            The optical wavelength setting value in nm.
        """
        cmd = ':WAVelength?'
        wl = float(Decimal(self.query(cmd)) * 10**9)
        return wl
    
    def set_wavelength(self, wavelength: int | float) -> None:
        """Set optical wavelength.

        Args:
            wavelength: The optical wavelength setting in nm.
        """
        if not self.min_wavelength <= wavelength <= self.max_wavelength:
            raise ValueError('Parameter wavelength out of range: {wl!r}'.format(wl=wavelength))
        cmd = ':WAVelength {wl:.3f}nm'.format(wl=wavelength)
        self.command(cmd)

    def get_bandwidth_in_nm(self) -> float:
        """
        Get the filter bandwidth in nm.

        Returns:
            The bandwidth value in nm.
        """
        cmd = ':BANDwidth?'
        bw = float(Decimal(self.query(cmd)) * 10**9)
        return bw

    def set_bandwidth_in_nm(self, value: int | float) -> None:
        """
        Set the filter bandwidth in nm.

        Args:
            value: The bandwidth value in nm.
        """
        if not self.min_bandwidth_in_nm <= value <= self.max_bandwidth_in_nm:
            raise ValueError('Parameter value out of range: {val!r}'.format(val=value))
        cmd = ':BANDwidth {value:.3f}nm'.format(value=value)
        self.command(cmd)
    
    def get_bandwidth_in_ghz(self) -> float:
        """
        Get the filter bandwidth in GHz.

        Returns:
            The bandwidth value in GHz.
        """
        return super().get_bandwidth_in_ghz()

    def set_bandwidth_in_ghz(self, value: int | float) -> None:
        """
        Set the filter bandwidth in GHz.

        Args:
            value: The bandwidth value in GHz.
        """
        return super().set_bandwidth_in_ghz(value)


class ModelOTF970(BaseModelSantecBandwidthTunableFilter):

    model = "OTF-970"
    brand = "Santec"
    details = {
        "Wavelength Range": "1525 ~ 1610 nm",
        "Bandwidth Range": "Type specified",
        "Max Input Power": "+27 dBm"
    }


class ModelOTF980(BaseModelSantecBandwidthTunableFilter):

    model = "OTF-980"
    brand = "Santec"
    details = {
        "Wavelength Range": "1525 ~ 1610 nm",
        "Bandwidth Range": "Bandwidth type specified",
        "Max Input Power": "+27 dBm"
    }


class ModelOTF930(VisaInstrument, TypeOTF):

    model = "OTF-930"

    brand = "Santec"

    details = {
        "Wavelength Range": "1520 ~ 1610 nm",
        "Frequency Range": "186.2 ~ 197.2 THz",
        "Bandwidth": "Fixed and different between bandwidth types",
        "Max Input Power": "+20 dBm"
    }

    def __init__(
        self, resource_name: str, read_termination: str = '\r\n', 
        write_termination: str = '\r\n', **kwargs: Any
    ):
        """
        Args:
            resource_name: Resource name or alias of the VISA resource to open.
            read_termination: Read termination character.
            write_termination: Write termination character.
        """
        super().__init__(resource_name, read_termination=read_termination, 
                         write_termination=write_termination, **kwargs)

    @property
    def min_frequency(self) -> float:
        """The minimum settable optical frequency value in THz."""
        return super().min_frequency

    @property
    def max_frequency(self) -> float:
        """The maximum settable optical frequency value in THz."""
        return super().max_frequency

    @property
    def min_wavelength(self) -> float:
        """The minimum settable optical wavelength value in nm."""
        return 1520.0
    
    @property
    def max_wavelength(self) -> float:
        """The maximum settable optical wavelength value in nm."""
        return 1610.0
    
    @property
    def min_bandwidth_in_nm(self) -> float:
        """The minimum bandwidth in nm."""
        return float('nan')

    @property
    def max_bandwidth_in_nm(self) -> float:
        """The maximum bandwidth in nm."""
        return float('nan')
    
    @property
    def min_bandwidth_in_ghz(self) -> float:
        """The minimum bandwidth in GHz."""
        return float('nan')
    
    @property
    def max_bandwidth_in_ghz(self) -> float:
        """The maximum bandwidth in GHz."""
        return float('nan')

    def get_frequency(self) -> float:
        """
        Queries the optical frequency setting of the instrument in THz.

        Returns:
            The optical frequency setting value in THz.
        """
        return super().get_frequency()
    
    def set_frequency(self, frequency: int | float) -> None:
        """Set optical frequency.

        Args:
            frequency: The optical frequency setting in THz.
        """
        return super().set_frequency(frequency)

    def get_wavelength(self) -> float:
        """Queries the optical wavelength setting of the instrument in nm.

        Returns:
            The optical wavelength setting value in nm.
        """
        cmd = 'WA'
        wl = float(self.query(cmd))
        return wl
    
    def set_wavelength(self, wavelength: int | float) -> None:
        """Set optical wavelength.

        Args:
            wavelength: The optical wavelength setting in nm.
        """
        if not self.min_wavelength <= wavelength <= self.max_wavelength:
            raise ValueError('Parameter wavelength out of range: {wl!r}'.format(wl=wavelength))
        cmd = 'WA {wl:.3f}'.format(wl=wavelength)
        self.command(cmd)

    def get_bandwidth_in_nm(self) -> float:
        """
        Get the filter bandwidth in nm.

        Returns:
            The bandwidth value in nm.
        """
        raise Error('The bandwidth of this OTF model is not tunable.')

    def set_bandwidth_in_nm(self, value: int | float) -> None:
        """
        Set the filter bandwidth in nm.

        Args:
            value: The bandwidth value in nm.
        """
        raise Error('The bandwidth of this OTF model is not tunable.')
    
    def get_bandwidth_in_ghz(self) -> float:
        """
        Get the filter bandwidth in GHz.

        Returns:
            The bandwidth value in GHz.
        """
        raise Error('The bandwidth of this OTF model is not tunable.')

    def set_bandwidth_in_ghz(self, value: int | float) -> None:
        """
        Set the filter bandwidth in GHz.

        Args:
            value: The bandwidth value in GHz.
        """
        raise Error('The bandwidth of this OTF model is not tunable.')


class ModelBTF10011(RawSerialInstrument, TypeOTF):
    model = "BTF-100-11"
    brand = "OZ Optics"
    detais = {
        "Wavelength Range": "1525 ~ 1565 nm",
        "Bandwidth (FWHM)": "1 ~ 18 nm"
    }

    def __init__(self, resource_name: str, baudrate: int = 115200, read_termination: str = "\r\n", write_termination: str = "\r\n", **kwargs: Any):
        super().__init__(resource_name, baudrate, read_termination, write_termination, **kwargs)

    @property
    def min_frequency(self) -> float:
        """The minimum settable optical frequency value in THz."""
        return super().min_frequency

    @property
    def max_frequency(self) -> float:
        """The maximum settable optical frequency value in THz."""
        return super().max_frequency

    @property
    def min_wavelength(self) -> float:
        """The minimum settable optical wavelength value in nm."""
        return 1525.0

    @property
    def max_wavelength(self) -> float:
        """The maximum settable optical wavelength value in nm."""
        return 1565.0

    @property
    def min_bandwidth_in_ghz(self) -> float:
        """The minimum bandwidth in GHz."""
        return super().min_bandwidth_in_ghz
    
    @property
    def max_bandwidth_in_ghz(self) -> float:
        """The maximum bandwidth in GHz."""
        return super().max_bandwidth_in_ghz

    @property
    def min_bandwidth_in_nm(self) -> float:
        """The minimum bandwidth in nm."""
        return 1.0
    
    @property
    def max_bandwidth_in_nm(self) -> float:
        """The maximum bandwidth in nm."""
        return 18

    def __get_wl_bw(self) -> Tuple[float, float]:
        self.write('w?')
        reply = ''
        while True:
            rx = self.read().lower()
            reply += rx
            if 'done' in rx or 'error' in rx:
                break
        if 'unknown' in reply:
            raise ValueError('Unknown wavelength.')
        else:
            matched = re.search(r'.*WL\((.*?)\).*LW\((.*?)nm\).*', reply)
            wl = float(matched.group(1))
            bw = float(matched.group(2))
        return wl, bw

    def get_frequency(self) -> float:
        """
        Queries the optical frequency setting of the instrument in THz.

        Returns:
            The optical frequency setting value in THz.
        """
        return super().get_frequency()

    def set_frequency(self, frequency: int | float) -> None:
        """Set optical frequency.

        Args:
            frequency: The optical frequency setting in THz.
        """
        return super().set_frequency(frequency)

    def get_wavelength(self) -> float:
        """Queries the optical wavelength setting of the instrument in nm.

        Returns:
            The optical wavelength setting value in nm.
        """
        return self.__get_wl_bw()[0]

    def set_wavelength(self, wavelength: int | float) -> None:
        """Set optical wavelength.

        Args:
            wavelength: The optical wavelength setting in nm.
        """
        if not self.min_wavelength <= wavelength <= self.max_wavelength:
            raise ValueError(f'Parameter wavelength is out of range: {wavelength!r}')
        self.write(f'w{wavelength:.2f}')
        reply = ''
        while True:
            rx = self.read().lower()
            reply += rx
            if 'done' in rx or 'error' in rx:
                break
        if 'unknown' in reply:
            raise ValueError('Unkonwn linewidth.')
        if 'error' in reply:
            raise ValueError('Failed to set wavelength.')
        
    def get_bandwidth_in_ghz(self) -> float:
        """
        Get the filter bandwidth in GHz.

        Returns:
            The bandwidth value in GHz.
        """
        return super().get_bandwidth_in_ghz()

    def set_bandwidth_in_ghz(self, value: int | float) -> None:
        """
        Set the filter bandwidth in GHz.

        Args:
            value: The bandwidth value in GHz.
        """
        return super().set_bandwidth_in_ghz(value)

    def get_bandwidth_in_nm(self) -> float:
        """
        Get the filter bandwidth in nm.

        Returns:
            The bandwidth value in nm.
        """
        self.__get_wl_bw()[1]
    
    def set_bandwidth_in_nm(self, value: int | float) -> None:
        """
        Set the filter bandwidth in nm.

        Args:
            value: The bandwidth value in nm.
        """
        if not self.min_bandwidth_in_nm <= value <= self.max_bandwidth_in_nm:
            raise ValueError(f'Parameter value is out of range: {value!r}')
        wl = self.get_wavelength()
        self.write(f'w{wl:.2f},{value:.2f}')
        reply = ''
        while True:
            rx = self.read().lower()
            reply += rx
            if 'done(a)' in rx or 'error' in rx:
                break
        if 'out of range' in reply:
            raise ValueError('Out of range.')
        if 'error' in reply:
            raise ValueError('Failed to set bandwidth.')


class ModelNSW(BaseInstrument, TypeSW):
    """The Smart Optical Switch produced by NeoPhotonics."""
    model = "Neo_SW"
    brand = "NeoPhotonics"
    params = [
        {
            "name": "slot_or_type",
            "type": "str",
            "options": ['1', '2', '3', '1*8', '1*16']
        }
    ]

    def __init__(self, resource_name: str, slot_or_type: int | str) -> None:
        """
        Args:
            resource_name: The USB S/N of the device. You can use 
                get_usb_devices() method to list all the available devices.
            slot_or_type: For optical switch with 1x2/2x2/1x4 optical switch 
                slots, this parameter is the slot number in the frame. For 1x8
                and 1x16 optical switch, this parameter defines the type of
                the optical switch.
                - `1`|`2`|`3`: The slot in the frame.
                - `'1*8'`: This optical switch is 1x8 type.
                - `'1*16'`: This optical switch is 1x16 type.
        """
        super(ModelNSW, self).__init__(resource_name)
        if isinstance(slot_or_type, int):
            self.__index = slot_or_type - 1
        else:
            index_map = {
                '1': 0,
                '2': 1,
                '3': 2,
                '1*8': 3,
                '1*16': 4,
            }
            try:
                self.__index = index_map[slot_or_type]
            except KeyError:
                raise KeyError('Invalid value for slot_or_type: %r' % slot_or_type)
        self.__usb_dev = NeoUsbDevice(resource_name)
        self.__reg_ch_sel = 16*self.__index + 130

    @classmethod
    def get_usb_devices(cls) -> List[str]:
        """The USB S/N of all the available devices."""
        return [i["Serial Number"].upper() for i in NeoUsbDevice.get_devices_information()]

    def close(self) -> None:
        "Release the instrument resource."
        pass

    def _check_communication(self) -> None:
        try:
            self.get_channel()
        except Exception as e:
            raise InstrIOError("Check communication failed.") from e

    def set_channel(self, channel: int) -> None:
        """
        Switch to the specified channel route.

        Args:
            channel: The channel number.
        """
        self.__usb_dev.write_registers(0xC2, self.__reg_ch_sel, channel.to_bytes(1, 'big'))
        time.sleep(0.4)
        if self.get_channel() != channel:
            raise ValueError('Set switch channel failed.')

    def get_channel(self) -> int:
        """
        Queries the current channel route of the switch.

        Returns:
            The channel number of current route.
        """
        channel = int.from_bytes(self.__usb_dev.read_registers(0xC2, self.__reg_ch_sel, 1), 'big')
        if channel <= 0:
            raise ValueError('Invalid channel number.')
        return channel


class ModelAT5524(VisaInstrument, TypeSW):
    
    model = "AT5524"
    brand = "Applent"

    def __init__(self, resource_name: str, **kwargs: Any):
        """
        Args:
            resource_name: Resource name or alias of the VISA resource to open.
            **kwargs: Directly passed to `VisaInstrument.__init__`.
        """
        super(ModelAT5524, self).__init__(resource_name, **kwargs)

    def get_channel(self) -> int:
        """
        Queries the current channel route of the switch.

        Returns:
            The channel number of current route.
        """
        return int(self.query('SW?'))

    def set_channel(self, channel: int) -> None:
        """
        Switch to the specified channel route.

        Args:
            channel: The channel number.
        """
        cmd = 'SW {ch:d}'.format(ch=channel)
        self.command(cmd)
        time.sleep(0.5)

        if self.get_channel() != channel:
            raise ValueError('Set switch channel failed.')


class ModelMAP_mOSX_C1(VisaInstrument, TypeMSW):
    """mOSX-C1 is a optical matrix switch by VIAVI."""

    model = "mOSX-C1"

    brand = "VIAVI"     

    details = {
        "Wavelength Range": "1260 ~ 1675 nm",
        "Return Loss": "> 50 dB",
        "Switching Time": "<= 25 ms",
        "Insertion Loss": "<= 1.5 dB",
        "PDL": "< 0.1 dB",
    }

    params = [
        {
            "name": "slot",
            "type": "int",
            "min": 1,
            "max": 8,
        }
    ]

    def __init__(self, resource_name: str, slot: int, **kwargs: Any) -> None:
        """
        Args:
            resource_name: Resource name or alias of the VISA resource to open.
            slot: The slot number in the frame.
            **kwargs: directly passed to `VisaInstrument.__init__`.
        """
        super(ModelMAP_mOSX_C1, self).__init__(resource_name, **kwargs)
        self.__device = '{slot:d},{device}'.format(slot=slot, device=1)

    def get_switch_topology(self) -> Tuple[int, int]:
        """
        Returns the configured switch topology

        Returns:
            M: number of input ports
            N: number of output ports

        Notes:
            For common connection mode, M = total number of ports, N = 0.
        """
        cmd = ':MODUle:TYPE? {device}'.format(device=self.__device)
        rpl = self.query(cmd)
        config = tuple(int(i) for i in rpl.split(','))
        return config

    def set_switch_topology(self, n_in: int, n_out: int) -> None:
        """
        Sets the switch topology to emulate an MxN switch or common connection.
        All the channels will be cleared after topology changed.

        Args:
            n_in: Number of input ports (0 for common connection mode).
            n_out: Number of output ports (0 for common connection mode).
        """
        cmd = ':MODUle:TYPe {device},{n_in},{n_out}'.format(
            device=self.__device,
            n_in=n_in,
            n_out=n_out
        )
        self.command(cmd)

    def list_channels(self) -> List[Tuple[int, int, bool]]:
        """
        Returns a list of all configured connections and their status.

        Returns:
            All configured connections and their status. [(port1, port2, state), ...].

            For state, False = Disabled, True = Enabled.
        """
        cmd = ':ROUTe:LIST? {device}'.format(device=self.__device)
        rpl = self.query(cmd)
        channels = []
        for s in rpl.split(','):
            spl = s.split()
            port1, port2 = (int(i) for i in spl[0].split('-'))
            state = bool(int(spl[1]))
            channels.append((port1, port2, state))
        return channels

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
        m, n = self.get_switch_topology()
        if m == n:
            raise ValueError('Invalid port value: please select 2 different ports. port1={port1}, port2={port2}'.format(port1=port1, port2=port2))
        if n == 0:
            if port1 > m or port2 > m:
                raise ValueError('Invalid port value: exceed max port number {m}. port1={port1}, port2={port2}'.format(m=m, port1=port1, port2=port2))
        else:
            if not (port1 <= m)^(port2 <= m):
                raise ValueError('Invalid port value for {m}x{n} switch: port1={port1}, port2={port2}'.format(m=m, n=n, port1=port1, port2=port2))
        cmd = ':ROUTe:CLOSe {device},{port1:d},{port2:d},{state:d}'.format(
            device=self.__device, port1=port1, port2=port2, state=enable
        )
        self.command(cmd)

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
        cmd = ':ROUTe:CLOSe? {device},{port:d}'.format(device=self.__device, port=port)
        rpl = self.query(cmd)
        return int(rpl) or None

    def clear(self, port: int) -> None:
        """
        Clears a configured optical connection connected to the specified port.

        Args:
            port: The port at either end of the configured connection.
        """
        cmd = ':ROUTe:CLEAR {device},{port:d}'.format(device=self.__device, port=port)
        self.command(cmd)

    def clear_all(self) -> None:
        """Clears all configured optical connections."""
        cmd = ':ROUTe:CLEAR:ALL {device}'.format(device=self.__device)
        self.command(cmd)

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
        cmd = ':ROUTe:CHECK? {device},{port1:d},{port2:d}'.format(
            device=self.__device, port1=port1, port2=port2
        )
        rpl = self.query(cmd)
        return bool(int(rpl))

    def enable(self, port: int, enable: bool = True) -> None:
        """
        Sets the connection state of a configured optical connection.

        Args:
            port: The port at either end of the connection.
            enable: True = Enable | False = Disable.
        """
        cmd = ':ROUTe:ENABle {device},{port:d},{state:d}'.format(
            device=self.__device, port=port, state=enable
        )
        self.command(cmd)

    def disable(self, port: int) -> None:
        """
        Disable the connection of a configured optical connection.

        Args:
            port: The port at either end of the connection.
        """
        return self.enable_channel(port, enable=False)

    def is_enabled(self, port: int) -> bool:
        """
        Returns the connection state of a configured optical connection.

        Returns:
            True = Enabled | False = Disabled
        """
        cmd = ':ROUTe:ENABle? {device},{port:d}'.format(device=self.__device, port=port)
        rpl = self.query(cmd)
        return bool(int(rpl))


class ModelE3631A(VisaInstrument, TypePS):

    model = "E3631A"

    brand = "Keysight"

    details = {
        "Power Supply Range": "Port 1: 6V, 5A; Port 2: 25V, 1A; Port 3: -25V, 1A"
    }

    params = [
        {
            "name": "port",
            "type": "int",
            "options": [1, 2, 3]
        }
    ]

    def __init__(self, resource_name: str, port: int, **kwargs: Any):
        """
        Args:
            resource_name: Resource name or alias of the VISA resource to open.
            port: The port number among three output ports. 
                - `1`: +6V
                - `2`: +25V
                - `3`: -25V
            **kwargs: directly passed to `VisaInstrument.__init__`.
        """
        super().__init__(resource_name, **kwargs)
        if port not in {1, 2, 3}:
            raise ValueError(f"Invalid parameter port: {port!r}")
        self.__port = port

    def __select_port(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs: Any):
            cmd = f":INSTrument:NSELect {self.port:d}"
            self.command(cmd)
            return func(self, *args, **kwargs)
        return wrapper

    @property
    def port(self) -> int:
        """The selected port number among three output ports."""
        return self.__port
    
    @property
    @__select_port
    def min_voltage(self) -> float:
        """The minimum programmable voltage level in V."""
        cmd = ":VOLTage? MIN"
        v = float(self.query(cmd))
        return v

    @property
    @__select_port
    def max_voltage(self) -> float:
        """The maximum programmable voltage level in V."""
        cmd = ":VOLTage? MAX"
        v = float(self.query(cmd))
        return v

    @property
    @__select_port
    def min_current(self) -> float:
        """The minimum programmable current level in A."""
        cmd = ":CURRent? MIN"
        i = float(self.query(cmd))
        return i

    @property
    @__select_port
    def max_current(self) -> float:
        """The maximum programmable current level in A."""
        cmd = ":CURRent? MAX"
        i = float(self.query(cmd))
        return i
        
    @__select_port
    def enable(self, en: bool = True) -> None:
        """
        Enables (or disables) the outputs of the power supply.

        Args:
            en: `True` = Enable, `False` = Disable.
        """
        if not isinstance(en, bool):
            raise TypeError(f"Parameter en must be a bool, not '{type(en).__name__}'.")
        cmd = f':OUTPut {["OFF", "ON"][int(en)]}'
        self.command(cmd)

    def disable(self) -> None:
        """Disables the output of the power supply."""
        self.enable(False)

    @__select_port
    def is_enabled(self) -> bool:
        """
        Queries whether the output of the power supply is enabled.

        Returns:
            `True` = Enabled, `False` = Disabled
        """
        cmd = ":OUTPut?"
        status = bool(int(self.query(cmd)))
        return status

    @__select_port
    def set_voltage_limit(self, value: int | float) -> None:
        """
        Sets the immediate voltage level of the power supply.

        Args:
            value: The voltage level in V.
        """
        if not 0 <= value <= self.max_voltage:
            raise ValueError(f"The voltage limit value out of range: {value!r}")
        cmd = f":VOLTage {value:.4f}"
        self.command(cmd)

    @__select_port
    def get_voltage_limit(self) -> float:
        """
        Queries the immediate voltage level of the power supply.

        Returns:
            The voltage level in V.
        """
        cmd = ":VOLTage?"
        v = float(self.query(cmd))
        return v

    @__select_port
    def measure_voltage(self) -> float:
        """Queries the voltage measured at the sense terminals of the power 
        supply.

        Returns:
            The voltage measured in V.
        """
        cmd = ":MEASure:VOLTage?"
        v = float(self.query(cmd))
        return v

    @__select_port
    def set_current_limit(self, value: int | float) -> None:
        """
        Sets the immediate current level of the power supply.

        Args:
            value: The current level in A.
        """
        if not 0 <= value <= self.max_current:
            raise ValueError(f"The current limit value out of range: {value!r}")
        cmd = f":CURRent {value:.4f}"
        self.command(cmd)

    @__select_port
    def get_current_limit(self) -> float:
        """
        Queries the immediate current level of the power supply.

        Returns:
            The current level in A.
        """
        cmd = ":CURRent?"
        i = float(self.command(cmd))
        return i

    @__select_port
    def measure_current(self) -> float:
        """Queries the current measured across the current sense resistor 
        inside the power supply.

        Returns:
            The current measured in A.
        """
        cmd = ":MEASure:CURRent?"
        i = float(self.command(cmd))
        return i


class ModelE3633A(VisaInstrument, TypePSwithOvpOcpFunctions):
    
    model = "E3633A"

    brand = "Keysight"

    details = {
        "Power Supply Range": "20 V, 10 A | 8 V, 20 A"
    }

    def __init__(self, resource_name: str, **kwargs: Any):
        """
        Args:
            resource_name: Resource name or alias of the VISA resource to open.
            **kwargs: directly passed to `VisaInstrument.__init__`.
        """
        super().__init__(resource_name, **kwargs)

    def set_output_range(self, option: str) -> None:
        """Selects an output range to be programmed.
        
        Note:
            For model E3633A, the programming ranges are:

            - LOW: 0 V to 8.24 V, 0 A to 20.60 A
            - HIGH: 0 V to 20.60 V, 0 A to 10.30 A
        
        Args:
            option: `"LOW"` | `"HIGH"`
        """
        cmd = f":VOLTage:RANGe {option}"
        self.command(cmd)

    def get_output_range(self) -> str:
        """Queries current selected output range.

        Please refer to `set_output_range()` for more information.
        
        Returns:
            `"LOW"` | `"HIGH"`
        """
    
    @property
    def min_voltage(self) -> float:
        """The minimum programmable voltage level in V."""
        cmd = ":VOLTage? MIN"
        v = float(self.query(cmd))
        return v

    @property
    def max_voltage(self) -> float:
        """The maximum programmable voltage level in V."""
        cmd = ":VOLTage? MAX"
        v = float(self.query(cmd))
        return v

    @property
    def min_current(self) -> float:
        """The minimum programmable current level in A."""
        cmd = ":CURRent? MIN"
        i = float(self.query(cmd))
        return i

    @property
    def max_current(self) -> float:
        """The maximum programmable current level in A."""
        cmd = ":CURRent? MAX"
        i = float(self.query(cmd))
        return i

    def enable(self, en: bool = True) -> None:
        """
        Enables (or disables) the outputs of the power supply.

        Args:
            en: `True` = Enable, `False` = Disable.
        """
        if not isinstance(en, bool):
            raise TypeError(f"Parameter en must be a bool, not '{type(en).__name__}'.")
        cmd = f':OUTPut {["OFF", "ON"][int(en)]}'
        self.command(cmd)

    def disable(self) -> None:
        """Disables the output of the power supply."""
        self.enable(False)

    def is_enabled(self) -> bool:
        """
        Queries whether the output of the power supply is enabled.

        Returns:
            `True` = Enabled, `False` = Disabled
        """
        cmd = ":OUTPut?"
        status = bool(int(self.query(cmd)))
        return status

    def set_voltage_limit(self, value: int | float) -> None:
        """
        Sets the immediate voltage level of the power supply.

        Args:
            value: The voltage level in V.
        """
        if not 0 <= value <= self.max_voltage:
            raise ValueError(f"The voltage limit value out of range: {value!r}")
        cmd = f":VOLTage {value:.4f}"
        self.command(cmd)

    def get_voltage_limit(self) -> float:
        """
        Queries the immediate voltage level of the power supply.

        Returns:
            The voltage level in V.
        """
        cmd = ":VOLTage?"
        v = float(self.query(cmd))
        return v

    def measure_voltage(self) -> float:
        """Queries the voltage measured at the sense terminals of the power 
        supply.

        Returns:
            The voltage measured in V.
        """
        cmd = ":MEASure:VOLTage?"
        v = float(self.query(cmd))
        return v

    def set_current_limit(self, value: int | float) -> None:
        """
        Sets the immediate current level of the power supply.

        Args:
            value: The current level in A.
        """
        if not 0 <= value <= self.max_current:
            raise ValueError(f"The current limit value out of range: {value!r}")
        cmd = f":CURRent {value:.4f}"
        self.command(cmd)

    def get_current_limit(self) -> float:
        """
        Queries the immediate current level of the power supply.

        Returns:
            The current level in A.
        """
        cmd = ":CURRent?"
        i = float(self.command(cmd))
        return i

    def measure_current(self) -> float:
        """Queries the current measured across the current sense resistor 
        inside the power supply.

        Returns:
            The current measured in A.
        """
        cmd = ":MEASure:CURRent?"
        i = float(self.command(cmd))
        return i

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
        cmd = f":CURRent:PROTection {level:.4f}"
        self.command(cmd)

    def get_ocp_level(self) -> float:
        """Returns the overcurrent protection trip level presently programmed.

        See `set_ocp_level()` for more details.

        Returns:
            The OCP level in A.
        """
        cmd = f":CURRent:PROTection?"
        ocp = float(self.query(cmd))
        return ocp
    
    def enable_ocp(self, enable: bool = True) -> None:
        """Enables (or disables) the overcurrent protection function of the 
        power supply.

        Args:
            enable: `True` = Enable, `False` = Disable.
        """
        if not isinstance(enable, bool):
            raise TypeError(f"Parameter enable must be a bool, not '{type(enable).__name__}'.")
        cmd = f":CURRent:PROTection:STATe {enable:d}"
        self.command(cmd)
        
    def disable_ocp(self) -> None:
        """Disables the overcurrent protection function of the power supply.
        """
        self.enable_ocp(False)

    def is_ocp_enabled(self) -> bool:
        """Queries whether the overcurrent protection function of the power 
        supply is enabled.

        Returns:
            Whether the OCP function is enabled.
        """
        cmd = ":CURRent:PROTection:STATe?"
        enabled = bool(int(self.query(cmd)))
        return enabled

    def is_ocp_tripped(self) -> bool:
        """Queries if the overcurrent protection circuit is tripped and not 
        cleared.

        Returns:
            If the overcurrent protection circuit is tripped and not cleared.
        """
        cmd = ":CURRent:PROTection:TRIPped?"
        tripped = bool(int(self.query(cmd)))
        return tripped

    def clear_ocp(self) -> None:
        """This method causes the overcurrent protection circuit to be 
        cleared. Before using this method, lower the output current below the 
        trip OCP point, or raise the OCP trip level above the output setting.

        Note:
            Note that the overcurrent condition caused by an external source 
            must be removed first before proceeding this method.
        """
        cmd = ":CURRent:PROTection:CLEar"
        self.command(cmd)

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
        cmd = f":VOLTage:PROTection {level:.4f}"
        self.command(cmd)

    def get_ovp_level(self) -> float:
        """Returns the overvoltage protection trip level presently programmed.

        See `set_ovp_level()` for more details.

        Returns:
            The OVP level in V.
        """
        cmd = ":VOLTage:PROTection?"
        ovp = float(self.query(cmd))
        return ovp

    def enable_ovp(self, enable: bool = True) -> None:
        """Enables (or disables) the overvoltage protection function of the 
        power supply.

        Args:
            enable: `True` = Enable, `False` = Disable.
        """
        if not isinstance(enable, bool):
            raise TypeError(f"Parameter enable must be a bool, not '{type(enable).__name__}'.")
        cmd = f":VOLTage:PROTection:STATe {enable:d}"
        self.command(cmd)

    def disable_ovp(self) -> None:
        """Disables the overvoltage protection function of the power supply.
        """
        self.enable_ovp(False)

    def is_ovp_enabled(self) -> bool:
        """Queries whether the overvoltage protection function of the power 
        supply is enabled.

        Returns:
            Whether the OVP function is enabled.
        """
        cmd = ":VOLTage:PROTection:STATe?"
        enabled = bool(int(self.query(cmd)))
        return enabled
    
    def is_ovp_tripped(self) -> bool:
        """Queries if the overvoltage protection circuit is tripped and not 
        cleared.

        Returns:
            If the overvoltage protection circuit is tripped and not cleared.
        """
        cmd = ":VOLTage:PROTection:TRIPped?"
        tripped = bool(int(self.query(cmd)))
        return tripped

    def clear_ovp(self) -> None:
        """This method causes the overvoltage protection circuit to be 
        cleared. Before sending this method, lower the output voltage below 
        the trip OVP point, or raise the OVP trip level above the output
        setting.

        Note:
            Note that the overvoltage condition caused by an external source 
            must be removed first before proceeding this method.
        """
        cmd = ":VOLTage:PROTection:CLEar"
        self.command(cmd)


class ModelPDLE101(VisaInstrument, TypePDLE):

    model = "PDLE-101"

    brand = "General Photonics"

    details = {
        "Wavelength Range": "1520 ~ 1570 nm",
        "Insertion Loss (Max.)": "3 dB at PDL=0",
        "PDL Range": "0.1 to 20 dB",
        "PDL Resolution": "0.1 dB",
        "PDL Accuracy": "2 ± (0.1 dB +1% of PDL)"
    }

    def __init__(self, resource_name: str, write_termination: str = '', read_termination: str = '#', **kwargs: Any) -> None:
        super(ModelPDLE101, self).__init__(
            resource_name, write_termination=write_termination, read_termination=read_termination, **kwargs
        )

    def __format_result(self, result: str) -> str:
        return result[1:]

    @property
    def opc(self):
        # PDLE-101 does not support *OPC query, return '1' for compliance
        return '1'

    @property
    def min_frequency(self) -> float:
        """The minimum settable optical frequency value in THz."""
        return super().min_frequency

    @property
    def max_frequency(self) -> float:
        """The maximum settable optical frequency value in THz."""
        return super().max_frequency

    @property
    def min_wavelength(self) -> float:
        """The minimum settable optical wavelength value in nm."""
        return 1520.0

    @property
    def max_wavelength(self) -> float:
        """The maximum settable optical wavelength value in nm."""
        return 1570.0
    
    @property
    def min_pdl(self) -> float:
        """The minimum settable PDL value."""
        return 0.1

    @property
    def max_pdl(self) -> float:
        """The maximum settable PDL value."""
        return 20.0

    def get_frequency(self) -> float:
        """
        Queries the optical frequency setting of the instrument in THz.

        Returns:
            The optical frequency setting value in THz.
        """
        return super().get_frequency()
    
    def set_frequency(self, frequency: int | float) -> None:
        """Set optical frequency.

        Args:
            frequency: The optical frequency setting in THz.
        """
        return super().set_frequency(frequency)

    def get_wavelength(self) -> float:
        """Queries the optical wavelength setting of the instrument in nm.

        Returns:
            The optical wavelength setting value in nm.
        """
        cmd = "*WAV?"
        wl = float(self.__format_result(self.query(cmd)))
        return wl
    
    def set_wavelength(self, wavelength: int | float) -> None:
        """Set optical wavelength.

        Args:
            wavelength: The optical wavelength setting in nm.
        """
        if not self.min_wavelength <= wavelength <= self.max_wavelength:
            raise ValueError(f"The parameter wavelength is out of range: {wavelength!r}")
        cmd = f"*WAV {round(wavelength):d}#"
        err_code = self.__format_result(self.query(cmd))
        if err_code != 'E00':
            raise Error(f'Error code: {err_code}')
    
    def set_pdl_value(self, value: int | float) -> None:
        """
        Args:
            value: The PDL setting value in dB.
        """
        if not self.min_pdl <= value <= self.max_pdl:
            raise ValueError(f"The parameter value is out of range: {value!r}")
        cmd = f'*PDL {value:.1f}#'
        err_code = self.__format_result(self.query(cmd))
        if err_code != 'E00':
            raise Error(f'Error code: {err_code}')
    
    def get_pdl_value(self) -> float:
        """
        Returns:
            The PDL setting value in dB.
        """
        cmd = '*PDL?'
        pdl = float(self.__format_result(self.query(cmd)))
        return pdl


class ModelPSY201(VisaInstrument, TypePOLC):

    model = "PSY-201"

    brand = "General Photonics"

    details = {
        "Wavelength Range": "1480 ~ 1620 nm",
        "Operating power range": "-35 ~ 10 dBm"
    }

    def __init__(self, resource_name: str, write_termination: str = '\r\n', read_termination: str = '\r\n', **kwargs: Any):
        """
        Args:
            resource_name: Resource name or alias of the VISA resource to open.
            read_termination: Read termination character.
            write_termination: Write termination character.
            **kwargs: Directly passed to `rm.open_resource`.
        """
        super(ModelPSY201, self).__init__(
            resource_name, write_termination=write_termination, read_termination=read_termination, **kwargs
        )

    @property
    def min_frequency(self) -> float:
        """The minimum settable optical frequency value in THz."""
        return super().min_frequency

    @property
    def max_frequency(self) -> float:
        """The maximum settable optical frequency value in THz."""
        return super().max_frequency

    @property
    def min_wavelength(self) -> float:
        """The minimum settable optical wavelength value in nm."""
        return 1480.0

    @property
    def max_wavelength(self) -> float:
        """The maximum settable optical wavelength value in nm."""
        return 1620.0
    
    def get_frequency(self) -> float:
        """
        Queries the optical frequency setting of the instrument in THz.

        Returns:
            The optical frequency setting value in THz.
        """
        return super().get_frequency()

    def set_frequency(self, frequency: int | float) -> None:
        """Set optical frequency.

        Args:
            frequency: The optical frequency setting in THz.
        """
        return super().set_frequency(frequency)
    
    def get_wavelength(self) -> float:
        """Queries the optical wavelength setting of the instrument in nm.

        Returns:
            The optical wavelength setting value in nm.
        """
        cmd = ":CONFigure:WLENgth?"
        wl = float(self.query(cmd))
        return wl
    
    def set_wavelength(self, wavelength: int | float) -> None:
        """Set optical wavelength value. Wavelength setting rounds to the 
        nearest multiple of 5.
        
        Args:
            wavelength: The optical wavelength in nm.
        """
        if not self.min_wavelength <= wavelength <= self.max_wavelength:
            raise ValueError(f"Parameter wavelength is out of range: {wavelength!r}")
        cmd = f":CONFigure:WLENgth {round(wavelength):d}"
        self.command(cmd)

    def _discrete_scramble(self, state: bool, rate: Optional[int | float] = None) -> None:
        """Set discrete scrambling rate and state.
        
        Args:
            state: `True` = Enable scrambling, `False` = Disable scrambling.
            rate: The scrambling rate in points/s.
        """
        if rate is not None:
            if not 0.01 <= rate <= 20000:
                raise ValueError(f'Parameter rate is out of range: {rate!r}')
            cmd1 = f":CONTrol:SCRamble:DISCrete:RATE {rate:.2f}"
            self.command(cmd1)
            self.opc

        cmd2 = f":CONTrol:SCRamble:DISCrete:STATe {state:d}"
        self.command(cmd2)

    def _triangle_scramble(self, state: bool, rate: Optional[int | float] = None) -> None:
        """Set triangle scrambling rate and state.
        
        Args:
            state: `True` = Enable scrambling, `False` = Disable scrambling.
            rate: The scrambling rate in 2π rad/s.
        """
        if rate is not None:
            if not 0.01 <= rate <= 2000:
                raise ValueError(f'Parameter rate is out of range: {rate!r}')
            cmd1 = f":CONTrol:SCRamble:TRIangle:RATE {rate:.2f}"
            self.command(cmd1)
            self.opc
        
        cmd2 = f":CONTrol:SCRamble:TRIangle:STATe {state:d}"
        self.command(cmd2)

    def _tornado_scramble(self, state: bool, _type: Optional[int]=None, rate: Optional[int | float]=None) -> None:
        """Set tornado scrambling rate, type and state.
        
        Args:
            state: `True` = Enable scrambling, `False` = Disable scrambling.
            _type: The scrambling type of tornado.
                `0` = Fixed axis, `1` = Rotating axis.
            rate: The scrambling rate in Rev/s.
        """
        if rate is not None:
            if not 0.01 <= rate <= 2000:
                raise ValueError(f'Parameter rate is out of range: {rate!r}')
            cmd2 = f":CONTrol:SCRamble:TORNado:RATE {rate:.2f}"
            self.command(cmd2)
            self.opc

        if _type is not None:
            cmd1 = f":CONTrol:SCRamble:TORNado:TYPE {_type:d}"
            self.command(cmd1)
            self.opc
        
        cmd3 = f":CONTrol:SCRamble:TORNado:STATe {state:d}"
        self.command(cmd3)
    
    def get_sop(self) -> Tuple[float, float, float]:
        """Query measured SOP (Stokes parameters) S1, S2, S3.

        Returns:
            The stokes parameters S1, S2, S3.
        """
        cmd = ":MEASure:SOP?"
        reply = self.query(cmd)
        try:
            s1, s2, s3 = (float(i) for i in reply.split(','))
        except ValueError:
            raise ValueError(f'Get SOP failed: {reply}')
        return s1, s2, s3

    def get_dop(self) -> float:
        """Query measured degree of polarization.

        Returns:
            The degree of polarization.
        """
        cmd = ':MEASure:DOP?'
        reply = self.query(cmd)
        try:
            dop = float(reply)
        except ValueError:
            raise ValueError(f'Get DOP failed: {reply}')
        return dop

    def set_sop(self, s1: int | float, s2: int | float, s3: int | float) -> None:
        """Set SOP by Stokes parameters and enable tracking.

        Args:
            s1: 1st dimention of the Stokes parameters.
            s2: 2nd dimention of the Stokes parameters.
            s3: 3rd dimention of the Stokes parameters.

        Tips:
            Stokes parameters are auto-normalized to unit vector before 
            tracking:

            SOP will be set to `(s1/A, s2/A, s3/A)` where

            `A = sqrt(s1*s1, s2*s2, s3*s3)`

        Note:
            `s1=s2=s3=0` is not allowed.
        """
        if s1==s2==s3==0:
            raise ValueError("s1=s2=s3=0 is not allowed.")
        cmd = f":CONTrol:SOP {s1:.2f},{s2:.2f},{s3:.2f}"
        self.command(cmd)

    def set_sop_in_spherical(self, theta: int | float, phi: int | float) -> None:
        """ Set SOP in spherical coordinates and enable tracking.

        Args:
            theta: 1st dimension in degree of the spherical coordinates. 0 to 360 (degrees).
            phi: 2nd dimention in degree of the spherical cordinates. 0 to 180 (degrees).
        """
        if not 0 <= theta <= 360:
            raise ValueError(f"Parameter theta is out of range: {theta!r}")
        if not 0 <= phi <= 180:
            raise ValueError(f"Parameter phi is out of range: {phi!r}")
        cmd = f":CONTrol:ANGLe {theta:.2f},{phi:.2f}"
        self.command(cmd)

    def start_scrambling(self, mode: str, rate: int | float, **params: Any) -> None:
        """Start scrambling with specified mode and speed.

        Args:
            mode: Scrambling mode.

                - `DISCrete`: Discrete scrambling.
                - `TRIangle`: Triangle scrambling.
                - `TORNado`: Tornado scrambling. Additional scrambling parameter `_type` is required.
            rate: Scrambling rate. Different mode may have different units.
            **params: Additional scrambling params if any.

                * `_type (int)`: For `TORNado` mode only. `0` = Fixed axis, `1` = Rotating axis.

        Note:
            Different mode has different unit for scrambling rate:

            - Discrete: points/s
            - Triangle: 2π rad/s
            - Tornado: rev/s
        """
        if mode.upper().startswith('DISC'):
            self._discrete_scramble(True, rate=rate)
        elif mode.upper().startswith('TRI'):
            self._triangle_scramble(True, rate=rate)
        elif mode.upper().startswith('TORN'):
            self._tornado_scramble(True, _type=params['_type'], rate=rate)
        else:
            raise ValueError(f"Invalid mode: {mode!r}")

    def stop_scrambling(self) -> None:
        """Stop scrambling."""
        self._tornado_scramble(False)


class ModelPSY101(VisaInstrument, TypePOLC):

    model = "PSY-101"

    brand = "General Photonics"

    details = {
        "Wavelength Range": "1500 ~ 1600 nm",
        "Operating Power Range": "-15 ~ 10 dBm"
    }

    def __init__(self, resource_name: str, read_termination: str = '#', write_termination: str = '', **kwargs: Any):
        """
        Args:
            resource_name: Resource name or alias of the VISA resource to open.
            read_termination: Read termination character.
            write_termination: Write termination character.
            **kwargs: Directly passed to `rm.open_resource`.
        """
        super().__init__(resource_name, read_termination, write_termination, **kwargs)

    def __format_result(self, result: str) -> str:
        return result[1:]

    @property
    def opc(self):
        # PSY-101 does not support *OPC query, return '1' for compliance
        return '1'

    @property
    def min_frequency(self) -> float:
        """The minimum settable optical frequency value in THz."""
        return super().min_frequency

    @property
    def max_frequency(self) -> float:
        """The maximum settable optical frequency value in THz."""
        return super().max_frequency

    @property
    def min_wavelength(self) -> float:
        """The minimum settable optical wavelength value in nm."""
        return 1500.0

    @property
    def max_wavelength(self) -> float:
        """The maximum settable optical wavelength value in nm."""
        return 1600.0

    def get_frequency(self) -> float:
        """
        Queries the optical frequency setting of the instrument in THz.

        Returns:
            The optical frequency setting value in THz.
        """
        return super().get_frequency()

    def set_frequency(self, frequency: int | float) -> None:
        """Set optical frequency.

        Args:
            frequency: The optical frequency setting in THz.
        """
        return super().set_frequency(frequency)

    def get_wavelength(self) -> float:
        """Queries the optical wavelength setting of the instrument in nm.

        Returns:
            The optical wavelength setting value in nm.
        """
        cmd = "*WAV?"
        wl = float(self.__format_result(self.query(cmd)))
        return wl

    def set_wavelength(self, wavelength: int | float) -> None:
        """Set optical wavelength.

        Args:
            wavelength: The optical wavelength setting in nm.
        """
        if not self.min_wavelength <= wavelength <= self.max_wavelength:
            raise ValueError(f"The parameter wavelength is out of range: {wavelength!r}")
        cmd = f"*WAV {round(wavelength):d}#"
        err_code = self.__format_result(self.query(cmd))
        if err_code != 'E00':
            raise Error(f'Error code: {err_code}')

    def _random_scramble(self, state: bool, rate: Optional[int | float] = None) -> None:
        """Set random scrambling rate and state.
        
        Args:
            state: `True` = Enable scrambling, `False` = Disable scrambling.
            rate: The scrambling rate in Hz.
        """
        if rate is not None:
            if not 1 <= rate <= 6000:
                raise ValueError(f"Parameter rate is out of range: {rate!r}")
            cmd1 = f"*RAN:FRQ {rate:d}#"
            err_code = self.__format_result(self.query(cmd1))
            if err_code != 'E00':
                raise Error(f'Error code: {err_code}')
            self.opc
        
        cmd2 = f"*RAN:ENA {['OFF', 'ON'][state]}#"
        err_code = self.__format_result(self.query(cmd2))
        if err_code != 'E00':
            raise Error(f'Error code: {err_code}')

    def _saw_scramble(self, state: bool, rate: Optional[int | float] = None) -> None:
        """Set saw wave scrambling rate and state.
        
        Args:
            state: `True` = Enable scrambling, `False` = Disable scrambling.
            rate: The scrambling rate in Hz.
        """
        if rate is not None:
            if not 0.1 <= rate <= 500.0:
                raise ValueError(f"Parameter rate is out of range: {rate!r}")
            cmd1 = f"*SAW:FRQ {rate:.1f}#"
            err_code = self.__format_result(self.query(cmd1))
            if err_code != 'E00':
                raise Error(f'Error code: {err_code}')
            self.opc
        
        cmd2 = f"*SAW:ENA {['OFF', 'ON'][state]}#"
        err_code = self.__format_result(self.query(cmd2))
        if err_code != 'E00':
            raise Error(f'Error code: {err_code}')

    def start_scrambling(self, mode: str, rate: int | float, **params: Any) -> None:
        """Start scrambling with specified mode and speed.

        Args:
            mode: Scrambling mode.

                - `RANdom`: Random scrambling.
                - `SAW`: Saw wave scrambling.

            rate: Scrambling rate in Hz.
            **params: Not used for PSY-101.
        """
        if mode.upper().startswith('RAN'):
            self._random_scramble(True, rate=rate)
        elif mode.upper().startswith('SAW'):
            self._saw_scramble(True, rate=rate)
        else:
            raise ValueError(f"Invalid mode: {mode!r}")

    def stop_scrambling(self) -> None:
        """Stop scrambling."""
        self._random_scramble(False)


class ModelMPC202(VisaInstrument, TypePOLC):
    
    model = "MPC-202"

    brand = "General Photonics"

    details = {
        'Wavelength Range': '1260 ~ 1650 nm',
        'Scrambling Modes': 'Discrete, Tornado, Rayleigh, Triangle',
        'Tornado Rate': '0 to 60,000 Rev/s',
        'Rayleigh Rate': '0 to 2000 rad/s',
        'Triangle Rate': '0 to 2000 x 2π rad/s',
        'Discrete Rate': '0 to 20,000 points/s'
    }

    def __init__(self, resource_name: str, read_termination: str = '\r\n', write_termination: str = '\r\n', **kwargs: Any):
        """
        Args:
            resource_name: Resource name or alias of the VISA resource to open.
            read_termination: Read termination character.
            write_termination: Write termination character.
            **kwargs: Directly passed to `rm.open_resource`.
        """
        super().__init__(resource_name, read_termination, write_termination, **kwargs)

    @property
    def min_frequency(self) -> float:
        """The minimum settable optical frequency value in THz."""
        return super().min_frequency

    @property
    def max_frequency(self) -> float:
        """The maximum settable optical frequency value in THz."""
        return super().max_frequency

    @property
    def min_wavelength(self) -> float:
        """The minimum settable optical wavelength value in nm."""
        return 1260.0

    @property
    def max_wavelength(self) -> float:
        """The maximum settable optical wavelength value in nm."""
        return 1650.0

    def get_frequency(self) -> float:
        """
        Queries the optical frequency setting of the instrument in THz.

        Returns:
            The optical frequency setting value in THz.
        """
        return super().get_frequency()

    def set_frequency(self, frequency: int | float) -> None:
        """Set optical frequency.

        Args:
            frequency: The optical frequency setting in THz.
        """
        return super().set_frequency(frequency)

    def get_wavelength(self) -> float:
        """Queries the optical wavelength setting of the instrument in nm.

        Returns:
            The optical wavelength setting value in nm.
        """
        cmd = ":CONFigure:WLENgth?"
        wl = float(self.query(cmd))
        return wl

    def set_wavelength(self, wavelength: int | float) -> None:
        """Set optical wavelength.

        Args:
            wavelength: The optical wavelength setting in nm.
        """
        if not self.min_wavelength <= wavelength <= self.max_wavelength:
            raise ValueError(f"Parameter wavelength is out of range: {wavelength!r}")
        cmd = f":CONFigure:WLENgth {round(wavelength):d}"
        self.command(cmd)

    def _discrete_scramble(self, state: bool, rate: Optional[int | float] = None) -> None:
        """Set discrete scrambling rate and state.
        
        Args:
            state: `True` = Enable scrambling, `False` = Disable scrambling.
            rate: The scrambling rate in points/s.
        """
        if rate is not None:
            if not 0.01 <= rate <= 20000:
                raise ValueError(f'Parameter rate is out of range: {rate!r}')
            cmd1 = f":SCRamble:DISCrete:RATE {rate:.2f}"
            self.command(cmd1)
            self.opc
        
        cmd2 = f":SCRamble:DISCrete:STATe {['OFF', 'ON'][state]}"
        self.command(cmd2)

    def _triangle_scramble(self, state: bool, rate: Optional[int | float] = None) -> None:
        """Set triangle scrambling rate and state.
        
        Args:
            state: `True` = Enable scrambling, `False` = Disable scrambling.
            rate: The scrambling rate in 2π rad/s.
        """
        if rate is not None:
            if not 0.01 <= rate <= 2000:
                raise ValueError(f'Parameter rate is out of range: {rate!r}')
            cmd1 = f":SCRamble:TRIangle:RATE {rate:.2f}"
            self.command(cmd1)
            self.opc
        
        cmd2 = f":SCRamble:TRIangle:STATe {['OFF', 'ON'][state]}"
        self.command(cmd2)

    def _rayleigh_scramble(self, state: bool, rate: Optional[int | float] = None) -> None:
        """Set Rayleigh scrambling rate and state.
        
        Args:
            state: `True` = Enable scrambling, `False` = Disable scrambling.
            rate: The scrambling rate in rad/s.
        """
        if rate is not None:
            if not 0.01 <= rate <= 2000:
                raise ValueError(f'Parameter rate is out of range: {rate!r}')
            cmd1 = f":SCRamble:RAYLeigh:RATE {rate:.2f}"
            self.command(cmd1)
            self.opc

        cmd2 = f":SCRamble:RAYLeigh:STATe {['OFF', 'ON'][state]}"
        self.command(cmd2)

    def _tornado_scramble(self, state: bool, _type: Optional[int]=None, rate: Optional[int | float]=None) -> None:
        """Set tornado scrambling rate, type and state.
        
        Args:
            state: `True` = Enable scrambling, `False` = Disable scrambling.
            _type: The scrambling type of tornado.
                `0` = Fixed rotation axis, `1` = Moving rotation axis.
            rate: The scrambling rate in rev/s.
        """
        if rate is not None:
            if not 0.01 <= rate <= 60000:
                raise ValueError(f'Parameter rate is out of range: {rate!r}')
            cmd2 = f":SCRamble:TORNado:RATE {rate:.2f}"
            self.command(cmd2)
            self.opc

        if _type is not None:
            cmd1 = f":SCRamble:TORNado:TYPE {_type:d}"
            self.command(cmd1)
        
        cmd3 = f":SCRamble:TORNado:STATe {['OFF', 'ON'][state]}"
        self.command(cmd3)
    
    def start_scrambling(self, mode: str, rate: int | float, **params: Any) -> None:
        """Start scrambling with specified mode and speed.

        Args:
            mode: Scrambling mode.

                - `DISCrete`: Discrete scrambling.
                - `TRIangle`: Triangle scrambling.
                - `RAYLeigh`: Rayleigh scrambling.
                - `TORNado`: Tornado scrambling. Additional scrambling parameter `_type` is required.
            rate: Scrambling rate. Different mode may have different units.
            **params: Additional scrambling params if any.

                * `_type (int)`: For `TORNado` mode only. `0` = Fixed axis, `1` = Rotating axis.

        Note:
            Different mode has different unit for scrambling rate:

            - Discrete: points/s
            - Triangle: 2π rad/s
            - Rayleigh: rad/s
            - Tornado: rev/s
        """
        if mode.upper().startswith('DISC'):
            self._discrete_scramble(True, rate=rate)
        elif mode.upper().startswith('TRI'):
            self._triangle_scramble(True, rate=rate)
        elif mode.upper().startswith('RAYL'):
            self._rayleigh_scramble(True, rate=rate)
        elif mode.upper().startswith('TORN'):
            self._tornado_scramble(True, _type=params['_type'], rate=rate)
        else:
            raise ValueError(f"Invalid mode: {mode!r}")

    def stop_scrambling(self) -> None:
        """Stop scrambling."""
        self._tornado_scramble(False)


class ModelEPS1000(BaseInstrument, TypePOLC):
    
    model = "EPS1000"
    brand = "Novoptel"
    details = {
        "Wavelength Range": "1510.3-1639.1 nm",
        "Frequency Range": "182.9-198.5 THz",
        "Insertion loss": "1.5-3 dB",
        "Peaked Rate": "0-20,000,000 rad/s",
        "Rayleigh Rate": "0-10,000,000 rad/s"
    }

    def __init__(self, resource_name: str, timeout: int | float = 3000):
        """
        Args:
            resource_name: The S/N of the instrument model to open.
            timeout: Timeout in milliseconds for all resource I/O operations.
        """
        super().__init__(resource_name)

        baudrate = 230400

        device_list = ftd.listDevices()

        for i in range(len(device_list)):
            desc = ftd.getDeviceInfoDetail(i)["description"].decode()
            if desc.startswith('EPS1000'):
                sn = desc.split()[-1]
            else:
                continue
            if resource_name.endswith(sn):
                self.__device_num = i
                break
        else:
            raise ValueError('Device not found: {model} | S/N:{sn}'.format(model=self.model, sn=resource_name))        

        self.__device = ftd.open(self.__device_num)
        self.__device.setBaudRate(baudrate)
        self.__device.setDataCharacteristics(8, 0, 0)
        self.__device.setTimeouts(round(timeout), round(timeout))
        self.__connected = True

    def _check_communication(self) -> None:
        return self.__connected

    @property
    def min_frequency(self) -> float:
        """The minimum settable optical frequency value in THz."""
        return 182.9

    @property
    def max_frequency(self) -> float:
        """The maximum settable optical frequency value in THz."""
        return 198.5

    @property
    def min_wavelength(self) -> float:
        return super().min_wavelength

    @property
    def max_wavelength(self) -> float:
        return super().max_wavelength

    def close(self) -> None:
        """Release the instrument resource."""
        self.__device.close()
        self.__connected = False

    def __write_register(self, addr, data) -> None:
        if not self.__connected:
            raise ValueError('Device is closed. Please connect first.')
        time.sleep(0.01)
        write_str = 'W' + '{:03X}'.format(addr) + '{:04X}'.format(data) + chr(13)
        write_str_c = ctypes.create_string_buffer(write_str.encode('utf-8'), 9)
        self.__device.write(write_str_c)

    def __read_register(self, addr) -> int:
        if not self.__connected:
            raise ValueError('Device is closed. Please connect first.')
        self.__device.purge()  # clear buffer
        time.sleep(0.01)

        # send request
        read_request = 'R' + '{:03X}'.format(addr) + '0000' + chr(13)
        read_request_c = ctypes.create_string_buffer(read_request.encode('utf-8'), 9)
        self.__device.write(read_request_c)

        # wait response
        bytesavailable=0
        tries=0
        while bytesavailable<5 and tries<1000:
            bytesavailable=self.__device.getQueueStatus()
            tries += 1
            time.sleep(0.001)

        # get responce
        res = self.__device.read(bytesavailable)

        # return responce as integer
        if bytesavailable>4:
            value = int(res.decode("utf-8"),16)
        else:
            raise ValueError('Invalid response from ')

        return value

    def set_qwp(self, qwp_n , direction , speed) -> None:
        """
        qwp_n = 0, 1, 2, 3, 4, 5
        direction = 0(Disabled), 1(Forward), -1(Backward)
        speed = (rad/s)
        """
        control_reg_addr = qwp_n + 1
        speed_reg_addr0 = qwp_n*2+11
        speed_reg_addr1 = qwp_n*2+12
        
        if direction == 0:
            self.__write_register(control_reg_addr, 0)
        elif direction == 1:
            self.__write_register(control_reg_addr, 1)
        elif direction == -1:
            self.__write_register(control_reg_addr, 3)
        else:
            raise ValueError('Invalid value for direction: {}. Options: 0(Disabled), 1(Forward), -1(Backward)'.format(direction))
        
        speed_msb = int((speed*100)/(2**16)) & 0xffff
        speed_lsb = int((speed*100)) & 0xffff
        
        self.__write_register(speed_reg_addr0, speed_lsb)
        self.__write_register(speed_reg_addr1, speed_msb)
        
    def set_hwp(self, direction , speed) -> None:
    
        """
        direction = 0(Disabled), 1(Forward), -1(Backward)
        speed = (krad/s)
        """
        
        control_reg_addr = 0
        speed_reg_addr0 = 9
        speed_reg_addr1 = 10

        if direction == 0:
            self.__write_register(control_reg_addr, 0)
        elif direction == 1:
            self.__write_register(control_reg_addr, 1)
        elif direction == -1:
            self.__write_register(control_reg_addr, 3)
        else:
            raise ValueError('Invalid value for direction: {}. Options: 0(Disabled), 1(Forward), -1(Backward)'.format(direction))

        speed_msb = int((speed*100)/(2**16)) & 0xffff
        speed_lsb = int((speed*100)) & 0xffff
        
        self.__write_register(speed_reg_addr0, speed_lsb)
        self.__write_register(speed_reg_addr1, speed_msb)

    def get_frequency(self) -> float:
        """
        Queries the optical frequency setting of the instrument in THz.

        Returns:
            The optical frequency setting value in THz.
        """
        value = int(self.__read_register(addr=25))
        freq = (value + 1828)/10
        return freq

    def set_frequency(self, frequency: int | float) -> None:
        """Set optical frequency.

        Args:
            frequency: The optical frequency setting in THz.
        """
        if not self.min_frequency <= frequency <= self.max_frequency:
            raise ValueError(f"Parameter frequency is out of range: {frequency!r}")
        value = round(frequency*10 - 1828)
        self.__write_register(addr=25, data=value)
        time.sleep(0.1)

    def get_wavelength(self) -> float:
        """Queries the optical wavelength setting of the instrument in nm.

        Returns:
            The optical wavelength setting value in nm.
        """
        return super().get_wavelength()

    def set_wavelength(self, wavelength: int | float) -> None:
        """Set optical wavelength value.
        
        Args:
            wavelength: The optical wavelength in nm.
        """
        return super().set_wavelength(wavelength)

    def start_scrambling(self, mode: str, rate: int | float, **params) -> None:
        '''
        The unit of rate is rad/s.
        - When mode is 'Peaked', the max rate is 2000000rad/s
        - When mode is  'Rayleigh', the max rate is 1000000rad/s
        - When mode is 'Marvell', the unit is rad/s
        '''
        speed = rate
        if mode == 'Peaked':
            if 0 <= speed <= 20000000:
                speed_10 = round(speed/10)
                lsb = speed_10&0xFFFF
                msb = (2<<14)|(speed_10>>16)
                self.__write_register(addr=23, data=lsb)
                self.__write_register(addr=24, data=msb)
            else:
                raise ValueError("Speed is out of range, the max speed of 'Peaked' mode is 2000000rad/s")

        elif mode == 'Rayleigh':
            if 0 <= speed <= 10000000:
                speed_10 = round(speed/10)
                lsb = speed_10&0xFFFF
                msb = (3<<14)|(speed_10>>16)
                self.__write_register(addr=23, data=lsb)
                self.__write_register(addr=24, data=msb)
            else:
                raise ValueError("Speed is out of range, the max speed of 'Rayleigh' mode is 1000000rad/s")

        elif mode == 'Marvell':
            self.stop_scrambling()
            self.__write_register(addr=23, data=0)
            self.__write_register(addr=24, data=0)
            time.sleep(0.1)

            qwp_speed = speed / 6
            offset = 0.02
            self.set_qwp(qwp_n=0, direction=1, speed=qwp_speed*(1.0+offset))
            self.set_qwp(qwp_n=1, direction=-1, speed=qwp_speed*(1.0-offset))
            self.set_qwp(qwp_n=2, direction=1, speed=qwp_speed*(1.0+offset))
            self.set_hwp(direction=-1, speed=0.01) # -1 is backward. 0.01 could be just rad/s
            self.set_qwp(qwp_n=3, direction=-1, speed=qwp_speed*(1.0-offset))
            self.set_qwp(qwp_n=4, direction=1, speed=qwp_speed*(1.0+offset))
            self.set_qwp(qwp_n=5, direction=-1, speed=qwp_speed*(1.0-offset))
            if qwp_speed < 10:
                self.set_hwp(direction=0, speed=0)

    def stop_scrambling(self) -> None:
        """Stop scrambling."""
        self.start_scrambling('Peaked', 0)


class ModelPMD1000(VisaInstrument, TypePMDE):
    model = "PMD-1000"
    brand = "General Photonics"
    details = {
        "Wavelength Range": "C Band",
        "Insertion Loss": "5.5 dB",
        "1st Order PMD Range": "0.36 to 182.4 ps",
        "2nd Order PMD Range": "8100 ps2"
    }

    def __init__(self, resource_name: str, read_termination: str = '#', write_termination: str = '', **kwargs: Any):
        super().__init__(resource_name, read_termination, write_termination, **kwargs)

    def _formatted_query(self, cmd) -> str:
        return self.query(cmd)[1:]

    @property
    def opc(self):
        # PMD1000 does not support *OPC query, return '1' for compliance
        return '1'

    @property
    def min_frequency(self) -> float:
        """The minimum settable optical frequency value in THz."""
        return 191.6

    @property
    def max_frequency(self) -> float:
        """The maximum settable optical frequency value in THz."""
        return 195.9

    @property
    def min_wavelength(self) -> float:
        """The minimum settable optical wavelength value in nm."""
        return super().min_wavelength

    @property
    def max_wavelength(self) -> float:
        """The maximum settable optical wavelength value in nm."""
        return super().max_wavelength
    
    def get_frequency(self) -> float:
        """
        Queries the optical frequency setting of the instrument in THz.

        Returns:
            The optical frequency setting value in THz.
        """
        ch_str = self._formatted_query('*CHA?')
        if ch_str[0] != 'C':
            raise ValueError('Unexpected Reply')
        ch = int(ch_str[1:])
        freq = 191.6 + (ch-1)*0.05
        return freq

    def set_frequency(self, frequency: int | float) -> None:
        """Set optical frequency value.

        Note:
            The PMD-1000 can only set to several discrete values on the 
            ITU C-band:

                frequency = 191.6 + n*0.05, 0 <= n <= 86

            If the frequency is not on the ITU grid, it will be set to 
            the nearest valid value, and no exception will be raised.

        Args:
            frequency: optical frequency in THz.
        """
        if not self.min_frequency <= frequency <= self.max_frequency:
            raise ValueError(f'frequency is out of range: {frequency!r}')
        ch = round((frequency - 191.6)/0.05)+1
        self.query('*CHC %03d#' % ch)

    def get_wavelength(self) -> float:
        """Queries the optical wavelength setting of the instrument in nm.

        Returns:
            The optical wavelength setting value in nm.
        """
        return super().get_wavelength()

    def set_wavelength(self, wavelength: int | float) -> None:
        """Set optical wavelength. Please refer to `set_frequency`.

        Args:
            wavelength: The optical wavelength setting in nm.
        """
        return super().set_wavelength(wavelength)
    
    def get_pmd_value(self) -> Tuple[float, float]:
        """
        Get PMD (DGD) and SOPMD (Second Order PMD) target value.

        Returns:
            pmd: The DGD value in ps.
            sopmd: The 2nd order pmd in ps**2.
        """
        cmd = "*PMD:CON CAL?"
        r = self._formatted_query(cmd)
        pmd, sopmd = (float(i) for i in r.split(','))
        return pmd, sopmd

    def set_pmd_value(self, pmd: int | float, sopmd: int | float) -> None:
        """
        Set PMD (DGD) and SOPMD (Second Order PMD) target value.

        Args:
            pmd: The DGD value in ps.
            sopmd: The 2nd order pmd in ps**2.
        
        Note:
            The pmd and sopmd setting of the PMD-1000 is not continuous. The 
            pmd and sopmd will be set to the nearest supported values, so the 
            real value will not be exactly the same with the setting values.
        """
        if not 0 <= pmd <= 182.4:
            raise ValueError(f'pmd is out of range: {pmd}')
        if not 0 <= sopmd <= 8319.9:
            raise ValueError(f'sopmd is out of range: {sopmd}')
        err_code = self._formatted_query('*PMD:CON %.2f,%.2f#' % (pmd, sopmd))
        if err_code != 'E00':
            raise ValueError(f'Error code = {err_code}')
