# This code is part of isQ.
# (C) Copyright ArcLight Quantum 2023.
# This code is licensed under the MIT License.

"""
Symmetry preserving ansatzs implementation.
This file is inspired by PennyLane.
"""

from ..circuits import QuantumCircuit
from typing import Sequence


def single_excitation(
    circuit: QuantumCircuit,
    qubit_idx: Sequence[int],
    theta: str = "theta",
) -> None:
    """Single excitation rotation."""
    if len(qubit_idx) != 2:
        raise ValueError(
            "four qubits are required to apply the operation.",
        )

    circuit.td(qubit_idx[0])
    circuit.h(qubit_idx[0])
    circuit.s(qubit_idx[0])
    circuit.td(qubit_idx[1])
    circuit.sd(qubit_idx[1])
    circuit.h(qubit_idx[1])
    circuit.cnot(qubit_idx[1], qubit_idx[0])
    circuit.rz(theta + "* (-0.5)", qubit_idx[0])
    circuit.ry(theta + "* 0.5", qubit_idx[1])
    circuit.cnot(qubit_idx[1], qubit_idx[0])
    circuit.sd(qubit_idx[0])
    circuit.h(qubit_idx[0])
    circuit.t(qubit_idx[0])
    circuit.h(qubit_idx[1])
    circuit.s(qubit_idx[1])
    circuit.t(qubit_idx[1])


def double_excitation(
    circuit: QuantumCircuit,
    qubit_idx: Sequence[int],
    theta: str = "theta",
) -> None:
    """Double excitation rotation."""

    if len(qubit_idx) != 4:
        raise ValueError(
            "four qubits are required to apply the operation.",
        )

    circuit.cnot(qubit_idx[2], qubit_idx[3])
    circuit.cnot(qubit_idx[0], qubit_idx[2])
    circuit.h(qubit_idx[3])
    circuit.h(qubit_idx[0])
    circuit.cnot(qubit_idx[2], qubit_idx[3])
    circuit.cnot(qubit_idx[0], qubit_idx[1])
    circuit.ry(theta + "/ 8", qubit_idx[1])
    circuit.ry(theta + "/ (-8)", qubit_idx[0])
    circuit.cnot(qubit_idx[0], qubit_idx[3])
    circuit.h(qubit_idx[3])
    circuit.cnot(qubit_idx[3], qubit_idx[1])
    circuit.ry(theta + "/ 8", qubit_idx[1])
    circuit.ry(theta + "/ (-8)", qubit_idx[0])
    circuit.cnot(qubit_idx[2], qubit_idx[1])
    circuit.cnot(qubit_idx[2], qubit_idx[0])
    circuit.ry(theta + "/ (-8)", qubit_idx[1])
    circuit.ry(theta + "/ 8", qubit_idx[0])
    circuit.cnot(qubit_idx[3], qubit_idx[1])
    circuit.h(qubit_idx[3])
    circuit.cnot(qubit_idx[0], qubit_idx[3])
    circuit.ry(theta + "/ (-8)", qubit_idx[1])
    circuit.ry(theta + "/ 8", qubit_idx[0])
    circuit.cnot(qubit_idx[0], qubit_idx[1])
    circuit.cnot(qubit_idx[2], qubit_idx[0])
    circuit.h(qubit_idx[0])
    circuit.h(qubit_idx[3])
    circuit.cnot(qubit_idx[0], qubit_idx[2])
    circuit.cnot(qubit_idx[2], qubit_idx[3])
