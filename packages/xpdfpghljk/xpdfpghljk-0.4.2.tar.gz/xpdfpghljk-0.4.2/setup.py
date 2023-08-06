from setuptools import setup
from Cython.Build import cythonize

setup(ext_modules = cythonize("xpdfpghljk/hello.pyx", language_level=3))
