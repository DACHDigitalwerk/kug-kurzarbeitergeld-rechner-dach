# -*- coding: utf-8 -*-
"""
kug_dach.calculator
~~~~~~~~~~~~~~~~~~~
Berechnungsalgorithmen für Kurzarbeitergeld nach SGB III (DE), KUA (AT) und KAE (CH).
"""

from typing import List, Dict, Any, Optional
from .models import KugInput, KugResult, Country, RegionDE, TaxClassDE
from .validator import validate_input
from .tables import (
    BBG_WEST_2026,
    BBG_OST_2026,
    BBG_CH_2026,
    get_pauschaliertes_netto_de
)


def calculate_kug(params: KugInput) -> KugResult:
    """
    Berechnet das Kurzarbeitergeld im Abrechnungsmonat.
    """
    val = validate_input(params)

    # 1. Beitragsbemessungsgrenze ermitteln
    if val.country == Country.DE:
        bbg = BBG_WEST_2026 if val.region == RegionDE.WEST else BBG_OST_2026
    elif val.country == Country.CH:
        bbg = BBG_CH_2026
    else:  # AT: Höchstbeitragsgrundlage ASVG ~ 6.060 €
        bbg = 6060.0

    soll_brutto_capped = min(val.soll_brutto, bbg)

    # 2. Ist-Brutto
    ist_faktor = max(0.0, (100.0 - val.ausfall_prozent) / 100.0)
    ist_brutto_raw = round(val.soll_brutto * ist_faktor, 2)
    ist_brutto_capped = min(ist_brutto_raw, bbg)

    soll_netto = 0.0
    ist_netto = 0.0
    leistungssatz = 0.67
    kug_auszahlung = 0.0
    ag_sv = 0.0

    if val.country == Country.DE:
        leistungssatz = 0.67 if val.has_child else 0.60
        soll_netto = get_pauschaliertes_netto_de(soll_brutto_capped, val.tax_class, val.church_tax)
        ist_netto = get_pauschaliertes_netto_de(ist_brutto_capped, val.tax_class, val.church_tax)
        netto_diff = max(0.0, round(soll_netto - ist_netto, 2))
        kug_auszahlung = round(netto_diff * leistungssatz, 2)

        # AG SV auf 80 % des fiktiven Entgelts (§ 166 SGB VI)
        fiktives_entgelt = max(0.0, soll_brutto_capped - ist_brutto_capped) * 0.80
        ag_sv = round(fiktives_entgelt * 0.196, 2)

    elif val.country == Country.AT:
        # Österreich KUA: 80% bis 90% Nettoersatz
        soll_netto = round(soll_brutto_capped * 0.65, 2)
        ist_netto = round(ist_brutto_capped * 0.65, 2)
        netto_diff = max(0.0, round(soll_netto - ist_netto, 2))
        rate = 0.85 if soll_brutto_capped <= 2685.0 else 0.80
        leistungssatz = rate
        kug_auszahlung = round(netto_diff * rate, 2)
        ag_sv = round(netto_diff * 0.21, 2)

    else:  # Schweiz KAE
        soll_netto = round(soll_brutto_capped * 0.82, 2)
        ist_netto = round(ist_brutto_capped * 0.82, 2)
        netto_diff = max(0.0, round(soll_netto - ist_netto, 2))
        leistungssatz = 0.80
        kug_auszahlung = round(netto_diff * leistungssatz, 2)
        ag_sv = round(netto_diff * 0.064, 2)

    # 3. Arbeitgeber-Aufstockung (optional)
    topup_eur = 0.0
    if val.employer_topup_percent > 0:
        ziel_erhalt = round((val.employer_topup_percent / 100.0) * soll_netto, 2)
        vorlaeufig = round(ist_netto + kug_auszahlung, 2)
        if ziel_erhalt > vorlaeufig:
            topup_eur = round(ziel_erhalt - vorlaeufig, 2)

    gesamt_netto = round(ist_netto + kug_auszahlung + topup_eur, 2)
    netto_verlust = max(0.0, round(soll_netto - gesamt_netto, 2))
    netto_erhalt_prozent = round((gesamt_netto / soll_netto * 100.0), 2) if soll_netto > 0 else 0.0

    return KugResult(
        country=val.country,
        soll_brutto_raw=round(val.soll_brutto, 2),
        soll_brutto_capped=round(soll_brutto_capped, 2),
        ist_brutto_raw=ist_brutto_raw,
        ist_brutto_capped=round(ist_brutto_capped, 2),
        ausfall_prozent=round(val.ausfall_prozent, 2),
        pauschal_soll_netto=soll_netto,
        pauschal_ist_netto=ist_netto,
        netto_differenz=netto_diff,
        leistungssatz_prozent=round(leistungssatz * 100.0, 2),
        kug_auszahlung=kug_auszahlung,
        ist_netto_auszahlung=ist_netto,
        employer_topup_eur=topup_eur,
        gesamt_netto=gesamt_netto,
        netto_verlust=netto_verlust,
        netto_erhalt_prozent=netto_erhalt_prozent,
        ag_sv_aufwand=ag_sv,
        bbg_applied=bbg,
    )


def generate_matrix(
    soll_brutto: float,
    country: Country = Country.DE,
    tax_class: TaxClassDE = TaxClassDE.I,
    has_child: bool = True,
    region: RegionDE = RegionDE.WEST,
    church_tax: bool = False,
    steps: Optional[List[int]] = None
) -> List[Dict[str, Any]]:
    """
    Erstellt eine Ausfall-Matrix für Ausfälle von 10 % bis 100 %.
    """
    if steps is None:
        steps = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

    rows = []
    for ausfall in steps:
        inp = KugInput(
            soll_brutto=soll_brutto,
            ausfall_prozent=float(ausfall),
            country=country,
            tax_class=tax_class,
            has_child=has_child,
            region=region,
            church_tax=church_tax
        )
        res = calculate_kug(inp)
        rows.append({
            "ausfall_prozent": ausfall,
            "ist_brutto": res.ist_brutto_capped,
            "ist_netto": res.pauschal_ist_netto,
            "kug_auszahlung": res.kug_auszahlung,
            "gesamt_netto": res.gesamt_netto,
            "netto_verlust": res.netto_verlust,
            "netto_erhalt_prozent": res.netto_erhalt_prozent
        })
    return rows
