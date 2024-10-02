# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import glob

import mpi4py.MPI as mpi
import pytest

import c3po
import c3po.mpi

import tests.medBuilder as medBuilder


def checkArray(array, length):
    assert len(array) == length
    for i in range(length):
        assert pytest.approx(array[i], abs=1.E-6) == 4. / length

def main_mpi_clean():
    myRemapper = c3po.Remapper()
    one2two = c3po.SharedRemapping(myRemapper, reverse=True)
    two2one = c3po.SharedRemapping(myRemapper, reverse=False)

    comm = mpi.COMM_WORLD
    rank = comm.Get_rank()

    firstData = c3po.mpi.MPIRemoteProcess(comm, 0)
    secondData = c3po.mpi.MPIRemoteProcess(comm, 1)

    if rank == 0:
        firstData = c3po.LocalDataManager()
        inputField = medBuilder.makeField3DCart(1., 1., 1., 1, 1, 4)
        inputField.getArray().fillWithValue(1.)
        firstData.setInputMEDDoubleField("toto", inputField)
        firstData.setInputMEDDoubleField("tata", inputField)
    if rank == 1:
        secondData = c3po.LocalDataManager()
        secondData.setInputMEDDoubleFieldTemplate("toto", medBuilder.makeField3DCart(1., 1., 1., 1, 1, 8))
        secondData.setInputMEDDoubleFieldTemplate("tata", medBuilder.makeField3DCart(1., 1., 1., 1, 1, 8))

    exchOne2TwoA = c3po.mpi.MPIExchanger(one2two, [(firstData, "toto")], [(secondData, "toto")])
    exchOne2TwoB = c3po.mpi.MPIExchanger(one2two, [(firstData, "tata")], [(secondData, "tata")], exchangeWithFiles=True)
    exchOne2Two = c3po.CollaborativeExchanger([exchOne2TwoA, exchOne2TwoB])

    try:
        exchOne2Two.exchange()
        if rank == 1:
            checkArray(secondData.getOutputMEDDoubleField("toto").getArray(), 8)
            checkArray(secondData.getOutputMEDDoubleField("tata").getArray(), 8)
            print("ok 1")

        if rank == 1:
            secondData.setInputMEDDoubleFieldTemplate("toto", medBuilder.makeField3DCart(1., 1., 1., 1, 1, 12))
            secondData.setInputMEDDoubleFieldTemplate("tata", medBuilder.makeField3DCart(1., 1., 1., 1, 1, 12))

        exchOne2Two.clean()
        exchOne2Two.exchange()

        if rank == 1:
            checkArray(secondData.getOutputMEDDoubleField("toto").getArray(), 12)
            checkArray(secondData.getOutputMEDDoubleField("tata").getArray(), 12)
            print("ok 2")
    except:
        raise
    finally:
        if rank == 1:
            medFiles = glob.glob("*.med")
            for medFile in medFiles:
                os.remove(medFile)

if __name__ == "__main__":
    main_mpi_clean()
