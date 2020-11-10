# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contains the class SharedRemapping.
"""
from __future__ import print_function, division

from MEDCouplingRemapper import MEDCouplingRemapper


class Remapper(MEDCouplingRemapper):
    """ Allows to share the mesh projection for different SharedRemapping objects by building them with the same instance of this class. """

    def __init__(self):
        MEDCouplingRemapper.__init__(self)
        self.isInit_ = False

    def initialize(self, sourceMesh, targetMesh, meshAlignment, offset):
        if meshAlignment:
            for mesh in [sourceMesh, targetMesh]:
                [(xmin, xmax), (ymin, ymax), (zmin, _)] = mesh.getBoundingBox()
                offsettmp = [-0.5 * (xmin + xmax), -0.5 * (ymin + ymax), -zmin]
                mesh.translate(offsettmp)
        if offset != [0., 0., 0.]:
            sourceMesh.translate([-x for x in offset])
        self.prepare(sourceMesh, targetMesh, "P0P0")
        self.isInit_ = True


class SharedRemapping(object):
    """ The __call__ method of this class projects the input fields one by one before returning them as outputs, in the same order.

    The method assumes that all input fields have the same mesh, and produces output fields on identical meshes.
    This output mesh is the one of the first field passed to the method (obtained by getInputMEDFieldTemplate).

    The input scalars are returned in the same order, without modification.

    The initialization of the projection method (long operation) is done only once, and can be shared with other instances of SharedRemapping.
    """

    def __init__(self, remapper, reverse=False, defaultValue=0., linearTransform=(1., 0.), meshAlignment=False, offset=[0., 0., 0.]):
        """ Builds an SharedRemapping object, to be given to an Exchanger object.

        :param remapper: A Remapper object (defined in C3PO and inheriting from MEDCouplingRemapper) performing the projection. It can thus be shared with other instances of SharedRemapping (its initialization will always be done only once).
        :param reverse: Allows the Remapper to be shared with an instance of SharedRemapping performing the reverse exchange (the projection will be done in the reverse direction if reverse is set to True).
        :param defaultValue: This is the default value to be assigned, during the projection, in the meshes of the target mesh which are not intersected by the source mesh.
        :param linearTransform: Tuple (a,b): apply a linear function to all output fields f such as they become a * f + b. The transformation is applied after the mesh projection.
        :param meshAlignment: If set to True, at the initialization phase of the Remapper object, meshes are translated such as their "bounding box" are radially centred on (x = 0., y = 0.) and have zmin = 0.
        :param offset: Value of the 3D offset between the source and the target meshes (>0 on z means that the source mesh is above the target one). The given vector is used to translate the source mesh (after the mesh alignment, if any).
        """
        self.remapper_ = remapper
        self.isReverse_ = reverse
        self.defaultValue_ = defaultValue
        self.linearTransform_ = linearTransform
        self.meshAlignment_ = meshAlignment
        self.offset_ = offset

    def initialize(self, fieldsToGet, fieldsToSet, valuesToGet):
        if not self.remapper_.isInit_:
            if self.isReverse_:
                self.remapper_.initialize(fieldsToSet[0].getMesh(), fieldsToGet[0].getMesh(), self.meshAlignment_, [-x for x in self.offset_])
            else:
                self.remapper_.initialize(fieldsToGet[0].getMesh(), fieldsToSet[0].getMesh(), self.meshAlignment_, self.offset_)

    def __call__(self, fieldsToGet, fieldsToSet, valuesToGet):
        if len(fieldsToSet) != len(fieldsToGet):
            raise Exception("sharedRemapping : there must be the same number of input and output MED fields")

        self.initialize(fieldsToGet, fieldsToSet, valuesToGet)
        TransformedMED = []
        for i in range(len(fieldsToSet)):
            if self.isReverse_:
                TransformedMED.append(self.remapper_.reverseTransferField(fieldsToGet[i], self.defaultValue_))
            else:
                TransformedMED.append(self.remapper_.transferField(fieldsToGet[i], self.defaultValue_))
        if self.linearTransform_ != (1., 0.):
            for med in TransformedMED:
                med.applyLin(*(self.linearTransform_))
        return TransformedMED, valuesToGet