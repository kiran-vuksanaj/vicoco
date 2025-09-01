#!/usr/bin/env python3

import importlib
import sys

from vicoco.manager import XSimManager

# cocotb.simulator is usually populated with C GPI functions that call out to the simulator
# we replace those with our gpi_emulation module, which hook back into our manager
sys.modules["cocotb.simulator"] = importlib.import_module("vicoco.gpi_emulation")
import cocotb

from os import getenv

def _initialize_simulator(argv_):

    # create (single universal) instance of the simulator manager
    # so that it can be used by the gpi emulation modules
    launch_mode = getenv("XSIM_INTERFACE",'XSI')
    sim_manager = XSimManager.init(launch_mode)
    sim_manager.start_simulator()

    # TODO replace with proper reference to PYGPI_ENTRYPOINT / PYGPI_USERS
    # this is just the default value of that.
    cocotb._initialise_testbench(argv_)

    sim_manager.run()
    


import sys

if __name__ == "__main__":
    # when the module is run directly, that implies we're launching as the "simulator"
    _initialize_simulator(sys.argv)
