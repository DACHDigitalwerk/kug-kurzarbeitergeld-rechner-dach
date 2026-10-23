# DACH Kurzarbeitergeld-Rechner 2026 (KUG, KUA & KAE)

[![Python Tests](https://github.com/DACHDigitalwerk/kug-kurzarbeitergeld-rechner-dach/actions/workflows/python-tests.yml/badge.svg)](https://github.com/DACHDigitalwerk/kug-kurzarbeitergeld-rechner-dach/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![100% DSGVO & Client-Side](https://img.shields.io/badge/Privacy-100%25%20Client--Side-brightgreen.svg)](https://dachdigitalwerk.github.io/kurzarbeitergeld-rechner/)

Normgerechte und prüffähige **Kurzarbeitergeld-Berechnung 2026** nach dem Dritten Buch Sozialgesetzbuch (§§ 95 ff., 105, 106 SGB III), der amtlichen KUG-Verordnung sowie den Kurzarbeitsregelungen in Österreich (KUA) und der Schweiz (KAE).

> 🌐 **Kostenloses interaktives Web-Tool:**  
> Nutzen Sie den sofort einsatzbereiten Browser-Rechner mit Arbeitsausfall-Matrix, Steuerklassen-Vergleich und druckfertigem DIN-A4 Abrechnungsnachweis direkt unter:  
> **[DACH Kurzarbeitergeld-Rechner 2026](https://dachdigitalwerk.github.io/kurzarbeitergeld-rechner/)**

---

## 🚀 Highlights & Features

- **Gesetzliche Leistungssätze (§ 105 SGB III):**
  - **67 % erhöhter Leistungssatz** für Arbeitnehmer mit mindestens einem Kind (Kinderfreibetrag &ge; 0,5).
  - **60 % allgemeiner Leistungssatz** für alle übrigen Beschäftigten.
- **Amtliche KUG-Pauschaltabelle (§ 106 SGB III):**
  - Berücksichtigung der 20 %-igen Sozialversicherungspauschale und Lohnsteuer nach Steuerklassen I bis VI.
  - Exakte Nettoentgeltdifferenz zwischen Soll- und Ist-Entgelt.
- **Beitragsbemessungsgrenzen 2026:**
  - Alte Bundesländer (West): **7.550 € / Monat**.
  - Neue Bundesländer (Ost): **7.450 € / Monat**.
  - Schweiz (AVIG): **12.350 CHF / Monat** (148.200 CHF / Jahr).
- **Arbeitgeber-Aufstockungsberechnung:**
  - Simulation freiwilliger oder tarifvertraglicher Aufstockungszuschüsse (z. B. auf 80 %, 90 % oder 95 % des Vollzeit-Nettos).
- **Arbeitgeber-Sozialversicherungsaufwand (§ 166 Abs. 1 Nr. 2 SGB VI):**
  - Berechnung der allein vom Arbeitgeber zu tragenden KV-, PV- und RV-Beiträge auf 80 % des fiktiven Entgelts.
- **Vollständiger DACH-Support:**
  - 🇩🇪 Deutschland: SGB III KUG
  - 🇦🇹 Österreich: AMS Kurzarbeitsbeihilfe (KUA mit 80 % bis 90 % Nettoersatz)
  - 🇨🇭 Schweiz: AVIG Kurzarbeitsentschädigung (KAE mit 80 % Verdienstausfall)

---

## 📦 Installation

```bash
pip install git+https://github.com/DACHDigitalwerk/kug-kurzarbeitergeld-rechner-dach.git
```

Oder im Entwicklungsmodus:

```bash
git clone https://github.com/DACHDigitalwerk/kug-kurzarbeitergeld-rechner-dach.git
cd kug-kurzarbeitergeld-rechner-dach
pip install -e .
```

---

## 💻 CLI-Nutzung (`dach-kug`)

### 1. Standardfall: 50 % Arbeitsausfall (Steuerklasse I, mit Kind)

```bash
dach-kug --brutto 4000 --ausfall 50 --tax-class 1 --with-child
```

Ausgabe:
```text
============================================================
📉  DACH KURZARBEITERGELD-RECHNER 2026
============================================================
Land & Rechtsrahmen     : DE
Soll-Entgelt (Vollzeit) : 4.000,00 € (BBG: 4.000,00 €)
Arbeitsausfall          : 50,00 %
Ist-Entgelt (KUG-Monat) : 2.000,00 €
Pauschal-Netto Soll     : 2.582,00 €
Pauschal-Netto Ist      : 1.390,20 €
Nettoentgeltdifferenz   : 1.191,80 €
Leistungssatz           : 67,00 %
------------------------------------------------------------
⚡ KURZARBEITERGELD (KUG): 798,51 €
Lohn Ist-Netto (vom AG) : 1.390,20 €
🎯 GESAMTE NETTOAUSZAHLUNG: 2.188,71 € (84,77 % Erhalt)
Netto-Einkommensverlust : 393,29 €
AG-Sozialversicherungs-SV: ca. 313,60 € (auf 80% fiktives Entgelt)
============================================================
```

### 2. Ausfall-Matrix für alle Szenarien (10 % bis 100 % KUG-Null)

```bash
dach-kug --brutto 4000 --matrix
```

### 3. Mit tariflicher Arbeitgeber-Aufstockung auf 90 %

```bash
dach-kug --brutto 4000 --ausfall 50 --topup 90
```

### 4. JSON-Export für HR- & Payroll-Systeme

```bash
dach-kug --brutto 3800 --ausfall 40 --json
```

---

## 🐍 Python API

```python
from kug_dach import (
    calculate_kug,
    generate_matrix,
    KugInput,
    Country,
    TaxClassDE
)

inp = KugInput(
    soll_brutto=4200.0,
    ausfall_prozent=50.0,
    country=Country.DE,
    tax_class=TaxClassDE.I,
    has_child=True
)

res = calculate_kug(inp)
print(f"KUG-Auszahlung: {res.kug_auszahlung} €")
print(f"Gesamt-Netto:   {res.gesamt_netto} € ({res.netto_erhalt_prozent}% Erhalt)")
print(f"AG-SV-Beitrag:  {res.ag_sv_aufwand} €")
```

---

## 🧪 Tests

```bash
pytest -v
```

Alle 28+ Unit-Tests verifizieren die Beitragsbemessungsgrenzen 2026, Steuerklassenprogressionen, Kurzarbeit Null und KUA/KAE-Länderregeln.

---

## ⚖️ Rechtlicher Hinweis & Haftungsausschluss

Dieses Software-Tool dient der **technischen Berechnung und Lohnabrechnungssimulation**. Es stellt **keine Rechts- oder Steuerberatung** im Sinne des Rechtsdienstleistungsgesetzes (§ 2 RDG) oder des Steuerberatungsgesetzes (§ 5 StBerG) dar. Das Tool ersetzt nicht die amtliche Prüfung und Bewilligung durch die Bundesagentur für Arbeit, das AMS oder die zuständige Arbeitslosenkasse. Weitere Angaben: [AGB](https://dachdigitalwerk.github.io/agb/) | [Haftungsausschluss](https://dachdigitalwerk.github.io/haftungsausschluss/).

---

## 📄 Lizenz

Veröffentlicht unter der [MIT License](LICENSE).  
Copyright (c) 2026 **DACH Digitalwerk**.
