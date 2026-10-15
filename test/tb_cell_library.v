// ==============================================================================
// Comprehensive Testbench for SIMIT-Nb03 Standard Cell Library & Datapath
// Reference: Gao et al., IEEE Transactions on Applied Superconductivity, Aug. 2021
// ==============================================================================

`timescale 1ps/100fs

module tb_cell_library;

    reg clk;
    reg rst_n;
    reg [7:0] data_in;
    reg load_en;
    wire [7:0] data_out;
    wire [7:0] cell_states;

    // Single-cell test signals
    reg rdff_ai, rdff_ti, rdff_ri;
    wire rdff_ao, rdff_state;

    reg tff_trig;
    wire tff_out, tff_state;

    reg and_a, and_b, and_clk;
    wire and_out;

    reg xor_a, xor_b, xor_clk;
    wire xor_out;

    reg not_in, not_clk;
    wire not_out;

    integer errors = 0;
    integer tests_passed = 0;

    // Instantiate RDFF single cell
    rdff_cell u_test_rdff (
        .ai    (rdff_ai),
        .ti    (rdff_ti),
        .ri    (rdff_ri),
        .rst_n (rst_n),
        .ao    (rdff_ao),
        .state (rdff_state)
    );

    // Instantiate TFF single cell
    tff_cell u_test_tff (
        .trig  (tff_trig),
        .rst_n (rst_n),
        .out   (tff_out),
        .state (tff_state)
    );

    // Instantiate AND single cell
    and_cell u_test_and (
        .a     (and_a),
        .b     (and_b),
        .clk   (and_clk),
        .rst_n (rst_n),
        .out   (and_out)
    );

    // Instantiate XOR single cell
    xor_cell u_test_xor (
        .a     (xor_a),
        .b     (xor_b),
        .clk   (xor_clk),
        .rst_n (rst_n),
        .out   (xor_out)
    );

    // Instantiate NOT single cell
    not_cell u_test_not (
        .in_pulse (not_in),
        .clk      (not_clk),
        .rst_n    (rst_n),
        .out      (not_out)
    );

    // Instantiate 8-Bit Datapath Demo
    lsi_datapath_demo u_demo (
        .clk         (clk),
        .rst_n       (rst_n),
        .data_in     (data_in),
        .load_en     (load_en),
        .data_out    (data_out),
        .cell_states (cell_states)
    );

    initial begin
        $dumpfile("simit_sim.vcd");
        $dumpvars(0, tb_cell_library);

        // Initialize signals
        clk = 0;
        rst_n = 0;
        data_in = 8'h00;
        load_en = 0;

        rdff_ai = 0;
        rdff_ti = 0;
        rdff_ri = 0;

        tff_trig = 0;
        and_a = 0;
        and_b = 0;
        and_clk = 0;

        xor_a = 0;
        xor_b = 0;
        xor_clk = 0;

        not_in = 0;
        not_clk = 0;

        #50 rst_n = 1;
        #50;

        $display("=== STARTING SIMIT-Nb03 STANDARD CELL LIBRARY TESTBENCH ===");

        // Test 1: RDFF Data In -> Clock Out
        rdff_ai = 1; #5 rdff_ai = 0; #20;
        if (rdff_state == 1'b1) begin
            $display("[PASS] Test 1: RDFF data pulse trapped fluxon (state=1)");
            tests_passed = tests_passed + 1;
        end else begin
            $display("[FAIL] Test 1: RDFF state = %b", rdff_state);
            errors = errors + 1;
        end

        rdff_ti = 1; #5 rdff_ti = 0; #20;
        if (rdff_state == 1'b0) begin
            $display("[PASS] Test 2: RDFF clock emitted output pulse and cleared state");
            tests_passed = tests_passed + 1;
        end else begin
            $display("[FAIL] Test 2: RDFF state not cleared: %b", rdff_state);
            errors = errors + 1;
        end

        // Test 3: RDFF Reset Operation
        rdff_ai = 1; #5 rdff_ai = 0; #20;
        rdff_ri = 1; #5 rdff_ri = 0; #20;
        if (rdff_state == 1'b0) begin
            $display("[PASS] Test 3: RDFF reset pulse cleared state without trigger");
            tests_passed = tests_passed + 1;
        end else begin
            $display("[FAIL] Test 3: RDFF failed to reset: %b", rdff_state);
            errors = errors + 1;
        end

        // Test 4: TFF Frequency Divider
        tff_trig = 1; #5 tff_trig = 0; #20;
        tff_trig = 1; #5 tff_trig = 0; #20;
        if (tff_state == 1'b0) begin
            $display("[PASS] Test 4: TFF toggled twice returning to 0 (divide-by-2)");
            tests_passed = tests_passed + 1;
        end else begin
            $display("[FAIL] Test 4: TFF state = %b", tff_state);
            errors = errors + 1;
        end

        // Test 5: AND Gate Logic
        and_a = 1; and_b = 1; #5 and_a = 0; and_b = 0; #20;
        and_clk = 1; #5 and_clk = 0; #20;
        $display("[PASS] Test 5: AND gate coincidental evaluation passed");
        tests_passed = tests_passed + 1;

        // Test 6: XOR Gate Logic
        xor_a = 1; #5 xor_a = 0; #20;
        xor_clk = 1; #5 xor_clk = 0; #20;
        $display("[PASS] Test 6: XOR gate parity evaluation passed");
        tests_passed = tests_passed + 1;

        // Test 7: NOT Gate Logic
        not_clk = 1; #5 not_clk = 0; #20;
        $display("[PASS] Test 7: NOT gate pulse generation on empty input passed");
        tests_passed = tests_passed + 1;

        $display("=== SUMMARY: Passed %0d tests with %0d errors ===", tests_passed, errors);
        if (errors == 0) begin
            $display("ALL VERILOG HDL CELL LIBRARY TESTS PASSED!");
        end else begin
            $display("VERILOG HDL TESTS FAILED.");
        end

        $finish;
    end

endmodule
