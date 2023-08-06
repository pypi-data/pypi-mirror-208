# This code is part of isQ.
# (C) Copyright ArcLight Quantum 2023.
# This code is licensed under the MIT License.

"""
UCCSD ansatzs implementation.
This file is inspired by TenCirChem and OpenFermion.
"""

from .ucc import UCC
import numpy as np
from typing import Tuple, List, Optional
from pyscf import gto

try:
    from pyscf import gto
except Exception:
    print("Pyscf is not installed.")

DISCARD_EPS = 1e-12


class UCCSD(UCC):
    """UCCSD"""

    def __init__(
        self,
        mol: gto.Mole,
        active_space: Tuple[int, int] = None,
        mo_coeff: Optional[np.ndarray] = None,
        epsilon: float = DISCARD_EPS,
        pick_ex2: bool = False,
        sort_ex2: bool = False,
        run_ccsd: bool = False,
    ) -> None:

        super().__init__(
            mol=mol,
            active_space=active_space,
            mo_coeff=mo_coeff,
        )

        self.pick_ex2 = pick_ex2
        self.sort_ex2 = sort_ex2

        # screen out excitation operators based on t2 amplitude
        self.t2_discard_eps = epsilon

        if run_ccsd:
            ccsd = mol.CCSD()
            if self.frozen_idx:
                ccsd.frozen = self.frozen_idx
            e_corr_ccsd, ccsd_t1, ccsd_t2 = ccsd.kernel()
            self.t1, self.t2 = ccsd_t1, ccsd_t2

        self.ex_ops, self.param_ids, self.init_guess = self.get_ex_ops(
            self.t1,
            self.t2,
        )
        self.num_params = self.param_ids[-1] + 1

    def get_ex_ops(
        self,
        t1: np.ndarray = None,
        t2: np.ndarray = None,
    ) -> Tuple[List[Tuple], List[int], List[float]]:
        """Get one-body and two-body excitation operators for UCCSD ansatz."""

        ex1_ops, ex1_param_ids, ex1_init_guess = self.get_ex1_ops(self.t1)
        ex2_ops, ex2_param_ids, ex2_init_guess = self.get_ex2_ops(self.t2)

        # screen out symmetrically not allowed excitation
        ex2_ops, ex2_param_ids, ex2_init_guess = self.pick_and_sort(
            ex2_ops,
            ex2_param_ids,
            ex2_init_guess,
            self.pick_ex2,
            self.sort_ex2,
        )

        ex_op = ex1_ops + ex2_ops
        param_ids = ex1_param_ids + \
            [i + max(ex1_param_ids) + 1 for i in ex2_param_ids]
        init_guess = ex1_init_guess + ex2_init_guess
        return ex_op, param_ids, init_guess

    def pick_and_sort(
        self,
        ex_ops,
        param_ids,
        init_guess,
        do_pick=True,
        do_sort=True,
    ):
        # sort operators according to amplitude
        if do_sort:
            sorted_ex_ops = sorted(
                zip(ex_ops, param_ids), key=lambda x: -np.abs(init_guess[x[1]]))
        else:
            sorted_ex_ops = list(zip(ex_ops, param_ids))
        ret_ex_ops = []
        ret_param_ids = []
        for ex_op, param_id in sorted_ex_ops:
            # discard operators with tiny amplitude.
            # The default eps is so small that the screened out excitations are probably not allowed
            if do_pick and np.abs(init_guess[param_id]) < self.t2_discard_eps:
                continue
            ret_ex_ops.append(ex_op)
            ret_param_ids.append(param_id)
        unique_ids = np.unique(ret_param_ids)
        ret_init_guess = np.array(init_guess)[unique_ids]
        id_mapping = {old: new for new, old in enumerate(unique_ids)}
        ret_param_ids = [id_mapping[i] for i in ret_param_ids]
        return ret_ex_ops, ret_param_ids, list(ret_init_guess)
