# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import unittest

import c3po
from PhysicsScalar import PhysicsScalar


class ScalarPhysicsCoupler(c3po.Coupler):
    def __init__(self, physics, exchangers, dataManagers=[]):
        c3po.Coupler.__init__(self, physics, exchangers, dataManagers)

    def solveTimeStep(self):
        self._physicsDrivers[0].solve()
        self._exchangers[0].exchange()
        self._physicsDrivers[1].solve()
        return self.getSolveStatus()


class Scalar_linear_test(unittest.TestCase):
    def test_main(self):
        myPhysics = PhysicsScalar()
        myPhysics.setOption(1., 0.5)
        myPhysics2 = PhysicsScalar()
        myPhysics2.setOption(3., -1.)

        Transformer = c3po.DirectMatching()

        DataCoupler = c3po.LocalDataManager()
        First2Second = c3po.LocalExchanger(Transformer, [], [], [(myPhysics, "y")], [(myPhysics2, "x")])
        Second2Data = c3po.LocalExchanger(Transformer, [], [], [(myPhysics2, "y")], [(DataCoupler, "y")])
        Data2First = c3po.LocalExchanger(Transformer, [], [], [(DataCoupler, "y")], [(myPhysics, "x")])

        OneIterationCoupler = ScalarPhysicsCoupler([myPhysics, myPhysics2], [First2Second])

        mycoupler = c3po.FixedPointCoupler([OneIterationCoupler], [Second2Data, Data2First], [DataCoupler])
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
