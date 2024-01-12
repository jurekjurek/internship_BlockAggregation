import matplotlib.pyplot as plt

def draw_quantum_circuits(circuits):
    fig, ax = plt.subplots()

    # Set the y-coordinates for each qubit
    num_qubits = len(circuits[0])
    qubit_positions = {qubit: i for i, qubit in enumerate(range(num_qubits, 0, -1))}

    # Plot each circuit
    for circuit in circuits:
        for i in range(num_qubits - 1):
            # Get the coordinates of the current and next qubit in the current circuit
            current_qubit = circuit[i]
            next_qubit = circuit[i + 1]

            # Plot a line connecting the current and next qubit
            ax.plot([i, i + 1], [qubit_positions[current_qubit], qubit_positions[next_qubit]], marker='o', color='b')

    # Customize plot appearance
    ax.set_yticks(range(num_qubits))
    ax.set_yticklabels([f'Qubit {i+1}' for i in range(num_qubits)])
    ax.set_xlabel('Quantum Circuit')
    ax.set_ylabel('Qubit')

    plt.show()

# Example circuits
circuits = [
    [1, 2, 3, 4, 5, 6, 7, 8],
    [8, 7, 6, 5, 4, 3, 2, 1],
    [4, 2, 1, 3, 8, 7, 6, 5],
    # Add more circuits as needed
]

draw_quantum_circuits(circuits)
