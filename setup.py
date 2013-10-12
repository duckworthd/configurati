from setuptools import setup, find_packages

import configurati

setup(
    name         = 'configurati',
    version      =  configurati.__version__,
    author       = 'Daniel Duckworth',
    author_email = 'duckworthd@gmail.com',
    description  = 'Configuration files for Python',
    license      = 'BSD',
    keywords     = 'config configuration',
    url          = 'http://github.com/duckworthd/configurati',
    packages     = find_packages(),
    classifiers  = [
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Operating System :: OS Independent',
      'Programming Language :: Python',
      'Programming Language :: Python :: Implementation :: CPython',
      'Topic :: Software Development :: Libraries',
    ],
    install_requires = [
      'PyYAML>=3.10',
    ],
    tests_require    = [
      'nose',
    ]
)
