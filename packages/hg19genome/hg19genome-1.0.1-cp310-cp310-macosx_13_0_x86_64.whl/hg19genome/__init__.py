"""Init for CBS."""

from __future__ import absolute_import
from .import kmers
from . import data
from .core.hg19_core import *
from .core.calculate_bias import calculate_bias, calculate_bin_bias

# This is extracted automatically by the top-level setup.py.
__version__ = '1.0.1'

# Check download was completed


        