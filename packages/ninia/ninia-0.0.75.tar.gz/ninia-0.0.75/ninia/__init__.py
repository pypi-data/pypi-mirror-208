# Copyright 2022 Alex Summers
# See LICENSE file for more information

import sys

if sys.version_info[0] == 2:
    raise ImportError('Ninia requires Python 3.7. This is Python 2.')

__all__ = ['Relax']
__version__ = '0.0.75'

from ninia.relax import Relax
