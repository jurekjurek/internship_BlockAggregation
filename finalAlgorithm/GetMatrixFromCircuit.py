import json
import matplotlib.pyplot as plt
import numpy as np
from itertools import product

from qiskit import QuantumCircuit, assemble
from qiskit.circuit import Gate, Qubit
from qiskit.visualization import plot_state_city

# from umz_qiskit_backend.qiskit_backend import UmzBackend, RedTrapBackend, UmzSimulatorBackend


from IPython.display import display, Latex
from collections.abc import Iterable



'''
Stuff we need for print_matrix, and for the function of interest, which is calculate_matrix in the end 
'''
def is_iterable(obj):
    return isinstance(obj, Iterable)

def format_imag_part(imag_part, digits) -> str:
    if imag_part == 1:
        return "i"
    elif imag_part == -1:
        return "-i"
    elif imag_part == 0:
        return "0"
    return f"{np.round(imag_part, digits)}i"

def format_real_part(real_part, digits) -> str:
    if real_part == 1:
        return "1"
    elif real_part == -1:
        return "-1"
    elif real_part == 0:
        return "0"
    return f"{np.round(real_part, digits)}"

def complex_format(value, digits = 2) -> str:
    if isinstance(value, complex):
        real_part = np.round(value.real, digits) if value.real != 0 else 0
        imag_part = np.round(value.imag, digits) if value.imag != 0 else 0
        if real_part == 0:
            return format_imag_part(imag_part, digits)
        else:
            real_part_repr = format_real_part(real_part, digits)
            imag_part_repr = format_imag_part(imag_part, digits)
            if imag_part_repr == "0":
                return real_part_repr
            elif imag_part_repr[0] == "-":
                return f"{real_part_repr} - {imag_part_repr[1:]}"
            return f"{real_part_repr} + {imag_part_repr}"
    elif isinstance(value, (int, float)):
        return "0" if value == 0 else f"{np.round(value, digits)}"
    else:
        return str(value)



def print_matrix(matrix: np.ndarray):
    matrix_latex = "\\begin{pmatrix}\n"
    for row in matrix:
        if not is_iterable(row):
            row_str = complex_format(row)
        else:
            row_str = " & ".join([complex_format(elem) for elem in row])
        matrix_latex += f"{row_str} \\\\\n"
    matrix_latex += "\\end{pmatrix}"

    display(Latex(matrix_latex))





def get_binary_representation(integer: int, size: int) -> str:
    """Converts an integer to its binary representation with leading zeros, ensuring a fixed size.

    This function takes an integer and converts it to its binary representation.
    Leading zeros are added to the binary representation to ensure that the resulting
    string always has the specified size. If the binary representation is too long to fit
    within the desired size, a ValueError exception is raised.

    Parameters
    ----------
    integer : int
        The integer to be converted to binary.
    size : int
        The desired size of the binary representation string.

    Returns
    -------
    str
        The binary representation of the integer as a string with leading zeros.

    Raises
    ------
    ValueError
        If the binary representation is too large for the given size.

    Examples
    --------
    >>> get_binary_representation(5, 8)
    '00000101'

    >>> get_binary_representation(10, 6)
    '010101'

    >>> get_binary_representation(255, 8)
    '11111111'
    """
    binary_string = bin(integer)[2:]  # Remove '0b' prefix from binary string

    if len(binary_string) > size:
        raise ValueError("Binary representation too large for the given size")

    padded_binary_string = binary_string.rjust(size, '0')
    return padded_binary_string

def calculate_new_col(col: int, index_map: dict) -> int:
    """Calculates the new column for column col, given an index_map
    which maps old qubit indices to their new qubit indices.

    The column in a density matrix shaped matrix (2^n x 2^n) that transforms
    a representation of a state vector (size 2^n) where element i represents the
    qubit state i.to_binary(), e.g. i = 3 corresponds to state 0..011. The
    index_map maps each position in the binary representation to a new position.
    The resulting binary value is then converted back to a decimal value which
    corresponds to the new column that is returned.

    Parameters
    ----------
    col : int
        Old column in a matrix of size 2^n x 2^n.
    index_map : dict
        Map which maps the old qubit index to the new qubit index.

    Returns
    -------
    int
        New column.
    """
    num_qb = len(index_map.values())
    
    # get the binary representation of the old column
    state = get_binary_representation(col, num_qb)

    # sort the index_map to be ascending in the values to
    # simply iterate over it and build up the new state
    sorted_index_map = dict(sorted(index_map.items(), key=lambda item: item[1]))
    
    new_state = ''
    for old_index in sorted_index_map.keys():
        new_state += state[old_index]

    return int(new_state, base=2)

def calculate_swap_matrix(index_map: dict, circuit_qubits: list[Qubit]) -> np.ndarray:
    """Calculates the swap matrix for rearranging qubits based on an index map.

    This function calculates the swap matrix that rearranges qubits in a circuit
    based on a given index map. The index map specifies how qubits should be shifted
    to new positions.

    Parameters
    ----------
    index_map : dict
        A dictionary that maps old qubit indices to new qubit indices.
    circuit_qubits : list of Qubit
        The list of qubits in the circuit.

    Returns
    -------
    np.ndarray
        The swap matrix for rearranging qubits.
    """
    swap_matrix = np.identity(2**len(circuit_qubits))

    swapped_cols = set()  # Keep track of columns that have been swapped

    for col in range(2**len(circuit_qubits)):
        if col in swapped_cols:
            continue  # Skip columns that have already been swapped

        new_col = calculate_new_col(col, index_map)
        # print(f'Mapping column {col} to {new_col}')
        
        # Swap columns
        tmp = swap_matrix[col].copy()  # Create a copy of the column
        swap_matrix[col] = swap_matrix[new_col]
        swap_matrix[new_col] = tmp

        # Update swapped_cols
        swapped_cols.add(col)
        swapped_cols.add(new_col)

    return swap_matrix

def calculate_gate_matrix(gate: Gate, qubits: list[Qubit], circuit_qubits: list[Qubit]):
    """Calculates the global gate matrix for the given gate and qubits in a circuit.

    This function calculates the global gate matrix for a specified gate and its associated qubits
    in a circuit. The calculation involves considering the qubit positions, handling swaps if necessary,
    and constructing the final global gate matrix.

    Parameters
    ----------
    gate : Gate
        The quantum gate to be applied.
    qubits : list of Qubit
        The qubits on which the gate is applied.
    circuit_qubits : list of Qubit
        All qubits in the circuit.

    Returns
    -------
    np.ndarray
        The resulting global gate matrix.
    """
    # determine the global matrix for this gate:
    global_gate_matrix = np.identity(2**len(circuit_qubits), dtype=complex)
    
    index_map = {i: i for i in range(len(circuit_qubits))}

    if len(qubits) == 2:
        # determine the indices
        qb0_index = circuit_qubits.index(qubits[0])
        qb1_index = circuit_qubits.index(qubits[1])

        # if the two qubits are not adjacend, transfer the quantum information
        # using swap gates
        if np.abs(qb0_index - qb1_index) != 1:
            new_qb1_index = qb0_index + 1
            index_map = {}
            for i in range(len(circuit_qubits)):
                if i <= qb0_index:
                    # qubits prior to qb0 stay in place
                    index_map[i] = i
                elif i == qb1_index:
                    # qb1 is mapped to its new position
                    index_map[qb1_index] = new_qb1_index
                else:
                    # qubits after qb0 (except qb1) are shifted one to the right
                    index_map[i] = i + 1
    
    # replace the submatrices for a certain qubit
    locals = [] # list of local matrices
    i = 0
    used_qbs = set() # keep track of qubits that participated in a gate
    while i < len(circuit_qubits):
        qb = circuit_qubits[i]
        i += 1
        if qb in used_qbs:
            continue
        if qb in qubits:
            locals.append(gate.to_matrix())

            # add all qubits of the gate to used_qubits
            for q in qubits:
                used_qbs.add(q)
        else:
            locals.append(np.identity(2, dtype=complex))

    if len(locals) > 1:
        global_gate_matrix = np.kron(locals[0], locals[1])
        for local in locals[2:]:
            global_gate_matrix = np.kron(global_gate_matrix, local)
    else:
        global_gate_matrix = locals[0]
    
    swap_matrix = calculate_swap_matrix(index_map, circuit_qubits)

    return np.matmul(swap_matrix, np.matmul(global_gate_matrix, swap_matrix))

def calculate_circuit_matrix(circuit: QuantumCircuit):
    """Calculates the matrix representation of a quantum circuit.

    This function calculates the matrix representation of a given quantum circuit.
    It applies the gates in the circuit's data list to construct the circuit matrix.

    Parameters
    ----------
    circuit : QuantumCircuit
        The quantum circuit to calculate the matrix for.

    Returns
    -------
    np.ndarray
        The matrix representation of the quantum circuit.
    """
    circuit_matrix = np.identity(2**len(circuit.qubits))
    for instruction in circuit.data[::-1]:
        gate: Gate = instruction[0]
        qubits: list[Qubit] = instruction[1:][0]

        global_gate_matrix = calculate_gate_matrix(gate, qubits, circuit.qubits)
        # print_matrix(global_gate_matrix)
        circuit_matrix = np.matmul(global_gate_matrix, circuit_matrix)
    
    return circuit_matrix



circ = QuantumCircuit(2)
circ.rx(np.pi, 0)

num_qb = circ.num_qubits




circuit_matrix = calculate_circuit_matrix(circ)
print('Circuit matrix: ')
print_matrix(np.round(circuit_matrix, 10))

input_state = np.zeros(2**num_qb, dtype=complex)
input_state[0] = 1

output_state = np.array([1, 0])# np.matmul(circuit_matrix, input_state)
print('expected output state: ')
print_matrix(np.round(output_state, 10))
# fidelity