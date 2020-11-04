# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contains the class ListingWriter. """
from __future__ import print_function, division


def getFormattedTime(time):
    """ For internal use only. """
    timeToWrite = ""
    if time > 1.:
        timeToWrite = "{:.4f}".format(time)
    else:
        timeToWrite = "{:.4e}".format(time)
    return timeToWrite


class ListingWriter(object):
    """  ListingWriter allows, in association with TTracer, to write a global coupling listing file with calculation time measurement.
    """

    e_top = 0
    e_entete = 1
    e_closeTop = 2
    e_bilan = 3
    e_term = 4
    e_interrupt = 5
    e_continue = 6

    def __init__(self, listingFile):
        """ Builds a ListingWriter object.

        :param listingFile: a file object which has to be already open in written-binary mode (file = open("file.txt", "wb")). It has to be closed (file.close()) by caller.
        """
        self.listingFile_ = listingFile

    def initialize(self, coupler, physics, exchangers):
        """ Initialize the object. Should be done after the building of all involved objects but before their initialization.

        :param coupler: Coupler or related object that drive the calculation, modified with Tracer to point on this ListingWriter object. The call to the methods initialize, validateTimeStep and terminate of coupler will lead to special treatments.
        :param physics: a list of tuples (object, name). object should be a PhysicsDriver, modified with Tracer to point on this ListingWriter object. A column is created in the listing file for each of them. name allows to identify them.
        :param exchangers: a list of tuples (object, name). object should be an Exchanger object, modified with Tracer to point on this ListingWriter object. name allows to identify them in the final listing file.
        """
        self.coupler_ = coupler
        if not isinstance(self, mergedListingWriter) and not (hasattr(coupler, "static_lWriter") and coupler.static_lWriter is self):
            raise Exception("listingWriter.initialize : The coupler object is not modified by tracer to point on self.")
        self.physics_ = []
        self.physicsData_ = []  
        for p in physics:
            if isinstance(self, mergedListingWriter) or (hasattr(p[0], "static_lWriter") and p[0].static_lWriter is self):
                self.physics_.append(p[0])
                self.physicsData_.append([p[1], u""])  # (name, format)
        self.exchangers_ = [e[0] for e in exchangers]
        self.exchangersData_ = [[e[1], u""] for e in exchangers]  # (name, format)
        self.timeInit_ = 0.
        self.timeValid_ = 0.
        self.charPerLine_ = 0
        self.sumCalculationTime_ = 0.

        self.boxFormat = [""] * 7
        for p in self.physicsData_:
            p[1] += u"┃{:^28}│"
        for e in self.exchangersData_:
            e[1] += u"┃{0:^28.28}│"
        self.boxFormat[ListingWriter.e_top] += u"┏{}┯".format(u"━" * 28)
        self.boxFormat[ListingWriter.e_entete] += u"┃{:^28}│".format(u"In / Out")
        self.boxFormat[ListingWriter.e_closeTop] += u"┠{}┼".format(u"─" * 28)
        self.boxFormat[ListingWriter.e_bilan] += u"┃{:^28}│".format(u"Time step complete")
        self.boxFormat[ListingWriter.e_term] += u"┗{}┷".format(u"━" * 28)
        self.boxFormat[ListingWriter.e_interrupt] += u"┠{}┼".format(u"─" * 28)
        self.boxFormat[ListingWriter.e_continue] += u"┠{}┼".format(u"─" * 28)
        for i, p1 in enumerate(self.physicsData_):
            for j in range(len(self.physicsData_)):
                if i == j:
                    p1[1] += u"{:^22}│"
                else:
                    p1[1] += u"                      │"
            for e in self.exchangersData_:
                e[1] += u"{1:-^22}│"
            self.boxFormat[ListingWriter.e_top] += u"━━━━━━━━━━━━━━━━━━━━━━┯"
            self.boxFormat[ListingWriter.e_entete] += u"{:^22.22}│"
            self.boxFormat[ListingWriter.e_closeTop] += u"──────────────────────┼"
            self.boxFormat[ListingWriter.e_term] += u"━━━━━━━━━━━━━━━━━━━━━━┷"
            self.boxFormat[ListingWriter.e_interrupt] += u"──────────────────────" + (u"┴" if i != (len(self.physicsData_) - 1) else u"┼")
            self.boxFormat[ListingWriter.e_continue] += u"──────────────────────" + (u"┬" if i != (len(self.physicsData_) - 1) else u"┼")

        decalage = (22 + 1) * len(self.physicsData_) - 1
        self.boxFormat[ListingWriter.e_bilan] += u"{:^" + str(decalage) + u"}│"

        for p in self.physicsData_:
            p[1] += u"{:^12}│"
        for e in self.exchangersData_:
            e[1] += u"{2:^12}│"
        self.boxFormat[ListingWriter.e_top] += u"━━━━━━━━━━━━┯"
        self.boxFormat[ListingWriter.e_entete] += u"    time    │"
        self.boxFormat[ListingWriter.e_closeTop] += u"────────────┼"
        self.boxFormat[ListingWriter.e_bilan] += u"{:^12}│"
        self.boxFormat[ListingWriter.e_term] += u"━━━━━━━━━━━━┷"
        self.boxFormat[ListingWriter.e_interrupt] += u"────────────┼"
        self.boxFormat[ListingWriter.e_continue] += u"────────────┼"

        for p in self.physicsData_:
            p[1] += u"{:^12}┃\n"
        for e in self.exchangersData_:
            e[1] += u"{3:^12}┃\n"
        self.boxFormat[ListingWriter.e_top] += u"━━━━━━━━━━━━┓ Reference time = {:}\n"
        self.boxFormat[ListingWriter.e_entete] += u"     dt     ┃\n"
        self.boxFormat[ListingWriter.e_closeTop] += u"────────────┨\n"
        self.boxFormat[ListingWriter.e_bilan] += u"{:^12}┃\n"
        self.boxFormat[ListingWriter.e_term] += u"━━━━━━━━━━━━┛\n"
        self.boxFormat[ListingWriter.e_interrupt] += u"────────────┨\n"
        self.boxFormat[ListingWriter.e_continue] += u"────────────┨\n"

        self.charPerLine_ = len(self.boxFormat[ListingWriter.e_top].encode('utf-8'))

    def writeBefore(self, sourceObject, methodName, PresentTime):
        """ For internal use only. """
        if sourceObject is self.coupler_ and methodName == "initialize":
            self.listingFile_.write(self.boxFormat[ListingWriter.e_top].format("{:10.6f}".format(PresentTime)).encode('utf-8'))
            physicsName = [p[0] for p in self.physicsData_]
            self.listingFile_.write(self.boxFormat[ListingWriter.e_entete].format(*physicsName).encode('utf-8'))
            self.listingFile_.write(self.boxFormat[ListingWriter.e_closeTop].encode('utf-8'))
            self.timeInit_ = PresentTime
            self.timeValid_ = PresentTime
            self.listingFile_.flush()

    def writeAfter(self, sourceObject, input_var, outputTuple, methodName, PresentTime, calculationTime):
        """ For internal use only. """
        PresentTimeToWrite = getFormattedTime(PresentTime - self.timeInit_)
        calculationTimeToWrite = getFormattedTime(calculationTime)

        if sourceObject in self.physics_:
            self.sumCalculationTime_ += calculationTime

            ind = self.physics_.index(sourceObject)
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
                if input_var > 1e2 or input_var < 0.1:
                    toWrite += "{:.4e}".format(input_var)
                else:
                    toWrite += "{:.4f}".format(input_var)
                toWrite += ", ok = " + ("yes" if outputTuple else "no")

            elif methodName in ["solveTimeStep", "initialize", "terminate"]:
                toWrite += "succeed = " + ("yes" if outputTuple else "no")
            elif methodName == "iterateTimeStep":
                toWrite += "succeed = " + ("yes" if outputTuple[0] else "no")
                toWrite += ", cv. = " + ("yes" if outputTuple[1] else "no")
            elif methodName == "validateTimeStep":
                toWrite += "time = " + "{:.4f}".format(sourceObject.presentTime())

            self.listingFile_.write(self.physicsData_[ind][1].format(toWrite, methodName, PresentTimeToWrite, calculationTimeToWrite).encode('utf-8'))

        if sourceObject in self.exchangers_:
            ind = self.exchangers_.index(sourceObject)
            self.listingFile_.write(self.exchangersData_[ind][1].format(self.exchangersData_[ind][0], methodName, PresentTimeToWrite, calculationTimeToWrite).encode('utf-8'))

        if sourceObject is self.coupler_ and methodName == "validateTimeStep":
            PresentTime += calculationTime
            PresentTimeToWrite = getFormattedTime(PresentTime - self.timeInit_)
            calculationTimeToWrite = getFormattedTime(PresentTime - self.timeValid_)
            sumCalculationTimeToWrite = getFormattedTime(self.sumCalculationTime_)

            self.listingFile_.write(self.boxFormat[ListingWriter.e_interrupt].encode('utf-8'))
            self.listingFile_.write(self.boxFormat[ListingWriter.e_bilan].format("SpentTime " + calculationTimeToWrite, PresentTimeToWrite, sumCalculationTimeToWrite).encode('utf-8'))
            self.listingFile_.write(self.boxFormat[ListingWriter.e_continue].encode('utf-8'))

            self.timeValid_ = PresentTime
            self.sumCalculationTime_ = 0.

        if sourceObject is self.coupler_ and methodName == "terminate":
            self.listingFile_.write(self.boxFormat[ListingWriter.e_term].encode('utf-8'))

        self.listingFile_.flush()


class mergedListingWriter(ListingWriter):
    """ For internal use only. """
    e_physics_start = 7
    e_physics_end = 8
    e_exchange_start = e_physics_start
    e_exchange_end = e_physics_end
    e_exchange_elem = 9

    def __init__(self, listingFile):
        ListingWriter.__init__(self, listingFile)

    def initialize(self, coupler, physics, exchangers):
        ListingWriter.initialize(self, coupler, physics, exchangers)

        self.boxFormat.append("")
        self.boxFormat.append("")
        self.boxFormat.append("")
        self.boxFormat.append("")
        self.boxFormat[mergedListingWriter.e_physics_start] += u"┃{:^28}│"
        self.boxFormat[mergedListingWriter.e_physics_end] += u"┃{:^28}│"

        for p1 in self.physicsData_:
            self.boxFormat[mergedListingWriter.e_physics_start] += u"{:^22}│"
            self.boxFormat[mergedListingWriter.e_physics_end] += u"{:^22}│"

        self.boxFormat[mergedListingWriter.e_physics_start] += u"{:^12}│"
        self.boxFormat[mergedListingWriter.e_physics_end] += u"{:^12}│"

        self.boxFormat[mergedListingWriter.e_physics_start] += u"{:^12}┃\n"
        self.boxFormat[mergedListingWriter.e_physics_end] += u"            ┃\n"

        self.boxFormat[mergedListingWriter.e_exchange_elem] += u"{:-^22}"

    def readLastLine(self):
        self.listingFile_.seek(-self.charPerLine_, 2)
        moreThanLastLine = self.listingFile_.read(self.charPerLine_ - 1).decode('utf-8', "ignore")
        LastLine = ""
        count = 0
        for c in reversed(moreThanLastLine):
            if c == "\n":
                break
            LastLine += c
            count -= len(c.encode('utf-8'))
        LastLine = LastLine[::-1]
        LastLine = LastLine.strip(u"┃")
        LastLine = LastLine.replace(" ", "")
        return LastLine.split(u"│"), count

    def writeBefore(self, sourceObject, toWrite, methodName, runningPhysics, PresentTime, calculationTime):
        if sourceObject in self.physics_:
            calculationTimeToWrite = getFormattedTime(calculationTime)
            self.sumCalculationTime_ += calculationTime
            
            PresentTimeToWrite = getFormattedTime(PresentTime - self.timeInit_)
            ind = self.physics_.index(sourceObject)

            columnList = [":" if running else "" for running in runningPhysics]
            columnList[ind] = methodName + " start"

            self.listingFile_.write(self.boxFormat[mergedListingWriter.e_physics_start].format(*((toWrite,) + tuple(columnList) + (PresentTimeToWrite, calculationTimeToWrite))).encode('utf-8'))

    def writeBeforeExchange(self, sourceObject, toWrite, methodName, involvedPhysics, runningPhysics, PresentTime, calculationTime):
        if sourceObject in self.exchangers_:
            PresentTimeToWrite = getFormattedTime(PresentTime - self.timeInit_)
            calculationTimeToWrite = getFormattedTime(calculationTime)

            columnList = [":" if running else "" for running in runningPhysics]
            for ind in involvedPhysics:
                columnList[ind] = self.boxFormat[mergedListingWriter.e_exchange_elem].format(methodName + " start")

            self.listingFile_.write(self.boxFormat[mergedListingWriter.e_exchange_start].format(*((toWrite,) + tuple(columnList) + (PresentTimeToWrite, calculationTimeToWrite))).encode('utf-8'))

    def writeAfter(self, sourceObject, toWrite, methodName, runningPhysics, PresentTime):
        if sourceObject in self.physics_:
            columnList = [":" if running else "" for running in runningPhysics]

            ind = self.physics_.index(sourceObject)

            lastWords, count = self.readLastLine()
            if len(lastWords) > ind + 1 and lastWords[ind + 1] == methodName + "start":
                self.listingFile_.seek(count - 1, 2)
                columnList[ind] = methodName
                PresentTime = float(lastWords[-2])
                calculationTime = float(lastWords[-1])
                PresentTimeToWrite = getFormattedTime(PresentTime)
                calculationTimeToWrite = getFormattedTime(calculationTime)
                self.listingFile_.write(self.boxFormat[mergedListingWriter.e_physics_start].format(*((toWrite,) + tuple(columnList) + (PresentTimeToWrite, calculationTimeToWrite))).encode('utf-8'))
            else:
                self.listingFile_.seek(0, 2)
                columnList[ind] = "end"
                PresentTimeToWrite = getFormattedTime(PresentTime - self.timeInit_)
                self.listingFile_.write(self.boxFormat[mergedListingWriter.e_physics_end].format(*((toWrite,) + tuple(columnList) + (PresentTimeToWrite,))).encode('utf-8'))

        if sourceObject is self.coupler_ and (methodName == "validateTimeStep" or methodName == "terminate"):
            ListingWriter.writeAfter(self, sourceObject, 0, 0, methodName, PresentTime, 0.)

    def writeAfterExchange(self, sourceObject, toWrite, methodName, involvedPhysics, runningPhysics, PresentTime):
        if sourceObject in self.exchangers_:
            columnList = [":" if running else "" for running in runningPhysics]

            lastWords, count = self.readLastLine()
            if lastWords[involvedPhysics[0] + 1].strip('-') == methodName + "start":
                self.listingFile_.seek(count - 1, 2)
                for ind in involvedPhysics:
                    columnList[ind] = self.boxFormat[mergedListingWriter.e_exchange_elem].format(methodName)
                PresentTime = float(lastWords[-2])
                calculationTime = float(lastWords[-1])
                PresentTimeToWrite = getFormattedTime(PresentTime)
                calculationTimeToWrite = getFormattedTime(calculationTime)
                self.listingFile_.write(self.boxFormat[mergedListingWriter.e_exchange_start].format(*((toWrite,) + tuple(columnList) + (PresentTimeToWrite, calculationTimeToWrite))).encode('utf-8'))
            else:
                self.listingFile_.seek(0, 2)
                for ind in involvedPhysics:
                    columnList[ind] = self.boxFormat[mergedListingWriter.e_exchange_elem].format("end")
                PresentTimeToWrite = getFormattedTime(PresentTime - self.timeInit_)
                self.listingFile_.write(self.boxFormat[mergedListingWriter.e_exchange_end].format(*((toWrite,) + tuple(columnList) + (PresentTimeToWrite,))).encode('utf-8'))


def mergeListing(listingsName, newListingName):
    """ This function allows to merge listing files produced by ListingWriter. It is designed to produce a comprehensive view of a MPI calculation.

    :param listingsName: list of the name of the listing files to merge.
    :param newListingName: name of the file to write.
    """
    listings = [open(lname, "r") for lname in listingsName]
    newListing = open(newListingName, "wb+")
    writer = mergedListingWriter(newListing)
    lineNumbers = [sum(1 for _ in l) for l in listings]
    for l in listings:
        l.seek(0)
    lineCurrentNumbers = [0 for l in listings]
    physicsName = []
    physicsNumber = [0 for l in listings]
    refTimes = [0. for l in listings]
    refTime = float('inf')

    for i, l in enumerate(listings):
        if lineNumbers[i] > 2:
            line = l.readline()
            words = line.split()
            refTimes[i] = float(words[-1])
            if refTimes[i] < refTime:
                refTime = refTimes[i]
            line = l.readline()
            words = line.split("│")
            if len(words) > 3:
                for iw in range(1, len(words) - 2):
                    physicsName.append(words[iw].strip())
                physicsNumber[i] += len(words) - 3
            l.readline()
            lineCurrentNumbers[i] += 3

    physicsShift = [0 for l in listings]
    for i in range(1, len(physicsShift)):
        physicsShift[i] = physicsShift[i - 1] + physicsNumber[i - 1]

    myCoupler = 0
    mydumbPhysics = [(i + 1, physicsName[i]) for i in range(len(physicsName))]
    runningPhysics = [False for p in mydumbPhysics]
    myExchanger = len(physicsName) + 1

    writer.initialize(myCoupler, mydumbPhysics, [(myExchanger, "")])
    ListingWriter.writeBefore(writer, myCoupler, "initialize", refTime)

    lineWords = [[] for l in listings]
    CurrentTime = [0. for l in listings]
    lineNature = [-1 for l in listings]
    physicsInd = [[] for l in listings]
    nature_oneLineCalculation = 0
    nature_end = 1
    nature_exchange_start = 2
    nature_exchange_oneline = 3
    nature_start = 4
    nature_end_exchange = 5

    def readOneListingLine(i):
        l = listings[i]
        lineWords[i] = []
        physicsInd[i] = []
        lineOK = False
        done = False
        while not done:
            if lineCurrentNumbers[i] - 1 < lineNumbers[i]:
                line = l.readline()
                line = line.strip().strip("┃")
                lineWords[i] = line.split("│")
                lineWords[i] = [word.strip() for word in lineWords[i]]
                lineCurrentNumbers[i] += 1
                lineOK = len(lineWords[i]) > 3 and (len(lineWords[i][1].split()) == 0 or lineWords[i][1].split()[0] != "SpentTime")
                done = lineOK
            else:
                done = True
        if not lineOK:
            CurrentTime[i] = float('inf')
        else:
            CurrentTime[i] = float(lineWords[i][-2]) + refTimes[i]
            lineNature[i] = -1
            for j in range(1, len(lineWords[i]) - 2):
                if lineWords[i][j] != "" and lineWords[i][j] != ":":
                    physicsInd[i].append(physicsShift[i] + j - 1)
                    if lineWords[i][j].strip('-') == "exchange":
                        lineNature[i] = nature_exchange_oneline
                    elif lineWords[i][j].strip('-') == "exchange start":
                        lineNature[i] = nature_exchange_start
                    elif lineWords[i][j] == "end":
                        lineNature[i] = nature_end
                    elif lineWords[i][j].strip('-') == "end":
                        lineNature[i] = nature_end_exchange
                    elif len(lineWords[i][j].split()) > 1 and lineWords[i][j].split()[1] == "start" :
                        lineNature[i] = nature_start
            if lineNature[i] == -1:
                lineNature[i] = nature_oneLineCalculation

    minTime = 0.
    timeStepValidated = [False for p in mydumbPhysics]
    lastStarted = ["" for p in mydumbPhysics]
    for i in range(len(listings)):
        readOneListingLine(i)

    while minTime < float('inf'):
        minTime = float('inf')
        imin = -1
        for i, t in enumerate(CurrentTime):
            if t < minTime:
                minTime = t
                imin = i
        if imin > -1:
            if lineNature[imin] == nature_oneLineCalculation or lineNature[imin] == nature_exchange_oneline:
                methodName = ""
                for iword in range(1, len(lineWords[imin]) - 2):
                    if lineWords[imin][iword] != "" and lineWords[imin][iword] != ":":
                        methodName = lineWords[imin][iword]
                if lineNature[imin] == nature_oneLineCalculation:
                    writer.writeBefore(mydumbPhysics[physicsInd[imin][0]][0], lineWords[imin][0], methodName, runningPhysics, CurrentTime[imin], float(lineWords[imin][-1]))
                    lineNature[imin] = nature_end
                else:
                    writer.writeBeforeExchange(myExchanger, lineWords[imin][0], "exchange", physicsInd[imin], runningPhysics, CurrentTime[imin], float(lineWords[imin][-1]))
                    lineNature[imin] = nature_end_exchange
                for ilast in physicsInd[imin]:
                    lastStarted[ilast] = methodName
                    runningPhysics[ilast] = True
                CurrentTime[imin] += float(lineWords[imin][-1])

            else:
                if lineNature[imin] == nature_end:
                    writer.writeAfter(mydumbPhysics[physicsInd[imin][0]][0], lineWords[imin][0], lastStarted[physicsInd[imin][0]], runningPhysics, CurrentTime[imin])
                    runningPhysics[physicsInd[imin][0]] = False
                    if lastStarted[physicsInd[imin][0]] == "validateTimeStep":
                        timeStepValidated[physicsInd[imin][0]] = True
                    if min(timeStepValidated):
                        writer.writeAfter(myCoupler, "", "validateTimeStep", runningPhysics, CurrentTime[imin])
                        for ivalid in range(len(timeStepValidated)):
                            timeStepValidated[ivalid] = False
                elif lineNature[imin] == nature_end_exchange:
                    writer.writeAfterExchange(myExchanger, lineWords[imin][0], "exchange", physicsInd[imin], runningPhysics, CurrentTime[imin])
                    for ilast in physicsInd[imin]:
                        runningPhysics[ilast] = False
                elif lineNature[imin] == nature_start or lineNature[imin] == nature_exchange_start:
                    methodName = ""
                    for iword in range(1, len(lineWords[imin]) - 2):
                        if lineWords[imin][iword] != "" and lineWords[imin][iword] != ":":
                            methodName = lineWords[imin][iword].split()[0]
                    if lineNature[imin] == nature_start:
                        writer.writeBefore(mydumbPhysics[physicsInd[imin][0]][0], lineWords[imin][0], methodName, runningPhysics, CurrentTime[imin], float(lineWords[imin][-1]))
                    else:
                        writer.writeBeforeExchange(myExchanger, lineWords[imin][0], "exchange", physicsInd[imin], runningPhysics, CurrentTime[imin], float(lineWords[imin][-1]))
                    for ilast in physicsInd[imin]:
                        lastStarted[ilast] = methodName
                        runningPhysics[ilast] = True
                readOneListingLine(imin)

    writer.writeAfter(myCoupler, "", "terminate", runningPhysics, 0.)
    for l in listings:
        l.close()
    newListing.close()
