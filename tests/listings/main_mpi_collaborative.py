# -*- coding: utf-8 -*-
from __future__ import print_function

import pytest


def main_mpi_collaborative():
    import sys
    import os
    from mpi4py import MPI

    import c3po
    import c3po.mpi

    from tests.listings.PhysicsScalarTransient import PhysicsScalarTransient

    class ScalarPhysicsCoupler(c3po.mpi.MPICoupler):
        def __init__(self, physics, exchangers, dataManagers=[]):
            c3po.mpi.MPICoupler.__init__(self, physics, exchangers, dataManagers)
            self._failed = False

        def solveTimeStep(self):
            self._physicsDrivers[0].solve()
            self._exchangers[0].exchange()
            self._physicsDrivers[1].solve()
            return self.getSolveStatus()

        def abortTimeStep(self):
            self._failed = True
            c3po.Coupler.abortTimeStep(self)

        def validateTimeStep(self):
            self._failed = False
            c3po.Coupler.validateTimeStep(self)

        def computeTimeStep(self):
            (dt, stop) = c3po.Coupler.computeTimeStep(self)
            if self._failed:
                dt = self._dt / 2.
            return (dt, stop)

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    file5 = open("listingGeneral" + str(rank) + ".log", "wb+")
    listingW = c3po.ListingWriter(file5)
    if rank == 0:
        file1 = open("first.log", "w")
        file3 = open("listingFirst.log", "w")
        try:
            os.mkdir("run_1")
        except:
            pass
        Physics1 = c3po.tracer(pythonFile=file1, stdoutFile=file3, listingWriter=listingW, workingDir="run_1")(PhysicsScalarTransient)
    else:
        file2 = open("second.log", "w")
        file4 = open("listingSecond.log", "w")
        try:
            os.mkdir("run_2")
        except:
            pass
        Physics2 = c3po.tracer(pythonFile=file2, stdoutFile=file4, listingWriter=listingW, workingDir="run_2")(PhysicsScalarTransient)

    TracedExchanger = c3po.tracer(listingWriter=listingW)(c3po.mpi.MPIExchanger)

    myPhysics = c3po.mpi.MPIRemoteProcess(comm, 0)
    DataCoupler = c3po.mpi.MPICollectiveDataManager(comm)
    myPhysics2 = c3po.mpi.MPIRemoteProcess(comm, 1)
    localPhysics = 0

    if rank == 0:
        myPhysics = Physics1()
        localPhysics = myPhysics
    elif rank == 1:
        myPhysics2 = Physics2()
        localPhysics = myPhysics2

    listingW.setPhysicsDriverName(localPhysics, "Physics" + str(rank + 1))

    Transformer = c3po.DirectMatching()

    First2Second = TracedExchanger(Transformer, [], [], [(myPhysics, "y")], [(myPhysics2, "x")])
    Second2Data = TracedExchanger(Transformer, [], [], [(myPhysics2, "y")], [(DataCoupler, "y")])
    Data2First = TracedExchanger(Transformer, [], [], [(DataCoupler, "y")], [(myPhysics, "x")])
    listingW.setExchangerName(First2Second, "1 -> 2")
    listingW.setExchangerName(Second2Data, "2 -> Data")
    listingW.setExchangerName(Data2First, "Data -> 1")

    OneIterationCoupler = ScalarPhysicsCoupler([myPhysics, myPhysics2], [First2Second])

    mycoupler = c3po.FixedPointCoupler([OneIterationCoupler], [Second2Data, Data2First], [DataCoupler])
    mycoupler.setDampingFactor(0.5)
    mycoupler.setConvergenceParameters(1E-5, 10)

    mycoupler.init()

    mycoupler.setStationaryMode(False)
    print('Stationary mode :', mycoupler.getStationaryMode())

    if rank == 0:
        myPhysics.setOption(1., 0.5)
    else:
        myPhysics2.setOption(3., -1.)

    mycoupler.setTransientPrintLevel(2)
    mycoupler.solveTransient(2.)
    print(localPhysics.getOutputDoubleValue("y"))
    reference = 0.
    if rank == 0:
        reference = round(3.416666, 4)
    else:
        reference = round(2.733333, 4)

    assert pytest.approx(localPhysics.getOutputDoubleValue("y"), abs=1.E-4) == reference

    localPhysics.setInputDoubleValue("x", 0.)
    mycoupler.resetTime(0.)
    mycoupler.setTransientLogger(c3po.FortuneTeller())
    mycoupler.setPrintLevel(1)
    mycoupler.solveTransient(1., finishAtTmax=True)
    if rank == 0:
        reference = round(3. + 1./3., 4)
    else:
        reference = round(2. + 2./3., 4)

    print(localPhysics.getOutputDoubleValue("y"))
    assert pytest.approx(localPhysics.getOutputDoubleValue("y"), abs=1.E-4) == reference

    localPhysics.setInputDoubleValue("x", 0.)
    mycoupler.resetTime(0.)
    mycoupler.setTransientPrintLevel(1)
    mycoupler.solveTransient(0.5, finishAtTmax=True)
    if rank == 0:
        reference = round(2.5, 4)
    else:
        reference = round(2., 4)

    print(localPhysics.getOutputDoubleValue("y"))
    assert pytest.approx(localPhysics.getOutputDoubleValue("y"), abs=1.E-4) == reference

    mycoupler.term()

    if rank == 0:
        file1.close()
        file3.close()
    else:
        file2.close()
        file4.close()
    file5.close()

    if rank == 0:
        nameListing1 = "listingGeneral0.log"
        nameListing2 = "listingGeneral1.log"
        filegeneral = "listingGeneralMerged.log"
        c3po.mergeListing([nameListing1, nameListing2], filegeneral)

        dt1 = c3po.getTotalTimePhysicsDriver("listingGeneralMerged.log", "Physics1")
        dt2 = c3po.getTotalTimePhysicsDriver("listingGeneralMerged.log", "Physics2")

        dt3 = c3po.getTimesExchanger("listingGeneralMerged.log", "1 -> 2", ["Physics1", "Physics2"])
        dt4 = c3po.getTimesExchanger("listingGeneralMerged.log", "2 -> Data", ["Physics1", "Physics2"])
        dt5 = c3po.getTimesExchanger("listingGeneralMerged.log", "Data -> 1", ["Physics1"])

        print("Temps de calcul : ", dt1, dt2)
        print("Temps d'echange 1 -> 2 :", dt3)
        print("Temps d'echange 2 -> Data :", dt4)
        print("Temps d'echange Data -> 1 :", dt5)

        def nLines(fileName):
            with open(fileName, "r") as file_:
                n = 0
                for line in file_:
                    n += 1
            return n

        Nlines = [nLines("first.log"), nLines("second.log"), nLines("listingFirst.log"), nLines("listingSecond.log"), nLines("listingGeneral0.log"), nLines("listingGeneral1.log"), nLines("run_1/listing_PST.txt")]
        print(Nlines)
        assert Nlines == [701, 698, 129, 129, 819, 819, 129]

if __name__ == "__main__":
    main_mpi_collaborative()
