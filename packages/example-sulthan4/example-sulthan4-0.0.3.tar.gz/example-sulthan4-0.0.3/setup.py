from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import setuptools

# Check if we're running on Windows
WINDOWS = sys.platform.startswith('win')

# pybind11 import, if it's missing then try to install it
try:
    import pybind11
    from pybind11 import get_include as get_pybind_include
except ImportError:
    print("pybind11 not found, installing...")
    setuptools.install("pybind11")
    import pybind11
    from pybind11 import get_include as get_pybind_include

# Get the numpy include directory
try:
    import numpy as np
except ImportError:
    print("numpy not found, please install numpy")
    sys.exit(1)

def get_numpy_include():
    """Return numpy include directory."""
    return np.get_include()

# Extension modules
ext_modules = [
    Extension(
        'example',
        sources=['example.cpp'],
        include_dirs=[
            # Path to pybind11 headers
            get_pybind_include(),
            get_numpy_include()
        ],
        language='c++'
    ),
]

# Specify all the necessary options for compilation and linking
if WINDOWS:
    for extension in ext_modules:
        extension.extra_compile_args = ['/utf-8']
        extension.extra_link_args = ['/LTCG']
else:
    for extension in ext_modules:
        extension.extra_compile_args = ['-std=c++11', '-fPIC']
        extension.extra_link_args = ['-std=c++11', '-fPIC']

# setup
setup(
    name='example-sulthan4',
    version='0.0.3',
    author='Your Name',
    author_email='your.email@example.com',
    description='Example project using pybind11',
    ext_modules=ext_modules,
    cmdclass={'build_ext': build_ext},
    zip_safe=False,
)
