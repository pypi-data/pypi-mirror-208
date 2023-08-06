def load_dll_dependencies():
    import platform
    import os
    arch = platform.architecture()[0]
    arch_mapping = {
        '32bit': 'x86',
        '64bit': 'x64'
    }
    dlls_dir = os.path.join(os.path.join(os.path.dirname(__file__), 'DLLs', arch_mapping[arch]))
    os.add_dll_directory(dlls_dir)

# Load DLL dependencies before import other packages
load_dll_dependencies()

# =======================

# from . import functions
from . import abc
from .models import *
from .functions import *
from . import constants

__version__ = '1.1.1'
