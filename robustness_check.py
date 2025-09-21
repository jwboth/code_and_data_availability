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

df = pd.read_csv(args.input)

# Make sure all "theoretical" entries have data availability score of < 1
assert df.loc[df["category"] == "theoretical", "data_availability_score"].max() < 1.0, (
    "Theoretical articles should not have full data availability score of 1.0"
)


def open_url_in_browser(url):
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    logger.info("Opening URL: %s", url)
    if Path(edge_path).exists():
        webbrowser.register("edge", None, webbrowser.BackgroundBrowser(edge_path))
        webbrowser.get("edge").open(url)
    else:
        # Fallback to default browser if Edge not found
        webbrowser.open(url)
    # Here you would add the code to open the URL in a browser.
    response = requests.get(url)
    if response.status_code == 200:
        print("Success!")
    else:
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

if args.random:
    sample_df = df.sample(args.sample_size)
    for index, row in sample_df.iterrows():
        url = row["url"]
        open_url_in_browser(url)

elif args.category:
    filtered_df = df[df["category"] == args.category]
    sample_df = filtered_df.sample(args.sample_size)
    for index, row in sample_df.iterrows():
        url = row["url"]
        open_url_in_browser(url)
