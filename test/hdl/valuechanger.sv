`timescale 1ns / 1ps

module valuechanger(
  input wire         clk,
  input wire         rst,
  input wire         incr_in,
  input wire         secondary_in,
  output logic       slow_out,
  output logic       incr_out_delay,
  output logic       secondary_delay,
  output logic [3:0] smallcount_out
);

  assign slow_out = smallcount_out[3];
  
  always_ff @(posedge clk) begin

    if (rst) begin
      smallcount_out <= 4'b0;
      incr_out_delay <= 1'b0;
      secondary_delay <= 1'b0;
    end else begin
      if (incr_in) begin
        smallcount_out <= smallcount_out + 1;
      end
      incr_out_delay <= incr_in;
      secondary_delay <= secondary_in;
    end
    
  end

endmodule
