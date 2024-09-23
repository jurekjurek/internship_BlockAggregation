In this project, the experimental realisation of quantum computers in terms of ions being moved is optimised. 
In the process of carrying out a quantum algorithm on a quantum circuit, or even a quantum circuit in general, qubits (ions with two accesable energy levels) have to be moved around to be entangled with each other. 
This project optimises this scheme with the objective of minimising the overall movement of the qubits. 

Two different optimising algorithms are applied to the problem: 
- The tabu search, in which a list of before encountered values is kept. If a solution in this list is encountered in one iteration of the algorithm, this temporary solution is not considered.

A genetic algorithm, treating the individual schemes after which qubits are moved as individuals. An algorithm mimicing evolution is applied to search for the optimal scheme. 

The algorithms are tested on up to 40 qubits, with 40 gates in the circuits that are to be carried out. 

