"""
Vrstva 2: Mzdy
  - Vývoj miezd podľa krajov (2010-2024)
  - Regionálne mzdové nerovnosti v 2024
  - Mzdový gap podľa vzdelania
  - Mzdový lifecycle podľa veku
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from loader import load

OUT = Path(__file__).parent

# Len NUTS3 kraje – bez SR, NUTS2 agregátov
KRAJE = {
    "SK010": "Bratislavský",
    "SK021": "Trnavský",
    "SK022": "Trenčiansky",
    "SK023": "Nitriansky",
    "SK031": "Žilinský",
    "SK032": "Banskobystrický",
    "SK041": "Prešovský",
    "SK042": "Košický",
}

KRAJ_COLORS = [
    "#39d353", "#26a641", "#006d32", "#0e4429",
    "#58a6ff", "#1f6feb", "#388bfd", "#79c0ff",
]


# ── pomocné ──────────────────────────────────────────────────────────────────

def mzda_kraje_rok(df: pd.DataFrame, nuts_col: str, rok_col: str, dim_col: str,
                   dim_val: str) -> pd.DataFrame:
    """Pivot: kraj × rok, hodnota = priemerná mzda pre zadaný dim_val (napr. 'Spolu')."""
    sub = df[(df[nuts_col].isin(KRAJE)) & (df[dim_col] == dim_val)].copy()
    sub.loc[:, "kraj"] = sub[nuts_col].map(KRAJE)
    pivot = sub.pivot_table(index="kraj", columns=rok_col, values="value", aggfunc="first")
    pivot.columns = pivot.columns.astype(int)
    pivot = pivot[[c for c in pivot.columns if c >= YEAR_MIN]]
    return pivot.sort_values(pivot.columns[-1], ascending=False)


# ── téma grafov ───────────────────────────────────────────────────────────────

STYLE = {
    "bg":      "#0d1117",
    "panel":   "#161b22",
    "border":  "#30363d",
    "text":    "#e6edf3",
    "subtext": "#8b949e",
    "grid":    "#21262d",
}

def apply_dark(ax):
    ax.set_facecolor(STYLE["panel"])
    ax.tick_params(colors=STYLE["subtext"], labelsize=8)
    ax.xaxis.label.set_color(STYLE["subtext"])
    ax.yaxis.label.set_color(STYLE["subtext"])
    ax.title.set_color(STYLE["text"])
    for spine in ax.spines.values():
        spine.set_edgecolor(STYLE["border"])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f} €"))
    ax.grid(axis="y", color=STYLE["grid"], linewidth=0.6, linestyle="--")
    ax.set_axisbelow(True)


# ── GRAF 1: vývoj miezd podľa krajov ─────────────────────────────────────────

def plot_trend(ax, pivot: pd.DataFrame):
    years = pivot.columns.tolist()
    for i, (kraj, row) in enumerate(pivot.iterrows()):
        color = KRAJ_COLORS[i % len(KRAJ_COLORS)]
        ax.plot(years, row.values, color=color, linewidth=1.8, marker="o",
                markersize=3, label=kraj)
        # label na konci riadku
        last_val = row.iloc[-1]
        ax.annotate(f"{kraj}  {last_val:,.0f} €",
                    xy=(years[-1], last_val),
                    xytext=(6, 0), textcoords="offset points",
                    color=color, fontsize=7, va="center")

    ax.set_xlim(years[0] - 0.5, years[-1] + 2.5)
    ax.set_title("Vývoj priemernej hrubej mzdy podľa krajov  (2010–2024)", pad=8)
    ax.set_xlabel("Rok")
    apply_dark(ax)


# ── GRAF 2: mzdový bar 2024 ───────────────────────────────────────────────────

def plot_bar_2024(ax, pivot: pd.DataFrame):
    vals = pivot[2024].sort_values(ascending=True)
    colors = [KRAJ_COLORS[i % len(KRAJ_COLORS)] for i in range(len(vals))]
    bars = ax.barh(vals.index, vals.values, color=colors, height=0.65)

    for bar, val in zip(bars, vals.values):
        ax.text(bar.get_width() + 20, bar.get_y() + bar.get_height() / 2,
                f"{val:,.0f} €", va="center", fontsize=8, color=STYLE["text"])

    sk_avg = 1748  # SK0 spolu 2024
    ax.axvline(sk_avg, color="#f78166", linewidth=1.2, linestyle="--")
    ax.text(sk_avg + 20, -0.7, f"SR priemer  {sk_avg:,} €",
            color="#f78166", fontsize=7.5)

    ax.set_title("Priemerná hrubá mzda podľa kraja  (2024)", pad=8)
    ax.set_xlabel("EUR / mesiac")
    ax.set_xlim(0, vals.max() * 1.22)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f} €"))
    apply_dark(ax)
    ax.yaxis.set_major_formatter(mticker.NullFormatter())
    ax.tick_params(axis="y", labelcolor=STYLE["text"], labelsize=8.5)


# ── GRAF 3: gap vzdelanie ─────────────────────────────────────────────────────

EDU_ORDER = [
    "Základné",
    "Stredné odborné (učňovské) bez maturity",
    "Úplné stredné odborné",
    "Úplné stredné všeobecné",
    "Vyššie odborné",
    "Vysokoškolské 1. stupeň",
    "Vysokoškolské 2. stupeň",
    "Vysokoškolské 3. stupeň",
]

def plot_edu_gap(ax, df2: pd.DataFrame):
    sub = df2[(df2["nuts13"] == "SK0") & (df2["np3102rr_rok"] == "2024")].copy()
    sub = sub[sub["np3102rr_dim1_label"].isin(EDU_ORDER)]
    sub = sub.set_index("np3102rr_dim1_label")["value"].reindex(EDU_ORDER).dropna()

    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.85, len(sub)))
    bars = ax.barh(range(len(sub)), sub.values, color=colors, height=0.65)

    ax.set_yticks(range(len(sub)))
    ax.set_yticklabels(sub.index, fontsize=8, color=STYLE["text"])

    for i, (bar, val) in enumerate(zip(bars, sub.values)):
        ax.text(bar.get_width() + 20, bar.get_y() + bar.get_height() / 2,
                f"{val:,.0f} €", va="center", fontsize=8, color=STYLE["text"])

    ax.set_title("Priemerná hrubá mzda podľa dosiahnutého vzdelania  (SK, 2024)", pad=8)
    ax.set_xlabel("EUR / mesiac")
    ax.set_xlim(0, sub.max() * 1.22)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f} €"))
    apply_dark(ax)
    ax.yaxis.set_major_formatter(mticker.NullFormatter())


# ── GRAF 4: lifecycle veku ────────────────────────────────────────────────────

AGE_ORDER = [
    "do 19 rokov", "od 20 do 24 rokov", "od 25 do 29 rokov",
    "od 30 do 34 rokov", "od 35 do 39 rokov", "od 40 do 44 rokov",
    "od 45 do 49 rokov", "od 50 do 54 rokov", "od 55 do 59 rokov",
    "60 a viac rokov",
]
AGE_SHORT = ["<19", "20-24", "25-29", "30-34", "35-39",
             "40-44", "45-49", "50-54", "55-59", "60+"]

YEAR_MIN = 2020
YEARS_LIFECYCLE = [2020, 2021, 2022, 2023, 2024]

def plot_lifecycle(ax, df1: pd.DataFrame):
    sub = df1[(df1["nuts13"] == "SK0") &
              (df1["np3101rr_rok"].astype(int).isin(YEARS_LIFECYCLE)) &
              (df1["np3101rr_dim1_label"].isin(AGE_ORDER))].copy()

    colors_lc = ["#30363d", "#1f6feb", "#006d32", "#26a641", "#39d353"]

    for i, year in enumerate(YEARS_LIFECYCLE):
        yr_data = sub[sub["np3101rr_rok"].astype(str) == str(year)]
        yr_data = yr_data.set_index("np3101rr_dim1_label")["value"].reindex(AGE_ORDER).dropna()
        ax.plot(range(len(yr_data)), yr_data.values,
                color=colors_lc[i], linewidth=2, marker="o", markersize=4,
                label=str(year))

    ax.set_xticks(range(len(AGE_SHORT)))
    ax.set_xticklabels(AGE_SHORT, fontsize=8)
    ax.set_title("Mzdový lifecycle podľa veku  (SR, vybrané roky)", pad=8)
    ax.set_xlabel("Veková skupina")
    ax.legend(framealpha=0, labelcolor=STYLE["text"], fontsize=8)
    apply_dark(ax)


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    df1 = load("np3101rr")
    df2 = load("np3102rr")

    pivot_spolu = mzda_kraje_rok(df1, "nuts13", "np3101rr_rok", "np3101rr_dim1_label", "Spolu")

    fig, axes = plt.subplots(2, 2, figsize=(20, 13))
    fig.patch.set_facecolor(STYLE["bg"])
    fig.suptitle("Mzdová analýza Slovenska  |  ŠÚ SR DATAcube",
                 color=STYLE["text"], fontsize=15, fontweight="bold", y=0.98)

    plot_trend(axes[0, 0], pivot_spolu)
    plot_bar_2024(axes[0, 1], pivot_spolu)
    plot_edu_gap(axes[1, 0], df2)
    plot_lifecycle(axes[1, 1], df1)

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    out = OUT / "wages_analysis.png"
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"✓ Uložené: {out}")


if __name__ == "__main__":
    main()
