# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import os
import pytest

import c3po


class OneIterationCoupler(c3po.Coupler):
    def __init__(self, physics, exchangers, dataManagers=[]):
        c3po.Coupler.__init__(self, physics, exchangers, dataManagers)

    def solveTimeStep(self):
        self._physicsDrivers[0].solve()
        self._exchangers[0].exchange()
        self._physicsDrivers[1].solve()
        return self.getSolveStatus()


class ExplicitCoupler(c3po.Coupler):
    def __init__(self, physics, exchangers, dataManagers=[]):
        c3po.Coupler.__init__(self, physics, exchangers, dataManagers)

    def solveTimeStep(self):
        self._exchangers[0].exchange()
        self._physicsDrivers[0].solve()
        self._exchangers[1].exchange()
        self._physicsDrivers[1].solve()
        return self.getSolveStatus()


def main_1():
    from tests.transient.PhysicsScalarTransient import PhysicsScalarTransient

    nameListing1 = "listingBox1.log"
    nameListing2 = "listingBox2.log"
    fileBox = open("listingBox1.log", "wb+")
    fileBoxAccu = open("listingBox2.log", "wb+")
    listingW = c3po.ListingWriter(fileBox)
    listingWAccu = c3po.ListingWriter(fileBoxAccu)

    TracedPhysics = c3po.tracer(listingWriter=listingW)(PhysicsScalarTransient)
    TracedExchanger = c3po.tracer(listingWriter=listingW)(c3po.LocalExchanger)
    TracedAccu = c3po.tracer(listingWriter=listingWAccu)(c3po.TimeAccumulator)

    coef1 = 1.
    sec1 = 3.
    coef2 = 5.
    sec2 = 2.

    myPhysics1 = TracedPhysics()
    myPhysics1.init()
    myPhysics1.setOption(coef1, sec1, 0.2)
    accuPhysics1 = TracedAccu(myPhysics1, saveParameters=(1, "INTERNAL"), stabilizedTransient=(True, 100.))
    accuPhysics1.init()

    myPhysics2 = TracedPhysics()
    myPhysics2.init()
    myPhysics2.setOption(coef2, sec2, 0.3)
    accuPhysics2 = TracedAccu(myPhysics2, saveParameters=(1, "INTERNAL"), stabilizedTransient=(True, 100.))
    accuPhysics2.init()

    transformer = c3po.DirectMatching()

    myData = c3po.LocalDataManager()
    first2Second = TracedExchanger(transformer, [], [], [(accuPhysics1, "y")], [(accuPhysics2, "x")])
    second2First = TracedExchanger(transformer, [], [], [(accuPhysics2, "y")], [(accuPhysics1, "x")])
    second2Data = TracedExchanger(transformer, [], [], [(accuPhysics2, "y")], [(myData, "y")])
    data2First = TracedExchanger(transformer, [], [], [(myData, "y")], [(accuPhysics1, "x")])

    iterativeCoupler = OneIterationCoupler([accuPhysics1, accuPhysics2], [first2Second])
    iterativeCoupler.init()

    stationaryCoupler = c3po.AndersonCoupler([iterativeCoupler], [second2Data, data2First], [myData])
    stationaryCoupler.setConvergenceParameters(1E-5, 100)

    listingW.initialize([(myPhysics1, "Physics1"), (myPhysics2, "Physics2")], [(first2Second, "1 -> 2"), (second2First, "2 -> 1"), (second2Data, "2 -> Data"), (data2First, "Data -> 1")])
    listingWAccu.initialize([(accuPhysics1, "accuPhysics1"), (accuPhysics2, "accuPhysics2")], [])

    stationaryCoupler.init()

    stationaryCoupler.setStationaryMode(True)
    stationaryCoupler.initTimeStep(0.)
    stationaryCoupler.solve()
    stationaryCoupler.validateTimeStep()

    print(accuPhysics1.getOutputDoubleValue("y"), accuPhysics2.getOutputDoubleValue("y"))
    assert pytest.approx(accuPhysics1.getOutputDoubleValue("y"), abs=1.E-4) == (sec2 + coef2 * sec1) / (coef1 * coef2 - 1.)
    assert pytest.approx(accuPhysics2.getOutputDoubleValue("y"), abs=1.E-4) == coef1 * (sec2 + coef2 * sec1) / (coef1 * coef2 - 1.) - sec1

    stationaryCoupler.term()
    iterativeCoupler.term()

    sec1Transient = 10.
    myPhysics1.setOption(coef1, sec1Transient, 0.2)

    transientCoupler = ExplicitCoupler([accuPhysics1, accuPhysics2], [second2First, first2Second])
    transientCoupler.init()

    accuPhysics1.setInputDoubleValue("macrodt", 1.)
    accuPhysics2.setInputDoubleValue("macrodt", 2.)

    transientCoupler.initTimeStep(0.45)
    transientCoupler.solve()
    print(myPhysics1.getOutputDoubleValue("y"), myPhysics2.getOutputDoubleValue("y"))
    assert pytest.approx(accuPhysics1.getOutputDoubleValue("y"), abs=1.E-4) == 9.924554470450024
    assert pytest.approx(accuPhysics2.getOutputDoubleValue("y"), abs=1.E-4) == 2.357362317604187
    transientCoupler.abortTimeStep()

    transientCoupler.solveTransient(0.45, finishAtTmax=True)

    print(myPhysics1.getOutputDoubleValue("y"), myPhysics2.getOutputDoubleValue("y"))
    assert pytest.approx(accuPhysics1.getOutputDoubleValue("y"), abs=1.E-4) == 9.924554470450024
    assert pytest.approx(accuPhysics2.getOutputDoubleValue("y"), abs=1.E-4) == 2.357362317604187

    transientCoupler.solveTransient(7.)
    print(myPhysics1.getOutputDoubleValue("y"), myPhysics2.getOutputDoubleValue("y"))
    assert pytest.approx(accuPhysics1.getOutputDoubleValue("y"), abs=1.E-4) == (sec2 + coef2 * sec1Transient) / (coef1 * coef2 - 1.)
    assert pytest.approx(accuPhysics2.getOutputDoubleValue("y"), abs=1.E-4) == coef1 * (sec2 + coef2 * sec1Transient) / (coef1 * coef2 - 1.) - sec1Transient

    transientCoupler.term()
    accuPhysics1.term()
    accuPhysics2.term()
    myPhysics1.term()
    myPhysics2.term()

    fileBox.close()
    fileBoxAccu.close()

    nameListingMerged = "listingBox.log"
    c3po.mergeListing([nameListing1, nameListing2], nameListingMerged)

    def nLines(fileName):
        with open(fileName, "r") as file_:
            n = 0
            for line in file_:
                n += 1
        return n

    Nlines = [nLines(nameListing1), nLines(nameListing2), nLines(nameListingMerged)]
    print(Nlines)
    assert Nlines == [880, 130, 1053]

def test_sequential():
    main_1()
    try: os.remove("listingBox1.log")
    except: pass
    try: os.remove("listingBox2.log")
    except: pass
    try: os.remove("listingBox.log")
    except: pass

if __name__ == "__main__":
    main_1()
