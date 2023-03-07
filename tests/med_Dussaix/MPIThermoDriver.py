# -*- coding: utf-8 -*-
# This class is the "thermohydraulic" part of the two meshes model.
from __future__ import print_function, division

import c3po.medcouplingCompat as mc

import tests.med_Dussaix.MEDBuilder as MEDBuilder
from tests.med_Dussaix.ThermoDriver import ThermoDriver


class MPIThermoDriver(ThermoDriver):
    def __init__(self):
        ThermoDriver.__init__(self)
        self.T_ = [1.]
        self._mpiComm = None

    def setMPIComm(self, mpicomm):
        self._mpiComm = mpicomm

    def getMPIComm(self):
        return self._mpiComm

    # Initialize the object.
    def initialize(self):
        if not self.isInit_:
            if self._mpiComm is not None and self._mpiComm.Get_size() != 2:
                raise Exception("We are waiting for a mpiComm a size 2.")
            self.MEDResu_ = MEDBuilder.makeFieldHexa(self._mpiComm.Get_rank())
            self.isInit_ = True
        return True
