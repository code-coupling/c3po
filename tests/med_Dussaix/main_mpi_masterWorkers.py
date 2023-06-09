# -*- coding: utf-8 -*-
from __future__ import print_function, division


def main_mpi_masterWorkers():
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


if __name__ == "__main__":
    main_mpi_masterWorkers()
