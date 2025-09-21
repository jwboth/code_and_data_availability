import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("tipm_analysis.csv")

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
    # Pick three times num_entries many colors and store as open_colors, conditional_colors, closed_colors. Use seaborn color palette for better distinction.
    palette = sns.color_palette("husl", 3 * num_entries)

    open_colors = palette[:num_entries]
    conditional_colors = palette[num_entries : 2 * num_entries]
    closed_colors = palette[2 * num_entries : 3 * num_entries]

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

    plt.figure("Open vs closed access over time (stacked bar)")
    width = 0.6
    x = np.arange(len(years))

    num_entries = len(entries)
    displacement = np.linspace(
        -width / num_entries, width / num_entries, num_entries + 1
    )[:-1]

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
    plt.legend()
    plt.title("Open vs Closed Access Over Time (Stacked Bar)")
    plt.tight_layout()
    plt.show()

    # Additional plot: Data availability (open, conditional, closed) over time, split by category
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
    plt.legend()
    plt.title("Data Availability Over Time (Stacked Bar)")
    plt.tight_layout()
    plt.show()

    # Additional plot: Data availability (open, conditional, closed) over time, split by category, relative to total counts (percent)
    plt.figure("Relative Data availability over time (stacked bar, %)")

    # For computational
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
            width=width / 2,
            label=f"{entry} - Open",
            color=open_colors[idx],
        )
        plt.bar(
            x + displacement[idx],
            data_conditional_rel,
            width=width / 2,
            bottom=data_open_rel,
            label=f"{entry} - Conditional",
            color=conditional_colors[idx],
        )
        plt.bar(
            x + displacement[idx],
            data_closed_rel,
            width=width / 2,
            bottom=data_open_rel + data_conditional_rel,
            label=f"{entry} - Closed",
            color=closed_colors[idx],
        )

    plt.xticks(x, years)
    plt.xlabel("Year")
    plt.ylabel("Percent of articles [%]")
    plt.legend()
    plt.title("Relative Data Availability Over Time (Stacked Bar, %)")
    plt.ylim(0, 100)
    plt.tight_layout()
    plt.show()


# Reduce df to computational and experimental
df_computational = df_by_category.get_group("computational")
df_experimental = df_by_category.get_group("experimental")
df_total_category = pd.concat([df_computational, df_experimental])

df_pde = df_by_subcategory.get_group("pde")
df_simulation = df_by_subcategory.get_group("simulation")
df_imaging = df_by_subcategory.get_group("imaging")
df_image_analysis = df_by_subcategory.get_group("image analysis")
df_total_subcategory = pd.concat([df_pde, df_simulation, df_imaging, df_image_analysis])


statistics_over_time(df, "category", ["computational", "experimental", "other"])
statistics_over_time(
    df_total_subcategory,
    "subcategory",
    [
        "simulation",
        "imaging",
    ],
)
