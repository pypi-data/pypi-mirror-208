# This code is part of isQ.
# (C) Copyright ArcLight Quantum 2023.
# This code is licensed under the MIT License.

"""Quantum circuit object."""

from isq import LocalDevice, quantumCor
from isq.device.device import Device, AwsDevice
from isq import Drawer
from typing import Callable, Union, Sequence, Literal, Optional
from functools import partial
import numpy as np
import itertools
import time


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

SIMULATOR_METHOD = Literal["simulator", "autograd", "jax", "torch", "pytorch"]


class QuantumCircuitError(Exception):
    """
    Quantum circuits error.
    """
    pass


class QuantumCircuit:
    """
    Quantum circuit class.

    """

    def __init__(
        self,
        num_qubits: int,
        backend: Device = None,
        method: SIMULATOR_METHOD = "autograd",
        dict_format: bool = False,
        sleep_time: int = 3,
        run_time: Optional[int] = None,
    ) -> None:

        if backend is None:
            backend = LocalDevice()

        self.use_hardware = False
        self.run_time = None
        self.sleep_time = None
        if isinstance(backend, AwsDevice):
            self.use_hardware = True
            self.run_time = run_time
            self.sleep_time = sleep_time
        # When using hardware, `method` is invalid

        if method == "jax":
            if not HAS_JAX:
                raise QuantumCircuitError("Jax is not installed.")

        if method == "autograd":
            if not HAS_AUTOGRAD:
                raise QuantumCircuitError("Autograd is not installed.")

        if method in ["torch", "pytorch"]:
            if not HAS_TORCH:
                raise QuantumCircuitError("Pytorch is not installed.")

        self._circuit_recording = []  # to record isqfile
        self._measure_recording = []  # to recoed measurement

        self.backend = backend
        self.method = method
        self.dict_format = dict_format

        self.num_qubits = num_qubits
        self._qbit_init(num_qubits)

    def __repr__(self) -> str:  # print isqfile
        return "\n".join(self.circuit)

    __str__ = __repr__

    def __len__(self) -> int:
        return len(self.circuit)

    @property
    def idx(self) -> int:
        return len(self.circuit)

    def __getitem__(self, key: int) -> str:
        return self.circuit[key]

    @property
    def circuit(self) -> list:
        return self._circuit_recording + self._measure_recording

    def qir(self, **kw) -> str:
        if kw is None:
            return self.backend.compile_to_ir(self.__repr__())
        self.backend.compile_with_par(self.__repr__(), **kw)
        return self.backend.get_ir()

    def extend(
        self,
        circuit: "QuantumCircuit",
        remove_qbit_def: bool = True,
    ) -> None:
        if remove_qbit_def:
            self._circuit_recording.extend(circuit._circuit_recording[1:])
        else:
            self._circuit_recording.extend(circuit._circuit_recording)

    def insert(
        self,
        start: int,
        end: int,
        reverse: bool = True
    ) -> None:
        """
        insert part of circuits inversely.
        """

        insert_list = self[start:end]
        if reverse:
            insert_list = insert_list[::-1]
        self._circuit_recording.extend(insert_list)

    def inv(
        self,
        func: Callable,
        *args,
        **kw
    ) -> None:
        """
        Insert a part of circuit inversely from a function.
        """
        start = self.idx
        func(*args, **kw)
        end = self.idx
        insert_list = self[start:end][::-1]
        for i in range(end-start):
            _ = self._circuit_recording.pop()
        self._circuit_recording.extend(insert_list)

    def _qbit_init(
        self,
        num_qubits: int,
    ) -> None:
        """
        Qubits initialization.
        """
        if num_qubits < 0:
            raise QuantumCircuitError(
                f"Number of inputs cannot be negative: {num_qubits}!")

        self._circuit_recording.append(f"qbit q[{num_qubits}];")

    def _one_qubit_op(
        self,
        qubit_idx: int,
        operation: str,
    ) -> None:
        """
        General one qubit operations.
        """
        self._circuit_recording.append(f"{operation}(q[{qubit_idx}]);")

    def h(
        self,
        qubit_idx: int,
    ) -> None:
        operation = "H"
        self._one_qubit_op(qubit_idx, operation)

    def x(
        self,
        qubit_idx: int,
    ) -> None:
        operation = "X"
        self._one_qubit_op(qubit_idx, operation)

    def y(
        self,
        qubit_idx: int,
    ) -> None:
        operation = "Y"
        self._one_qubit_op(qubit_idx, operation)

    def z(
        self,
        qubit_idx: int,
    ) -> None:
        operation = "Z"
        self._one_qubit_op(qubit_idx, operation)

    def s(
        self,
        qubit_idx: int,
    ) -> None:
        operation = "S"
        self._one_qubit_op(qubit_idx, operation)

    def sd(
        self,
        qubit_idx: int,
    ) -> None:
        operation = "SD"
        self._one_qubit_op(qubit_idx, operation)

    def t(
        self,
        qubit_idx: int,
    ) -> None:
        operation = "T"
        self._one_qubit_op(qubit_idx, operation)

    def td(
        self,
        qubit_idx: int,
    ) -> None:
        operation = "TD"
        self._one_qubit_op(qubit_idx, operation)

    def x2p(
        self,
        qubit_idx: int,
    ) -> None:
        """X rotate pi/2"""
        operation = "X2P"
        self._one_qubit_op(qubit_idx, operation)

    def x2m(
        self,
        qubit_idx: int,
    ) -> None:
        """X rotate -pi/2"""
        operation = "X2M"
        self._one_qubit_op(qubit_idx, operation)

    def y2p(
        self,
        qubit_idx: int,
    ) -> None:
        """Y rotate pi/2"""
        operation = "Y2P"
        self._one_qubit_op(qubit_idx, operation)

    def y2m(
        self,
        qubit_idx: int,
    ) -> None:
        """Y rotate -pi/2"""
        operation = "Y2M"
        self._one_qubit_op(qubit_idx, operation)

    def m(
        self,
        qubit_idx: int,
    ) -> None:
        operation = "M"
        self._one_qubit_op(qubit_idx, operation)

    def H(
        self,
        qubit_idx: int,
    ) -> None:
        operation = "H"
        self._one_qubit_op(qubit_idx, operation)

    def X(
        self,
        qubit_idx: int,
    ) -> None:
        operation = "X"
        self._one_qubit_op(qubit_idx, operation)

    def Y(
        self,
        qubit_idx: int,
    ) -> None:
        operation = "Y"
        self._one_qubit_op(qubit_idx, operation)

    def Z(
        self,
        qubit_idx: int,
    ) -> None:
        operation = "Z"
        self._one_qubit_op(qubit_idx, operation)

    def S(
        self,
        qubit_idx: int,
    ) -> None:
        operation = "S"
        self._one_qubit_op(qubit_idx, operation)

    def SD(
        self,
        qubit_idx: int,
    ) -> None:
        operation = "SD"
        self._one_qubit_op(qubit_idx, operation)

    def T(
        self,
        qubit_idx: int,
    ) -> None:
        operation = "T"
        self._one_qubit_op(qubit_idx, operation)

    def TD(
        self,
        qubit_idx: int,
    ) -> None:
        operation = "TD"
        self._one_qubit_op(qubit_idx, operation)

    def X2P(
        self,
        qubit_idx: int,
    ) -> None:
        """X rotate pi/2"""
        operation = "X2P"
        self._one_qubit_op(qubit_idx, operation)

    def X2M(
        self,
        qubit_idx: int,
    ) -> None:
        """X rotate -pi/2"""
        operation = "X2M"
        self._one_qubit_op(qubit_idx, operation)

    def Y2P(
        self,
        qubit_idx: int,
    ) -> None:
        """Y rotate pi/2"""
        operation = "Y2P"
        self._one_qubit_op(qubit_idx, operation)

    def Y2M(
        self,
        qubit_idx: int,
    ) -> None:
        """Y rotate -pi/2"""
        operation = "Y2M"
        self._one_qubit_op(qubit_idx, operation)

    def M(
        self,
        qubit_idx: int,
    ) -> None:
        operation = "M"
        self._one_qubit_op(qubit_idx, operation)

    def _two_qubits_op(
        self,
        qubit_control: int,
        qubit_target: int,
        operation: str,
    ) -> None:
        """
        General two qubit operations.
        """
        self._circuit_recording.append(
            f"{operation}(q[{qubit_control}], q[{qubit_target}]);")

    def cnot(
        self,
        qubit_control: int,
        qubit_target: int,
    ) -> None:
        operation = "CNOT"
        self._two_qubits_op(qubit_control, qubit_target, operation)

    def cx(
        self,
        qubit_control: int,
        qubit_target: int,
    ) -> None:
        operation = "CX"
        self._two_qubits_op(qubit_control, qubit_target, operation)

    def cy(
        self,
        qubit_control: int,
        qubit_target: int,
    ) -> None:
        operation = "CY"
        self._two_qubits_op(qubit_control, qubit_target, operation)

    def cz(
        self,
        qubit_control: int,
        qubit_target: int,
    ) -> None:
        operation = "CZ"
        self._two_qubits_op(qubit_control, qubit_target, operation)

    def CNOT(
        self,
        qubit_control: int,
        qubit_target: int,
    ) -> None:
        operation = "CNOT"
        self._two_qubits_op(qubit_control, qubit_target, operation)

    def CX(
        self,
        qubit_control: int,
        qubit_target: int,
    ) -> None:
        operation = "CX"
        self._two_qubits_op(qubit_control, qubit_target, operation)

    def CY(
        self,
        qubit_control: int,
        qubit_target: int,
    ) -> None:
        operation = "CY"
        self._two_qubits_op(qubit_control, qubit_target, operation)

    def CZ(
        self,
        qubit_control: int,
        qubit_target: int,
    ) -> None:
        operation = "CZ"
        self._two_qubits_op(qubit_control, qubit_target, operation)

    def _rotate_gate(
        self,
        param: Union[float, str],
        qubit_idx: int,
        operation: str,
    ) -> None:
        """
        General rotion operations.
        """
        self._circuit_recording.append(
            f"{operation}({param}, q[{qubit_idx}]);")

    def rx(
        self,
        param: Union[float, str],
        qubit_idx: int,
    ) -> None:
        operation = "RX"
        self._rotate_gate(param, qubit_idx, operation)

    def ry(
        self,
        param: Union[float, str],
        qubit_idx: int,
    ) -> None:
        operation = "RY"
        self._rotate_gate(param, qubit_idx, operation)

    def rz(
        self,
        param: Union[float, str],
        qubit_idx: int,
    ) -> None:
        operation = "RZ"
        self._rotate_gate(param, qubit_idx, operation)

    def RX(
        self,
        param: Union[float, str],
        qubit_idx: int,
    ) -> None:
        operation = "RX"
        self._rotate_gate(param, qubit_idx, operation)

    def RY(
        self,
        param: Union[float, str],
        qubit_idx: int,
    ) -> None:
        operation = "RY"
        self._rotate_gate(param, qubit_idx, operation)

    def RZ(
        self,
        param: Union[float, str],
        qubit_idx: int,
    ) -> None:
        operation = "RZ"
        self._rotate_gate(param, qubit_idx, operation)

    def add_gate(
        self,
        gate_name: str,
        matrix: Union[list, np.ndarray],
    ) -> None:
        """add gates manually"""
        quantumCor.addGate(gate_name, matrix)
        cm_gate_name = partial(self.cm, gate_name)
        setattr(self, gate_name, cm_gate_name)

    def cm(
        self,
        gate_name: str,
        *qubit_idx: Union[Sequence[int], int],
    ) -> None:
        """
        Customized gates.
        """
        para_list = []
        for idx in qubit_idx:
            para_list.append(f"q[{idx}]")
        para_str = ", ".join(para_list)
        self._circuit_recording.append(f"{gate_name}({para_str});")

    def measure_qubit(
        self,
        *qubit_idx: Union[Sequence[int], int],
    ) -> None:
        """
        Specifies the object to be measured.
        """

        self._len_qubit_measure = len(qubit_idx)
        # reset measurement
        self._measure_recording = []

        for idx in qubit_idx:
            self._measure_recording.append(f"M(q[{idx}]);")

    # these abbr are for brother Long
    measu_qubit = measure_qubit
    mqbit = measure_qubit
    # these abbr are for brother Long

    def measure(
        self,
        **params,
    ):
        """
        Forward calculation.
        """

        if len(self._measure_recording) == 0:
            raise ValueError("Please set measurement.")

        if self.use_hardware:
            task = self._measure_hardware(**params)
            if self.dict_format:
                return task.result()
            return self._dict2array(task.result())

        if self.method == "simulator":
            results_dict = self.backend.run(self.__repr__(), **params)
            if self.dict_format:
                return results_dict
            return self._dict2array(results_dict)

        elif self.method == "autograd":
            return self.backend.probs(self.__repr__(), mod=0, **params)

        elif self.method == "jax":
            return self.backend.probs(self.__repr__(), mod=1, **params)

        elif self.method in ["torch", "pytorch"]:
            return self.backend.probs(self.__repr__(), mod=2, **params)

        else:
            raise NotImplementedError("Undefined method.")

    def _measure_hardware(self, **params) -> dict:
        """Using quantum hardwares."""
        from isq import TaskState
        task = self.backend.run(self.__repr__(), **params)
        self.task_cancel = task.cancel
        # Expose the cancel API
        start_time = time.time()
        while task.state == TaskState.WAIT:
            task.result()
            # Wait for a period of time before doing an http request
            time.sleep(self.sleep_time)
            if self.run_time is not None:
                if time.time() > start_time + self.run_time:
                    break
        return task

    def _dict2array(
        self,
        result_dicts: dict,
    ) -> np.ndarray:
        """
        Transfer measurement results from Dict to Array.
        """
        shots = self.backend.shots
        # results_list = [0.0] * (2 ** self._len_qubit_measure)
        results_arrays = np.zeros(2 ** self._len_qubit_measure)

        for bin_idx, freq in result_dicts.items():
            results_arrays[int(bin_idx, 2)] = float(freq/shots)
        return results_arrays

    def pauli(
        self,
        gate_name: Union[str, tuple],
        format: str = "str",
    ) -> None:
        """
        Pauli measurement.
        """
        self._measure_recording = []

        if format == "str":
            gates = gate_name[0::2]
            locations = [int(location) for location in gate_name[1::2]]

            if not len(locations) == len(set(locations)):
                raise ValueError("Error pauli measurement.")

            for i in range(len(gates)):
                if gates[i] in ["x", "X"]:
                    self._measure_recording.append(
                        f"H(q[{locations[i]}]);",
                    )
                    self._measure_recording.append(
                        f"M(q[{locations[i]}]);",
                    )
                elif gates[i] in ["y", "Y"]:
                    self._measure_recording.append(
                        f"X2P(q[{locations[i]}]);",
                    )
                    self._measure_recording.append(
                        f"M(q[{locations[i]}]);",
                    )
                elif gates[i] in ["z", "Z"]:
                    self._measure_recording.append(
                        f"M(q[{locations[i]}]);",
                    )
                else:
                    raise ValueError(
                        f"Please input correct Pauli gates instead of {gates[i]}.")

        elif format == "openfermion":
            for single_gate in gate_name:
                if single_gate[1] == "X":
                    self._measure_recording.append(
                        f"H(q[{single_gate[0]}]);",
                    )
                    self._measure_recording.append(
                        f"M(q[{single_gate[0]}]);",
                    )
                elif single_gate[1] == "Y":
                    self._measure_recording.append(
                        f"X2P(q[{single_gate[0]}]);",
                    )
                    self._measure_recording.append(
                        f"M(q[{single_gate[0]}]);",
                    )
                elif single_gate[1] == "Z":
                    self._measure_recording.append(
                        f"M(q[{single_gate[0]}]);",
                    )
                else:
                    raise ValueError("Please input correct Pauli gates.")

    def pauli_measure(self, **params):
        """
        Pauli measurement.
        """

        if len(self._measure_recording) == 0:
            raise ValueError("Please set measurement.")

        if self.use_hardware:
            task = self._measure_hardware(**params)
            measure_result_dict = task.result()
            result = 0
            for res_index, frequency in measure_result_dict.items():
                parity = (-1) ** (res_index.count("1") % 2)
                # e.g. {"011": 222}, to count "1"
                result += parity * frequency / self.backend.shots
            return result

        if self.method == "simulator":
            measure_result_dict = self.backend.run(self.__repr__(), **params)
            result = 0
            for res_index, frequency in measure_result_dict.items():
                parity = (-1) ** (res_index.count("1") % 2)
                # e.g. {"011": 222}, to count "1"
                result += parity * frequency / self.backend.shots
            return result

        elif self.method == "autograd":
            measure_result_list = self.backend.probs(
                self.__repr__(), mod=0, **params)
            parity = [(-1) ** (str(bin(int(index))).count("1") % 2)
                      for index in range(len(measure_result_list))]
            return anp.dot(measure_result_list, anp.array(parity))

        elif self.method == "jax":
            measure_result_list = self.backend.probs(
                self.__repr__(), mod=1, **params)
            parity = [(-1) ** (str(bin(int(index))).count("1") % 2)
                      for index in range(len(measure_result_list))]
            return jnp.vdot(jnp.array(measure_result_list), jnp.array(parity))

        elif self.method in ["torch", "pytorch"]:
            measure_result_list = self.backend.probs(
                self.__repr__(), mod=2, **params)
            parity = [(-1) ** (str(bin(int(index))).count("1") % 2)
                      for index in range(len(measure_result_list))]
            return torch.dot(
                measure_result_list,
                torch.tensor(parity).type_as(measure_result_list),
            )

        else:
            raise NotImplementedError("Undefined method.")

    def str2circuit(
        self,
        isq_str: str,
        remove_qbit_def: bool = False,
    ) -> None:
        """Convert strings to quantum circuits."""
        if remove_qbit_def:
            del (self._circuit_recording[0])
        for isq_line in isq_str.splitlines():
            if len(isq_line) != 0:
                self._circuit_recording.append(isq_line.strip())

    def file2circuit(
        self,
        filename: str,
        remove_qbit_def: bool = False,
    ) -> None:
        """Convert a file to quantum circuits."""
        with open(filename) as f:
            self.str2circuit(
                f.read(),
                remove_qbit_def=remove_qbit_def,
            )

    def circuit2file(
        self,
        filename: str,
        mode="x",
    ) -> None:
        """Convert a quantum circuits to a file."""
        with open(filename, mode) as f:
            f.write(self.__repr__())

    def chain(
        self,
        gate_name: str,
        qubit_idx: Optional[Sequence] = None,
    ) -> None:
        """Act on each qubit and the next in turn"""
        if qubit_idx is None:
            qubit_idx = list(range(self.num_qubits - 1))
        operation = getattr(self, gate_name)
        for idx in qubit_idx:
            # self._two_qubits_op(idx, idx+1, gate_name)
            operation(idx, idx+1)

    def ring(
        self,
        gate_name: str,
        num_qubits: Optional[int] = None,
    ) -> None:
        """Act on all qubits via a ring"""
        if num_qubits is None:
            num_qubits = self.num_qubits
        if num_qubits < 2:
            raise ValueError(
                f"Number of qubits have to be larger than 1 but given {num_qubits}")
        operation = getattr(self, gate_name)
        for num_qubit in range(num_qubits-1):
            operation(num_qubit, num_qubit+1)
        operation(num_qubits-1, 0)

    def single(
        self,
        gate_name: str,
        qubit_idx: Optional[Sequence] = None,
    ) -> None:
        """Act on each qubit in turn"""
        if qubit_idx is None:
            qubit_idx = list(range(self.num_qubits))
        operation = getattr(self, gate_name)
        for idx in qubit_idx:
            # self._one_qubit_op(idx, gate_name)
            operation(idx)

    def perm(
        self,
        gate_name: str,
        qubit_idx: Optional[Sequence] = None,
    ) -> None:
        """Permutation of all."""
        if qubit_idx is None:
            qubit_idx = list(range(self.num_qubits))
        operation = getattr(self, gate_name)
        for idx in itertools.permutations(qubit_idx, 2):
            operation(*idx)

    def comb(
        self,
        gate_name: str,
        qubit_idx: Optional[Sequence] = None,
    ) -> None:
        """combinations of all."""
        if qubit_idx is None:
            qubit_idx = list(range(self.num_qubits))
        operation = getattr(self, gate_name)
        for idx in itertools.combinations(qubit_idx, 2):
            operation(*idx)

    def param(
        self,
        gate_name: str,
        qubit_idx: Optional[Sequence] = None,
        param_name: str = "x",
        param_idx: Optional[Sequence] = None,
    ) -> None:
        """Quickly build parameterized circuits"""
        if qubit_idx is None:
            qubit_idx = list(range(self.num_qubits))
        if param_idx is None:
            param_idx = qubit_idx
        operation = getattr(self, gate_name)
        for pidx, qidx in zip(param_idx, qubit_idx):
            operation(f"{param_name}[{pidx}]", qidx)

    def cmt(self, comments: Optional[str] = None) -> None:
        """Add comments"""
        if comments is None:
            self._circuit_recording.append("")
        elif isinstance(comments, str):
            self._circuit_recording.append(f"// {comments}")

    def draw(
        self,
        show_param: bool = False,
        **kw,
    ) -> None:
        drawer = Drawer(showparam=show_param)
        drawer.plot(self.qir(**kw))
