# -*- coding: utf-8 -*-
from __future__ import print_function
import sys

import C3PO
from PhysicsScalarTransient import PhysicsScalarTransient


class ScalarPhysicsCoupler(C3PO.Coupler):
    def __init__(self, physics, exchangers, dataManagers=[]):
        C3PO.Coupler.__init__(self, physics, exchangers, dataManagers)

    def solveTimeStep(self):
        self.physicsDrivers_[0].solve()
        self.exchangers_[0].exchange()
        self.physicsDrivers_[1].solve()
        return self.getSolveStatus()


file1 = open("first.log", "w")
file2 = open("second.log", "w")
file3 = open("listingFirst.log", "w")
file4 = open("listingSecond.log", "w")
file5 = open("listingGeneral.log", "wb+")
listingW = C3PO.ListingWriter(file5)

Physics1 = C3PO.Tracer(pythonFile=file1, stdoutFile=file3, listingWriter=listingW)(PhysicsScalarTransient)
Physics2 = C3PO.Tracer(pythonFile=file2, stdoutFile=file4, listingWriter=listingW)(PhysicsScalarTransient)
C3PO.Exchanger = C3PO.Tracer(listingWriter=listingW)(C3PO.Exchanger)

myPhysics = Physics1()
myPhysics2 = Physics2()

Transformer = C3PO.DirectMatching()

DataCoupler = C3PO.DataManager()
First2Second = C3PO.Exchanger(Transformer, [], [], [(myPhysics, "y")], [(myPhysics2, "x")])
Second2Data = C3PO.Exchanger(Transformer, [], [], [(myPhysics2, "y")], [(DataCoupler, "y")])
Data2First = C3PO.Exchanger(Transformer, [], [], [(DataCoupler, "y")], [(myPhysics, "x")])

OneIterationCoupler = ScalarPhysicsCoupler([myPhysics, myPhysics2], [First2Second])

mycoupler = C3PO.FixedPointCoupler([OneIterationCoupler], [Second2Data, Data2First], [DataCoupler])
mycoupler.setDampingFactor(0.5)
mycoupler.setConvergenceParameters(1E-5, 100)

listingW.initialize([(myPhysics, "Physics1"), (myPhysics2, "Physics2")], [(First2Second, "1 -> 2"), (Second2Data, "2 -> Data"), (Data2First, "Data -> 1")])

mycoupler.init()

myPhysics.setOption(1., 0.5)
myPhysics2.setOption(3., -1.)

mycoupler.solveTransient(2.)
print(myPhysics.getValue("y"), myPhysics2.getValue("y"))
assert round(myPhysics.getValue("y"), 4) == round(3.166666, 4) and round(myPhysics2.getValue("y"), 4) == round(2.533333, 4), "Results not good!"

mycoupler.terminate()

file1.close()
file2.close()
file3.close()
file4.close()
file5.close()
