
import cocotb
from cocotb.triggers import Timer,RisingEdge,FallingEdge, ClockCycles, ReadOnly
import logging

from cocotb_bus.bus import Bus
from cocotb_bus.drivers import Driver, BusDriver

import random

class ReadDataDriver(Driver):
    def __init__(self,dut,clock):
        self.clock = clock
        self.dut = dut
        self.drive_phase = FallingEdge(clock)
        Driver.__init__(self)
        self.dut.app_rd_data.value = 0
        self.dut.app_rd_data_valid.value = 0

    async def _driver_send(self, data, sync=True):
        if (not sync):
            await self.drive_phase

        self.dut.app_rd_data_valid = 1
        self.dut.app_rd_data = data
        
        await self.drive_phase
        self.dut.app_rd_data_valid = 0


class MigDDR:
    """
    class MigDDR: simulates connections to DRAM memory
    """
    CMD_READ = 1
    CMD_WRITE = 0
    
    def __init__(self,dut,clock):
        self.memory = {}

        self.dut = dut
        self.clock = clock
        self.bus = Bus(dut,'app',[
            'addr',
            'cmd',
            'en',
            'wdf_data',
            'wdf_end',
            'wdf_wren',
            'wdf_mask',
            'rdy',
            'wdf_rdy'
        ])

        self._drive_phase = FallingEdge( self.clock )
        self._read_phase = ReadOnly()
        self.log = logging.getLogger("cocotb.dram")
        self.rd_data_driver = ReadDataDriver(dut,dut.clk_in)
        self._ready_chance = 0.7
        self._ready_write_chance = 0.9
        self._write_cycles = 4
        self._read_cycles = 30


        
        cocotb.start_soon( self.simulate() )

    async def simulate(self):
        
        await self._drive_phase

        cocotb.start_soon( self.randomized_ready() )
        
        while True:
            # read values

            # write values
            
            await self._read_phase
            # just before rising edge

            if (self.bus.en.value == 1 and self.bus.rdy.value == 1):
                # handshake: command input accepted
                
                if (self.bus.cmd.value == MigDDR.CMD_READ):
                    # accept a read command!
                    addr = self.bus.addr.value.integer
                    self.log.info(f"Read Request submitted: [addr = 0x{addr:X}]")
                    cocotb.start_soon( self.read_command( addr ) )
                elif (self.bus.cmd.value == MigDDR.CMD_WRITE):
                    if (self.bus.wdf_rdy.value == 1 and self.bus.wdf_wren.value == 1):
                        addr = self.bus.addr.value.integer
                        data = self.bus.wdf_data.value.integer
                        self.log.info(f"Write Request submitted: [addr = 0x{addr:X}, data = 0x{data:032X}]")
                        cocotb.start_soon( self.write_command( addr, data ) )
                    else:
                        self.log.info("Warning: write command not accepted!")
                else:
                    self.log.info("Improper (or not-implemented) app_cmd")
                
            
            await self._drive_phase

    async def write_command(self,addr,data):
        # writing to an address with a non-zero offset isn't supported here
        assert (addr%8 == 0), "Attempted to write to address with non-zero offset."
        addr = addr//8
        await ClockCycles(self.clock, self._write_cycles ,rising=False)
        self.memory[addr] = data

    async def read_command(self,addr):
        # writing to an address with a non-zero offset isn't supported here
        assert (addr%8 == 0), "Attempted to read to address with non-zero offset."
        addr = addr//8
        
        await ClockCycles(self.clock, self._read_cycles ,rising=False)
        if (addr in self.memory):
            data = self.memory[addr]
        else:
            self.log.info(f"Reading from unwritten memory address 0x{addr:X}. (this might be fine)")
            data = 0xAAAA_AAAA_AAAA_AAAA_AAAA_AAAA_AAAA_AAAA
        self.rd_data_driver.append( data )
        
            
    async def randomized_ready(self):
        while True:
            if random.random() < self._ready_chance:
                self.bus.rdy.value = 1
                self.bus.wdf_rdy.value = 1 if random.random()<self._ready_write_chance else 0
            else:
                self.bus.rdy.value = 0
                self.bus.wdf_rdy.value = 0

            await self._drive_phase

    def __getitem__(self,addr):
        return self.memory[addr]


        

