# -*- coding: utf-8 -*-
from __future__ import print_function
import pytest

import c3po


def test_warnings():
    newPhysicsDriver = c3po.nameChanger({})(c3po.PhysicsDriver)
    timeAccu = c3po.TimeAccumulator(None)
    timeAccu.setInputDoubleValue("macrodt", 1.)


if __name__ == "__main__":
    test_warnings()
