# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the function shiftList. """


def shiftList(listToShift, shiftMap):
    """! Shift in place listToShift according to shiftMap.

    @note Users should not need to call this function directly.

    @param listToShift the list to shift.
    @param shiftMap a list of integers of same length than listToShift. shiftMap[i] is the new position of listToShift[i].
        'out' can be used to indicate that this element is no more used. In this case, the associated element is moved to one of the free positions.

    @return the list of listToShift elements that were associated to 'out' in the shiftMap.

    For example, shiftMap=[3, 'out', 1, 2] indicates that at first call listToShift[0] goes to position 3, listToShift[1] is discharged, listToShift[2] goes to 1 and listToShift[3] goes to 2. It returns [listToShift[1]] (and listToShift[1] goes to position 0).
    At the second call with the same input, listToShift[0] (now at position 3) goes to 2, listToShift[1] (at 0) goes to 3, listToShift[2] (at 1) is discharged and listToShift[3] (at 2) goes to 1. It returns [listToShift[2]].
    The thrid call returns [listToShift[3]], the fourth call [listToShift[0]], the fifth call [listToShift[1]].
    """
    if len(listToShift) != len(shiftMap):
        raise ValueError(f"The length of the shift map {len(shiftMap)} is not equal to the length of the list to shift {len(listToShift)}")
    newList = ["empty"] * len(listToShift)
    removedElems = []
    for i, toShift in enumerate(listToShift):
        if shiftMap[i] == "out":
            removedElems.append(toShift)
        else:
            if newList[shiftMap[i]] != "empty":
                raise ValueError("The shift map appears to contain the same value twice.")
            newList[shiftMap[i]] = toShift
    count = 0
    for i, newElem in enumerate(newList):
        if newElem == "empty":
            newList[i] = removedElems[count]
            count += 1
    listToShift[:] = newList[:]
    return removedElems
