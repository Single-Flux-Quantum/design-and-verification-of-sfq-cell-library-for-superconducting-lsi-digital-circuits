"""
High-Resolution Plot and Benchmark Generator for SIMIT-Nb03 Cell Library
========================================================================
Reference: Gao et al. (SIMIT / CAS, Shanghai)
"Design and Verification of SFQ Cell Library for Superconducting LSI Digital Circuits"
IEEE Transactions on Applied Superconductivity, Vol. 31, No. 5, August 2021
Art. ID 1101105, DOI: 10.1109/TASC.2021.3062570

Strictly Adheres to the "1 Image Per Figure / Panel Standard":
- Every figure is a single dedicated panel (NO composite subplots).
- Crisp 300 DPI resolution, professional typography, tailored color palettes.
- Outputs 8 standalone publication-quality figures to docs/figures/
- Outputs benchmark JSON metrics to docs/tables/
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path
import sys

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.spice_rcsj_solver import SIMITCellLibraryRCSJSolver, RDFFCellSimulator
from src.hdl_digital_simulator import SIMITCellLibraryCatalog
from src.cell_library_optimizer import CellLibraryOptimizer
from src.triple_engine_comparator import TripleEngineComparator

# Output directories
FIGURES_DIR = PROJECT_ROOT / "docs" / "figures"
TABLES_DIR = PROJECT_ROOT / "docs" / "tables"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

# Plot styling configuration
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 14,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})


def plot_fig1_optimization_flow():
    """Figure 1: Closed-Loop SFQ Cell Design & Multi-Target Optimization Flow (Fig. 1)."""
    fig, ax = plt.subplots(figsize=(9, 6.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")

    ax.text(5.0, 6.6, "SIMIT-Nb03 Cell Design & Multi-Target Optimization Flow",
            ha="center", va="center", fontsize=14, fontweight="bold", color="#0f172a")
    ax.text(5.0, 6.2, "Closed-Loop Procedure: State Machine -> Schematic -> PSCAN2 Margin Optimization -> Layout",
            ha="center", va="center", fontsize=10, fontstyle="italic", color="#475569")

    # Flowchart boxes
    steps = [
        (1.0, 4.8, 2.2, 0.9, "1. Logic Function\nState Machine (FSM)", "#dbeafe", "#1d4ed8"),
        (3.9, 4.8, 2.2, 0.9, "2. Circuit Schematic\n& Initial Sizing", "#fef3c7", "#d97706"),
        (6.8, 4.8, 2.2, 0.9, "3. PSCAN2 Simulation\n(DUT + JTL Buffers)", "#dcfce7", "#15803d"),
        (6.8, 3.0, 2.2, 0.9, "4. Multi-Target Opt.\n(XI, XJ, XL, Critical)", "#fed7aa", "#c2410c"),
        (3.9, 3.0, 2.2, 0.9, "5. Layout Design\n(30 um Grid & Moats)", "#e9d5ff", "#7c3aed"),
        (1.0, 3.0, 2.2, 0.9, "6. Model Extraction\n(Verilog + Timing)", "#f1f5f9", "#475569"),
    ]

    for x, y, w, h, label, fc, ec in steps:
        box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15", fc=fc, ec=ec, lw=1.8)
        ax.add_patch(box)
        ax.text(x + w/2, y + h/2, label, ha="center", va="center", fontsize=9, fontweight="bold", color="#0f172a")

    # Forward arrows
    ax.annotate("", xy=(3.8, 5.25), xytext=(3.3, 5.25), arrowprops=dict(arrowstyle="->", color="#1e40af", lw=2))
    ax.annotate("", xy=(6.7, 5.25), xytext=(6.2, 5.25), arrowprops=dict(arrowstyle="->", color="#1e40af", lw=2))
    ax.annotate("", xy=(7.9, 4.0), xytext=(7.9, 4.7), arrowprops=dict(arrowstyle="->", color="#1e40af", lw=2))
    ax.annotate("", xy=(6.2, 3.45), xytext=(6.7, 3.45), arrowprops=dict(arrowstyle="->", color="#1e40af", lw=2))
    ax.annotate("", xy=(3.3, 3.45), xytext=(3.8, 3.45), arrowprops=dict(arrowstyle="->", color="#1e40af", lw=2))

    # Optimization feedback loop
    ax.annotate("Margin Re-Check Loop", xy=(5.0, 4.7), xytext=(5.0, 4.0),
                arrowprops=dict(arrowstyle="->", color="#dc2626", lw=1.8, linestyle="--"),
                ha="center", fontsize=8.5, fontweight="bold", color="#dc2626")

    # Bottom summary banner
    banner = patches.FancyBboxPatch((1.0, 0.8), 8.0, 1.4, boxstyle="round,pad=0.2",
                                    fc="#f8fafc", ec="#94a3b8", lw=1.5)
    ax.add_patch(banner)
    ax.text(5.0, 1.8, "Key Optimization Criteria across 3 Stages (Table I):",
            ha="center", va="center", fontsize=9.5, fontweight="bold", color="#1e293b")
    ax.text(5.0, 1.3, "- Case 1: Global parameter centering (XI bias, XJ critical current, XL inductance)\n- Case 2: Individual critical element (JR3) margin expansion to eliminate weakest link\n- Case 3: Global maximization across all component parameters (Critical Margin -> [-34.8%, +30.1%])",
            ha="center", va="center", fontsize=8.5, color="#334155")

    out_path = FIGURES_DIR / "fig1_cell_design_and_optimization_flow.png"
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path.name}")


def plot_fig2_rdff_schematic_state_machine():
    """Figure 2: Resettable D-Flip-Flop (RDFF) State Machine & Circuit Topology (Fig. 2)."""
    fig, ax = plt.subplots(figsize=(9, 6.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")

    ax.text(5.0, 6.6, "Resettable D-Flip-Flop (RDFF) Architecture & State Transitions",
            ha="center", va="center", fontsize=14, fontweight="bold", color="#0f172a")
    ax.text(5.0, 6.2, "Storage SQUID Loop (JA2, LA2, LO3, JO3, JO2) & Reset Branch (J4, JR1, JR2, JR3)",
            ha="center", va="center", fontsize=10, fontstyle="italic", color="#475569")

    # State Machine Diagram (Left)
    sm_box = patches.FancyBboxPatch((0.5, 1.2), 4.2, 4.6, boxstyle="round,pad=0.2",
                                    fc="#eff6ff", ec="#2563eb", lw=1.8)
    ax.add_patch(sm_box)
    ax.text(2.6, 5.4, "State Transition Diagram", ha="center", va="center",
            fontsize=11, fontweight="bold", color="#1e40af")

    # Two states: State 0 and State 1
    c0 = patches.Circle((1.7, 3.3), 0.65, fc="#ffffff", ec="#1e3a8a", lw=2)
    c1 = patches.Circle((3.5, 3.3), 0.65, fc="#ffffff", ec="#1e3a8a", lw=2)
    ax.add_patch(c0)
    ax.add_patch(c1)
    ax.text(1.7, 3.3, "State 0\n(Empty)", ha="center", va="center", fontsize=9, fontweight="bold")
    ax.text(3.5, 3.3, "State 1\n(Phi0)", ha="center", va="center", fontsize=9, fontweight="bold")

    # State machine arrows
    # AI: 0 -> 1
    ax.annotate("AI (Data In)", xy=(2.9, 3.6), xytext=(2.3, 3.6),
                arrowprops=dict(arrowstyle="->", color="#16a34a", lw=1.8),
                fontsize=8.5, fontweight="bold", color="#15803d")
    # TI: 1 -> 0 with AO
    ax.annotate("TI / AO (Clk / Out)", xy=(2.3, 3.0), xytext=(2.9, 3.0),
                arrowprops=dict(arrowstyle="->", color="#dc2626", lw=1.8),
                fontsize=8.5, fontweight="bold", color="#b91c1c")
    # RI: 1 -> 0 without AO
    ax.annotate("RI (Reset)", xy=(2.0, 2.5), xytext=(3.2, 2.3),
                arrowprops=dict(arrowstyle="->", color="#7c3aed", lw=1.8, linestyle="--"),
                fontsize=8.5, fontweight="bold", color="#6d28d9")

    # Schematic & Component Specs (Right)
    sch_box = patches.FancyBboxPatch((5.1, 1.2), 4.4, 4.6, boxstyle="round,pad=0.2",
                                     fc="#fdf4ff", ec="#c026d3", lw=1.8)
    ax.add_patch(sch_box)
    ax.text(7.3, 5.4, "Circuit Component Topology", ha="center", va="center",
            fontsize=11, fontweight="bold", color="#86198f")

    specs = [
        "- Junction Count: 11 JJs (60 um x 90 um)",
        "- Storage Loop: JA2 + LA2 + LO3 + JO3 + JO2",
        "- Storage Loop Inductance: L_loop = 12.0 pH",
        "- Reset Branch: J4 (Input) + JR1 (Escape JJ)",
        "- Reset Summing: JR2 + JR3 (Reset JJ)",
        "- Output Decision JJ: JO3 (Ic = 200 uA)",
        "- Clock Interrogation: JT1 + JT2 (TI -> AO)",
        "- Measured Bias Margin: -28% to +52% (Table II)",
        "- Optimized Critical Margin: [-34.8%, +30.1%]"
    ]
    for idx, sp in enumerate(specs):
        ax.text(5.4, 4.8 - idx * 0.4, sp, fontsize=8.5, color="#4a044e")

    out_path = FIGURES_DIR / "fig2_rdff_schematic_and_state_machine.png"
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path.name}")


def plot_fig3_dut_simulation_testbench():
    """Figure 3: DUT Simulation Testbench Configuration with 2-Stage JTL Buffers (Fig. 3)."""
    fig, ax = plt.subplots(figsize=(9, 5.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")

    ax.text(5.0, 6.6, "Simulation Configuration for SFQ Library Cell Design",
            ha="center", va="center", fontsize=14, fontweight="bold", color="#0f172a")
    ax.text(5.0, 6.2, "2-Stage Standard JTL Input/Output Buffering for Realistic Loading & Margin Extraction",
            ha="center", va="center", fontsize=10, fontstyle="italic", color="#475569")

    # DUT Central Box
    dut_box = patches.FancyBboxPatch((3.7, 2.2), 2.6, 3.0, boxstyle="round,pad=0.2",
                                     fc="#fef2f2", ec="#dc2626", lw=2.2)
    ax.add_patch(dut_box)
    ax.text(5.0, 4.3, "Design Under Test\n(DUT Cell)", ha="center", va="center",
            fontsize=11, fontweight="bold", color="#991b1b")
    ax.text(5.0, 3.2, "(RDFF, DFF, TFF,\nAND, XOR, NDRO)", ha="center", va="center",
            fontsize=9, color="#7f1d1d")

    # Input JTL Buffers (Left)
    jtl_in1 = patches.FancyBboxPatch((0.8, 3.8), 2.1, 1.2, boxstyle="round,pad=0.1",
                                     fc="#eff6ff", ec="#2563eb", lw=1.8)
    jtl_in2 = patches.FancyBboxPatch((0.8, 2.2), 2.1, 1.2, boxstyle="round,pad=0.1",
                                     fc="#eff6ff", ec="#2563eb", lw=1.8)
    ax.add_patch(jtl_in1)
    ax.add_patch(jtl_in2)
    ax.text(1.85, 4.4, "Input JTL Stage 1\n& Stage 2 (Data)", ha="center", va="center",
            fontsize=8.5, fontweight="bold", color="#1e40af")
    ax.text(1.85, 2.8, "Input JTL Stage 1\n& Stage 2 (Clock)", ha="center", va="center",
            fontsize=8.5, fontweight="bold", color="#1e40af")

    # Arrows into DUT
    ax.annotate("", xy=(3.6, 4.4), xytext=(3.0, 4.4), arrowprops=dict(arrowstyle="->", color="#1d4ed8", lw=2))
    ax.annotate("", xy=(3.6, 2.8), xytext=(3.0, 2.8), arrowprops=dict(arrowstyle="->", color="#1d4ed8", lw=2))

    # Output JTL Buffers (Right)
    jtl_out = patches.FancyBboxPatch((7.1, 3.0), 2.1, 1.4, boxstyle="round,pad=0.1",
                                     fc="#f0fdf4", ec="#16a34a", lw=1.8)
    ax.add_patch(jtl_out)
    ax.text(8.15, 3.7, "Output JTL Stage 1\n& Stage 2 (Load)", ha="center", va="center",
            fontsize=8.5, fontweight="bold", color="#15803d")

    # Arrow from DUT to Output JTL
    ax.annotate("", xy=(7.0, 3.7), xytext=(6.4, 3.7), arrowprops=dict(arrowstyle="->", color="#15803d", lw=2))

    # Bottom notes
    note = patches.FancyBboxPatch((1.2, 0.7), 7.6, 1.0, boxstyle="round,pad=0.2",
                                 fc="#f8fafc", ec="#cbd5e1", lw=1.2)
    ax.add_patch(note)
    ax.text(5.0, 1.2, "Isolation & Reflection Protection: Standard 2-stage JTL buffers at all ports isolate\nthe DUT from external driver impedances and ensure realistic SFQ switching waveforms.",
            ha="center", va="center", fontsize=8.5, color="#334155")

    out_path = FIGURES_DIR / "fig3_dut_simulation_testbench_configuration.png"
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path.name}")


def plot_fig4_dff_layout_variants():
    """Figure 4: 3 Layout Variants of DFF with Different I/O Port Positions (Fig. 4)."""
    fig, ax = plt.subplots(figsize=(9, 5.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")

    ax.text(5.0, 6.6, "D-Flip-Flop Standard Cell Layout Variants (60 um x 60 um)",
            ha="center", va="center", fontsize=14, fontweight="bold", color="#0f172a")
    ax.text(5.0, 6.2, "Three Layouts Providing Flexible Port Placement for Automated Place-and-Route",
            ha="center", va="center", fontsize=10, fontstyle="italic", color="#475569")

    # 3 Variants
    variants = [
        (1.0, 2.0, "DFF Variant 1", "Clock: Top\nData: Left\nOut: Right", "#dbeafe", "#1d4ed8"),
        (4.0, 2.0, "DFF Variant 2", "Clock: Left\nData: Bottom\nOut: Right", "#fef3c7", "#d97706"),
        (7.0, 2.0, "DFF Variant 3", "Clock: Bottom\nData: Left\nOut: Top", "#dcfce7", "#15803d"),
    ]

    for x, y, title, desc, fc, ec in variants:
        box = patches.FancyBboxPatch((x, y), 2.2, 3.2, boxstyle="round,pad=0.2", fc=fc, ec=ec, lw=2)
        ax.add_patch(box)
        ax.text(x + 1.1, y + 2.7, title, ha="center", va="center", fontsize=10.5, fontweight="bold", color="#0f172a")
        ax.text(x + 1.1, y + 1.5, desc, ha="center", va="center", fontsize=9, color="#334155")
        ax.text(x + 1.1, y + 0.5, "Grid: 60x60 um\n4 JJs | 4 um Ports", ha="center", va="center",
                fontsize=8, fontstyle="italic", color="#64748b")

    # Annotations on bias and port standards
    ax.text(5.0, 1.0, "Universal Compatibility: Surrounding DC bias rings automatically connect when cells are tiled.",
            ha="center", va="center", fontsize=9.5, fontweight="bold", color="#1e40af",
            bbox=dict(boxstyle="round,pad=0.3", fc="#eff6ff", ec="#3b82f6", lw=1))

    out_path = FIGURES_DIR / "fig4_dff_layout_and_io_port_variants.png"
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path.name}")


def plot_fig5_tff_moat_arrangements():
    """Figure 5: TFF Moat Layout Arrangements (Fig. 5)."""
    fig, ax = plt.subplots(figsize=(9, 5.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")

    ax.text(5.0, 6.6, "Toggle Flip-Flop (TFF) Moat Layout Arrangements for Flux Trapping",
            ha="center", va="center", fontsize=14, fontweight="bold", color="#0f172a")
    ax.text(5.0, 6.2, "Comparison between Layouts without Moats (V1-V3) and with Moats (V1'-V3')",
            ha="center", va="center", fontsize=10, fontstyle="italic", color="#475569")

    # Left Container: Without Moats
    box_no = patches.FancyBboxPatch((0.8, 1.5), 3.9, 4.2, boxstyle="round,pad=0.2",
                                    fc="#fef2f2", ec="#dc2626", lw=2)
    ax.add_patch(box_no)
    ax.text(2.75, 5.3, "Without Moats (V1, V2, V3)", ha="center", va="center",
            fontsize=11, fontweight="bold", color="#991b1b")
    ax.text(2.75, 4.4, "- Continuous ground plane\n- Highly vulnerable to flux trapping\n- Variant V3: 0/4 Working Chips (0% Yield)",
            ha="center", va="center", fontsize=9, color="#7f1d1d")
    ax.text(2.75, 2.6, "V3 Yield = 0%\n(Catastrophic Failure)", ha="center", va="center",
            fontsize=11, fontweight="bold", color="#dc2626",
            bbox=dict(boxstyle="round,pad=0.3", fc="#fee2e2", ec="#ef4444", lw=1.5))

    # Right Container: With Moats
    box_yes = patches.FancyBboxPatch((5.3, 1.5), 3.9, 4.2, boxstyle="round,pad=0.2",
                                     fc="#f0fdf4", ec="#16a34a", lw=2)
    ax.add_patch(box_yes)
    ax.text(7.25, 5.3, "With Moats (V1', V2', V3')", ha="center", va="center",
            fontsize=11, fontweight="bold", color="#15803d")
    ax.text(7.25, 4.4, "- Dedicated holes in ground plane\n- Traps stray magnetic flux quanta\n- Variant V3': 5/6 Working Chips (83.3% Yield)",
            ha="center", va="center", fontsize=9, color="#14532d")
    ax.text(7.25, 2.6, "V3' Yield = 83.3%\n(Full Recovery)", ha="center", va="center",
            fontsize=11, fontweight="bold", color="#15803d",
            bbox=dict(boxstyle="round,pad=0.3", fc="#dcfce7", ec="#22c55e", lw=1.5))

    out_path = FIGURES_DIR / "fig5_tff_moat_arrangements_v1_v3.png"
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path.name}")


def plot_fig6_chip_to_chip_margins():
    """Figure 6: Measured Bias Current Margins Across Multiple Chips (Fig. 6)."""
    fig, ax = plt.subplots(figsize=(8.8, 5.8))

    # Chips tested in Fig. 6 for DFF (3 chips) and XOR (4 chips)
    categories = ["DFF (Sim)", "DFF (Chip 1)", "DFF (Chip 2)", "DFF (Chip 3)",
                  "XOR (Sim)", "XOR (Chip 1)", "XOR (Chip 2)", "XOR (Chip 3)", "XOR (Chip 4)"]
    lows = [-54.0, -48.0, -52.0, -45.0, -24.0, -20.0, -22.0, -18.0, -21.0]
    highs = [76.0, 68.0, 72.0, 65.0, 46.0, 42.0, 44.0, 38.0, 41.0]

    y_pos = np.arange(len(categories))

    for i in range(len(categories)):
        span = highs[i] - lows[i]
        c = "#2563eb" if "DFF" in categories[i] else "#d97706"
        ax.barh(y_pos[i], span, left=lows[i], height=0.55, color=c, alpha=0.85,
                edgecolor="#0f172a", lw=1.2)
        ax.text(highs[i] + 2.0, y_pos[i], f"[{lows[i]:.0f}%, {highs[i]:.0f}%]",
                va="center", fontsize=8.5, fontweight="bold", color=c)

    ax.axvline(0, color="#dc2626", linestyle="--", lw=1.5, label="Nominal Bias Current (0%)")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(categories, fontweight="bold")
    ax.invert_yaxis()
    ax.set_xlabel("DC Bias Current Margin Span (%)")
    ax.set_title("Figure 6: Chip-to-Chip Experimental Bias Current Margin Distributions",
                 fontweight="bold", pad=12)
    ax.set_xlim(-70, 95)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="lower right", framealpha=0.92)

    out_path = FIGURES_DIR / "fig6_chip_to_chip_margin_distributions.png"
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path.name}")


def plot_fig7_tff_moat_yield_comparison():
    """Figure 7: Quantitative Experimental Yield Comparison with vs without Moats (Fig. 7)."""
    fig, ax = plt.subplots(figsize=(8.8, 5.8))

    labels = ["Variant V1\n(Port config 1)", "Variant V2\n(Port config 2)", "Variant V3\n(Port config 3)", "Overall\nAverage Yield"]
    x = np.arange(len(labels))
    width = 0.35

    yield_without = [100.0, 100.0, 0.0, 66.7]
    yield_with = [100.0, 100.0, 83.3, 94.4]

    rects1 = ax.bar(x - width/2, yield_without, width, label="Without Moats (V1, V2, V3 - 4 Chips)",
                    color="#f87171", edgecolor="#b91c1c", lw=1.5)
    rects2 = ax.bar(x + width/2, yield_with, width, label="With Moats (V1', V2', V3' - 6 Chips)",
                    color="#4ade80", edgecolor="#15803d", lw=1.5)

    # Annotate bar values
    for rect in rects1:
        h = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2, h + 2.0, f"{h:.1f}%",
                ha="center", va="bottom", fontsize=9, fontweight="bold", color="#991b1b")
    for rect in rects2:
        h = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2, h + 2.0, f"{h:.1f}%",
                ha="center", va="bottom", fontsize=9, fontweight="bold", color="#166534")

    ax.set_ylabel("Experimental Functional Yield (%)", fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontweight="bold")
    ax.set_ylim(0, 115)
    ax.set_title("Figure 7: Experimental Yield Enhancement via Moat Ground-Plane Openings",
                 fontweight="bold", pad=12)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper right", framealpha=0.92)

    out_path = FIGURES_DIR / "fig7_tff_moat_yield_experimental_comparison.png"
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path.name}")


def plot_fig8_ndro_precision_margins():
    """Figure 8: High-Resolution Bias Current Margins (NDRO vs NDRO1, Fig. 8)."""
    fig, ax = plt.subplots(figsize=(8.8, 5.8))

    chips = ["Simulation", "Chip 1", "Chip 2", "Chip 3", "Chip 4", "Chip 5"]
    x = np.arange(len(chips))
    width = 0.35

    # Margins for NDRO
    ndro_low = [-18.0, -16.0, -17.5, -15.0, -18.0, -16.5]
    ndro_high = [36.0, 34.0, 35.0, 32.0, 36.0, 34.5]
    ndro_spans = [h - l for l, h in zip(ndro_low, ndro_high)]

    # Margins for NDRO1
    ndro1_low = [-12.0, -11.0, 0.0, -10.5, -12.0, -11.5]
    ndro1_high = [46.0, 44.5, 0.0, 42.0, 45.0, 46.0]
    ndro1_spans = [h - l for l, h in zip(ndro1_low, ndro1_high)]

    rects1 = ax.bar(x - width/2, ndro_spans, width, label="NDRO (Initial Layout)",
                    color="#93c5fd", edgecolor="#1d4ed8", lw=1.2)
    rects2 = ax.bar(x + width/2, ndro1_spans, width, label="NDRO1 (Optimized Layout)",
                    color="#c084fc", edgecolor="#7e22ce", lw=1.2)

    # Annotate Chip 2 failure for NDRO1 under fine scan
    ax.annotate("Failed on fine scan", xy=(2 + width/2, 5), xytext=(2 + width/2, 25),
                arrowprops=dict(arrowstyle="->", color="#dc2626", lw=1.5),
                ha="center", fontsize=8, fontweight="bold", color="#dc2626")

    ax.set_ylabel("Total Margin Width (%)", fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(chips, fontweight="bold")
    ax.set_ylim(0, 75)
    ax.set_title("Figure 8: High-Resolution Bias Current Margin Scan (NDRO vs NDRO1)",
                 fontweight="bold", pad=12)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper right", framealpha=0.92)

    out_path = FIGURES_DIR / "fig8_ndro_vs_ndro1_precision_margins.png"
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path.name}")


def export_benchmark_tables():
    """Exports structured benchmark JSON metrics."""
    comparator = TripleEngineComparator()
    report = comparator.run_all_checks()
    solver = SIMITCellLibraryRCSJSolver()
    opt = CellLibraryOptimizer()

    data = {
        "paper_metadata": {
            "title": "Design and Verification of SFQ Cell Library for Superconducting LSI Digital Circuits",
            "authors": "Xiaoping Gao, Qi Qiao, Mingliang Wang, Minghui Niu, Huanli Liu, Masaaki Maezawa, Jie Ren, Zhen Wang",
            "institution": "Shanghai Institute of Microsystem and Information Technology (SIMIT), Chinese Academy of Sciences (CAS)",
            "journal": "IEEE Transactions on Applied Superconductivity",
            "volume": 31,
            "issue": 5,
            "year": 2021,
            "article_id": "1101105",
            "doi": "10.1109/TASC.2021.3062570"
        },
        "fabrication_process": {
            "name": "SIMIT-Nb03",
            "jc_nominal_ka_cm2": 6.0,
            "mask_levels": 10,
            "ground_planes": 1,
            "wiring_layers": 2,
            "unit_grid_size_um": "30 x 30",
            "io_port_width_um": 4.0,
            "london_penetration_depth_nm": 90.0
        },
        "table_i_rdff_optimization": opt.get_table_i_progression(),
        "table_ii_standard_cells": solver.TABLE_II_GROUND_TRUTH,
        "moat_yield_summary": opt.get_moat_yield_summary(),
        "triple_engine_parity": {
            "all_passed": report["all_passed"],
            "pass_count": report["pass_count"],
            "total_count": report["total_count"],
            "pass_rate_pct": report["pass_rate_pct"],
            "checks": report["summary"]
        }
    }

    out_file = TABLES_DIR / "simit_cell_library_benchmarks.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Exported: {out_file.name}")


def main():
    print("\n" + "=" * 75)
    print("GENERATING 8 STANDALONE 300-DPI PUBLICATION FIGURES & BENCHMARK JSON (SIMIT-Nb03)")
    print("=" * 75)

    plot_fig1_optimization_flow()
    plot_fig2_rdff_schematic_state_machine()
    plot_fig3_dut_simulation_testbench()
    plot_fig4_dff_layout_variants()
    plot_fig5_tff_moat_arrangements()
    plot_fig6_chip_to_chip_margins()
    plot_fig7_tff_moat_yield_comparison()
    plot_fig8_ndro_precision_margins()

    export_benchmark_tables()
    print("=" * 75)
    print("ALL 8 FIGURES AND BENCHMARK TABLES GENERATED SUCCESSFULLY!")
    print("=" * 75)


if __name__ == "__main__":
    main()
