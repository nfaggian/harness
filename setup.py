"""Setup script for harness package."""

from setuptools import setup, find_packages

setup(
    name="harness",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
