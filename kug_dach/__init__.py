# -*- coding: utf-8 -*-
"""
kug_dach
~~~~~~~~
Präziser Kurzarbeitergeld-Rechner 2026 für Deutschland (SGB III §§ 95ff.),
Österreich (KUA) und die Schweiz (KAE).
Pauschalierte Nettoentgelte, Leistungssätze 60% / 67%, AG-Aufstockung und Ausfall-Matrix.
"""

from .models import Country, RegionDE, TaxClassDE, RateType, KugInput, KugResult
from .calculator import calculate_kug, generate_matrix
from .tables import BBG_WEST_2026, BBG_OST_2026, BBG_CH_2026

__version__ = "1.0.0"
__author__ = "DACH Digitalwerk"
__all__ = [
    "Country",
    "RegionDE",
    "TaxClassDE",
    "RateType",
    "KugInput",
    "KugResult",
    "calculate_kug",
    "generate_matrix",
    "BBG_WEST_2026",
    "BBG_OST_2026",
    "BBG_CH_2026",
]
