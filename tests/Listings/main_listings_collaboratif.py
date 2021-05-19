# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
from mpi4py import MPI
import unittest

import c3po
import c3po.mpi


class ScalarPhysicsCoupler(c3po.mpi.MPICoupler):
    def __init__(self, physics, exchangers, dataManagers=[]):
        c3po.mpi.MPICoupler.__init__(self, physics, exchangers, dataManagers)

    def solveTimeStep(self):
        self._physicsDrivers[0].solve()
        self._exchangers[0].exchange()
        self._physicsDrivers[1].solve()
        return self.getSolveStatus()


class ListingsCollab_test(unittest.TestCase):
    def test_main(self):
        from PhysicsScalarTransient import PhysicsScalarTransient

        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()

        file1 = open("first.log", "w")
        file2 = open("second.log", "w")
        file3 = open("listingFirst.log", "w")
        file4 = open("listingSecond.log", "w")
        file5 = open("listingGeneral" + str(rank) + ".log", "wb+")
        listingW = c3po.ListingWriter(file5)

        Physics1 = c3po.tracer(pythonFile=file1, stdoutFile=file3, listingWriter=listingW)(PhysicsScalarTransient)
        Physics2 = c3po.tracer(pythonFile=file2, stdoutFile=file4, listingWriter=listingW)(PhysicsScalarTransient)
        c3po.mpi.MPIExchanger = c3po.tracer(listingWriter=listingW)(c3po.mpi.MPIExchanger)

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

        Transformer = c3po.DirectMatching()

        First2Second = c3po.mpi.MPIExchanger(Transformer, [], [], [(myPhysics, "y")], [(myPhysics2, "x")])
        Second2Data = c3po.mpi.MPIExchanger(Transformer, [], [], [(myPhysics2, "y")], [(DataCoupler, "y")])
        Data2First = c3po.mpi.MPIExchanger(Transformer, [], [], [(DataCoupler, "y")], [(myPhysics, "x")])

        OneIterationCoupler = ScalarPhysicsCoupler([myPhysics, myPhysics2], [First2Second])

        mycoupler = c3po.FixedPointCoupler([OneIterationCoupler], [Second2Data, Data2First], [DataCoupler])
        mycoupler.setDampingFactor(0.5)
        mycoupler.setConvergenceParameters(1E-5, 100)

        listingW.initialize([(localPhysics, "Physics" + str(rank + 1))], [(First2Second, "1 -> 2"), (Second2Data, "2 -> Data"), (Data2First, "Data -> 1")])

        mycoupler.init()

        if rank == 0:
            myPhysics.setOption(1., 0.5)
        else:
            myPhysics2.setOption(3., -1.)

        mycoupler.solveTransient(2.)
        print(localPhysics.getValue("y"))
        reference = 0.
        if rank == 0:
            reference = round(3.166666, 4)
        else:
            reference = round(2.533333, 4)

        self.assertAlmostEqual(localPhysics.getValue("y"), reference, 4)

        mycoupler.terminate()

        file1.close()
        file2.close()
        file3.close()
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


if __name__ == "__main__":
    unittest.main()
