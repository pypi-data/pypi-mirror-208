

""""""# start delvewheel patch
def _delvewheel_init_patch_1_3_6():
    import os
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'supy.libs'))
    is_pyinstaller = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
    if not is_pyinstaller or os.path.isdir(libs_dir):
        os.add_dll_directory(libs_dir)


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
