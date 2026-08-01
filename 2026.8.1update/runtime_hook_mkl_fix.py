"""
Runtime hook to fix MKL library loading issues
"""
import os
import sys

# Set MKL threading layer to sequential (no threading DLL needed)
os.environ['MKL_THREADING_LAYER'] = 'SEQUENTIAL'

# Force MKL to use the available runtime
os.environ['MKL_ENABLE_INSTRUCTIONS'] = 'SSE4_2'

# Prevent NumPy from trying to load MKL threading libraries
import numpy as np
try:
    # Try to import MKL early and handle the error
    import numpy.core._multiarray_umath as _mu
except:
    pass