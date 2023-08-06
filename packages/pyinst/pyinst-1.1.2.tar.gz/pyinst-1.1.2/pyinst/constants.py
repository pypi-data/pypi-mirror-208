"""Provides user-friendly naming to values used in different functions."""
from enum import IntEnum, IntFlag, Enum, unique


LIGHTSPEED = 299792.458  # km/s

# =======================
# Default VISA attributes
# =======================

VI_OPEN_TIMEOUT = 0

VI_TIMEOUT = 2000

VI_QUERY_DELAY = 0.001

VI_READ_TERMINATION = '\n'

VI_WRITE_TERMINATION = '\n'

# =========================
# Default serial attributes
# =========================

SERIAL_READ_TERMINATION = '\n'

SERIAL_WRITE_TERMINATION = '\n'

SERIAL_READ_TIMEOUT = 2000

SERIAL_WRITE_TIMEOUT = 2000

SERIAL_QUERY_DELAY = 0.1

# =====
# Enums
# =====

@unique
class InstrumentType(IntFlag):
    """The flags of instrument types."""
    
    OPM = 1 << 0;   "Optical Power Meter"

    VOA = 1 << 1;   "Variable Optical Attenuator"

    OMA = 1 << 2;   "Optical Modulation Analyzer"

    OSA = 1 << 3;   "Optical Spectrum Analyzer"

    WM = 1 << 4;    "Optical Wavelength Meter"

    OTF = 1 << 5;   "Optical Tunable Filter"

    TS = 1 << 6;    "Temperature Source"

    SW = 1 << 7;    "Optical Switch"

    MSW = 1 << 8;   "Optical Matrix Switch"

    PS = 1 << 9;    "Power Supply"

    PDLE = 1 << 10; "PDL Emulator/Source"

    POLC = 1 << 11; "Polarization Controller/Scrambler"

    PMDE = 1 << 12; "PMD Emulator/Source"


@unique
class TemperatureSourceType(IntEnum):
    UNDEFINED = 0
    CHAMBER = 1
    TEC = 2
    THERMO_STREAM = 3


@unique
class OpticalPowerUnit(IntEnum):
    DBM = 0
    W = 1


@unique
class TemperatureUnit(IntEnum):
    F = 0
    C = 1


@unique
class OpticalBandwidthUnit(IntEnum):
    GHZ = 0
    NM = 1


@unique
class SerialParity(Enum):
    NONE = 'N'
    EVEN = 'E'
    ODD = 'O'
    MARK = 'M'
    SPACE = 'S'


@unique
class SerialStopBits(Enum):
    ONE = 1
    ONE_POINT_FIVE = 1.5
    TWO = 2


@unique
class SerialByteSize(Enum):
    FIVEBITS = 5
    SIXBITS = 6
    SEVENBITS = 7
    EIGHTBITS = 8


@unique
class ChamberOperatingMode(IntEnum):
    OFF = 0
    CONSTANT = 1
    PROGRAM = 2
