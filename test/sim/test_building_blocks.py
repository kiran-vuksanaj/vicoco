#!/usr/bin/env python3

import cocotb
from cocotb.triggers import Timer,ClockCycles
from cocotb.clock import Clock
try:
    import pytest
except ImportError:
    pass
@cocotb.test()
async def put_values_clocks(dut):
    cocotb.start_soon( Clock(dut.clk,10,'ns').start() )

    dut.rst.value = 1
    dut.clk_en.value = 1
    dut.data_in.value = 0
    await ClockCycles(dut.clk,2)
    dut.rst.value = 0
    dut.data_in.value = 1
    await ClockCycles(dut.clk,3)
    dut.data_in.value = 0
    await ClockCycles(dut.clk,2)




from pathlib import Path
# from cocotb.runner import get_runner
from vicoco.vivado_runner import get_runner,VHDL,Verilog

def test_building_blocks():
    this_file = Path(__file__).resolve()
    tb_name = this_file.stem
    proj_path = this_file.parent.parent

    sources = [proj_path / "hdl" / "building_blocks.sv"]

    sim = "vivado"

    hdl_toplevel_lang = "verilog"
    toplevel = "building_blocks"

    runner = get_runner(sim, xilinx_extra_libraries=["unisim"])


    runner.build(
        sources=sources,
        hdl_toplevel=toplevel,
        always=True,
        build_args=[VHDL("-2008")], # this doesn't do anything, but does demo the tagged build arg system
        timescale=('1ns','1ps'),
        waves=True)
    runner.test(
        hdl_toplevel=toplevel,
        test_module=tb_name,
        hdl_toplevel_lang=hdl_toplevel_lang,
        waves=True)


if __name__ == "__main__":
    test_building_blocks()
