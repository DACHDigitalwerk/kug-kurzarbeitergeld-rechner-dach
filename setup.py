# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="kug-dach",
    version="1.0.0",
    description="Kurzarbeitergeld-Rechner 2026 fuer Deutschland nach SGB III und KUG-Verordnung sowie AT KUA und CH KAE",
    author="DACH Digitalwerk",
    author_email="dach.digitalwerk@gmail.com",
    packages=find_packages(),
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "dach-kug = kug_dach.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
