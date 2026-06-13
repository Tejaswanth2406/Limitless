"""Limitless package setup."""
from setuptools import setup, find_packages

setup(
    name="limitless",
    version="0.1.0",
    description="Temporal Reality Operating System — a framework where time is the fundamental substrate",
    author="Limitless Research",
    python_requires=">=3.9",
    packages=find_packages(exclude=["tests*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
