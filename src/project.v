`default_nettype none
`timescale 1ns / 1ps

module tt_um_vital_ap (
    input  wire [7:0] ui_in,
    output wire [7:0] uo_out,

    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,

    input wire ena,
    input wire clk,
    input wire rst_n
);

    // =========================================================
    // CONTROL
    // =========================================================

    wire enable;
    wire [1:0] sensitivity;

    assign enable = ena;

    assign sensitivity = uio_in[1:0];


    // =========================================================
    // INTERNAL REGISTERS
    // =========================================================

    reg [7:0] pixel_out;
    reg [7:0] previous_pixel;

    reg activity_d1;
    reg activity_d2;


    // =========================================================
    // PIXEL DIFFERENCE
    // =========================================================

    wire current_change;

    reg [7:0] difference;

    assign current_change = (ui_in != previous_pixel);


    always @(*) begin

        if (ui_in >= previous_pixel)
            difference = ui_in - previous_pixel;
        else
            difference = previous_pixel - ui_in;

    end


    // =========================================================
    // TEMPORAL ACTIVITY DETECTOR
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
    //
    // Sensitivity:
    //
    // 00 -> threshold 1
    // 01 -> threshold 3
    // 10 -> threshold 7
    // 11 -> threshold 15
    //
    // Temporal activity modifies threshold.
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
    // UPDATE / HOLD DECISION
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
    // SEQUENTIAL ADAPTIVE REGISTER
    // =========================================================

    always @(posedge clk or negedge rst_n) begin

        if (!rst_n) begin

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
    // PIXEL OUTPUT
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
    // BIDIRECTIONAL PIN DIRECTIONS
    //
    // uio[0] = SENSITIVITY[0] INPUT
    // uio[1] = SENSITIVITY[1] INPUT
    //
    // uio[3] = UPDATE OUTPUT
    // uio[4] = HOLD OUTPUT
    // uio[5] = ACTIVITY[0] OUTPUT
    // uio[6] = ACTIVITY[1] OUTPUT
    //
    // uio[2] and uio[7] unused inputs
    // =========================================================

    assign uio_oe = 8'b0111_1000;


endmodule

`default_nettype wire
