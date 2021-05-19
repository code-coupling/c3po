# -*- coding: utf-8 -*-
from __future__ import print_function, division
from mpi4py import MPI
import unittest

import c3po.medcouplingCompat as mc
import c3po
import c3po.mpi


class Thermo2Neutro(c3po.SharedRemapping):
    def __init__(self, remapper):
        c3po.SharedRemapping.__init__(self, remapper, reverse=False)


class Neutro2Thermo(c3po.SharedRemapping):
    def __init__(self, remapper):
        c3po.SharedRemapping.__init__(self, remapper, reverse=True)


class OneIterationCoupler(c3po.mpi.MPICoupler):
    def __init__(self, physics, exchangers, dataManagers=[]):
        c3po.mpi.MPICoupler.__init__(self, physics, exchangers, dataManagers)

    def solveTimeStep(self):
        self._physicsDrivers["neutro"].solve()
        self._exchangers[0].exchange()
        self._physicsDrivers["thermo"].solve()
        return self.getSolveStatus()


class DussaixSeq_collaborative(unittest.TestCase):
    def test_main(self):
        from NeutroDriver import NeutroDriver
        from ThermoDriver import ThermoDriver

        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()

        myThermoDriver = c3po.mpi.MPIRemoteProcess(comm, 0)
        DataCoupler = c3po.mpi.MPICollectiveDataManager(comm)
        myNeutroDriver = c3po.mpi.MPIRemoteProcess(comm, 1)

        if rank == 0:
            myThermoDriver = ThermoDriver()

        elif rank == 1:
            myNeutroDriver = NeutroDriver()

        myThermoDriver.init()
        myThermoDriver.setValue("Vv_Vl", 10.)

        myNeutroDriver.init()
        myNeutroDriver.setValue("meanT", 1000.)

        basicTransformer = c3po.Remapper()
        Thermo2DataTransformer = c3po.DirectMatching()
        Data2NeutroTransformer = Thermo2Neutro(basicTransformer)
        Neutro2ThermoTransformer = Neutro2Thermo(basicTransformer)

        DataCoupler = c3po.mpi.MPICollectiveDataManager(MPI.COMM_WORLD)
        ExchangerNeutro2Thermo = c3po.mpi.MPIExchanger(Neutro2ThermoTransformer, [(myNeutroDriver, "Temperatures")], [(myThermoDriver, "Temperatures")])
        ExchangerThermo2Data = c3po.mpi.MPIExchanger(Thermo2DataTransformer, [(myThermoDriver, "Densities")], [(DataCoupler, "Densities")])
        ExchangerData2Neutro = c3po.mpi.MPIExchanger(Data2NeutroTransformer, [(DataCoupler, "Densities")], [(myNeutroDriver, "Densities")])

        OneIteration = OneIterationCoupler({"neutro": myNeutroDriver, "thermo": myThermoDriver}, [ExchangerNeutro2Thermo])

        mycoupler = c3po.FixedPointCoupler([OneIteration], [ExchangerThermo2Data, ExchangerData2Neutro], [DataCoupler])
        mycoupler.setDampingFactor(0.125)
        mycoupler.setConvergenceParameters(1E-5, 100)

        mycoupler.solve()

        print("Convergence :", mycoupler.getSolveStatus())
        if rank == 1:
            FieldT = myNeutroDriver.getOutputMEDField("Temperatures")
            ArrayT = FieldT.getArray()
            print("Temperatures :", ArrayT.getIJ(0, 0), ArrayT.getIJ(1, 0))
            self.assertAlmostEqual(ArrayT.getIJ(0, 0), 1032.46971894, 3)
            self.assertAlmostEqual(ArrayT.getIJ(1, 0), 967.530281064, 3)
        if rank == 0:
            FieldRho = myThermoDriver.getOutputMEDField("Densities")
            ArrayRho = FieldRho.getArray()
            print("Densities :", ArrayRho.getIJ(0, 0), ArrayRho.getIJ(1, 0))
            self.assertAlmostEqual(ArrayRho.getIJ(0, 0), 822.372079129, 3)
            self.assertAlmostEqual(ArrayRho.getIJ(1, 0), 700.711939405, 3)

        mycoupler.terminate()


if __name__ == "__main__":
    unittest.main()
