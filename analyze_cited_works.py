# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 17:25:55 2025

@author: nli022
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

path = Path("../database") / "cited_works.xlsx"
save_folder = Path("../results")
save_folder.mkdir(parents=True, exist_ok=True)

# 0. Load data
data = pd.read_excel(path, sheet_name="Ark1")
data = data[data["Year"] > 1995]

# ---- 1. Ensure numeric columns ----
data["Year"] = pd.to_numeric(data["Year"], errors="coerce")
data["citation"] = pd.to_numeric(data["citation"], errors="coerce")

# -------------------------
# 2. Create 5-year bins 2021-2025, 2016-2020, etc.
# -------------------------
bin_size = 5
start = 1996
end = 2026
bins = list(range(start, end + 1, bin_size))
labels = [f"{bins[i]}-{bins[i + 1] - 1}" for i in range(len(bins) - 1)]
data["Period"] = pd.cut(data["Year"], bins=bins, labels=labels, right=False)

# -------------------------
# 3. Standardize categorical columns
# -------------------------
# Paper
data["paper_availability_final"] = (
    data["paper availability"]
    .str.strip()
    .str.lower()
    .map({"open access": "Open access", "not open": "Not open"})
)
# Code
data["code_availability_final"] = (
    data["code availability"]
    .str.strip()
    .str.lower()
    .map({"yes": "Yes", "no": "No", "on request": "On request"})
)
# Data
data["data_availability_final"] = (
    data["Data availability"]
    .str.strip()
    .str.lower()
    .map({"yes": "Yes", "no": "No", "on request": "On request"})
)
# AI
data["AI_included_final"] = (
    data["AI included"].str.strip().str.lower().map({"yes": "Yes", "no": "No"})
)


# -------------------------
# 4. Group categorical trends and ensure all categories present
# -------------------------
def group_trend(col, categories):
    trend = data.groupby(["Period", col]).size().unstack(fill_value=0)
    trend = trend.reindex(columns=categories, fill_value=0)
    return trend.loc[trend.sum(axis=1) > 0]


def return_total_number_per_period(col):
    trend = data.groupby(["Period", col]).size().unstack(fill_value=0)
    return trend.loc[trend.sum(axis=1) > 0].sum(axis=1)


trend_paper = group_trend("paper_availability_final", ["Open access", "Not open"])
trend_code = group_trend("code_availability_final", ["Yes", "On request", "No"])
trend_data = group_trend("data_availability_final", ["Yes", "On request", "No"])
trend_ai = group_trend("AI_included_final", ["Yes", "No"])

# -------------------------
# 5. Define fixed colors for consistent legend
# -------------------------
paper_colors = {
    "Not open": "tab:red",
    "Open access": "tab:green",
}
code_colors = {
    "No": "tab:red",
    "On request": "#FFC300",  # bright dark yellow
    "Yes": "tab:green",
}
data_colors = {
    "No": "tab:red",
    "On request": "#FFC300",  # bright dark yellow
    "Yes": "tab:green",
}
ai_colors = {
    "No": "tab:pink",
    "Yes": "tab:blue",
}


# -------------------------
# 6. Create figure with subplots
# -------------------------
# Set global font size for all plots
plt.rcParams.update({"font.size": 20})
dpi = 1000


# --- Grouped Pie Charts: Paper, Code, Data Availability ---
def autopct_func(pct):
    return f"{pct:.1f}%" if pct > 0 else ""


fig_paper, axes_paper = plt.subplots(
    1, len(trend_paper.index), figsize=(4 * len(trend_paper.index), 4)
)
if len(trend_paper.index) == 1:
    axes_paper = [axes_paper]
for i, period in enumerate(trend_paper.index):
    values = trend_paper.loc[period]
    wedges, texts, autotexts = axes_paper[i].pie(
        values,
        labels=None,  # No labels on the pie
        autopct=autopct_func,  # Show percent only if > 0
        colors=[paper_colors[c] for c in values.index],
        startangle=90,
        counterclock=False,
        textprops={"color": "white", "fontsize": 16},
        wedgeprops={"edgecolor": "white", "linewidth": 1},
    )
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontweight("bold")
    # Place period label below the pie (line split for PEP8)
    axes_paper[i].text(
        0.5,
        -0.00,
        f"{period}",
        ha="center",
        va="center",
        transform=axes_paper[i].transAxes,
        fontsize=16,
    )
    # Add total count just below the period label
    total = int(values.sum())
    axes_paper[i].text(
        0.5,
        -0.10,
        f"#total: {total}",
        ha="center",
        va="center",
        transform=axes_paper[i].transAxes,
        fontsize=14,
    )
# Add a single legend to the last pie only, using the last values and wedges
axes_paper[-1].legend(
    wedges,
    values.index,
    title="Paper Availability",
    loc="center left",
    bbox_to_anchor=(1, 0.5),
)
fig_paper.text(
    0.01,
    0.5,
    "Paper Availability",
    va="center",
    ha="center",
    rotation=90,
    fontsize=16,
    transform=fig_paper.transFigure,
)
plt.tight_layout()
fig_paper.savefig(save_folder / "cited_works_paper_availability_pies.png", dpi=dpi)
plt.show()

fig_code, axes_code = plt.subplots(
    1, len(trend_code.index), figsize=(4 * len(trend_code.index), 4)
)
if len(trend_code.index) == 1:
    axes_code = [axes_code]
for i, period in enumerate(trend_code.index):
    values = trend_code.loc[period]
    wedges, texts, autotexts = axes_code[i].pie(
        values,
        labels=None,
        autopct=autopct_func,
        colors=[code_colors[c] for c in values.index],
        startangle=90,
        counterclock=False,
        textprops={"color": "white", "fontsize": 16},
        wedgeprops={"edgecolor": "white", "linewidth": 1},
    )
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontweight("bold")
    axes_code[i].text(
        0.5,
        -0.0,
        f"{period}",
        ha="center",
        va="center",
        transform=axes_code[i].transAxes,
        fontsize=16,
    )
    # Add total count just below the period label
    total = int(values.sum())
    axes_code[i].text(
        0.5,
        -0.10,
        f"#total: {total}",
        ha="center",
        va="center",
        transform=axes_code[i].transAxes,
        fontsize=14,
    )
axes_code[-1].legend(
    wedges,
    values.index,
    title="Code Availability",
    loc="center left",
    bbox_to_anchor=(1, 0.5),
)
fig_code.text(
    0.01,
    0.5,
    "Code Availability",
    va="center",
    ha="center",
    rotation=90,
    fontsize=16,
    transform=fig_code.transFigure,
)
plt.tight_layout()
fig_code.savefig(save_folder / "cited_works_code_availability_pies.png", dpi=dpi)
plt.show()

fig_data, axes_data = plt.subplots(
    1, len(trend_data.index), figsize=(4 * len(trend_data.index), 4)
)
if len(trend_data.index) == 1:
    axes_data = [axes_data]
for i, period in enumerate(trend_data.index):
    values = trend_data.loc[period]
    wedges, texts, autotexts = axes_data[i].pie(
        values,
        labels=None,
        autopct=autopct_func,
        colors=[data_colors[c] for c in values.index],
        startangle=90,
        counterclock=False,
        textprops={"color": "white", "fontsize": 16},
        wedgeprops={"edgecolor": "white", "linewidth": 1},
    )
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontweight("bold")
    axes_data[i].text(
        0.5,
        -0.0,
        f"{period}",
        ha="center",
        va="center",
        transform=axes_data[i].transAxes,
        fontsize=16,
    )
    # Add total count just below the period label
    total = int(values.sum())
    axes_data[i].text(
        0.5,
        -0.10,
        f"#total: {total}",
        ha="center",
        va="center",
        transform=axes_data[i].transAxes,
        fontsize=14,
    )
axes_data[-1].legend(
    wedges,
    values.index,
    title="Data Availability",
    loc="center left",
    bbox_to_anchor=(1, 0.5),
)
fig_data.text(
    0.01,
    0.5,
    "Data Availability",
    va="center",
    ha="center",
    rotation=90,
    fontsize=16,
    transform=fig_data.transFigure,
)
plt.tight_layout()
fig_data.savefig(save_folder / "cited_works_data_availability_pies.png", dpi=dpi)
plt.show()

# --- AI Included Bar Plot ---
(trend_ai.div(trend_ai.sum(axis=1), axis=0) * 100).plot(
    kind="bar",
    stacked=True,
    color=[ai_colors[c] for c in trend_ai.columns],
)
plt.title("AI Included over time (%)")
plt.ylabel("Percentage")
plt.legend(title="AI Included")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

# --- Citation vs Paper Availability ---
fig, ax = plt.subplots(figsize=(8, 5))
sns.scatterplot(
    data=data,
    x="Year",
    y="citation",
    hue="paper_availability_final",
    s=50,
    palette=paper_colors,
    ax=ax,
)
for period in labels:
    period_data = data[data["Period"] == period][
        data["paper_availability_final"] == "Open access"
    ]
    if not period_data.empty:
        sns.regplot(
            data=period_data,
            x="Year",
            y="citation",
            scatter=False,
            ax=ax,
            color="tab:green",
        )
    period_data = data[data["Period"] == period][
        data["paper_availability_final"] == "Not open"
    ]
    if not period_data.empty:
        sns.regplot(
            data=period_data,
            x="Year",
            y="citation",
            scatter=False,
            ax=ax,
            color="tab:red",
        )
ax.set_title("Citation vs Year by Paper Availability")
ax.set_ylabel("Citations")
ax.set_xlabel("Year")
ax.set_yscale("log")
ax.legend(title="Paper Availability")
plt.tight_layout()
plt.show()

# --- Citation vs Data Availability ---
fig, ax = plt.subplots(figsize=(8, 5))
sns.scatterplot(
    data=data,
    x="Year",
    y="citation",
    hue="data_availability_final",
    s=50,
    palette=data_colors,
    ax=ax,
)
for period in labels:
    period_data = data[data["Period"] == period][
        (data["data_availability_final"] == "Yes")
        | (data["data_availability_final"] == "On request")
    ]
    if not period_data.empty:
        sns.regplot(
            data=period_data,
            x="Year",
            y="citation",
            scatter=False,
            ax=ax,
            color="tab:green",
        )
    period_data = data[data["Period"] == period][
        data["data_availability_final"] == "No"
    ]
    if not period_data.empty:
        sns.regplot(
            data=period_data,
            x="Year",
            y="citation",
            scatter=False,
            ax=ax,
            color="tab:red",
        )
ax.set_title("Citation vs Year by Data Availability")
ax.set_ylabel("Citations")
ax.set_xlabel("Year")
ax.set_yscale("log")
ax.legend(title="Data Availability")
plt.tight_layout()
plt.show()
