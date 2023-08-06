

""""""# start delvewheel patch
def _delvewheel_init_patch_1_3_6():
    import ctypes
    import os
    import platform
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'supy.libs'))
    is_pyinstaller = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
    is_conda_cpython = platform.python_implementation() == 'CPython' and (hasattr(ctypes.pythonapi, 'Anaconda_GetVersion') or 'packaged by conda-forge' in sys.version)
    if sys.version_info[:2] >= (3, 8) and not is_conda_cpython or sys.version_info[:2] >= (3, 10):
        if not is_pyinstaller or os.path.isdir(libs_dir):
            os.add_dll_directory(libs_dir)
    else:
        load_order_filepath = os.path.join(libs_dir, '.load-order-supy-2023.5.15.dev0')
        if not is_pyinstaller or os.path.isfile(load_order_filepath):
            with open(os.path.join(libs_dir, '.load-order-supy-2023.5.15.dev0')) as file:
                load_order = file.read().split()
            for lib in load_order:
                lib_path = os.path.join(os.path.join(libs_dir, lib))
                if not is_pyinstaller or os.path.isfile(lib_path):
                    ctypes.WinDLL(lib_path)


_delvewheel_init_patch_1_3_6()
del _delvewheel_init_patch_1_3_6
# end delvewheel patch

###########################################################################
# SuPy: SUEWS that speaks Python
# Authors:
# Ting Sun, ting.sun@reading.ac.uk
# History:
# 20 Jan 2018: first alpha release
# 01 Feb 2018: performance improvement
# 03 Feb 2018: improvement in output processing
# 08 Mar 2018: pypi packaging
# 01 Jan 2019: public release
# 22 May 2019: restructure of module layout
# 02 Oct 2019: logger restructured
###########################################################################


# core functions
from ._supy_module import (
    init_supy,
    load_SampleData,
    load_forcing_grid,
    run_supy,
    save_supy,
    check_forcing,
    check_state,
)


# utilities
from . import util


# version info
from ._version import show_version, __version__

from .cmd import SUEWS

# module docs
__doc__ = """
supy - SUEWS that speaks Python
===============================

**SuPy** is a Python-enhanced urban climate model with SUEWS as its computation core.

"""
