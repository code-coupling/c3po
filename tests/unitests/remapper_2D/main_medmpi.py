# -*- coding: utf-8 -*-
# Contains some simple functions for MED Mesh building
from __future__ import print_function, division
import math
import pytest
import mpi4py.MPI as mpi

import c3po
import c3po.mpi
import c3po.medcouplingCompat as mc


def main_exception_medmpi():
    import tests.medBuilder as medBuilder

    world = mpi.COMM_WORLD
    rank = world.Get_rank()

    if rank == 0:
        field = medBuilder.makeField2DCart([0., 1.], [0., 1., 2.])
    elif rank == 1:
        field = medBuilder.makeField2DCart([1., 2.], [0., 1., 2.])
    else:
        field = medBuilder.makeField3DCart(1., 1., 1., 2, 2, 2)

    remapper = c3po.mpi.MPIRemapper()
    sharedRemapping = c3po.mpi.MPISharedRemapping(remapper)
    sharedRemapping.setRanks([0, 1], [2], world)

    errorMsg = ""
    try:
        sharedRemapping.initialize(field)
    except Exception as exception:
        errorMsg = str(exception)

    refMsg = "MPISharedRemapping : the following error occured during remapper initialization with the field {}:\n".format(field.getName())
    refMsg += "    MPIRemapper : All mesh dimensions should be the same! We found at least two: 2 and 3."

    print(errorMsg)

    assert errorMsg == refMsg


def main_medmpi():
    import tests.medBuilder as medBuilder

    refArray = [1., 4./3., 0.0, 0.0]
    refCoord = [1., 1.]

    world = mpi.COMM_WORLD
    rank = world.Get_rank()

    if rank == 0:
        field = medBuilder.makeField2DCart([0., 1.], [0., 1., 2.])
        array = field.getArray()
        array.setIJ(0, 0, 2.)
    elif rank == 1:
        field = medBuilder.makeField2DCart([1., 2.], [0., 1., 2.])
    else:
        field = medBuilder.makeField2DCart([10., 11., 12.], [10., 11., 12.])
    field.setNature(mc.IntensiveMaximum)

    remapper = c3po.mpi.MPIRemapper(meshAlignment=True, rescaling=1.5, offset=[1., 0., 0.], rotation=math.pi/2., outsideCellsScreening=False) #outsideCellsScreening not available
    remapper.initialize([0, 1], [2], world, field)

    if rank == 0 or rank == 1:
        remapper.sendField(field)
        if rank == 0:
            noodsCoord = field.getMesh().getCoordinatesOfNode(3)
            print(noodsCoord)
            assert len(noodsCoord) == len(refCoord)
            for i in range(len(refCoord)):
                assert pytest.approx(noodsCoord[i], abs=1.E-4) == refCoord[i]
    else:
        resuField = remapper.recvField(field)
        resuValues = resuField.getArray().toNumPyArray().tolist()
        print(resuValues)
        assert len(refArray) == len(resuValues)
        for i in range(len(refArray)):
            assert pytest.approx(resuValues[i], abs=1.E-4) == refArray[i]

    remapper.terminate()


if __name__ == "__main__":
    main_exception_medmpi()
    main_medmpi()
