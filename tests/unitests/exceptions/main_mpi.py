# -*- coding: utf-8 -*-
from __future__ import print_function
from mpi4py import MPI as mpi

import c3po
import c3po.mpi

def main_mpi():

    world = mpi.COMM_WORLD
    rank = world.Get_rank()

    if rank == 0:
        from tests.unitests.exceptions.MEDBuilder import makeField2DCart
        field = makeField2DCart([0., 1., 2.], [0., 1., 2.])
    else:
        from tests.unitests.exceptions.MEDBuilder import makeField3DCart
        field = makeField3DCart(1., 1., 1., 2, 2, 2)

    remapper = c3po.mpi.MPIRemapper()
    sharedRemapping = c3po.mpi.MPISharedRemapping(remapper)
    sharedRemapping.setRanks([0], [1], world)

    errorMsg = ""
    try:
        sharedRemapping.initialize(field)
    except Exception as exception:
        errorMsg = str(exception)

    refMsg = "MPISharedRemapping : the following error occured during remapper initialization with the field {}:\n".format(field.getName())
    refMsg += "    MPIRemapper : All mesh dimensions should be the same! We found at least two: 2 and 3."

    assert errorMsg == refMsg

if __name__ == "__main__":
    main_mpi()
