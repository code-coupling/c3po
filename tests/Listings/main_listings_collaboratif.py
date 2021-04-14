# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
from mpi4py import MPI
import unittest

import C3PO
import C3POMPI

class ScalarPhysicsCoupler(C3POMPI.MPICoupler):
    def __init__(self, physics, exchangers, dataManagers=[]):
        C3POMPI.MPICoupler.__init__(self, physics, exchangers, dataManagers)

    def solveTimeStep(self):
        self.physicsDrivers_[0].solve()
        self.exchangers_[0].exchange()
        self.physicsDrivers_[1].solve()
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
        listingW = C3PO.ListingWriter(file5)

        Physics1 = C3PO.Tracer(pythonFile=file1, stdoutFile=file3, listingWriter=listingW)(PhysicsScalarTransient)
        Physics2 = C3PO.Tracer(pythonFile=file2, stdoutFile=file4, listingWriter=listingW)(PhysicsScalarTransient)
        C3POMPI.MPIExchanger = C3PO.Tracer(listingWriter=listingW)(C3POMPI.MPIExchanger)

        myPhysics = C3POMPI.MPIRemoteProcess(comm, 0)
        DataCoupler = C3POMPI.MPICollectiveDataManager(comm)
        myPhysics2 = C3POMPI.MPIRemoteProcess(comm, 1)
        localPhysics = 0

        if rank == 0:
            myPhysics = Physics1()
            localPhysics = myPhysics
        elif rank == 1:
            myPhysics2 = Physics2()
            localPhysics = myPhysics2

        Transformer = C3PO.DirectMatching()

        First2Second = C3POMPI.MPIExchanger(Transformer, [], [], [(myPhysics, "y")], [(myPhysics2, "x")])
        Second2Data = C3POMPI.MPIExchanger(Transformer, [], [], [(myPhysics2, "y")], [(DataCoupler, "y")])
        Data2First = C3POMPI.MPIExchanger(Transformer, [], [], [(DataCoupler, "y")], [(myPhysics, "x")])

        OneIterationCoupler = ScalarPhysicsCoupler([myPhysics, myPhysics2], [First2Second])

        mycoupler = C3PO.FixedPointCoupler([OneIterationCoupler], [Second2Data, Data2First], [DataCoupler])
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
            C3PO.mergeListing([nameListing1, nameListing2], filegeneral)

            dt1 = C3PO.getTotalTimePhysicsDriver("listingGeneralMerged.log", "Physics1")
            dt2 = C3PO.getTotalTimePhysicsDriver("listingGeneralMerged.log", "Physics2")

            dt3 = C3PO.getTimesExchanger("listingGeneralMerged.log", "1 -> 2", ["Physics1", "Physics2"])
            dt4 = C3PO.getTimesExchanger("listingGeneralMerged.log", "2 -> Data", ["Physics1", "Physics2"])
            dt5 = C3PO.getTimesExchanger("listingGeneralMerged.log", "Data -> 1", ["Physics1"])

            print("Temps de calcul : ", dt1, dt2)
            print("Temps d'echange 1 -> 2 :", dt3)
            print("Temps d'echange 2 -> Data :", dt4)
            print("Temps d'echange Data -> 1 :", dt5)

if __name__ == "__main__":
    unittest.main()
