source env.sh

python test_sequential.py

python test_shift1DFields.py

mpiexec -n 5 python main_mpi_hybrid.py

mpiexec -n 5 python main_mpi_remapper.py
