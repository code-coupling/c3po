# -*- coding: utf-8 -*-
from __future__ import print_function

import os

from tests import runMPITest


def test_mpi_warnings():
    runMPITest(1, os.path.join(os.path.dirname(os.path.realpath(__file__)), "main_mpi_warnings.py"))
