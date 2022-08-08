# -*- coding: utf-8 -*-
from __future__ import print_function

from pytest_easyMPI import mpi_parallel

from tests.listings.main_mpi_collaborative import main_mpi_collaborative


@mpi_parallel(2)
def test_collaborative():
    main_mpi_collaborative()
    from mpi4py import MPI
    import os
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    if rank == 0:
        try:
            os.remove("first.log")
        except:
            pass
        try:
            os.remove("second.log")
        except:
            pass
        try:
            os.remove("listingFirst.log")
        except:
            pass
        try:
            os.remove("listingSecond.log")
        except:
            pass
        try:
            os.remove("listingGeneral0.log")
        except:
            pass
        try:
            os.remove("listingGeneral1.log")
        except:
            pass
        try:
            os.remove("listingGeneralMerged.log")
        except:
            pass

