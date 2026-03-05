
Vicoco Limitations
==================

Vicoco is built around the `XSI C Interface`_ for accessing the ``xsim`` simulator while operating.
This is unfortunately a very limited interface; the only interactions that are possible with the
simulator during the course of simulation are:

* Getting the value of a top-level signal
* Setting the value of a top-level signal
* Advancing the simulation by ``n`` timesteps.

In the absence of the complete API interface that other simulators implement through the VPI/VHPI
interfaces, Vicoco instead implements a substantial portion of cocotb's necessary behavior in
Python, in the ``XSimManager``. To see more details on how this system works, see
:doc:`runtime_environment`. However, the most important components to understand are the inherent
limitations that come with this approach to using the Vivado simulator with cocotb.
  
.. _XSI C Interface: https://docs.amd.com/r/en-US/ug900-vivado-logic-simulation/Using-Xilinx-Simulator-Interface

HDL-Based Delay Operations
--------------------------

The most vital limitation of Vicoco is the fact that it **will not know** about any simulation time
reached due to a delay in simulation HDL. So, if any Verilog code uses a line akin to

.. code-block:: verilog

                #(DELAY_NS);
                signal = 1'b1;


a cocotb simulation will not know to poll any potential value changes at this timestep. The
simulation will still advance as normal, but if a cocotb thread is awaiting a
``RisingEdge(dut.signal)``, this thread will not be aware of the change to ``signal`` until
the next timestep reached by a ``Timer`` trigger.

Due to this constraint, it's **vital** that any clocks in a DUT using vicoco come *from Python*,
likely using a cocotb ``Clock`` object or similar. Clocks should not be generated from simulation
Verilog or VHDL. If an HDL design uses no delay directives, then every value-change event can be
noticed by the cocotb testbench.

If for some reason an HDL source is being used that must include delay directives, but the times
when these delay directives are known, a Vicoco testbench can ensure access to all relevant
timesteps by registering ``Timer`` triggers that fire at the same time as the known delay
directives. Nothing needs to happen after the ``Timer`` trigger, it simply needs to fire so that
Vicoco has the opportunity to poll pending value-change triggers. So, to appropriately detect the
above example of an HDL delay directive, the following Python coroutine could be scheduled to ``start_soon()`` at the same time as the HDL code's execution.

.. code-block:: python
                
                async def match_delay():
                    await Timer(DELAY_NS,unit='ns')
                    return
       
Bear in mind that it may be the case that if using encrypted Vivado IP, there are hidden HDL delay
directives that aren't possible to account for with this approach.

Internal Signals
----------------

In most cocotb testbenches, it's possible to access signals other than the top-level module's
input and output ports; both signals declared inside the body of a module and the signals of
submodules declared within the top-level module. However, the XSI interface only allows the
setting and reading of top-level ports, so Vicoco has no way of accessing these sub-ports.
However, any port can be accessed with the addition of an appropriate Verilog wrapper to the
top-level module that breaks out desired ports as inputs or outputs to the wrapper.

In future releases of Vicoco, a pre-build stage may be introduced to optionally break out
necessary signals into a wrapper to allow cocotb to see all internal signals as expected. The
beginnings of this concept can be seen in `this github issue <https://github.com/kiran-vuksanaj/vicoco/issues/2>`_.

.. _
