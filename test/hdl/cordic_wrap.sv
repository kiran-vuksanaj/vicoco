`timescale 1ns / 1ps

module cordic_wrap(
  input wire aclk,
  input wire s_axis_cartesian_tvalid,
  input wire [15:0] s_axis_cartesian_tdata,
  output logic m_axis_dout_tvalid,
  output logic [15:0] m_axis_dout_tdata
);

  cordic_0 cordic_utm(
    .aclk(aclk),
    .s_axis_cartesian_tvalid(s_axis_cartesian_tvalid),
    .s_axis_cartesian_tdata(s_axis_cartesian_tdata),
    .m_axis_dout_tvalid(m_axis_dout_tvalid),
    .m_axis_dout_tdata(m_axis_dout_tdata));


endmodule
