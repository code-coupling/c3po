# -*- coding: utf-8 -*-
# Contains some simple functions for MED Mesh building
from __future__ import print_function, division
import math
import pytest

import c3po
import c3po.medcouplingCompat as mc


def test_exception():
    import tests.medBuilder as medBuilder
    field1 = medBuilder.makeField2DCart([0., 1., 2.], [0., 1., 2.])
    field2 = medBuilder.makeField3DCart(1., 1., 1., 2, 2, 2)

    remapper = c3po.Remapper()
    sharedRemapping = c3po.SharedRemapping(remapper)

    errorMsg = ""
    try:
        sharedRemapping.initialize(field1, field2)
    except Exception as exception:
        errorMsg = str(exception)

    refMsg = "SharedRemapping : the following error occured during remapper initialization with the fields 2DField and 3DField:"
    refMsg += "\n    Remapper : the dimension of source and target meshes are not the same (2DMesh : 2 and 3DMesh : 3 respectively)."

    print(errorMsg)

    assert errorMsg == refMsg


def test_sequential():
    import tests.medBuilder as medBuilder

    refArray = [1., 4./3., 0.0, 0.0]
    refCoord = [1., 1.]

    field1 = medBuilder.makeField2DCart([0., 1., 2.], [0., 1., 2.])
    field2 = medBuilder.makeField2DCart([10., 11., 12.], [10., 11., 12.])
    field1.setNature(mc.IntensiveMaximum)
    field2.setNature(mc.IntensiveMaximum)

    array1 = field1.getArray()
    array1.setIJ(0, 0, 2.)

    remapper = c3po.Remapper(meshAlignment=True, rescaling=1.5, offset=[0.99999, 0., 0.], rotation=math.pi/2., outsideCellsScreening=True)
    remapper.initialize(field1.getMesh(), field2.getMesh())

    resuField = remapper.directRemap(field1, 0.)
    resuValues = resuField.getArray().toNumPyArray().tolist()

    print(resuValues)

    noodsCoord = field1.getMesh().getCoordinatesOfNode(4)
    print(noodsCoord)

    assert len(refArray) == len(resuValues)
    for i in range(len(refArray)):
        assert pytest.approx(resuValues[i], abs=1.E-4) == refArray[i]

    assert len(noodsCoord) == len(refCoord)
    for i in range(len(refCoord)):
        assert pytest.approx(noodsCoord[i], abs=1.E-4) == refCoord[i]


if __name__ == "__main__":
    test_exception()
    test_sequential()
