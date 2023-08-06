import setuptools
from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text('utf-8')

setup(
    name='CreaTeBME',
    version='1.0.1',
    author='Jonathan Matarazzi',
    author_email='git@jonathanm.nl',
    description='Python Package for interfacing the bluetooth IMU module for CreaTe M8 BME.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/CreaTe-M8-BME/CreaTeBME',
    project_urls={
        'Bug Tracker': 'https://github.com/CreaTe-M8-BME/CreaTeBME/issues',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent'
    ],
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    python_requires='>=3.7',
    install_requires=[
        'bleak >= 0.19.5',
    ]
)
