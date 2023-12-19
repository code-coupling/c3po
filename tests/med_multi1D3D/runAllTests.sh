source env.sh

python test_sequential.py

python test_reloading.py

mpiexec -n 5 python main_medmpi_collaborative.py

mpiexec -n 5 python main_medmpi_reloading.py
