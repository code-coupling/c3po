# -*- coding: utf-8 -*-
from __future__ import print_function, division


def main_workerNeutro():
    import mpi4py.MPI as mpi

    import c3po
    import c3po.mpi

    from tests.med_Dussaix.NeutroDriver import NeutroDriver

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

    myNeutroDriver.init()
    myNeutroDriver.setInputDoubleValue("meanT", 1000.)

    basicTransformer = c3po.Remapper()
    Thermo2DataTransformer = c3po.DirectMatching()
    Data2NeutroTransformer = Thermo2Neutro(basicTransformer)
    Neutro2ThermoTransformer = Neutro2Thermo(basicTransformer)

    ExchangerNeutro2Thermo = c3po.mpi.MPIExchanger(Neutro2ThermoTransformer, [(myNeutroDriver, "Temperatures")], [(myThermoDriver, "Temperatures")])
    ExchangerThermo2Data = c3po.mpi.MPIExchanger(Thermo2DataTransformer, [(myThermoDriver, "Densities")], [(DataCoupler, "Densities")])
    ExchangerData2Neutro = c3po.mpi.MPIExchanger(Data2NeutroTransformer, [(DataCoupler, "Densities")], [(myNeutroDriver, "Densities")])
    ExchangerReturnResu = c3po.mpi.MPIExchanger(c3po.DirectMatching(), [(myNeutroDriver, "Temperatures")], [(MasterProcess, "Temperatures")])

    exchangers = [ExchangerNeutro2Thermo, ExchangerThermo2Data, ExchangerData2Neutro, ExchangerReturnResu]

    Worker = c3po.mpi.MPIWorker([myNeutroDriver, myThermoDriver], exchangers, [DataCoupler], MasterProcess)

    Worker.listen()
    myNeutroDriver.term()


main_workerNeutro()
