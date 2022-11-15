# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class MPITag. """
from __future__ import print_function, division


class MPITag(object):
    """! INTERNAL

    MPITag defines tags used in MPI communications.
    """
    answer = 0
    data = 1

    setDataFile = 2
    init = 3
    getInitStatus = 4
    terminate = 5
    presentTime = 6
    computeTimeStep = 7
    initTimeStep = 8
    solve = 9
    getSolveStatus = 10
    validateTimeStep = 11
    setStationaryMode = 12
    getStationaryMode = 13
    abortTimeStep = 14
    isStationary = 15
    resetTime = 16
    iterate = 17
    getIterateStatus = 18
    save = 19
    restore = 20
    forget = 21
    setInputDoubleValue = 22
    setInputIntValue = 23
    setInputStringValue = 24

    tagBARRIER = 100

    deleteDataManager = 101
    cloneEmptyData = 102
    copyData = 103
    normMax = 104
    norm2 = 105
    addData = 106
    iaddData = 107
    subData = 108
    isubData = 109
    mulData = 110
    imulData = 111
    imuladdData = 112
    dotData = 113

    exchange = 150
