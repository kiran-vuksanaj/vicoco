"""
Python runner for Vivado within the structure of the Cocotb Python runner launcher.
"""
from __future__ import annotations

import csv
import logging
import os
from collections.abc import Mapping, Sequence
from glob import glob
from os import environ
from pathlib import Path

from cocotb import runner
from cocotb.runner import VHDL, Simulator, Verilog

PathLike = os.PathLike[str]|str
Command = list[str]
Timescale = tuple[str, str]

FILE_DUMP_WAVES = """
{timescale_declaration}
module cocotb_vivado_dump();
  initial begin
    $dumpfile("{waveform_filename}");
    $dumpvars(0,{toplevel});
  end
endmodule
"""

FILE_FORCE_EXPORT = """
export_simulation
exit
"""

class Vivado(Simulator):
    """
    Cocotb Python runner implementation for Vivado for use with vicoco/cocotb_vivado
    """

    supported_gpi_interfaces = {'verilog': ['xsi'], 'vhdl': ['xsi']}
    LAUNCHING_MODULE = "vicoco"

    def __init__(
            self,
            mode: str = 'XSI',
            xilinx_root: str|None = None,
            part_num: str|None = None,
            xilinx_extra_libraries: list[str]|None = None,
            fst_output: bool = True,
            validate_flags: bool = True,
            extra_global_modules: list[str]|None = None
            ):
        """
        Initialize the Vivado Python runner.
        xilinx_root:
            Optional manual specification of root xilinx vivado path.
            if unspecified, $XILINX_VIVADO is checked instead.
        part_num:
            Part number to be used for default IP generation from XCI
            files. if unspecified, $COCOTB_DEFAULT_PART_NUM is checked instead,
            and if still unspecified we default to the part in an Arty S7;
            the xc7s50-csga324-1.
        xilinx_extra_libraries:
            List of additional libraries to include when elaborating
            the design. All necessary libraries for specified IP will
            be included by default.
        fst_output:
            If outputting a waveform file, the VCD file will be converted
            to an FST file. Requires use of vcd2fst, from gtkwave. Default
            value is True, if vcd2fst is found.
        validate_flags:
            enable additional warnings regarding common flags used in other
            simulators, and exclude them from Vivado flags. Default True
        extra_global_modules:
            Additional modules to elaborate with in the `xelab` command.
        """

        self.launch_mode = mode

        self.xilinx_libraries = set(xilinx_extra_libraries or [])
        self.fst_output = fst_output
        self.validate_flags = validate_flags

        self.elab_modules = list(extra_global_modules or [])

        self.exported_simulations = []

        self.xilinx_root = xilinx_root or environ.get('XILINX_VIVADO',None)

        self.part_num = part_num or environ.get('COCOTB_DEFAULT_PART_NUM','xc7s50-csga324-1')
        self.waveform_filename = ""
        self.snapshot_name = "pybound_sim"
        self.force_export_tcl = False
        self.waves = False

        self.log = logging.getLogger(__name__)
        logging.basicConfig()

        super().__init__()


    def _timescale_declaration(self) -> str:
        """
        Verilog declaration of timescale matching to specified build/test timescale arg
        """
        timescale = self.timescale
        if timescale is None:
            return ""
        assert isinstance(timescale,tuple)
        assert len(timescale) == 2
        stepsize,precision = timescale
        return f"`timescale {stepsize} / {precision}"


    def _simulator_in_path(self) -> None:
        """
        Raise error if an installation of Vivado is not specified
        """
        if self.xilinx_root is None:
            raise SystemExit(
                "ERROR: Vivado not found in path. Run {VIVADO}/settings64.sh if you"
                "haven't, or specify get_runner('vivado',xilinx_root={INSTALL_DIRECTORY})."
            )

    def _vivado_exec_path(self,vivado_cmd) -> str:
        """Returns full path string to the specified ``vivado_cmd`` in the specified xilinx_root"""
        return str(Path(self.xilinx_root) / 'bin' / vivado_cmd)


    def _outofdate_ip(self,ip_files: Sequence[PathLike]) -> Sequence[PathLike]:
        """
        Given list of XCI/BD files, returns a filtered list of files
        which have been modified more recently than their associated
        generated files.
        """
        def ip_file_outofdate(ip_file: PathLike) -> bool:
            ip_file = Path(ip_file).resolve()
            ip_name = ip_file.stem
            # this is a file that [seems to be] generated with every IP generation
            # used to compare modify times of generated files and source XCI/BD file
            sample_ip_user_file = self.build_dir.joinpath(
                ".ip_user_files",
                "sim_scripts",
                ip_name,
                "xsim",
                "README.txt"
                )

            return runner.outdated(sample_ip_user_file,[ip_file])

        outofdate = [ip_file for ip_file in ip_files if ip_file_outofdate(ip_file)]
        self.log.info("Out Of Date: %s",outofdate)
        return outofdate

    def execute_tcl(
            self,
            tcl_files: list[PathLike],
            result_file: PathLike|None = None,
            tcl_mode: str = 'batch'
    ) -> None:
        """
        Calls Vivado to execute the specified TCL files in batch mode. If result_file is specified,
        only run the TCL script if it's been modified more recently than result_file.
        """
        tcl_files = [Path(tcl_file) for tcl_file in tcl_files]

        for tcl_file in tcl_files:
            assert tcl_file.exists(), f"TCL file {tcl_file} does not exist"

        if result_file and not runner.outdated(Path(result_file),tcl_files[0:1]):
            return

        source_args = []
        for tcl_file in tcl_files:
            tcl_file_resolved = Path(tcl_file).resolve()
            source_args.extend(['-source', str(tcl_file_resolved)])

        self._execute([[
            self._vivado_exec_path('vivado'),
            '-mode',tcl_mode,
            *source_args
            ]], cwd=self.build_dir)

    def add_export_simulation_tcl(
            self,
            tcl_file: PathLike|None = None,
            mode: str = "batch",
            force_export: bool = False,
            result_dir: PathLike = "export_sim",
            result_file: PathLike|None = None,
    ):
        """
        Registers a TCL script and resulting exported simulation to be used as
        an additional source at the build stage.

        tcl_file ::
            TCL file to execute at build stage. Can be unspecified for an
            already-exported simulation (as long as result_dir is specified)
        mode :: (default "batch")
            Vivado mode in which to execute the TCL command.
        force_export (default False) ::
            If set to True, adds the "export_simulation; exit" commands to the
            end of the specified TCL file. Useful for default TCL files exported
            using Vivado's ``write_bd_tcl`` command.
        result_dir ::
            Directory into which simulation scripts have been exported, for
            cocotb compilation purposes. Defaults to ``export_sim``, the
            default directory chosen by Vivado's ``export_simulation`` command.
            If the path is relative, it will be found from the directory where
            the tcl file is launched, the ``sim_build/`` dir.
        result_file ::
            Optional; any filename generated by the TCL script's execution, used
            for checking whether the generated simulation is out of date. Must
            be a relative path.
        """

        if tcl_file and force_export:
            self.force_export_tcl = True
            tcl_files = [tcl_file,self.build_dir / "force_export.tcl"]
        elif tcl_file:
            tcl_files = [tcl_file]
        else:
            tcl_files = []

        self.exported_simulations.append((tcl_files,mode,result_file,result_dir))

    def _write_generation_tcl(self, ip_files: Sequence[PathLike]) -> PathLike:
        """
        Writes file at $BUILD_DIR/build_ip.tcl to generate the specified IP files.
        Returns the path of the generated TCL file.
        """
        generated_file_path = self.build_dir / "build_ip.tcl"
        with open(generated_file_path,"w",encoding="utf-8") as f:
            f.write(f"set partNum {self.part_num}\n")
            f.write("set_part $partNum\n")

            for ip_path in ip_files:
                f.write(f"add_files -norecurse {ip_path}\n")
                # f.write(f"read_ip {xci_path}\n")
            f.write("export_ip_user_files\n")
        return generated_file_path

    def _write_force_export_tcl(self) -> PathLike:
        """
        Writes file at $BUILD_DIR/force_export.tcl which exports simulation and exits.
        Returns the path of the generated TCL file.
        """
        generated_file_path = self.build_dir / "force_export.tcl"
        with open(generated_file_path,"w",encoding="utf-8") as f:
            f.write(FILE_FORCE_EXPORT)
        return generated_file_path

    def _parse_file_info(self,file_info_file: PathLike) -> list[dict[str,str]]:
        """
        Reads a file_info.txt file and yields a list of labeled attributes
        for each entry in the file.
        """
        def row_to_labeled_attributes(row):
            entry = {}
            entry['module_filename'] = row[0]
            entry['module_name'] = row[0][:row[0].index('.')]
            entry['language'] = row[1]
            entry['library'] = row[2]
            entry['source_path'] = row[3]
            if len(row) > 4:
                # rooted at weird location, keep in mind...
                entry['incdir'] = row[4]
            return entry

        with open(str(file_info_file),newline='',encoding="utf-8") as f:
            reader = csv.reader(f)
            return [ row_to_labeled_attributes(row) for row in reader ]

    def _compile_cmd(self,src_file: PathLike, language: str, prj=False) -> Command:
        """
        Returns command to compile the specified ``src_file``.
        """
        src_file = Path(src_file).resolve()
        language_compiler = {
            'vhdl': self._vivado_exec_path('xvhdl'),
            'verilog': self._vivado_exec_path('xvlog')
            }

        compile_exec = language_compiler[language]
        cmd = [compile_exec, '--incr', '--relax', '-work','xil_defaultlib']
        if prj:
            cmd += ['-prj']
        elif src_file.suffix == '.sv':
            cmd += ['-sv']
        cmd += [str(src_file)]

        if language == 'verilog':
            cmd += self._get_include_options(self.includes)

        return cmd



    def _ip_filename_cmds(self, ip_file: PathLike) -> Sequence[Command]:
        """
        Returns appropriate compilation commands for specified XCI/BD file,
        and adds appropriate elaboration libraries + additional modules for
        the elaboration stage.
        """
        ip_name = Path(ip_file).stem
        ip_sim_scripts = self.build_dir / '.ip_user_files' / 'sim_scripts' / ip_name
        return self._ip_dir_cmds(ip_sim_scripts)

    def _ip_dir_cmds(self, ip_sim_scripts: PathLike) -> Sequence[Command]:
        # we look in a handful of locations for the appropriate info
        # 1. any non-xsim "file_info.txt" file holds the appropriate
        #    files to include
        # 2. the xsim "file_info.txt" file indicates whether the
        #    Verilog glbl.v module should be elaborated
        # 3. the xsim "vhdl.prj" and "vlog.prj" can be compiled
        #    by xvhdl and xvlog for all necessary direct source files
        ip_sim_scripts = Path(ip_sim_scripts)

        vcs_script_root = ip_sim_scripts / 'vcs'
        vcs_file_info = self._parse_file_info( vcs_script_root / 'file_info.txt' )

        ip_libraries = {row['library'] for row in vcs_file_info}
        self.xilinx_libraries.update(ip_libraries)

        xsim_script_root = ip_sim_scripts / 'xsim'
        xsim_file_info = self._parse_file_info(xsim_script_root / 'file_info.txt')

        for row in xsim_file_info:
            if 'glbl' in row['module_name']:
                self.elab_modules.append(f"{row['library']}.{row['module_name']}")

        ip_cmds = []
        vhdl_proj = xsim_script_root / 'vhdl.prj'
        vlog_proj = xsim_script_root / 'vlog.prj'

        if vhdl_proj.exists():
            ip_cmds.append( self._compile_cmd(vhdl_proj, 'vhdl', prj=True) )
        if vlog_proj.exists():
            ip_cmds.append( self._compile_cmd(vlog_proj, 'verilog', prj=True) )

        return ip_cmds

    def _ip_synth_cmds(self, ip_files: Sequence[PathLike]) -> Sequence[Command]:
        """
        Given a list of XCI/BD files, returns a sequence of commands to generate
        and compile the specified IP.

        This function also modifies state so that relevant libraries are included in
        elaboration calls.
        """
        # build tiny vivado script to use to generate all out of date IP

        ip_cmds: Sequence[Command] = []

        outdated_ip_files = self._outofdate_ip(ip_files)

        # if there are outdated IP files, write and execute TCL to re-generate
        if len(outdated_ip_files) > 0:
            generate_ip_tcl = self._write_generation_tcl(outdated_ip_files)
            self.execute_tcl([generate_ip_tcl])


        # IP compilation expects contents of mem_init_files/ directory
        # to be present in the cwd; so, we copy those files to the build_dir
        mem_init_files = glob( str(self.build_dir/'.ip_user_files'/'mem_init_files'/'*') )
        if len(mem_init_files) > 0:
            self._execute( [['cp', *mem_init_files,'.']], cwd=self.build_dir)

        for ip_filename in ip_files:
            ip_cmds.extend( self._ip_filename_cmds(ip_filename) )

        return ip_cmds

    def _get_include_options(self, includes):
        out = []
        for incl in includes:
            out.extend(['-i',str(incl)])
        return out

    def _write_wavedump_file(self):
        """
        Write dummy Verilog file to initialize wavedump to VCD/FST formats,
        according to flags specified at initialization
        """

        toplevel = self.hdl_toplevel
        if "." in toplevel:
            toplevel = toplevel.split(".")[-1]

        self.waveform_filename = str(self.build_dir / f'{toplevel}.vcd')
        if self.fst_output:
            self.waveform_filename = self.waveform_filename.replace('.vcd','.fst')
        self.log.info("Waveform output to %s",self.waveform_filename)

        file_text = FILE_DUMP_WAVES.format(
            waveform_filename=self.waveform_filename,
            toplevel=toplevel,
            timescale_declaration=self._timescale_declaration()
        )
        file_name = self.build_dir / "cocotb_vivado_dump.v"
        with open(file_name,'w',encoding="utf-8") as f:
            f.write(file_text)

        self.elab_modules.append("xil_defaultlib.cocotb_vivado_dump")
        self.sources.append(file_name)

    def _define_args(self) -> Sequence[str]:

        out = []
        for key,val in self.defines.items():
            out.extend(['-d',f'{key}={val}'])
        return out

    def _issue_build_warnings(self) -> None:
        """
        Issue special warnings to be aware of when building with Vicoco at the
        compile/elaborate stage.
        """
        if (self.waves and len(self.parameters) > 0):
            self.log.warning(
                "Known Vicoco issue: when top-level parameters are set by Python, Vicoco doesn't "
                "successfully yield a VCD/FST waveform output. A Vivado WDB file will still be "
                "available. Setting waves=False and manually creating a waveform file using Verilog"
                "$dumpfile/$dumpvars commands in your top-level is a workable alternative.\n"
            )
        if (self.validate_flags and '-Wall' in self.build_args):
            self.log.warning(
                "Build arg -Wall is not valid for Vivado simulation. -Wall will be removed "
                "from build_args list. To disable this behavior/warning, set "
                "runner.validate_flags to False."
            )
            self.build_args.remove('-Wall')


    def _issue_test_warnings(self) -> None:
        """
        Issue special warnings to be aware of when building with Vicoco at the
        simulation launching stage
        """
        if (self.waves and self.hdl_toplevel_lang == "vhdl"):
            self.log.warning(
                "Vicoco limitation: VCD/FST waveform output can't be generated on VHDL"
                "top level designs. A Vivado WDB file will still be generated. runner.waves"
                "will be set to False.\n")
            self.waves = False

    def _elab_command(self) -> Command:
        """
        Returns the elaboration command, including all specified defines/libraries/etc.
        """
        # construct xelab command


        define_args = self._define_args()
        param_args = self._get_parameter_options(self.parameters)

        toplevel = self.hdl_toplevel
        if "." not in toplevel:
            toplevel = f"xil_defaultlib.{toplevel}"

        elab_cmd = [self._vivado_exec_path("xelab"),
                    "-top", toplevel,
                    "-snapshot", "pybound_sim",
                    *self._get_include_options(self.includes),
                    *define_args,
                    *param_args
                    ]

        elab_cmd.extend(self.elab_modules)

        for library_name in self.xilinx_libraries:
            elab_cmd.extend(['-L',library_name])

        if self.launch_mode == 'XSI':
            elab_cmd.extend(['-dll','-debug','wave'])
        else:
            elab_cmd.extend(['-debug','all'])

        return elab_cmd


    def _build_command(self) -> Sequence[Command]:
        self._issue_build_warnings()

        define_args = self._define_args()

        self.xilinx_libraries.add( 'xpm' )
        self.xilinx_libraries.add( 'secureip' )

        if self.waves:
            self._write_wavedump_file()

        cmds = []

        ip_sources = []
        verilog_build_args = [str(arg) for arg in self.build_args if type(arg) in (str,Verilog)]
        vhdl_build_args = [str(arg) for arg in self.build_args if type(arg) in (str,VHDL)]

        for source in (Path(source) for source in self.sources):
            if runner.is_verilog_source(source):
                cmds.append(
                    self._compile_cmd( source, 'verilog' ) + define_args + verilog_build_args
                )
            elif runner.is_vhdl_source(source):
                cmds.append(
                    self._compile_cmd( source, 'vhdl' ) + define_args + vhdl_build_args
                )
            elif source.suffix in {'.bd','.xci'}:
                ip_sources.append(str(source))
            else:
                raise ValueError(
                    f"Unknown file type: {source!s} can't be compiled."
                )


        if len(ip_sources) > 0:
            cmds.extend( self._ip_synth_cmds(ip_sources) )

        if self.force_export_tcl:
            self._write_force_export_tcl()
        for tcl_files,mode,result_file,scripts_dir in self.exported_simulations:
            full_result_file = self.build_dir / Path(result_file) if result_file else None
            if tcl_files:
                self.execute_tcl(tcl_files,result_file=full_result_file,tcl_mode=mode)
            full_scripts_dir = Path(scripts_dir)
            if not full_scripts_dir.is_absolute():
                full_scripts_dir = (self.build_dir / full_scripts_dir)
            print(full_scripts_dir)
            cmds.extend( self._ip_dir_cmds(full_scripts_dir) )

        elab_cmd = self._elab_command()
        cmds.append(elab_cmd)

        return cmds

    def _test_command(self) -> Sequence[Command]:
        # bridge to cross: everything needs to become internalized to a module
        self._issue_test_warnings()

        cmd = [
            ["python3", "-m", self.LAUNCHING_MODULE]
        ]

        # set environment for launching vicoco
        xilinx_root = self.xilinx_root
        self.env["LD_LIBRARY_PATH"] = (
            f"{xilinx_root}/lib/lnx64.o:{xilinx_root}/lib/lnx64.o/Default:"
            )
        self.env["VIVADO_SNAPSHOT_NAME"] = "pybound_sim"
        self.env["TOPLEVEL_LANG"] = self.hdl_toplevel_lang
        self.env["XSIM_INTERFACE"] = self.launch_mode

        # conversion from vcd to fst, if necessary
        if self.waves and self.fst_output:
            cmd.append(["vcd2fst", self.waveform_filename, self.waveform_filename])

        return cmd

    def _get_parameter_options(self, parameters: Mapping[str, object]) -> Command:
        param_options = []
        for param,val in parameters.items():
            param_options.extend(["-generic_top",f"{param}={val!s}"])
        return param_options


def get_runner(simulator_name: str, **kwargs) -> Simulator:
    """
    Wrapper for the native get_runner function, which initializes the
    Vivado runner if the 'vivado' simulator name is specified. Otherwise,
    calls the original cocotb ``get_runner`` function.
    """

    if simulator_name == "vivado":
        return Vivado(**kwargs)
    if simulator_name == "vivado_tcl":
        return Vivado(mode='TCL',**kwargs)
    return runner.get_runner(simulator_name)
