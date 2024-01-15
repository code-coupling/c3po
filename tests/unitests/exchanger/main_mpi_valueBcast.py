# -*- coding: utf-8 -*-
from __future__ import print_function
import mpi4py.MPI as mpi

import c3po
import c3po.mpi


def makeBroadcast(ranks1, ranks2, op, input, result):
    world = mpi.COMM_WORLD
    rank = world.Get_rank()

    valueBcast = c3po.mpi.MPIValueBcast(reduceOp=op)

    dataManager1 = c3po.mpi.MPIRemoteProcesses(world, ranks1)
    dataManager2 = c3po.mpi.MPIRemoteProcesses(world, ranks2)

    comm1 = world.Split(1 if rank in ranks1 else mpi.UNDEFINED)
    comm2 = world.Split(1 if rank in ranks2 else mpi.UNDEFINED)
    if rank in ranks1:
        dataManager1 = c3po.mpi.MPICollectiveDataManager(comm1)
        dataManager1.setInputDoubleValue("a", input)
    if rank in ranks2:
        dataManager2 = c3po.mpi.MPICollectiveDataManager(comm2)

    exchanger = c3po.mpi.MPIExchanger(valueBcast, [], [], [(dataManager1, "a")] ,[(dataManager2, "b")], mpiComm=world)
    exchanger.exchange()

    if rank in ranks2:
        print(rank, dataManager2.getOutputDoubleValue("b"))
        assert dataManager2.getOutputDoubleValue("b") == result


def makeError():
    valueBcast = c3po.mpi.MPIValueBcast(reduceOp=None)

    try:
        valueBcast([0], [0], [0])
    except ValueError as error:
        errorMsg = str(error)

    refMsg = "MPIValueBcast: we cannot deal with fields."
    print(errorMsg)
    assert errorMsg == refMsg


def main_mpi_valueBcast():
    makeBroadcast([0, 1], [2, 3], mpi.SUM, 1., 2.)
    makeBroadcast([0, 1], [1, 2, 3], mpi.SUM, 1., 2.)
    makeBroadcast([0, 1], [3], mpi.SUM, 1., 2.)
    makeBroadcast([0, 1, 2, 3], [0, 1, 2, 3], mpi.SUM, 1., 4.)

    makeBroadcast([0, 1], [2, 3], None, 1., 1.)

    makeBroadcast([0, 1], [2, 3], None, "toto", "toto")
    makeBroadcast([0, 1], [2, 3], mpi.SUM, "tu", "tutu")

    makeError()

if __name__ == "__main__":
    main_mpi_valueBcast()
