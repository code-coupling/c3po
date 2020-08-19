# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contains the class listingWriter. """
from __future__ import print_function, division

def getFormattedTime(time):
    """ For internal use only. """
    timeToWrite = ""
    if time > 1.:
        timeToWrite = "{:.4f}".format(time)
    else:
        timeToWrite = "{:.4e}".format(time)
    return timeToWrite


class listingWriter(object):
    """  listingWriter allows, in association with tracer, to write a global coupling listing file with calculation time measurement.
    """

    e_top = 0
    e_entete = 1
    e_closeTop = 2
    e_bilan = 3
    e_term = 4
    e_interrupt = 5
    e_continue = 6

    def __init__(self, listingFile):
        """ Builds a listingWriter object.

        :param listingFile: a file object which has to be already open in written mode (file = open("file.txt", "w")). It has to be closed (file.close()) by caller.
        """
        self.listingFile_ = listingFile
        
    def initialize(self, coupler, physics, exchangers):
        """ Initialize the object. Should be done after the building of all involved objects but before their initialization.

        :param coupler: coupler or related object that drive the calculation, modified with tracer to point on this listingWriter object. The call to the methods initialize, validateTimeStep and terminate of coupler will lead to special treatments.
        :param physics: a list of tuples (object, name). object should be a physicsDriver, modified with tracer to point on this listingWriter object. A column is created in the listing file for each of them. name allows to identify them.
        :param exchangers: a list of tuples (object, name). object should be an exchanger object, modified with tracer to point on this listingWriter object. name allows to identify them in the final listing file.
        """
        self.coupler_ = coupler
        self.physics_ = [p[0] for p in physics]
        self.physicsData_ = [[p[1], ""] for p in physics] #(name, format)
        self.exchangers_ = [e[0] for e in exchangers]
        self.exchangersData_ = [[e[1], ""] for e in exchangers] #(name, format)
        self.timeInit_ = 0.
        self.timeValid_ = 0.
        self.charPerLine_ = 0
        self.sumCalculationTime_ = 0.
        
        self.boxFormat = [""]*7
        for p in self.physicsData_:
            p[1] += "┃{:^27}│"
        for e in self.exchangersData_:
            e[1] += "┃{0:^27.27}│"
        self.boxFormat[listingWriter.e_top] += "┏{}┯".format("━" * 27)
        self.boxFormat[listingWriter.e_entete] += "┃{:^27}│".format("In / Out")
        self.boxFormat[listingWriter.e_closeTop] += "┠{}┼".format("─" * 27)
        self.boxFormat[listingWriter.e_bilan] += "┃{:^27}│".format("Time step complete")
        self.boxFormat[listingWriter.e_term] += "┗{}┷".format("━" * 27)
        self.boxFormat[listingWriter.e_interrupt] += "┠{}┼".format("─" * 27)
        self.boxFormat[listingWriter.e_continue] += "┠{}┼".format("─" * 27)
        for i, p1 in enumerate(self.physicsData_):
            for j in range(len(self.physicsData_)):
                if i == j:
                    p1[1] += "{:^18}│"
                else:
                    p1[1] += "                  │"
            for e in self.exchangersData_:
                e[1] += "{1:-^18}│"
            self.boxFormat[listingWriter.e_top] += "━━━━━━━━━━━━━━━━━━┯"
            self.boxFormat[listingWriter.e_entete] += "{:^18.18}│"
            self.boxFormat[listingWriter.e_closeTop] += "──────────────────┼"
            self.boxFormat[listingWriter.e_term] += "━━━━━━━━━━━━━━━━━━┷"
            self.boxFormat[listingWriter.e_interrupt] += "──────────────────" + ("┴" if i != (len(self.physicsData_) - 1) else "┼")
            self.boxFormat[listingWriter.e_continue] += "──────────────────" + ("┬" if i != (len(self.physicsData_) - 1) else "┼")
        
        decalage = (18 + 1) * len(self.physicsData_) - 1
        self.boxFormat[listingWriter.e_bilan] += "{:^"+str(decalage)+"}│"

        for p in self.physicsData_:
            p[1] += "{:^12}│"
        for e in self.exchangersData_:
            e[1] += "{2:^12}│"
        self.boxFormat[listingWriter.e_top] += "━━━━━━━━━━━━┯"
        self.boxFormat[listingWriter.e_entete] += "  cputime   │"
        self.boxFormat[listingWriter.e_closeTop] += "────────────┼"
        self.boxFormat[listingWriter.e_bilan] += "{:^12}│"
        self.boxFormat[listingWriter.e_term] += "━━━━━━━━━━━━┷"
        self.boxFormat[listingWriter.e_interrupt] += "────────────┼"
        self.boxFormat[listingWriter.e_continue] += "────────────┼"

        for p in self.physicsData_:
            p[1] += "{:^12}┃\n"
        for e in self.exchangersData_:
            e[1] += "{3:^12}┃\n"
        self.boxFormat[listingWriter.e_top] += "━━━━━━━━━━━━┓ Reference time = {:}\n"
        self.boxFormat[listingWriter.e_entete] += "   cpudt    ┃\n"
        self.boxFormat[listingWriter.e_closeTop] += "────────────┨\n"
        self.boxFormat[listingWriter.e_bilan] += "{:^12}┃\n"
        self.boxFormat[listingWriter.e_term] += "━━━━━━━━━━━━┛\n"
        self.boxFormat[listingWriter.e_interrupt] += "────────────┨\n"
        self.boxFormat[listingWriter.e_continue] += "────────────┨\n"

        self.charPerLine_ = len(self.boxFormat[listingWriter.e_top])

    def writeBefore(self, sourceObject, methodName, PresentTime):
        """ For internal use only. """
        if sourceObject is self.coupler_ and methodName == "initialize":
            self.listingFile_.write(self.boxFormat[listingWriter.e_top].format("{:10.6f}".format(PresentTime)))
            physicsName = [p[0] for p in self.physicsData_]
            self.listingFile_.write(self.boxFormat[listingWriter.e_entete].format(*physicsName))
            self.listingFile_.write(self.boxFormat[listingWriter.e_closeTop])
            self.timeInit_ = PresentTime
            self.timeValid_ = PresentTime

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
                toWrite += ", ok = " +  ("yes" if outputTuple else "no")
                
            elif methodName in ["solveTimeStep", "initialize", "terminate"]:
                toWrite += "succed = " + ("yes" if outputTuple else "no")
            elif methodName == "iterateTimeStep":
                toWrite += "succed = " + ("yes" if outputTuple[0] else "no")
                toWrite += ", conv. = " + ("yes" if outputTuple[1] else "no")
            elif methodName == "validateTimeStep":
                toWrite += "time = " + "{:.4f}".format(sourceObject.presentTime())
            
            self.listingFile_.write(self.physicsData_[ind][1].format(toWrite, methodName, PresentTimeToWrite, calculationTimeToWrite))

        if sourceObject in self.exchangers_:
            ind = self.exchangers_.index(sourceObject)
            self.listingFile_.write(self.exchangersData_[ind][1].format(self.exchangersData_[ind][0], methodName, PresentTimeToWrite, calculationTimeToWrite))

        if sourceObject is self.coupler_ and methodName == "validateTimeStep":
            PresentTime += calculationTime
            PresentTimeToWrite = getFormattedTime(PresentTime - self.timeInit_)
            calculationTimeToWrite = getFormattedTime(PresentTime - self.timeValid_)
            sumCalculationTimeToWrite = getFormattedTime(self.sumCalculationTime_)

            self.listingFile_.write(self.boxFormat[listingWriter.e_interrupt])
            self.listingFile_.write(self.boxFormat[listingWriter.e_bilan].format("SumCPU " + sumCalculationTimeToWrite, PresentTimeToWrite, calculationTimeToWrite))  
            self.listingFile_.write(self.boxFormat[listingWriter.e_continue])

            self.timeValid_ = PresentTime
            self.sumCalculationTime_ = 0.

        if sourceObject is self.coupler_ and methodName == "terminate":
            self.listingFile_.write(self.boxFormat[listingWriter.e_term])


class mergedListingWriter(listingWriter):
    """ For internal use only. """
    e_physics_start = 7
    e_physics_end = 8
    e_exchange_start = 9
    e_exchange_end = e_physics_end
    e_exchange_elem = 10
    
    def __init__(self, listingFile):
        listingWriter.__init__(self, listingFile)
    
    def initialize(self, coupler, physics, exchangers):
        listingWriter.initialize(self, coupler, physics, exchangers)
        
        self.boxFormat.append("")
        self.boxFormat.append("")
        self.boxFormat.append("")
        self.boxFormat.append("")
        self.boxFormat[mergedListingWriter.e_physics_start] += "┃{}│".format(" " * 27)
        self.boxFormat[mergedListingWriter.e_physics_end] += "┃{:^27}│"
        self.boxFormat[mergedListingWriter.e_exchange_start] += "┃{:^27}│"

        for p1 in self.physicsData_:
            self.boxFormat[mergedListingWriter.e_physics_start] += "{:^18}│"
            self.boxFormat[mergedListingWriter.e_physics_end] += "{:^18}│"
            self.boxFormat[mergedListingWriter.e_exchange_start] += "{:^18}│"

        self.boxFormat[mergedListingWriter.e_physics_start] += "{:^12}│"
        self.boxFormat[mergedListingWriter.e_physics_end] += "{:^12}│"
        self.boxFormat[mergedListingWriter.e_exchange_start] += "{:^12}│"

        self.boxFormat[mergedListingWriter.e_physics_start] += "            ┃\n"
        self.boxFormat[mergedListingWriter.e_physics_end] += "{:^12}┃\n"
        self.boxFormat[mergedListingWriter.e_exchange_start] += "            ┃\n"
        
        self.boxFormat[mergedListingWriter.e_exchange_elem] += "{:-^18}"

    def readLastLine(self):
        self.listingFile_.seek(-self.charPerLine_, 2)
        moreThanLastLine = self.listingFile_.read(self.charPerLine_ - 1)
        LastLine = ""
        count = 0
        for c in reversed(moreThanLastLine):
            if c == "\n":
                break
            LastLine += c
            count -= 1
        LastLine = LastLine[::-1]
        LastLine = LastLine.strip("┃")
        LastLine = LastLine.replace(" ","")
        LastLine = LastLine.replace("-","")
        return LastLine.split("│"), count

    def writeBefore(self, sourceObject, methodName, runningPhysics, PresentTime):
        if sourceObject in self.physics_:
            PresentTimeToWrite = getFormattedTime(PresentTime - self.timeInit_)
            ind = self.physics_.index(sourceObject)
            
            columnList = [":" if running else "" for running in runningPhysics]
            columnList[ind] = methodName

            self.listingFile_.write(self.boxFormat[mergedListingWriter.e_physics_start].format(*(tuple(columnList) + (PresentTimeToWrite,))))

    def writeBeforeExchange(self, sourceObject, toWrite, methodName, involvedPhysics, runningPhysics, PresentTime):
        if sourceObject in self.exchangers_:
            PresentTimeToWrite = getFormattedTime(PresentTime - self.timeInit_)

            columnList = [":" if running else "" for running in runningPhysics]
            for ind in involvedPhysics:
                columnList[ind] = self.boxFormat[mergedListingWriter.e_exchange_elem].format(methodName)

            self.listingFile_.write(self.boxFormat[mergedListingWriter.e_exchange_start].format(*((toWrite,) + tuple(columnList) + (PresentTimeToWrite,))))

    def writeAfter(self, sourceObject, toWrite, methodName, runningPhysics, PresentTime, calculationTime):
        calculationTimeToWrite = getFormattedTime(calculationTime)

        if sourceObject in self.physics_:
            columnList = [":" if running else "" for running in runningPhysics]

            self.sumCalculationTime_ += calculationTime

            ind = self.physics_.index(sourceObject)
           
            lastWords, count = self.readLastLine()
            if lastWords[ind + 1] == methodName:
                self.listingFile_.seek(count - 1, 2)
                columnList[ind] = methodName
            else:
                self.listingFile_.seek(0, 2)
                columnList[ind] = "end"
                PresentTime += calculationTime
            PresentTimeToWrite = getFormattedTime(PresentTime - self.timeInit_)
            self.listingFile_.write(self.boxFormat[mergedListingWriter.e_physics_end].format(*((toWrite,) + tuple(columnList) + (PresentTimeToWrite, calculationTimeToWrite))))

        if sourceObject is self.coupler_ and (methodName == "validateTimeStep" or methodName == "terminate"):
            listingWriter.writeAfter(self, sourceObject, 0, 0, methodName, PresentTime, calculationTime)

    def writeAfterExchange(self, sourceObject, toWrite, methodName, involvedPhysics, runningPhysics, PresentTime, calculationTime):
        if sourceObject in self.exchangers_:
            PresentTimeToWrite = getFormattedTime(PresentTime - self.timeInit_)
            calculationTimeToWrite = getFormattedTime(calculationTime)

            columnList = [":" if running else "" for running in runningPhysics]

            lastWords, count = self.readLastLine()
            if lastWords[involvedPhysics[0] + 1] == methodName:
                self.listingFile_.seek(count - 1, 2)
                for ind in involvedPhysics:
                    columnList[ind] = self.boxFormat[mergedListingWriter.e_exchange_elem].format(methodName)
            else:
                self.listingFile_.seek(0, 2)
                for ind in involvedPhysics:
                    columnList[ind] = self.boxFormat[mergedListingWriter.e_exchange_elem].format("end")

            self.listingFile_.write(self.boxFormat[mergedListingWriter.e_exchange_end].format(*((toWrite,) + tuple(columnList) + (PresentTimeToWrite, calculationTimeToWrite))))


def mergeListing(listingsName, newListingName):
    """ This function allows to merge listing files produced by listingWriter. It is designed to produce a comprehensive view of a MPI calculation.

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
    
    for i,l in enumerate(listings):
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
        physicsShift[i] = physicsShift[i-1] + physicsNumber[i-1]
    
    myCoupler = 0
    mydumbPhysics = [(i+1, physicsName[i]) for i in range(len(physicsName))]
    runningPhysics = [False for p in mydumbPhysics]
    myExchanger = len(physicsName)+1
    
    writer.initialize(myCoupler, mydumbPhysics, [(myExchanger, "")])
    listingWriter.writeBefore(writer, myCoupler, "initialize", refTime)
    
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
                lineOK = len(lineWords[i]) > 3 and (len(lineWords[i][1].split()) == 0 or lineWords[i][1].split()[0] != "SumCPU")
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
                        if lineWords[i][-1] != "":
                            lineNature[i] = nature_exchange_oneline
                        else:
                            lineNature[i] = nature_exchange_start
                    if lineWords[i][j] == "end":
                        lineNature[i] = nature_end
                    elif lineWords[i][j].strip('-')  == "end":
                        lineNature[i] = nature_end_exchange
            if lineNature[i] == -1 and lineWords[i][-1] != "":
                lineNature[i] = nature_oneLineCalculation
            if lineNature[i] == -1:
                lineNature[i] = nature_start

    minTime = 0.
    timeStepValidated = [False for p in mydumbPhysics]
    lastStarted = ["" for p in mydumbPhysics]
    for i in range(len(listings)):
        readOneListingLine(i)

    while minTime < float('inf'):
        minTime = float('inf')
        imin = -1
        for i,t in enumerate(CurrentTime):
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
                    writer.writeBefore(mydumbPhysics[physicsInd[imin][0]][0], methodName, runningPhysics, CurrentTime[imin])
                    lineNature[imin] = nature_end
                else:
                    writer.writeBeforeExchange(myExchanger, lineWords[imin][0], "exchange", physicsInd[imin], runningPhysics, CurrentTime[imin])
                    lineNature[imin] = nature_end_exchange
                for ilast in physicsInd[imin]:
                    lastStarted[ilast] = methodName
                    runningPhysics[ilast] = True
                CurrentTime[imin] += float(lineWords[imin][-1])
                
            else:
                if lineNature[imin] == nature_end:
                    writer.writeAfter(mydumbPhysics[physicsInd[imin][0]][0], lineWords[imin][0], lastStarted[physicsInd[imin][0]], runningPhysics, CurrentTime[imin] - float(lineWords[imin][-1]), float(lineWords[imin][-1]))
                    runningPhysics[physicsInd[imin][0]] = False
                    if lastStarted[physicsInd[imin][0]] == "validateTimeStep":
                        timeStepValidated[physicsInd[imin][0]] = True
                    if min(timeStepValidated):
                        writer.writeAfter(myCoupler, "", "validateTimeStep", runningPhysics, CurrentTime[imin] - float(lineWords[imin][-1]), float(lineWords[imin][-1]))
                        for ivalid in range(len(timeStepValidated)):
                            timeStepValidated[ivalid] = False
                elif lineNature[imin] == nature_end_exchange:
                    writer.writeAfterExchange(myExchanger, lineWords[imin][0], "exchange", physicsInd[imin], runningPhysics, CurrentTime[imin], float(lineWords[imin][-1]))
                    for ilast in physicsInd[imin]:
                        runningPhysics[ilast] = False
                elif lineNature[imin] == nature_start or lineNature[imin] == nature_exchange_start:
                    methodName = ""
                    for iword in range(1, len(lineWords[imin]) - 2):
                        if lineWords[imin][iword] != "" and lineWords[imin][iword] != ":":
                            methodName = lineWords[imin][iword]
                    if lineNature[imin] == nature_start:
                        writer.writeBefore(mydumbPhysics[physicsInd[imin][0]][0], methodName, runningPhysics, CurrentTime[imin])
                    else:
                        writer.writeBeforeExchange(myExchanger, lineWords[imin][0], "exchange", physicsInd[imin], runningPhysics, CurrentTime[imin])
                    for ilast in physicsInd[imin]:
                        lastStarted[ilast] = methodName
                        runningPhysics[ilast] = True
                readOneListingLine(imin)

    writer.writeAfter(myCoupler, "", "terminate", runningPhysics, 0., 0.)
    for l in listings:
        l.close()
    newListing.close()
    