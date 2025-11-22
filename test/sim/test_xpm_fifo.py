#!/usr/bin/env python3

#!/usr/bin/env python3

import cocotb
from cocotb.triggers import Timer
from pathlib import Path

# from cocotb.runner import get_runner
from vicoco.vivado_runner import get_runner
import os

from cocotb.clock import Clock
try:
    import pytest
except ImportError:
    pass

@cocotb.test()
async def barebones_clock(dut):
    cocotb.start_soon( Clock(dut.sender_clk,10,units='ns').start() )
    cocotb.start_soon( Clock(dut.receiver_clk,12,units='ns').start() )
    await Timer(3000,'ns')

def test_xpm_fifo_tb():
    tb_name = "test_xpm_fifo"

    proj_path = Path(__file__).resolve().parent

    sources = [proj_path / "../hdl" / "clockdomain_fifo.sv",
               proj_path / "../hdl" / "glbl.v"
               ]
    sim = "vivado"
    hdl_toplevel_lang = "verilog"
    toplevel = "clockdomain_fifo"
    runner = get_runner(sim, extra_global_modules=["work.glbl"])

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
    test_xpm_fifo_tb()
