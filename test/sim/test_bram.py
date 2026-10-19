#!/usr/bin/env python3
import cocotb
from cocotb.triggers import Timer, RisingEdge, ClockCycles, ReadOnly, Edge
from cocotb.clock import Clock
try:
    import pytest
except ImportError:
    pass

async def match_delay():
    await Timer(0.1,'ns')

async def match_delay_on_clock(clk):
    while True:
        await RisingEdge(clk)
        cocotb.start_soon( match_delay() )

@cocotb.test(skip=True)
async def clocks_only(dut):

    dut.ena.value = 1
    dut.enb.value = 1

    cocotb.start_soon( Clock(dut.clka, 12,unit='ns').start() )
    cocotb.start_soon( Clock(dut.clkb, 12, unit='ns').start() )

    cocotb.start_soon(match_delay_on_clock(dut.clka))
    cocotb.start_soon(match_delay_on_clock(dut.clkb))

    await Timer(200,unit='ns')


    
async def port_a(dut):
    dut.wea.value = 1
    await ClockCycles(dut.clka,2)
    dut.addra.value = 0x42
    dut.dina.value = 0xAB
    await ClockCycles(dut.clka,1)
    dut.addra.value = 0x43
    dut.dina.value = 0xCD
    await ClockCycles(dut.clka,3)
    await ReadOnly()
    assert dut.douta.value == 0xCD
    await Edge(dut.doutb)
    dut._log.info(f"doutb {dut.doutb.value}")

async def port_b(dut):
    dut.web.value = 0
    await ClockCycles(dut.clkb,5)
    dut.addrb.value = 0x42
    await ClockCycles(dut.clkb,1)
    dut.addrb.value = 0x43
    await ClockCycles(dut.clkb,2)
    # the IP has a delay built into it
    dut._log.info(f"doutb {dut.doutb.value.to_unsigned():x}")
    await ReadOnly()
    dut._log.info(f"doutb {dut.doutb.value.to_unsigned():x}")
    assert dut.doutb.value == 0xAB
    await ClockCycles(dut.clkb,1)
    dut._log.info(f"doutb {dut.doutb.value.to_unsigned():x}")
    await ReadOnly()
    dut._log.info(f"doutb {dut.doutb.value.to_unsigned():x}")
    assert dut.doutb.value == 0xCD
    
@cocotb.test()
async def value_io(dut):

    dut.ena.value = 1
    dut.enb.value = 1

    cocotb.start_soon( Clock(dut.clka, 10,unit='ns').start() )
    cocotb.start_soon( Clock(dut.clkb, 12, unit='ns').start() )
    cocotb.start_soon(match_delay_on_clock(dut.clka))
    cocotb.start_soon(match_delay_on_clock(dut.clkb))

    a = cocotb.start_soon( port_b(dut) )
    b = cocotb.start_soon( port_a(dut) )

    await cocotb.triggers.gather(a,b)

    

    


from vicoco.runner import get_runner
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
