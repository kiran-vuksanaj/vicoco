#!/usr/bin/env python3

import cocotb
from cocotb.triggers import Timer, RisingEdge, ClockCycles, ReadOnly, NextTimeStep
from cocotb.utils import get_sim_time
from pathlib import Path
import os

# from cocotb.runner import get_runner
from vicoco.vivado_runner import get_runner
from cocotb.clock import Clock

import logging
try:
    import pytest
except ImportError:
    pass

async def coro_a(dut):
    dut._log.info("coro running")
    await RisingEdge(dut.incr_in)
    dut.secondary_in.value = 1
    dut._log.info(f"0 readonly, {get_sim_time('ns')}")
    await ReadOnly()
    dut._log.info(f"1 readonly, {get_sim_time('ns')}")
    await ReadOnly()
    dut._log.info(f"2 readonly, {get_sim_time('ns')}")
    # dut.secondary_in.value = 0


@cocotb.test()
async def only_clockedge(dut):

    cocotb.start_soon( Clock(dut.clk,10,units='ns').start() )
    cocotb.start_soon( coro_a(dut) )
    dut._log.info(f"Clock handle: {type(dut.clk._handle)}")
    dut.clk.value = 1
    dut.rst.value = 1
    dut.incr_in.value = 0
    dut.secondary_in.value = 0
    await ReadOnly()
    dut._log.info(f"Clock value: {dut.clk.value.integer}")
    await ClockCycles(dut.clk,2)
    dut._log.info(f"Clock value: {dut.clk.value.integer}")
    dut._log.info(f"Count out value: {dut.smallcount_out.value.integer}")
    dut.rst.value = 0
    dut.incr_in.value = 1
    dut._log.info(f"Setting incr in now")
    dut._log.info(f"Count out value: {dut.smallcount_out.value.integer}")
    await ReadOnly()
    # await Timer(1,'ns')
    dut._log.info(f"Count out value: [post read-only] {dut.smallcount_out.value.integer}")
    await ClockCycles(dut.clk,10)
    dut._log.info(f"Slow out value: {dut.slow_out.value.integer}")
    await RisingEdge(dut.slow_out)
    dut._log.info(f"Slow out value: {dut.slow_out.value.integer}")
    
    dut._log.info(f"Finishing... {get_sim_time('ns')}")
    


def test_completetb():
    tb_name = "test_valuechanges"

    proj_path = Path(__file__).resolve().parent
    sources = [proj_path / "../hdl/valuechanger.sv",
               proj_path / "../hdl/valuechanger_tb.sv"]
    sim = os.getenv("SIM","vivado")
    hdl_toplevel_lang = "verilog"
    toplevel = "valuechanger"
    parameters = {"SLOW_DEPTH":5}
    runner = get_runner(sim)


    runner.build(
        sources=sources,
        hdl_toplevel=toplevel,
        always=True,
        timescale = ('1ns','1ps'),
        parameters=parameters,
        waves=True)
    runner.test(
        hdl_toplevel=toplevel,
        test_module=tb_name,
        hdl_toplevel_lang=hdl_toplevel_lang,
        waves=True)

if __name__ == "__main__":
    test_completetb()
