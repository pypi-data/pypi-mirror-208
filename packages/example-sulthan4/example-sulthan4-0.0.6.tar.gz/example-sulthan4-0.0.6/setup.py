import sys
from setuptools import setup, Extension

# Get the numpy include directory
try:
    import numpy as np
except ImportError:
    print("numpy not found, please install numpy")
    sys.exit(1)

# Extension modules
ext_modules = [
    Extension(
        'example',
        sources=['example.cpp'],
        include_dirs=[
            # Path to numpy headers
            np.get_include(),
        ],
        language='c++'
    ),
]

# Specify all the necessary options for compilation and linking
if sys.platform.startswith('win'):
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
    version='0.0.6',
    author='Your Name',
    author_email='your.email@example.com',
    description='Example project using numpy',
    ext_modules=ext_modules,
    zip_safe=False,
)
