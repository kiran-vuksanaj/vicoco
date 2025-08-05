#!/usr/bin/env python3

import cocotb
from cocotb.triggers import Timer, RisingEdge, ClockCycles, ReadOnly
from cocotb.clock import Clock

from model.AXIStream import AXISMonitor, AXISDriver



@cocotb.test()
async def clock_only(dut):

    cocotb.start_soon( Clock(dut.s_axis_aclk, 10, units='ns').start() )

    await Timer(2000,units='ns')

@cocotb.test()
async def monitored_and_driven_i(dut):

    cocotb.start_soon( Clock(dut.s_axis_aclk, 10, units='ns').start() )

    inm = AXISMonitor(dut,'s',dut.s_axis_aclk)
    outm = AXISMonitor(dut,'m',dut.s_axis_aclk)

    ind = AXISDriver(dut,'s',dut.s_axis_aclk)

    dut.s_axis_aresetn.value = 1
    await ClockCycles(dut.s_axis_aclk,2)
    dut.s_axis_aresetn.value = 0
    dut.m_axis_tready.value = 0
    await ClockCycles(dut.s_axis_aclk,10)
    dut.s_axis_aresetn.value = 1
    
    dut.m_axis_tready.value = 1
    
    for i in range(1,10):
        ind.append({'data':i,'last':0})
    ind.append({'data':10,'last':1})
    
    await ClockCycles(dut.s_axis_aclk,15)
    dut.m_axis_tready.value = 0
    await ClockCycles(dut.s_axis_aclk,8)
    dut.m_axis_tready.value = 1
    await ClockCycles(dut.s_axis_aclk,15)
    dut._log.info("Done!")





from vicoco.vivado_runner import get_runner
from pathlib import Path

def test_fifotb():

    file_path = Path(__file__).resolve()

    tb_name = file_path.stem
    proj_path = file_path.parent.parent
    sources = [proj_path / "ip/Vivado_2024_2/fifo_dut_sync/fifo_dut_sync.xci",
               proj_path / "hdl" / "fifo_wrap.sv"
               ]
    sim = "vivado"
    hdl_toplevel_lang = "verilog"
    toplevel = "fifo_wrap"

    runner = get_runner(sim)

    runner.build(
        sources=sources,
        hdl_toplevel=toplevel,
        always=False,
        timescale = ('1ns','1ps'),
        waves=True)
    runner.test(
        hdl_toplevel=toplevel,
        test_module=tb_name,
        hdl_toplevel_lang=hdl_toplevel_lang,
        waves=True)


if __name__ == "__main__":
    test_fifotb()
