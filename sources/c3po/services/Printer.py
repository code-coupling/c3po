# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class Printer. """
from __future__ import print_function, division


class Printer(object):
    """! INTERNAL.

    Printer writes strings in the standard output.
    """

    def __init__(self, printLevel):
        """! Build a Printer.

        @param printLevel (int) Set the print level (0: None, 1: written lines are overwritten by the following ones, 2: usual printing).
        """
        self._printLevel = printLevel
        self._lastPrinted = ""

    @property
    def _endOfLine(self):
        """! INTERNAL """
        return "\r" if self._printLevel == 1 else "\n"

    def setPrintLevel(self, level):
        """! Set the print level (0: None, 1: written lines are overwritten by the following ones, 2: usual printing).

        @param level (int) integer in range [0;2].
        """
        if not level in [0, 1, 2]:
            raise Exception("Printer.setPrintLevel level should be one of [0, 1, 2]!")
        self._printLevel = level

    def getPrintLevel(self):
        """! Return the print level previously set.

        @return (int) The print level.
        """
        return self._printLevel

    def print(self, toPrint, tmplevel=None):
        """! Write the provided string in standard output.

        @param toPrint (string) string to print.
        @param tmplevel (int) printing level to apply to this printing only.
        """
        previousLevel = self._printLevel
        if tmplevel is not None:
            self._printLevel = tmplevel
        try:
            print("\x1b[K{}".format(toPrint), end=self._endOfLine)
            self._lastPrinted = toPrint
        finally:
            if tmplevel is not None:
                self._printLevel = previousLevel

    def reprint(self, tmplevel=None):
        """! Rewrite the last printed string in standard output.

        @param tmplevel (int) printing level to apply to this printing only.
        """
        self.print(self._lastPrinted, tmplevel)


def warning(message):
    """! Write a warning message.

    @param message (string) message of the warning.
    """
    print('\x1b[1;33m' + "WARNING : " + message + '\x1b[0m')
