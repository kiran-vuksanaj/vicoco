
import cocotb.runner

from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, TextIO, Tuple, Type, Union
PathLike = Union["os.PathLike[str]", str]
Command = List[str]
Timescale = Tuple[str, str]
from cocotb.runner import VHDL,Verilog

import subprocess
from os import environ
from glob import glob

import csv

file_dump_waves = """
`timescale 1ns / 1ps
module cocotb_vivado_dump();
  initial begin
    $dumpfile("{waveform_filename}");
    $dumpvars(0,{toplevel});
  end
endmodule
"""

class Vivado(cocotb.runner.Simulator):

    supported_gpi_interfaces = {'verilog': ['xsi'], 'vhdl': ['xsi']}

    def __init__(self,mode,xilinx_root=None,part_num=None):
        self.launch_mode = mode
        self.xilinx_libraries = set()
        self.fst_output = True

        if xilinx_root is not None:
            self.xilinx_root = xilinx_root
        else:
            self.xilinx_root = environ.get('XILINX_VIVADO',None)

        self.part_num = part_num
        
        super().__init__()
    
    def _simulator_in_path(self) -> None:
        # if 'XILINX_VIVADO' not in environ:
        if self.xilinx_root is None:
            raise Warning("WARNING: Vivado not found in path. Run {VIVADO}/settings64.sh if you haven't, or specify get_runner('vivado',xilinx_root={INSTALL_DIRECTORY}).")

    def _full_path(self,vivado_cmd):
        return str(Path(self.xilinx_root) / 'bin' / vivado_cmd)
        
    def _file_info_to_parse(self, file_info,working_dir):
        """
        converts list of traits as written in a "file_info.txt" file to a command to compile the file

        """
        if(len(file_info) == 5):
             filename, language, output_lib, filepath, include_dirs = file_info
        else:
            filename, language, output_lib, filepath = file_info
            include_dirs = ""
        cmd = []

        language = language.lower()
        if language == "systemverilog":
            cmd += [self._full_path('xvlog'), '-sv', '--incr', '--relax']
        elif language == "verilog":
            cmd += [self._full_path('xvlog'), '--incr', '--relax']
        elif language == "vhdl":
            cmd += [self._full_path('xvhdl'), '--incr', '--relax']

        cmd += ['-work',f'{output_lib}=xsim.dir/{output_lib}']

        absolute_path = working_dir / filepath

        if "/tools/Xilinx" in filepath:
            real_start = filepath.index("/tools/Xilinx")
            filepath = filepath[real_start:]
            absolute_path = Path(filepath)
        
        absolute_path = absolute_path.resolve()
        cmd += [str(absolute_path)]

        if (language != "vhdl"):
            include_dirs = include_dirs.split("incdir=")
            for dirname in include_dirs:
                dirname = dirname.strip('\'"')
                if (len(dirname)>0):
                    absolute_path = working_dir / dirname
                    absolute_path = absolute_path.resolve()

                    cmd += ['-i', str(absolute_path)]

        # print(cmd)
        return cmd
        

    def _outofdate_ip(self,xci_files: Sequence[PathLike]) -> Sequence[PathLike]:

        # if self.always:
        #     return xci_files

        outofdate = []
        
        for xci_file in xci_files:

            xci_file = Path(xci_file).resolve()
            ip_name = xci_file.stem
            sample_ip_user_file = self.build_dir / ".ip_user_files" / "sim_scripts" / ip_name / "xsim" / "README.txt"

            if cocotb.runner.outdated(sample_ip_user_file,[xci_file]):
                outofdate.append(xci_file)

        print("Out Of Date: ",outofdate)
        return outofdate
        
    def _ip_synth_cmds(self, xci_files: Sequence[PathLike]) -> Sequence[Command]:
        """
        file-generation + commands in order to synthesize ip for simulation
        """

        if self.part_num == None:
            partNum = "xc7s50csga324-1"
        else:
            partNum = self.part_num

        # build tiny vivado script to usep

        ip_cmds: Sequence[Command] = []

        outdated_xci_files = self._outofdate_ip(xci_files)

        if (len(outdated_xci_files) > 0):
            with open(self.build_dir / "build_ip.tcl","w") as f:
                f.write(f"set partNum {partNum}\n")
                f.write("set_part $partNum\n")

                for xci_path in outdated_xci_files:
                    f.write(f"read_ip {xci_path}\n")
                f.write("export_ip_user_files\n")
            self._execute( [[self._full_path('vivado'), '-mode', 'batch', '-source', 'build_ip.tcl']], cwd=self.build_dir)

        
        ip_user_root = self.build_dir / '.ip_user_files'
        
        # Move mem_init_files directory contents to build directory to be accessed during simulation
        mem_init_files = glob( str(ip_user_root/'mem_init_files'/'*') )
        if (len(mem_init_files) > 0):
            self._execute( [['cp'] + mem_init_files + ['.']], cwd=self.build_dir)
        

        for xci_filename in xci_files:
            xci_as_path = Path(xci_filename)
            ip_name = xci_as_path.stem
            print("IP Name:", ip_name)


            # ipstatic = ip_user_root / 'ipstatic' / 'ip'
            # for child in ipstatic.iterdir():
            #     if child.is_dir():
            #         dir_to_include = child / 'hdl'
            #         self.includes.append(str(dir_to_include))

            vcs_script_root = ip_user_root / 'sim_scripts' / ip_name / 'vcs'
            vcs_file_info = vcs_script_root / 'file_info.txt'

            with open(str(vcs_file_info),newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    library_name = row[2]
                    self.xilinx_libraries.add( library_name )

            xsim_script_root = ip_user_root / 'sim_scripts' / ip_name / 'xsim'

            xsim_file_info = xsim_script_root / 'file_info.txt'
            with open(str(xsim_file_info),newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    module_name = row[0]
                    library_name = row[2]
                    module_name = module_name[:module_name.index('.')]
                    if module_name != ip_name:
                        self.elab_modules.append(f"{library_name}.{module_name}")
                    # ip_cmds.append ( self._file_info_to_parse(row,xsim_script_root) )

            
            vhdl_proj = xsim_script_root / 'vhdl.prj'
            vlog_proj = xsim_script_root / 'vlog.prj'

            if vhdl_proj.exists():
                ip_cmds.append( [self._full_path('xvhdl'),'--incr','--relax','-prj',str(vhdl_proj)] )
            if vlog_proj.exists():
                ip_cmds.append( [self._full_path('xvlog'),'--incr','--relax','-prj',str(vlog_proj)] + self._get_include_options(self.includes) )

            # ip_cmds.append( ['sh','-c', f"cd {xsim_script_root} && ./{ip_name}.sh -step compile"] )

        return ip_cmds

    def _get_include_options(self, includes):
        out = []
        for incl in includes:
            out.extend(['-i',str(incl)])
        return out

    def _write_wavedump_file(self):

        toplevel = self.hdl_toplevel
        if "." in toplevel:
            toplevel = toplevel.split(".")[-1]

        self.waveform_filename = str(self.build_dir / f'{toplevel}.vcd')
        if self.fst_output:
            self.waveform_filename = self.waveform_filename.replace('.vcd','.fst')
        print(f"waveform output to {self.waveform_filename}")
        
        file_text = file_dump_waves.format(waveform_filename=self.waveform_filename,toplevel=toplevel)
        file_name = self.build_dir / "cocotb_vivado_dump.v"
        with open(file_name,'w') as f:
            f.write(file_text)

        self.elab_modules.append("work.cocotb_vivado_dump")
        self.sources.append(file_name)

    def _define_args(self) -> Sequence[str]:

        out = []
        for key,val in self.defines.items():
            out.extend(['-d',f'{key}={val}'])
        return out
        
    def _build_command(self) -> Sequence[Command]:

        define_args = self._define_args()
        
        self.elab_modules = []

        self.xilinx_libraries.add( 'xpm' )
        self.xilinx_libraries.add( 'secureip' )



        if self.waves:
            self._write_wavedump_file()
        
        cmds = []

        ip_sources = []
        verilog_build_args = ["-{}".format(arg) for arg in self.build_args if type(arg) in (str,Verilog)]
        vhdl_build_args = ["-{}".format(arg) for arg in self.build_args if type(arg) in (str,VHDL)]

        for source in self.sources:
            if cocotb.runner.is_verilog_source(source):
                # TODO maybe should be redone for a .v file ending?
                cmds.append([self._full_path('xvlog'),'-sv', '--incr', '--relax', str(source)] + self._get_include_options(self.includes) + define_args + verilog_build_args)
            elif cocotb.runner.is_vhdl_source(source):
                cmds.append([self._full_path('xvhdl'), '--incr', '--relax', str(source)] + self._get_include_options(self.includes) + define_args + vhdl_build_args)
            elif ".xci" in str(source):
                # JANK as fuck
                ip_sources.append(str(source))
            else:
                raise ValueError(
                    f"Unknown file type: {str(source)} can't be compiled."
                )


        if len(ip_sources) > 0:
            cmds.extend( self._ip_synth_cmds(ip_sources) )
        # cmds.append(['vivado', '-mode', 'batch', '-source', 'build_ip.tcl'])
        # cmds.append(['xvhdl', '--incr', '--relax', '-prj', '.ip_user_files/sim_scripts/cordic_0/xsim/vhdl.prj'])
        # cmds.append
        # cmds.append(['xvhdl','--incr', '--relax', '-prj', '/home/kiranv/Documents/fpga/vivgui/getfifos/getfifos.ip_user_files/sim_scripts/cordic_0/xsim/vhdl.prj'])


        self.snapshot_name = "pybound_sim"

        elab_cmd = [self._full_path("xelab"),
                    "-top", self.hdl_toplevel,
                    "-snapshot", "pybound_sim",
                    ] + self._get_include_options(self.includes) + define_args

        elab_cmd.extend(self.elab_modules)

        for library_name in self.xilinx_libraries:
            elab_cmd.extend(['-L',library_name])
        
        if (self.launch_mode == 'XSI'):
            elab_cmd.extend(['-dll','-debug','wave'])
        else:
            elab_cmd.extend(['-debug','all'])
        
        cmds.append(elab_cmd)

        print("Build Commands: ",cmds)

        return cmds

    def _test_command(self) -> Sequence[Command]:
        # bridge to cross: everything needs to become internalized to a module

        cmd = [
            ["python3", "-m", "vicoco"]
        ]

        xilinx_root = self.xilinx_root
        self.env["LD_LIBRARY_PATH"] = f"{xilinx_root}/lib/lnx64.o:{xilinx_root}/lib/lnx64.o/Default:"
        self.env["VIVADO_SNAPSHOT_NAME"] = "pybound_sim"
        self.env["TOPLEVEL_LANG"] = self.hdl_toplevel_lang
        self.env["XSIM_INTERFACE"] = self.launch_mode

        if self.waves and self.fst_output:
            cmd.append(["vcd2fst", self.waveform_filename, self.waveform_filename])
        
        return cmd

    def _get_parameter_options(self, paramters: Mapping[str, object]) -> Command:
        # TODO make this actually return stuff properly... i think fitting the -generic_top "PARAM=1" format
        return []
        

def get_runner(simulator_name: str, **kwargs) -> cocotb.runner.Simulator:
    """
    this is... pretty jank. manually add 'vivado' to the list of supported sims
    """

    if simulator_name == "vivado":
        return Vivado('XSI',**kwargs)
    elif simulator_name == "vivado_tcl":
        return Vivado('TCL')
    else:
        return cocotb.runner.get_runner(simulator_name)


def makefile_recreate():
    """
    match what the makefile does, so as to motivate the proper functions for the runner type
    """

    sources = ["counter.sv", "counter_tb.sv"]

    toplevel = "counter"
    snapshot_name = "pybound_sim"

    module = "simple_cocotbtest"

    for source in sources:
        compile_source_cmd = ["xvlog", "-sv", source]
        status = subprocess.run(compile_source_cmd)
        print(f'compile {source} status: {status}')

    elab_cmd = ["xelab", "-top", toplevel, "-snapshot", snapshot_name, "-debug", "wave", "-dll"]
    status = subprocess.run(elab_cmd)
    print(f'elaborate status: {status}')

    new_env = environ
    xilinx_root = environ["XILINX_VIVADO"]
    new_env["LD_LIBRARY_PATH"] = f"{xilinx_root}/lib/lnx64.o:{xilinx_root}/lib/lnx64.o/Default:"
    new_env["SNAPSHOT_NAME"] = "pybound_sim"
    new_env["MODULE"] = module
    
    launch_cmd = ["python3", "-m", "vicoco"]
    status = subprocess.run(launch_cmd, env=new_env)
    print(f'launch status: {status}')


if __name__=="__main__":
    makefile_recreate()
