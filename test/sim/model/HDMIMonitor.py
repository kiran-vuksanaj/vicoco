#!/usr/bin/env python3

from cocotb_bus.bus import Bus
from cocotb_bus.monitors import BusMonitor


from cocotb.triggers import Timer, RisingEdge, FallingEdge, ClockCycles, ReadOnly

class HDMIMonitor(BusMonitor):

    def __init__(self,dut,name,clock_pixel,clock_fast):
        self._signals = ['tx_p','tx_n']
        BusMonitor.__init__(self,dut,name,clock_pixel)
        self.clock_pixel = clock_pixel
        self.clock_fast = clock_fast

    async def _monitor_recv(self):

        rising_edge_pixel = RisingEdge(self.clock_pixel)
        rising_edge_fast = RisingEdge(self.clock_fast)
        falling_edge_fast = RisingEdge(self.clock_fast)
        read_only = ReadOnly()

        print("Hello!")
        while True:
            await rising_edge_pixel
            await read_only
            for i in range(5):

                data = self.bus.capture()
                self.log.info(data)

                await falling_edge_fast
                await read_only

                data = self.bus.capture()
                self.log.info(data)

                await rising_edge_fast
                await read_only
