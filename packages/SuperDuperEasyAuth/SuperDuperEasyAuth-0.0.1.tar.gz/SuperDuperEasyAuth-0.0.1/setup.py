"""A python module that can easily authenticate remote computers.

See:
https://github.com/noah560/EasyAuth
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")


setup(
    name="SuperDuperEasyAuth",
    version="0.0.1",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/noah560/EasyAuth",
    author="Noah C. C. S.",
    author_email="noahisontheinternet@outlook.com",
    install_requires=["hashlib", "random"]
)
