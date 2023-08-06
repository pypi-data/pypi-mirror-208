import setuptools
from distutils.extension import Extension
from Cython.Build import cythonize
import Cython.Distutils
import numpy as np
import codecs

def get_version():
    f = codecs.open("./fmsne/__init__.py").read()
    for line in f.splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError('Unable to find version string')

setuptools.setup(
    version = get_version(),
    packages = ['fmsne'],
    platforms = ['any'],
    ext_modules = cythonize([
        Extension('fmsne_implem', [
            'fmsne/fmsne_implem.pyx',
            'fmsne/lbfgs.c'
        ])], annotate=False),
    install_requires = [
        'numpy',
        'numba',
        'Cython',
        'matplotlib',
        'sklearn',
        'scipy'],
    setup_requires = [
        'Cython',
        'numpy'],
    include_dirs = [np.get_include(), 'fmsne']
)
