import setuptools
from setuptools import setup

setup(
    name="docstruct",
    version="1.0.224",
    description="A package for representing documents as a tree of document, pages, paragraphs, lines, words, and characters",
    long_description=open("docstruct/README.md").read(),
    long_description_content_type="text/markdown",
    author="Moran Nechushtan, Serah Tapia, Shlomo Agishtein",
    author_email="moran.n@trullion.com, serah@trullion.com, shlomo@trullion.com",
    url="https://github.com/smrt-co/docstruct",
    packages=setuptools.find_packages(),
    install_requires=[
        "attrs>=22.0.0",
        "pillow>=8.1.1",
        "numpy==1.23.2",
        "openpyxl==3.1.2",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
