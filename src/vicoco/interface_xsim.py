#!/usr/bin/env python3

import abc
from vicoco.xsi_loader import Xsi_Loader

class XSimInterface(abc.ABC):

    """
    abstract base class for either an XSI-based interface or a TTY-TCL interface
    """

    def __init__(self):
        pass

    @abc.abstractmethod
    def launch_simulator(self):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def stop_simulator(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def list_port_names(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def advance(self,steps):
        raise NotImplementedError()

    @abc.abstractmethod
    def sim_getvalue(self,port):
        raise NotImplementedError()

    @abc.abstractmethod
    def sim_setvalue(self,port,val):
        raise NotImplementedError()

    @abc.abstractmethod
    def sim_getsimtime(self):
        raise NotImplementedError()        
    
    @abc.abstractmethod
    def sim_isactive(self):
        raise NotImplementedError()

class XSI_XSimInterface(XSimInterface):
    """
    Implementation of interface interactions using the Xsi_Loader class
    """
    
    def launch_simulator(self):
        self._loader = Xsi_Loader()
        self._loader.open_handle(None,"test.wdb")
        self._portmap = self._load_portmap()
        self._active = True

    def stop_simulator(self):
        self._loader.close()
        self._active = False

    def _load_portmap(self):
        portmap = {}
        i = 0
        portname = self._loader.get_port_name(i)
        portsize = self._loader.get_port_size(i)
        while portname is not None:
            portmap[portname] = (i,portsize)
            # portmap.append((portname,portsize))
            i += 1
            portname = self._loader.get_port_name(i)
            portsize = self._loader.get_port_size(i)

        # print('PORTMAP',portmap)
        return portmap


    def list_port_names(self):
        return self._portmap
        # return self._portmap


    def advance(self,steps):
        self._loader.run(steps)

    def sim_getvalue(self,portname):
        # portnum = [info[0] for info in self._portmap].index(portname)
        portnum,portsize = self._portmap[portname]
        return self._loader.get_value(portnum,portsize)

    def sim_setvalue(self,portname,val):
        portnum,portsize = self._portmap[portname]
        # portnum = [info[0] for info in self._portmap].index(portname)
        self._loader.put_value(portnum,portsize,val)

    def sim_getsimtime(self):
        return self._loader.get_time()
        
    def sim_isactive(self):
        return self._active



def tiny_testbench():
    xsim = XSI_XSimInterface()
    print(xsim.list_port_names())

    xsim.sim_setvalue("clk",0)
    xsim.advance(300)
    print(xsim.sim_getvalue("clk"))
    xsim.sim_setvalue("clk",1)
    xsim.advance(300)
    print(xsim.sim_getvalue("clk"))
    
if __name__ == "__main__":
    tiny_testbench()
