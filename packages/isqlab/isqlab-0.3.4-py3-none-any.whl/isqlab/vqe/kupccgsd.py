# This code is part of isQ.
# (C) Copyright ArcLight Quantum 2023.
# This code is licensed under the MIT License.

"""
kUpCCGSD ansatzs implementation.
This file is inspired by TenCirChem and OpenFermion.
"""

from .ucc import UCC
import numpy as np
from typing import Tuple, List, Optional

try:
    from pyscf import gto
except Exception:
    print("Pyscf is not installed.")


class KUPCCGSD(UCC):
    """
    Run :math:`k`-UpCCGSD calculation.
    The interfaces are similar to :class:`UCCSD <tencirchem.UCCSD>`.
    """

    def __init__(
        self,
        mol: gto.Mole,
        active_space: Tuple[int, int] = None,
        mo_coeff: Optional[np.ndarray] = None,
        k: int = 3,
    ) -> None:
        """Initialize the class with molecular input."""
        super().__init__(
            mol,
            active_space,
            mo_coeff,
        )
        # the number of layers
        self.k = k

        self.ex_ops, self.param_ids, self.init_guess = self.get_ex_ops(
            self.t1,
            self.t2,
        )
        self.num_params = self.param_ids[-1] + 1

    def get_ex_ops(
        self,
        t1: np.ndarray = None,
        t2: np.ndarray = None,
    ) -> Tuple[List[Tuple], List[int], np.ndarray]:
        """
        Get one-body and two-body excitation operators for :math:`k`-UpCCGSD ansatz.
        The excitations are generalized and two-body excitations are restricted to paired ones.
        Initial guesses are generated randomly.
        """
        ex1_ops, ex1_param_id, _ = self.get_ex1_ops()
        ex2_ops, ex2_param_id, _ = self.get_ex2_ops()

        ex_op = []
        param_ids = [-1]
        for _ in range(self.k):
            ex_op.extend(ex2_ops + ex1_ops)
            param_ids.extend([i + param_ids[-1] + 1 for i in ex2_param_id])
            param_ids.extend([i + param_ids[-1] + 1 for i in ex1_param_id])
        init_guess = np.random.rand(max(param_ids) + 1) - 0.5
        return ex_op, param_ids[1:], init_guess

    def get_ex1_ops(
        self,
        t1: np.ndarray = None,
    ) -> Tuple[List[Tuple], List[int], np.ndarray]:
        """
        Get generalized one-body excitation operators.
        """
        assert t1 is None
        no, nv = self.no, self.nv

        ex1_ops = []
        ex1_param_id = [-1]

        for a in range(no + nv):
            for i in range(a):
                # alpha to alpha
                ex_op_a = (no + nv + a, no + nv + i)
                # beta to beta
                ex_op_b = (a, i)
                ex1_ops.extend([ex_op_a, ex_op_b])
                ex1_param_id.extend([ex1_param_id[-1] + 1] * 2)

        ex1_init_guess = np.zeros(max(ex1_param_id) + 1)
        return ex1_ops, ex1_param_id[1:], ex1_init_guess

    def get_ex2_ops(
        self,
        t2: np.ndarray = None,
    ) -> Tuple[List[Tuple], List[int], np.ndarray]:
        """
        Get generalized paired two-body excitation operators.
        """

        assert t2 is None
        no, nv = self.no, self.nv

        ex2_ops = []
        ex2_param_id = [-1]

        for a in range(no + nv):
            for i in range(a):
                # i correspond to a and j correspond to b, as in PySCF convention
                # otherwise the t2 amplitude has incorrect phase
                # paired
                ex_op_ab = (a, no + nv + a, no + nv + i, i)
                ex2_ops.append(ex_op_ab)
                ex2_param_id.append(ex2_param_id[-1] + 1)

        ex2_init_guess = np.zeros(max(ex2_param_id) + 1)
        return ex2_ops, ex2_param_id[1:], ex2_init_guess
