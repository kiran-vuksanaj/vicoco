`timescale 1ns/1ps

module building_blocks(
  input wire clk,
  input wire rst,
  input wire data_in,
  input wire clk_en,
  output logic data_out
);

  FDRE dff(
    .C(clk),
    .CE(clk_en),
    .R(rst),
    .D(data_in),
    .Q(data_out)
  );


endmodule
