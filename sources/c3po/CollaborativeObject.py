# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class CollaborativePhysicsDriver. """
from __future__ import print_function, division


class CollaborativeObject(object):
    """! CollaborativeObject defines the concept of a collaborative object.

    A collaborative object of a certain type is built from a collection of objects of that same type.
    Collaborative actions are obtained by the realization of these same actions by the objects held.
    """

    def __init__(self, elements):
        """! Build an CollaborativeObject object.

        @param elements list of collaborating elements.
        """
        self._elements = elements

    def getElements(self):
        """! Return the elements held.

        @return the list of elements provided to the constructor.
        """
        return self._elements

    def getElementsRecursively(self):
        """! Similar to getElements() but is applied recursively in order to return the full list of elements.

        @return the full list of elements.
        """
        fullList = []
        for elem in self._elements:
            if isinstance(elem, CollaborativeObject):
                fullList += elem.getElementsRecursively()
            else:
                fullList.append(elem)
        return fullList
