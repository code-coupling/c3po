source env.sh

python3 test_sequential.py

mpiexec -n 5 python3 test_mpi_hybrid.py
