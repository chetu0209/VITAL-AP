`timescale 1ns/1ps

module tt_um_vital_ap #(
    parameter DATA_WIDTH = 8
)(
    input  logic                  clk,

    // 8-bit grayscale pixel input
    input  logic [DATA_WIDTH-1:0] pixel_in,

    // Enable adaptive processing
    input  logic                  enable,

    // Select initial sensitivity
    // 00 = high sensitivity
    // 01 = medium sensitivity
    // 10 = low sensitivity
    // 11 = very low sensitivity
    input  logic [1:0]            sensitivity,

    // Registered output pixel
    output logic [DATA_WIDTH-1:0] pixel_out,

    // Status outputs
    output logic                  update,
    output logic                  hold,
    output logic [1:0]            activity_level
);

    // ------------------------------------------------------------
    // Internal signals
    // ------------------------------------------------------------

    logic [DATA_WIDTH-1:0] previous_pixel;

    logic [DATA_WIDTH-1:0] difference;

    logic [DATA_WIDTH-1:0] threshold;

    // Temporal activity history
    logic activity_d1;
    logic activity_d2;

    logic current_change;

    // ------------------------------------------------------------
    // Calculate absolute pixel difference
    // ------------------------------------------------------------

    always_comb begin
        if (pixel_in >= previous_pixel)
            difference = pixel_in - previous_pixel;
        else
            difference = previous_pixel - pixel_in;
    end

    // ------------------------------------------------------------
    // Current transition detection
    // ------------------------------------------------------------

    always_comb begin
        current_change = (pixel_in != previous_pixel);
    end

    // ------------------------------------------------------------
    // Activity level
    //
    // Uses present transition + previous two transitions.
    //
    // 00 = no/very low activity
    // 01 = low activity
    // 10 = medium activity
    // 11 = high activity
    // ------------------------------------------------------------

    always_comb begin
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

    // ------------------------------------------------------------
    // Adaptive threshold
    //
    // Base threshold comes from sensitivity.
    //
    // High activity -> smaller threshold
    // Low activity  -> larger threshold
    //
    // This means:
    // Static image  -> aggressive suppression
    // Dynamic image -> more frequent updates
    // ------------------------------------------------------------

    always_comb begin

        case (sensitivity)

            2'b00: threshold = 8'd1;
            2'b01: threshold = 8'd3;
            2'b10: threshold = 8'd7;
            2'b11: threshold = 8'd15;

            default: threshold = 8'd3;

        endcase

        // Adapt threshold using temporal activity

        case (activity_level)

            2'b00:
                threshold = threshold + 8'd4;

            2'b01:
                threshold = threshold + 8'd2;

            2'b10:
                threshold = threshold;

            2'b11:
                if (threshold > 8'd2)
                    threshold = threshold - 8'd2;

            default:
                threshold = threshold;

        endcase

    end

    // ------------------------------------------------------------
    // Update decision
    //
    // UPDATE if:
    //   1. Processing enabled
    //   2. Pixel difference >= adaptive threshold
    //
    // HOLD otherwise.
    // ------------------------------------------------------------

    always_comb begin

        update = 1'b0;
        hold   = 1'b1;

        if (enable && current_change &&
            (difference >= threshold)) begin

            update = 1'b1;
            hold   = 1'b0;

        end

    end

    // ------------------------------------------------------------
    // Sequential logic
    // ------------------------------------------------------------

    always_ff @(posedge clk or negedge rst_n) begin

        if (!rst_n) begin

            previous_pixel <= '0;
            pixel_out      <= '0;

            activity_d1    <= 1'b0;
            activity_d2    <= 1'b0;

        end
        else begin

            // Store previous pixel
            previous_pixel <= pixel_in;

            // Temporal activity history
            activity_d2 <= activity_d1;
            activity_d1 <= current_change;

            // Adaptive register update
            if (enable && update) begin
                pixel_out <= pixel_in;
            end

        end

    end

endmodule
