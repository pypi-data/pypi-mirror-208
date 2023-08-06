import sys
import sysconfig

from Cython.Build import cythonize
from setuptools import setup
from setuptools import Extension
import os

__version__="2.1.8"
__package_name__='shared_atomic_enterprise'
__author__="Xiquan Ren"
__author_email__="xiquanren@yandex.com"
__description__="Shared atomicity with multiprocessing or multiple threads"
__url__='http://sharedatomic.top/en/'
__packages__=['shared_atomic']


if sys.platform == 'darwin':
    __version__ += '.MacOSX'
elif sys.platform == 'linux':
    try:
        os.stat("/etc/redhat-release")
        __version__ += '.RHEL'
    except FileNotFoundError as e:
        with open("/etc/issue",'rt') as issue:
            linux_distribution = issue.read()
            if linux_distribution.startswith("Ubuntu"):
                __version__ += "Ubuntu"
            elif linux_distribution.startswith("Welcome to SUSE Linux Enterprise Server"):
                __version__ += "SLES"
else:
    pass



with open("readme.rst") as f:
    readme = f.read()

    # cython_extensions = [Extension("atomic_uint", ["shared_atomic/atomic_uint.py"]),
    #                      Extension("atomic_int", ["shared_atomic/atomic_int.py"]),
    #                      Extension("atomic_boolfloat", ["shared_atomic/atomic_boolfloat.py"]),
    #                      Extension("atomic_bytearray", ["shared_atomic/atomic_bytearray.py"]),
    #                      Extension("atomic_string", ["shared_atomic/atomic_string.py"]),
    #                      Extension("atomic_set", ["shared_atomic/atomic_set.py"]),
    #                      Extension("atomic_list", ["shared_atomic/atomic_list.py"]),
    #                      Extension("atomic_shared_memory", ["shared_atomic/atomic_shared_memory.py"]),
    #                      Extension("win_dll", ["shared_atomic/win_dll.py"]),
    #                      Extension("atomic_activation", ["shared_atomic/atomic_activation.py"]),
    #                      Extension("atomic_async_activation_check", ["shared_atomic/atomic_async_activation_check.py"])
    #                      ]



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
        python_requires=">=3.0",
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
        ext_modules=cythonize(cython_extensions,
                              compiler_directives={'language_level': 3},
                              force=True),
        install_requires=[
            'cppyy >=1.5.0,<=2.3.1',
            'cython==0.29.28',
            'cryptography >= 2.1.4'
        ],
        include_package_data=True,
    )

