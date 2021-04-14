# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import unittest

import C3PO
from PhysicsScalar import PhysicsScalar

class ScalarPhysicsCoupler(C3PO.Coupler):
    def __init__(self, physics, exchangers, dataManagers=[]):
        C3PO.Coupler.__init__(self, physics, exchangers, dataManagers)

    def solveTimeStep(self):
        self.physicsDrivers_[0].solve()
        self.exchangers_[0].exchange()
        self.physicsDrivers_[1].solve()
        return self.getSolveStatus()

class Scalar_linear_test(unittest.TestCase):
    def test_main(self):
        myPhysics = PhysicsScalar()
        myPhysics.setOption(1., 0.5)
        myPhysics2 = PhysicsScalar()
        myPhysics2.setOption(3., -1.)

        Transformer = C3PO.DirectMatching()

        DataCoupler = C3PO.DataManager()
        First2Second = C3PO.Exchanger(Transformer, [], [], [(myPhysics, "y")], [(myPhysics2, "x")])
        Second2Data = C3PO.Exchanger(Transformer, [], [], [(myPhysics2, "y")], [(DataCoupler, "y")])
        Data2First = C3PO.Exchanger(Transformer, [], [], [(DataCoupler, "y")], [(myPhysics, "x")])

        OneIterationCoupler = ScalarPhysicsCoupler([myPhysics, myPhysics2], [First2Second])

        mycoupler = C3PO.FixedPointCoupler([OneIterationCoupler], [Second2Data, Data2First], [DataCoupler])
        mycoupler.setDampingFactor(0.5)
        mycoupler.setConvergenceParameters(1E-5, 100)

        mycoupler.init()
        mycoupler.solve()
        print(myPhysics.getValue("y"), myPhysics2.getValue("y"))
        self.assertAlmostEqual(myPhysics.getValue("y"), 5. / 3., 4)
        self.assertAlmostEqual(myPhysics2.getValue("y"), 4. / 3., 4)
        mycoupler.terminate()

if __name__ == "__main__":
    unittest.main()
