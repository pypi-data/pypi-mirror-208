# This code is part of isQ.
# (C) Copyright ArcLight Quantum 2023.
# This code is licensed under the MIT License.

"""Molecular Hamiltonian measurement."""

from isqlab.circuits import QuantumCircuit, QuantumCircuitError
from typing import Tuple, List
import numpy as np

try:
    from openfermion.ops.operators import QubitOperator
except Exception:
    print("OpenFermion is not installed.")

try:
    import jax.numpy as jnp
    HAS_JAX = True
except Exception:
    HAS_JAX = False

try:
    import torch
    HAS_TORCH = True
except Exception:
    HAS_TORCH = False

try:
    from autograd import numpy as anp
    HAS_AUTOGRAD = True
except Exception:
    HAS_AUTOGRAD = False


def hamiltonian_measure(
    circuit: QuantumCircuit,
    qubit_hamiltonian: QubitOperator,
    **params,
) -> np.float64:
    """transform qubit hamiltonian to pauli measurements."""

    coeffs, gates = _openfermion_to_pauligates(qubit_hamiltonian)

    if circuit.use_hardware or circuit.method in ["simulator"]:
        measure_results = [1.0, ]
        for gate in gates:
            circuit.pauli(gate, format="openfermion")
            # circuit.pauli(gate, format="str")
            measure_results.append(circuit.pauli_measure(**params))
        return np.dot(measure_results, coeffs)

    # TODO: anp.array type??? support
    # elif circuit.method == "autograd":
    #     measure_results = anp.zeros(len(gates) + 1)
    #     measure_results[0] = 1.0
    #     for idx, gate in enumerate(gates):
    #         circuit.pauli(gate, format="openfermion")
    #         # circuit.pauli(gate, format="str")
    #         measure_results[idx+1] = circuit.pauli_measure(**params)
    #     return anp.dot(measure_results, anp.array(coeffs))

    elif circuit.method == "autograd":
        measure_results = [1.0, ]
        for gate in gates:
            circuit.pauli(gate, format="openfermion")
            # circuit.pauli(gate, format="str")
            measure_results.append(circuit.pauli_measure(**params))
        return anp.dot(anp.array(measure_results), anp.array(coeffs))

    # TODO: jnp.array type??? support
    # elif circuit.method == "jax":
    #     measure_results = jnp.zeros(len(gates) + 1)
    #     measure_results = measure_results.at[0].set(1.0)
    #     for idx, gate in enumerate(gates):
    #         circuit.pauli(gate, format="openfermion")
    #         # circuit.pauli(gate, format="str")
    #         measure_results = measure_results.at[idx + 1].set(
    #             circuit.pauli_measure(**params),
    #         )
    #     return jnp.vdot(measure_results, jnp.array(coeffs))

    elif circuit.method == "jax":
        measure_results = [1.0, ]
        for gate in gates:
            circuit.pauli(gate, format="openfermion")
            # circuit.pauli(gate, format="str")
            measure_results.append(circuit.pauli_measure(**params))
        return jnp.vdot(jnp.array(measure_results), jnp.array(coeffs))

    elif circuit.method in ["torch", "pytorch"]:
        measure_results = torch.zeros(len(gates) + 1, dtype=torch.float)
        # dtype
        measure_results[0] = 1.0
        for idx, gate in enumerate(gates):
            circuit.pauli(gate, format="openfermion")
            measure_results[idx+1] = circuit.pauli_measure(**params)
        return torch.dot(
            measure_results,
            torch.tensor(coeffs).type_as(measure_results)
        )

    else:
        raise QuantumCircuitError("Method is not implemented yet.")


def _openfermion_to_pauligates(
    qubit_hamiltonian: QubitOperator,
) -> Tuple[List[float], List[str]]:
    """
    extract coefficients and gates of qubit hamiltonian.
    """
    coeffs = []
    gates = []
    for gate, coeff in qubit_hamiltonian.terms.items():
        coeffs.append(coeff)
        gates.append(gate)
    return coeffs, gates[1:]

    # hamiltonian_strs = str(qubit_hamiltonian).split("\n")
    # hamiltonian_strs[-1] += " +"
    #
    # coeffs = []
    # gates = []
    #
    # for hamiltonian_str in hamiltonian_strs:
    #     hamiltonian_ele = hamiltonian_str.split(" ")
    #     coeffs.append(float(hamiltonian_ele[0]))
    #     gates.append("".join(hamiltonian_ele[1:-1])[1:-1])
    # # the first gate is None
    # return coeffs, gates[1:]
