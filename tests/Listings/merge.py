# -*- coding: utf-8 -*-
from __future__ import print_function

import C3PO

file1 = "listingGeneral0.log"
file2 = "listingGeneral1.log"
file3 = "listingGeneralMerged.log"
C3PO.mergeListing([file1, file2], file3)

