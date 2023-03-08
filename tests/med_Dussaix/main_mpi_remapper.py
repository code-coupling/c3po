# -*- coding: utf-8 -*-
from __future__ import print_function, division

import pytest


def main_mpi_remapper():
    from mpi4py import MPI

    import c3po
    import c3po.mpi

    from tests.med_Dussaix.MPINeutroDriver import MPINeutroDriver
    from tests.med_Dussaix.MPIThermoDriver import MPIThermoDriver

    class OneIterationCoupler(c3po.mpi.MPICoupler):
        def __init__(self, physics, exchangers, dataManagers=[]):
            c3po.mpi.MPICoupler.__init__(self, physics, exchangers, dataManagers)

        def solveTimeStep(self):
            self._physicsDrivers["neutro"].solve()
            self._exchangers[0].exchange()
            self._physicsDrivers["thermo"].solve()
            return self.getSolveStatus()

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    isThermo = comm.Get_rank() < 2
    codeMPIComm = comm.Split(isThermo)

    myThermoDriver = c3po.mpi.MPIRemoteProcesses(comm, [0, 1])
    myThermoData = c3po.mpi.MPIRemoteProcesses(comm, [0, 1])
    myNeutroDriver = c3po.mpi.MPIRemoteProcesses(comm, [2, 3])

    if isThermo:
        myThermoDriver = MPIThermoDriver()
        myThermoDriver.setMPIComm(codeMPIComm)
        myThermoData = c3po.mpi.MPIDomainDecompositionDataManager(codeMPIComm)

    else:
        myNeutroDriver = MPINeutroDriver()
        myNeutroDriver.setMPIComm(codeMPIComm)

    myThermoDriver.init()
    myThermoDriver.setInputDoubleValue("Vv_Vl", 10.)

    myNeutroDriver.init()
    myNeutroDriver.setInputDoubleValue("meanT", 1000.)

    basicTransformer = c3po.mpi.MPIRemapper()
    Thermo2DataTransformer = c3po.DirectMatching()
    Data2NeutroTransformer = c3po.mpi.MPISharedRemapping(basicTransformer, reverse=False)
    Neutro2ThermoTransformer = c3po.mpi.MPISharedRemapping(basicTransformer, reverse=True)

    ExchangerNeutro2Thermo = c3po.mpi.MPIExchanger(Neutro2ThermoTransformer, [(myNeutroDriver, "Temperatures")], [(myThermoDriver, "Temperatures")])
    ExchangerThermo2Data = c3po.mpi.MPIExchanger(Thermo2DataTransformer, [(myThermoDriver, "Densities")], [(myThermoData, "Densities")])
    ExchangerData2Neutro = c3po.mpi.MPIExchanger(Data2NeutroTransformer, [(myThermoData, "Densities")], [(myNeutroDriver, "Densities")])

    OneIteration = OneIterationCoupler({"neutro": myNeutroDriver, "thermo": myThermoDriver}, [ExchangerNeutro2Thermo])

    DataCoupler = c3po.mpi.MPICollaborativeDataManager([myThermoData], comm)
    mycoupler = c3po.FixedPointCoupler([OneIteration], [ExchangerThermo2Data, ExchangerData2Neutro], [DataCoupler])
    mycoupler.init()
    mycoupler.setDampingFactor(0.125)
    mycoupler.setConvergenceParameters(1E-5, 100)

    mycoupler.solve()

    print("Convergence :", mycoupler.getSolveStatus())
    if rank == 1:
        FieldT = myNeutroDriver.getOutputMEDDoubleField("Temperatures")
        ArrayT = FieldT.getArray()
        print("Temperatures :", ArrayT.getIJ(0, 0), ArrayT.getIJ(1, 0))
        assert pytest.approx(ArrayT.getIJ(0, 0), abs=1.E-3) == 1032.46971894
        assert pytest.approx(ArrayT.getIJ(1, 0), abs=1.E-3) == 967.530281064
    if rank == 0:
        FieldRho = myThermoDriver.getOutputMEDDoubleField("Densities")
        ArrayRho = FieldRho.getArray()
        print("Densities :", ArrayRho.getIJ(0, 0), ArrayRho.getIJ(1, 0))
        assert pytest.approx(ArrayRho.getIJ(0, 0), abs=1.E-3) == 822.372079129
        assert pytest.approx(ArrayRho.getIJ(1, 0), abs=1.E-3) == 700.711939405

    mycoupler.term()
    myNeutroDriver.term()
    myThermoDriver.term()
    basicTransformer.terminate()


if __name__ == "__main__":
    main_mpi_remapper()
