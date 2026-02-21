"""
Vrstva 4: Ekonomika
  - Vývoj ekonomických subjektov podľa právnej formy (2020-2025, štvrťročne)
  - Top NACE odvetvia podľa počtu podnikov (2024)
  - Priemerná mzda podľa odvetvia NACE (od0008ms, 2024)
  - Štruktúra podnikov podľa veľkosti a právnej formy (2024)
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
YEARS = list(range(2020, 2026))

STYLE = {
    "bg": "#0d1117", "panel": "#161b22", "border": "#30363d",
    "text": "#e6edf3", "sub": "#8b949e", "grid": "#21262d",
}
GREEN  = ["#0e4429", "#006d32", "#26a641", "#39d353", "#56d364"]
BLUE   = ["#0d419d", "#1f6feb", "#388bfd", "#58a6ff", "#79c0ff"]
RED    = "#f78166"
ORANGE = "#e3b341"
PURPLE = "#bc8cff"
TEAL   = "#3fb950"


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


# ── GRAF 1: Vývoj subjektov podľa právnej formy (štvrťročne) ─────────────────

FORMY = {
    "05frm00": ("Všetky subjekty",  ORANGE,  "-",  2.5),
    "05frm05": ("Spol. s r.o.",     GREEN[3],"-",  2.0),
    "05frm17": ("Živnostníci",      BLUE[2], "--", 2.0),
    "05frm12": ("Neziskové",        PURPLE,  ":",  1.5),
    "05frm04": ("Akciové spol.",    RED,     "-.", 1.5),
}

def plot_subjects_trend(ax, df):
    # Vytvor časovú os zo rok + štvrťrok
    sub = df[df["og2019qs_ukaz"].isin(FORMY)].copy()
    sub["rok_int"] = sub["og2019qs_rok"].astype(int)
    sub = sub[sub["rok_int"].isin(YEARS)]
    stv_map = {"1.Q.": 0.0, "2.Q.": 0.25, "3.Q.": 0.5, "4.Q.": 0.75}
    sub["t"] = sub["rok_int"] + sub["og2019qs_stv"].map(stv_map)

    for ukaz, (label, color, ls, lw) in FORMY.items():
        row = sub[sub["og2019qs_ukaz"] == ukaz].sort_values("t")
        if row.empty:
            continue
        ax.plot(row["t"], row["value"], color=color, linewidth=lw,
                linestyle=ls, label=label)
        last = row.dropna(subset=["value"]).iloc[-1]
        ax.annotate(f"{label}  {last['value']:,.0f}",
                    xy=(last["t"], last["value"]),
                    xytext=(5, 0), textcoords="offset points",
                    color=color, fontsize=7, va="center")

    ax.set_title("Vývoj ekonomických subjektov podľa právnej formy  (SR, 2020–2025)", pad=8)
    ax.set_ylabel("Počet subjektov")
    xticks = list(range(2020, 2026))
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticks)
    ax.set_xlim(2020 - 0.1, 2025.5)
    ax.legend(framealpha=0, labelcolor=STYLE["text"], fontsize=8)
    apply_dark(ax, yformat=lambda x, _: f"{x:,.0f}")


# ── GRAF 2: Top NACE odvetvia – počet podnikateľských subjektov (2024 Q1) ────

NACE_SKIP = {"nace1", "nace2ZZ"}

def plot_nace_top(ax, df):
    sub = df[
        (df["og2021qs_form"] == "05frm010") &       # podnikateľské subjekty
        (df["og2021qs_rok"] == "2024") &
        (df["og2021qs_stv"] == "1.Q.") &
        (~df["og2021qs_nace2"].isin(NACE_SKIP)) &
        (df["og2021qs_nace2"] != "nace2C")           # agregát – vynechaj
    ].copy()
    sub = sub.dropna(subset=["value"])
    sub["label"] = sub["og2021qs_nace2_label"].str.replace(r"^[A-Z]{2} ", "", regex=True)
    sub = sub.nlargest(15, "value")
    sub = sub.sort_values("value", ascending=True)

    cmap_vals = np.linspace(0.2, 0.85, len(sub))
    colors = [plt.cm.YlGn(v) for v in cmap_vals]

    bars = ax.barh(range(len(sub)), sub["value"], color=colors, height=0.7)
    ax.set_yticks(range(len(sub)))
    ax.set_yticklabels(sub["label"].str.slice(0, 42), fontsize=7.5, color=STYLE["text"])

    for bar, val in zip(bars, sub["value"]):
        ax.text(bar.get_width() + 500, bar.get_y() + bar.get_height() / 2,
                f"{val:,.0f}", va="center", fontsize=7.5, color=STYLE["text"])

    ax.set_title("Top 15 odvetví – počet podnikateľských subjektov  (SR, 2024 Q1)", pad=8)
    ax.set_xlabel("Počet subjektov")
    ax.set_xlim(0, sub["value"].max() * 1.18)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    apply_dark(ax)
    ax.yaxis.set_major_formatter(mticker.NullFormatter())
    ax.grid(axis="x", color=STYLE["grid"], linewidth=0.6, linestyle="--")
    ax.grid(axis="y", visible=False)


# ── GRAF 3: Priemerná mzda podľa odvetvia NACE (od0008ms, 2024) ──────────────

NACE_MZDA_LABELS = {
    "NACE02": "Ťažobný priemysel",
    "NACE03": "Potravinárstvo",
    "NACE04": "Textil a odev",
    "NACE05": "Drevospracujúci",
    "NACE06": "Chemický priemysel",
    "NACE07": "Kovospracujúci",
    "NACE08": "Elektrotechnika",
    "NACE09": "Strojárstvo",
    "NACE10": "Dopravné prostriedky",
    "NACE11": "Ostatná výroba",
    "NACE12": "Energia a voda",
    "NACE13": "Stavebníctvo",
    "NACE14": "Obchod a opravovňe",
    "NACE15": "Doprava a sklad.",
}

def plot_wage_by_sector(ax, df):
    sub = df[
        (df["od0008ms_year"] == "2024") &
        (df["od0008ms_month"] == "12.") &
        (df["od0008ms_nace2"] != "NACE15") |
        (
            (df["od0008ms_year"] == "2024") &
            (df["od0008ms_month"].isin(["11.", "10."])) &
            (df["od0008ms_nace2"].isin(NACE_MZDA_LABELS))
        )
    ].copy()

    # Bober: vezmi pre každý NACE posledný dostupný mesiac
    latest = (
        df[(df["od0008ms_year"] == "2024") & (df["od0008ms_nace2"].isin(NACE_MZDA_LABELS))]
        .sort_values("od0008ms_month")
        .groupby("od0008ms_nace2")
        .last()
        .reset_index()
    )
    latest["label"] = latest["od0008ms_nace2"].map(NACE_MZDA_LABELS)
    latest = latest.sort_values("value", ascending=True)

    # Farba podľa výšky mzdy
    cmap_vals = np.linspace(0.15, 0.85, len(latest))
    colors = [plt.cm.RdYlGn(v) for v in cmap_vals]

    bars = ax.barh(range(len(latest)), latest["value"], color=colors, height=0.7)
    ax.set_yticks(range(len(latest)))
    ax.set_yticklabels(latest["label"], fontsize=8, color=STYLE["text"])

    for bar, val in zip(bars, latest["value"]):
        ax.text(bar.get_width() + 20, bar.get_y() + bar.get_height() / 2,
                f"{val:,.0f} €", va="center", fontsize=8, color=STYLE["text"])

    ax.set_title("Priemerná hrubá mzda podľa odvetvia  (SR, 2024)", pad=8)
    ax.set_xlabel("EUR / mesiac")
    ax.set_xlim(0, latest["value"].max() * 1.22)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f} €"))
    apply_dark(ax)
    ax.yaxis.set_major_formatter(mticker.NullFormatter())
    ax.grid(axis="x", color=STYLE["grid"], linewidth=0.6, linestyle="--")
    ax.grid(axis="y", visible=False)


# ── GRAF 4: Štruktúra podnikov podľa veľkosti – grouped bar ──────────────────

FORMY_BAR = {
    "FORM03": ("Spol. s r.o.",   GREEN[3]),
    "FORM02": ("Akciové spol.",  BLUE[2]),
    "FORM09": ("Živnostníci",    ORANGE),
    "FORM13": ("FO-podnikatelia",PURPLE),
}
VELKOSTI = {
    "UKAZ01": ("Malé (0–49)",    GREEN[2]),
    "UKAZ03": ("Stredné (50–249)",BLUE[1]),
    "UKAZ04": ("Veľké (250+)",   RED),
}

def plot_size_structure(ax, df):
    sub = df[
        (df["og1007rs_rok"] == "2024") &
        (df["og1007rs_ukaz"].isin(VELKOSTI)) &
        (df["og1007rs_form"].isin(FORMY_BAR))
    ].copy()

    forms = list(FORMY_BAR.keys())
    form_labels = [FORMY_BAR[f][0] for f in forms]
    x = np.arange(len(forms))
    n_vel = len(VELKOSTI)
    total_w = 0.72
    bar_w = total_w / n_vel

    for i, (ukaz, (vel_label, color)) in enumerate(VELKOSTI.items()):
        vals = []
        for form in forms:
            row = sub[(sub["og1007rs_ukaz"] == ukaz) & (sub["og1007rs_form"] == form)]
            vals.append(row["value"].values[0] if not row.empty else 0)
        offset = (i - (n_vel - 1) / 2) * bar_w
        bars = ax.bar(x + offset, vals, bar_w * 0.92, color=color,
                      label=vel_label, edgecolor=STYLE["bg"], linewidth=0.5)
        for bar, val in zip(bars, vals):
            if val > 50:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 80,
                        f"{val:,.0f}", ha="center", fontsize=6.5, color=STYLE["sub"])

    ax.set_xticks(x)
    ax.set_xticklabels(form_labels, color=STYLE["text"], fontsize=8.5)
    ax.set_title("Počet podnikov podľa veľkosti a právnej formy  (SR, 2024)", pad=8)
    ax.set_ylabel("Počet podnikov")
    ax.legend(framealpha=0, labelcolor=STYLE["text"], fontsize=8)
    apply_dark(ax, yformat=lambda x, _: f"{x:,.0f}")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    df_subj  = load("og2019qs")
    df_nace  = load("og2021qs")
    df_mzda  = load("od0008ms")
    df_velk  = load("og1007rs")

    fig, axes = plt.subplots(2, 2, figsize=(20, 13))
    fig.patch.set_facecolor(STYLE["bg"])
    fig.suptitle("Ekonomická analýza Slovenska  |  ŠÚ SR DATAcube",
                 color=STYLE["text"], fontsize=15, fontweight="bold", y=0.98)

    plot_subjects_trend(axes[0, 0], df_subj)
    plot_nace_top(axes[0, 1], df_nace)
    plot_wage_by_sector(axes[1, 0], df_mzda)
    plot_size_structure(axes[1, 1], df_velk)

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    out = OUT / "economics_analysis.png"
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"✓ Uložené: {out}")


if __name__ == "__main__":
    main()
