source env.sh

python test_patterns.py

mpiexec -n 4 python main_mpi_valueBcast.py

mpiexec -n 2 python main_mpi_clean.py
