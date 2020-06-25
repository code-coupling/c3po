# -*- coding: utf-8 -*-
from __future__ import print_function, division
from mpi4py import MPI

import MEDCoupling
import MEDLoader

from neutroDriver import neutroDriver
from thermoDriver import thermoDriver
import C3PO
import C3POMPI


class Thermo2Neutro(C3PO.sharedRemapping):
    def __init__(self, remapper):
        C3PO.sharedRemapping.__init__(self, remapper, False)


class Neutro2Thermo(C3PO.sharedRemapping):
    def __init__(self, remapper):
        C3PO.sharedRemapping.__init__(self, remapper, True)


class OneIterationCoupler(C3POMPI.MPICoupler):
    def __init__(self, physics, exchangers, dataManagers=[]):
        C3POMPI.MPICoupler.__init__(self, physics, exchangers, dataManagers)

    def solveTimeStep(self):
        self.physicsDrivers_[0].solve()
        self.exchangers_[0].exchange()
        self.physicsDrivers_[1].solve()
        return self.physicsDrivers_[0].getSolveStatus() and self.physicsDrivers_[1].getSolveStatus()


myThermoDriver = thermoDriver()
myThermoDriver.init()
myThermoDriver.setValue("Vv_Vl", 10.)

myNeutroDriver = neutroDriver()
myNeutroDriver.init()
myNeutroDriver.setValue("meanT", 1000.)

basicTransformer = C3PO.remapper()
Thermo2DataTransformer = C3PO.directMatching()
Data2NeutroTransformer = Thermo2Neutro(basicTransformer)
Neutro2ThermoTransformer = Neutro2Thermo(basicTransformer)

DataCoupler = C3POMPI.MPICollectiveDataManager(MPI.COMM_WORLD)
ExchangerNeutro2Thermo = C3POMPI.MPIExchanger(Neutro2ThermoTransformer, [(myNeutroDriver, "Temperatures")], [(myThermoDriver, "Temperatures")])
ExchangerThermo2Data = C3POMPI.MPIExchanger(Thermo2DataTransformer, [(myThermoDriver, "Densities")], [(DataCoupler, "Densities")])
ExchangerData2Neutro = C3POMPI.MPIExchanger(Data2NeutroTransformer, [(DataCoupler, "Densities")], [(myNeutroDriver, "Densities")])

OneIteration = OneIterationCoupler([myNeutroDriver, myThermoDriver], [ExchangerNeutro2Thermo])

mycoupler = C3PO.GaussSeidelCoupler([OneIteration], [ExchangerThermo2Data, ExchangerData2Neutro], [DataCoupler])
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
