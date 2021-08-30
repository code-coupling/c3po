# -*- coding: utf-8 -*-
from __future__ import print_function, division
from mpi4py import MPI
import unittest

import c3po.medcouplingCompat as mc

import c3po
import c3po.mpi


class OneIterationCoupler(c3po.mpi.MPICoupler):
    def __init__(self, physics, exchangers, dataManagers=[]):
        c3po.mpi.MPICoupler.__init__(self, physics, exchangers, dataManagers)

    def solveTimeStep(self):
        self._physicsDrivers[0].solve()
        self._exchangers[0].exchange()
        self._physicsDrivers[1].solve()
        return self.getSolveStatus()


class DussaixSeq_test(unittest.TestCase):
    def test_main(self):
        from NeutroDriver import NeutroDriver
        from ThermoDriver import ThermoDriver

        myThermoDriver = ThermoDriver()
        myThermoDriver.init()
        myThermoDriver.setInputDoubleValue("Vv_Vl", 10.)

        myNeutroDriver = NeutroDriver()
        myNeutroDriver.init()
        myNeutroDriver.setInputDoubleValue("meanT", 1000.)

        basicTransformer = c3po.Remapper()
        Thermo2DataTransformer = c3po.DirectMatching()
        Data2NeutroTransformer = c3po.SharedRemapping(basicTransformer, reverse=False)
        Neutro2ThermoTransformer = c3po.SharedRemapping(basicTransformer, reverse=True)

        DataCoupler = c3po.mpi.MPICollectiveDataManager(MPI.COMM_WORLD)
        ExchangerNeutro2Thermo = c3po.mpi.MPIExchanger(Neutro2ThermoTransformer, [(myNeutroDriver, "Temperatures")], [(myThermoDriver, "Temperatures")])
        ExchangerThermo2Data = c3po.mpi.MPIExchanger(Thermo2DataTransformer, [(myThermoDriver, "Densities")], [(DataCoupler, "Densities")])
        ExchangerData2Neutro = c3po.mpi.MPIExchanger(Data2NeutroTransformer, [(DataCoupler, "Densities")], [(myNeutroDriver, "Densities")])

        OneIteration = OneIterationCoupler([myNeutroDriver, myThermoDriver], [ExchangerNeutro2Thermo])

        mycoupler = c3po.FixedPointCoupler([OneIteration], [ExchangerThermo2Data, ExchangerData2Neutro], [DataCoupler])
        mycoupler.setDampingFactor(0.125)
        mycoupler.setConvergenceParameters(1E-5, 100)

        mycoupler.solve()
        FieldT = myNeutroDriver.getOutputMEDDoubleField("Temperatures")
        ArrayT = FieldT.getArray()
        FieldRho = myThermoDriver.getOutputMEDDoubleField("Densities")
        ArrayRho = FieldRho.getArray()

        print("Convergence :", mycoupler.getSolveStatus())
        print("Temperatures :", ArrayT.getIJ(0, 0), ArrayT.getIJ(1, 0))
        print("Densities :", ArrayRho.getIJ(0, 0), ArrayRho.getIJ(1, 0))

        self.assertAlmostEqual(ArrayT.getIJ(0, 0), 1032.46971894, 3)
        self.assertAlmostEqual(ArrayT.getIJ(1, 0), 967.530281064, 3)
        self.assertAlmostEqual(ArrayRho.getIJ(0, 0), 822.372079129, 3)
        self.assertAlmostEqual(ArrayRho.getIJ(1, 0), 700.711939405, 3)

        mycoupler.terminate()


if __name__ == "__main__":
    unittest.main()
