import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import argparse

parser = argparse.ArgumentParser(description="Visualize article analysis results")
parser.add_argument(
    "--input",
    "-i",
    type=str,
    required=True,
    help="Path to the input CSV file",
)
parser.add_argument(
    "--categories",
    "-c",
    type=str,
    nargs="+",
    default=["All"],
    help="List of categories to include in the analysis",
)
args = parser.parse_args()
categories = args.categories

# Load the data
df = pd.read_csv(args.input)

# Restrict to given categories
if categories != ["All"]:
    df = df[df["category"].isin(categories)]

# Display the categories
df_by_category = df.groupby("category")
category_counts = df_by_category.size()
plt.figure("Category distribution")
plt.pie(category_counts, labels=category_counts.index, autopct="%1.1f%%")
plt.title("Category Distribution")
plt.show()


# Display the subcategories
df_by_subcategory = df.groupby("subcategory")
subcategory_counts = df_by_subcategory.size()
plt.figure("Subcategory distribution")
plt.pie(subcategory_counts, labels=subcategory_counts.index, autopct="%1.1f%%")
plt.title("Subcategory Distribution")
plt.show()


def statistics_over_time(df, column, entries):
    num_entries = len(entries)
    # Use intuitive colors for open, conditional, closed
    # Open: green, Conditional: orange, Closed: red
    base_open = ["#4CAF50", "#81C784", "#388E3C"]  # green shades
    base_conditional = ["#FF9800", "#FFB74D", "#F57C00"]  # orange shades
    base_closed = ["#F44336", "#E57373", "#B71C1C"]  # red shades
    open_colors = (base_open * ((num_entries // len(base_open)) + 1))[:num_entries]
    conditional_colors = (
        base_conditional * ((num_entries // len(base_conditional)) + 1)
    )[:num_entries]
    closed_colors = (base_closed * ((num_entries // len(base_closed)) + 1))[
        :num_entries
    ]

    # assert set(df[column].unique().tolist()) == set(entries)
    years = []
    total_counts = {group: [] for group in df[column].unique()}
    open_access_counts = {group: [] for group in df[column].unique()}
    closed_access_counts = {group: [] for group in df[column].unique()}
    open_access_data_availability_counts = {group: [] for group in df[column].unique()}
    closed_access_data_availability_counts = {
        group: [] for group in df[column].unique()
    }
    conditional_access_data_availability_counts = {
        group: [] for group in df[column].unique()
    }

    # Make statistics over time
    df_by_year = df.groupby("year")
    for year_value, year_group in df_by_year:
        if year_value <= 2018:
            continue

        years.append(year_value)
        df_by_column = year_group.groupby(column)
        for entry in entries:
            if entry not in df_by_column.groups:
                # No entries for this category in this year
                total_counts[entry].append(0)
                open_access_counts[entry].append(0)
                closed_access_counts[entry].append(0)
                open_access_data_availability_counts[entry].append(0)
                closed_access_data_availability_counts[entry].append(0)
                conditional_access_data_availability_counts[entry].append(0)
            else:
                entry_group = df_by_column.get_group(entry)
                total_counts[entry].append(len(entry_group))
                open_access_counts[entry].append(
                    np.sum(entry_group["article_availability_score"] == 1)
                )
                closed_access_counts[entry].append(
                    np.sum(entry_group["article_availability_score"] == 0)
                )
                open_access_data_availability_counts[entry].append(
                    np.sum(entry_group["data_availability_score"] == 1)
                )
                closed_access_data_availability_counts[entry].append(
                    np.sum(entry_group["data_availability_score"] == 0)
                )
                conditional_access_data_availability_counts[entry].append(
                    np.sum(entry_group["data_availability_score"] == 0.5)
                )

    width = 0.6
    x = np.arange(len(years))
    num_entries = len(entries)
    displacement = np.linspace(
        -width / num_entries, width / num_entries, num_entries + 1
    )[:-1]

    # Additional plot: Total article counts over the years (no availability info)
    plt.figure("Total Article Counts Over Time")
    for idx, entry in enumerate(entries):
        plt.bar(
            x + displacement[idx],
            np.array(total_counts[entry]),
            label=entry,
            color=np.array([0.8, 0.8, 0.8]) * (num_entries - idx / 2) / num_entries,
        )
    plt.xlabel("Year")
    plt.ylabel("Number of articles")
    plt.title("Total Article Counts Over Time")
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.tight_layout()
    plt.show()

    plt.figure("Open vs closed access over time (stacked bar)")

    for idx, entry in enumerate(entries):
        if entry not in total_counts:
            continue
        plt.bar(
            x + displacement[idx],
            np.array(open_access_counts[entry]),
            width=width / 2,
            label=f"{entry} - Open",
            color=open_colors[idx],
        )
        plt.bar(
            x + displacement[idx],
            np.array(closed_access_counts[entry]),
            width=width / 2,
            bottom=np.array(open_access_counts[entry]),
            label=f"{entry} - Closed",
            color=closed_colors[idx],
        )

    plt.xticks(x, years)
    plt.xlabel("Year")
    plt.ylabel("Number of articles")
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.title("Open vs Closed Access Over Time (Stacked Bar)")
    plt.tight_layout()
    plt.show()

    # Additional plot: Data availability (open, conditional, closed) over time,
    # split by category
    plt.figure("Data availability over time (stacked bar)")
    width = 0.6
    x = np.arange(len(years))

    # Stacked bars for computational
    for idx, entry in enumerate(entries):
        if entry not in total_counts:
            continue
        data_open = np.array(open_access_data_availability_counts[entry])
        data_conditional = np.array(conditional_access_data_availability_counts[entry])
        data_closed = np.array(closed_access_data_availability_counts[entry])
        plt.bar(
            x + displacement[idx],
            data_open,
            width=width / 2,
            label=f"{entry} - Open",
            color=open_colors[idx],
        )
        plt.bar(
            x + displacement[idx],
            data_conditional,
            width=width / 2,
            bottom=data_open,
            label=f"{entry} - Conditional",
            color=conditional_colors[idx],
        )
        plt.bar(
            x + displacement[idx],
            data_closed,
            width=width / 2,
            bottom=data_open + data_conditional,
            label=f"{entry} - Closed",
            color=closed_colors[idx],
        )

    plt.xticks(x, years)
    plt.xlabel("Year")
    plt.ylabel("Number of articles")
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.title("Data Availability Over Time (Stacked Bar)")
    plt.tight_layout()
    plt.show()

    # Additional plot: Article availability (open, closed) over time, relative to total counts (percent)
    plt.figure("Relative Article availability over time (stacked bar, %)")
    for idx, entry in enumerate(entries):
        if entry not in total_counts:
            continue
        article_total = np.array(total_counts[entry])
        article_open = np.array(open_access_counts[entry])
        article_closed = np.array(closed_access_counts[entry])
        article_open_rel = np.where(
            article_total > 0, 100 * article_open / article_total, 0
        )
        article_closed_rel = np.where(
            article_total > 0, 100 * article_closed / article_total, 0
        )
        plt.bar(
            x + displacement[idx],
            article_open_rel,
            width=width / num_entries,
            label=f"{entry} - Open",
            color=open_colors[idx],
        )
        plt.bar(
            x + displacement[idx],
            article_closed_rel,
            width=width / num_entries,
            bottom=article_open_rel,
            label=f"{entry} - Closed",
            color=closed_colors[idx],
        )

    plt.xticks(x, years)
    plt.xlabel("Year")
    plt.ylabel("Percent of articles [%]")
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.title("Relative Article Availability Over Time (Stacked Bar, %)")
    plt.ylim(0, 100)
    plt.tight_layout()
    plt.show()

    # Additional plot: Data availability (open, conditional, closed) over time,
    # split by category, relative to total counts (percent)
    plt.figure("Relative Data availability over time (stacked bar, %)")
    for idx, entry in enumerate(entries):
        if entry not in total_counts:
            continue
        data_total = np.array(total_counts[entry])
        data_open = np.array(open_access_data_availability_counts[entry])
        data_conditional = np.array(conditional_access_data_availability_counts[entry])
        data_closed = np.array(closed_access_data_availability_counts[entry])
        data_open_rel = 100 * data_open / data_total
        data_conditional_rel = np.where(
            data_total > 0, 100 * data_conditional / data_total, 0
        )
        data_closed_rel = np.where(data_total > 0, 100 * data_closed / data_total, 0)
        plt.bar(
            x + displacement[idx],
            data_open_rel,
            width=width / num_entries,
            label=f"{entry} - Open",
            color=open_colors[idx],
        )
        plt.bar(
            x + displacement[idx],
            data_conditional_rel,
            width=width / num_entries,
            bottom=data_open_rel,
            label=f"{entry} - Conditional",
            color=conditional_colors[idx],
        )
        plt.bar(
            x + displacement[idx],
            data_closed_rel,
            width=width / num_entries,
            bottom=data_open_rel + data_conditional_rel,
            label=f"{entry} - Closed",
            color=closed_colors[idx],
        )

    plt.xticks(x, years)
    plt.xlabel("Year")
    plt.ylabel("Percent of articles [%]")
    # Put the legend to the top left corner of the plot
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.title("Relative Data Availability Over Time (Stacked Bar, %)")
    plt.ylim(0, 100)
    plt.tight_layout()
    plt.show()


statistics_over_time(
    df,
    "category",
    ["computational", "experimental"],  # , "other", "theoretical"]
)
statistics_over_time(
    df,
    "subcategory",
    ["simulation", "imaging"],  # , "computational", "experimental", "ml"]
)
# statistics_over_time(
#    df,
#    "subcategory2",
#    ["pde", "simulation"],  # , "computational", "experimental", "ml"]
# )
