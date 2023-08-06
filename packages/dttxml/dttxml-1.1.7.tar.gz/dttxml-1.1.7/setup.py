import os
import setup_helper
from setuptools import setup

with open(os.path.join('dttxml', 'version.py')) as f:
    exec(f.read())
cmdclass = setup_helper.version_checker(version, 'dttxml')


setup(
    name='dttxml',
    version=version,
    url='https://git.ligo.org/cds/dttxml',
    author='Lee McCuller',
    author_email='Lee.McCuller@ligo.org',
    description=(
        'Extract data from LIGO Diagnostics test tools XML format. Formerly dtt2hdf.'
    ),
    license='Apache v2',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    packages=[
        'dttxml',
    ],
    install_requires=[
        'numpy',
        'h5py',
        'declarative>=1.3.0',
    ],
    tests_require=[
        'pytest','matplotlib'
    ],
    entry_points={
        'console_scripts': [
            'dtt2hdf=dttxml.dtt2hdf:main',
        ],
    },
    cmdclass=cmdclass,
    zip_safe=True,
    keywords='LIGO dtt diagnostics file-reader',
)
