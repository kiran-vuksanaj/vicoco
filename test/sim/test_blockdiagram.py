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

@pytest.mark.skipif(not("SAMPLE_BD" in os.environ), reason="full Vivado project not included in repo. specify SAMPLE_BD and SAMPLE_BD_WRAPPER to test a block diagram toplevel design.")
def test_blockdiagram_tb():
    tb_name = "test_blockdiagram"

    proj_path = Path(__file__).resolve().parent

    sample_bd = os.getenv("SAMPLE_BD",None)
    sample_bd_wrapper = os.getenv("SAMPLE_BD_WRAPPER",None)

    if (sample_bd is None or sample_bd_wrapper is None):
        print("Run with SAMPLE_BD={path/to/bockdiagram.bd} SAMPLE_BD_WRAPPER={path/to/wrapper.v}.")
        return
    
    sources = [sample_bd,sample_bd_wrapper]
    sim = "vivado"
    hdl_toplevel_lang = "verilog"
    toplevel = "design_1_wrapper"
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
    test_blockdiagram_tb()
