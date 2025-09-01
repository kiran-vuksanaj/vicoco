`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company:
// Engineer:
//
// Create Date: 01/13/2025 03:17:49 PM
// Design Name:
// Module Name: counter
// Project Name:
// Target Devices:
// Tool Versions:
// Description:
//
// Dependencies:
//
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
//
//////////////////////////////////////////////////////////////////////////////////


module counter(
  input wire          clk,
  input wire          rst,
  output logic [47:0] count_out,
  input wire          incr_in,
  output logic [15:0] cordic_out,
  output logic        cordic_valid
);

  logic [15:0] count;

  logic        rstN;
  assign rstN = !rst;
  logic extracomb;
  always_comb begin
    extracomb = (clk & rstN);
  end
  // assign count_out = count << 32;
  assign count_out = count;
  always_ff @(posedge clk) begin
    if (rst) begin
      count <= 16'h0;
    end else begin
      if (incr_in) begin
        count <= count + 1;
      end
    end
  end


  subm subm_inst (
                  // Outputs
                  .yes_out              (cordic_valid),
                  // Inputs
                  .clk                  (clk),
                  .rst                  (rst),
                  .yes_in               (incr_in));

endmodule


module subm(
  input wire clk,
  input wire rst,
  input wire yes_in,
  output logic yes_out
);

  logic [12:0] stuff;
  always_ff @(posedge clk) begin
    if (rst) begin
      stuff <= 0;
    end else begin
      if (yes_in) begin
        stuff <= (stuff << 1) + (stuff >> 1) + 1;
      end
    end
  end

  assign yes_out = stuff[4];

endmodule
