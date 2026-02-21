# Dataset Slovensko 🇸🇰

Čistý Python pipeline nad otvorenými datasetmi Štatistického úradu SR ([data.statistics.sk](https://data.statistics.sk)) – DATAcube / API v2.

## Čo je tu

| Adresár | Obsah |
|---------|-------|
| `data/raw/` | Originálne CSV exporty z DATAcube |
| `data/warehouse/` | Vyčistené Parquet súbory s labelmi |
| `data/datacube_labels.json` | Labely dimenzií stiahnuté z API |
| `src/loader.py` | Unified loader – načítanie CSV/Parquet |
| `src/fetch_labels.py` | Stiahnutie labelov z DATAcube API |
| `src/build_warehouse.py` | Zostavenie Parquet warehouse |
| `analysis/heatmap.py` | Coverage heatmap – dostupnosť dát podľa roku |

## Datasety (27)

### Mzdy
| Kód | Názov | Roky |
|-----|-------|------|
| np3101rr | Hrubá mzda podľa veku (NUTS3) | 2010–2024 |
| np3102rr | Hrubá mzda podľa vzdelania (NUTS3) | 2010–2024 |
| np3106rr | Hrubá mzda podľa zamestnania (NUTS3) | 2012–2024 |
| od0008ms | Mesačná mzda v odvetviach | 2010–2025 |
| kz1001rs | Medián čistého príjmu | 2022–2024 |
| kz1008rs | Schopnosť výjsť s peniazmi | 2022–2024 |

### Demografia
| Kód | Názov | Roky |
|-----|-------|------|
| as1001rs | Obyvateľstvo a charakteristiky veku | 2018–2024 |
| nu1024rs | Obyvateľstvo, zamestnanosť | 1995–2024 |
| om3707rr | Pohyb obyvateľstva – mestá | 2010–2024 |

### Vzdelanie
| Kód | Názov | Roky |
|-----|-------|------|
| kz1030rs | Stupeň vzdelania (ISCED 2011) | 2005–2024 |
| sv3701rr | Vzdelanie – mestá | 2010–2024 |

### Ekonomika
| Kód | Názov | Roky |
|-----|-------|------|
| kz1018rs | Miera ekonomickej aktivity | 2005–2024 |
| og1007rs | SZČO | 2015–2025 |
| og2019qs | Ekonomické subjekty | 2017–2025 |
| og2021qs | Subjekty × SK NACE Rev. 2 | 2017–2025 |
| og3803rr | Podniky × NACE – mestá | 2024–2025 |

### Digitalizácia
| Kód | Názov | Roky |
|-----|-------|------|
| as1012rs | Používanie internetu podľa veku | 2018–2024 |
| is1001rs | IT vybavenie domácností | 2020–2022 |

### Inovácie & VaV
| Kód | Názov | Roky |
|-----|-------|------|
| vt0003rs | Inovácie | 2001–2022 |
| vt1002rs | Výdavky na inovácie | 2001–2022 |
| vt1003rs | Intenzita inovácie | 2001–2022 |
| vt1008rs | Výdavky na VaV | 2002–2024 |
| vt1009rs | Zamestnanci VaV | 2000–2024 |
| vt1011rs | Podniky s inovačnou aktivitou | 2001–2022 |

### Kvalita života
| Kód | Názov | Roky |
|-----|-------|------|
| kz1028rs | Spokojnosť so životom | 2013–2024 |
| kz1024rs | Frekvencia stretnutí s príbuznými | 2006–2015 |
| kz1029rs | Posúdenie či život má zmysel | 2013 |

## Quickstart

```python
from src.loader import load, load_all, catalog

# Jeden dataset
df = load("np3101rr")

# Všetky datasety
data = load_all()

# Prehľad
print(catalog())
```

## Rebuild

```bash
# Aktualizuj labely z API
python src/fetch_labels.py

# Prebuduj warehouse
python src/build_warehouse.py

# Generuj heatmapu
python analysis/heatmap.py
```

## Zdroj
[Štatistický úrad SR – DATAcube](https://data.statistics.sk)
