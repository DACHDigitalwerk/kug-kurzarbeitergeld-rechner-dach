# -*- coding: utf-8 -*-
"""
kug_dach.cli
~~~~~~~~~~~~
Kommandozeilen-Interface (CLI) dach-kug.
Berechnet Kurzarbeitergeld, Nettoentgeltdifferenz, AG-SV-Kosten und Ausfallszenarien.
"""

import sys
import json
import argparse
from typing import List, Optional
from .models import KugInput, Country, RegionDE, TaxClassDE
from .calculator import calculate_kug, generate_matrix


def format_currency(val: float, country: Country) -> str:
    sym = "CHF" if country == Country.CH else "€"
    return f"{val:,.2f} {sym}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_percent(val: float) -> str:
    return f"{val:,.2f} %".replace(".", ",")


def generate_markdown_report(res) -> str:
    md = []
    md.append("# Kurzarbeitergeld (KUG) Monats-Abrechnungsnachweis 2026")
    md.append(f"**Land:** {res.country.value} | **Arbeitsausfall:** {format_percent(res.ausfall_prozent)} | **Leistungssatz:** {format_percent(res.leistungssatz_prozent)}")
    md.append("")
    md.append("## 1. Ausgangs- & Entgeltdaten")
    md.append(f"- **Soll-Entgelt (Vollzeit-Brutto):** {format_currency(res.soll_brutto_raw, res.country)} (Gedeckelt auf BBG: {format_currency(res.soll_brutto_capped, res.country)})")
    md.append(f"- **Ist-Entgelt (Brutto bei KUG):** {format_currency(res.ist_brutto_raw, res.country)}")
    md.append(f"- **Pauschalisiertes Netto-Sollentgelt:** {format_currency(res.pauschal_soll_netto, res.country)}")
    md.append(f"- **Pauschalisiertes Netto-Istentgelt:** {format_currency(res.pauschal_ist_netto, res.country)}")
    md.append(f"- **Nettoentgeltdifferenz (Ausfall):** {format_currency(res.netto_differenz, res.country)}")
    md.append("")
    md.append("## 2. KUG-Auszahlungsermittlung")
    md.append(f"- **Kurzarbeitergeld (Staat):** {format_currency(res.kug_auszahlung, res.country)}")
    md.append(f"- **Ist-Netto (Arbeitgeberlohn):** {format_currency(res.ist_netto_auszahlung, res.country)}")
    if res.employer_topup_eur > 0:
        md.append(f"- **Tarifliche / AG-Aufstockung:** {format_currency(res.employer_topup_eur, res.country)}")
    md.append(f"- **GESAMT-NETTOAUSZAHLUNG:** {format_currency(res.gesamt_netto, res.country)} ({format_percent(res.netto_erhalt_prozent)} des Vollzeit-Nettos)")
    md.append(f"- **Tatsächlicher Nettoverlust:** {format_currency(res.netto_verlust, res.country)}")
    md.append("")
    md.append("## 3. Arbeitgeber-Aufwand")
    md.append(f"- **AG-Sozialversicherungsbeiträge auf 80 Prozent KUG-Ausfall:** {format_currency(res.ag_sv_aufwand, res.country)}")
    md.append("")
    md.append("---")
    md.append("*Erstellt mit DACH Digitalwerk KUG-Engine 2026 nach SGB III & KUG-Verordnung.*")
    return "\n".join(md)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="dach-kug",
        description="DACH Kurzarbeitergeld-Rechner 2026 nach SGB III, KUA & KAE (100 Prozent DSGVO)."
    )

    parser.add_argument(
        "-b", "--brutto",
        type=float,
        required=True,
        help="Regulaeres monatliches Soll-Bruttoentgelt"
    )
    parser.add_argument(
        "-a", "--ausfall",
        type=float,
        default=50.0,
        help="Arbeitsausfall im Abrechnungsmonat in Prozent (0 bis 100)"
    )
    parser.add_argument(
        "-c", "--country",
        choices=["DE", "AT", "CH"],
        default="DE",
        help="Land: DE (Deutschland KUG), AT (Oesterreich KUA) oder CH (Schweiz KAE)"
    )
    parser.add_argument(
        "-t", "--tax-class",
        choices=["1", "2", "3", "4", "5", "6"],
        default="1",
        help="Lohnsteuerklasse fuer Deutschland (1 bis 6)"
    )
    parser.add_argument(
        "--with-child",
        dest="has_child",
        action="store_true",
        default=True,
        help="Erhoehter Leistungssatz 67 Prozent (mit Kinderfreibetrag >= 0,5)"
    )
    parser.add_argument(
        "--without-child",
        dest="has_child",
        action="store_false",
        help="Allgemeiner Leistungssatz 60 Prozent (ohne Kinderfreibetrag)"
    )
    parser.add_argument(
        "-r", "--region",
        choices=["west", "ost"],
        default="west",
        help="Beitragsgebiet fuer BBG (west: 7.550 Euro / ost: 7.450 Euro)"
    )
    parser.add_argument(
        "--church-tax",
        action="store_true",
        default=False,
        help="Kirchensteuerabzug beruecksichtigen"
    )
    parser.add_argument(
        "--topup",
        type=float,
        default=0.0,
        help="Freiwillige Arbeitgeber-Aufstockung auf Ziel-Nettoerhalt in Prozent (z.B. 80 oder 90)"
    )

    # Ausgabemodi
    parser.add_argument("-m", "--matrix", action="store_true", help="Ausfall-Matrix (10 bis 100 Prozent) ausgeben")
    parser.add_argument("-j", "--json", action="store_true", help="Ausgabe als JSON-Objekt")
    parser.add_argument("-M", "--markdown", action="store_true", help="Druckfertigen Markdown-Bericht erzeugen")

    args = parser.parse_args(argv)

    country = Country(args.country)
    tax_class = TaxClassDE(args.tax_class)
    region = RegionDE(args.region)

    if args.matrix:
        rows = generate_matrix(
            soll_brutto=args.brutto,
            country=country,
            tax_class=tax_class,
            has_child=args.has_child,
            region=region,
            church_tax=args.church_tax
        )
        if args.json:
            print(json.dumps(rows, indent=2, ensure_ascii=False))
            return 0
        print("\n=== KURZARBEIT AUSFALL-MATRIX 2026 ===")
        print(f"Brutto-Soll: {format_currency(args.brutto, country)} | Land: {country.value} | StKl: {tax_class.value}\n")
        print(f"{'Ausfall':<10} | {'Ist-Brutto':<14} | {'Ist-Netto':<14} | {'KUG (Staat)':<14} | {'Gesamt-Netto':<14} | {'Erhalt':<10} | {'Verlust':<12}")
        print("-" * 92)
        for r in rows:
            print(
                f"{r['ausfall_prozent']} %{' (KUG 0)' if r['ausfall_prozent'] == 100 else '':<4} | "
                f"{format_currency(r['ist_brutto'], country):<14} | "
                f"{format_currency(r['ist_netto'], country):<14} | "
                f"+{format_currency(r['kug_auszahlung'], country):<13} | "
                f"{format_currency(r['gesamt_netto'], country):<14} | "
                f"{format_percent(r['netto_erhalt_prozent']):<10} | "
                f"-{format_currency(r['netto_verlust'], country):<11}"
            )
        return 0

    inp = KugInput(
        soll_brutto=args.brutto,
        ausfall_prozent=args.ausfall,
        country=country,
        tax_class=tax_class,
        has_child=args.has_child,
        region=region,
        church_tax=args.church_tax,
        employer_topup_percent=args.topup
    )
    res = calculate_kug(inp)

    if args.json:
        out = {
            "country": res.country.value,
            "soll_brutto_raw": res.soll_brutto_raw,
            "soll_brutto_capped": res.soll_brutto_capped,
            "ist_brutto_raw": res.ist_brutto_raw,
            "ist_brutto_capped": res.ist_brutto_capped,
            "ausfall_prozent": res.ausfall_prozent,
            "pauschal_soll_netto": res.pauschal_soll_netto,
            "pauschal_ist_netto": res.pauschal_ist_netto,
            "netto_differenz": res.netto_differenz,
            "leistungssatz_prozent": res.leistungssatz_prozent,
            "kug_auszahlung": res.kug_auszahlung,
            "ist_netto_auszahlung": res.ist_netto_auszahlung,
            "employer_topup_eur": res.employer_topup_eur,
            "gesamt_netto": res.gesamt_netto,
            "netto_verlust": res.netto_verlust,
            "netto_erhalt_prozent": res.netto_erhalt_prozent,
            "ag_sv_aufwand": res.ag_sv_aufwand,
            "bbg_applied": res.bbg_applied,
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0

    if args.markdown:
        print(generate_markdown_report(res))
        return 0

    # Standard Terminal Output
    print("\n" + "=" * 60)
    print("📉  DACH KURZARBEITERGELD-RECHNER 2026")
    print("=" * 60)
    print(f"Land & Rechtsrahmen     : {res.country.value}")
    print(f"Soll-Entgelt (Vollzeit) : {format_currency(res.soll_brutto_raw, res.country)} (BBG: {format_currency(res.soll_brutto_capped, res.country)})")
    print(f"Arbeitsausfall          : {format_percent(res.ausfall_prozent)}")
    print(f"Ist-Entgelt (KUG-Monat) : {format_currency(res.ist_brutto_capped, res.country)}")
    print(f"Pauschal-Netto Soll     : {format_currency(res.pauschal_soll_netto, res.country)}")
    print(f"Pauschal-Netto Ist      : {format_currency(res.pauschal_ist_netto, res.country)}")
    print(f"Nettoentgeltdifferenz   : {format_currency(res.netto_differenz, res.country)}")
    print(f"Leistungssatz           : {format_percent(res.leistungssatz_prozent)}")
    print("-" * 60)
    print(f"⚡ KURZARBEITERGELD (KUG): {format_currency(res.kug_auszahlung, res.country)}")
    print(f"Lohn Ist-Netto (vom AG) : {format_currency(res.ist_netto_auszahlung, res.country)}")
    if res.employer_topup_eur > 0:
        print(f"Arbeitgeber-Aufstockung : {format_currency(res.employer_topup_eur, res.country)}")
    print(f"🎯 GESAMTE NETTOAUSZAHLUNG: {format_currency(res.gesamt_netto, res.country)} ({format_percent(res.netto_erhalt_prozent)} Erhalt)")
    print(f"Netto-Einkommensverlust : {format_currency(res.netto_verlust, res.country)}")
    print(f"AG-Sozialversicherungs-SV: ca. {format_currency(res.ag_sv_aufwand, res.country)} (auf 80% fiktives Entgelt)")
    print("=" * 60 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
