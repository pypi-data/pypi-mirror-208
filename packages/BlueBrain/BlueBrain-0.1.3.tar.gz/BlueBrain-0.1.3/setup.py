from setuptools import setup, find_packages
import codecs
import os


VERSION = '0.1.3'
DESCRIPTION = 'Special AI/ML library for autonomous vehicles and underwater systems'
LONG_DESCRIPTION = 'A package that allows to build AI/ML models for manage self-driving cars' \
                   ' and images processing tools.'

# Setting up
setup(
    name="BlueBrain",
    version=VERSION,
    author="Uranyum (Mustafa Gülsoy)",
    author_email="<mustafagulsoy05@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['pickleshare==0.7.5'],
    keywords=['python', 'AI', 'ML', 'BlueBrain', 'Self-Drive'],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)