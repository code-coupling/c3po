# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Management of the various versions of MEDCoupling.
Importing this module instead of MEDCoupling directly should allow C3PO to nicely
deal with all possible versions of MEDCoupling.
"""

try:
    # MC version 8 and higher:
    from medcoupling import *   # includes MEDLoader basic API and remapper

    try:
        mcRelease = InterpKernelDEC.release
        MC_VERSION = (9, 7)
    except:
        MC_VERSION = (8, 0)
except:
    # MC version 7
    from MEDLoader import *  # also loads all of MEDCoupling
    from MEDCouplingRemapper import MEDCouplingRemapper

    WriteField = MEDLoader.WriteField
    WriteFieldUsingAlreadyWrittenMesh = MEDLoader.WriteFieldUsingAlreadyWrittenMesh
    WriteUMesh = MEDLoader.WriteUMesh
    WriteMesh = MEDLoader.WriteMesh
    ReadField = MEDLoader.ReadField

    IntensiveConservation = RevIntegral
    IntensiveMaximum = ConservativeVolumic
    ExtensiveConservation = IntegralGlobConstraint
    ExtensiveMaximum = Integral

    DataArray.setContigPartOfSelectedValuesSlice = DataArray.setContigPartOfSelectedValues2

    MC_VERSION = (7, 0)
