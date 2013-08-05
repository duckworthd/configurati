from setuptools import setup, find_packages

setup(
    name         = 'configurati',
    version      = '0.1.1',
    author       = 'Daniel Duckworth',
    author_email = 'pykalman@gmail.com',
    description  = 'Configuration files for Python',
    license      = 'BSD',
    keywords     = 'config configuration',
    url          = 'github.com/duckworthd/configurati',
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
    install_requires = [],
    tests_require    = [
      'nose',
    ]
)
