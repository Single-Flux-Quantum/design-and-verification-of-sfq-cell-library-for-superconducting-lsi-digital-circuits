// ==============================================================================
// SIMIT-Nb03 Standard Cell Library - Synthesizable Behavioral Models
// Reference: Gao et al. (SIMIT / CAS, Shanghai)
// "Design and Verification of SFQ Cell Library for Superconducting LSI Digital Circuits"
// IEEE Transactions on Applied Superconductivity, Vol. 31, No. 5, August 2021
// ==============================================================================

`timescale 1ps/100fs

// -----------------------------------------------------------------------------
// 1. JTL: Josephson Transmission Line (2 JJs, 60 um x 30 um)
// -----------------------------------------------------------------------------
module jtl_stage (
    input  wire in_pulse,
    input  wire rst_n,
    output reg  out_pulse
);
    parameter DELAY_PS = 4;
    parameter PULSE_WIDTH_PS = 4;

    always @(posedge in_pulse or negedge rst_n) begin
        if (!rst_n) begin
            out_pulse <= 1'b0;
        end else begin
            #DELAY_PS out_pulse <= 1'b1;
            #PULSE_WIDTH_PS out_pulse <= 1'b0;
        end
    end
endmodule


// -----------------------------------------------------------------------------
// 2. SPL31: 1-to-2 SFQ Splitter (3 JJs, 60 um x 30 um)
// -----------------------------------------------------------------------------
module splitter_1to2 (
    input  wire in_pulse,
    input  wire rst_n,
    output reg  out1,
    output reg  out2
);
    parameter DELAY_PS = 5;
    parameter PULSE_WIDTH_PS = 4;

    always @(posedge in_pulse or negedge rst_n) begin
        if (!rst_n) begin
            out1 <= 1'b0;
            out2 <= 1'b0;
        end else begin
            #DELAY_PS;
            out1 <= 1'b1;
            out2 <= 1'b1;
            #PULSE_WIDTH_PS;
            out1 <= 1'b0;
            out2 <= 1'b0;
        end
    end
endmodule


// -----------------------------------------------------------------------------
// 3. CB: Confluence Buffer (5 JJs, 60 um x 60 um)
// -----------------------------------------------------------------------------
module confluence_buffer (
    input  wire in1,
    input  wire in2,
    input  wire rst_n,
    output reg  out
);
    parameter DELAY_PS = 5;
    parameter PULSE_WIDTH_PS = 4;

    always @(posedge in1 or posedge in2 or negedge rst_n) begin
        if (!rst_n) begin
            out <= 1'b0;
        end else begin
            #DELAY_PS out <= 1'b1;
            #PULSE_WIDTH_PS out <= 1'b0;
        end
    end
endmodule


// -----------------------------------------------------------------------------
// 4. DFF: D-Flip-Flop (4 JJs, 60 um x 60 um)
// -----------------------------------------------------------------------------
module dff_cell (
    input  wire data_in,
    input  wire clk_in,
    input  wire rst_n,
    output reg  data_out,
    output reg  stored_state
);
    parameter DELAY_PS = 6;
    parameter PULSE_WIDTH_PS = 4;

    always @(posedge data_in or posedge clk_in or negedge rst_n) begin
        if (!rst_n) begin
            stored_state <= 1'b0;
            data_out <= 1'b0;
        end else if (data_in) begin
            stored_state <= 1'b1;
        end else if (clk_in) begin
            if (stored_state) begin
                stored_state <= 1'b0;
                #DELAY_PS data_out <= 1'b1;
                #PULSE_WIDTH_PS data_out <= 1'b0;
            end else begin
                data_out <= 1'b0;
            end
        end
    end
endmodule


// -----------------------------------------------------------------------------
// 5. RDFF: Resettable D-Flip-Flop (11 JJs, 90 um x 60 um, Fig. 2b)
// -----------------------------------------------------------------------------
module rdff_cell (
    input  wire ai,       // Data Input
    input  wire ti,       // Clock Input
    input  wire ri,       // Reset Input
    input  wire rst_n,    // Active-low global hardware reset
    output reg  ao,       // Data Output
    output reg  state     // Probed internal flux state (0 or 1)
);
    parameter DELAY_PS = 6;
    parameter PULSE_WIDTH_PS = 4;

    always @(posedge ai or posedge ti or posedge ri or negedge rst_n) begin
        if (!rst_n) begin
            state <= 1'b0;
            ao <= 1'b0;
        end else if (ri) begin
            // Reset clears trapped flux without emitting output at AO
            state <= 1'b0;
        end else if (ai) begin
            // Data in traps single fluxon Phi0
            state <= 1'b1;
        end else if (ti) begin
            // Clock interrogation
            if (state) begin
                state <= 1'b0;
                #DELAY_PS ao <= 1'b1;
                #PULSE_WIDTH_PS ao <= 1'b0;
            end else begin
                ao <= 1'b0;
            end
        end
    end
endmodule


// -----------------------------------------------------------------------------
// 6. TFF: Toggle Flip-Flop (6 JJs, 60 um x 60 um)
// -----------------------------------------------------------------------------
module tff_cell (
    input  wire trig,
    input  wire rst_n,
    output reg  out,
    output reg  state
);
    parameter DELAY_PS = 6;
    parameter PULSE_WIDTH_PS = 4;

    always @(posedge trig or negedge rst_n) begin
        if (!rst_n) begin
            state <= 1'b0;
            out <= 1'b0;
        end else begin
            state <= ~state;
            if (state == 1'b1) begin
                // Emit pulse on falling transition (frequency divide-by-2)
                #DELAY_PS out <= 1'b1;
                #PULSE_WIDTH_PS out <= 1'b0;
            end
        end
    end
endmodule


// -----------------------------------------------------------------------------
// 7. AND Gate (10 JJs, 90 um x 90 um)
// -----------------------------------------------------------------------------
module and_cell (
    input  wire a,
    input  wire b,
    input  wire clk,
    input  wire rst_n,
    output reg  out
);
    parameter DELAY_PS = 7;
    parameter PULSE_WIDTH_PS = 4;

    reg state_a, state_b;

    always @(posedge a or posedge b or posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state_a <= 1'b0;
            state_b <= 1'b0;
            out <= 1'b0;
        end else if (a) begin
            state_a <= 1'b1;
        end else if (b) begin
            state_b <= 1'b1;
        end else if (clk) begin
            if (state_a && state_b) begin
                #DELAY_PS out <= 1'b1;
                #PULSE_WIDTH_PS out <= 1'b0;
            end else begin
                out <= 1'b0;
            end
            state_a <= 1'b0;
            state_b <= 1'b0;
        end
    end
endmodule


// -----------------------------------------------------------------------------
// 8. XOR Gate (12 JJs, 90 um x 60 um)
// -----------------------------------------------------------------------------
module xor_cell (
    input  wire a,
    input  wire b,
    input  wire clk,
    input  wire rst_n,
    output reg  out
);
    parameter DELAY_PS = 7;
    parameter PULSE_WIDTH_PS = 4;

    reg state_a, state_b;

    always @(posedge a or posedge b or posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state_a <= 1'b0;
            state_b <= 1'b0;
            out <= 1'b0;
        end else if (a) begin
            state_a <= 1'b1;
        end else if (b) begin
            state_b <= 1'b1;
        end else if (clk) begin
            if (state_a ^ state_b) begin
                #DELAY_PS out <= 1'b1;
                #PULSE_WIDTH_PS out <= 1'b0;
            end else begin
                out <= 1'b0;
            end
            state_a <= 1'b0;
            state_b <= 1'b0;
        end
    end
endmodule


// -----------------------------------------------------------------------------
// 9. NOT Gate (Inverter) (7 JJs, 60 um x 60 um)
// -----------------------------------------------------------------------------
module not_cell (
    input  wire in_pulse,
    input  wire clk,
    input  wire rst_n,
    output reg  out
);
    parameter DELAY_PS = 6;
    parameter PULSE_WIDTH_PS = 4;

    reg received_pulse;

    always @(posedge in_pulse or posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            received_pulse <= 1'b0;
            out <= 1'b0;
        end else if (in_pulse) begin
            received_pulse <= 1'b1;
        end else if (clk) begin
            if (!received_pulse) begin
                // Invert: emit pulse when input did NOT arrive
                #DELAY_PS out <= 1'b1;
                #PULSE_WIDTH_PS out <= 1'b0;
            end else begin
                out <= 1'b0;
            end
            received_pulse <= 1'b0;
        end
    end
endmodule


// -----------------------------------------------------------------------------
// 10. NDRO: Non-Destructive Readout Cell (12 JJs, 90 um x 60 um)
// -----------------------------------------------------------------------------
module ndro_cell (
    input  wire set_in,
    input  wire reset_in,
    input  wire read_in,
    input  wire rst_n,
    output reg  out,
    output reg  stored_flux
);
    parameter DELAY_PS = 6;
    parameter PULSE_WIDTH_PS = 4;

    always @(posedge set_in or posedge reset_in or posedge read_in or negedge rst_n) begin
        if (!rst_n) begin
            stored_flux <= 1'b0;
            out <= 1'b0;
        end else if (reset_in) begin
            stored_flux <= 1'b0;
        end else if (set_in) begin
            stored_flux <= 1'b1;
        end else if (read_in) begin
            if (stored_flux) begin
                // Read without altering stored flux
                #DELAY_PS out <= 1'b1;
                #PULSE_WIDTH_PS out <= 1'b0;
            end else begin
                out <= 1'b0;
            end
        end
    end
endmodule
