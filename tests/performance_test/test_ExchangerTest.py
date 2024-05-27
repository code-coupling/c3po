# -*- coding: utf-8 -*-
from __future__ import print_function, division

import os

from tests import runMPITest


def test_ExchangerTest():
    print("Debut du test")
    runMPITest(2, os.path.join(os.path.dirname(os.path.realpath(__file__)), "ExchangerTest.py"))

