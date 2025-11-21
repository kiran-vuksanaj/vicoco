#!/usr/bin/env python3
import cocotb
from cocotb.triggers import Timer, RisingEdge, ClockCycles, ReadOnly
from cocotb.clock import Clock
try:
    import pytest
except ImportError:
    pass

@cocotb.test()
async def clocks_only(dut):

    dut.ena.value = 1
    dut.enb.value = 1

    cocotb.start_soon( Clock(dut.clka, 10,units='ns').start() )
    cocotb.start_soon( Clock(dut.clkb, 12, units='ns').start() )

    await Timer(200,units='ns')


from vicoco.vivado_runner import get_runner
from pathlib import Path
import os

def test_bramtb():

    file_path = Path(__file__).resolve()

    tb_name = file_path.stem
    proj_path = file_path.parent.parent

    vivado_version = os.getenv("VIVADO_VERSION","2025.1")
    vivado_version_directory = "Vivado_"+vivado_version.replace(".","_")


    sources = [proj_path / "ip" / vivado_version_directory / "blk_mem_kilobyte/blk_mem_kilobyte.xci",
               proj_path / "hdl" / "bram_wrap.sv"
               ]
    sim = "vivado"
    hdl_toplevel_lang = "verilog"
    toplevel = "bram_wrap"

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
    test_bramtb()
