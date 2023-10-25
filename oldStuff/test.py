import numpy as np
from qiskit import *
from qiskit import Aer

backend = Aer.get_backend('unitary_simulator')
#prepare 2qubits
circ = QuantumCircuit(2)
circ.h(0)
circ.x(1)

job = execute(circ, backend)
result = job.result()
print(circ)
print(result.get_unitary(circ, decimals=3))


