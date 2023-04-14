# -*- coding: utf-8 -*-
from __future__ import print_function

import os

from tests import runMPITest


def test_masterWorkers():
    runMPITest(3, os.path.join(os.path.dirname(os.path.realpath(__file__)), "main_masterWorkers.py"))
