// ==============================================================================
// 8-Bit Superconducting Pipelined Datapath Benchmark using SIMIT-Nb03 Cells
// Reference: Gao et al., IEEE Transactions on Applied Superconductivity, Aug. 2021
// ==============================================================================

`timescale 1ps/100fs

module lsi_datapath_demo (
    input  wire        clk,        // Global SFQ clock trigger
    input  wire        rst_n,      // Asynchronous global reset
    input  wire [7:0]  data_in,    // 8-bit data input pulses
    input  wire        load_en,    // Load enable pulse
    output wire [7:0]  data_out,   // 8-bit parallel registered output pulses
    output wire [7:0]  cell_states // Probed internal loop states
);

    genvar i;
    generate
        for (i = 0; i < 8; i = i + 1) begin : gen_slice
            wire jtl_in, jtl_out;
            wire split_clk1, split_clk2;

            // Input buffering via 2-stage JTL
            jtl_stage u_jtl1 (
                .in_pulse  (data_in[i]),
                .rst_n     (rst_n),
                .out_pulse (jtl_in)
            );

            jtl_stage u_jtl2 (
                .in_pulse  (jtl_in),
                .rst_n     (rst_n),
                .out_pulse (jtl_out)
            );

            // Clock distribution splitter
            splitter_1to2 u_spl (
                .in_pulse  (clk),
                .rst_n     (rst_n),
                .out1      (split_clk1),
                .out2      (split_clk2)
            );

            // Resettable D-Flip-Flop storage element
            rdff_cell u_rdff (
                .ai     (jtl_out),
                .ti     (split_clk1),
                .ri     (~load_en),
                .rst_n  (rst_n),
                .ao     (data_out[i]),
                .state  (cell_states[i])
            );
        end
    endgenerate

endmodule
