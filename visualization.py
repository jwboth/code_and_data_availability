import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("tipm_analysis.csv")

# Group by experimental and computational in the column "discipline"
df_by_discipline = df.groupby("discipline")
print(df_by_discipline.size())

# Extract the computational and experimental dataframes
df_computational = df_by_discipline.get_group("computational")
df_experimental = df_by_discipline.get_group("experimental")

# Make statistics based on the article_availability score
print(df_computational["article_availability_score"].describe())
print(df_experimental["article_availability_score"].describe())

# Total score statistics
print("----- Computational - article availability -----")
print(np.sum(df_computational["article_availability_score"] == 1))
print(np.sum(df_computational["article_availability_score"] == 0))
print()

print("----- Experimental - article availability -----")
print(np.sum(df_experimental["article_availability_score"] == 1))
print(np.sum(df_experimental["article_availability_score"] == 0))
print()

# Make the same for data_availability_score
print("----- Computational - data availability -----")
print(np.sum(df_computational["data_availability_score"] > 0.1))
print(np.sum(df_computational["data_availability_score"] == 1))
print(np.sum(df_computational["data_availability_score"] == 0.5))
print(np.sum(df_computational["data_availability_score"] == 0))
print()

print("----- Experimental - data availability -----")
print(np.sum(df_experimental["data_availability_score"] > 0.1))
print(np.sum(df_experimental["data_availability_score"] == 1))
print(np.sum(df_experimental["data_availability_score"] == 0.5))
print(np.sum(df_experimental["data_availability_score"] == 0))
print()

# Make statistics over time
df_by_year = df.groupby("year")
years = []
total_counts = {discipline: [] for discipline in df["discipline"].unique()}
open_access_counts = {discipline: [] for discipline in df["discipline"].unique()}
closed_access_counts = {discipline: [] for discipline in df["discipline"].unique()}
open_access_data_availability_counts = {
    discipline: [] for discipline in df["discipline"].unique()
}
closed_access_data_availability_counts = {
    discipline: [] for discipline in df["discipline"].unique()
}
conditional_access_data_availability_counts = {
    discipline: [] for discipline in df["discipline"].unique()
}
for year, group in df_by_year:
    years.append(year)
    df_sub_by_discipline = group.groupby("discipline")
    for discipline, subgroup in df_sub_by_discipline:
        total_count = len(subgroup)
        total_counts[discipline].append(total_count)

        open_access_count = np.sum(subgroup["article_availability_score"] == 1)
        closed_access_count = np.sum(subgroup["article_availability_score"] == 0)
        open_access_counts[discipline].append(open_access_count)
        closed_access_counts[discipline].append(closed_access_count)

        closed_access_data_count = np.sum(subgroup["data_availability_score"] == 0)
        open_access_data_count = np.sum(subgroup["data_availability_score"] == 1)
        conditional_access_data_count = np.sum(
            subgroup["data_availability_score"] == 0.5
        )
        open_access_data_availability_counts[discipline].append(open_access_data_count)
        closed_access_data_availability_counts[discipline].append(
            closed_access_data_count
        )
        conditional_access_data_availability_counts[discipline].append(
            conditional_access_data_count
        )

plt.figure("Open vs closed access over time (stacked bar)")
width = 0.6
x = np.arange(len(years))

# Stacked bars for computational
plt.bar(
    x - 0.15,
    np.array(open_access_counts["computational"]),
    width=width / 2,
    label="Computational - Open",
    color="tab:blue",
)
plt.bar(
    x - 0.15,
    np.array(closed_access_counts["computational"]),
    width=width / 2,
    bottom=np.array(open_access_counts["computational"]),
    label="Computational - Closed",
    color="tab:orange",
)

# Stacked bars for experimental
plt.bar(
    x + 0.15,
    np.array(open_access_counts["experimental"]),
    width=width / 2,
    label="Experimental - Open",
    color="tab:green",
)
plt.bar(
    x + 0.15,
    np.array(closed_access_counts["experimental"]),
    width=width / 2,
    bottom=np.array(open_access_counts["experimental"]),
    label="Experimental - Closed",
    color="tab:red",
)

plt.xticks(x, years)
plt.xlabel("Year")
plt.ylabel("Number of articles")
plt.legend()
plt.title("Open vs Closed Access Over Time (Stacked Bar)")
plt.tight_layout()
plt.show()

# Additional plot: Data availability (open, conditional, closed) over time, split by discipline
plt.figure("Data availability over time (stacked bar)")
width = 0.6
x = np.arange(len(years))

# Stacked bars for computational
data_open = np.array(open_access_data_availability_counts["computational"])
data_conditional = np.array(
    conditional_access_data_availability_counts["computational"]
)
data_closed = np.array(closed_access_data_availability_counts["computational"])
plt.bar(
    x - 0.15, data_open, width=width / 2, label="Computational - Open", color="tab:blue"
)
plt.bar(
    x - 0.15,
    data_conditional,
    width=width / 2,
    bottom=data_open,
    label="Computational - Conditional",
    color="tab:gray",
)
plt.bar(
    x - 0.15,
    data_closed,
    width=width / 2,
    bottom=data_open + data_conditional,
    label="Computational - Closed",
    color="tab:orange",
)

# Stacked bars for experimental
data_open_exp = np.array(open_access_data_availability_counts["experimental"])
data_conditional_exp = np.array(
    conditional_access_data_availability_counts["experimental"]
)
data_closed_exp = np.array(closed_access_data_availability_counts["experimental"])
plt.bar(
    x + 0.15,
    data_open_exp,
    width=width / 2,
    label="Experimental - Open",
    color="tab:green",
)
plt.bar(
    x + 0.15,
    data_conditional_exp,
    width=width / 2,
    bottom=data_open_exp,
    label="Experimental - Conditional",
    color="tab:olive",
)
plt.bar(
    x + 0.15,
    data_closed_exp,
    width=width / 2,
    bottom=data_open_exp + data_conditional_exp,
    label="Experimental - Closed",
    color="tab:red",
)

plt.xticks(x, years)
plt.xlabel("Year")
plt.ylabel("Number of articles")
plt.legend()
plt.title("Data Availability Over Time (Stacked Bar)")
plt.tight_layout()
plt.show()

# Additional plot: Data availability (open, conditional, closed) over time, split by discipline, relative to total counts (percent)
plt.figure("Relative Data availability over time (stacked bar, %)")

# For computational
data_total = np.array(total_counts["computational"])
data_open_rel = 100 * data_open / data_total
with np.errstate(divide="ignore", invalid="ignore"):
    data_conditional_rel = np.where(
        data_total > 0, 100 * data_conditional / data_total, 0
    )
    data_closed_rel = np.where(data_total > 0, 100 * data_closed / data_total, 0)
plt.bar(
    x - 0.15,
    data_open_rel,
    width=width / 2,
    label="Computational - Open",
    color="tab:blue",
)
plt.bar(
    x - 0.15,
    data_conditional_rel,
    width=width / 2,
    bottom=data_open_rel,
    label="Computational - Conditional",
    color="tab:gray",
)
plt.bar(
    x - 0.15,
    data_closed_rel,
    width=width / 2,
    bottom=data_open_rel + data_conditional_rel,
    label="Computational - Closed",
    color="tab:orange",
)

# For experimental
data_total_exp = np.array(total_counts["experimental"])
data_open_exp_rel = 100 * data_open_exp / data_total_exp
with np.errstate(divide="ignore", invalid="ignore"):
    data_conditional_exp_rel = np.where(
        data_total_exp > 0, 100 * data_conditional_exp / data_total_exp, 0
    )
    data_closed_exp_rel = np.where(
        data_total_exp > 0, 100 * data_closed_exp / data_total_exp, 0
    )
plt.bar(
    x + 0.15,
    data_open_exp_rel,
    width=width / 2,
    label="Experimental - Open",
    color="tab:green",
)
plt.bar(
    x + 0.15,
    data_conditional_exp_rel,
    width=width / 2,
    bottom=data_open_exp_rel,
    label="Experimental - Conditional",
    color="tab:olive",
)
plt.bar(
    x + 0.15,
    data_closed_exp_rel,
    width=width / 2,
    bottom=data_open_exp_rel + data_conditional_exp_rel,
    label="Experimental - Closed",
    color="tab:red",
)

plt.xticks(x, years)
plt.xlabel("Year")
plt.ylabel("Percent of articles [%]")
plt.legend()
plt.title("Relative Data Availability Over Time (Stacked Bar, %)")
plt.ylim(0, 100)
plt.tight_layout()
plt.show()
