# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class ListingWriter. """
from __future__ import print_function, division
import os


def getFormattedTime(timeValue):
    """! INTERNAL """
    timeToWrite = ""
    if timeValue > 1.:
        timeToWrite = "{:.4f}".format(timeValue)
    else:
        timeToWrite = "{:.4e}".format(timeValue)
    return timeToWrite


class ListingWriter(object):
    """! ListingWriter allows, in association with c3po.services.tracer.tracer, to write a global coupling listing file with calculation time measurement.

    ListingWriter is completed by the funtions mergeListing(), getTotalTimePhysicsDriver() and getTimesExchanger().
    """

    enumTop = 0
    enumEntete = 1
    enumCloseTop = 2
    enumBilan = 3
    enumTerm = 4
    enumInterrupt = 5
    enumContinue = 6

    def __init__(self, listingFile):
        """! Build a ListingWriter object.

        @param listingFile a file object which has to be already open in written-binary mode (file = open("file.txt", "wb")). It has to
        be closed (file.close()) by caller.
        """
        self._listingFile = listingFile
        self._autoFormat = True
        self._isPrepared = False
        self._isBoxOpen = False
        self._physics = []
        self._physicsData = []
        self._physicsToBeAdded = []
        self._nameOfPhysicsToBeAdded = []
        self._exchangers = []
        self._exchangersData = []
        self._timeInit = 0.
        self._timeValid = 0.
        self._charPerLine = 0
        self._sumCalculationTime = 0.
        self._timeValidatedPhysics = []
        self._terminatedPhysics = []
        self._boxFormat = [""] * 7

    def initialize(self, physics, exchangers, force=False):
        """! Clear and initialize the object.

        Can be replace by a call to terminate() (optional for the first call) followed by calls to setPhysicsDriverName() and setExchangerName().

        setPhysicsDriverName() and setExchangerName() can also be used after initialize(), but not before (what is set before is forgotten).

        @param physics a list of tuples (object, name). object should be a PhysicsDriver, modified with c3po.services.tracer.tracer to point on this ListingWriter object.
            An object that does not meet these conditions is ignored. A column (entitled with name) is created in the listing file for each of them.
        @param exchangers a list of tuples (object, name). object should be an Exchanger object, modified with c3po.services.tracer.tracer to point on this ListingWriter
            object. An object that does not meet these conditions is ignored. name allows to identify them in the final listing file.
        @param force if set to True, physics and exchangers are added even if they do not meet the previously defined conditions.
        """
        self.terminate()
        for phy in physics:
            self.setPhysicsDriverName(phy[0], phy[1], force)
        for exc in exchangers:
            self.setExchangerName(exc[0], exc[1], force)

    def terminate(self):
        """! Get ready to write a new listing.

        What was previously set by initialize(), setPhysicsDriverName() and setExchangerName() is forgotten.
        """
        if self._isBoxOpen:
            self.writeTerminate()
        self._physics = []
        self._physicsData = []
        self._exchangers = []
        self._exchangersData = []
        self._isPrepared = False

    def setPhysicsDriverName(self, physics, name, force=False):
        """! Get ready to write a listing with the provided PhysicsDriver.

        @param physics a PhysicsDriver object, modified with c3po.services.tracer.tracer to point on this ListingWriter object.
            If physics does not meet these conditions, it is ignored. Otherwise, a column (entitled with name) will be created in the listing file for it.
        @param name the name to use for physics in the listing.
        @param force if set to True, physics is added even if it does not meet the previously defined conditions.
        """
        if force or (hasattr(physics, "static_lWriter") and physics.static_lWriter is self):
            if self._isPrepared:
                self._physicsToBeAdded.append(physics)
                self._nameOfPhysicsToBeAdded.append(name)
            else:
                self._physics.append(physics)
                self._physicsData.append([name, u""])  # (name, format)

    def setExchangerName(self, exchanger, name, force=False):
        """! Get ready to write a listing with the provided Exchanger.

        @param exchanger a Exchanger object, modified with c3po.services.tracer.tracer to point on this ListingWriter object.
            If exchanger does not meet these conditions, it is ignored. Otherwise, a lign will be written in the listing for each call of exchanger's exchange() method .
        @param name the name to use for exchanger in the listing.
        @param force if set to True, exchanger is added even if it does not meet the previously defined conditions.
        """
        if force or (hasattr(exchanger, "static_lWriter") and exchanger.static_lWriter is self):
            self._exchangers.append(exchanger)
            self._exchangersData.append([name, u""])  # (name, format)
            if self._isPrepared:
                self._defineExchangerFormat(self._exchangersData[-1])

    def prepare(self):
        """! INTERNAL """
        self._timeInit = 0.
        self._timeValid = 0.
        self._charPerLine = 0
        self._sumCalculationTime = 0.
        self._timeValidatedPhysics = [-1. for _ in self._physics]
        self._terminatedPhysics = [False for _ in self._physics]
        self._defineFormats()
        self._isPrepared = True

    def _defineFormats(self):
        """! INTERNAL """
        self._boxFormat = [""] * 7
        for phy in self._physicsData:
            phy[1] = u"┃{:^28}│"
        self._boxFormat[ListingWriter.enumTop] += u"┏{}┯".format(u"━" * 28)
        self._boxFormat[ListingWriter.enumEntete] += u"┃{:^28}│".format(u"In / Out")
        self._boxFormat[ListingWriter.enumCloseTop] += u"┠{}┼".format(u"─" * 28)
        self._boxFormat[ListingWriter.enumBilan] += u"┃{:^28}│".format(u"Time step complete")
        self._boxFormat[ListingWriter.enumTerm] += u"┗{}┷".format(u"━" * 28)
        self._boxFormat[ListingWriter.enumInterrupt] += u"┠{}┼".format(u"─" * 28)
        self._boxFormat[ListingWriter.enumContinue] += u"┠{}┼".format(u"─" * 28)
        for i, ph1 in enumerate(self._physicsData):
            for j in range(len(self._physicsData)):
                if i == j:
                    ph1[1] += u"{:^23}│"
                else:
                    ph1[1] += u"                       │"
            self._boxFormat[ListingWriter.enumTop] += u"━━━━━━━━━━━━━━━━━━━━━━━┯"
            self._boxFormat[ListingWriter.enumEntete] += u"{:^23.23}│"
            self._boxFormat[ListingWriter.enumCloseTop] += u"───────────────────────┼"
            self._boxFormat[ListingWriter.enumTerm] += u"━━━━━━━━━━━━━━━━━━━━━━━┷"
            self._boxFormat[ListingWriter.enumInterrupt] += u"───────────────────────" + (u"┴" if i != (len(self._physicsData) - 1) else u"┼")
            self._boxFormat[ListingWriter.enumContinue] += u"───────────────────────" + (u"┬" if i != (len(self._physicsData) - 1) else u"┼")

        decalage = (23 + 1) * len(self._physicsData) - 1
        self._boxFormat[ListingWriter.enumBilan] += u"{:^" + str(decalage) + u"}│"

        for phy in self._physicsData:
            phy[1] += u"{:^12}│"
        self._boxFormat[ListingWriter.enumTop] += u"━━━━━━━━━━━━┯"
        self._boxFormat[ListingWriter.enumEntete] += u"    time    │"
        self._boxFormat[ListingWriter.enumCloseTop] += u"────────────┼"
        self._boxFormat[ListingWriter.enumBilan] += u"{:^12}│"
        self._boxFormat[ListingWriter.enumTerm] += u"━━━━━━━━━━━━┷"
        self._boxFormat[ListingWriter.enumInterrupt] += u"────────────┼"
        self._boxFormat[ListingWriter.enumContinue] += u"────────────┼"

        for phy in self._physicsData:
            phy[1] += u"{:^12}┃\n"
        self._boxFormat[ListingWriter.enumTop] += u"━━━━━━━━━━━━┓ Reference time = {:}\n"
        self._boxFormat[ListingWriter.enumEntete] += u"     dt     ┃\n"
        self._boxFormat[ListingWriter.enumCloseTop] += u"────────────┨\n"
        self._boxFormat[ListingWriter.enumBilan] += u"{:^12}┃\n"
        self._boxFormat[ListingWriter.enumTerm] += u"━━━━━━━━━━━━┛\n"
        self._boxFormat[ListingWriter.enumInterrupt] += u"────────────┨\n"
        self._boxFormat[ListingWriter.enumContinue] += u"────────────┨\n"

        for exc in self._exchangersData:
            self._defineExchangerFormat(exc)

        self._charPerLine = len(self._boxFormat[ListingWriter.enumTop].encode('utf-8'))

    def _defineExchangerFormat(self, exc):
        """! INTERNAL """
        exc[1] = u"┃{0:^28.28}│"
        for _ in self._physicsData:
            exc[1] += u"{1:-^23}│"
        exc[1] += u"{2:^12}│"
        exc[1] += u"{3:^12}┃\n"

    def writeInitialize(self, presentTime):
        """! INTERNAL """
        self._listingFile.write(self._boxFormat[ListingWriter.enumTop].format("{:10.6f}".format(presentTime)).encode('utf-8'))
        physicsName = [phy[0] for phy in self._physicsData]
        self._listingFile.write(self._boxFormat[ListingWriter.enumEntete].format(*physicsName).encode('utf-8'))
        self._listingFile.write(self._boxFormat[ListingWriter.enumCloseTop].encode('utf-8'))
        self._timeInit = presentTime
        self._timeValid = presentTime
        self._listingFile.flush()
        self._isBoxOpen = True

    def writeValidate(self, timeValid):
        """! INTERNAL """
        timeToWrite = getFormattedTime(timeValid - self._timeInit)
        calculationTimeToWrite = getFormattedTime(timeValid - self._timeValid)
        sumCalculationTimeToWrite = getFormattedTime(self._sumCalculationTime)

        self._listingFile.write(self._boxFormat[ListingWriter.enumInterrupt].encode('utf-8'))
        self._listingFile.write(self._boxFormat[ListingWriter.enumBilan].format("SpentTime " + calculationTimeToWrite, timeToWrite,
                                                                                sumCalculationTimeToWrite).encode('utf-8'))
        self._listingFile.write(self._boxFormat[ListingWriter.enumContinue].encode('utf-8'))

        self._timeValid = timeValid
        self._sumCalculationTime = 0.
        for i in range(len(self._timeValidatedPhysics)):
            self._timeValidatedPhysics[i] = -1.

    def writeTerminate(self):
        """! INTERNAL """
        self._listingFile.write(self._boxFormat[ListingWriter.enumTerm].encode('utf-8'))

        for i in range(len(self._terminatedPhysics)):
            self._terminatedPhysics[i] = False

        self._isBoxOpen = False

    def writeAfter(self, sourceObject, inputVar, outputTuple, methodName, presentTime, calculationTime):
        """! INTERNAL """
        if sourceObject in self._physicsToBeAdded:
            index = self._physicsToBeAdded.index(sourceObject)
            self._addPhysicsDriver(self._nameOfPhysicsToBeAdded[index], (sourceObject, inputVar, outputTuple, methodName, presentTime, calculationTime))
            self._physicsToBeAdded.pop(index)
            self._nameOfPhysicsToBeAdded.pop(index)
            return
        if not self._isPrepared:
            self.prepare()
        if self._autoFormat and not self._isBoxOpen:
            self.writeInitialize(presentTime)

        presentTimeToWrite = getFormattedTime(presentTime - self._timeInit)
        calculationTimeToWrite = getFormattedTime(calculationTime)

        if sourceObject in self._physics:
            self._sumCalculationTime += calculationTime

            ind = self._physics.index(sourceObject)
            toWrite = ""
            if methodName == "computeTimeStep":
                toWrite += "dt = "
                if outputTuple[0] > 1e2 or outputTuple[0] < 0.1:
                    toWrite += "{:.4e}".format(outputTuple[0])
                else:
                    toWrite += "{:.4f}".format(outputTuple[0])
                toWrite += ", stop = " + ("yes" if outputTuple[1] else "no")
            elif methodName == "initTimeStep":
                toWrite += "dt = "
                if inputVar > 1e2 or inputVar < 0.1:
                    toWrite += "{:.4e}".format(inputVar)
                else:
                    toWrite += "{:.4f}".format(inputVar)
                toWrite += ", ok = " + ("yes" if outputTuple else "no")
            elif methodName in ["solveTimeStep", "initialize"]:
                toWrite += "succeed = " + ("yes" if outputTuple else "no")
            elif methodName == "terminate":
                self._terminatedPhysics[self._physics.index(sourceObject)] = True
            elif methodName == "iterateTimeStep":
                toWrite += "succeed = " + ("yes" if outputTuple[0] else "no")
                toWrite += ", cv. = " + ("yes" if outputTuple[1] else "no")
            elif methodName == "validateTimeStep":
                objectPresentTime = sourceObject.presentTime()
                toWrite += "time = " + "{:.4f}".format(objectPresentTime)
                self._timeValidatedPhysics[self._physics.index(sourceObject)] = objectPresentTime
            elif methodName == "setStationaryMode":
                toWrite += "mode = " + ("stationary" if inputVar else "transient")
            elif methodName == "resetTime":
                toWrite += "time = "
                if inputVar > 1e2 or inputVar < 0.1:
                    toWrite += "{:.4e}".format(inputVar)
                else:
                    toWrite += "{:.4f}".format(inputVar)
                self._timeValidatedPhysics[self._physics.index(sourceObject)] = -1.
            elif methodName in ["save", "restore"]:
                toWrite += inputVar

            self._listingFile.write(self._physicsData[ind][1].format(toWrite, methodName, presentTimeToWrite,
                                                                     calculationTimeToWrite).encode('utf-8'))

        if sourceObject in self._exchangers:
            self._sumCalculationTime += calculationTime
            ind = self._exchangers.index(sourceObject)
            self._listingFile.write(self._exchangersData[ind][1].format(self._exchangersData[ind][0], methodName, presentTimeToWrite,
                                                                        calculationTimeToWrite).encode('utf-8'))

        if self._autoFormat and len(self._timeValidatedPhysics) > 0:
            minTValid = min(self._timeValidatedPhysics)
            if minTValid > 0.:
                if (max(self._timeValidatedPhysics) - minTValid) < 1.E-8:
                    self.writeValidate(presentTime + calculationTime)
        if self._autoFormat and len(self._terminatedPhysics) > 0 and min(self._terminatedPhysics):
            self.writeTerminate()

        self._listingFile.flush()

    def _addPhysicsDriver(self, name, writeArgs):
        """! INTERNAL """
        listingDir = os.path.dirname(self._listingFile.name)
        tmpFile1 = os.path.join(listingDir, "tmp_c3po_listing_1.txt")
        tmpFile2 = os.path.join(listingDir, "tmp_c3po_listing_2.txt")
        try:
            with open(tmpFile1, "wb") as filetmp:
                dummyWriter = ListingWriter(filetmp)
                dummyWriter.setPhysicsDriverName(writeArgs[0], name, force=True)
                dummyWriter.writeAfter(*writeArgs)
            mergeListing([self._listingFile.name, tmpFile1], tmpFile2)
            position = 0
            with open(self._listingFile.name, "r") as listingFile:
                goToLastBox(listingFile)
                position = listingFile.tell()
            with open(tmpFile2, "rb") as toCopy:
                self._listingFile.seek(position, 0)
                for line in toCopy:
                    self._listingFile.write(line)
            self._isPrepared = False
            self.setPhysicsDriverName(writeArgs[0], name)
            self._timeValidatedPhysics.append(-1)
            self._terminatedPhysics.append(False)
            self._defineFormats()
            self._listingFile.seek(-len(self._boxFormat[ListingWriter.enumTerm].encode('utf-8')), 2)
            self._listingFile.truncate()
        finally:
            self._isPrepared = True
            try:
                os.remove(tmpFile1)
            except:
                pass
            try:
                os.remove(tmpFile2)
            except:
                pass


class MergedListingWriter(ListingWriter):
    """! INTERNAL """
    enumPhysicsStart = 7
    enumPhysicsEnd = 8
    enumExchangeStart = enumPhysicsStart
    enumExchangeEnd = enumPhysicsEnd
    enumExchangeElem = 9

    def __init__(self, listingFile):
        """! INTERNAL """
        ListingWriter.__init__(self, listingFile)
        self._autoFormat = False

    def prepare(self):
        """! INTERNAL """
        ListingWriter.prepare(self)

        self._boxFormat.append("")
        self._boxFormat.append("")
        self._boxFormat.append("")
        self._boxFormat.append("")
        self._boxFormat[MergedListingWriter.enumPhysicsStart] += u"┃{:^28}│"
        self._boxFormat[MergedListingWriter.enumPhysicsEnd] += u"┃{:^28}│"

        for _ in self._physicsData:
            self._boxFormat[MergedListingWriter.enumPhysicsStart] += u"{:^23}│"
            self._boxFormat[MergedListingWriter.enumPhysicsEnd] += u"{:^23}│"

        self._boxFormat[MergedListingWriter.enumPhysicsStart] += u"{:^12}│"
        self._boxFormat[MergedListingWriter.enumPhysicsEnd] += u"{:^12}│"

        self._boxFormat[MergedListingWriter.enumPhysicsStart] += u"{:^12}┃\n"
        self._boxFormat[MergedListingWriter.enumPhysicsEnd] += u"            ┃\n"

        self._boxFormat[MergedListingWriter.enumExchangeElem] += u"{:-^23}"

    def readLastLine(self):
        """! INTERNAL """
        self._listingFile.seek(-self._charPerLine, 2)
        moreThanLastLine = self._listingFile.read(self._charPerLine - 1).decode('utf-8', "ignore")
        lastLine = ""
        count = 0
        for cha in reversed(moreThanLastLine):
            if cha == "\n":
                break
            lastLine += cha
            count -= len(cha.encode('utf-8'))
        lastLine = lastLine[::-1]
        lastLine = lastLine.strip(u"┃")
        lastLine = lastLine.replace(" ", "")
        return lastLine.split(u"│"), count

    def writeBefore(self, sourceObject, toWrite, methodName, runningPhysics, presentTime, calculationTime):
        """! INTERNAL """
        if sourceObject in self._physics:
            calculationTimeToWrite = getFormattedTime(calculationTime)
            self._sumCalculationTime += calculationTime

            presentTimeToWrite = getFormattedTime(presentTime - self._timeInit)
            ind = self._physics.index(sourceObject)

            columnList = [":" if running else "" for running in runningPhysics]
            columnList[ind] = methodName + " start"

            self._listingFile.write(self._boxFormat[MergedListingWriter.enumPhysicsStart].format(*((toWrite,) + tuple(columnList) + (presentTimeToWrite, calculationTimeToWrite))).encode('utf-8'))

    def writeBeforeExchange(self, sourceObject, toWrite, methodName, involvedPhysics, runningPhysics, presentTime, calculationTime):
        """! INTERNAL """
        if sourceObject in self._exchangers:
            presentTimeToWrite = getFormattedTime(presentTime - self._timeInit)
            calculationTimeToWrite = getFormattedTime(calculationTime)
            self._sumCalculationTime += calculationTime

            columnList = [":" if running else "" for running in runningPhysics]
            for ind in involvedPhysics:
                columnList[ind] = self._boxFormat[MergedListingWriter.enumExchangeElem].format(methodName + " start")

            self._listingFile.write(self._boxFormat[MergedListingWriter.enumExchangeStart].format(*((toWrite,) + tuple(columnList) + (presentTimeToWrite, calculationTimeToWrite))).encode('utf-8'))

    def writeAfterNew(self, sourceObject, toWrite, methodName, runningPhysics, presentTime):
        """! INTERNAL """
        if sourceObject in self._physics:
            columnList = [":" if running else "" for running in runningPhysics]

            ind = self._physics.index(sourceObject)

            lastWords, count = self.readLastLine()
            if len(lastWords) > ind + 1 and lastWords[ind + 1] == methodName + "start":
                self._listingFile.seek(count - 1, 2)
                columnList[ind] = methodName
                presentTime = float(lastWords[-2])
                calculationTime = float(lastWords[-1])
                presentTimeToWrite = getFormattedTime(presentTime)
                calculationTimeToWrite = getFormattedTime(calculationTime)
                self._listingFile.write(self._boxFormat[MergedListingWriter.enumPhysicsStart].format(*((toWrite,) + tuple(columnList) + (presentTimeToWrite, calculationTimeToWrite))).encode('utf-8'))
            else:
                self._listingFile.seek(0, 2)
                columnList[ind] = "end"
                presentTimeToWrite = getFormattedTime(presentTime - self._timeInit)
                self._listingFile.write(self._boxFormat[MergedListingWriter.enumPhysicsEnd].format(*((toWrite,) + tuple(columnList) + (presentTimeToWrite,))).encode('utf-8'))

    def writeAfterExchange(self, sourceObject, toWrite, methodName, involvedPhysics, runningPhysics, presentTime):
        """! INTERNAL """
        if sourceObject in self._exchangers:
            columnList = [":" if running else "" for running in runningPhysics]

            lastWords, count = self.readLastLine()
            if lastWords[involvedPhysics[0] + 1].strip('-') == methodName + "start":
                self._listingFile.seek(count - 1, 2)
                for ind in involvedPhysics:
                    columnList[ind] = self._boxFormat[MergedListingWriter.enumExchangeElem].format(methodName)
                presentTime = float(lastWords[-2])
                calculationTime = float(lastWords[-1])
                presentTimeToWrite = getFormattedTime(presentTime)
                calculationTimeToWrite = getFormattedTime(calculationTime)
                self._listingFile.write(self._boxFormat[MergedListingWriter.enumExchangeStart].format(*((toWrite,) + tuple(columnList) + (presentTimeToWrite, calculationTimeToWrite))).encode('utf-8'))
            else:
                self._listingFile.seek(0, 2)
                for ind in involvedPhysics:
                    columnList[ind] = self._boxFormat[MergedListingWriter.enumExchangeElem].format("end")
                presentTimeToWrite = getFormattedTime(presentTime - self._timeInit)
                self._listingFile.write(self._boxFormat[MergedListingWriter.enumExchangeEnd].format(*((toWrite,) + tuple(columnList) + (presentTimeToWrite,))).encode('utf-8'))


def goToLastBox(listingFile):
    """! INTERNAL """
    previousPosition = 0
    listingFile.seek(0, 0)
    boxPosition = previousPosition
    numberOfLines = 0
    line = listingFile.readline()
    while line:
        if line.startswith("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━"):
            boxPosition = previousPosition
            numberOfLines = 0
        numberOfLines += 1
        previousPosition = listingFile.tell()
        line = listingFile.readline()
    listingFile.seek(boxPosition, 0)
    return numberOfLines


def mergeListing(listingsName, newListingName):
    """! mergeListing() allows to merge listing files produced by ListingWriter (or by previous call to mergeListing()).

    It is designed to produce a comprehensive view of a MPI calculation.
    Only the last listing box of the provided files are considered.

    @param listingsName list of the name of the listing files to merge.
    @param newListingName name of the file to write.

    @warning Each of the provided files must contain one and only one listing (one table).
    """
    listings = [open(lname, "r") for lname in listingsName]
    newListing = open(newListingName, "wb+")
    writer = MergedListingWriter(newListing)
    lineNumbers = [goToLastBox(lis) for lis in listings]

    lineCurrentNumbers = [0 for lis in listings]
    physicsName = []
    physicsNumber = [0 for lis in listings]
    refTimes = [0. for lis in listings]
    refTime = float('inf')

    for i, lis in enumerate(listings):
        if lineNumbers[i] > 2:
            line = lis.readline()
            words = line.split()
            refTimes[i] = float(words[-1])
            if refTimes[i] < refTime:
                refTime = refTimes[i]
            line = lis.readline()
            words = line.split("│")
            if len(words) > 3:
                for iword in range(1, len(words) - 2):
                    physicsName.append(words[iword].strip())
                physicsNumber[i] += len(words) - 3
            lis.readline()
            lineCurrentNumbers[i] += 3

    physicsShift = [0 for lis in listings]
    for i in range(1, len(physicsShift)):
        physicsShift[i] = physicsShift[i - 1] + physicsNumber[i - 1]

    mydumbPhysics = [(i + 1, physicsName[i]) for i in range(len(physicsName))]
    runningPhysics = [False for p in mydumbPhysics]
    myExchanger = len(physicsName) + 1

    writer.initialize(mydumbPhysics, [(myExchanger, "")], force=True)
    writer.prepare()
    writer.writeInitialize(refTime)

    lineWords = [[] for lis in listings]
    currentTime = [0. for lis in listings]
    lineNature = [-1 for lis in listings]
    physicsInd = [[] for lis in listings]
    natureOneLineCalculation = 0
    natureEnd = 1
    naturenumExchangeStart = 2
    natureExchangeOneline = 3
    natureStart = 4
    natureEndExchange = 5

    def readOneListingLine(i):
        lis = listings[i]
        lineWords[i] = []
        physicsInd[i] = []
        lineOK = False
        done = False
        while not done:
            if lineCurrentNumbers[i] - 1 < lineNumbers[i]:
                line = lis.readline()
                line = line.strip().strip("┃")
                lineWords[i] = line.split("│")
                lineWords[i] = [word.strip() for word in lineWords[i]]
                lineCurrentNumbers[i] += 1
                lineOK = len(lineWords[i]) > 3 and (len(lineWords[i][1].split()) == 0 or lineWords[i][1].split()[0] != "SpentTime")
                done = lineOK
            else:
                done = True
        if not lineOK:
            currentTime[i] = float('inf')
        else:
            currentTime[i] = float(lineWords[i][-2]) + refTimes[i]
            lineNature[i] = -1
            for j in range(1, len(lineWords[i]) - 2):
                if lineWords[i][j] != "" and lineWords[i][j] != ":":
                    physicsInd[i].append(physicsShift[i] + j - 1)
                    if lineWords[i][j].strip('-') == "exchange":
                        lineNature[i] = natureExchangeOneline
                    elif lineWords[i][j].strip('-') == "exchange start":
                        lineNature[i] = naturenumExchangeStart
                    elif lineWords[i][j] == "end":
                        lineNature[i] = natureEnd
                    elif lineWords[i][j].strip('-') == "end":
                        lineNature[i] = natureEndExchange
                    elif len(lineWords[i][j].split()) > 1 and lineWords[i][j].split()[1] == "start":
                        lineNature[i] = natureStart
            if lineNature[i] == -1:
                lineNature[i] = natureOneLineCalculation

    minTime = 0.
    timeValidatedPhysics = [-1. for p in mydumbPhysics]
    lastStarted = ["" for phy in mydumbPhysics]
    for i in range(len(listings)):
        readOneListingLine(i)

    while minTime < float('inf'):
        minTime = float('inf')
        imin = -1
        for i, temps in enumerate(currentTime):
            if temps < minTime:
                minTime = temps
                imin = i
        if imin > -1:
            if lineNature[imin] == natureOneLineCalculation or lineNature[imin] == natureExchangeOneline:
                methodName = ""
                for iword in range(1, len(lineWords[imin]) - 2):
                    if lineWords[imin][iword] != "" and lineWords[imin][iword] != ":":
                        methodName = lineWords[imin][iword]
                if lineNature[imin] == natureOneLineCalculation:
                    writer.writeBefore(mydumbPhysics[physicsInd[imin][0]][0], lineWords[imin][0], methodName, runningPhysics,
                                       currentTime[imin], float(lineWords[imin][-1]))
                    lineNature[imin] = natureEnd
                else:
                    writer.writeBeforeExchange(myExchanger, lineWords[imin][0], "exchange", physicsInd[imin], runningPhysics,
                                               currentTime[imin], float(lineWords[imin][-1]))
                    lineNature[imin] = natureEndExchange
                for ilast in physicsInd[imin]:
                    lastStarted[ilast] = methodName
                    runningPhysics[ilast] = True
                currentTime[imin] += float(lineWords[imin][-1])

            else:
                if lineNature[imin] == natureEnd:
                    writer.writeAfterNew(mydumbPhysics[physicsInd[imin][0]][0], lineWords[imin][0], lastStarted[physicsInd[imin][0]],
                                         runningPhysics, currentTime[imin])
                    runningPhysics[physicsInd[imin][0]] = False
                    if lastStarted[physicsInd[imin][0]] == "validateTimeStep":
                        timeValidatedPhysics[physicsInd[imin][0]] = float(lineWords[imin][0].split()[-1])
                    if lastStarted[physicsInd[imin][0]] == "resetTime":
                        timeValidatedPhysics[physicsInd[imin][0]] = -1.
                    minTValid = min(timeValidatedPhysics)
                    if minTValid > 0.:
                        if (max(timeValidatedPhysics) - minTValid) < 1.E-8:
                            # if min(timeStepValidated):
                            writer.writeValidate(currentTime[imin])
                            for ivalid in range(len(timeValidatedPhysics)):
                                timeValidatedPhysics[ivalid] = -1
                elif lineNature[imin] == natureEndExchange:
                    writer.writeAfterExchange(myExchanger, lineWords[imin][0], "exchange", physicsInd[imin], runningPhysics, currentTime[imin])
                    for ilast in physicsInd[imin]:
                        runningPhysics[ilast] = False
                elif lineNature[imin] == natureStart or lineNature[imin] == naturenumExchangeStart:
                    methodName = ""
                    for iword in range(1, len(lineWords[imin]) - 2):
                        if lineWords[imin][iword] != "" and lineWords[imin][iword] != ":":
                            methodName = lineWords[imin][iword].split()[0]
                    if lineNature[imin] == natureStart:
                        writer.writeBefore(mydumbPhysics[physicsInd[imin][0]][0], lineWords[imin][0], methodName, runningPhysics,
                                           currentTime[imin], float(lineWords[imin][-1]))
                    else:
                        writer.writeBeforeExchange(myExchanger, lineWords[imin][0], "exchange", physicsInd[imin], runningPhysics,
                                                   currentTime[imin], float(lineWords[imin][-1]))
                    for ilast in physicsInd[imin]:
                        lastStarted[ilast] = methodName
                        runningPhysics[ilast] = True
                readOneListingLine(imin)

    writer.writeTerminate()
    for lis in listings:
        lis.close()
    newListing.close()


def getTotalTimePhysicsDriver(listingName, physicsDriverName,
                              methodNames=["initialize", "computeTimeStep", "initTimeStep", "solveTimeStep", "iterateTimeStep",
                                           "validateTimeStep", "setStationaryMode", "abortTimeStep", "resetTime", "terminate",
                                           "save", "restore"]):
    """! getTotalTimePhysicsDriver() reads a listing file produced by ListingWriter or mergeListing and returns the total time
    spent by one PhysicsDriver in indicated methods (in the last calculation).

    @param listingName name of the listing file to read.
    @param physicsDriverName name (given in the listing file) of the PhysicsDriver for which the total time is requested.
    @param methodNames list of the names of the methods to take into account. By defaut: everything but "exchange": ["initialize",
    "computeTimeStep", "initTimeStep", "solveTimeStep", "iterateTimeStep", "validateTimeStep",  "setStationaryMode", "abortTimeStep",
    "resetTime", "terminate", "save", "restore"].

    @return The total time spent by the PhysicsDriver in the indicated methods.
    """
    listing = open(listingName, "r")
    lineNumber = goToLastBox(listing)
    lineCurrentNumber = 0
    physicsColumn = -1

    if lineNumber > 2:
        line = listing.readline()
        line = listing.readline()
        words = line.split("│")
        if len(words) > 3:
            for iword in range(1, len(words) - 2):
                if words[iword].strip() == physicsDriverName:
                    physicsColumn = iword
        listing.readline()
        lineCurrentNumber += 3
    if physicsColumn < 0:
        raise Exception("getTotalTimePhysicsDriver: we do not find the PhysicsDriver " + physicsDriverName + " in listing file listingName.")

    sumTime = 0.
    while lineCurrentNumber < lineNumber:
        line = listing.readline()
        lineCurrentNumber += 1
        words = line.strip().strip('┃').split("│")
        if len(words) > physicsColumn:
            resuColumn = words[physicsColumn].strip(' -').split()
            if len(resuColumn) > 0 and resuColumn[0] in methodNames:
                sumTime += float(words[-1].strip())

    listing.close()
    return sumTime


def getTimesExchanger(listingName, exchangerName, physicsDriverNames):
    """! getTimesExchanger() reads a listing file produced by ListingWriter or mergeListing and returns time information about
    a chosen exchanger (during the last calculation).

    For each PhysicsDriver involved in the exchange, the function distinguishes between exchange time and waiting time. The
    exchange is assumed to really begin when all involved PhysicsDriver enter the exchange.
    For each of them, the waiting time is the time spent in the exchange before they all enter it. The exchange time is the time
    from this "real beginning" to the end of the exchange (from the point of view of each PhysicsDriver).

    @param listingName name of the listing file to read.
    @param exchangerName name (given in the listing file) of the Exchanger for which time information is requested.
    @param physicsDriverNames list of the names of the PhysicsDriver (given in the listing file) involved in the Exchanger. They must
    be really involved!

    @return A list of len(physicsDriverNames) elements, in the same order than physicsDriverNames. Each element is a list of two
    values: first the total exchange time spent by this PhysicsDriver in the Exchanger, then its total waiting time in the Exchanger.
    """
    listing = open(listingName, "r")
    lineNumber = goToLastBox(listing)
    lineCurrentNumber = 0
    physicsColumns = [-1 for p in physicsDriverNames]

    if lineNumber > 2:
        line = listing.readline()
        line = listing.readline()
        words = line.split("│")
        if len(words) > 3:
            for iword in range(1, len(words) - 2):
                if words[iword].strip() in physicsDriverNames:
                    physicsColumns[physicsDriverNames.index(words[iword].strip())] = iword
        listing.readline()
        lineCurrentNumber += 3
    for phy in physicsColumns:
        if phy < 0:
            raise Exception("getTimesExchanger: we do not find all the PhysicsDrivers of" + str(physicsDriverNames) + ".")

    sumTimes = [[0., 0.] for phy in physicsDriverNames]  # Pour chaque PhysicsDriver on renvoie le temps d'echange (sans l'attente) et le temps d'attente.
    intermediateTime = [0. for phy in physicsDriverNames]
    isStarted = [False for phy in physicsDriverNames]
    while lineCurrentNumber < lineNumber:
        line = listing.readline()
        lineCurrentNumber += 1
        words = line.strip().strip('┃').split("│")
        if len(words) > 0 and words[0].strip() == exchangerName:
            currentTime = float(words[-2].strip())
            for i, phy in enumerate(physicsColumns):
                resuColumn = words[phy].strip(' -').split()
                if len(resuColumn) > 0 and resuColumn[0] == "exchange":
                    intermediateTime[i] = currentTime
                    isStarted[i] = True
                if len(resuColumn) == 1 and resuColumn[0] == "end":
                    sumTimes[i][0] += currentTime - intermediateTime[i]
                if len(resuColumn) == 1 and resuColumn[0] == "exchange":
                    sumTimes[i][0] += float(words[-1].strip())
            if min(isStarted):
                for i in range(len(physicsDriverNames)):
                    isStarted[i] = False
                    sumTimes[i][1] += currentTime - intermediateTime[i]
                    intermediateTime[i] = currentTime
    listing.close()
    return sumTimes
