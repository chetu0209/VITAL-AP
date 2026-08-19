`default_nettype none
`timescale 1ns / 1ps

// ============================================================
// VITAL-AP
//
// Value-, Transition-, and Temporal-Aware Adaptive Register
// for Low-Power Image and Video Processing
//
// ============================================================
//
// Pin mapping:
//
// ui_in[7:0]
//     8-bit pixel input
//
// uo_out[7:0]
//     8-bit adaptive pixel output
//
// uio_in[0]
//     ENABLE
//
// uio_in[2:1]
//     SENSITIVITY
//
// uio_in[7]
//     RESET_N (active-low)
//
// uio_out[0]
//     UPDATE
//
// uio_out[1]
//     HOLD
//
// uio_out[3:2]
//     ACTIVITY LEVEL
//
// uio[4:6]
//     unused
//
// ============================================================

module tt_um_vital_ap (

    input  wire [7:0] ui_in,

    output wire [7:0] uo_out,

    input  wire [7:0] uio_in,

    output wire [7:0] uio_out,

    output wire [7:0] uio_oe,

    input  wire       ena,

    input  wire       clk

);

    // ========================================================
    // Control signals
    // ========================================================

    wire enable;

    wire [1:0] sensitivity;

    wire reset_n;


    assign enable     = ena & uio_in[0];

    assign sensitivity = uio_in[2:1];

    assign reset_n    = uio_in[7];


    // ========================================================
    // Registers
    // ========================================================

    reg [7:0] pixel_out;

    reg [7:0] previous_pixel;

    // Temporal history
    reg activity_d1;
    reg activity_d2;


    // ========================================================
    // Combinational signals
    // ========================================================

    wire current_change;

    reg [7:0] difference;

    reg [7:0] threshold;

    reg [1:0] activity_level;

    reg update;

    reg hold;


    // ========================================================
    // Transition detector
    // ========================================================

    assign current_change =
        (ui_in != previous_pixel);


    // ========================================================
    // Absolute difference detector
    // ========================================================

    always @(*) begin

        if (ui_in >= previous_pixel)

            difference =
                ui_in - previous_pixel;

        else

            difference =
                previous_pixel - ui_in;

    end


    // ========================================================
    // Temporal activity classifier
    //
    // current_change
    // activity_d1
    // activity_d2
    //
    // 00 = very low activity
    // 01 = low activity
    // 10 = medium activity
    // 11 = high activity
    // ========================================================

    always @(*) begin

        case ({current_change,
               activity_d1,
               activity_d2})

            3'b000,
            3'b001,
            3'b010:

                activity_level = 2'b00;


            3'b011,
            3'b100:

                activity_level = 2'b01;


            3'b101,
            3'b110:

                activity_level = 2'b10;


            default:

                activity_level = 2'b11;

        endcase

    end


    // ========================================================
    // Adaptive threshold
    //
    // sensitivity:
    //
    // 00 = 1
    // 01 = 3
    // 10 = 7
    // 11 = 15
    //
    // Temporal activity modifies the threshold.
    // ========================================================

    always @(*) begin

        case (sensitivity)

            2'b00:
                threshold = 8'd1;

            2'b01:
                threshold = 8'd3;

            2'b10:
                threshold = 8'd7;

            default:
                threshold = 8'd15;

        endcase


        case (activity_level)

            // Very low activity
            // More aggressive suppression

            2'b00:

                threshold = threshold + 8'd4;


            // Low activity

            2'b01:

                threshold = threshold + 8'd2;


            // Medium activity

            2'b10:

                threshold = threshold;


            // High activity
            // Become more sensitive

            2'b11:

                if (threshold >= 8'd2)

                    threshold =
                        threshold - 8'd2;

                else

                    threshold = 8'd0;

        endcase

    end


    // ========================================================
    // UPDATE / HOLD decision
    // ========================================================

    always @(*) begin

        update = 1'b0;

        hold = 1'b1;


        if (enable &&
            current_change &&
            (difference >= threshold)) begin

            update = 1'b1;

            hold = 1'b0;

        end

    end


    // ========================================================
    // Sequential block
    // ========================================================

    always @(posedge clk or negedge reset_n) begin

        if (!reset_n) begin

            pixel_out     <= 8'd0;

            previous_pixel <= 8'd0;

            activity_d1   <= 1'b0;

            activity_d2   <= 1'b0;

        end

        else begin

            // Save current pixel for next comparison

            previous_pixel <= ui_in;


            // Temporal activity history

            activity_d2 <= activity_d1;

            activity_d1 <= current_change;


            // Update adaptive pixel register

            if (enable && update)

                pixel_out <= ui_in;

        end

    end


    // ========================================================
    // Outputs
    // ========================================================

    assign uo_out = pixel_out;


    // uio_out:
    //
    // bit 0 = UPDATE
    // bit 1 = HOLD
    // bits 3:2 = ACTIVITY
    //

    assign uio_out = {
        4'b0000,
        activity_level,
        hold,
        update
    };


    // ========================================================
    // Bidirectional pin direction
    //
    // uio[3:0] = outputs
    // uio[7:4] = inputs
    //
    // uio[7] is RESET_N input.
    // ========================================================

    assign uio_oe = 8'b0000_1111;


endmodule

`default_nettype wire
