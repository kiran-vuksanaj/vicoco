#!/usr/bin/env python3

#!/usr/bin/env python3

import cocotb
from cocotb.triggers import Timer
from pathlib import Path

# from cocotb.runner import get_runner
from vicoco.runner import get_runner
import os

from cocotb.clock import Clock
import pytest

@cocotb.test()
async def barebones_clock(dut):
    cocotb.start_soon( Clock(dut.clk,10,units='ns').start() )
    await Timer(3000,'ns')

@pytest.mark.slow
def test_blockdiagram_tb():
    tb_name = "test_blockdiagram"

    proj_path = Path(__file__).resolve().parent

    sources = []
    sim = "vivado"
    hdl_toplevel_lang = "verilog"
    toplevel = "design_1"
    runner = get_runner(sim)

    runner.add_export_simulation_tcl(
        tcl_file = proj_path.parent / "tcl" / "design_1.tcl",
        result_file="myproj/project_1.xpr",
        force_export=True
    )
    
    runner.build(
        sources=sources,
        hdl_toplevel=toplevel,
        always=True,
        timescale = ('1ns','1ps'),
        # clean=True,
        waves=True)
    runner.test(
        hdl_toplevel=toplevel,
        test_module=tb_name,
        hdl_toplevel_lang=hdl_toplevel_lang,
        waves=True)

if __name__ == "__main__":
    test_blockdiagram_tb()
