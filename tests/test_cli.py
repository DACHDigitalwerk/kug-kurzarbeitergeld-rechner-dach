# -*- coding: utf-8 -*-
import json
import pytest
from kug_dach.cli import main


class TestCLI:
    def test_cli_help(self, capsys):
        with pytest.raises(SystemExit) as exc:
            main(["--help"])
        assert exc.value.code == 0
        out, _ = capsys.readouterr()
        assert "dach-kug" in out
        assert "--brutto" in out

    def test_cli_basic_run(self, capsys):
        code = main(["--brutto", "4000", "--ausfall", "50"])
        assert code == 0
        out, _ = capsys.readouterr()
        assert "KURZARBEITERGELD-RECHNER 2026" in out
        assert "KURZARBEITERGELD (KUG)" in out
        assert "GESAMTE NETTOAUSZAHLUNG" in out

    def test_cli_json_output(self, capsys):
        code = main(["--brutto", "4000", "--ausfall", "50", "--json"])
        assert code == 0
        out, _ = capsys.readouterr()
        data = json.loads(out)
        assert data["soll_brutto_raw"] == 4000.0
        assert data["ausfall_prozent"] == 50.0
        assert data["leistungssatz_prozent"] == 67.0
        assert data["kug_auszahlung"] > 0.0
        assert data["gesamt_netto"] > data["kug_auszahlung"]

    def test_cli_without_child(self, capsys):
        code = main(["--brutto", "3500", "--ausfall", "40", "--without-child", "--json"])
        assert code == 0
        out, _ = capsys.readouterr()
        data = json.loads(out)
        assert data["leistungssatz_prozent"] == 60.0

    def test_cli_markdown_output(self, capsys):
        code = main(["--brutto", "4500", "--ausfall", "60", "--markdown"])
        assert code == 0
        out, _ = capsys.readouterr()
        assert "# Kurzarbeitergeld (KUG) Monats-Abrechnungsnachweis 2026" in out
        assert "Nettoentgeltdifferenz" in out

    def test_cli_matrix_output(self, capsys):
        code = main(["--brutto", "3800", "--matrix"])
        assert code == 0
        out, _ = capsys.readouterr()
        assert "KURZARBEIT AUSFALL-MATRIX 2026" in out
        assert "10 %" in out
        assert "100 %" in out

    def test_cli_matrix_json(self, capsys):
        code = main(["--brutto", "3800", "--matrix", "--json"])
        assert code == 0
        out, _ = capsys.readouterr()
        data = json.loads(out)
        assert isinstance(data, list)
        assert len(data) == 10

    def test_cli_country_austria(self, capsys):
        code = main(["--brutto", "2500", "--country", "AT", "--json"])
        assert code == 0
        out, _ = capsys.readouterr()
        data = json.loads(out)
        assert data["country"] == "AT"
        assert data["leistungssatz_prozent"] == 85.0

    def test_cli_country_switzerland(self, capsys):
        code = main(["--brutto", "8000", "--country", "CH", "--json"])
        assert code == 0
        out, _ = capsys.readouterr()
        data = json.loads(out)
        assert data["country"] == "CH"
        assert data["leistungssatz_prozent"] == 80.0

    def test_cli_with_topup(self, capsys):
        code = main(["--brutto", "4000", "--ausfall", "50", "--topup", "90", "--json"])
        assert code == 0
        out, _ = capsys.readouterr()
        data = json.loads(out)
        assert data["employer_topup_eur"] > 0.0
        assert data["netto_erhalt_prozent"] >= 89.9
