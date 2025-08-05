#!/usr/bin/env python3

import cocotb
from cocotb.triggers import Timer
from cocotb.clock import Clock

from model.ClockWiz import ClockWiz

@cocotb.test()
async def simple_launch(dut):
    clock_specs = {
        'clk_100mhz': (ClockWiz.INPUT, 10, 'ns'),
        'clk_pixel': (ClockWiz.OUTPUT, 13.470, 'ns', 0), # 74.25MHz
        'clk_5x': (ClockWiz.OUTPUT, 2.694, 'ns', 0) # 371.25MHz
    }
    wizard = ClockWiz(dut,clock_specs,locked_output=None)

    cocotb.start_soon( Clock(dut.clk_100mhz,10,'ns').start() )
    cocotb.start_soon( wizard.start() )
    
    rst = dut.sys_rst
    rst.value = 0
    await Timer(30,'ns')
    rst.value = 1
    await Timer(30,'ns')
    rst.value = 0

    
    await Timer(1000,'ns')





from pathlib import Path
# from cocotb.runner import get_runner
from vicoco.vivado_runner import get_runner

def test_hdmi_pipeline():
    this_file = Path(__file__).resolve()
    tb_name = this_file.stem
    proj_path = this_file.parent.parent

    sources = [proj_path / "hdl" / "hdmi" / "hdmi_pipeline.sv",
               proj_path / "hdl" / "hdmi" / "tmds_encoder.sv",
               proj_path / "hdl" / "hdmi" / "tmds_serializer.sv",
               proj_path / "hdl" / "hdmi" / "tm_choice.sv",
               proj_path / "hdl" / "hdmi" / "video_sig_gen.sv",
               proj_path / "hdl" / "hdmi" / "hdmi_clk_wiz.v"]


    sim = "vivado"

    hdl_toplevel_lang = "verilog"
    toplevel = "hdmi_pipeline"

    runner = get_runner(sim)

    runner.xilinx_libraries.add("unisim")
    
    runner.build(
        sources=sources,
        hdl_toplevel=toplevel,
        always=True,
        timescale=('1ns','1ps'),
        waves=True)
    runner.test(
        hdl_toplevel=toplevel,
        test_module=tb_name,
        hdl_toplevel_lang=hdl_toplevel_lang,
        waves=True)


if __name__ == "__main__":
    test_hdmi_pipeline()
