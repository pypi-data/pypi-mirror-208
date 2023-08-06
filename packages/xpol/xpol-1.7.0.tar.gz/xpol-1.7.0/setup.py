#!/usr/bin/env python
import os
import setuptools
from numpy import get_include
from numpy.distutils.core import setup
from numpy.distutils.extension import Extension


compile_opts = {
    "extra_f90_compile_args": ["-O2", "-fopenmp", "-ffree-line-length-none", "-fPIC"],
    "f2py_options": ["skip:", ":"],
    "extra_link_args": ["-fopenmp"]
}

F2PY_TABLE = {'integer': {'int8': 'char',
                          'int16': 'short',
                          'int32': 'int',
                          'int64': 'long_long'},
              'real': {'real32': 'float',
                       'real64': 'double'},
              'complex': {'real32': 'complex_float',
                          'real64': 'complex_double'}}
try:
    root = os.path.dirname(os.path.abspath(__file__))
except NameError:
    root = os.path.dirname(os.path.abspath(sys.argv[0]))
with open(os.path.join(root, '.f2py_f2cmap'), 'w') as f:
    f.write(repr(F2PY_TABLE))


name = 'xpol'
long_description = open('README.rst').read() if os.path.isfile( 'README.rst') else ''

lib = Extension('_flib',
                sources=['src/xpol.f90'],
                include_dirs=['.', get_include()],
                libraries=['gomp',('fmod', {'sources': ['src/wig3j.f']})],
                **compile_opts)

setup(name=name,
      version="1.7.0",
      description='XPOL cross power-spectrum estimator',
      long_description=long_description,
      url='',
      author='Matthieu Tristram',
      author_email='matthieu.tristram@cnrs.fr',
      install_requires=["astropy","healpy>=0.6.1"],
      packages=['xpol'],
      ext_modules=[lib]
)
