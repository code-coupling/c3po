# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Import user non-MPI C3PO objects. """

import os
with open(os.path.join(os.path.dirname(__file__), "VERSION")) as file:
    __version__ = file.read().strip()

from .DataAccessor import DataAccessor
from .PhysicsDriver import PhysicsDriver
from .Exchanger import Exchanger
from .LocalExchanger import LocalExchanger
from .CollaborativeExchanger import CollaborativeExchanger
from .DataManager import DataManager
from .LocalDataManager import LocalDataManager
from .CollaborativeDataManager import CollaborativeDataManager
from .Coupler import Coupler, NormChoice
from .TimeAccumulator import TimeAccumulator
from .services.tracer import tracer
from .services.nameChanger import nameChanger
from .services.ListingWriter import ListingWriter, mergeListing, getTotalTimePhysicsDriver, getTimesExchanger
from .couplers.FixedPointCoupler import FixedPointCoupler
from .couplers.AndersonCoupler import AndersonCoupler
from .couplers.JFNKCoupler import JFNKCoupler
from .exchangeMethods.ExchangeMethod import ExchangeMethod
from .exchangeMethods.DirectMatching import DirectMatching
from .exchangeMethods.SharedRemapping import SharedRemapping, Remapper
from .exchangeMethods.SharedRemappingMulti1D3D import SharedRemappingMulti1D3D, Multi1D3DRemapper
