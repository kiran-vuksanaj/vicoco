`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 01/13/2025 03:24:11 PM
// Design Name: 
// Module Name: counter_tb
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


module counter_tb;

    logic clk,rst;
    logic [31:0] count;
    logic incr;
    
    counter dut(
        .clk(clk),
        .rst(rst),
        .count_out(count),
        .incr_in(incr)
        );
        
    always begin
        #5;
        clk = ~clk;
    end
    
    initial begin
        clk = 0;
        rst = 0;
        incr = 0;
        
        #6;
        rst = 1;
        #20;
        rst = 0;
        #10;
        incr = 1;
        #60;
        incr = 0;
        #70;
        
        $finish;
    end

endmodule
