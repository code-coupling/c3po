# -*- coding: utf-8 -*-
from __future__ import print_function
import sys

import C3PO
from physicsScalar import physicsScalar


class ScalarPhysicsCoupler(C3PO.coupler):
    def __init__(self, physics, exchangers, dataManagers=[]):
        C3PO.coupler.__init__(self, physics, exchangers, dataManagers)

    def solveTimeStep(self):
        self.physicsDrivers_[0].solve()
        self.exchangers_[0].exchange()
        self.physicsDrivers_[1].solve()
        return self.physicsDrivers_[0].getSolveStatus() and self.physicsDrivers_[1].getSolveStatus()


file1 = open("first.log", "w")
file2 = open("second.log", "w")
file3 = open("listingFirst.log", "w")
file4 = open("listingSecond.log", "w")

physicsScalar1 = C3PO.tracer(pythonFile = file1, stdoutFile = file3)(physicsScalar)
physicsScalar2 = C3PO.tracer(pythonFile = file2, stdoutFile = file4)(physicsScalar)

myPhysics = physicsScalar1()
myPhysics.setOption(1., 0.5)
myPhysics2 = physicsScalar2()
myPhysics2.setOption(3., -1.)

Transformer = C3PO.directMatching()

DataCoupler = C3PO.dataManager()
First2Second = C3PO.exchanger(Transformer, [], [], [(myPhysics, "y")], [(myPhysics2, "x")])
Second2Data = C3PO.exchanger(Transformer, [], [], [(myPhysics2, "y")], [(DataCoupler, "y")])
Data2First = C3PO.exchanger(Transformer, [], [], [(DataCoupler, "y")], [(myPhysics, "x")])

OneIterationCoupler = ScalarPhysicsCoupler([myPhysics, myPhysics2], [First2Second])

mycoupler = C3PO.fixedPointCoupler([OneIterationCoupler], [Second2Data, Data2First], [DataCoupler])
mycoupler.setDampingFactor(0.5)
mycoupler.setConvergenceParameters(1E-5, 100)

mycoupler.solve()
print(myPhysics.getValue("y"), myPhysics2.getValue("y"))
assert round(myPhysics.getValue("y"), 4) == round(5. / 3., 4) and round(myPhysics2.getValue("y"), 4) == round(4. / 3., 4), "Results not good!"

mycoupler.terminate()

file1.close()
file2.close()
file3.close()
file4.close()
