#!/usr/bin/env python3
# minimally adapted from themperek/cocotb-vivado ; thank you!!

import vicoco._gpi_enums as GPI_ENUMS

import abc
from collections.abc import Callable
from typing import Dict, List, Mapping, Optional, Sequence, TextIO, Tuple, Type, Union, Any
# from vicoco.gpi_emulation import gpi_cb_hdl, gpi_sim_hdl

class XsimRootHandle():
    def __init__(self, mgr):
        self.mgr = mgr

    def get_const(self):
        return True

    def get_type(self):
        return GPI_ENUMS.MODULE

    def get_name_string(self):
        return "top"

    def get_type_string(self):
        return "MODULE"

    def get_definition_name(self):
        return ""

    def get_definition_file(self):
        return ""

    def iterate(self, nothing):
        for name in self.mgr.ports:
            yield self.mgr.ports[name]

    def get_handle_by_name(self, name, discovery_method = 1):
        if name not in self.mgr.ports:
            return

        return self.mgr.ports[name]

class XsiPortHandle():
    def __init__(self, mgr, name, size):
        self.name = name

        self.size = size
        self.mgr = mgr

        if size == 1:
            self.type_int = GPI_ENUMS.LOGIC
            self.type_str = "LOGIC"
        else:
            self.type_int = GPI_ENUMS.LOGIC_ARRAY
            self.type_str = "LOGIC_ARRAY"

    def get_const(self):
        return False

    def get_type(self):
        return self.type_int

    def get_name_string(self):
        return self.name

    def get_type_string(self):
        return "REG"

    def get_definition_name(self):
        return ""

    def get_definition_file(self):
        return ""

    def get_num_elems(self):
        return self.size

    def get_range(self):
        return (self.size - 1, 0)

    def set_signal_val_int(self, action, value):
        # also what does action do? answer: action is FORCE, DEPOSIT, RELEASE, OR NO_DELAY.
        str_value = f"{value:0{self.size}b}"
        self.set_signal_val_binstr(action,str_value)

    def set_signal_val_binstr(self, action, value):
        # print(f"setting {self.name} to {value}, action type={action}")
        self.mgr.sim.sim_setvalue(self.name, value)

    def get_signal_val_binstr(self):
        value = self.mgr.sim.sim_getvalue(self.name)
        # print(f"getting {self.name}, its equal to {value}")
        # this should return a binstr
        return value
        # format_str = "{value:0"+str(self.size)+"b}"
        # binstr = format_str.format(value=value)
        # return binstr

    def get_signal_val_int(self):
        value = self.get_signal_val_binstr()
        value = int(value,2)
        return value

class CbClosure():
    def __init__(self) -> None:
        self.cb: Union[Callable[[Any],None],None] = None
        self.ud: Any = None

    def __call__(self):
        if self.cb is not None:
            self.cb(self.ud)

    def deregister(self):
        # print(f"CALLBACK DEREGISTERED! {self}")
        self.cb = None

class TimedCbClosure(CbClosure):
    def __init__(self, time_off, cb, ud):
        self.time_off = time_off
        self.cb = cb
        self.ud = ud
        self.cb_id = 1

class ValueChangeCbClosure(CbClosure):

    def __init__(self, handle, edge, cb, ud):
        self.handle = handle
        self.cb = cb
        self.ud = ud
        self.edge = edge

        # self.previous_value = 0
        try:
            self.previous_value = handle.get_signal_val_int()
        except ValueError:
            self.previous_value = None

    def change_condition_satisfied(self):
        try:
            current_value = self.handle.get_signal_val_int()
        except ValueError:
            current_value = None

        # print(f"Change condition satisfied? {self.previous_value}, {current_value}, {self.handle}, {self.edge}")
        if self.edge == 1:
            out = (current_value == 1) and (self.previous_value == 0 or self.previous_value is None)
        else:
            out = (current_value == 0) and (self.previous_value == 1 or self.previous_value is None)

        self.previous_value = current_value
        return out

class ReadWriteCbClosure(CbClosure):
    def __init__(self, callback, trigger):
        self.cb = callback
        self.ud = trigger

class ReadOnlyCbClosure(CbClosure):
    def __init__(self, callback, trigger):
        self.cb = callback
        self.ud = trigger
