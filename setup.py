from glob import glob
from os.path import basename, splitext
from setuptools import find_packages, setup

setup(
    name='visualize',
    version='0.1',
    packages=find_packages(where='include'),
    package_dir={'': 'include'},
    py_modules=[splitext(basename(path))[0] for path in glob('include/*.py')],
)

setup(
    name='clustering',
    version='0.1',
    packages=find_packages(where='include'),
    package_dir={'': 'include'},
    py_modules=[splitext(basename(path))[0] for path in glob('include/*.py')],
)

setup(
    name='filenameparser',
    version='0.1',
    packages=find_packages(where='include'),
    package_dir={'': 'include'},
    py_modules=[splitext(basename(path))[0] for path in glob('include/*.py')],
)