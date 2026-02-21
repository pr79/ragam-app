import sys
import os

print("--- DEBUG INFO ---")
print(f"Python Executable: {sys.executable}")
print(f"CWD: {os.getcwd()}")
print("sys.path:")
for p in sys.path:
    print(f"  {p}")

try:
    import numpy
    print(f"\nNumPy Version: {numpy.__version__}")
    print(f"NumPy File: {numpy.__file__}")
except ImportError as e:
    print(f"\nNumPy Import Failed: {e}")

try:
    import numba
    print(f"\nNumba Version: {numba.__version__}")
    print(f"Numba File: {numba.__file__}")
except ImportError as e:
    print(f"\nNumba Import Failed: {e}")

print("------------------")
