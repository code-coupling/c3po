# -*- coding: utf-8 -*-
from __future__ import print_function

import os

from tests import runMPITest


def test_collaborative():
    runMPITest(2, os.path.join(os.path.dirname(os.path.realpath(__file__)), "main_mpi_collaborative.py"))
    try:
        os.remove("first.log")
    except:
        pass
    try:
        os.remove("second.log")
    except:
        pass
    try:
        os.remove("listingFirst.log")
    except:
        pass
    try:
        os.remove("listingSecond.log")
    except:
        pass
    try:
        os.remove("listingGeneral0.log")
    except:
        pass
    try:
        os.remove("listingGeneral1.log")
    except:
        pass
    try:
        os.remove("listingGeneralMerged.log")
    except:
        pass

