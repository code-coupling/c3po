# -*- coding: utf-8 -*-
# This class is the "thermohydraulic" part of the two meshes model.
from __future__ import print_function, division
from math import *
import numpy

import c3po.medcouplingCompat as mc

import tests.med_Dussaix.MEDBuilder as MEDBuilder
from c3po.PhysicsDriver import PhysicsDriver

Tsat = 1173.
Pression = 1.5E5
Hvsat = 5401.99E3


def rhol(T):
    return 1. / (9.829728E-4 + T * (2.641186E-7 + T * (-3.340743E-11 + T * 6.680973E-14)))


def rhov(P):
    return P * 22.98977 * (2.49121 / Tsat - 5.53796E-3 + Tsat * (7.5465E-6 + Tsat * (-4.20217E-9 + Tsat * 8.59212E-13))) / 8314.47


def enthalpie(T):
    return 2992600. / T - 365770. + T * (1658.2 + T * (-.42395 + T * 1.4847E-4))


Hlsat = enthalpie(Tsat)


class ThermoDriver(PhysicsDriver):
    def __init__(self):
        PhysicsDriver.__init__(self)
        self.T_ = [1., 1.]
        self.MEDResu_ = 0
        self.Vv_Vl_ = 1.
        self.isInit_ = False
        self._stationaryMode = False

    # Initialize the object.
    def initialize(self):
        if not self.isInit_:
            self.MEDResu_ = MEDBuilder.makeFieldHexa()
            self.isInit_ = True
        return True

    def terminate(self):
        pass

    def initTimeStep(self, dt):
        return True

    def solveTimeStep(self):
        T1 = self.T_[0]
        T2 = self.T_[1]
        X1 = (enthalpie(T1) - Hlsat) / (Hvsat - Hlsat)
        X2 = (enthalpie(T2) - Hlsat) / (Hvsat - Hlsat)
        alpha1 = 0.
        alpha2 = 0.
        rhov1 = rhov(Pression)
        rhov2 = rhov(Pression)
        if X1 > 0.:
            T1 = Tsat
        if X2 > 0.:
            T2 = Tsat
        rhol1 = rhol(T1)
        rhol2 = rhol(T2)
        if X1 > 0.:
            alpha1 = X1 / (X1 + (1. - X1) * rhov1 / rhol1 * self.Vv_Vl_)
            if alpha1 > 1.:
                alpha1 = 1.
        if X2 > 0.:
            alpha2 = X2 / (X2 + (1. - X2) * rhov2 / rhol2 * self.Vv_Vl_)
            if alpha2 > 1.:
                alpha2 = 1.
        v = [alpha1 * rhov1 + (1. - alpha1) * rhol1, alpha2 * rhov2 + (1. - alpha2) * rhol2]
        array = mc.DataArrayDouble.New()
        array.setValues(v, len(v), 1)
        self.MEDResu_.setArray(array)
        return True

    def setStationaryMode(self, stationaryMode):
        self._stationaryMode = stationaryMode

    def getStationaryMode(self):
        return self._stationaryMode

    def validateTimeStep(self):
        pass

    def abortTimeStep(self):
        pass

    def getOutputMEDDoubleField(self, name):
        if name == "Densities":
            resu = self.MEDResu_
            try:
                resu.setMesh(self.MEDResu_.getMesh().deepCopy())
            except:
                resu.setMesh(self.MEDResu_.getMesh().deepCpy())
            return resu
        else:
            raise Exception("ThermoDriver.getOutputMEDDoubleField Only Densities output available.")

    def updateOutputMEDDoubleField(self, name, field):
        if name == "Densities":
            field.setArray(self.MEDResu_.getArray())
        else:
            raise Exception("ThermoDriver.updateOutputMEDDoubleField Only Densities output available.")

    def setInputMEDDoubleField(self, name, field):
        if name == "Temperatures":
            array = field.getArray()
            self.T_[0] = array.getIJ(0, 0)
            self.T_[1] = array.getIJ(1, 0)

    def getInputMEDDoubleFieldTemplate(self, name):
        return self.MEDResu_

    def setInputDoubleValue(self, name, value):
        if name == "Vv_Vl":
            self.Vv_Vl_ = value
