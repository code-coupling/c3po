# -*- coding: utf-8 -*-
# This class is the "neutronic" part of the two meshes model.
from __future__ import print_function, division
from math import *
from mpi4py import MPI as mpi

import c3po.medcouplingCompat as mc

import tests.med_Dussaix.MEDBuilder as MEDBuilder
from tests.med_Dussaix.NeutroDriver import NeutroDriver


class MPINeutroDriver(NeutroDriver):
    def __init__(self):
        NeutroDriver.__init__(self)
        self.densities_ = [1.]
        self._mpiComm = None

    def setMPIComm(self, mpicomm):
        self._mpiComm = mpicomm

    def getMPIComm(self):
        return self._mpiComm

    def initialize(self):
        if not self.isInit_:
            if self._mpiComm is not None and self._mpiComm.Get_size() != 2:
                raise Exception("We are waiting for a mpiComm a size 2.")
            self.MEDResu_ = MEDBuilder.makeFieldCarre(self._mpiComm.Get_rank())
            self.MEDTemplate_ = MEDBuilder.makeFieldCarre(self._mpiComm.Get_rank())
            self.MEDTemplate_.setNature(mc.IntensiveMaximum)
            self.isInit_ = True
        return True

    def solveTimeStep(self):
        sumDensities = self._mpiComm.allreduce(self.densities_[0], op=mpi.SUM)
        v = [self.meanT_ * self.densities_[0] / sumDensities + self.meanT_ / 2.]
        array = mc.DataArrayDouble.New()
        array.setValues(v, len(v), 1)
        self.MEDResu_.setArray(array)
        return True
