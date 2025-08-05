## Cocotb + Vivado XSim

Following closely in the footsteps of themperek's [cocotb-vivado](github.com/themperek/cocotb-vivado)


### Getting things running
* make sure you have Python installed in such a way that libpython / the `<Python.h>` file exists; from `apt`, this might look like installing `python3-dev`. If you have cocotb running, this should already be handled.
* make sure you have Vivado (default in these tests is 2025.1, but tests also work in 2024.2) installed, and its paths etc. added to your terminal: your `.bashrc` might need a line like
``` sh
source /tools/Xilinx/2025.1/Vivado/settings64.sh
```
(if using another version of Vivado or a different install location, locate Vivado's `settings64.sh` file)

* make a virtual environment with cocotb in it (only need to do once)

``` sh
python3 -m venv venv
source venv/bin/activate
pip3 install -e .
```
* if running this repository's tests, also install the requirements from `tb_environment.txt`

``` sh
pip3 install -r tb_environment.txt
```

* with the virtual environment activated, run the tests:

``` sh
pytest -s
```

if using Vivado 2024.2, add a `VIVADO_VERSION` environment variable to that launch command.:

``` sh
VIVADO_VERSION=2024.2 pytest -s
```



In brief, the following commands should get you up and running the first time:

``` sh
source /tools/Xilinx/2025.1/Vivado/settings64.sh
python3 -m venv venv
source venv/bin/activate
pip3 install -e .
pip3 install -r tb_environment.txt
pytest -s
```

### submodules here
TODO diagram + descriptions of operations (compare between normal cocotb and this)


### Upcoming things to work on
- ~~organize into directories properly~~, make more tests
- ~~python test runner object~~
- Make rising/falling edge triggers in the manager
- restore proper management of undefined variables
- Build second backend for launching a TCL shell for the simulator and interacting with Vivado through that
- Export to vcd files
- simplified way to go from Vivado IP to cocotb simulation
