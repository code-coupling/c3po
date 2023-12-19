# -*- coding: utf-8 -*-
from __future__ import print_function, division

import os

from tests import runMPITest


def test_mpi():
    runMPITest(2, os.path.join(os.path.dirname(os.path.realpath(__file__)), "main_mpi.py"))
