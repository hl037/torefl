#!/usr/bin/env python
import sys

from setuptools import setup, find_packages

__copyright__ = "Copyright 2007, Léo Flaventin Hauchecorne"
__license__ = "GPLv3"

def read_file(name):
    """
    Read file content
    """
    f = open(name)
    try:
        return f.read()
    except IOError:
        print("could not read %r" % name)
        f.close()

LONG_DESC = read_file('README.rst')

EXTRAS = {}

if sys.version_info < (3,):
    EXTRAS['use_2to3'] = True

setup(
    name='torefl',
    version='1.0b1',
    description='Software to manage references',
    long_description=LONG_DESC,
    author='hl037',
    author_email='hl037.prog@gmail.com',
    url='https://github.com/hl037/torefl',
    license='GPL',
    packages=find_packages(),
    test_suite=None,
    include_package_data=True,
    zip_safe=False,
    install_requires = [
			'appdirs>=1.4.3', 
			'bibtexparser>=0.6.2',
			'colorama>=0.3.9',
			'sortedcontainers>=1.5.7',
			],
    extras_require=None,
    entry_points={
			'console_scripts' : [ 'torefl=torefl:main' ]
			},
		keywords=['torefl', 'bibtex', 'bibliography', 'reference', 'pdf', 'management'],
    classifiers=[
			'Development Status :: 4 - Beta',
			'Environment :: Console',
			'Intended Audience :: Developers',
			'Intended Audience :: Education',
			'Intended Audience :: Science/Research',
			'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
			'Natural Language :: English',
			'Operating System :: OS Independent',
			'Programming Language :: Python :: 3',
			'Topic :: Scientific/Engineering',
			'Topic :: Utilities',
			'Topic :: Other/Nonlisted Topic',
			],
    **EXTRAS
)
