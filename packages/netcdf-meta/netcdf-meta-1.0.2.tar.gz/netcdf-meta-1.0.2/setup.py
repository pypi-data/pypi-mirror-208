
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = [line.strip() for line in f.readlines()]

setup(
    name="netcdf-meta",
    version="1.0.2",
    packages=find_packages(),
    py_modules=['netcdf_meta'],
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'netcdf_meta = netcdf_meta:main',
        ],
    },
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',)
