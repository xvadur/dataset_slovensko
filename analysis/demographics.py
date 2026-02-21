"""
Vrstva 1: Demografia
  - Veková štruktúra populácie (2020-2024)
  - Index starnutia + priemerný/mediánový vek
  - Pohyb obyvateľstva: živonarodení vs. zomretí, sobáše, rozvody
  - Zamestnanosť: aktívni / zamestnanci / nezamestnaní / SZČO
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from loader import load

OUT   = Path(__file__).parent
YEARS = list(range(2020, 2025))

STYLE = {
    "bg":     "#0d1117",
    "panel":  "#161b22",
    "border": "#30363d",
    "text":   "#e6edf3",
    "sub":    "#8b949e",
    "grid":   "#21262d",
}

GREEN  = ["#0e4429", "#006d32", "#26a641", "#39d353", "#56d364"]
BLUE   = ["#0d419d", "#1f6feb", "#388bfd", "#58a6ff", "#79c0ff"]
RED    = "#f78166"
ORANGE = "#e3b341"


def apply_dark(ax, yformat=None, xformat=None):
    ax.set_facecolor(STYLE["panel"])
    ax.tick_params(colors=STYLE["sub"], labelsize=8)
    ax.xaxis.label.set_color(STYLE["sub"])
    ax.yaxis.label.set_color(STYLE["sub"])
    ax.title.set_color(STYLE["text"])
    for sp in ax.spines.values():
        sp.set_edgecolor(STYLE["border"])
    ax.grid(axis="y", color=STYLE["grid"], linewidth=0.6, linestyle="--")
    ax.set_axisbelow(True)
    if yformat:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(yformat))
    if xformat:
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(xformat))


def filter_years(df, rok_col):
    return df[df[rok_col].astype(int).isin(YEARS)]


# ── GRAF 1: Veková štruktúra – stacked bar ───────────────────────────────────

def plot_age_structure(ax, df):
    sub = df[
        (df["as1001rs_poh"] == "TOTAL") &
        (df["as1001rs_ukaz"].isin(["UKAZ05", "UKAZ06", "UKAZ07"]))
    ].copy()
    sub = filter_years(sub, "as1001rs_rok")
    sub["rok"] = sub["as1001rs_rok"].astype(int)

    pivot = sub.pivot_table(index="rok", columns="as1001rs_ukaz", values="value")
    pivot = pivot[["UKAZ05", "UKAZ06", "UKAZ07"]]

    labels = ["Predproduktívni\n(0–14 r.)", "Produktívni\n(15–64 r.)", "Poproduktívni\n(65+ r.)"]
    colors = [GREEN[2], BLUE[2], RED]
    bottom = np.zeros(len(pivot))

    for i, (col, label, color) in enumerate(zip(pivot.columns, labels, colors)):
        vals = pivot[col].values
        bars = ax.bar(pivot.index, vals, bottom=bottom, color=color,
                      label=label, width=0.6, edgecolor=STYLE["bg"], linewidth=0.5)
        for bar, val, bot in zip(bars, vals, bottom):
            if val > 3:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bot + val / 2,
                        f"{val:.1f}%", ha="center", va="center",
                        fontsize=7.5, color="white", fontweight="bold")
        bottom += vals

    ax.set_xticks(pivot.index)
    ax.set_title("Veková štruktúra obyvateľstva  (SR, 2020–2024)", pad=8)
    ax.set_ylabel("%")
    ax.set_ylim(0, 105)
    ax.legend(framealpha=0, labelcolor=STYLE["text"], fontsize=8,
              loc="upper right", ncol=3)
    apply_dark(ax)


# ── GRAF 2: Starnutie – index + vek ──────────────────────────────────────────

def plot_ageing(ax, df):
    sub = df[
        (df["as1001rs_poh"] == "TOTAL") &
        (df["as1001rs_ukaz"].isin(["UKAZ16", "UKAZ17", "UKAZ18"]))
    ].copy()
    sub = filter_years(sub, "as1001rs_rok")
    sub["rok"] = sub["as1001rs_rok"].astype(int)

    pivot = sub.pivot_table(index="rok", columns="as1001rs_ukaz", values="value")

    ax2 = ax.twinx()

    # Ľavá os: index starnutia (UKAZ18, %)
    ax.plot(pivot.index, pivot["UKAZ18"], color=RED, linewidth=2.2,
            marker="o", markersize=5, label="Index starnutia (%)")
    ax.set_ylabel("Index starnutia (%)", color=RED, fontsize=8)
    ax.tick_params(axis="y", colors=RED, labelsize=8)

    # Pravá os: priemerný a mediánový vek
    ax2.plot(pivot.index, pivot["UKAZ16"], color=GREEN[3], linewidth=2,
             marker="s", markersize=4, label="Priemerný vek", linestyle="--")
    ax2.plot(pivot.index, pivot["UKAZ17"], color=BLUE[2], linewidth=2,
             marker="^", markersize=4, label="Mediánový vek", linestyle=":")
    ax2.set_ylabel("Vek (roky)", color=STYLE["sub"], fontsize=8)
    ax2.tick_params(axis="y", colors=STYLE["sub"], labelsize=8)
    ax2.set_facecolor(STYLE["panel"])
    ax2.spines["right"].set_edgecolor(STYLE["border"])

    # Spoločná legenda
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2,
              framealpha=0, labelcolor=STYLE["text"], fontsize=8, loc="upper left")

    ax.set_title("Starnutie populácie – index starnutia a vek  (SR, 2020–2024)", pad=8)
    ax.set_xticks(list(pivot.index))
    apply_dark(ax)
    ax.grid(axis="y", color=STYLE["grid"], linewidth=0.6, linestyle="--")


# ── GRAF 3: Pohyb obyvateľstva ────────────────────────────────────────────────

POHYB_UKAZOVATELE = {
    "FERMOR_ZIVONARDROK": ("Živonarodení", GREEN[3]),
    "FERMOR_ZOMRROK":     ("Zomretí",      RED),
    "FERMOR_SOBAS":       ("Sobáše",       BLUE[2]),
    "FERMOR_ROZVOD":      ("Rozvody",      ORANGE),
}

def plot_pohyb(ax, df3):
    sub = df3[
        (df3["om3707rr_uzemieua"] == "SK0") &
        (df3["om3707rr_fermor"].isin(POHYB_UKAZOVATELE.keys()))
    ].copy()
    sub = filter_years(sub, "om3707rr_rok")
    sub["rok"] = sub["om3707rr_rok"].astype(int)

    for fermor, (label, color) in POHYB_UKAZOVATELE.items():
        row = sub[sub["om3707rr_fermor"] == fermor].sort_values("rok")
        ax.plot(row["rok"], row["value"], color=color, linewidth=2.2,
                marker="o", markersize=5, label=label)
        if not row.empty:
            last = row.iloc[-1]
            ax.annotate(f"{label}  {last['value']:,.0f}",
                        xy=(last["rok"], last["value"]),
                        xytext=(6, 0), textcoords="offset points",
                        color=color, fontsize=7.5, va="center")

    ax.set_title("Pohyb obyvateľstva  (SR, 2020–2024)", pad=8)
    ax.set_ylabel("Počet osôb")
    ax.set_xticks(YEARS)
    ax.set_xlim(YEARS[0] - 0.3, YEARS[-1] + 1.5)
    ax.legend(framealpha=0, labelcolor=STYLE["text"], fontsize=8)
    apply_dark(ax, yformat=lambda x, _: f"{x:,.0f}")


# ── GRAF 4: Zamestnanosť ──────────────────────────────────────────────────────

ZAMEST = {
    "UKAZ02": ("Ekonomicky aktívni",   BLUE[3]),
    "UKAZ04": ("Zamestnané osoby",     GREEN[3]),
    "UKAZ06": ("SZČO",                 ORANGE),
    "UKAZ03": ("Nezamestnaní",         RED),
}

def plot_employment(ax, df2):
    sub = filter_years(df2, "nu1024rs_rok").copy()
    sub["rok"] = sub["nu1024rs_rok"].astype(int)

    for ukaz, (label, color) in ZAMEST.items():
        row = sub[sub["nu1024rs_ukaz"] == ukaz].sort_values("rok")
        ax.plot(row["rok"], row["value"] / 1000, color=color, linewidth=2.2,
                marker="o", markersize=5, label=label)
        if not row.empty:
            last = row.iloc[-1]
            ax.annotate(f"{label}  {last['value']/1000:,.0f}k",
                        xy=(last["rok"], last["value"] / 1000),
                        xytext=(6, 0), textcoords="offset points",
                        color=color, fontsize=7.5, va="center")

    ax.set_title("Trh práce  (SR, 2020–2024)", pad=8)
    ax.set_ylabel("Osoby (tis.)")
    ax.set_xticks(YEARS)
    ax.set_xlim(YEARS[0] - 0.3, YEARS[-1] + 1.8)
    ax.legend(framealpha=0, labelcolor=STYLE["text"], fontsize=8)
    apply_dark(ax, yformat=lambda x, _: f"{x:,.0f}k")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    df_pop  = load("as1001rs")
    df_emp  = load("nu1024rs")
    df_pohyb = load("om3707rr")

    fig, axes = plt.subplots(2, 2, figsize=(20, 13))
    fig.patch.set_facecolor(STYLE["bg"])
    fig.suptitle("Demografická analýza Slovenska  |  ŠÚ SR DATAcube",
                 color=STYLE["text"], fontsize=15, fontweight="bold", y=0.98)

    plot_age_structure(axes[0, 0], df_pop)
    plot_ageing(axes[0, 1], df_pop)
    plot_pohyb(axes[1, 0], df_pohyb)
    plot_employment(axes[1, 1], df_emp)

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    out = OUT / "demographics_analysis.png"
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"✓ Uložené: {out}")


if __name__ == "__main__":
    main()
