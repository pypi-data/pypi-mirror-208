import sys
import sysconfig

from Cython.Build import cythonize
from setuptools import setup
from setuptools import Extension
import os

__version__="2.1.13"
__package_name__='shared_atomic_enterprise'
__author__="Xiquan Ren"
__author_email__="xiquanren@yandex.com"
__description__="Shared atomicity with multiprocessing or multiple threads"
__url__='http://sharedatomic.top/en/'
__packages__=['shared_atomic']


if sys.platform == 'darwin':
    __version__ = '1!' + __version__
elif sys.platform == 'linux':
    try:
        os.stat("/etc/redhat-release")
        __version__ = '2!' + __version__
    except FileNotFoundError as e:
        with open("/etc/issue",'rt') as issue:
            linux_distribution = issue.read()
            if linux_distribution.startswith("Ubuntu"):
                __version__ = "3!" + __version__
            elif linux_distribution.find("Welcome to SUSE Linux Enterprise Server") != -1:
                __version__ = "4!" + __version__
else:
    pass



with open("readme.rst") as f:
    readme = f.read()



if sys.platform in('darwin', 'linux'):

    setup(
        name=__package_name__,
        version=__version__,
        author=__author__,
        author_email=__author_email__,
        description=__description__,
        url=__url__,
        long_description=readme,
        packages=__packages__,
        python_requires=">=3.6",
        #ext_modules=cythonize(cython_extensions,
        #                      compiler_directives={'language_level': 3,
        #                                           'initializedcheck': False,
        #                                           'embedsignature': True
        ##                                           },
        #                      nthreads=4,
        #                      force=True,
        #                      annotate=False),
        #cffi_modules=["shared_atomic/atomic_setup.py:ffi",
        #              "shared_atomic/atomic_decryption.py:ffi"],
        install_requires=[
            'cffi>=1.0',
            'urwid==2.1.2',
        ],
        include_package_data=True,
        zip_safe=False
    )
elif sys.platform == 'win32':

    if sysconfig.get_config_var('implementation') == 'PyPy':
        raise NotImplementedError('PyPy is not supported on Windows Platform!')
    setup(
        name=__package_name__,
        version=__version__,
        author=__author__,
        author_email=__author_email__,
        description=__description__,
        url=__url__,
        long_description=readme,
        packages=__packages__,
        python_requires=">=3.0",
        install_requires=[
            'cppyy >=1.5.0,<=2.3.1',
            'urwid==2.1.2',
        ],
        include_package_data=True,
        zip_safe=False
    )

