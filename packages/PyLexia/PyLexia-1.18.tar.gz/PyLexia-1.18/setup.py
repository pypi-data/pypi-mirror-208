import setuptools
from pathlib import Path

setuptools.setup(
    name="PyLexia",
    version=1.18,
    long_description=Path('README.md').read_text(),
    #packages=setuptools.find_packages(exclude=["tests"])
    package_dir={"":"PyLexia"}
)
