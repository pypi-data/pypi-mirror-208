# This code is part of isQ.
# (C) Copyright ArcLight Quantum 2023.
# This code is licensed under the MIT License.

"""A Quantum Neural Network for autograd"""

from .neural_network import NeuralNetwork
import numpy as np

try:
    import autograd.numpy as anp
    from autograd import jacobian
except Exception:
    pass


class QNNAutograd(NeuralNetwork):

    def __init__(
        self,
        circuit,
        num_inputs,
        num_weights,
        output_shape,
        input_gradients: bool = True,
        sparse: bool = False,
    ) -> None:

        super().__init__(
            num_inputs=num_inputs,
            num_weights=num_weights,
            sparse=sparse,
            output_shape=output_shape,
            input_gradients=input_gradients,
        )

        self.circuit = circuit

    def _forward(
        self,
        inputs,
        weights,
    ):

        inputs = anp.array(inputs)
        weights = anp.array(weights)

        output_data = [self.circuit(
            input, weights) for input in inputs]

        return np.array(output_data)

    def _backward(
        self,
        inputs,
        weights,
    ):

        inputs = anp.array(inputs)
        weights = anp.array(weights)

        inputs_grad = [jacobian(self.circuit, 0)(
            input, weights) for input in inputs]

        weights_grad = [jacobian(self.circuit, 1)(
            input, weights) for input in inputs]

        if not self._input_gradients:
            return None, np.array(weights_grad)

        return np.array(inputs_grad), np.array(weights_grad)
