# -*- coding: utf-8 -*-
from __future__ import print_function, division
from mpi4py import MPI

import MEDCoupling
import MEDLoader

from NeutroDriver import NeutroDriver
from ThermoDriver import ThermoDriver
import C3PO
import C3POMPI


class Thermo2Neutro(C3PO.SharedRemapping):
    def __init__(self, remapper):
        C3PO.SharedRemapping.__init__(self, remapper, reverse=False)


class Neutro2Thermo(C3PO.SharedRemapping):
    def __init__(self, remapper):
        C3PO.SharedRemapping.__init__(self, remapper, reverse=True)


class OneIterationCoupler(C3POMPI.MPICoupler):
    def __init__(self, physics, exchangers, dataManagers=[]):
        C3POMPI.MPICoupler.__init__(self, physics, exchangers, dataManagers)

    def solveTimeStep(self):
        self.physicsDrivers_["neutro"].solve()
        self.exchangers_[0].exchange()
        self.physicsDrivers_["thermo"].solve()
        return self.getSolveStatus()


comm = MPI.COMM_WORLD
rank = comm.Get_rank()

myThermoDriver = C3POMPI.MPIRemoteProcess(comm, 0)
DataCoupler = C3POMPI.MPICollectiveDataManager(comm)
myNeutroDriver = C3POMPI.MPIRemoteProcess(comm, 1)

if rank == 0:
    myThermoDriver = ThermoDriver()

elif rank == 1:
    myNeutroDriver = NeutroDriver()

myThermoDriver.init()
myThermoDriver.setValue("Vv_Vl", 10.)

myNeutroDriver.init()
myNeutroDriver.setValue("meanT", 1000.)

basicTransformer = C3PO.Remapper()
Thermo2DataTransformer = C3PO.DirectMatching()
Data2NeutroTransformer = Thermo2Neutro(basicTransformer)
Neutro2ThermoTransformer = Neutro2Thermo(basicTransformer)

DataCoupler = C3POMPI.MPICollectiveDataManager(MPI.COMM_WORLD)
ExchangerNeutro2Thermo = C3POMPI.MPIExchanger(Neutro2ThermoTransformer, [(myNeutroDriver, "Temperatures")], [(myThermoDriver, "Temperatures")])
ExchangerThermo2Data = C3POMPI.MPIExchanger(Thermo2DataTransformer, [(myThermoDriver, "Densities")], [(DataCoupler, "Densities")])
ExchangerData2Neutro = C3POMPI.MPIExchanger(Data2NeutroTransformer, [(DataCoupler, "Densities")], [(myNeutroDriver, "Densities")])

OneIteration = OneIterationCoupler({"neutro": myNeutroDriver, "thermo": myThermoDriver}, [ExchangerNeutro2Thermo])

mycoupler = C3PO.FixedPointCoupler([OneIteration], [ExchangerThermo2Data, ExchangerData2Neutro], [DataCoupler])
mycoupler.setDampingFactor(0.125)
mycoupler.setConvergenceParameters(1E-5, 100)

mycoupler.solve()

print("Convergence :", mycoupler.getSolveStatus())
if rank == 1:
    FieldT = myNeutroDriver.getOutputMEDField("Temperatures")
    ArrayT = FieldT.getArray()
    print("Temperatures :", ArrayT.getIJ(0, 0), ArrayT.getIJ(1, 0))
    assert round(ArrayT.getIJ(0, 0), 3) == round(1032.46971894, 3) and round(ArrayT.getIJ(1, 0), 3) == round(967.530281064, 3), "Results not good!"
if rank == 0:
    FieldRho = myThermoDriver.getOutputMEDField("Densities")
    ArrayRho = FieldRho.getArray()
    print("Densities :", ArrayRho.getIJ(0, 0), ArrayRho.getIJ(1, 0))
    assert round(ArrayRho.getIJ(0, 0), 3) == round(822.372079129, 3) and round(ArrayRho.getIJ(1, 0), 3) == round(700.711939405, 3), "Results not good!"

mycoupler.terminate()
