# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Installation script of the package."""

import os
from setuptools import find_packages, setup


def get_version():
    """Extract the package's version number from the ``VERSION`` file."""
#    filename = os.path.join(os.path.dirname(__file__), "sources", "c3po", "VERSION")
    filename = os.path.join(os.path.dirname(__file__), "c3po", "VERSION")
    with open(filename) as file:
        return file.read().strip()


def check_dependencies(requirements):
    """Check if the dependencies of the package are available in the current
    environment and print a warning message if not.

    The ``setup`` functions can do the same thing using its ``install_requires``
    parameter. But it interupts the installation process if any dependency is
    missing and cannot be installed. As C3PO is mainly used in on-the-fly
    defined environment, we just want to warn the user without preventing him
    from installing the package.

    Parameters
    ----------
    requirements = list of str

    Returns
    -------
    list of str
        List of the requirements available in the current environment.
    """
    from pkg_resources import WorkingSet, Requirement, VersionConflict
    available_requirements = []
    working_set = WorkingSet()
    for requirement in requirements:
        print("Searching for {}".format(requirement))
        try:
            distribution = working_set.find(Requirement(requirement))
        except VersionConflict:
            distribution = None
        if distribution is None:
            print("warning: Could not find suitable distribution for {}".format(
                requirement))
        else:
            print("Best match: {}".format(distribution))
            available_requirements.append(requirement)
    return available_requirements


setup(
    name="c3po",
    version=get_version(),
    author="CEA",
    author_email="cyril.patricot@cea.fr",
    maintainer="Cyril Patricot",
    maintainer_email="cyril.patricot@cea.fr",
    description="Collaborative Code Coupling PlatfOrm",
    url="https://sourceforge.net/projects/cea-c3po/",
    packages=find_packages(),
    package_data={
        "c3po": [
            "VERSION",
        ],
    },
    #    package_dir={"": "sources"},
    install_requires=check_dependencies([
        "numpy>=1.9",
        "mpi4py>=1.3",
    ]),
    extras_require={
        "pytest": ["pytest", "pytest-cov", "pytest-html"],
    },
    python_requires=">=2.7, !=3.0.*, !=3.1.*",
    licence="3-Clause BSD"
)
