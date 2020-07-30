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


class listingWriter(object):
    e_top = 0
    e_entete = 1
    e_closeTop = 2
    e_bilan = 3
    e_term = 4
    e_interrupt = 5
    e_continue = 6

    def __init__(self, listingFile):
        self.listingFile_ = listingFile
        
    def initialize(self, coupler, physics, exchangers):
        self.coupler_ = coupler
        self.physics_ = [p[0] for p in physics]
        self.physicsData_ = [[p[1], "", ""] for p in physics] #(name, format_start, format_end)
        self.exchangers_ = [e[0] for e in exchangers]
        self.exchangersData_ = [[e[1], ""] for e in exchangers] #(name, format)
        self.timeInit_ = 0.
        self.timeValid_ = 0.
        self.charPerLine_ = 0
        self.sumCalculationTime_ = 0.
        self.isMPI_ = False
        
        self.boxFormat = [""]*7
        for p in self.physicsData_:
            p[1] += "┃{:30}│"
            p[2] += "┃{:30}│"
        self.boxFormat[listingWriter.e_top] += "┏{}┯".format("━" * 30)
        self.boxFormat[listingWriter.e_entete] += "┃{:^30}│".format("In / Out")
        self.boxFormat[listingWriter.e_closeTop] += "┠{}┼".format("─" * 30)
        self.boxFormat[listingWriter.e_bilan] += "┃{:^30}│".format("Time step complete")
        self.boxFormat[listingWriter.e_term] += "┗{}┷".format("━" * 30)
        self.boxFormat[listingWriter.e_interrupt] += "┠{}┼".format("─" * 30)
        self.boxFormat[listingWriter.e_continue] += "┠{}┼".format("─" * 30)
        for i, p1 in enumerate(self.physicsData_):
            for j in range(len(self.physicsData_)):
                if i == j:
                    p1[1] += "{:^18}│"
                    p1[2] += "{:^18}│"
                else:
                    p1[1] += "                  │"
                    p1[2] += "                  │"
            self.boxFormat[listingWriter.e_top] += "━━━━━━━━━━━━━━━━━━┯"
            self.boxFormat[listingWriter.e_entete] += "{:^18}│"
            self.boxFormat[listingWriter.e_closeTop] += "──────────────────┼"
            self.boxFormat[listingWriter.e_term] += "━━━━━━━━━━━━━━━━━━┷"
            self.boxFormat[listingWriter.e_interrupt] += "──────────────────" + ("┴" if i != (len(self.physicsData_) - 1) else "┼")
            self.boxFormat[listingWriter.e_continue] += "──────────────────" + ("┬" if i != (len(self.physicsData_) - 1) else "┼")
        
        decalage = 19 * len(self.physicsData_) - 1
        self.boxFormat[listingWriter.e_bilan] += "{:^"+str(decalage)+"}│"
        #self.boxFormat[listingWriter.e_bilan] += " " * decalage + "│"

        for p in self.physicsData_:
            p[1] += "{:6.1e}│"
            p[2] += "{:6.1e}│"
        self.boxFormat[listingWriter.e_top] += "━━━━━━━┯"
        self.boxFormat[listingWriter.e_entete] += " time  │"
        self.boxFormat[listingWriter.e_closeTop] += "───────┼"
        self.boxFormat[listingWriter.e_bilan] += "{:6.1e}│"
        self.boxFormat[listingWriter.e_term] += "━━━━━━━┷"
        self.boxFormat[listingWriter.e_interrupt] += "───────┼"
        self.boxFormat[listingWriter.e_continue] += "───────┼"

        for p in self.physicsData_:
            p[1] += "       ┃\n"
            p[2] += "{:6.1e}┃\n"
        self.boxFormat[listingWriter.e_top] += "━━━━━━━┓\n"
        self.boxFormat[listingWriter.e_entete] += "  dt   ┃\n"
        self.boxFormat[listingWriter.e_closeTop] += "───────┨\n"
        self.boxFormat[listingWriter.e_bilan] += "{:6.1e}┃\n"
        self.boxFormat[listingWriter.e_term] += "━━━━━━━┛\n"
        self.boxFormat[listingWriter.e_interrupt] += "───────┨\n"
        self.boxFormat[listingWriter.e_continue] += "───────┨\n"

        self.charPerLine_ = len(self.boxFormat[listingWriter.e_top])
        
        for e in self.exchangersData_:
            e[1] += "┃{:30}│"
            e[1] += "{:-^"+str(decalage)+"}│"
            e[1] += "{:6.1e}│"
            e[1] += "{:6.1e}┃\n"

    def writeBefore(self, sourceObject, inputTuple, methodName, PresentTime):
        if sourceObject is self.coupler_ and methodName == "initialize":
            self.listingFile_.write(self.boxFormat[listingWriter.e_top])
            physicsName = [p[0] for p in self.physicsData_]
            self.listingFile_.write(self.boxFormat[listingWriter.e_entete].format(*physicsName))
            self.listingFile_.write(self.boxFormat[listingWriter.e_closeTop])
            self.timeInit_ = PresentTime
            self.timeValid_ = PresentTime

        if self.isMPI_:
            if sourceObject in self.physics_:
                ind = self.physics_.index(sourceObject)
                self.listingFile_.write(self.physicsData_[ind][1].format("{:^30}".format(""), methodName, PresentTime - self.timeInit_))

    def writeAfter(self, sourceObject, inputTuple, outputTuple, methodName, PresentTime, calculationTime):
        if sourceObject in self.physics_:
            self.sumCalculationTime_ += calculationTime

            ind = self.physics_.index(sourceObject)
            toWrite = ""
            if methodName == "computeTimeStep":
                toWrite += "dt = "
                if outputTuple[0] > 1e2 or outputTuple[0] < 0.1:
                    toWrite += "{:1e}".format(outputTuple[0])
                else:
                    toWrite += "{:5f}".format(outputTuple[0])
                toWrite += " stop = " + ("yes" if outputTuple[1] else "no")
            elif methodName == "initTimeStep":
                toWrite += "dt = "
                if inputTuple[0] > 1e2 or inputTuple[0] < 0.1:
                    toWrite += "{:1e}".format(inputTuple[0])
                else:
                    toWrite += "{:5f}".format(inputTuple[0])
                
            elif methodName == "solveTimeStep":
                toWrite += "succed = " + ("yes" if outputTuple else "no")
            elif methodName == "iterateTimeStep":
                toWrite += "succed = " + ("yes" if outputTuple[0] else "no")
                toWrite += " converged = " + ("yes" if outputTuple[0] else "no")
            elif methodName == "validateTimeStep":
                toWrite += "time = " + "{:5f}".format(sourceObject.presentTime())
            
            if self.isMPI_:
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
                LastLine = LastLine.replace(" ","")
                lastWords = LastLine.split("│")
                if lastWords[ind + 1] != "":
                    self.listingFile_.seek(count - 1, 2)
                    self.listingFile_.write(self.physicsData_[ind][2].format("{:^30}".format(toWrite), methodName, PresentTime - self.timeInit_, calculationTime))
                else:
                    self.listingFile_.seek(0, 2)
                    self.listingFile_.write(self.physicsData_[ind][2].format("{:^30}".format(toWrite), "end", PresentTime - self.timeInit_, calculationTime))
            else:
                self.listingFile_.write(self.physicsData_[ind][2].format("{:^30}".format(toWrite), methodName, PresentTime - self.timeInit_, calculationTime))

        if sourceObject in self.exchangers_:
            ind = self.exchangers_.index(sourceObject)
            self.listingFile_.write(self.exchangersData_[ind][1].format("{:^30.30}".format(self.exchangersData_[ind][0]), methodName, PresentTime - self.timeInit_, calculationTime))

        if sourceObject is self.coupler_ and methodName == "validateTimeStep":
            self.listingFile_.write(self.boxFormat[listingWriter.e_interrupt])
            self.listingFile_.write(self.boxFormat[listingWriter.e_bilan].format("SumCPU = " + "{:6.1e}".format(self.sumCalculationTime_), PresentTime - self.timeInit_, PresentTime - self.timeValid_))  
            self.listingFile_.write(self.boxFormat[listingWriter.e_continue])
            self.timeValid_ = PresentTime
            self.sumCalculationTime_ = 0.
        if sourceObject is self.coupler_ and methodName == "terminate":
            self.listingFile_.write(self.boxFormat[listingWriter.e_term])