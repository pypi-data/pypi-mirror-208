# This code is part of isQ.
# (C) Copyright ArcLight Quantum 2023.
# This code is licensed under the MIT License.

"""
A connector to directly use circuits as PyTorch modules.
This part code is inspired by tensorcircuit.
"""

from typing import Any, Callable, Tuple, Optional

try:
    import torch
    from torch import Tensor
    from torch.nn import Module, Parameter
except Exception:
    Module = object
    Tensor = Any


class TorchLayerError(Exception):
    """Torch layer exception."""


class TorchLayer(Module):
    """Apply a transformation of quantum circuits to the incoming data"""
    __constants__ = ["weights_number"]
    weights_number: int

    def __init__(
        self,
        circuit: Callable[..., Any],
        weights_number: int,
        is_vmap: bool = True,
        in_dims: Tuple[Optional[int], Optional[int]] = (0, None),
        initial_weights: Optional[Tensor] = None,
    ):
        super(TorchLayer, self).__init__()

        if is_vmap:
            circuit = torch.vmap(circuit, in_dims=in_dims)

        self.circuit = circuit

        if isinstance(initial_weights, Tensor):
            self.weights = Parameter(initial_weights)
        else:
            self.weights = Parameter(torch.randn(weights_number))

    def forward(self, inputs: Tensor) -> Tensor:
        return self.circuit(inputs, self.weights)
