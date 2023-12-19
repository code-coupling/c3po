source env.sh

python test_sequential.py

mpiexec -n 3 python main_medmpi.py
