# -*- coding: utf-8 -*-
"""
kug_dach.models
~~~~~~~~~~~~~~~
Datenmodelle und Enums für die Kurzarbeitsberechnung im DACH-Raum.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Country(str, Enum):
    DE = "DE"
    AT = "AT"
    CH = "CH"


class RegionDE(str, Enum):
    WEST = "west"
    OST = "ost"


class TaxClassDE(str, Enum):
    I = "1"
    II = "2"
    III = "3"
    IV = "4"
    V = "5"
    VI = "6"


class RateType(str, Enum):
    WITH_CHILD = "with_child"       # 67 % erhöhter Leistungssatz gem. § 105 SGB III
    WITHOUT_CHILD = "without_child" # 60 % allgemeiner Leistungssatz gem. § 105 SGB III


@dataclass
class KugInput:
    """Eingabeparameter für die Kurzarbeitsberechnung."""
    soll_brutto: float
    ausfall_prozent: float = 50.0  # 0.0 bis 100.0 %
    country: Country = Country.DE
    tax_class: TaxClassDE = TaxClassDE.I
    has_child: bool = True
    region: RegionDE = RegionDE.WEST
    church_tax: bool = False
    employer_topup_percent: float = 0.0  # z. B. 80.0 für 80% Nettoerhalt


@dataclass
class KugResult:
    """Berechnungsergebnis nach KUG-Verordnung und DACH-Standards."""
    country: Country
    soll_brutto_raw: float
    soll_brutto_capped: float
    ist_brutto_raw: float
    ist_brutto_capped: float
    ausfall_prozent: float
    pauschal_soll_netto: float
    pauschal_ist_netto: float
    netto_differenz: float
    leistungssatz_prozent: float
    kug_auszahlung: float
    ist_netto_auszahlung: float
    employer_topup_eur: float
    gesamt_netto: float
    netto_verlust: float
    netto_erhalt_prozent: float
    ag_sv_aufwand: float
    bbg_applied: float
