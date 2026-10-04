from accounting_intel.reporting import executive_report_html, write_executive_report


def test_executive_report_exposes_decision_signals(tmp_path):
    html = executive_report_html()
    assert "Priority clients" in html
    assert "C002" in html
    assert "Warehouse reconciliation" in html
    assert "PASS" in html
    assert "Manager capacity" in html

    path = write_executive_report(tmp_path / "report.html")
    assert path.exists()
    assert path.read_text(encoding="utf-8") == html
