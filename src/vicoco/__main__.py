#!/usr/bin/env python3
from __future__ import annotations

import importlib
import inspect
import sys

from vicoco.manager import XSimManager

# cocotb.simulator is usually populated with C GPI functions that call out to the simulator
# we replace those with our gpi_emulation module, which hook back into our manager

gpi_emulation = importlib.import_module("vicoco.gpi_emulation")
sys.modules["cocotb.simulator"] = gpi_emulation


# derived from themperek's cocotb-vivado
# beginning in cocotb 2.1, this works to load cocotb
# after injecting the GPI emulation, without causing
# circular import type issues. also works on cocotb 2.0
_spec = importlib.util.find_spec("cocotb")
assert _spec is not None and _spec.loader is not None
cocotb = importlib.util.module_from_spec(_spec)
cocotb.simulator = gpi_emulation
sys.modules["cocotb"] = cocotb
_spec.loader.exec_module(cocotb)

from os import getenv

from pygpi.entry import load_entry


# derived from themperek's cocotb-vivado
def load_cocotb() -> None:
    """Start the regression on cocotb 2.0 (``load_entry(argv)``) and 2.1 (no args)."""
    # cocotb 2.1 needs no arguments passed, cocotb 2.0 needs sys.argv passed.
    load = load_entry
    if inspect.signature(load_entry).parameters:
        load(sys.argv)
    else:
        load()


def _initialize_simulator():

    # create (single universal) instance of the simulator manager
    # so that it can be used by the gpi emulation modules
    launch_mode = getenv("XSIM_INTERFACE",'XSI')
    sim_manager = XSimManager.init(launch_mode)
    sim_manager.start_simulator()

    load_cocotb()

    sim_manager.run()



import sys

if __name__ == "__main__":
    # when the module is run directly, that implies we're launching as the "simulator"
    _initialize_simulator()
