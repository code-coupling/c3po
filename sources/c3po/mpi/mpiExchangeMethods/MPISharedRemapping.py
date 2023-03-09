# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class SharedRemapping. """
from __future__ import print_function, division
from mpi4py import MPI as mpi
import os

import c3po.medcouplingCompat as mc
from c3po.mpi.mpiExchangeMethods.MPIExchangeMethod import MPIExchangeMethod


class MPIRemapper(object):
    """! Allow to share the mesh projection for different MPISharedRemapping objects by building them with the same instance of this class. """

    def __init__(self, meshAlignment=False, offset=[0., 0., 0.], rescaling=1., rotation=0., outsideCellsScreening=False):
        """! Build a MPIRemapper object.

        @warning It is mandatory to call the terminate() method after use, otherwise MPI may be badly ended.

        @param meshAlignment If set to True, at the initialization phase of the MPIRemapper object, meshes are translated such as their "bounding
            box" are radially centred on (x = 0., y = 0.) and have zmin = 0.
        @param offset Value of the 3D offset between the source and the target meshes (>0 on z means that the source mesh is above the target one).
            The given vector is used to translate the source mesh (after the mesh alignment, if any).
        @param rescaling Value of a rescaling factor to be applied between the source and the target meshes (>1 means that the source mesh is
            initially larger than the target one). The scaling is centered on [0., 0., 0.] and is applied to the source mesh after mesh
            alignment or translation, if any.
        @param rotation Value of the rotation between the source and the target meshes. The rotation is centered on [0., 0., 0.] and is about
            the vertical axis. >0 means that the source mesh is rotated of the given angle compared to the target one. The inverse rotation is
            applied to the source mesh, after mesh alignment or translation, if any. pi means half turn.
        @param outsideCellsScreening If set to True, target (and source) cells whose barycentre is outside of source (or target) mesh are screen
            out (defaultValue is assigned to them). It can be useful to screen out cells that are in contact with the other mesh, but that should
            not be intersected by it. On the other hand, it will screen out cells actually intersected if their barycenter is outside of the other
            mesh ! Be careful with this option.

        @warning The option outsideCellsScreening is not ready to use yet.
        """
        self.isInit = False
        self.isInitPerNature = {}
        self._meshAlignment = meshAlignment
        self._offset = offset
        if rescaling <= 0.:
            raise ValueError("MPIRemapper: rescaling must be > 0!")
        self._rescaling = rescaling
        self._rotation = rotation
        if outsideCellsScreening:
            raise ValueError("MPIRemapper: The option outsideCellsScreening is not ready to use yet.")
        self._interpKernelDECs = {}

    def initialize(self, ranksToGet, ranksToSet, mpiComm, field):
        """! INTERNAL """
        if not self.isInit:
            self.terminate()

        if len(set(ranksToSet) - set(ranksToGet)) != len(ranksToSet):
            raise Exception("MPIRemapper.initialize: there must not be ranks present in both lists of ranks (to get and to set).")
        if min(min(ranksToGet), min(ranksToSet)) !=0 and max(max(ranksToGet), max(ranksToSet)) != mpiComm.Get_size() - 1:
            raise Exception("MPIRemapper.initialize: ranks must be between 0 and {} (included). We found a min value of {} and a max value of {}.".format(mpiComm.Get_size() - 1, min(min(ranksToGet), min(ranksToSet)), max(max(ranksToGet), max(ranksToSet))))
        if len(ranksToGet) + len(ranksToSet) != mpiComm.Get_size():
            raise Exception("MPIRemapper.initialize: the provided list of ranks must be a partitioned of the MPI communicator. Here we have {} and {} ranks while the size of the communicator is {}.".format(len(ranksToGet), len(ranksToSet), mpiComm.Get_size()))

        if self._meshAlignment:
            localComm = mpiComm.Split(mpiComm.Get_rank() in ranksToGet)
            [(xmin, xmax), (ymin, ymax), (zmin, _)] = field.getMesh().getBoundingBox()
            xmin = localComm.allreduce(xmin, op=mpi.MIN)
            xmax = localComm.allreduce(xmax, op=mpi.MAX)
            ymin = localComm.allreduce(ymin, op=mpi.MIN)
            ymax = localComm.allreduce(ymax, op=mpi.MAX)
            zmin = localComm.allreduce(zmin, op=mpi.MIN)
            offsettmp = [-0.5 * (xmin + xmax), -0.5 * (ymin + ymax), -zmin]
            field.getMesh().translate(offsettmp)
        if self._offset != [0., 0., 0.] and mpiComm.Get_rank() in ranksToGet:
            field.getMesh().translate([-x for x in self._offset])
        if self._rescaling != 1. and mpiComm.Get_rank() in ranksToGet:
            field.getMesh().scale([0., 0., 0.], 1. / self._rescaling)
        if self._rotation != 0. and mpiComm.Get_rank() in ranksToGet:
            field.getMesh().rotate([0., 0., 0.], [0., 0., 1.], self._rotation)

        nature = field.getNature()
        if mpiComm == mpi.COMM_WORLD:
            self._interpKernelDECs[nature] = mc.InterpKernelDEC(ranksToGet, ranksToSet)
        else:
            self._interpKernelDECs[nature] = mc.InterpKernelDEC(ranksToGet, ranksToSet, mpiComm)
        self._interpKernelDECs[nature].setMethod("P0")
        self._interpKernelDECs[nature].attachLocalField(field)
        self._interpKernelDECs[nature].synchronize()

        self.isInit = True
        self.isInitPerNature[nature] = True

    def terminate(self):
        for dec in self._interpKernelDECs.values():
            dec.release()
        self._interpKernelDECs = {}
        self.isInitPerNature = {}
        self.isInit = False

    def recvField(self, fieldTemplate):
        """! INTERNAL """
        nature = fieldTemplate.getNature()
        self._interpKernelDECs[nature].attachLocalField(fieldTemplate)
        self._interpKernelDECs[nature].recvData()
        return fieldTemplate

    def sendField(self, field):
        """! INTERNAL """
        nature = field.getNature()
        self._interpKernelDECs[nature].attachLocalField(field)
        self._interpKernelDECs[nature].sendData()


class MPISharedRemapping(MPIExchangeMethod):
    """! MPISharedRemapping is an MPIExchangeMethod which projects the input fields one by one before returning them as outputs,
    in the same order.

    See c3po.Exchanger.Exchanger.__init__().

    The method assumes that all input fields have the same mesh, and produces output fields on identical meshes.

    This output mesh is the one of the first field passed to the method (obtained by getInputMEDFieldTemplate).

    The input scalars are returned in the same order, without modification.

    The initialization of the projection method (long operation) is done only once, and can be shared with other instances of
    MPISharedRemapping through a MPIRemapper object.
    """

    def __init__(self, remapper, reverse=False, defaultValue=0., linearTransform=(1., 0.)):
        """! Build an MPISharedRemapping object, to be given to an Exchanger.

        @param remapper A MPIRemapper object (defined in C3PO and inheriting from MEDCouplingRemapper) performing the projection. It
               can thus be shared with other instances of MPISharedRemapping (its initialization will always be done only once).
        @param reverse Allows the MPIRemapper to be shared with an instance of MPISharedRemapping performing the reverse exchange (the projection
               will be done in the reverse direction if reverse is set to True).
        @param defaultValue This is the default value to be assigned, during the projection, in the meshes of the target mesh that are not
               intersected by the source mesh.
        @param linearTransform Tuple (a,b): apply a linear function to all output fields f such as they become a * f + b. The transformation
               is applied after the mesh projection.

        @warning at the present time, defaultValue has to be 0.
        """
        self._remapper = remapper
        self._defaultValue = 0.
        if defaultValue != 0.:
            raise ValueError("MPISharedRemapping: At the present time, it is not possible to use a defaultValue different from 0 ({} was provided).".format(defaultValue))
        self._isReverse = reverse
        self._linearTransform = linearTransform
        self._ranksToGet = []
        self._ranksToSet = []
        self._mpiComm = None

    def setRanks(self, ranksToGet, ranksToSet, mpiComm):
        """! See MPIExchangeMethod.setRanks. """
        self._ranksToGet[:] = ranksToSet[:] if self._isReverse else ranksToGet[:]
        self._ranksToSet[:] = ranksToGet[:] if self._isReverse else ranksToSet[:]
        self._mpiComm = mpiComm

    def initialize(self, field):
        """! INTERNAL """
        localNature = field.getNature()
        minNature = self._mpiComm.allreduce(localNature, op=mpi.MIN)
        maxNature = self._mpiComm.allreduce(localNature, op=mpi.MAX)
        if minNature != maxNature:
            raise Exception("MPISharedRemapping.initialize: All fields involved in the same exchange must share the same nature. We found at least two: {} and {}.".format(minNature, maxNature))

        if not self._remapper.isInit or localNature not in self._remapper.isInitPerNature or not self._remapper.isInitPerNature[localNature]:
            if len(self._ranksToGet) == 0:
                raise Exception("MPISharedRemapping: setRanks() must be call before the first exchange.")
            self._remapper.initialize(self._ranksToGet, self._ranksToSet, self._mpiComm, field)

    def __call__(self, fieldsToGet, fieldsToSet, valuesToGet):
        """! Project the input fields one by one before returning them as outputs, in the same order. """
        if len(valuesToGet) != 0:
            raise Exception("MPISharedRemapping: we cannot deal with scalar values.")

        transformedMED = []

        if len(fieldsToSet) > 0 or len(fieldsToGet) > 0:
            for field in fieldsToGet + fieldsToSet:
                self.initialize(field)
            for field in fieldsToGet:
                self._remapper.sendField(field)
            for field in fieldsToSet:
                transformedMED.append(self._remapper.recvField(field))
            if self._linearTransform != (1., 0.):
                for med in transformedMED:
                    med.applyLin(*(self._linearTransform))

        return transformedMED, []

    def getPatterns(self):
        """! See ExchangeMethod.getPatterns. """
        return [(1, 0, 0, 0), (0, 1, 0, 0)]
