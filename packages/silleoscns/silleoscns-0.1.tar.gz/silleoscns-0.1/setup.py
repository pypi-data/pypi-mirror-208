from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))
setup(
    name='silleoscns',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # http://packaging.python.org/en/latest/tutorial.html#version
    version='0.1',

    description='Walker Comm Simulation',
    long_description='Large, low Earth orbit, broadband satellite networks, have recently become a growing area of research as a number of implementations are currently being constructed by commercial businesses. Unlike current systems, these new constellations are comprised of 100s to 1,000s of interconnected satellites. This Thesis seeks to create and demonstrate a tool for generating and simulating such networks.',  #this is the

    # The project's main homepage.

    # Author details
    author='Ben Kempton',

    # Choose your license
    license='GNU General Public License Version 3, [1] B. S. Kempton, "A Simulation Tool to Study Routing in Large Broadband Satellite Networks." Christopher Newport University, 2020.',

    # See https://PyPI.python.org/PyPI?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6',
    ],

    # What does your project relate to?
    keywords='Walker Comm Sim',

    packages=["silleoscns"],

)