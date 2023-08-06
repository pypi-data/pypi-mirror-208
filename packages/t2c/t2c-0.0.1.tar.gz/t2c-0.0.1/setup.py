from setuptools import setup, find_packages
from codecs import open
from os import path
import sys
import os

# Get the long description from the relevant file
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='t2c',
    version='0.0.1',

    description='A Python Library That Converts Human Readable Text To Cron Expression.',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/iguangyu/text2cron',

    # Author details
    author='iguangyu',
    author_email='oofheaven7@gmail.com',

    license='MIT',

    classifiers=[

        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
    ],

    # What does your project relate to?
    keywords='text cron text langchain gpt npl',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    # packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    packages=find_packages(),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['pendulum', 'cn2an'],

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
        't2c': ['*.py'],
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    # entry_po
    # scripts=['hide_code/hide_code.py'],
    # cmdclass={'install': install},
)