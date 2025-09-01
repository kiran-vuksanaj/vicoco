#!/usr/bin/env python3

from vicoco.interface_xsim import XSimInterface

import pexpect
import re

import logging

class Tcl_XSimInterface(XSimInterface):
    def __init__(self):

        self._simproc = None

        # self.command_times = {}
        # self.cmd_count = {}


    def _pass_command(self,command_str,cat="default"):
        """
        Returns process to predictable state while passing a command and returning response
        """
        assert self._simproc is not None, "simulator not running"
        
        prompt_text = "xsim%"

        self._simproc.sendline(command_str)
        self._simproc.expect(prompt_text)

        resp = self._simproc.before

        assert command_str in resp
        resp_start_idx = resp.find(command_str) + len(command_str)
        resp = resp[resp_start_idx:].strip()


        return resp


    

    def launch_simulator(self):
        # print("launch simulator")
        # self._simproc = subprocess.Popen(["xsim","pybound_sim"],stdin=subprocess.PIPE,stdout=subprocess.PIPE)

        self._simproc = pexpect.spawn("xsim pybound_sim", encoding='utf-8',searchwindowsize=200)
        self._simproc.delaybeforesend = None

        fout = open('pybound_xsim.log','w')
        self._simproc.logfile = fout

        self._simproc.expect("xsim%")

        print("simulator is running")

        # print("first time:",self._pass_command("current_time"))

        # TODO once we can handle multi layer, set scope to root
        self._pass_command("current_scope /")

        self._portmap = self._load_portmap()

        # while True:
        #     line = self._simproc.stdout.read(1)
        #     if not line:
        #         break
        #     print("test:",line)


    def stop_simulator(self):
        print("stopping simulator")
        self._simproc.sendline("exit")
        self._simproc.expect(pexpect.EOF)
        self._simproc = None

        # print("COMMAND TIMES:",self.command_times)
        # print("COMMAND COUNT:",self.command_count)


    def _load_portmap(self):

        # TODO once naming structure can handle -r, do that
        port_info = self._pass_command("report_objects [get_objects]").split("\n")

        portmap = {}
        for i in range(len(port_info)):

            port = port_info[i]
            # currently missing: proper interpretation of packed multi-dimensional arrays TODO
            port_info_match = re.search(r"{(?P<full_portname>[a-zA-Z/_0-9]*)(\[(?P<width_hi>\d+):(?P<width_lo>\d+)\])*}", port)
            full_portname = port_info_match.group('full_portname')
            width_hi = port_info_match.group('width_hi')
            width_lo = port_info_match.group('width_lo')

            port_size = 1
            if width_hi is not None:
                port_size = int(width_hi) - int(width_lo)

            portmap[full_portname] = (i,port_size)
                

        return portmap


    def list_port_names(self):
        assert self._portmap is not None
        return self._portmap
    
    def advance(self,steps):
        self._pass_command(f"run {steps} ps")


    def sim_getvalue(self,port):

        value = self._pass_command(f"get_value -radix bin {port}")
        # print("port",port, "value binstr",value)
        return value


    def sim_setvalue(self,port,val):
        self._pass_command(f"set_value -radix bin {port} {val}")


    def sim_getsimtime(self):
        time_str = self._pass_command("current_time").split()
        # print('TIME_STR',time_str)
        return int(get_sim_steps(int(time_str[0]),unit=time_str[1]))



    def sim_isactive(self):
        return self._simproc is not None


def get_sim_steps(time,unit='steps'):

    # TODO hard-coded to 1ns/1ps timescale
    power = {
        'steps': -12,
        'fs': -15,
        'ps': -12,
        'ns': -9,
        'us': -6,
        'ms': -3,
        'sec': 0
    }
    total_power_adjust = power[unit] + 12
    return time * 10**total_power_adjust
