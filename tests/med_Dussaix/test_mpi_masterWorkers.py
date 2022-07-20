# -*- coding: utf-8 -*-
from __future__ import print_function, division

from pytest_easyMPI import mpi_parallel

def main_masterWorkers():
    import mpi4py.MPI as mpi

    comm = mpi.COMM_WORLD
    rank = comm.Get_rank()

    if rank == 0:
        from tests.med_Dussaix.main_master import main_master
        main_master()
    elif rank == 1:
        from tests.med_Dussaix.main_workerThermo import main_workerThermo
        main_workerThermo()
    elif rank == 2:
        from tests.med_Dussaix.main_workerNeutro import main_workerNeutro
        main_workerNeutro()

@mpi_parallel(3)
def test_masterWorkers():
    main_masterWorkers()

if __name__ == "__main__":
    main_masterWorkers()
