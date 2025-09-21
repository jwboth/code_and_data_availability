import pandas as pd
import numpy as np
import re
import webbrowser

from pathlib import Path
import pandas as pd
import requests


df = pd.read_csv("tipm_analysis.csv")

# Robustness check: Assessing open vs closed access of the articles.
# Check availability of Rights and Permissions section.
df_by_year = df.groupby("year")
for year in df_by_year.groups.keys():
    # Pick 5 random articles and open their URL in the browser.
    random_articles = df_by_year.get_group(year).sample(5)
    for index, row in random_articles.iterrows():
        url = row["url"]
        # Open the URL in Microsoft Edge
        edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        if Path(edge_path).exists():
            webbrowser.register("edge", None, webbrowser.BackgroundBrowser(edge_path))
            webbrowser.get("edge").open(url)
        else:
            # Fallback to default browser if Edge not found
            webbrowser.open(url)
        print(f"Opening {url}...")
        # Here you would add the code to open the URL in a browser.
        response = requests.get(url)
        if response.status_code == 200:
            print("Success!")
        else:
            print("Failed to retrieve article.")
        # For demonstration, we just print the first 100 characters of the page content.
