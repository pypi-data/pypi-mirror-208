import setuptools
import re
import os
import sys

setuptools.setup(
    name="scdiffeq_plots",
    version="0.0.1rc0",
    python_requires=">3.9.0",
    author="Michael E. Vinyard - Harvard University - Massachussetts General Hospital - Broad Institute of MIT and Harvard",
    author_email="mvinyard@broadinstitute.org",
    url="https://github.com/mvinyard/sc-neural-diffeqs",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    description="Plotting functions associated wtih analyses from scDiffEq",
    packages=setuptools.find_packages(),
    install_requires=[
        "matplotlib>=3.7.1",
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    license="MIT",
)
