#!/usr/bin/env python3

# minimally adapted from themperek/cocotb-vivado ; thank you!!

from vicoco.interface_xsim import XSimInterface, XSI_XSimInterface
# from vicoco.tcl_loader import Tcl_XSimInterface

from vicoco.vivado_handles import XsimRootHandle, XsiPortHandle, TimedCbClosure, ValueChangeCbClosure, ReadWriteCbClosure, ReadOnlyCbClosure

class XSimManager:

    """
    entity to keep track of a simulation running, advance simulation for each subsequent trigger
    """

    _inst = None
    
    def __init__(self, mode):

        interface_type = XSimInterface
        if mode=="XSI":
            interface_type = XSI_XSimInterface
        elif mode == "TCL":
            interface_type = Tcl_XSimInterface

        self.sim = interface_type()
        self.ports = {}
        self._timerqueue = {
            0:[]
        }
        self._vcqueue = []
        
        self._readwrite_queue = []
        self._readonly_queue = []

        self.time = 0

        self.is_running = False

    def _sim_advance(self,steps):
        self.time += steps
        self.sim.advance(steps)

    def _attempt_valuechange_callbacks(self):
        # print(f"making attempts on {len(self._vcqueue)}")
        # something_ran = False
        for vc in self._vcqueue:
            if vc.cb is not None and vc.change_condition_satisfied():
                # print("running vc")
                vc()
                # something_ran = True
                # print("removing one")
                self._vcqueue.remove(vc)

        # return something_ran
        
    def _any_callbacks_primed(self,callback_list):
        for callback in callback_list:
            if callback.cb is not None:
                return True
        return False

    def run(self):
        next_time = 0
        while len(self._timerqueue) > 0:

            # loop between normal state -> readwrite state
            # during normal state: check valuechange callbacks


            # first normal state: execute all callbacks scheduled for this timestep
            # (in order they were registered)
            for cb in self._timerqueue[next_time]:
                if cb is not None:
                    cb()
            
            self._timerqueue.pop(next_time)

            self._attempt_valuechange_callbacks()

            if (not self.is_running):
                break
            
            while(self._readwrite_queue):
                # release for readwrite phase, values will be set
                # print(f"New RW cycle at time {next_time}")
                self._sim_advance(0)
                released_rw_cb = self._readwrite_queue.pop(0)
                if released_rw_cb is not None:
                    released_rw_cb()

                # once ReadWrite callback executes, all pending writes are complete
                # so, in new stable state, re-attempt value-change callbacks
                self._attempt_valuechange_callbacks()

            # print("Read Only callbacks: ",self._readonly_queue)
            # once this exits, there are no more readwrite stages
            # so readonly callbacks can run (cannot register value-sets)
            self._sim_advance(0)
            self._attempt_valuechange_callbacks()
            for cb in self._readonly_queue:
                if cb is not None:
                    cb()

            self._readwrite_queue = []
            self._readonly_queue = []

            if (len(self._timerqueue) == 0):
                continue
            
            next_time = min(self._timerqueue.keys())
            while(not(self._any_callbacks_primed( self._timerqueue[next_time] ))):
                self._timerqueue.pop(next_time)
                next_time = min(self._timerqueue.keys())
                
            time_to_run = next_time - self.get_sim_time()
            self._sim_advance(time_to_run)
            # print("NEW TIME STEP",next_time)

        
    def get_root_handle(self):
        return XsimRootHandle(self)


    def _init_port_handles(self,port_info):
        out = {}
        for portname in port_info.keys():
            handle = XsiPortHandle(self,portname,port_info[portname][1])
            out[ portname ] = handle
        return out
    
    def start_simulator(self):
        self.sim.launch_simulator()
        self.ports = self._init_port_handles( self.sim.list_port_names() )
        self.is_running = True

    def register_timed_cb(self,t,cb,ud):

        ret = TimedCbClosure(t,cb,ud)

        time_to_fire = self.get_sim_time()+t

        if time_to_fire in self._timerqueue:
            self._timerqueue[time_to_fire].append(ret)
        else:
            self._timerqueue[time_to_fire] = [ret]
        
        return ret

    def register_vc_cb(self,handle,callback,edge,ud):

        closure = ValueChangeCbClosure(handle,edge,callback,ud)
        self._vcqueue.append(closure)
        return closure

    def register_readwrite_cb(self,callback,trigger):
        closure = ReadWriteCbClosure(callback,trigger)
        self._readwrite_queue.append( closure )
        return closure

    def register_readonly_cb(self,callback,trigger):
        closure = ReadOnlyCbClosure(callback,trigger)
        self._readonly_queue.append( closure )
        return closure
        

    def get_sim_time(self):
        return self.time
        # return self.sim.sim_getsimtime()

    def sim_setvalue(self,name,value):
        self.sim.sim_setvalue(name,value)

    def stop_simulator(self):
        # print("queues:")
        # print(f"timed callbacks: {self._timerqueue}")
        # print(f"value change callbacks: {self._vcqueue}")
        # print(f"read-write callbacks: {self._readwrite_queue}")
        # print(f"read-only callbacks: {self._readonly_queue}")

        self.is_running = False
        self.sim.stop_simulator()

    @classmethod
    def inst(cls):
        if cls._inst is None:
            raise Exception("Simulation manager not initialized")
        return cls._inst

    @classmethod
    def init(cls,mode):
        cls._inst = XSimManager(mode)
        return cls._inst
