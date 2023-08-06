import os
from setuptools import setup

# Meta information
from tempcf._version import __version__
dirname = os.path.dirname(__file__)

setup(
    # Basic info
    name='tempcf',
    version=__version__,
    author='Nick Brown',
    author_email='',
    url='https://gitlab.com/permafrostnet/permafrost-tempcf',
    description='A toolbox for flagging and cleaning ground temperature data',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 4 - Beta',
    ],

    # Packages and depencies
    packages=['tempcf'],
    install_requires=[
        'numpy',  # ==1.19.3',
        'matplotlib',  # ==3.2.2',
        'tsp>=1.5.0',
        'pfit',
        'pandas',
        'pillow',
        'scipy',
    ],
    extras_require={},

    # Data files
    package_data={
        'python_boilerplate': [
            'templates/*.*',
            'templates/license/*.*',
            'templates/docs/*.*',
            'templates/package/*.*'
        ],
    },

    # Scripts
    entry_points={
        'console_scripts': [
            'tempcf = tempcf.main:main']
    },

)
