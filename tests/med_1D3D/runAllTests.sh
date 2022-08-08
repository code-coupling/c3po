source env.sh

python test_sequential.py

mpiexec -n 5 python main_mpi_hybrid.py
