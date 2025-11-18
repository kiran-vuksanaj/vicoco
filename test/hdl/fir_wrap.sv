`timescale 1ns/1ps
`default_nettype none


module fir_wrap(
    input wire clk,
    input wire rst,
    input wire s_axis_data_tvalid,
    output logic s_axis_data_tready,
    input wire [15:0] s_axis_data_tdata,
    output logic [23:0] m_axis_data_tdata
);



    fir_compiler_0 fc0m(
        .aclk(clk),
        .s_axis_data_tvalid(s_axis_data_tvalid),
        .s_axis_data_tready(s_axis_data_tready),
        .s_axis_data_tdata(s_axis_data_tdata),
        .m_axis_data_tdata(m_axis_data_tdata)
    );

endmodule

