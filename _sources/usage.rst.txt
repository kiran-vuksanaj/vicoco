
Getting Started
===============
If you're already working with cocotb testbenches, the transition to using
vicoco/the Vivado simulator should be simple.

Installation
------------
In the appropriate environment, vicoco can be installed with:

``pip3 install git+https://github.com/kiran-vuksanaj/vicoco.git@stable``

**If you are using cocotb 1.x**: be sure to install vicoco version 0.0.3, with:

``pip3 install git+https://github.com/kiran-vuksanaj/vicoco.git@v0.0.3``

Using vicoco in a testbench
---------------------------

Vicoco is launched using the `cocotb Python runner`_, so if you


.. _`cocotb Python runner`:
   https://docs.cocotb.org/en/stable/library_reference.html#python-test-runner

.. toctree::
   :maxdepth: 2
   :name: howto-section
   :caption: Vicoco Usage

   self
   vivado_ip_usage
   limitations

