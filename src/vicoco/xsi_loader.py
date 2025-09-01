import os
import ctypes
# import cocotb
# heavily inspired by themperek/cocotb-vivado; thank you!!

# char conversion for values 0-8 as specified by UG900 IEEE std_logic type
VHDL_std_logic = ['U','X','0','1','Z','W','L','H','_']
VHDL_binstr_to_std_logic = {
    'U':0,
    'X':1,
    '0':2,
    '1':3,
    'Z':4,
    'W':5,
    'L':6,
    'H':7,
    '_':8
}

class Xsi_Loader:
    """
    Class for
    
    """
    xsiNumTopPorts = 1
    xsiTimePrecisionKernel = 2
    xsiDirectionTopPort = 3
    xsiHDLValueSize = 4
    xsiNameTopPort = 5


    def __init__(self):
        self.load_libraries()

        self.toplevel_lang = os.getenv('TOPLEVEL_LANG')
        if self.toplevel_lang is None:
            self.toplevel_lang = 'verilog'

        self.handle = ctypes.c_void_p(None)
    
    def load_libraries(self):

        snapshot_name = os.getenv("VIVADO_SNAPSHOT_NAME")

        design_so_file = "xsim.dir/{snapshot_name}/xsimk.so".format(snapshot_name=snapshot_name)

        kernel_so_file = "libxv_simulator_kernel.so"
        self.kernel_lib = ctypes.CDLL(kernel_so_file)
        self.design_lib = ctypes.CDLL(design_so_file)

        Xsi_H.define_lib( self.design_lib, Xsi_H.design_lib_defines )
        Xsi_H.define_lib( self.kernel_lib, Xsi_H.kernel_lib_defines )


    def open_handle(self,logFileName,wdbFileName,trace=True):

        # setup_info = Xsi_H.s_xsi_setup_info(logFileName,wdbFileName)
        setup_info = Xsi_H.s_xsi_setup_info(None,None)

        self.handle = self.design_lib.xsi_open( ctypes.pointer(setup_info) )

        # i dont really understand why this needs to be re-wrapped, and it concerns me
        self.handle = Xsi_H.xsiHandle( self.handle )
        
        if trace:
            self.kernel_lib.xsi_trace_all( self.handle )


    def close(self):
        self.kernel_lib.xsi_close( self.handle )

    def run(self,steps):
        step_count = ctypes.c_int64(steps)
        self.kernel_lib.xsi_run( self.handle, step_count )



    def xsi_compliant_space_type(self,port_size):
        assert port_size>0,f"illegal port size {port_size}"
        if self.toplevel_lang == "verilog":
            num_spaces = ((port_size-1) // 32)+1
            array_type = Xsi_H.s_xsi_vlog_logicval * num_spaces
            return array_type
        elif self.toplevel_lang == "vhdl":
            array_type = ctypes.c_char * port_size
            return array_type
        else:
            raise KeyError(f"Unknown toplevel language {self.toplevel_lang} (not verilog or vhdl)")
        
    def xsi2binstr(self,val_array,port_size):

        ### val_ptr should be an array type
        output = ""
        if (self.toplevel_lang == 'verilog'):
            for val in val_array:

                binary_bits = list("{:032b}".format(val.aVal))

                bVal = val.bVal
                for i in range(32):
                    if ((bVal >> i) & 1):
                        if binary_bits[31-i] == '0':
                            binary_bits[31-i] = 'Z'
                        else:
                            binary_bits[31-i] = 'X'
                
                # prepend new section

                output = ''.join(binary_bits) + output
        else:
            for val in val_array:
                # each val should be a ctypes.c_char
                byte_val = ord(val)
                binstr_char = VHDL_std_logic[byte_val]
                output = output + binstr_char
            

        # trim excess zeroes from the front
        output = output[-port_size:]
        return output

    def binstr2xsi(self,binstr,port_size):
        assert(len(binstr)==port_size)
        binstr = binstr.upper()
        memory_space = self.xsi_compliant_space_type(port_size)()
        
        if (self.toplevel_lang == 'verilog'):

            for i in range(0,port_size,32):
                i = i // 32 # actual cycle number
                binstr_substring = binstr[-32:]
                binstr = binstr[:-32]
                aVal_str = binstr_substring
                aVal_str = aVal_str.replace('X','1')
                aVal_str = aVal_str.replace('Z','0')

                bVal_str = binstr_substring
                bVal_str = bVal_str.replace('1','0')
                bVal_str = bVal_str.replace('X','1')
                bVal_str = bVal_str.replace('Z','1')

                aVal = int(aVal_str,2)
                bVal = int(bVal_str,2)
                memory_space[i] = Xsi_H.s_xsi_vlog_logicval(aVal,bVal)

            return memory_space
        else:
            for i in range(port_size):
                # binstr_char = binstr[port_size-1-i]
                binstr_char = binstr[i]
                binstr_byteval = VHDL_binstr_to_std_logic[binstr_char]
                memory_space[i] = binstr_byteval
            return memory_space
                


    def get_value(self,port_number,port_size):

        # print("XSI GET VALUE")
        value_space_type = self.xsi_compliant_space_type(port_size)
        value_space = value_space_type()
        value_pointer = ctypes.pointer(value_space)

        port_number = ctypes.c_int(port_number)

        self.kernel_lib.xsi_get_value( self.handle, port_number, value_pointer )

        return self.xsi2binstr(value_pointer.contents,port_size)

    def put_value(self,port_number,port_size,value):
        # print("XSI PUT VALUE",self.get_time())
        value_space = self.binstr2xsi(value,port_size)
        value_pointer = ctypes.pointer(value_space)

        port_number = ctypes.c_int(port_number)
        self.kernel_lib.xsi_put_value( self.handle, port_number, value_pointer )

    def get_port_name(self,port_number):
        """ this doesn't exist in the documentation??? does that mean itll disappear?"""
        port_number = ctypes.c_int(port_number)
        name_bytes_p = self.kernel_lib.xsi_get_port_name( self.handle, port_number )

        if name_bytes_p is not None:
            return name_bytes_p.decode('utf-8')
        else:
            return None

    def get_port_number(self,port_name):
        port_name = bytes(port_name,'utf-8')
        return self.kernel_lib.xsi_get_port_number( self.handle, port_name )

    def get_status(self):
        val = self.kernel_lib.get_status( self.handle )
        return val

    def get_time(self):
        time = self.kernel_lib.xsi_get_time( self.handle )
        return time

    def get_port_size(self,port_number):
        port_size = self.kernel_lib.xsi_get_int_port( self.handle, port_number, Xsi_Loader.xsiHDLValueSize )
        return port_size


    
    # trace_all
    # get_error_info
    # isopen
    # restart


class Xsi_H:
    """
    ctypes structs and types to match the "xsi.h" file, and allow interactions with the key functions
    see file $XILINX_VIVADO/data/xsim/include/xsi.h to reference
    """

    class t_xsi_setup_info(ctypes.Structure):
        _fields_ = [("logFileName",ctypes.c_char_p),
                    ("wdbFileName",ctypes.c_char_p),
                    ("xsimDir",ctypes.c_char_p)
                    ]
    class s_xsi_setup_info(t_xsi_setup_info):
        def __init__(self,logFileName,wdbFileName,xsimDir=""):
            if logFileName is not None:
                logFileName = bytes(logFileName,'utf-8')
            if wdbFileName is not None:
                wdbFileName = bytes(wdbFileName,'utf-8')
            if xsimDir is not None:
                xsimDir = bytes(xsimDir,'utf-8')

            super().__init__(logFileName,wdbFileName,xsimDir)
            
    p_xsi_setup_info = ctypes.POINTER(t_xsi_setup_info)

    class s_xsi_vlog_logicval(ctypes.Structure):
        _fields_ = [("aVal",ctypes.c_uint32),
                    ("bVal",ctypes.c_uint32)]

    p_xsi_vlog_logicval = ctypes.POINTER(s_xsi_vlog_logicval)
    xsiHandle = ctypes.c_void_p

    design_lib_defines = {
        'xsi_open': (
            (p_xsi_setup_info,),
            xsiHandle
        )
    }

    kernel_lib_defines = {
        'xsi_run': (
            (xsiHandle, ctypes.c_int64),
            None
            ),
        'xsi_close': (
            (xsiHandle,),
            None
            ),
        'xsi_trace_all': (
            (xsiHandle,),
            None
            ),
        'xsi_get_port_number': (
            (xsiHandle, ctypes.c_char_p),
            ctypes.c_int
            ),
        'xsi_get_port_name': (
            (xsiHandle, ctypes.c_int),
            (ctypes.c_char_p)
        ),
        'xsi_put_value': (
            (xsiHandle, ctypes.c_int, ctypes.c_void_p),
            None
            ),
        'xsi_get_value': (
            (xsiHandle, ctypes.c_int, ctypes.c_void_p),
            None
            ),
        'xsi_get_status': (
            (xsiHandle,),
            ctypes.c_int
            ),
        'xsi_get_time': (
            (xsiHandle,),
            ctypes.c_int
        ),
        'xsi_get_int_port': ( # god i literally don't see docs for this anywhere??
            (xsiHandle,ctypes.c_int,ctypes.c_int),
            ctypes.c_int
        )

    }

    def define_lib(lib,lib_defines):
        """ load argtype and restype into library after it's been opened, according to a dictionary of types"""
        for key in lib_defines:
            lib_fn = getattr(lib,key)
            fn_header = lib_defines[key]
            lib_fn.argtypes = fn_header[0]
            lib_fn.restype = fn_header[1]
        

