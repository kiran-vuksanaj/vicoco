#!/usr/bin/env python3

import cocotb
from cocotb.triggers import Timer, RisingEdge
from pathlib import Path

import os

# from cocotb.runner import get_runner
from vicoco.vivado_runner import get_runner
from cocotb.binary import BinaryValue, LogicArray
from cocotb.clock import Clock

try:
    import pytest
except ImportError:
    pass

@cocotb.test()
async def undefined_values(dut):

    await Timer(20,'ns')
    dut._log.info(f"count out value with no set inputs: {dut.count_out.value}")

@cocotb.test()
async def cocotb_a(dut):
    dut.clk.value = 0
    await Timer(300,units='ns')
    dut.clk.value = 1
    await Timer(300,units='ns')
    dut._log.info(f"clock value: {dut.clk.value}")
    dut._log.info(f"value type: {type(dut.clk.value)}")
    dut.incr_in.value = LogicArray('Z')
    await Timer(20,units='ns')
    dut._log.info(f"incr value: {dut.incr_in.value.binstr}")
    dut._log.info("done")


@cocotb.test()
async def cocotb_b(dut):

    cocotb.start_soon( Clock(dut.clk,10,units='ns').start() )
    dut.rst.value = 1
    dut.incr_in.value = 1
    await Timer(20,'ns')
    dut.rst.value = 0
    for i in range(30):
        count_out_val = dut.count_out.value.integer
        dut._log.info(f"Count out value: {count_out_val}, i={i}")
        # assert(count_out_val==i*(2**32))
        assert(count_out_val==i)
        await Timer(10,'ns')
    dut._log.info( f'cordic_out: {dut.cordic_out.value.binstr}' )
    dut._log.info( f'cordic_valid: {dut.cordic_valid.value.binstr}' )


@cocotb.test()
async def using_edges(dut):
    cocotb.start_soon( Clock(dut.clk,10,units='ns').start() )
    dut.rst.value = 1
    dut.incr_in.value = 0
    await RisingEdge(dut.clk)
    dut._log.info("one rising edge completed")
    await RisingEdge(dut.clk)
    dut._log.info("two rising edges completed")
    dut.rst.value = 0
    dut.incr_in.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut._log.info(f"three more rising edges done: count_out = {dut.count_out.value.integer}")

      
def test_completetb():
    tb_name = "test_simplecoco"

    proj_path = Path(__file__).resolve().parent.parent
    sources = [proj_path / "hdl" / "counter.sv"]
    sim = os.getenv('SIM','vivado')
    hdl_toplevel_lang = "verilog"
    toplevel = "counter"
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
    test_completetb()
