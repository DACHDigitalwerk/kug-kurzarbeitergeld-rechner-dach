# -*- coding: utf-8 -*-
"""
Quickstart Example for kug_dach.
"""

from kug_dach import (
    calculate_kug,
    generate_matrix,
    KugInput,
    Country,
    TaxClassDE
)

def main():
    print("=== Quickstart: DACH Kurzarbeitergeld-Rechner 2026 ===")

    # 1. Deutschland KUG (4.000 € Brutto, 50% Ausfall, Steuerklasse I, mit Kind 67%)
    inp_de = KugInput(
        soll_brutto=4000.0,
        ausfall_prozent=50.0,
        country=Country.DE,
        tax_class=TaxClassDE.I,
        has_child=True
    )
    res_de = calculate_kug(inp_de)
    print(f"\n1. Deutschland KUG (50% Ausfall, 67% Leistungssatz):")
    print(f"   Soll-Brutto (Vollzeit):   {res_de.soll_brutto_capped:,.2f} €")
    print(f"   Ist-Brutto (KUG-Monat):   {res_de.ist_brutto_capped:,.2f} €")
    print(f"   Pauschal-Netto Soll:      {res_de.pauschal_soll_netto:,.2f} €")
    print(f"   Pauschal-Netto Ist:       {res_de.pauschal_ist_netto:,.2f} €")
    print(f"   Nettoentgeltdifferenz:    {res_de.netto_differenz:,.2f} €")
    print(f"   Kurzarbeitergeld (Staat): {res_de.kug_auszahlung:,.2f} €")
    print(f"   Ist-Lohn (Arbeitgeber):   {res_de.ist_netto_auszahlung:,.2f} €")
    print(f"   Gesamte Nettoauszahlung:  {res_de.gesamt_netto:,.2f} € ({res_de.netto_erhalt_prozent:.1f}% Erhalt)")
    print(f"   AG-Sozialversicherung:    {res_de.ag_sv_aufwand:,.2f} € (auf 80% fiktives Entgelt)")

    # 2. Mit tariflicher Arbeitgeber-Aufstockung auf 90%
    inp_topup = KugInput(
        soll_brutto=4000.0,
        ausfall_prozent=50.0,
        country=Country.DE,
        employer_topup_percent=90.0
    )
    res_topup = calculate_kug(inp_topup)
    print(f"\n2. Mit Arbeitgeber-Aufstockung auf 90%:")
    print(f"   KUG-Betrag:               {res_topup.kug_auszahlung:,.2f} €")
    print(f"   AG-Aufstockungszuschuss:  {res_topup.employer_topup_eur:,.2f} €")
    print(f"   Gesamtauszahlung:         {res_topup.gesamt_netto:,.2f} € ({res_topup.netto_erhalt_prozent:.1f}% Erhalt)")

    # 3. Österreich KUA (AMS)
    inp_at = KugInput(soll_brutto=3000.0, ausfall_prozent=50.0, country=Country.AT)
    res_at = calculate_kug(inp_at)
    print(f"\n3. Österreich KUA (AMS 80% Nettoersatz):")
    print(f"   Gesamtauszahlung:         {res_at.gesamt_netto:,.2f} €")

if __name__ == "__main__":
    main()
