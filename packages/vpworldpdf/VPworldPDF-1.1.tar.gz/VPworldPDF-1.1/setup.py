import setuptools
from pathlib import Path

setuptools.setup(
    name="VPworldPDF",
    version="1.1",
    author="VPworld",
    description="A Python package for converting PDF files to TXT files",
    long_description=Path("README.md").read_text(),
    packages=setuptools.find_packages(exclude=["tests", "data"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
