# -*- coding: utf-8 -*-
from __future__ import print_function, division
import mpi4py.MPI as mpi

from NeutroDriver import NeutroDriver
import C3PO
import C3POMPI


class Thermo2Neutro(C3PO.SharedRemapping):
    def __init__(self, remapper):
        C3PO.SharedRemapping.__init__(self, remapper, reverse=False)


class Neutro2Thermo(C3PO.SharedRemapping):
    def __init__(self, remapper):
        C3PO.SharedRemapping.__init__(self, remapper, reverse=True)


comm = mpi.COMM_WORLD

myNeutroDriver = NeutroDriver()
myThermoDriver = C3POMPI.MPIRemoteProcess(comm, 1)
MasterProcess = C3POMPI.MPIRemoteProcess(comm, 0)
DataCoupler = C3POMPI.MPIRemoteProcess(comm, 1)

basicTransformer = C3PO.Remapper()
Thermo2DataTransformer = C3PO.DirectMatching()
Data2NeutroTransformer = Thermo2Neutro(basicTransformer)
Neutro2ThermoTransformer = Neutro2Thermo(basicTransformer)

ExchangerNeutro2Thermo = C3POMPI.MPIExchanger(Neutro2ThermoTransformer, [(myNeutroDriver, "Temperatures")], [(myThermoDriver, "Temperatures")])
ExchangerThermo2Data = C3POMPI.MPIExchanger(Thermo2DataTransformer, [(myThermoDriver, "Densities")], [(DataCoupler, "Densities")])
ExchangerData2Neutro = C3POMPI.MPIExchanger(Data2NeutroTransformer, [(DataCoupler, "Densities")], [(myNeutroDriver, "Densities")])

exchangers = [ExchangerNeutro2Thermo, ExchangerThermo2Data, ExchangerData2Neutro]

Worker = C3POMPI.MPIWorker([myNeutroDriver, myThermoDriver], exchangers, [DataCoupler], MasterProcess)

Worker.listen()
