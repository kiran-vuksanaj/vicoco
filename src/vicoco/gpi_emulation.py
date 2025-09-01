#!/usr/bin/env python3

# minimally adapted from themperek/cocotb-vivado ; thank you!!

from vicoco.manager import XSimManager

# ********************************************************************
# * These constants are used by cocotb 'main'
# ********************************************************************
MODULE = 0
STRUCTURE = 1
REG = 2
NET = 3
NETARRAY = 4
REAL = 5
INTEGER = 6
ENUM = 8
STRING = 9
GENARRAY = 10

RISING = 11
FALLING = 12
VALUE_CHANGE = 13
PACKED_STRUCTURE = 14
LOGIC = 15
LOGIC_ARRAY = 16

PACKAGE = None


def log_msg(*args, **kwargs):
    raise Exception("Nuh Uh")


def get_root_handle(root_name):
    return XSimManager.inst().get_root_handle()

def register_timed_callback(t, cb, ud):
    return XSimManager.inst().register_timed_cb(t,cb,ud)


def register_value_change_callback(handle,callback,edge,ud):
    return XSimManager.inst().register_vc_cb(handle,callback,edge,ud)

def register_readonly_callback(cb,ud):
    # print("READONLY CALLBACK!")
    return XSimManager.inst().register_readonly_cb(cb,ud)


def register_nextstep_callback(cb,ud):
    return register_timed_callback(1,cb,ud)

def register_rwsynch_callback(cb, ud):
    # print("registering rwSync callback")
    # return register_timed_callback(0,cb,ud)
    return XSimManager.inst().register_readwrite_cb(cb,ud)

def stop_simulator():
    # print("STOPPING SIMULATOR")
    XSimManager.inst().stop_simulator()
    # print("simulator stop success")

def log_level(level):
    # TODO skipping 4 now
    pass

def is_running(*args, **kwargs):
    raise Exception("Nuh Uh")

def get_sim_time():
    time = XSimManager.inst().get_sim_time()
    return (0,time) # ? maybe?

def get_precision():
    # HACK TODO hardcoded to picosecond precision...
    return -12

def get_simulator_product():
    return "vivado xsim"

def get_simulator_version():
    return "???"

OBJECTS = []
