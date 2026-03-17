
from .runner import get_runner, VHDL, Verilog

import warnings
warnings.warn(
    "The Vivado Runner module has been renamed from vicoco.vivado_runner to vicoco.runner; "
    "import from vicoco.runner instead.",
    DeprecationWarning,
    stacklevel=2
)
