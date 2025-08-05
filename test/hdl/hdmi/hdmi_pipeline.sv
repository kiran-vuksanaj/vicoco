`timescale 1 ns / 1 ps

module hdmi_pipeline(
  input wire         clk_100mhz,
  input wire         clk_pixel,
  input wire         clk_5x,
  input wire         sys_rst,
  output logic [2:0] hdmi_tx_p,
  output logic [2:0] hdmi_tx_n,
  output logic       hdmi_clk_p,
  output logic       hdmi_clk_n
);

  logic [1:0] sw;
  assign sw = 2'b00;

  // logic locked;
  // logic clk_pixel, clk_5x;

   // //clock manager...creates 74.25 Hz and 5 times 74.25 MHz for pixel and TMDS
   // hdmi_clk_wiz_720p mhdmicw (
	 //  	      .reset(0),
	 //  	      .locked(locked),
	 //  	      .clk_ref(clk_100mhz),
	 //  	      .clk_pixel(clk_pixel),
	 //  	      .clk_tmds(clk_5x));


  logic [10:0] 		     hcount; //hcount of system!
  logic [9:0]          vcount; //vcount of system!
  logic                hor_sync; //horizontal sync signal
  logic                vert_sync; //vertical sync signal
  logic                active_draw; //ative draw! 1 when in drawing region.0 in blanking/sync
  logic                new_frame; //one cycle active indicator of new frame of info!
  logic [5:0]          frame_count; //0 to 59 then rollover frame counter

   //written by you! (make sure you include in your hdl)
   //default instantiation so making signals for 720p
  video_sig_gen mvg(
		.clk_pixel_in(clk_pixel),
		.rst_in(sys_rst),
		.hcount_out(hcount),
		.vcount_out(vcount),
		.vs_out(vert_sync),
		.hs_out(hor_sync),
		.ad_out(active_draw),
		.nf_out(new_frame),
		.fc_out(frame_count));


  logic [7:0] tp_r,tp_g,tp_b;
  logic [7:0] red,green,blue;
  
  test_pattern_generator mtpg(
		.sel_in(sw[1:0]),
		.hcount_in(hcount),
		.vcount_in(vcount),
		.red_out(tp_r),
		.green_out(tp_g),
		.blue_out(tp_b));

  assign red = tp_r;
  assign green = tp_g;
  assign blue = tp_b;

  logic [9:0] tmds_10b [0:2]; //output of each TMDS encoder!
  logic       tmds_signal [2:0]; //output of each TMDS serializer!

  tmds_encoder tmds_red(
		.clk_in(clk_pixel),
		.rst_in(sys_rst),
		.data_in(red),
		.control_in(2'b0),
		.ve_in(active_draw),
		.tmds_out(tmds_10b[2]));

  tmds_encoder tmds_green(
		.clk_in(clk_pixel),
		.rst_in(sys_rst),
		.data_in(green),
		.control_in(2'b0),
		.ve_in(active_draw),
		.tmds_out(tmds_10b[1]));

  tmds_encoder tmds_blue(
		.clk_in(clk_pixel),
		.rst_in(sys_rst),
		.data_in(blue),
		.control_in({vert_sync,hor_sync}),
		.ve_in(active_draw),
		.tmds_out(tmds_10b[0]));

  //three tmds_serializers (blue, green, red):
  //MISSING: two more serializers for the green and blue tmds signals.
  tmds_serializer red_ser(
		.clk_pixel_in(clk_pixel),
		.clk_5x_in(clk_5x),
		.rst_in(sys_rst),
		.tmds_in(tmds_10b[2]),
		.tmds_out(tmds_signal[2]));
  tmds_serializer green_ser(
		.clk_pixel_in(clk_pixel),
		.clk_5x_in(clk_5x),
		.rst_in(sys_rst),
		.tmds_in(tmds_10b[1]),
		.tmds_out(tmds_signal[1]));
  tmds_serializer blue_ser(
		.clk_pixel_in(clk_pixel),
		.clk_5x_in(clk_5x),
		.rst_in(sys_rst),
		.tmds_in(tmds_10b[0]),
		.tmds_out(tmds_signal[0]));

  //output buffers generating differential signals:
  //three for the r,g,b signals and one that is at the pixel clock rate
  //the HDMI receivers use recover logic coupled with the control signals asserted
  //during blanking and sync periods to synchronize their faster bit clocks off
  //of the slower pixel clock (so they can recover a clock of about 742.5 MHz from
  //the slower 74.25 MHz clock)
  OBUFDS OBUFDS_blue (.I(tmds_signal[0]), .O(hdmi_tx_p[0]), .OB(hdmi_tx_n[0]));
  OBUFDS OBUFDS_green(.I(tmds_signal[1]), .O(hdmi_tx_p[1]), .OB(hdmi_tx_n[1]));
  OBUFDS OBUFDS_red  (.I(tmds_signal[2]), .O(hdmi_tx_p[2]), .OB(hdmi_tx_n[2]));
  OBUFDS OBUFDS_clock(.I(clk_pixel), .O(hdmi_clk_p), .OB(hdmi_clk_n));


endmodule


module test_pattern_generator(
			      input wire [1:0] sel_in,
			      input wire [10:0] hcount_in,
			      input wire [9:0] vcount_in,
			      output logic [7:0] red_out,
			      output logic [7:0] green_out,
			      output logic [7:0] blue_out
			      );
   always_comb begin
      case(sel_in)
	2'b00: begin
	   red_out = 8'h9b;
	   green_out = 8'h3b;
	   blue_out = 8'h91;
	end
	2'b01: begin
	   red_out = (vcount_in == 360 || hcount_in==640) ? 8'hFF : 8'h00;
	   green_out = (vcount_in == 360 || hcount_in==640) ? 8'hFF : 8'h00;
	   blue_out = (vcount_in == 360 || hcount_in==640) ? 8'hFF : 8'h00;
	end
	2'b10: begin
	   red_out = hcount_in;
	   green_out = hcount_in;
	   blue_out = hcount_in;
	end
	2'b11: begin
	   red_out = hcount_in;
	   green_out = vcount_in;
	   blue_out = hcount_in+vcount_in;
	end
      endcase // case (sel_in)
   end

  // stuff
endmodule // test_pattern_generator
