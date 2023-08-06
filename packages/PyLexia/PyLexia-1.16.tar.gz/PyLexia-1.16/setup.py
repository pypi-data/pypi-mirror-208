import setuptools
from pathlib import Path

setuptools.setup(
    name="PyLexia",
    version=1.16,
    long_description=Path('README.md').read_text(),
    packages=setuptools.find_packages(exclude=["tests"],include=["src"])
)
