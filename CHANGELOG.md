v0.0.3 - 2025-11-21

Improvements/stabilizations for the vivado\_runner class. Stable version for 6.205 lab-bc machines.

* access to global modules, extra libraries etc at get\_runner() instantiation
* WIP validate\_flags operator to remove invalid flags (e.g. -Wall) from `build\_args` parameter, avoid crashes during xvlog/xelab process 

v0.0.2dev- 2025-11-20

Various updates to the vivado\_runner system to more properly match native Vivado simulations + make more stuff compile successfully. 

* Added --relax, --incr flags for xvlog and xvhdl compilation
* Proper part number handling, runner.part\_num can be set to non-default values
* Proper handling of mem\_init\_files for compiled IP; now the FIR Compiler IP works
* Parameter passing in the Python runner
* More warnings surrounding the waves=True state (it behaves weird if you pass parameters or if your top level is VHDL)


v0.0.1

Initial release as provided to 6.205/6.S965.
