from typing import Tuple


class Error(Exception):
    """Abstract basic exception class for this module."""


class InstrIOError(Error):
    """Exception class for Instr I/O errors."""

    def __init__(self, msg) -> None:
        self.msg = msg
        super(InstrIOError, self).__init__(msg)

    def __reduce__(self) -> Tuple[type, Tuple[int]]:
        """Store the error code when pickling."""
        return (InstrIOError, (self.msg,))


class InstrWarning(Warning):
    """Warning class for instrument operations."""

    def __init__(self, msg) -> None:
        self.msg = msg
        super(InstrWarning, self).__init__(msg)

    def __reduce__(self) -> Tuple[type, Tuple[int]]:
        """Store the error code when pickling."""
        return (InstrWarning, (self.msg,))