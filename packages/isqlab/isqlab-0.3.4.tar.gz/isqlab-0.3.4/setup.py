# This code is part of isQ.
# (C) Copyright ArcLight Quantum 2023.
# This code is licensed under the MIT License.

from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as readme:
    long_description = readme.read()

requirements = [
    # "isqopen",
    # "pyscf",
    # "openfermion",
    # "openfermionpyscf",
]

setup(
    name="isqlab",
    version="0.3.4",
    description="application modules for isq",
    platforms="python 3.8+",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Yusheng Yang",
    author_email="yangys@arclightquantum.com",
    packages=find_packages(where="."),
    package_data={"": ["*.txt"]},
    install_requires=requirements,
)
