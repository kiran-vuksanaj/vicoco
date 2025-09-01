`timescale 1 ns / 1 ps

module fifo_wrap(
  input wire s_axis_aclk,
  input wire s_axis_aresetn,
  input wire s_axis_tvalid,
  output logic s_axis_tready,
  input wire [15:0] s_axis_tdata,
  input wire s_axis_tlast,
  output logic m_axis_tvalid,
  input wire m_axis_tready,
  output logic [15:0] m_axis_tdata,
  output logic m_axis_tlast
);

  fifo_dut_sync dut(
    // Outputs
    .s_axis_tready      (s_axis_tready),
    .m_axis_tvalid      (m_axis_tvalid),
    .m_axis_tdata       (m_axis_tdata[15:0]),
    .m_axis_tlast       (m_axis_tlast),
    // Inputs
    .s_axis_aresetn     (s_axis_aresetn),
    .s_axis_aclk        (s_axis_aclk),
    .s_axis_tvalid      (s_axis_tvalid),
    .s_axis_tdata       (s_axis_tdata[15:0]),
    .s_axis_tlast       (s_axis_tlast),
    .m_axis_tready      (m_axis_tready));

endmodule
