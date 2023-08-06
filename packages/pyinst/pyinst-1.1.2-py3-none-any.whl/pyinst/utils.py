from __future__ import annotations
import math
import functools
import inspect
import warnings

from .constants import LIGHTSPEED


def w_to_dbm(p_w: int | float) -> float:
    """Convert the optical power in W to dbm.
    
    Args:
        p_w: The optical power value in W.

    Returns:
        The optical power value in dBm.
    """
    if p_w <= 0:
        raise ValueError('Optical power value in W shoud be greater than 0.')
    return 10*math.log(p_w*1000, 10)


def dbm_to_w(p_dbm: int | float) -> float:
    """Convert the optical power in dBm to W.
    
    Args:
        p_dbm: The optical power value in dBm.

    Returns:
        The optical power value in W.
    """
    return 10**(p_dbm/10)/1000


def bw_in_nm_to_ghz(bw_in_nm: int | float, center_wl: int | float) -> float:
    """Convert the optical bandwidth in nm to GHz.

    Args:
        bw_in_nm: The bandwidth in nm.
        center_wl: The center wavelength in nm.

    Returns:
        The bandwidth in GHz.
    """
    return 1000 * (LIGHTSPEED/(center_wl-bw_in_nm/2) - LIGHTSPEED/(center_wl+bw_in_nm/2))


def bw_in_ghz_to_nm(bw_in_ghz: int | float, center_freq: int | float) -> float:
    """Convert the optical bandwidth in GHz to nm.

    Args:
        bw_in_ghz: The bandwidth in GHz.
        center_freq: The center frequency in THz.

    Returns:
        The bandwidth in GHz.
    """
    return LIGHTSPEED/(center_freq-bw_in_ghz/2000) - LIGHTSPEED/(center_freq+bw_in_ghz/2000)


def signed_to_unsigned(s: int, n_bytes: int):
    """Convert a signed int into its 2's complement.
    
    Args:
        s: The signed int to convert.
        n_bytes: The number of bytes of the int.

    Returns:
        The unsigned int (2's complement).
    """
    if not -0x100**n_bytes/2 <= s <= 0x100**n_bytes/2-1:
        raise ValueError(f'{s!r} can not convert into an unsigned int of {n_bytes:d} bytes.')
    b = s.to_bytes(n_bytes, 'big', signed=True)
    u = int.from_bytes(b, 'big', signed=False)
    return u


def unsigned_to_signed(u: int, n_bytes: int) -> int:
    """Convert a unsigned int into signed int.
    
    Args:
        u: The unsigned int to convert.
        n_bytes: The number of bytes of the int.
    
    Returns:
        The signed int.
    """
    if not 0 <= u < 0x100**n_bytes:
        raise ValueError(f'{u!r} is not an unsigned int of {n_bytes:d} bytes.')
    b = u.to_bytes(n_bytes, 'big', signed=False)
    s = int.from_bytes(b, 'big', signed=True)
    return s


def calc_check_sum(b: bytes) -> int:
    """Calculate the checksum of the bytes.
    
    Args:
        b: The bytes to calculate checksum.
    """
    return sum(b) & 0xFF


string_types = (type(b''), type(u''))


def deprecated(reason):
    """
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.

    **Classic usage:**

    To use this, decorate your deprecated function with **@deprecated** decorator:

    ``` python
    @deprecated
    def some_old_function(x, y):
        return x + y
    ```

    You can also decorate a class or a method:

    ``` python
    class SomeClass(object):
        @deprecated
        def some_old_method(self, x, y):
            return x + y
    @deprecated
    class SomeOldClass(object):
        pass
    ```

    You can give a "reason" message to help the developer to choose another function/class:
    
    ``` python
    @deprecated(reason="use another function")
    def some_old_function(x, y):
        return x + y
    ```
    
    :type  reason: str or callable or type
    :param reason: Reason message (or function/class/method to decorate).
    """

    if isinstance(reason, string_types):

        # The @deprecated is used with a 'reason'.
        #
        # .. code-block:: python
        #
        #    @deprecated("please, use another function")
        #    def old_function(x, y):
        #      pass

        def decorator(func1):

            if inspect.isclass(func1):
                fmt1 = "Call to deprecated class {name} ({reason})."
            else:
                fmt1 = "Call to deprecated function {name} ({reason})."

            @functools.wraps(func1)
            def new_func1(*args, **kwargs):
                with warnings.simplefilter('always', DeprecationWarning):
                    warnings.warn(
                        fmt1.format(name=func1.__name__, reason=reason),
                        category=DeprecationWarning,
                        stacklevel=2
                    )
                return func1(*args, **kwargs)

            return new_func1

        return decorator

    elif inspect.isclass(reason) or inspect.isfunction(reason):

        # The @deprecated is used without any 'reason'.
        #
        # .. code-block:: python
        #
        #    @deprecated
        #    def old_function(x, y):
        #      pass

        func2 = reason

        if inspect.isclass(func2):
            fmt2 = "Call to deprecated class {name}."
        else:
            fmt2 = "Call to deprecated function {name}."

        @functools.wraps(func2)
        def new_func2(*args, **kwargs):
            with warnings.simplefilter('always', DeprecationWarning):
                warnings.warn(
                   fmt2.format(name=func2.__name__),
                    category=DeprecationWarning,
                    stacklevel=2
                )
            return func2(*args, **kwargs)

        return new_func2

    else:
        raise TypeError(repr(type(reason)))
