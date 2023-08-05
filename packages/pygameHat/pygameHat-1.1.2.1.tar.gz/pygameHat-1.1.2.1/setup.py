from setuptools import setup, find_packages
import codecs
import os

VERSION = '1.1.2.1'
DESCRIPTION = 'Pygame game-making engine'

# Setting up
setup(
    name="pygameHat",
    version=VERSION,
    author="Wojciech Błajda",
    #author_email="None",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=["pygame", "pyinstaller"],
    keywords=['python', 'engine', 'pygame', 'game', 'maker'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
