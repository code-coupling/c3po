# -*- coding: utf-8 -*-
from __future__ import print_function, division

import time
import sys
import os
import pytest
import tests.medBuilder as medBuilder
import medcoupling as mc

def main_mpi_collaborative():
    from mpi4py import MPI

    import c3po
    import c3po.mpi

    def makeMesh3DCart(x_coord, y_coord, z_coord=None):
        arrayX = mc.DataArrayDouble(x_coord)
        arrayX.setInfoOnComponent(0, "X [m]")
        arrayY = mc.DataArrayDouble(y_coord)
        arrayY.setInfoOnComponent(0, "Y [m]")
        arrayZ = mc.DataArrayDouble(z_coord) if z_coord else None
        cMesh = mc.MEDCouplingCMesh("CartesianMesh")
        if z_coord:
            cMesh.setCoords(arrayX, arrayY, arrayZ)
        else:
            cMesh.setCoords(arrayX, arrayY)
        return cMesh.buildUnstructured()

    def makeField(nature, mesh, nbComponents):
        field = mc.MEDCouplingFieldDouble.New(mc.ON_CELLS)
        field.setMesh(mesh)
        nbCells = mesh.getNumberOfCells()
        values = [1.] * nbCells * nbComponents
        array = mc.DataArrayDouble.New()
        array.setValues(values, nbCells, nbComponents)

        for i in range(nbComponents):
            array.setInfoOnComponent(i, "Comp" + str(i))
        field.setArray(array)
        field.setName("cartesianField")
        field.setNature(nature)
        return field

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    Driver2 = c3po.mpi.MPIRemoteProcess(comm, 0)
    Driver1 = c3po.mpi.MPIRemoteProcess(comm, 1)

    if rank == 0:
        Driver2 = c3po.LocalDataManager()

    elif rank == 1:
        Driver1 = c3po.LocalDataManager()
        mesh = makeMesh3DCart(list(range(1000)), list(range(100)), list(range(100)))
        field = makeField(mc.IntensiveMaximum, mesh, 1)
        Driver1.setInputMEDDoubleField( "cartesianField" , field)

    Driver12Driver2Transformer = c3po.DirectMatching()
    DataCoupler = c3po.mpi.MPICollectiveDataManager(MPI.COMM_WORLD)
    ExchangerDriver12Driver2 = c3po.mpi.MPIExchanger(Driver12Driver2Transformer, [(Driver1, "cartesianField")], [(Driver2, "cartesianField")])
    for i in range(1000):
        ExchangerDriver12Driver2.exchange()

    if rank == 0:
        print(Driver2.getOutputMEDDoubleField("cartesianField"))
        field2= Driver2.getOutputMEDDoubleField("cartesianField")
        print(Driver2.norm2())

        mc.WriteField("MEDSimpleExchange.med", field2, True)

    
if __name__ == "__main__":
    tps1 = time.clock()
    main_mpi_collaborative()
    tps2 = time.clock()
    print(tps2 - tps1)

