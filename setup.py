from setuptools import setup, find_packages

setup(
    name         = 'configurati',
    version      = '0.2.3',
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
