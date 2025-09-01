#!/usr/bin/env python3

class Tcl_XSimManager:

    _inst = None

    @classmethod
    def inst(cls):
        if cls._inst is None:
            raise Exception("Simulation manager not initialized")
        return cls._inst

    @classmethod
    def init(cls,mode):
        cls._inst = Tcl_XSimManager(mode)
        return cls._inst

    def __init__(self):
        self._simproc = None

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
