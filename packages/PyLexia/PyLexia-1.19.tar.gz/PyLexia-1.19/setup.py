import setuptools
from pathlib import Path

setuptools.setup(
    name="PyLexia",
    version=1.19,
    long_description=Path('README.md').read_text(),
    #packages=setuptools.find_packages(exclude=["tests"])
     install_requires=[
        'numpy',
        'cupy-cuda117',
        'matplotlib',
        'NewlineJSON',
        'opencv-python',
        'panda',
        'pandas-read-xml',
        'pdf2image',
        'pytesseract',
        'spacy',
        'tensorflow'
    ],
    package_dir={"":"PyLexia"}
)
