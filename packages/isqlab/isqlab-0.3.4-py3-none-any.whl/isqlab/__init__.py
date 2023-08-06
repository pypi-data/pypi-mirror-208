from isqlab.linkers import TorchLayer
from isqlab.circuits import QuantumCircuit
import os
import logging
__version__ = "0.3.4"
__author__ = "Arclight Quantum"
__creator__ = "Yusheng Yang"

# 0 = all messages are logged (default behavior)
# 1 = INFO messages are not printed
# 2 = INFO and WARNING messages are not printed
# 3 = INFO, WARNING, and ERROR messages are not printed
# os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
logging.getLogger("jax").setLevel(logging.CRITICAL)

# to use double-precision numbers
os.environ["JAX_ENABLE_X64"] = "True"

# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
