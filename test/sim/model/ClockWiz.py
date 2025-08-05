#!/usr/bin/env python3
import cocotb

from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock



class ClockWiz:

    INPUT = 0
    OUTPUT = 1

    def __init__(self,stub_handle,clock_specs,locked_output='locked'):
        """
        stub_handle: cocotb handle for the stub clk_wiz module
        """
        self._handle = stub_handle
        self._process_specs(clock_specs)

        if locked_output is not None:
            self.locked = self._handle.__getattr__(locked_output)
            self.locked.value = 0
        else:
            self.locked = None

    def _process_specs(self,clock_specs):
        self.input_clock = None
        self.output_clocks = []
        for clock_name in clock_specs.keys():
            clock_data = clock_specs[clock_name]
            handle = self._handle.__getattr__(clock_name)

            # TODO option of Hz input

            if (clock_data[0] == ClockWiz.INPUT):
                self.input_clock = handle
            else:
                _, period, unit, phase = clock_data
                phase_delay = Timer(period*phase/360, unit)
                clock_object = Clock(handle,period,unit)
                self.output_clocks.append( (phase_delay,clock_object) )


    async def launch_clock(self,output_clock):
        phase_delay, clock_object = output_clock
        await phase_delay
        await clock_object.start()
                
    async def start(self):
        await RisingEdge(self.input_clock)
        if self.locked is not None:
            self.locked.value = 1
        
        for output_clock in self.output_clocks:
            cocotb.start_soon( self.launch_clock(output_clock) )



@cocotb.test()
async def clkwiz_stub(dut):
    clock_specs = {
        'clk_in1': (ClockWiz.INPUT, 10, 'ns'),
        'clk_out1': (ClockWiz.OUTPUT, 12, 'ns', 0), # 83.333 MHz
        'clk_out2': (ClockWiz.OUTPUT, 3, 'ns', 0), # 333.333 MHz
        'clk_out3': (ClockWiz.OUTPUT, 5, 'ns', 0),
        'clk_out4': (ClockWiz.OUTPUT, 3, 'ns', 90), # 333.333 MHz, 90 degree phase shift
    }

    stub_handle = dut.clk_wiz_inst
    wizard = ClockWiz(stub_handle,clock_specs)

    cocotb.start_soon( Clock(dut.clk,10,'ns').start() )
    await Timer(1,'ps')

    cocotb.start_soon( wizard.start() )
    
    await Timer(200,'ns')


import os
from pathlib import Path
import sys
from cocotb.runner import get_runner

if __name__ == "__main__":
    tb_name = "ClockWiz"
    proj_dir = Path(__file__).resolve().parent

    hdl_toplevel_lang = "verilog"
    sim = os.getenv("SIM","icarus")


    sources = [proj_dir / "clk_wiz.sv", proj_dir / "clkwiz_tl.sv"]
    toplevel = "clkwiz_tl"

    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel=toplevel,
        always=True,
        waves=True)
    runner.test(
        hdl_toplevel=toplevel,
        test_module=tb_name,
        waves=True)
