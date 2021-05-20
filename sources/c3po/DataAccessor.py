# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class DataAccessor. """
from __future__ import print_function, division


class DataAccessor(object):
    """! DataAccessor is a class interface (to be implemented) which standardizes the accesses to data. It follows the ICOCO standard. """

    def getInputMEDFieldTemplate(self, name):
        """! Get a template of the field expected for a given name.

        This method is useful to know the mesh, discretization… on which an input field is expected.

        @param name string identifying the asked MEDField template.
        @return a ParaMEDMEM::MEDCouplingFieldDouble field.
        """
        raise NotImplementedError

    def setInputMEDField(self, name, field):
        """! Provide the input field corresponding to name.

        After this call, the state of the computation and of the output fields are invalidated.
        It should always be possible to switch consecutive calls to setInputMEDField().
        At least one call to iterateTimeStep() or solveTimeStep() must be performed before getOutputMEDField() or validateTimeStep() can be called.

        @param name string identifying the input field.
        @param field a ParaMEDMEM::MEDCouplingFieldDouble field.
        """
        raise NotImplementedError

    def getOutputMEDField(self, name):
        """! Return the output field corresponding to name.

        @param name string identifying the output field.
        @return a ParaMEDMEM::MEDCouplingFieldDouble field.
        """
        raise NotImplementedError

    def setValue(self, name, value):
        """! Provide the input scalar value corresponding to name.

        @param name string identifying the input scalar.
        @param value a scalar.
        """
        raise NotImplementedError

    def getValue(self, name):
        """! Return the output scalar corresponding to name.

        @param name string identifying the output scalar.
        @return a scalar.
        """
        raise NotImplementedError
