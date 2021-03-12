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
#from enum import *

# class AutoNumber(IntEnum):
# def __new__(cls):
#value = len(cls.__members__) + 1
#obj = object.__new__(cls)
#obj._value_ = value
# return obj


class MPITag(object):
    """! INTERNAL

    MPITag defines tags used in MPI communications.
    """
    answer = 0
    data = 1

    init = 2
    getInitStatus = 3
    terminate = 4
    presentTime = 5
    computeTimeStep = 6
    initTimeStep = 7
    solve = 8
    getSolveStatus = 9
    validateTimeStep = 10
    abortTimeStep = 11
    isStationary = 12
    iterate = 13
    getIterateStatus = 14
    save = 15
    restore = 16
    forget = 17
    getInputFieldsNames = 18
    getInputMEDFieldTemplate = 19
    setInputMEDField = 20
    getOutputFieldsNames = 21
    getOutputMEDField = 22
    getInputValuesNames = 23
    setValue = 24
    getOutputValuesNames = 25
    getValue = 26

    deleteDataManager = 27
    cloneEmptyData = 28
    copyData = 29
    normMax = 30
    norm2 = 31
    addData = 32
    iaddData = 33
    subData = 34
    isubData = 35
    mulData = 36
    imulData = 37
    imuladdData = 38
    dotData = 39

    exchange = 40
