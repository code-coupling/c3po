source env.sh

python3 main_sequential.py

mpiexec -n 1 python3 main_master.py : -n 1 python3 main_workerThermo.py : -n 1 python3 main_workerNeutro.py

mpiexec -n 2 python3 main_collaborative.py
