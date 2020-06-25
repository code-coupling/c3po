source env.sh

python main_sequential.py 
 
mpiexec -n 1 python main_master.py : -n 1 python main_workerThermo.py : -n 1 python main_workerNeutro.py 

mpiexec -n 2 python main_collaborative.py 
