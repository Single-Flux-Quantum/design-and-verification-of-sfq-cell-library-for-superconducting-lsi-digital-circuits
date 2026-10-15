"""
Comprehensive 15-Test Unit Suite for SIMIT-Nb03 SFQ Cell Library
================================================================
Reference: Gao et al. (SIMIT / CAS, Shanghai)
"Design and Verification of SFQ Cell Library for Superconducting LSI Digital Circuits"
IEEE Transactions on Applied Superconductivity, Vol. 31, No. 5, August 2021
Art. ID 1101105, DOI: 10.1109/TASC.2021.3062570

Test Suite Structure:
  1. test_01_jj_damping_and_beta_c: SIMIT-Nb03 junction parameters (Ic0=125 uA, beta_c ~ 1.0)
  2. test_02_jtl_pulse_propagation: JTL 2-JJ pulse propagation and 3.8 ps delay
  3. test_03_splitter_balanced_fanout: SPL31 3-JJ balanced fanout duplication
  4. test_04_confluence_buffer_merging: CB 5-JJ confluence buffer merging
  5. test_05_dff_clocked_storage: DFF 4-JJ single fluxon storage and release
  6. test_06_rdff_storage_and_clock_read: RDFF 11-JJ data write (AI) and clock interrogation (TI)
  7. test_07_rdff_reset_suppression: RDFF 11-JJ reset pulse (RI) clearing loop without AO emission
  8. test_08_tff_frequency_halving: TFF 6-JJ toggle flip-flop divide-by-2 frequency operation
  9. test_09_and_xor_not_logic_evaluation: Combinational gates (AND, XOR, NOT) truth evaluation
 10. test_10_ndro_retention_across_reads: NDRO 12-JJ non-destructive multi-read retention
 11. test_11_table_i_pscan2_progression: Table I 3-stage PSCAN2 margin optimization progression
 12. test_12_table_ii_cell_dimensions_and_jjs: Table II complete 17-cell dimensional verification
 13. test_13_moat_yield_recovery_simulation: Moat layout effect recovering chip yield from 0% to 83.3%
 14. test_14_pcm_process_spread_upward_shift: PCM +50% Jc spread causing upward bias operating shift
 15. test_15_triple_engine_parity_concordance: 7/7 Triple-Engine checks with 100% concordance
"""

import math
import numpy as np
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.spice_rcsj_solver import (
    JosephsonJunctionRCSJ,
    RDFFCellSimulator,
    SIMITCellLibraryRCSJSolver,
    PHI_0,
)
from src.hdl_digital_simulator import (
    SIMITCellLibraryCatalog,
    JTLCell,
    SplitterCell,
    ConfluenceBufferCell,
    DFFCell,
    RDFFCell,
    TFFCell,
    ANDCell,
    XORCell,
    NOTCell,
    NDROCell,
)
from src.cell_library_optimizer import CellLibraryOptimizer
from src.triple_engine_comparator import TripleEngineComparator


def test_01_jj_damping_and_beta_c():
    """Verify junction parameters and Stewart-McCumber critical damping."""
    jj = JosephsonJunctionRCSJ(ic=125e-6, cj=0.20e-12)
    assert abs(jj.beta_c - 1.0) < 0.05, f"Beta_c = {jj.beta_c:.3f} must be near 1.0"
    assert abs(jj.rn - 3.63) < 0.1, f"Rn = {jj.rn:.2f} must be ~ 3.63 ohms"
    return "PASS: SIMIT-Nb03 junction parameters and beta_c ~ 1.0 verified"


def test_02_jtl_pulse_propagation():
    """Verify JTL pulse propagation."""
    jtl = JTLCell()
    assert jtl.jjs == 2
    assert jtl.width_um == 60 and jtl.height_um == 30
    assert jtl.propagate(True) is True
    assert jtl.propagate(False) is False
    return "PASS: JTL 2-JJ pulse propagation and cell geometry verified"


def test_03_splitter_balanced_fanout():
    """Verify SPL31 1-to-2 splitter."""
    spl = SplitterCell("SPL31", jjs=3)
    assert spl.jjs == 3
    out1, out2 = spl.split(True)
    assert out1 is True and out2 is True
    return "PASS: SPL31 balanced fanout duplication verified"


def test_04_confluence_buffer_merging():
    """Verify Confluence Buffer merging."""
    cb = ConfluenceBufferCell("CB", jjs=5)
    assert cb.jjs == 5
    assert cb.merge(True, False) is True
    assert cb.merge(False, True) is True
    assert cb.merge(False, False) is False
    return "PASS: CB 5-JJ confluence merging verified"


def test_05_dff_clocked_storage():
    """Verify DFF data storage and clock interrogation."""
    dff = DFFCell()
    assert dff.jjs == 4
    dff.data_in()
    assert dff.state == 1
    assert dff.clock_in() is True
    assert dff.state == 0
    assert dff.clock_in() is False
    return "PASS: DFF 4-JJ clocked single fluxon storage verified"


def test_06_rdff_storage_and_clock_read():
    """Verify RDFF data write and clock readout."""
    sim = RDFFCellSimulator()
    sim.data_in()
    assert sim.stored_state == 1
    res = sim.clock_in()
    assert res["pulse_emitted"] is True
    assert sim.stored_state == 0
    return "PASS: RDFF data write (AI) and clock interrogation (TI) verified"


def test_07_rdff_reset_suppression():
    """Verify RDFF reset pulse suppression without output trigger."""
    sim = RDFFCellSimulator()
    sim.data_in()
    assert sim.stored_state == 1
    was_cleared = sim.reset_op()
    assert was_cleared is True
    assert sim.stored_state == 0

    res = sim.clock_in()
    assert res["pulse_emitted"] is False, "Output must NOT be emitted after reset"
    return "PASS: RDFF reset pulse (RI) clearing loop without AO emission verified"


def test_08_tff_frequency_halving():
    """Verify TFF divide-by-2 toggle operation."""
    tff = TFFCell()
    assert tff.jjs == 6
    out1 = tff.trigger()  # state 0 -> 1 (no out)
    assert out1 is False
    out2 = tff.trigger()  # state 1 -> 0 (out emitted)
    assert out2 is True
    return "PASS: TFF 6-JJ frequency divide-by-2 operation verified"


def test_09_and_xor_not_logic_evaluation():
    """Verify combinational gates: AND, XOR, NOT."""
    and_c = ANDCell()
    and_c.in_a(); and_c.in_b()
    assert and_c.clock_in() is True

    xor_c = XORCell()
    xor_c.in_a()
    assert xor_c.clock_in() is True

    not_c = NOTCell()
    assert not_c.clock_in() is True
    not_c.in_pulse()
    assert not_c.clock_in() is False
    return "PASS: Combinational gates (AND, XOR, NOT) logic evaluation verified"


def test_10_ndro_retention_across_reads():
    """Verify NDRO non-destructive multi-read retention."""
    ndro = NDROCell()
    assert ndro.jjs == 12
    ndro.set_in()
    # Read 5 times without destruction
    for _ in range(5):
        assert ndro.read_in() is True
    assert ndro.state == 1
    ndro.reset_in()
    assert ndro.read_in() is False
    return "PASS: NDRO 12-JJ non-destructive multi-read retention verified"


def test_11_table_i_pscan2_progression():
    """Verify Table I 3-stage PSCAN2 margin optimization progression."""
    opt = CellLibraryOptimizer()
    t1 = opt.get_table_i_progression()

    # Initial vs Case 3
    init_crit = t1["Initial"]["critical_margin_pct"]
    c3_crit = t1["Case3"]["critical_margin_pct"]
    assert init_crit == [-25.99, 13.56]
    assert c3_crit == [-34.79, 30.14]

    c3_xl = t1["Case3"]["xl_margin_pct"]
    assert c3_xl[1] == 71.19
    return "PASS: Table I 3-stage PSCAN2 optimization progression verified"


def test_12_table_ii_cell_dimensions_and_jjs():
    """Verify complete Table II 17-cell dimensional catalog."""
    catalog = SIMITCellLibraryCatalog()
    assert len(catalog.cells) == 17

    # Check widths and heights match 30 um grid multiples
    for name, cell in catalog.cells.items():
        assert cell.width_um % 30 == 0, f"{name} width {cell.width_um} not multiple of 30 um"
        assert cell.height_um % 30 == 0, f"{name} height {cell.height_um} not multiple of 30 um"
    return f"PASS: All {len(catalog.cells)} cells conform to 30 um grid multiples"


def test_13_moat_yield_recovery_simulation():
    """Verify moat layout effect on circuit yield."""
    opt = CellLibraryOptimizer()
    moat = opt.get_moat_yield_summary()
    assert moat["without_moats"]["V3"]["yield_pct"] == 0.0
    assert moat["with_moats"]["V3_prime"]["yield_pct"] == 83.3
    assert moat["with_moats"]["total_yield_pct"] == 94.4
    return "PASS: Moat layout effect recovering chip yield from 0% to 83.3% verified"


def test_14_pcm_process_spread_upward_shift():
    """Verify PCM +50% Jc spread causing upward bias operating shift."""
    opt = CellLibraryOptimizer()
    pcm = opt.evaluate_pcm_variation(9.0)
    assert pcm["shift_pct"] == 50.0
    assert pcm["upward_margin_shift"] is True
    return "PASS: PCM +50% Jc upward margin shift verified"


def test_15_triple_engine_parity_concordance():
    """Verify 7/7 Triple-Engine checks with 100% concordance."""
    comparator = TripleEngineComparator()
    report = comparator.run_all_checks()
    assert report["all_passed"] is True
    assert report["pass_count"] == 7
    return f"PASS: Triple-Engine Parity {report['pass_count']}/{report['total_count']} (100%) verified"


def run_all_tests():
    """Execute all 15 tests and output summary report."""
    tests = [
        ("Test 01: JJ Parameters and Damping", test_01_jj_damping_and_beta_c),
        ("Test 02: JTL Pulse Propagation", test_02_jtl_pulse_propagation),
        ("Test 03: Splitter Balanced Fanout", test_03_splitter_balanced_fanout),
        ("Test 04: Confluence Buffer Merging", test_04_confluence_buffer_merging),
        ("Test 05: DFF Clocked Storage", test_05_dff_clocked_storage),
        ("Test 06: RDFF Storage & Readout", test_06_rdff_storage_and_clock_read),
        ("Test 07: RDFF Reset Suppression", test_07_rdff_reset_suppression),
        ("Test 08: TFF Frequency Halving", test_08_tff_frequency_halving),
        ("Test 09: AND/XOR/NOT Logic Gates", test_09_and_xor_not_logic_evaluation),
        ("Test 10: NDRO Multi-Read Retention", test_10_ndro_retention_across_reads),
        ("Test 11: Table I PSCAN2 Progression", test_11_table_i_pscan2_progression),
        ("Test 12: Table II 17-Cell Catalog", test_12_table_ii_cell_dimensions_and_jjs),
        ("Test 13: Moat Yield Recovery", test_13_moat_yield_recovery_simulation),
        ("Test 14: PCM Process Spread Upward Shift", test_14_pcm_process_spread_upward_shift),
        ("Test 15: Triple-Engine Parity Concordance", test_15_triple_engine_parity_concordance),
    ]

    print("\n" + "=" * 75)
    print("RUNNING 15-TEST COMPREHENSIVE UNIT SUITE (SIMIT-Nb03 Library, Gao et al. 2021)")
    print("=" * 75)

    passed_count = 0
    for name, func in tests:
        try:
            msg = func()
            print(f"[PASS] {name:<42} | {msg}")
            passed_count += 1
        except Exception as e:
            print(f"[FAIL] {name:<42} | ERROR: {str(e)}")

    print("-" * 75)
    print(f"Total Test Results: {passed_count}/{len(tests)} PASSED ({(passed_count/len(tests))*100:.1f}%)")
    print("=" * 75)

    return passed_count == len(tests)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
