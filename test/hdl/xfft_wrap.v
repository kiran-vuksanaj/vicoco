`timescale 1ns / 1ps

module xfft_wrap(
  input wire           aclk,
  input wire [15:0]    s_axis_config_tdata,
  input wire           s_axis_config_tvalid,
  output wire          s_axis_config_tready,
  input wire [31 : 0]  s_axis_data_tdata,
  input wire           s_axis_data_tvalid,
  output wire [31 : 0] m_axis_data_tdata,
  output wire          m_axis_data_tvalid,
  input wire           m_axis_data_tready,
  output wire          m_axis_data_tlast,
  output wire          event_frame_started,
  output wire          event_tlast_unexpected,
  output wire          event_tlast_missing,
  output wire          event_status_channel_halt,
  output wire          event_data_in_channel_halt,
  output wire          event_data_out_channel_halt);

  xfft_0 your_instance_name (
    .aclk(aclk),                                                // input wire aclk
    .s_axis_config_tdata(s_axis_config_tdata),                  // input wire [15 : 0] s_axis_config_tdata
    .s_axis_config_tvalid(s_axis_config_tvalid),                // input wire s_axis_config_tvalid
    .s_axis_config_tready(s_axis_config_tready),                // output wire s_axis_config_tready
    .s_axis_data_tdata(s_axis_data_tdata),                      // input wire [31 : 0] s_axis_data_tdata
    .s_axis_data_tvalid(s_axis_data_tvalid),                    // input wire s_axis_data_tvalid
    .s_axis_data_tready(s_axis_data_tready),                    // output wire s_axis_data_tready
    .s_axis_data_tlast(s_axis_data_tlast),                      // input wire s_axis_data_tlast
    .m_axis_data_tdata(m_axis_data_tdata),                      // output wire [31 : 0] m_axis_data_tdata
    .m_axis_data_tvalid(m_axis_data_tvalid),                    // output wire m_axis_data_tvalid
    .m_axis_data_tready(m_axis_data_tready),                    // input wire m_axis_data_tready
    .m_axis_data_tlast(m_axis_data_tlast),                      // output wire m_axis_data_tlast
    .event_frame_started(event_frame_started),                  // output wire event_frame_started
    .event_tlast_unexpected(event_tlast_unexpected),            // output wire event_tlast_unexpected
    .event_tlast_missing(event_tlast_missing),                  // output wire event_tlast_missing
    .event_status_channel_halt(event_status_channel_halt),      // output wire event_status_channel_halt
    .event_data_in_channel_halt(event_data_in_channel_halt),    // output wire event_data_in_channel_halt
    .event_data_out_channel_halt(event_data_out_channel_halt)  // output wire event_data_out_channel_halt
  );

endmodule
