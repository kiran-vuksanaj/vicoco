`timescale 1 ns / 1 ps

module bram_wrap(
  input wire clka,
  input wire [9:0] addra,
  input wire [7:0] dina,
  output logic [7:0] douta,
  input wire ena,
  input wire wea,
  input wire clkb,
  input wire [9:0] addrb,
  input wire [7:0] dinb,
  output logic [7:0] doutb,
  input wire enb,
  input wire web
);

  blk_mem_kilobyte dut(
    // Outputs
    .douta               (douta[7:0]),
    .doutb               (doutb[7:0]),
    // Inputs
    .clka                (clka),
    .addra               (addra[9:0]),
    .dina                (dina[7:0]),
    .ena                 (ena),
    .wea                 (wea),
    .clkb                (clkb),
    .addrb               (addrb[9:0]),
    .dinb                (dinb[7:0]),
    .enb                 (enb),
    .web                 (web));

endmodule
