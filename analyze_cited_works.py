# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 17:25:55 2025

@author: nli022
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

data = pd.read_excel('C:/Users/nli022/OneDrive - University of Bergen/paper/Paper for ACIS/data for ASIC.xlsx')
# ---- 1. Ensure numeric columns ----
data['Year'] = pd.to_numeric(data['Year'], errors='coerce')
data['citation'] = pd.to_numeric(data['citation'], errors='coerce')

# -------------------------
# 2. Create 10-year bins
# -------------------------
start = (data['Year'].min() // 10) * 10
end = (data['Year'].max() // 10 + 1) * 10
bins = list(range(start, end + 1, 10))
labels = [f"{bins[i]}-{bins[i+1]-1}" for i in range(len(bins)-1)]
data['Period'] = pd.cut(data['Year'], bins=bins, labels=labels, right=False)

# -------------------------
# 3. Standardize categorical columns
# -------------------------
# Paper
data['paper_availability_final'] = data['paper availability'].str.strip().str.lower().map({
    'open access': 'Open access', 'not open': 'Not open'
})
# Code
data['code_availability_final'] = data['code availability'].str.strip().str.lower().map({
    'yes': 'Yes', 'no': 'No', 'on request': 'On request'
})
# Data
data['data_availability_final'] = data['Data availability'].str.strip().str.lower().map({
    'yes': 'Yes', 'no': 'No', 'on request': 'On request'
})
# AI
data['AI_included_final'] = data['AI included'].str.strip().str.lower().map({
    'yes': 'Yes', 'no': 'No'
})

# -------------------------
# 4. Group categorical trends and ensure all categories present
# -------------------------
def group_trend(col, categories):
    trend = data.groupby(['Period', col]).size().unstack(fill_value=0)
    trend = trend.reindex(columns=categories, fill_value=0)
    return trend.loc[trend.sum(axis=1) > 0]

trend_paper = group_trend('paper_availability_final', ["Open access", "Not open"])
trend_code = group_trend('code_availability_final', ["Yes", "No", "On request"])
trend_data = group_trend('data_availability_final', ["Yes", "No", "On request"])
trend_ai = group_trend('AI_included_final', ["Yes", "No"])

# -------------------------
# 5. Define fixed colors for consistent legend
# -------------------------
paper_colors = {"Open access": "tab:blue", "Not open": "tab:orange"}
code_colors = {"Yes": "tab:green", "No": "tab:red", "On request": "tab:purple"}
data_colors = {"Yes": "tab:cyan", "No": "tab:brown", "On request": "tab:pink"}
ai_colors = {"Yes": "tab:olive", "No": "tab:gray"}

# -------------------------
# 6. Create figure with subplots
# -------------------------
fig, axes = plt.subplots(5, 2, figsize=(16, 25))  # 5 rows × 2 columns
plt.subplots_adjust(hspace=0.5)

# --- Row 1: Paper Availability ---
trend_paper.plot(kind='bar', ax=axes[0,0], color=[paper_colors[c] for c in trend_paper.columns])
axes[0,0].set_title("Paper Availability Counts")
axes[0,0].set_ylabel("Number of Papers")
axes[0,0].set_xlabel("Period")
axes[0,0].legend(title="Paper Availability")

(trend_paper.div(trend_paper.sum(axis=1), axis=0) * 100).plot(
    kind='bar', stacked=True, ax=axes[0,1], color=[paper_colors[c] for c in trend_paper.columns]
)
axes[0,1].set_title("Paper Availability (%)")
axes[0,1].set_ylabel("Percentage")
axes[0,1].set_xlabel("Period")
axes[0,1].legend(title="Paper Availability")

# --- Row 2: Code Availability ---
trend_code.plot(kind='bar', ax=axes[1,0], color=[code_colors[c] for c in trend_code.columns])
axes[1,0].set_title("Code Availability Counts")
axes[1,0].set_ylabel("Number of Papers")
axes[1,0].set_xlabel("Period")
axes[1,0].legend(title="Code Availability")

(trend_code.div(trend_code.sum(axis=1), axis=0) * 100).plot(
    kind='bar', stacked=True, ax=axes[1,1], color=[code_colors[c] for c in trend_code.columns]
)
axes[1,1].set_title("Code Availability (%)")
axes[1,1].set_ylabel("Percentage")
axes[1,1].set_xlabel("Period")
axes[1,1].legend(title="Code Availability")

# --- Row 3: Data Availability ---
trend_data.plot(kind='bar', ax=axes[2,0], color=[data_colors[c] for c in trend_data.columns])
axes[2,0].set_title("Data Availability Counts")
axes[2,0].set_ylabel("Number of Papers")
axes[2,0].set_xlabel("Period")
axes[2,0].legend(title="Data Availability")

(trend_data.div(trend_data.sum(axis=1), axis=0) * 100).plot(
    kind='bar', stacked=True, ax=axes[2,1], color=[data_colors[c] for c in trend_data.columns]
)
axes[2,1].set_title("Data Availability (%)")
axes[2,1].set_ylabel("Percentage")
axes[2,1].set_xlabel("Period")
axes[2,1].legend(title="Data Availability")

# --- Row 4: AI Included ---
trend_ai.plot(kind='bar', ax=axes[3,0], color=[ai_colors[c] for c in trend_ai.columns])
axes[3,0].set_title("AI Included Counts")
axes[3,0].set_ylabel("Number of Papers")
axes[3,0].set_xlabel("Period")
axes[3,0].legend(title="AI Included")

(trend_ai.div(trend_ai.sum(axis=1), axis=0) * 100).plot(
    kind='bar', stacked=True, ax=axes[3,1], color=[ai_colors[c] for c in trend_ai.columns]
)
axes[3,1].set_title("AI Included (%)")
axes[3,1].set_ylabel("Percentage")
axes[3,1].set_xlabel("Period")
axes[3,1].legend(title="AI Included")

# --- Row 5: Citation plots side by side ---
# Citation vs Paper Availability
sns.scatterplot(
    data=data, x='Year', y='citation', hue='paper_availability_final',
    ax=axes[4,0], s=50, palette=paper_colors
)
sns.regplot(data=data, x='Year', y='citation', scatter=False, color='gray', ax=axes[4,0])
axes[4,0].set_title("Citation vs Year by Paper Availability")
axes[4,0].set_ylabel("Citations")
axes[4,0].set_xlabel("Year")
axes[4,0].legend(title="Paper Availability")

# Citation vs Data Availability
sns.scatterplot(
    data=data, x='Year', y='citation', hue='data_availability_final',
    ax=axes[4,1], s=50, palette=data_colors
)
sns.regplot(data=data, x='Year', y='citation', scatter=False, color='gray', ax=axes[4,1])
axes[4,1].set_title("Citation vs Year by Data Availability")
axes[4,1].set_ylabel("Citations")
axes[4,1].set_xlabel("Year")
axes[4,1].legend(title="Data Availability")

# -------------------------
plt.tight_layout()
plt.savefig("all_trends_combined_fixed_colors.png", dpi=300)
plt.show()
