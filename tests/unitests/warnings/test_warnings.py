# -*- coding: utf-8 -*-
from __future__ import print_function
import pytest

import c3po


def test_warnings():
    newPhysicsDriver = c3po.nameChanger({})(c3po.PhysicsDriver)
    timeAccu = c3po.TimeAccumulator(None)
    timeAccu.setInputDoubleValue("macrodt", 1.)
    c3po.SharedRemappingMulti1D3D(c3po.Multi1D3DRemapper([0., 1.], [0., 1.], [0], [1.]))


if __name__ == "__main__":
    test_warnings()
