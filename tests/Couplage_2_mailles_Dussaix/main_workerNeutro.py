# -*- coding: utf-8 -*-
from __future__ import print_function, division
import mpi4py.MPI as mpi

from NeutroDriver import NeutroDriver
import c3po
import c3po.mpi


class Thermo2Neutro(c3po.SharedRemapping):
    def __init__(self, remapper):
        c3po.SharedRemapping.__init__(self, remapper, reverse=False)


class Neutro2Thermo(c3po.SharedRemapping):
    def __init__(self, remapper):
        c3po.SharedRemapping.__init__(self, remapper, reverse=True)


comm = mpi.COMM_WORLD

myNeutroDriver = NeutroDriver()
myThermoDriver = c3po.mpi.MPIRemoteProcess(comm, 1)
MasterProcess = c3po.mpi.MPIRemoteProcess(comm, 0)
DataCoupler = c3po.mpi.MPIRemoteProcess(comm, 1)

basicTransformer = c3po.Remapper()
Thermo2DataTransformer = c3po.DirectMatching()
Data2NeutroTransformer = Thermo2Neutro(basicTransformer)
Neutro2ThermoTransformer = Neutro2Thermo(basicTransformer)

ExchangerNeutro2Thermo = c3po.mpi.MPIExchanger(Neutro2ThermoTransformer, [(myNeutroDriver, "Temperatures")], [(myThermoDriver, "Temperatures")])
ExchangerThermo2Data = c3po.mpi.MPIExchanger(Thermo2DataTransformer, [(myThermoDriver, "Densities")], [(DataCoupler, "Densities")])
ExchangerData2Neutro = c3po.mpi.MPIExchanger(Data2NeutroTransformer, [(DataCoupler, "Densities")], [(myNeutroDriver, "Densities")])

exchangers = [ExchangerNeutro2Thermo, ExchangerThermo2Data, ExchangerData2Neutro]

Worker = c3po.mpi.MPIWorker([myNeutroDriver, myThermoDriver], exchangers, [DataCoupler], MasterProcess)

Worker.listen()
