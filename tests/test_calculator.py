# -*- coding: utf-8 -*-
import pytest
from kug_dach.models import KugInput, Country, RegionDE, TaxClassDE
from kug_dach.calculator import calculate_kug, generate_matrix
from kug_dach.validator import ValidationError
from kug_dach.tables import BBG_WEST_2026, BBG_OST_2026, BBG_CH_2026, get_pauschaliertes_netto_de


class TestKugCalculatorDE:
    def test_standard_50_percent_with_child(self):
        # 4.000 € Brutto, 50% Ausfall -> Ist-Brutto 2.000 €
        inp = KugInput(soll_brutto=4000.0, ausfall_prozent=50.0, tax_class=TaxClassDE.I, has_child=True)
        res = calculate_kug(inp)
        assert res.soll_brutto_raw == 4000.0
        assert res.ist_brutto_raw == 2000.0
        assert res.leistungssatz_prozent == 67.0
        assert res.pauschal_soll_netto > res.pauschal_ist_netto
        assert res.netto_differenz == round(res.pauschal_soll_netto - res.pauschal_ist_netto, 2)
        assert res.kug_auszahlung == round(res.netto_differenz * 0.67, 2)
        assert res.gesamt_netto == round(res.pauschal_ist_netto + res.kug_auszahlung, 2)
        assert res.netto_verlust == round(res.pauschal_soll_netto - res.gesamt_netto, 2)
        assert res.ag_sv_aufwand > 0.0

    def test_standard_50_percent_without_child(self):
        inp = KugInput(soll_brutto=4000.0, ausfall_prozent=50.0, tax_class=TaxClassDE.I, has_child=False)
        res = calculate_kug(inp)
        assert res.leistungssatz_prozent == 60.0
        assert res.kug_auszahlung == round(res.netto_differenz * 0.60, 2)

    def test_kurzarbeit_null_100_percent(self):
        # 100 % Ausfall: Ist-Brutto 0 €, Ist-Netto 0 €, Gesamtauszahlung = reines KUG
        inp = KugInput(soll_brutto=3500.0, ausfall_prozent=100.0, tax_class=TaxClassDE.I, has_child=True)
        res = calculate_kug(inp)
        assert res.ist_brutto_capped == 0.0
        assert res.pauschal_ist_netto == 0.0
        assert res.netto_differenz == res.pauschal_soll_netto
        assert res.kug_auszahlung == round(res.pauschal_soll_netto * 0.67, 2)
        assert res.gesamt_netto == res.kug_auszahlung

    def test_zero_ausfall_0_percent(self):
        # 0 % Ausfall: KUG ist 0, Gesamtes Netto = Soll-Netto
        inp = KugInput(soll_brutto=3000.0, ausfall_prozent=0.0, tax_class=TaxClassDE.I)
        res = calculate_kug(inp)
        assert res.netto_differenz == 0.0
        assert res.kug_auszahlung == 0.0
        assert res.gesamt_netto == res.pauschal_soll_netto
        assert res.netto_verlust == 0.0
        assert res.ag_sv_aufwand == 0.0

    def test_bbg_capping_west(self):
        # Einkommen 10.000 € > BBG West 7.550 €
        inp = KugInput(soll_brutto=10000.0, ausfall_prozent=50.0, region=RegionDE.WEST)
        res = calculate_kug(inp)
        assert res.soll_brutto_raw == 10000.0
        assert res.soll_brutto_capped == BBG_WEST_2026
        assert res.bbg_applied == BBG_WEST_2026

    def test_bbg_capping_ost(self):
        inp = KugInput(soll_brutto=10000.0, ausfall_prozent=50.0, region=RegionDE.OST)
        res = calculate_kug(inp)
        assert res.soll_brutto_capped == BBG_OST_2026
        assert res.bbg_applied == BBG_OST_2026

    def test_tax_classes_netto_order(self):
        # Steuerklasse III (Splitting) sollte höheres Netto liefern als Steuerklasse V
        brutto = 4000.0
        netto_stkl3 = get_pauschaliertes_netto_de(brutto, TaxClassDE.III)
        netto_stkl1 = get_pauschaliertes_netto_de(brutto, TaxClassDE.I)
        netto_stkl5 = get_pauschaliertes_netto_de(brutto, TaxClassDE.V)
        assert netto_stkl3 > netto_stkl1 > netto_stkl5

    def test_church_tax_effect(self):
        brutto = 3500.0
        netto_no_kist = get_pauschaliertes_netto_de(brutto, TaxClassDE.I, church_tax=False)
        netto_with_kist = get_pauschaliertes_netto_de(brutto, TaxClassDE.I, church_tax=True)
        assert netto_no_kist > netto_with_kist

    def test_employer_topup_active(self):
        # Soll 4.000 €, 50% Ausfall, Topup auf 90% Nettoerhalt
        inp = KugInput(soll_brutto=4000.0, ausfall_prozent=50.0, employer_topup_percent=90.0)
        res = calculate_kug(inp)
        assert res.employer_topup_eur > 0.0
        target = round(0.90 * res.pauschal_soll_netto, 2)
        assert abs(res.gesamt_netto - target) <= 0.05

    def test_employer_topup_inactive_if_below(self):
        # Topup auf 50% wenn KUG+Lohn bereits > 80% erreicht
        inp = KugInput(soll_brutto=4000.0, ausfall_prozent=20.0, employer_topup_percent=50.0)
        res = calculate_kug(inp)
        assert res.employer_topup_eur == 0.0


class TestKugDACHCountries:
    def test_austria_kua_low_income(self):
        # Österreich KUA: <= 2.685 € Brutto -> 85 % Satz
        inp = KugInput(soll_brutto=2500.0, ausfall_prozent=50.0, country=Country.AT)
        res = calculate_kug(inp)
        assert res.country == Country.AT
        assert res.leistungssatz_prozent == 85.0
        assert res.kug_auszahlung > 0.0

    def test_austria_kua_high_income(self):
        # Österreich KUA: > 2.685 € Brutto -> 80 % Satz
        inp = KugInput(soll_brutto=3500.0, ausfall_prozent=50.0, country=Country.AT)
        res = calculate_kug(inp)
        assert res.leistungssatz_prozent == 80.0

    def test_switzerland_kae(self):
        # Schweiz KAE: 80 % des Verdienstausfalls
        inp = KugInput(soll_brutto=6000.0, ausfall_prozent=50.0, country=Country.CH)
        res = calculate_kug(inp)
        assert res.country == Country.CH
        assert res.leistungssatz_prozent == 80.0
        assert res.bbg_applied == BBG_CH_2026

    def test_switzerland_kae_capping(self):
        # Schweiz: Gedeckelt auf 12.350 CHF
        inp = KugInput(soll_brutto=15000.0, ausfall_prozent=50.0, country=Country.CH)
        res = calculate_kug(inp)
        assert res.soll_brutto_capped == BBG_CH_2026


class TestValidationAndMatrix:
    def test_negative_brutto_raises(self):
        with pytest.raises(ValidationError, match="nicht negativ"):
            calculate_kug(KugInput(soll_brutto=-1000.0))

    def test_invalid_ausfall_raises(self):
        with pytest.raises(ValidationError, match="zwischen 0"):
            calculate_kug(KugInput(soll_brutto=3000.0, ausfall_prozent=105.0))

    def test_invalid_topup_raises(self):
        with pytest.raises(ValidationError, match="zwischen 0 und 100"):
            calculate_kug(KugInput(soll_brutto=3000.0, employer_topup_percent=120.0))

    def test_generate_matrix(self):
        matrix = generate_matrix(4000.0)
        assert len(matrix) == 10
        # 10 % bis 100 %
        assert matrix[0]["ausfall_prozent"] == 10
        assert matrix[-1]["ausfall_prozent"] == 100
        # Bei höherem Ausfall sinkt das Gesamtnetto stetig
        assert matrix[0]["gesamt_netto"] > matrix[-1]["gesamt_netto"]
        # Bei 100% Ausfall ist KUG am höchsten
        assert matrix[-1]["kug_auszahlung"] > matrix[0]["kug_auszahlung"]
