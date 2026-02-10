# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Installation script of the package."""

import pathlib
from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
def get_long_description():
    """Extract README content"""
    return (here / "sources" / "README.md").read_text(encoding="utf-8")

def get_version():
    """Extract the package's version number from the ``VERSION`` file."""
    with open(here / "sources" / "c3po" / "VERSION") as file:
        return file.read().strip()


setup(
    name="c3po",
    version=get_version(),
    author="CEA",
    author_email="cyril.patricot@cea.fr",
    maintainer="Cyril Patricot",
    maintainer_email="cyril.patricot@cea.fr",
    description="Collaborative Code Coupling PlatfOrm",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/code-coupling/c3po",
    packages=find_packages(where="sources"),
    package_data={
        "c3po": [
            "VERSION",
        ],
    },
    package_dir={"": "sources"},
    install_requires=[
        "numpy>=1.9",
        "icoco>=2.0.3",
    ],
    extras_require={
        "pytest": ["pytest", "pytest-cov", "pytest-html"],
        "doc": ["graphviz", "sphinx>=8.2.0", "sphinx-rtd-theme"],
        "mpi": ["mpi4py>=1.3"],
    },
    python_requires=">=3.7",
    licence="3-Clause BSD"
)
