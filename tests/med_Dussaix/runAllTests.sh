source env.sh

python3 test_sequential.py

mpiexec -n 3 python3 test_mpi_masterWorkers.py

mpiexec -n 2 python3 test_mpi_collaborative.py
