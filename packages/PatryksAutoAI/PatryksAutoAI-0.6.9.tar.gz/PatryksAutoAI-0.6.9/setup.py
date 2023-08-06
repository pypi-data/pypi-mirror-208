from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

VERSION = '0.6.9'
DESCRIPTION = 'Auto_AI_patryk'
LONG_DESCRIPTION = 'Package contains helping functions for creating ML models'

# Read the requirements from requirements.txt
with open('./KaggleAutoAI/requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="PatryksAutoAI",
    version=VERSION,
    author="patryk",
    author_email="lyczkopatryk1@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=requirements, 
    keywords=['python', 'machine_learning', 'auto'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ]
)
