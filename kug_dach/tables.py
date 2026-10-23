# -*- coding: utf-8 -*-
"""
kug_dach.tables
~~~~~~~~~~~~~~~
Beitragsbemessungsgrenzen 2026 und KUG-Pauschaltabellen-Algorithmus.
"""

from .models import TaxClassDE

# Gesetzliche Beitragsbemessungsgrenzen Arbeitslosenversicherung 2026
BBG_WEST_2026 = 7550.0  # Alte Bundesländer: 7.550 € / Monat
BBG_OST_2026 = 7450.0   # Neue Bundesländer: 7.450 € / Monat
BBG_CH_2026 = 12350.0   # Schweiz AVIG: 148.200 CHF / 12 = 12.350 CHF / Monat


def get_pauschaliertes_netto_de(brutto: float, tax_class: TaxClassDE, church_tax: bool = False) -> float:
    """
    Berechnet das pauschalierte Nettoentgelt nach § 106 SGB III & KUG-Verordnung 2026.
    Abzüge:
    1. Sozialversicherungspauschale von 20 %
    2. Lohnsteuer nach Steuerklasse (I bis VI)
    3. Solidaritätszuschlag (falls über Freigrenze)
    4. Ggf. Kirchensteuer (9 %)
    """
    if brutto <= 0:
        return 0.0

    # 1. Gesetzliche 20 % Sozialversicherungspauschale (§ 153 SGB III)
    sv_pauschale = brutto * 0.20
    taxable = max(0.0, brutto - sv_pauschale)

    # 2. Lohnsteuer-Pauschale nach Steuerklasse
    lst = 0.0
    tc_val = tax_class.value if isinstance(tax_class, TaxClassDE) else str(tax_class)

    if tc_val in ("1", "4"):  # Ledige oder Ehegatten Faktor 1:1
        if taxable > 1050.0:
            lst = max(0.0, (taxable - 1050.0) * 0.26)
    elif tc_val == "2":  # Alleinerziehend (höherer Freibetrag)
        if taxable > 1400.0:
            lst = max(0.0, (taxable - 1400.0) * 0.24)
    elif tc_val == "3":  # Günstigste Steuerklasse
        if taxable > 1800.0:
            lst = max(0.0, (taxable - 1800.0) * 0.17)
    elif tc_val == "5":  # Höchste Progression
        lst = taxable * 0.35
    elif tc_val == "6":  # Zweitjob ohne Grundfreibetrag
        lst = taxable * 0.38
    else:
        if taxable > 1050.0:
            lst = max(0.0, (taxable - 1050.0) * 0.26)

    if church_tax:
        lst += lst * 0.09

    netto = max(0.0, brutto - sv_pauschale - lst)
    return round(netto, 2)
