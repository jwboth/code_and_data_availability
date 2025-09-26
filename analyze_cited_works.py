# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 17:25:55 2025

@author: nli022
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

path = Path("cited_works") / "data for ASIC.xlsx"

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
    "On request": "tab:orange",
    "Yes": "tab:green",
}
data_colors = {
    "No": "tab:red",
    "On request": "tab:orange",
    "Yes": "tab:green",
}
ai_colors = {
    "No": "tab:pink",
    "Yes": "tab:blue",
}

# -------------------------
# 6. Create figure with subplots
# -------------------------
# Total number
totals = return_total_number_per_period("paper_availability_final")
fig, axes = plt.subplots(6, 1, figsize=(16, 25))  # 5 rows × 2 columns
plt.subplots_adjust(hspace=20)

# --- Row 1: Paper Availability ---
(trend_paper.div(trend_paper.sum(axis=1), axis=0) * 100).plot(
    kind="bar",
    stacked=True,
    ax=axes[0],
    color=[paper_colors[c] for c in trend_paper.columns],
)

axes[0].set_title("Paper Availability over time (%)")
axes[0].set_ylabel("Percentage")
# Write the x-labels horizontally
# axes[0].set_xlabel("Period", rotation=0)
axes[0].legend(title="Paper Availability")
axes[0].set_xticklabels(axes[0].get_xticklabels(), rotation=0)

# --- Row 2: Code Availability ---
(trend_code.div(trend_code.sum(axis=1), axis=0) * 100).plot(
    kind="bar",
    stacked=True,
    ax=axes[1],
    color=[code_colors[c] for c in trend_code.columns],
)
axes[1].set_title("Code Availability over time (%)")
axes[1].set_ylabel("Percentage")
# axes[1].set_xlabel("Period")
axes[1].legend(title="Code Availability")
axes[1].set_xticklabels(axes[1].get_xticklabels(), rotation=0)

# --- Row 3: Data Availability ---
(trend_data.div(trend_data.sum(axis=1), axis=0) * 100).plot(
    kind="bar",
    stacked=True,
    ax=axes[2],
    color=[data_colors[c] for c in trend_data.columns],
)
axes[2].set_title("Data Availability over time (%)")
axes[2].set_ylabel("Percentage")
# axes[2].set_xlabel("Period")
axes[2].legend(title="Data Availability")
axes[2].set_xticklabels(axes[2].get_xticklabels(), rotation=0)

# --- Row 4: AI Included ---
(trend_ai.div(trend_ai.sum(axis=1), axis=0) * 100).plot(
    kind="bar",
    stacked=True,
    ax=axes[3],
    color=[ai_colors[c] for c in trend_ai.columns],
)
axes[3].set_title("AI Included over time (%)")
axes[3].set_ylabel("Percentage")
# axes[3].set_xlabel("Period")
axes[3].legend(title="AI Included")
axes[3].set_xticklabels(axes[3].get_xticklabels(), rotation=0)

# --- Row 5: Citation plots side by side ---
# Citation vs Paper Availability
sns.scatterplot(
    data=data,
    x="Year",
    y="citation",
    hue="paper_availability_final",
    ax=axes[4],
    s=50,
    palette=paper_colors,
)
# sns.regplot(data=data, x="Year", y="citation", scatter=False, color="gray", ax=axes[4])
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
            ax=axes[4],
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
            ax=axes[4],
            color="tab:red",
        )
axes[4].set_title("Citation vs Year by Paper Availability")
axes[4].set_ylabel("Citations")
axes[4].set_xlabel("Year")
axes[4].set_yscale("log")
axes[4].legend(title="Paper Availability")

# Citation vs Data Availability
sns.scatterplot(
    data=data,
    x="Year",
    y="citation",
    hue="data_availability_final",
    ax=axes[5],
    s=50,
    palette=data_colors,
)
# Make a regression for each period
# sns.regplot(data=data, x="Year", y="citation", scatter=False, color="gray", ax=axes[5])
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
            ax=axes[5],
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
            ax=axes[5],
            color="tab:red",
        )
axes[5].set_title("Citation vs Year by Data Availability")
axes[5].set_ylabel("Citations")
axes[5].set_xlabel("Year")
axes[5].set_yscale("log")
axes[5].legend(title="Data Availability")

for j in range(4):
    for i, total in enumerate(totals):
        axes[j].text(i, 50, str(total), ha="center")

# -------------------------
plt.tight_layout()
plt.savefig("all_trends_combined_fixed_colors.png", dpi=300)
plt.show()
