"""Robustness check: Requires correct link to webbrowser. Here MS Edge is used.

Potentially adapt to your system and browser of choice, e.g., Chrome, Firefox, Brave, etc.
"""

# NOTE: Hardcoded path to MS Edge browser executable
edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

import pandas as pd
import webbrowser

from pathlib import Path
import pandas as pd
import requests
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description="Robustness check for article access")
parser.add_argument(
    "--input", type=str, default="tipm_analysis.csv", help="Path to the input CSV file"
)
parser.add_argument(
    "--sample-years",
    action="store_true",
    help="Whether to sample years and open articles in browser",
)
parser.add_argument(
    "--random",
    action="store_true",
    help="Whether to randomly sample articles instead of the first N articles",
)
parser.add_argument(
    "--category",
    type=str,
    default=None,
    help="Category to filter articles by before sampling",
)
parser.add_argument(
    "--sample-size",
    type=int,
    default=5,
    help="Number of articles to sample per year if --sample-years is set",
)
args = parser.parse_args()

# Make sure that args.random and args.category are not both set
if args.random and args.category:
    raise ValueError("Cannot use --random and --category together. Please choose one.")

# Load the CSV file
df = pd.read_csv(args.input)


def open_url_in_browser(url):
    """Open a URL in the default web browser."""
    logger.info("Opening URL: %s", url)
    if Path(edge_path).exists():
        webbrowser.register("edge", None, webbrowser.BackgroundBrowser(edge_path))
        webbrowser.get("edge").open(url)
    else:
        # Fallback to default browser if Edge not found
        webbrowser.open(url)
    # Here you would add the code to open the URL in a browser.
    response = requests.get(url)
    if not response.status_code == 200:
        print("Failed to retrieve article.")


# Robustness check: Assessing open vs closed access of the articles.
# Check availability of Rights and Permissions section.
df_by_year = df.groupby("year")
for year in df_by_year.groups.keys():
    if not args.sample_years:
        continue
    random_articles = df_by_year.get_group(year).sample(args.sample_size)
    for index, row in random_articles.iterrows():
        url = row["url"]
        open_url_in_browser(url)
        for col in row.keys():
            print(col, row[col])

# Robustness check: Assessing whether the right category was assigned.
# Sample N articles from a specific category.
if args.category:
    filtered_df = df[df["category"] == args.category]
    sample_df = filtered_df.sample(args.sample_size)
    for index, row in sample_df.iterrows():
        url = row["url"]
        open_url_in_browser(url)
        for col in row.keys():
            print(col, row[col])
