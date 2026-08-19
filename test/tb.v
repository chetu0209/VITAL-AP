`default_nettype none
`timescale 1ns / 1ps

module tb;

    // ------------------------------------------------------------
    // Clock and reset
    // ------------------------------------------------------------

    reg clk;
    reg rst_n;
    reg ena;

    // ------------------------------------------------------------
    // Tiny Tapeout inputs
    // ------------------------------------------------------------

    reg [7:0] ui_in;
    reg [7:0] uio_in;

    // ------------------------------------------------------------
    // Tiny Tapeout outputs
    // ------------------------------------------------------------

    wire [7:0] uo_out;
    wire [7:0] uio_out;
    wire [7:0] uio_oe;

    // ------------------------------------------------------------
    // DUT
    // ------------------------------------------------------------

    tt_um_vital_ap user_project (
        .ui_in   (ui_in),
        .uo_out  (uo_out),
        .uio_in  (uio_in),
        .uio_out (uio_out),
        .uio_oe  (uio_oe),
        .ena     (ena),
        .clk     (clk),
        .rst_n   (rst_n)
    );

    // ------------------------------------------------------------
    // Waveform dump
    // ------------------------------------------------------------

    initial begin
        $dumpfile("tb.fst");
        $dumpvars(0, tb);
    end

endmodule

`default_nettype wire
