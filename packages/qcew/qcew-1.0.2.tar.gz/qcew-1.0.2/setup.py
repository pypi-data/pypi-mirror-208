from setuptools import setup
from pathlib import Path

VERSION = "1.0.2"
DESCRIPTION = "A package for retrieving Quarterly Census of Employment and Wages (QCEW) data."

setup(
    name="qcew",
    version=VERSION,
    description=DESCRIPTION,
    author="Trent Thompson",
    author_email="808trent@gmail.com",
    url="https://github.com/TrentLThompson/qcew",
    long_description=(Path(__file__).parent/"README.md").read_text(),
    long_description_content_type='text/markdown',
    keywords=["QCEW", "BLS", "employment", "wages", "statistics"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">= 3.8",
)