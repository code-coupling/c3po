# -*- coding: utf-8 -*-
from __future__ import print_function

import C3PO

file1 = open("listingGeneral0.log", "r")
file2 = open("listingGeneral1.log", "r")
file3 = open("listingGeneralMerged.log", "wb+")
C3PO.mergeListing([file1, file2], file3)

file1.close()
file2.close()
file3.close()

