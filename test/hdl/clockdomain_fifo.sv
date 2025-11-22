`timescale 1ns / 1ps
`default_nettype none

/*
 * ddr_fifo
 * 
 * wrapper for the Xilinx Parametrized Macro, xpm_fifo_axis
 * with parameters set as we want them for transferring data into/out of the DDR controller clock domain
 */

module clockdomain_fifo
  #(parameter DEPTH=128, 
    parameter PROGFULL_DEPTH=12)
  (
   input wire 		sender_rst,
   input wire 		sender_clk,
   input wire 		sender_axis_tvalid,
   output logic 	sender_axis_tready,
   input wire [127:0] 	sender_axis_tdata,
   input wire 		sender_axis_tlast,
   output logic 	sender_axis_prog_full,

   input wire 		receiver_clk,
   output logic 	receiver_axis_tvalid,
   input wire 		receiver_axis_tready,
   output logic [127:0] receiver_axis_tdata,
   output logic 	receiver_axis_tlast,
   output logic 	receiver_axis_prog_empty
   );

  
   xpm_fifo_axis #(
      .CASCADE_HEIGHT(0),             // DECIMAL
      .CDC_SYNC_STAGES(3),            // DECIMAL
      .CLOCKING_MODE("independent_clock"), // String
      .ECC_MODE("no_ecc"),            // String
      .FIFO_DEPTH(DEPTH),              // DECIMAL
      .FIFO_MEMORY_TYPE("auto"),      // String
      .PACKET_FIFO("false"),          // String
      .PROG_EMPTY_THRESH(10),         // DECIMAL
      .PROG_FULL_THRESH(DEPTH-PROGFULL_DEPTH),          // DECIMAL
      .RELATED_CLOCKS(0),             // DECIMAL
      .SIM_ASSERT_CHK(0),             // DECIMAL; 0=disable simulation messages, 1=enable simulation messages
      .TDATA_WIDTH(128),               // DECIMAL
      .USE_ADV_FEATURES("0202")      // String
   )
   xpm_fifo_axis_inst (
  // ddr_fifo (
     .m_aclk(receiver_clk),
     // .m_axis_aclk(receiver_clk),
     .m_axis_tdata(receiver_axis_tdata),
     .m_axis_tdest(),
     .m_axis_tid(),
     .m_axis_tkeep(),
     .m_axis_tlast(receiver_axis_tlast),
     .m_axis_tready(receiver_axis_tready),
     .m_axis_tstrb(),
     .m_axis_tuser(),
     .m_axis_tvalid(receiver_axis_tvalid),
     .prog_empty_axis(receiver_axis_prog_empty),
     .prog_full_axis(sender_axis_prog_full),
     // .prog_empty(receiver_axis_prog_empty),
     // .prog_full(sender_axis_prog_full),
     .s_aclk(sender_clk),
     // .s_axis_aclk(sender_clk),
     .s_aresetn(~sender_rst),
     // .s_axis_aresetn(~sender_rst),
     .s_axis_tdata(sender_axis_tdata),
     .s_axis_tdest(0),
     .s_axis_tid(0),
     .s_axis_tkeep(0),
     .s_axis_tlast(sender_axis_tlast),
     .s_axis_tready(sender_axis_tready),
     .s_axis_tstrb(0),
     .s_axis_tuser(0),
     .s_axis_tvalid(sender_axis_tvalid));

   // End of xpm_fifo_axis_inst instantiation

endmodule

   


`default_nettype wire
