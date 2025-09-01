

export LD_LIBRARY_PATH=$(XILINX_VIVADO)/lib/lnx64.o:$(XILINX_VIVADO)/lib/lnx64.o/Default:

SOURCES +=counter.sv
SOURCES +=counter_tb.sv

TOPLEVEL=counter
export SNAPSHOT_NAME=pybound_sim

export MODULE = simple_cocotbtest

.PHONY: compile compile_sv clean clean_log

compile_sv: $(SOURCES)
	xvlog -sv $^

compile: compile_sv
	xelab -top $(TOPLEVEL) -snapshot $(SNAPSHOT_NAME) -debug wave -dll

run: compile
	python3 -m cocotb_xsim

clean_log:
	rm -f *.log
	rm -f *.jou
	rm -f *.pb

clean: clean_log
	rm -rf xsim.dir
	rm -f *~
	rm -f \#*
	rm -f *.so
	rm -f *.wdb
	rm -f results.xml
	rm -rf __pycache__
