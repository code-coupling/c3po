# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import unittest

import c3po


class ScalarPhysicsCoupler(c3po.Coupler):
    def __init__(self, physics, exchangers, dataManagers=[]):
        c3po.Coupler.__init__(self, physics, exchangers, dataManagers)

    def solveTimeStep(self):
        self._physicsDrivers[0].solve()
        self._exchangers[0].exchange()
        self._physicsDrivers[1].solve()
        return self.getSolveStatus()


class Listings_test(unittest.TestCase):
    def test_main(self):
        from PhysicsScalarTransient import PhysicsScalarTransient

        file1 = open("first.log", "w")
        file2 = open("second.log", "w")
        file3 = open("listingFirst.log", "w")
        file4 = open("listingSecond.log", "w")
        file5 = open("listingGeneral.log", "wb+")
        listingW = c3po.ListingWriter(file5)

        Physics1 = c3po.tracer(pythonFile=file1, stdoutFile=file3, listingWriter=listingW)(PhysicsScalarTransient)
        Physics1 = c3po.nameChanger({"toto": "x", "tat@*": "*"}, '*')(Physics1)
        Physics2 = c3po.tracer(pythonFile=file2, stdoutFile=file4, listingWriter=listingW)(PhysicsScalarTransient)
        c3po.LocalExchanger = c3po.tracer(listingWriter=listingW)(c3po.LocalExchanger)

        myPhysics = Physics1()
        myPhysics2 = Physics2()
        myPhysics.init()
        myPhysics2.init()

        Transformer = c3po.DirectMatching()

        DataCoupler = c3po.LocalDataManager()
        First2Second = c3po.LocalExchanger(Transformer, [], [], [(myPhysics, "tat@y")], [(myPhysics2, "x")])
        Second2Data = c3po.LocalExchanger(Transformer, [], [], [(myPhysics2, "y")], [(DataCoupler, "y")])
        Data2First = c3po.LocalExchanger(Transformer, [], [], [(DataCoupler, "y")], [(myPhysics, "toto")])

        OneIterationCoupler = ScalarPhysicsCoupler([myPhysics, myPhysics2], [First2Second])

        mycoupler = c3po.FixedPointCoupler([OneIterationCoupler], [Second2Data, Data2First], [DataCoupler])
        mycoupler.setDampingFactor(0.5)
        mycoupler.setConvergenceParameters(1E-5, 100)

        listingW.initialize([(myPhysics, "Physics1"), (myPhysics2, "Physics2")], [(First2Second, "1 -> 2"), (Second2Data, "2 -> Data"), (Data2First, "Data -> 1")])

        mycoupler.init()

        mycoupler.setStationaryMode(False)
        print('Stationary mode :', mycoupler.getStationaryMode())

        myPhysics.setOption(1., 0.5)
        myPhysics2.setOption(3., -1.)

        mycoupler.solveTransient(2.)
        print(myPhysics.getOutputDoubleValue("y"), myPhysics2.getOutputDoubleValue("y"))

        self.assertAlmostEqual(myPhysics.getOutputDoubleValue("y"), 3.166666, 4)
        self.assertAlmostEqual(myPhysics2.getOutputDoubleValue("y"), 2.533333, 4)

        mycoupler.resetTime(0.)
        mycoupler.solveTransient(1.)

        mycoupler.term()
        myPhysics.term()
        myPhysics2.term()

        file1.close()
        file2.close()
        file3.close()
        file4.close()
        file5.close()


if __name__ == "__main__":
    unittest.main()
