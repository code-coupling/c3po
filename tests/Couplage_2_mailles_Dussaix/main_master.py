# -*- coding: utf-8 -*-
from __future__ import print_function, division
import mpi4py.MPI as mpi

import MEDCoupling
import MEDLoader

import C3PO
import C3POMPI


class OneIterationCoupler(C3PO.coupler):
    def __init__(self, physics, exchangers, dataManagers=[]):
        C3PO.coupler.__init__(self, physics, exchangers, dataManagers)

    def solveTimeStep(self):
        self.physicsDrivers_[0].solve()
        self.exchangers_[0].exchange()
        self.physicsDrivers_[1].solve()
        return self.physicsDrivers_[0].getSolveStatus() and self.physicsDrivers_[1].getSolveStatus()


comm = mpi.COMM_WORLD

ThermoProcess = C3POMPI.MPIRemoteProcess(comm, 1)
NeutroProcess = C3POMPI.MPIRemoteProcess(comm, 2)

myThermoDriver = C3POMPI.MPIMasterPhysicsDriver(ThermoProcess)
myThermoDriver.init()
myThermoDriver.setValue("Vv_Vl", 10.)

myNeutroDriver = C3POMPI.MPIMasterPhysicsDriver(NeutroProcess)
myNeutroDriver.init()
myNeutroDriver.setValue("meanT", 1000.)

DataCoupler = C3POMPI.MPIMasterDataManager(myThermoDriver, 0)
ExchangerNeutro2Thermo = C3POMPI.MPIMasterExchanger([ThermoProcess, NeutroProcess], 0)
ExchangerThermo2Data = C3POMPI.MPIMasterExchanger([ThermoProcess, NeutroProcess], 1)
ExchangerData2Neutro = C3POMPI.MPIMasterExchanger([ThermoProcess, NeutroProcess], 2)

OneIteration = OneIterationCoupler([myNeutroDriver, myThermoDriver], [ExchangerNeutro2Thermo])

mycoupler = C3PO.fixedPointCoupler([OneIteration], [ExchangerThermo2Data, ExchangerData2Neutro], [DataCoupler])
mycoupler.setDampingFactor(0.125)
mycoupler.setConvergenceParameters(1E-5, 100)

mycoupler.solve()
FieldT = myNeutroDriver.getOutputMEDField("Temperatures")
ArrayT = FieldT.getArray()
FieldRho = myThermoDriver.getOutputMEDField("Densities")
ArrayRho = FieldRho.getArray()

print("Convergence :", mycoupler.getSolveStatus())
print("Temperatures :", ArrayT.getIJ(0, 0), ArrayT.getIJ(1, 0))
print("Densities :", ArrayRho.getIJ(0, 0), ArrayRho.getIJ(1, 0))
assert round(ArrayT.getIJ(0, 0), 3) == round(1032.46971894, 3) and round(ArrayT.getIJ(1, 0), 3) == round(967.530281064, 3) and round(ArrayRho.getIJ(0, 0), 3) == round(822.372079129, 3) and round(ArrayRho.getIJ(1, 0), 3) == round(700.711939405, 3), "Results not good!"

mycoupler.terminate()
