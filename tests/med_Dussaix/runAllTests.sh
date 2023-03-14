source env.sh

python test_sequential.py

mpiexec -n 3 python main_mpi_masterWorkers.py

mpiexec -n 2 python main_mpi_collaborative.py

mpiexec -n 4 python main_medmpi_collaborative.py
