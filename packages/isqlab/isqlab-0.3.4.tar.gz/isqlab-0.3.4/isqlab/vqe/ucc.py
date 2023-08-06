# This code is part of isQ.
# (C) Copyright ArcLight Quantum 2023.
# This code is licensed under the MIT License.

"""
UCC ansatzs implementation.
This file is inspired by TenCirChem and OpenFermion.
"""

from isqlab.circuits import QuantumCircuit
from isqlab.vqe.chem import ex_op_to_fop, reverse_qop_idx, canonical_mo_coeff
import numpy as np
from typing import Tuple, List, Union, Optional, Sequence

try:
    from pyscf.cc.addons import spatial2spin
    from pyscf import gto
except Exception:
    print("Pyscf is not installed.")

try:
    from openfermion import jordan_wigner
except Exception:
    print("OpenFermion is not installed.")


class UCC:
    """Basic class for couple cluster"""

    def __init__(
        self,
        mol: gto.Mole,
        active_space: Tuple[int, int] = None,
        mo_coeff: Optional[np.ndarray] = None,
    ) -> None:

        self.mol = mol
        # self.mol = mol.copy()
        if active_space is None:
            active_space = (mol.nelectron, int(mol.nao))

        self.n_qubits = 2 * active_space[1]
        self.active_space = active_space
        self.n_elec = active_space[0]
        self.active = active_space[1]
        self.inactive_occ = mol.nelectron // 2 - active_space[0] // 2
        self.inactive_vir = mol.nao - active_space[1] - self.inactive_occ
        self.frozen_idx = list(range(self.inactive_occ)) + \
            list(range(mol.nao - self.inactive_vir, mol.nao))

        # classical quantum chemistry
        self.e_nuc = mol.energy_nuc()
        # initial guess
        self.t1 = self.t2 = None

        if mo_coeff is not None:
            # use user defined coefficient
            self.mo_coeff = canonical_mo_coeff(mo_coeff)

        self.ex_ops = None
        self.param_idx = None

    @property
    def no(self) -> int:
        """The number of occupied orbitals."""
        return self.n_elec // 2

    @property
    def nv(self) -> int:
        """The number of virtual (unoccupied orbitals)."""
        return self.active - self.no

    @staticmethod
    def evolve_pauli(
        circuit: QuantumCircuit,
        pauli_string: Tuple,
        theta: str,
        value: complex,
    ) -> None:
        # pauli_string in openfermion.QubitOperator.terms format
        for idx, symbol in pauli_string:
            if symbol == "X":
                circuit.H(idx)
            elif symbol == "Y":
                circuit.SD(idx)
                circuit.H(idx)
            elif symbol == "Z":
                continue
            else:
                raise ValueError(f"Invalid Pauli String: {pauli_string}")

        for i in range(len(pauli_string) - 1):
            circuit.CNOT(pauli_string[i][0], pauli_string[i + 1][0])

        circuit.RZ(str(-2 * value.imag) + "*" + theta, pauli_string[-1][0])

        for i in reversed(range(len(pauli_string) - 1)):
            circuit.CNOT(pauli_string[i][0], pauli_string[i + 1][0])

        for idx, symbol in pauli_string:
            if symbol == "X":
                circuit.H(idx)
            elif symbol == "Y":
                circuit.H(idx)
                circuit.S(idx)
            elif symbol == "Z":
                continue
            else:
                raise ValueError(f"Invalid Pauli String: {pauli_string}")

    @staticmethod
    def get_init_circuit(
        n_qubits: int,
        n_elec: int,
        init_state: Union[QuantumCircuit, str] = "hf",
    ) -> QuantumCircuit:

        if isinstance(init_state, QuantumCircuit):
            return init_state
        if init_state in ["hf", "Hf", "HF"]:
            circuit = QuantumCircuit(n_qubits)
            for i in range(n_elec // 2):
                circuit.X(i)
                circuit.X(n_qubits // 2 + i)

        return circuit

    def get_circuit(
        self,
        params_name: str = "theta",
        ex_ops: list = None,
        param_ids: Sequence = None,
        init_state: Union[QuantumCircuit, str] = None,
        trotter: bool = True,
    ) -> QuantumCircuit:

        if ex_ops is None:
            ex_ops = self.ex_ops

        if param_ids is None:
            param_ids = self.param_ids

        circuit = QuantumCircuit(self.n_qubits)

        if init_state:
            init_circuit = self.get_init_circuit(
                self.n_qubits, self.n_elec, init_state)
            circuit.extend(init_circuit)

        for param_id, f_idx in zip(param_ids, ex_ops):
            theta = f"{params_name}[{param_id}]"
            fop = ex_op_to_fop(f_idx, with_conjugation=True)
            qop = reverse_qop_idx(jordan_wigner(fop), self.n_qubits)
            if trotter:
                for pauli_string, value in qop.terms.items():
                    self.evolve_pauli(circuit, pauli_string, theta, value)
            else:
                raise NotImplementedError("multicontrol_ry")
                # TODO:
                # https://arxiv.org/pdf/2005.14475.pdf
                # circuit = evolve_excitation(
                #     circuit, f_idx, qop, 2 * theta, decompose_multicontrol)
        return circuit

    def get_ex_ops(
        self,
        t1: np.ndarray = None,
        t2: np.ndarray = None,
    ):
        """Abs method to be implemented"""
        raise NotImplementedError

    def get_ex1_ops(
        self,
        t1: np.ndarray = None,
    ) -> Tuple[List[Tuple], List[int], List[float]]:
        """Get one-body excitation operators."""
        # single excitations
        no, nv = self.no, self.nv
        if t1 is None:
            t1 = np.zeros((no, nv))

        t1 = spatial2spin(t1)

        ex1_ops = []
        # unique parameters. -1 is a place holder
        ex1_param_ids = [-1]
        ex1_init_guess = []
        for i in range(no):
            for a in range(nv):
                # alpha to alpha
                ex_op_a = (2 * no + nv + a, no + nv + i)
                # beta to beta
                ex_op_b = (no + a, i)
                ex1_ops.extend([ex_op_a, ex_op_b])
                ex1_param_ids.extend([ex1_param_ids[-1] + 1] * 2)
                ex1_init_guess.append(t1[i, a])

        return ex1_ops, ex1_param_ids[1:], ex1_init_guess

    def get_ex2_ops(
        self,
        t2: np.ndarray = None,
    ) -> Tuple[List[Tuple], List[int], List[float]]:
        """Get two-body excitation operators."""

        # t2 in oovv 1212 format
        no, nv = self.no, self.nv
        if t2 is None:
            t2 = np.zeros((no, no, nv, nv))

        t2 = spatial2spin(t2)

        def alpha_o(_i):
            return no + nv + _i

        def alpha_v(_i):
            return 2 * no + nv + _i

        def beta_o(_i):
            return _i

        def beta_v(_i):
            return no + _i

        # double excitations
        ex_ops = []
        ex2_param_ids = [-1]
        ex2_init_guess = []
        # 2 alphas or 2 betas
        for i in range(no):
            for j in range(i):
                for a in range(nv):
                    for b in range(a):
                        # i correspond to a and j correspond to b, as in PySCF convention
                        # otherwise the t2 amplitude has incorrect phase
                        # 2 alphas
                        ex_op_aa = (
                            alpha_v(b),
                            alpha_v(a),
                            alpha_o(i),
                            alpha_o(j),
                        )
                        # 2 betas
                        ex_op_bb = (
                            beta_v(b),
                            beta_v(a),
                            beta_o(i),
                            beta_o(j),
                        )
                        ex_ops.extend([
                            ex_op_aa,
                            ex_op_bb,
                        ])
                        ex2_param_ids.extend([ex2_param_ids[-1] + 1] * 2)
                        ex2_init_guess.append(t2[2 * i, 2 * j, 2 * a, 2 * b])
        assert len(ex_ops) == 2 * (no * (no - 1) / 2) * (nv * (nv - 1) / 2)
        # 1 alpha + 1 beta
        for i in range(no):
            for j in range(i + 1):
                for a in range(nv):
                    for b in range(a + 1):
                        # i correspond to a and j correspond to b, as in PySCF convention
                        # otherwise the t2 amplitude has incorrect phase
                        if i == j and a == b:
                            # paired
                            ex_op_ab = (
                                beta_v(a),
                                alpha_v(a),
                                alpha_o(i),
                                beta_o(i),
                            )
                            ex_ops.append(ex_op_ab)
                            ex2_param_ids.append(ex2_param_ids[-1] + 1)
                            ex2_init_guess.append(
                                t2[2 * i, 2 * i + 1, 2 * a, 2 * a + 1],
                            )
                            continue
                        # simple reflection
                        ex_op_ab1 = (
                            beta_v(b),
                            alpha_v(a),
                            alpha_o(i),
                            beta_o(j),
                        )
                        ex_op_ab2 = (
                            alpha_v(b),
                            beta_v(a),
                            beta_o(i),
                            alpha_o(j),
                        )
                        ex_ops.extend([
                            ex_op_ab1,
                            ex_op_ab2,
                        ])
                        ex2_param_ids.extend([ex2_param_ids[-1] + 1] * 2)
                        ex2_init_guess.append(
                            t2[2 * i, 2 * j + 1, 2 * a, 2 * b + 1],
                        )
                        if (i != j) and (a != b):
                            # exchange alpha and beta
                            ex_op_ab3 = (
                                beta_v(a),
                                alpha_v(b),
                                alpha_o(i),
                                beta_o(j),
                            )
                            ex_op_ab4 = (
                                alpha_v(a),
                                beta_v(b),
                                beta_o(i),
                                alpha_o(j),
                            )
                            ex_ops.extend([
                                ex_op_ab3,
                                ex_op_ab4,
                            ])
                            ex2_param_ids.extend([ex2_param_ids[-1] + 1] * 2)
                            ex2_init_guess.append(
                                t2[2 * i, 2 * j + 1, 2 * b, 2 * a + 1],
                            )

        return ex_ops, ex2_param_ids[1:], ex2_init_guess
