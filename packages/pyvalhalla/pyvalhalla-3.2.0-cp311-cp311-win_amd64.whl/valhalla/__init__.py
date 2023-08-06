

""""""# start delvewheel patch
def _delvewheel_init_patch_1_3_6():
    import os
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'pyvalhalla.libs'))
    is_pyinstaller = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
    if not is_pyinstaller or os.path.isdir(libs_dir):
        os.add_dll_directory(libs_dir)


_delvewheel_init_patch_1_3_6()
del _delvewheel_init_patch_1_3_6
# end delvewheel patch

from .actor import Actor
from .config import get_config, get_help
from ._valhalla import *
from .__version__ import __version__

__valhalla_commit__ = "cbabe7cfb"
