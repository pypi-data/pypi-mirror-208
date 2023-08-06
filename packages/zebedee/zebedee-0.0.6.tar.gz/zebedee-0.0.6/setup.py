from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.6'
DESCRIPTION = 'Move Money at the Speed of the Internet '
LONG_DESCRIPTION = 'A package that allows for faster integration of the ZEBEDEE API.'

# Setting up
setup(
    name="zebedee",
    version=VERSION,
    author="zantoshi (Santos Hernandez)",
    author_email="<santosdhernandez@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=["zebedee"],
    install_requires=['certifi', 'charset-normalizer', 'idna', 'requests', 'urllib3'],
    keywords=['python', 'payments', 'bitcoin', 'lightning network', 'django', 'lightning'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)