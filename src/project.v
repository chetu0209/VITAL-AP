`default_nettype none
`timescale 1ns / 1ps

// ============================================================
// VITAL-APEX
//
// Value-, Prediction-, Activity-, and Edge-aware
// Adaptive Register for Low-Power Image and Video Processing
//
// Functional blocks:
//
// 1. Four-sample temporal history
// 2. Temporal predictor
// 3. Prediction error
// 4. Transition detector
// 5. Edge-strength estimator
// 6. Temporal activity detector
// 7. Motion burst detector
// 8. Value-aware threshold
// 9. Adaptive threshold
// 10. Edge preservation
// 11. Prediction confidence
// 12. Adaptive register
//
// Target:
// SKY130 / Tiny Tapeout
// ============================================================

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

    // ========================================================
    // INPUT
    //
    // ui_in = current 8-bit pixel
    //
    // uio_in:
    //
    // [1:0] sensitivity
    // [2]   prediction enable
    // [3]   force update
    // [4]   value-aware enable
    // [5]   edge preservation enable
    // [6]   motion enhancement enable
    // [7]   reserved / mode
    // ========================================================

    wire [7:0] pixel_in;

    assign pixel_in = ui_in;

    wire [1:0] sensitivity;
    wire prediction_enable;
    wire force_update;
    wire value_enable;
    wire edge_enable;
    wire motion_enable;

    assign sensitivity        = uio_in[1:0];
    assign prediction_enable  = uio_in[2];
    assign force_update       = uio_in[3];
    assign value_enable       = uio_in[4];
    assign edge_enable        = uio_in[5];
    assign motion_enable      = uio_in[6];


    // ========================================================
    // TEMPORAL HISTORY
    // ========================================================

    reg [7:0] pixel_d1;
    reg [7:0] pixel_d2;
    reg [7:0] pixel_d3;
    reg [7:0] pixel_d4;


    // ========================================================
    // OUTPUT REGISTER
    // ========================================================

    reg [7:0] pixel_out;


    // ========================================================
    // ACTIVITY HISTORY
    // ========================================================

    reg transition_d1;
    reg transition_d2;
    reg transition_d3;
    reg transition_d4;


    // ========================================================
    // MOTION BURST COUNTER
    // ========================================================

    reg [3:0] motion_count;


    // ========================================================
    // HISTORY SUM
    //
    // 4 x 8-bit values = 10-bit sum
    // ========================================================

    wire [9:0] history_sum;

    assign history_sum =
          {2'b00, pixel_d1}
        + {2'b00, pixel_d2}
        + {2'b00, pixel_d3}
        + {2'b00, pixel_d4};


    // ========================================================
    // TEMPORAL PREDICTION
    // ========================================================

    wire [7:0] predicted_pixel;

    assign predicted_pixel = history_sum[9:2];


    // ========================================================
    // ABSOLUTE DIFFERENCE FUNCTION
    // ========================================================

    function [8:0] abs_diff;

        input [7:0] a;
        input [7:0] b;

        begin

            if (a >= b)
                abs_diff = {1'b0, a} - {1'b0, b};

            else
                abs_diff = {1'b0, b} - {1'b0, a};

        end

    endfunction


    // ========================================================
    // CURRENT -> PREVIOUS DIFFERENCE
    // ========================================================

    wire [8:0] transition_difference;

    assign transition_difference =
        abs_diff(pixel_in, pixel_d1);


    // ========================================================
    // CURRENT -> PREDICTION DIFFERENCE
    // ========================================================

    wire [8:0] prediction_difference;

    assign prediction_difference =
        abs_diff(pixel_in, predicted_pixel);


    // ========================================================
    // PREVIOUS -> SECOND PREVIOUS
    // ========================================================

    wire [8:0] previous_difference;

    assign previous_difference =
        abs_diff(pixel_d1, pixel_d2);


    // ========================================================
    // SECOND -> THIRD PREVIOUS
    // ========================================================

    wire [8:0] history_difference;

    assign history_difference =
        abs_diff(pixel_d2, pixel_d3);


    // ========================================================
    // EDGE STRENGTH
    //
    // Edge strength is based on two consecutive gradients:
    //
    // |P[n] - P[n-1]| +
    // |P[n-1] - P[n-2]|
    //
    // This is useful for preserving image boundaries.
    // ========================================================

    wire [9:0] edge_strength;

    assign edge_strength =
          {1'b0, transition_difference}
        + {1'b0, previous_difference};


    // ========================================================
    // SECOND EDGE MEASURE
    // ========================================================

    wire [9:0] edge_history;

    assign edge_history =
          {1'b0, previous_difference}
        + {1'b0, history_difference};


    // ========================================================
    // TEMPORAL ACTIVITY
    //
    // Four recent transition indicators.
    // ========================================================

    wire [2:0] activity_count;

    assign activity_count =
          {2'b00, transition_d1}
        + {2'b00, transition_d2}
        + {2'b00, transition_d3}
        + {2'b00, transition_d4};


    // ========================================================
    // ACTIVITY LEVEL
    // ========================================================

    reg [1:0] activity_level;

    always @(*) begin

        case (activity_count)

            3'd0:
                activity_level = 2'b00;

            3'd1:
                activity_level = 2'b01;

            3'd2:
                activity_level = 2'b10;

            default:
                activity_level = 2'b11;

        endcase

    end


    // ========================================================
    // VALUE CLASSIFIER
    // ========================================================

    reg [1:0] value_class;

    always @(*) begin

        if (pixel_in < 8'd64)

            value_class = 2'b00;

        else if (pixel_in < 8'd128)

            value_class = 2'b01;

        else if (pixel_in < 8'd192)

            value_class = 2'b10;

        else

            value_class = 2'b11;

    end


    // ========================================================
    // BASIC SIGNIFICANT TRANSITION
    // ========================================================

    wire significant_transition;

    assign significant_transition =
        (transition_difference >= 9'd8);


    // ========================================================
    // EDGE DETECTION
    //
    // Strong gradient = image boundary / detail.
    // ========================================================

    wire strong_edge;

    assign strong_edge =
        (edge_strength >= 10'd24);


    // ========================================================
    // STRONG MOTION
    // ========================================================

    wire strong_motion;

    assign strong_motion =
        (transition_difference >= 9'd16);


    // ========================================================
    // ADAPTIVE THRESHOLD
    // ========================================================

    reg [8:0] threshold_base;
    reg [8:0] threshold_value;
    reg [8:0] threshold_activity;
    reg [8:0] threshold_edge;
    reg [8:0] adaptive_threshold;


    // ========================================================
    // BASE THRESHOLD
    // ========================================================

    always @(*) begin

        case (sensitivity)

            2'b00:
                threshold_base = 9'd2;

            2'b01:
                threshold_base = 9'd5;

            2'b10:
                threshold_base = 9'd10;

            default:
                threshold_base = 9'd20;

        endcase

    end


    // ========================================================
    // VALUE-DEPENDENT THRESHOLD
    // ========================================================

    always @(*) begin

        threshold_value = threshold_base;

        if (value_enable) begin

            case (value_class)

                // Dark pixels
                2'b00:
                    threshold_value =
                        threshold_base + 9'd3;

                // Mid-low
                2'b01:
                    threshold_value =
                        threshold_base + 9'd1;

                // Mid-high
                2'b10:
                    threshold_value =
                        threshold_base;

                // Bright pixels
                2'b11:

                    if (threshold_base > 9'd2)
                        threshold_value =
                            threshold_base - 9'd2;

                    else
                        threshold_value = 9'd0;

            endcase

        end

    end


    // ========================================================
    // ACTIVITY-DEPENDENT THRESHOLD
    //
    // Static image -> larger threshold
    // Motion -> smaller threshold
    // ========================================================

    always @(*) begin

        threshold_activity = threshold_value;

        case (activity_level)

            2'b00:
                threshold_activity =
                    threshold_value + 9'd6;

            2'b01:
                threshold_activity =
                    threshold_value + 9'd3;

            2'b10:
                threshold_activity =
                    threshold_value;

            2'b11:

                if (threshold_value > 9'd4)
                    threshold_activity =
                        threshold_value - 9'd4;

                else
                    threshold_activity = 9'd0;

        endcase

    end


    // ========================================================
    // EDGE-DEPENDENT THRESHOLD
    //
    // Strong edges get lower threshold so that image detail
    // is preserved.
    // ========================================================

    always @(*) begin

        threshold_edge = threshold_activity;

        if (edge_enable) begin

            if (strong_edge) begin

                if (threshold_activity > 9'd5)
                    threshold_edge =
                        threshold_activity - 9'd5;

                else
                    threshold_edge = 9'd0;

            end

            else if (edge_history >= 10'd16) begin

                if (threshold_activity > 9'd2)
                    threshold_edge =
                        threshold_activity - 9'd2;

                else
                    threshold_edge = 9'd0;

            end

        end

    end


    // ========================================================
    // MOTION ENHANCEMENT
    // ========================================================

    always @(*) begin

        adaptive_threshold = threshold_edge;

        if (motion_enable) begin

            if (motion_count >= 4'd5) begin

                if (threshold_edge > 9'd4)
                    adaptive_threshold =
                        threshold_edge - 9'd4;

                else
                    adaptive_threshold = 9'd0;

            end

            else if (motion_count >= 4'd3) begin

                if (threshold_edge > 9'd2)
                    adaptive_threshold =
                        threshold_edge - 9'd2;

                else
                    adaptive_threshold = 9'd0;

            end

        end

    end


    // ========================================================
    // PREDICTION CONFIDENCE
    //
    // High confidence means the current pixel is close to
    // the temporal prediction.
    // ========================================================

    wire prediction_confidence;

    assign prediction_confidence =
        (prediction_difference <= adaptive_threshold);


    // ========================================================
    // TEMPORAL STABILITY
    // ========================================================

    wire temporal_stable;

    assign temporal_stable =
        (activity_count == 3'd0);


    // ========================================================
    // EDGE PRESERVE
    // ========================================================

    wire preserve_edge;

    assign preserve_edge =
        edge_enable && strong_edge;


    // ========================================================
    // MOTION PRESERVE
    // ========================================================

    wire preserve_motion;

    assign preserve_motion =
        motion_enable &&
        (strong_motion || motion_count >= 4'd4);


    // ========================================================
    // UPDATE DECISION
    // ========================================================

    reg update_decision;

    always @(*) begin

        update_decision = 1'b0;


        // ----------------------------------------------------
        // Force update
        // ----------------------------------------------------

        if (force_update) begin

            update_decision = 1'b1;

        end


        // ----------------------------------------------------
        // Disabled
        // ----------------------------------------------------

        else if (!ena) begin

            update_decision = 1'b0;

        end


        // ----------------------------------------------------
        // Edge preservation
        // ----------------------------------------------------

        else if (preserve_edge) begin

            update_decision = 1'b1;

        end


        // ----------------------------------------------------
        // Motion preservation
        // ----------------------------------------------------

        else if (preserve_motion) begin

            update_decision = 1'b1;

        end


        // ----------------------------------------------------
        // Prediction enabled
        // ----------------------------------------------------

        else if (prediction_enable) begin

            if (!prediction_confidence)
                update_decision = 1'b1;

            else if (transition_difference >
                     adaptive_threshold)
                update_decision = 1'b1;

        end


        // ----------------------------------------------------
        // Prediction disabled
        // ----------------------------------------------------

        else begin

            if (transition_difference >
                adaptive_threshold)

                update_decision = 1'b1;

        end

    end


    // ========================================================
    // TEMPORAL HOLD DECISION
    // ========================================================

    wire hold_decision;

    assign hold_decision =
        ena && !update_decision;


    // ========================================================
    // SEQUENTIAL LOGIC
    // ========================================================

    always @(posedge clk or negedge rst_n) begin

        if (!rst_n) begin

            pixel_d1 <= 8'd0;
            pixel_d2 <= 8'd0;
            pixel_d3 <= 8'd0;
            pixel_d4 <= 8'd0;

            pixel_out <= 8'd0;

            transition_d1 <= 1'b0;
            transition_d2 <= 1'b0;
            transition_d3 <= 1'b0;
            transition_d4 <= 1'b0;

            motion_count <= 4'd0;

        end

        else begin

            // ------------------------------------------------
            // Four-stage temporal history
            // ------------------------------------------------

            pixel_d4 <= pixel_d3;
            pixel_d3 <= pixel_d2;
            pixel_d2 <= pixel_d1;
            pixel_d1 <= pixel_in;


            // ------------------------------------------------
            // Transition history
            // ------------------------------------------------

            transition_d4 <= transition_d3;
            transition_d3 <= transition_d2;
            transition_d2 <= transition_d1;
            transition_d1 <= significant_transition;


            // ------------------------------------------------
            // Motion burst accumulation
            // ------------------------------------------------

            if (strong_motion) begin

                if (motion_count < 4'd15)
                    motion_count <= motion_count + 4'd1;

            end

            else begin

                if (motion_count > 4'd0)
                    motion_count <= motion_count - 4'd1;

            end


            // ------------------------------------------------
            // Adaptive output register
            // ------------------------------------------------

            if (update_decision)
                pixel_out <= pixel_in;

        end

    end


    // ========================================================
    // OUTPUT DATA
    // ========================================================

    assign uo_out = pixel_out;


    // ========================================================
    // STATUS OUTPUTS
    //
    // uio_out[0] = update
    // uio_out[1] = hold
    // uio_out[2] = prediction confidence
    // uio_out[3] = strong edge
    // uio_out[4] = strong motion
    // uio_out[5] = activity bit 0
    // uio_out[6] = activity bit 1
    // uio_out[7] = motion burst active
    // ========================================================

    assign uio_out[0] = update_decision;
    assign uio_out[1] = hold_decision;
    assign uio_out[2] = prediction_confidence;
    assign uio_out[3] = strong_edge;
    assign uio_out[4] = strong_motion;
    assign uio_out[5] = activity_level[0];
    assign uio_out[6] = activity_level[1];
    assign uio_out[7] = (motion_count >= 4'd4);


    // ========================================================
    // UIO DIRECTION
    //
    // All UIO pins are inputs.
    //
    // Status is available on UIO through the corresponding
    // output path when configured externally.
    //
    // Keeping UIO input-only avoids contention.
    // ========================================================

    assign uio_oe = 8'b00000000;


endmodule

`default_nettype wire
