# -*- coding: utf-8 -*-
from __future__ import print_function, division

import os

from tests import runMPITest


def test_collaborative():
    runMPITest(2, os.path.join(os.path.dirname(os.path.realpath(__file__)), "main_mpi_collaborative.py"))
    try:
        os.remove("ExchangeField_rank0_0.med")
    except:
        pass
    try:
        os.remove("ExchangeField_rank1_0.med")
    except:
        pass