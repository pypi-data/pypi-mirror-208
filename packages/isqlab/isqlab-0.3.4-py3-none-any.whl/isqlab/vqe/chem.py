# This code is part of isQ.
# (C) Copyright ArcLight Quantum 2023.
# This code is licensed under the MIT License.

"""
Some useful functions of quantum chemistry.
This file is inspired by TenCirChem and OpenFermion.
"""

import numpy as np
from typing import Tuple
from itertools import product

try:
    from pyscf.scf.hf import RHF
    from pyscf.mcscf import CASCI
    from pyscf import ao2mo, gto
except Exception:
    print("Pyscf is not installed.")

try:
    from openfermion import (
        FermionOperator,
        QubitOperator,
        binary_code_transform,
        parity_code,
    )
    from openfermion.ops.representations import InteractionOperator
    from openfermion.utils import hermitian_conjugated
except Exception:
    print("OpenFermion is not installed.")


TOLERANCE = 1e-8


def spin_orb_from_int(
    int1e: np.ndarray,
    int2e: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:

    n_orb = int1e.shape[0]  # orbitals

    if int1e.shape != (n_orb, n_orb):
        raise ValueError(
            f"Invalid one-boby integral array shape: {int1e.shape}")
    if int2e.shape != (n_orb, n_orb, n_orb, n_orb):
        raise ValueError(
            f"Invalid two-boby integral array shape: {int2e.shape}")

    n_sorb = n_orb * 2  # spin orbitals
    one_body_coefficients = np.zeros((
        n_sorb,
        n_sorb,
    ))
    two_body_coefficients = np.zeros((
        n_sorb,
        n_sorb,
        n_sorb,
        n_sorb,
    ))

    one_body_coefficients[
        :n_orb,
        :n_orb,
    ] = one_body_coefficients[
        n_orb:,
        n_orb:
    ] = int1e

    for p, q, r, s in product(range(n_sorb), repeat=4):
        # a_p^\dagger a_q^\dagger a_r a_s
        if ((p < n_orb) == (s < n_orb)) and ((q < n_orb) == (r < n_orb)):
            # note the different orders of the indices
            two_body_coefficients[p, q, r, s] = int2e[
                p % n_orb,
                s % n_orb,
                q % n_orb,
                r % n_orb,
            ]

    # Truncate
    one_body_coefficients[np.absolute(
        one_body_coefficients) < TOLERANCE] = 0.
    two_body_coefficients[np.absolute(
        two_body_coefficients) < TOLERANCE] = 0.

    return one_body_coefficients, two_body_coefficients


def canonical_mo_coeff(
    mo_coeff: np.ndarray
) -> np.ndarray:
    """
    make the first large element positive
    all elements smaller than 1e-5 is highly unlikely (at least 1e10 basis)
    """
    largest_elem_idx = np.argmax(1e-5 < np.abs(mo_coeff), axis=0)
    largest_elem = mo_coeff[(
        largest_elem_idx,
        np.arange(len(largest_elem_idx)),
    )]

    return mo_coeff * np.sign(largest_elem).reshape(1, -1)


def get_int_from_hf(
    hf: RHF,
    active_space: Tuple = None,
) -> Tuple[np.ndarray, np.ndarray, float]:

    if not isinstance(hf, RHF):
        raise TypeError(f"hf object must be RHF class, got {type(hf)}")

    m = hf.mol
    assert hf.mo_coeff is not None
    hf.mo_coeff = canonical_mo_coeff(hf.mo_coeff)
    if active_space is None:
        nelecas = m.nelectron
        ncas = m.nao
    else:
        nelecas, ncas = active_space
    casci = CASCI(hf, ncas, nelecas)
    int1e, e_core = casci.get_h1eff()
    int2e = ao2mo.restore("s1", casci.get_h2eff(), ncas)

    return int1e, int2e, e_core


def get_int_from_mol(
    mol: gto.M,
    C: np.array,
) -> Tuple[np.ndarray, np.ndarray, float]:
    """Do not use Hartree-Fock molecular coefficients as a
    starting stare."""

    e_core = mol.energy_nuc()
    AO = mol.intor("int2e", aosym=1)
    h = mol.get_hcore()
    # h = mol.intor("int1e_kin") + mol.intor("int1e_nuc")
    # C = hf.mo_coeff
    int1e = C.T @ h @ C
    int2e = np.einsum("uvkl, up, vq, kr, ls -> pqrs", AO, C, C, C, C)
    return int1e, int2e, e_core


def get_molecular_hamiltonian(
    hf: RHF,
) -> InteractionOperator:
    """Get get molecular hamiltonian"""
    int1e, int2e, e_core = get_int_from_hf(hf)
    one_body_coefficients, two_body_coefficients = spin_orb_from_int(
        int1e,
        int2e,
    )
    return InteractionOperator(
        e_core, one_body_coefficients,
        1 / 2 * two_body_coefficients
    )


def ex_op_to_fop(
    ex_op: list,
    with_conjugation: bool = False,
) -> FermionOperator:
    """Excited operators to Fermion operators."""
    if len(ex_op) == 2:
        fop = FermionOperator(f"{ex_op[0]}^ {ex_op[1]}")
    else:
        assert len(ex_op) == 4
        fop = FermionOperator(f"{ex_op[0]}^ {ex_op[1]}^ {ex_op[2]} {ex_op[3]}")
    if with_conjugation:
        fop = fop - hermitian_conjugated(fop)
    return fop


def reverse_qop_idx(
    op: QubitOperator,
    n_qubits: int,
) -> QubitOperator:
    """Reverse qubit operators."""
    ret = QubitOperator()
    for pauli_string, value in op.terms.items():
        # internally QubitOperator assumes ascending index
        pauli_string = tuple(
            reversed([(
                n_qubits - 1 - idx,
                symbol,
            ) for idx, symbol in pauli_string])
        )
        ret.terms[pauli_string] = value
    return ret


def reverse_fop_idx(
    op: FermionOperator,
    n_qubits: int,
) -> FermionOperator:
    ret = FermionOperator()
    for word, v in op.terms.items():
        word = tuple([(n_qubits - 1 - idx, symbol) for idx, symbol in word])
        ret.terms[word] = v
    return ret


def parity(
    fermion_operator: FermionOperator,
    n_modes: int,
    n_elec: int,
) -> QubitOperator:
    """
    Performs parity transformation.

    Parameters
    ----------
    fermion_operator: FermionOperator
        The fermion operator.
    n_modes: int
        The number of modes (spin-orbitals).
    n_elec: int
        The number of electrons.

    Returns
    -------
    qubit_operator: QubitOperator
    """
    qubit_operator = _parity(
        reverse_fop_idx(
            fermion_operator,
            n_modes,
        ),
        n_modes,
    )
    res = 0
    assert n_modes % 2 == 0
    reduction_indices = [n_modes // 2 - 1, n_modes - 1]
    phase_alpha = (-1) ** (n_elec // 2)
    for qop in qubit_operator:
        # qop example: 0.5 [Z1 X2 X3]
        pauli_string, coeff = next(iter(qop.terms.items()))
        # pauli_string example: ((1, 'Z'), (2, 'X'), (3, 'X'))
        # coeff example: 0.5
        new_pauli_string = []
        for idx, symbol in pauli_string:
            is_alpha = idx <= reduction_indices[0]
            if idx in reduction_indices:
                if symbol in ["X", "Y"]:
                    # discard this term because the bit will never change
                    continue
                else:
                    assert symbol == "Z"
                    if is_alpha:
                        coeff *= phase_alpha
                    continue
            if not is_alpha:
                idx -= 1
            new_pauli_string.append((idx, symbol))
        qop.terms = {tuple(new_pauli_string): coeff}
        res += qop
    return res


def _parity(fermion_operator, n_modes):
    return binary_code_transform(fermion_operator, parity_code(n_modes))
