# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import os
import pytest

import c3po


class ScalarPhysicsCoupler(c3po.Coupler):
    def __init__(self, physics, exchangers, dataManagers=[]):
        c3po.Coupler.__init__(self, physics, exchangers, dataManagers)
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


def main_sequential():
    from tests.listings.PhysicsScalarTransient import PhysicsScalarTransient

    file1 = open("first.log", "w")
    file2 = open("second.log", "w")
    file3 = open("listingFirst.log", "w")
    file4 = open("listingSecond.log", "w")
    file5 = open("listingGeneral.log", "wb+")
    listingW = c3po.ListingWriter(file5)

    Physics1 = c3po.tracer(pythonFile=file1, stdoutFile=file3, listingWriter=listingW)(PhysicsScalarTransient)
    Physics2 = c3po.tracer(pythonFile=file2, stdoutFile=file4, listingWriter=listingW)(PhysicsScalarTransient)
    TracedExchanger = c3po.tracer(listingWriter=listingW)(c3po.LocalExchanger)

    myPhysics = Physics1()
    myPhysics.setOption(1., 0.5)
    myPhysics1 = c3po.NameChanger(myPhysics, nameMappingValue={"toto": "x", "tat@*": "*"}, wildcard="*")

    myPhysics2 = Physics2()
    myPhysics2.setOption(3., -1.)

    Transformer = c3po.DirectMatching()

    DataCoupler = c3po.LocalDataManager()
    First2Second = TracedExchanger(Transformer, [], [], [(myPhysics1, "tat@y")], [(myPhysics2, "x")])
    Second2Data = TracedExchanger(Transformer, [], [], [(myPhysics2, "y")], [(DataCoupler, "y")])
    Data2First = TracedExchanger(Transformer, [], [], [(DataCoupler, "y")], [(myPhysics1, "toto")])

    OneIterationCoupler = ScalarPhysicsCoupler([myPhysics1, myPhysics2], [First2Second])

    mycoupler = c3po.FixedPointCoupler([OneIterationCoupler], [Second2Data, Data2First], [DataCoupler])
    mycoupler.setDampingFactor(0.5)
    mycoupler.setConvergenceParameters(1E-5, 10)

    listingW.initialize([(myPhysics, "Physics1"), (myPhysics2, "Physics2")], [(First2Second, "1 -> 2"), (Second2Data, "2 -> Data"), (Data2First, "Data -> 1")])

    myPhysics1.init()
    myPhysics2.init()
    mycoupler.init()

    mycoupler.setStationaryMode(False)
    print('Stationary mode :', mycoupler.getStationaryMode())
    assert not mycoupler.getStationaryMode()

    mycoupler.setTransientPrintLevel(2)
    mycoupler.solveTransient(2.)

    print(myPhysics1.getOutputDoubleValue("y"), myPhysics2.getOutputDoubleValue("y"))
    assert pytest.approx(myPhysics1.getOutputDoubleValue("y"), abs=1.E-4) == 3.416666
    assert pytest.approx(myPhysics2.getOutputDoubleValue("y"), abs=1.E-4) == 2.733333

    myPhysics1.setInputDoubleValue("x", 0.)
    myPhysics2.setInputDoubleValue("x", 0.)
    mycoupler.resetTime(0.)
    mycoupler.setTransientLogger(c3po.FortuneTeller())
    mycoupler.setPrintLevel(1)
    mycoupler.solveTransient(1., finishAtTmax=True)

    print(myPhysics1.getOutputDoubleValue("y"), myPhysics2.getOutputDoubleValue("y"))
    assert pytest.approx(myPhysics1.getOutputDoubleValue("y"), abs=1.E-4) == 3. + 1./3.
    assert pytest.approx(myPhysics2.getOutputDoubleValue("y"), abs=1.E-4) == 2. + 2./3.

    myPhysics1.setInputDoubleValue("x", 0.)
    myPhysics2.setInputDoubleValue("x", 0.)
    mycoupler.resetTime(0.)
    mycoupler.setTransientPrintLevel(1)
    mycoupler.solveTransient(0.5, finishAtTmax=True)

    print(myPhysics1.getOutputDoubleValue("y"), myPhysics2.getOutputDoubleValue("y"))
    assert pytest.approx(myPhysics1.getOutputDoubleValue("y"), abs=1.E-4) == 2.5
    assert pytest.approx(myPhysics2.getOutputDoubleValue("y"), abs=1.E-4) == 2.

    print(myPhysics1.getInputValuesNames())
    print(myPhysics1.getOutputValuesNames())
    assert myPhysics1.getInputValuesNames() == ['toto', 'x']
    assert myPhysics1.getOutputValuesNames() == ['tat@y', 'y']

    mycoupler.term()
    myPhysics2.term()
    myPhysics1.term()

    file1.close()
    file2.close()
    file3.close()
    file4.close()
    file5.close()

    def nLines(fileName):
        with open(fileName, "r") as file_:
            n = 0
            for line in file_:
                n += 1
        return n

    Nlines = [nLines("first.log"), nLines("second.log"), nLines("listingFirst.log"), nLines("listingSecond.log"), nLines("listingGeneral.log")]
    print(Nlines)
    assert Nlines == [708, 700, 129, 129, 1230]


def test_sequential():
    main_sequential()
    try:
        os.remove("first.log")
    except:
        pass
    try:
        os.remove("second.log")
    except:
        pass
    try:
        os.remove("listingFirst.log")
    except:
        pass
    try:
        os.remove("listingSecond.log")
    except:
        pass
    try:
        os.remove("listingGeneral.log")
    except:
        pass


if __name__ == "__main__":
    main_sequential()
