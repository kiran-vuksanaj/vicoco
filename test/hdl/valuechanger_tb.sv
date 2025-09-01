`timescale 1ns / 1ps

module valuechanger_tb;
  logic clk;

  valuechanger dut(
    .clk                 (clk)
  );

  always begin
    #5;
    clk = ~clk;
  end

  initial begin
    clk = 0;
  end


endmodule
