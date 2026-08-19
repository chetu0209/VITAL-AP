`default_nettype none
`timescale 1ns / 1ps

module tt_um_vital_ap (
    input  wire [7:0] ui_in,
    output wire [7:0] uo_out,

    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,

    input wire clk,
    input wire ena
);

    // =========================================================
    // CONTROL
    // =========================================================

    wire enable;
    wire reset_n;

    wire [1:0] sensitivity;

    assign enable = ena;

    assign sensitivity = uio_in[1:0];

    assign reset_n = uio_in[2];


    // =========================================================
    // INTERNAL REGISTERS
    // =========================================================

    reg [7:0] pixel_out;

    reg [7:0] previous_pixel;

    reg activity_d1;
    reg activity_d2;


    // =========================================================
    // DIFFERENCE
    // =========================================================

    wire current_change;

    reg [7:0] difference;

    assign current_change =
        (ui_in != previous_pixel);


    always @(*) begin

        if (ui_in >= previous_pixel)
            difference = ui_in - previous_pixel;
        else
            difference = previous_pixel - ui_in;

    end


    // =========================================================
    // TEMPORAL ACTIVITY
    // =========================================================

    reg [1:0] activity_level;

    always @(*) begin

        case ({current_change, activity_d1, activity_d2})

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


    // =========================================================
    // ADAPTIVE THRESHOLD
    // =========================================================

    reg [7:0] threshold;

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

            2'b00:
                threshold = threshold + 8'd4;

            2'b01:
                threshold = threshold + 8'd2;

            2'b10:
                threshold = threshold;

            2'b11:
                if (threshold >= 8'd2)
                    threshold = threshold - 8'd2;
                else
                    threshold = 8'd0;

        endcase

    end


    // =========================================================
    // UPDATE / HOLD
    // =========================================================

    reg update;
    reg hold;

    always @(*) begin

        update = 1'b0;
        hold   = 1'b1;

        if (enable &&
            current_change &&
            (difference >= threshold)) begin

            update = 1'b1;
            hold   = 1'b0;

        end

    end


    // =========================================================
    // SEQUENTIAL LOGIC
    // =========================================================

    always @(posedge clk or negedge reset_n) begin

        if (!reset_n) begin

            pixel_out      <= 8'd0;
            previous_pixel <= 8'd0;

            activity_d1    <= 1'b0;
            activity_d2    <= 1'b0;

        end
        else begin

            previous_pixel <= ui_in;

            activity_d2 <= activity_d1;
            activity_d1 <= current_change;

            if (enable && update)
                pixel_out <= ui_in;

        end

    end


    // =========================================================
    // OUTPUT PIXEL
    // =========================================================

    assign uo_out = pixel_out;


    // =========================================================
    // STATUS OUTPUTS
    //
    // uio_out[3] = UPDATE
    // uio_out[4] = HOLD
    // uio_out[5] = ACTIVITY[0]
    // uio_out[6] = ACTIVITY[1]
    // =========================================================

    assign uio_out = {
        1'b0,
        activity_level[1],
        activity_level[0],
        hold,
        update,
        3'b000
    };


    // =========================================================
    // PIN DIRECTIONS
    //
    // uio[0] = INPUT
    // uio[1] = INPUT
    // uio[2] = INPUT
    //
    // uio[3] = OUTPUT
    // uio[4] = OUTPUT
    // uio[5] = OUTPUT
    // uio[6] = OUTPUT
    //
    // uio[7] = INPUT/unused
    // =========================================================

    assign uio_oe = 8'b0111_1000;


endmodule

`default_nettype wire
