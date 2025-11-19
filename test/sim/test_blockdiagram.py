#!/usr/bin/env python3

#!/usr/bin/env python3

import cocotb
from cocotb.triggers import Timer
from pathlib import Path

# from cocotb.runner import get_runner
from vicoco.vivado_runner import get_runner
import os

from cocotb.clock import Clock
import pytest

@cocotb.test()
async def barebones_clock(dut):
    cocotb.start_soon( Clock(dut.clk,10,units='ns').start() )
    await Timer(3000,'ns')

def test_fft_tb():
    tb_name = "test_blockdiagram"

    proj_path = Path(__file__).resolve().parent

    vivado_version = os.getenv("VIVADO_VERSION","2025.1")
    vivado_version_directory = "Vivado_"+vivado_version.replace(".","_")
    
    sources = ["/home/kiranv/Documents/fpga/vivgui/bd_test/bd_test.gen/sources_1/bd/design_1/hdl/design_1_wrapper.v",
            "/home/kiranv/Documents/fpga/vivgui/bd_test/bd_test.srcs/sources_1/bd/design_1/design_1.bd"
               ]
    sim = "vivado"
    hdl_toplevel_lang = "verilog"
    toplevel = "design_1_wrapper.v"
    runner = get_runner(sim)

    runner.build(
        sources=sources,
        hdl_toplevel=toplevel,
        always=True,
        timescale = ('1ns','1ps'),
        waves=True)
    runner.test(
        hdl_toplevel=toplevel,
        test_module=tb_name,
        hdl_toplevel_lang=hdl_toplevel_lang,
        waves=True)

if __name__ == "__main__":
    test_fft_tb()
