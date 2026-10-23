# -*- coding: utf-8 -*-
"""
kug_dach.validator
~~~~~~~~~~~~~~~~~~
Validierungslogik für Eingabewerte der Kurzarbeitsberechnung.
"""

from typing import Union
from .models import KugInput, Country, RegionDE, TaxClassDE


class ValidationError(ValueError):
    """Fehler bei der Parameter-Validierung."""
    pass


def validate_input(params: KugInput) -> KugInput:
    """Validiert die übergebenen Berechnungsparameter."""
    if params.soll_brutto < 0:
        raise ValidationError(f"Soll-Entgelt darf nicht negativ sein: {params.soll_brutto}")

    if not (0.0 <= params.ausfall_prozent <= 100.0):
        raise ValidationError(
            f"Arbeitsausfall muss zwischen 0 % und 100 % liegen: {params.ausfall_prozent}"
        )

    if not isinstance(params.country, Country):
        try:
            params.country = Country(str(params.country).upper())
        except ValueError:
            raise ValidationError(f"Ungültiges Land: {params.country}. Erlaubt: DE, AT, CH")

    if not isinstance(params.tax_class, TaxClassDE):
        try:
            params.tax_class = TaxClassDE(str(params.tax_class))
        except ValueError:
            raise ValidationError(f"Ungültige Steuerklasse: {params.tax_class}. Erlaubt: 1 bis 6")

    if params.employer_topup_percent < 0 or params.employer_topup_percent > 100:
        raise ValidationError(
            f"Arbeitgeber-Aufstockung muss zwischen 0 und 100 % liegen: {params.employer_topup_percent}"
        )

    return params
