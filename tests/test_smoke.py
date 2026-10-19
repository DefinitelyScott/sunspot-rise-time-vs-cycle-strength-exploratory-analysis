"""End to end: the real analysis runs and writes every promised output."""

from __future__ import annotations

from sunspot_cycles.report import format_summary, run_analysis


def test_run_analysis_writes_outputs(tmp_path):
    results = run_analysis(tmp_path)
    for name in (
        "cycles.csv",
        "results.json",
        "fig1_cycles.png",
        "fig2_rise_vs_amplitude.png",
        "fig3_sensitivity.png",
    ):
        assert (tmp_path / name).stat().st_size > 0
    assert "rise_years" in format_summary(results)
