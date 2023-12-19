# -*- coding: utf-8 -*-
from __future__ import print_function
import pytest

import c3po.medcouplingCompat as mc

import c3po

def test_exceptions():
    from tests.unitests.exceptions.MEDBuilder import makeField2DCart, makeField3DCart
    field1 = makeField2DCart([0., 1., 2.], [0., 1., 2.])
    field2 = makeField3DCart(1., 1., 1., 2, 2, 2)

    remapper = c3po.Remapper()
    sharedRemapping = c3po.SharedRemapping(remapper)

    errorMsg = ""
    try:
        sharedRemapping.initialize(field1, field2)
    except Exception as exception:
        errorMsg = str(exception)

    refMsg = "SharedRemapping : the following error occured during remapper initialization with the fields 2DField and 3DField:"
    refMsg += "\n    Remapper : the dimension of source and target meshes are not the same (2DMesh : 2 and 3DMesh : 3 respectively)."

    assert errorMsg == refMsg

if __name__ == "__main__":
    test_exceptions()
