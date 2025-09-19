import argparse
import logging
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; DataAvailabilityBot/1.0)"}


def read_keywords_from_csv(filename):
    # Read a single line of comma-separated keywords, strip whitespace
    with open(filename, encoding="utf-8") as f:
        line = f.readline()
        # Use raw string for each keyword to preserve escapes like \b
        return [rf"{key.strip()}" for key in line.strip().split(",") if key.strip()]


# Read keywords from CSV files as DataFrames
numerical_keywords_df = pd.read_csv("numerical_keywords.csv")
experimental_keywords_df = pd.read_csv("experimental_keywords.csv")
availability_scores_df = pd.read_csv("availability_scores.csv")
open_access_scores_df = pd.read_csv("open_access_scores.csv")


def fetch_url(url, timeout=20):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return r
    except Exception as e:
        logging.warning("Request failed for %s: %s", url, e)
        return None


def extract_open_access(soup):
    # Look for <span class="c-article-meta-recommendations__access-type">
    tag = soup.find("span", class_="c-article-meta-recommendations__access-type")
    if tag:
        return tag.get_text(strip=True).lower()
    else:
        "unknown"


def extract_abstract(soup):
    tag = soup.find("div", class_="c-article-body", attrs={"data-article-body": "true"})
    if tag:
        section = tag.find("section", attrs={"data-title": "Abstract"})
        if section:
            content = section.find("div", class_="c-article-section__content")

            return content.get_text(strip=True)
    return None


def count_occurences(text, df, column_key, column_count):
    if not text:
        return
    counts = []
    for _, row in df.iterrows():
        key = row[column_key]
        count = len(re.findall(rf"{key}", text, re.I))
        counts.append(count)
    df[column_count] = counts
    return


def find_largest_counter(df_list, column):
    total_counts = [sum(df[column]) for df in df_list]
    if sum(total_counts) == 0:
        return None
    max_index = total_counts.index(max(total_counts))
    return max_index


def extract_matching_keywords(df_list):
    keywords = [
        row["keyword"]
        for df in df_list
        for _, row in df.iterrows()
        if row["keyword_counter"] > 0
    ]
    # Convert to comma-separated string
    return ", ".join(keywords)


def count_category(df):
    # Make unique and remove NaN categories
    categories = df["category"].unique()
    categories = [cat for cat in categories if pd.notna(cat)]
    counter = {
        category: sum(
            [
                row["keyword_counter"]
                for _, row in df.iterrows()
                if row["category"] == category
            ]
        )
        for category in categories
    }
    category_counter = []
    for _, row in df.iterrows():
        if pd.isna(row["category"]):
            category_counter.append(0)
        else:
            category_counter.append(counter[row["category"]])
    df["category_counter"] = category_counter


def find_frequent_key(df, column_key, column_count):
    # Find the index of the max value in the column_count column
    max_index = df[column_count].idxmax()
    max_value = df.loc[max_index, column_key]
    return max_value


def find_all_section_titles(soup):
    # List all data-title attributes for all sections in soup
    sections = soup.find_all("section", attrs={"data-title": True})
    titles = [sec["data-title"] for sec in sections if "data-title" in sec.attrs]
    return titles


def extract_section(soup, title: list):
    sections = soup.find_all("section", attrs={"data-title": True})
    sections_list = [sec for sec in sections]
    section_titles = [
        sec["data-title"] for sec in sections if "data-title" in sec.attrs
    ]
    # Count matches for each title keyword
    title_matches = [
        sum([1 for key in title if re.search(rf"{key}", sec_title, re.I)])
        for sec_title in section_titles
    ]
    if not title_matches or max(title_matches) == 0:
        return None

    # Extract the section with the highest match count
    max_index = title_matches.index(max(title_matches))
    section = sections_list[max_index]
    return section.text


def find_all_sections(soup, title: list):
    # Find section that machtes
    # <section lang="en"><div class="c-article-section" id="Abs1-section"><div class="c-article-section__content" id="Abs1-content"><h3 class="c-article__sub-heading" data-test="abstract-sub-heading">
    sections = soup.find_all("section")
    sections_list = [sec for sec in sections]
    for sec in sections_list:
        try:
            print(sec)
        except Exception as e:
            print(f"Error printing section: {e}")
    return sections


def extract_meta(soup, content: list):
    # Check <meta> tags for keywords in content
    metas = soup.find_all("meta")
    metas_list = [meta for meta in metas]
    meta_matches = [
        sum(
            [
                1
                for key in content
                if re.search(rf"{key}", meta.get("content", ""), re.I)
            ]
        )
        for meta in metas_list
    ]
    # Found nothing
    if not meta_matches or max(meta_matches) == 0:
        return None
    # Extract the meta with the highest match count
    max_index = meta_matches.index(max(meta_matches))
    meta = metas_list[max_index]
    return meta.get("content")


def score(text, evaluation_df, empty_category="none"):
    if not text:
        return 0, empty_category
    scores = []
    categories = evaluation_df.get("category", [])
    for _, row in evaluation_df.iterrows():
        key = row["keyword"]
        score = row["score"]
        if re.search(rf"{key}", text, re.I):
            scores.append(score)
        else:
            scores.append(0)
    if not scores or all(s == 0 for s in scores):
        return 0, empty_category
    return max(scores), categories[scores.index(max(scores))]


def save_soup_to_file(soup, filename="soup.html"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(str(soup))


def main(input_csv, output_csv):
    df = pd.read_csv(input_csv, dtype=str)

    # Count articles
    logging.info("Read %d rows from %s", len(df), input_csv)

    # Unify the categories from TiPM style to generic style
    df["year"] = df["Publication Year"]
    df["title"] = df["Item Title"]
    df["doi"] = df["Item DOI"]
    df["type"] = (
        df["Content Type"]
        .map(
            {
                "Article": "article",
                "Review": "article",
                "Book Chapter": "book-chapter",
                "Book": "book",
                "Conference Paper": "conference-paper",
                "Data Paper": "data-paper",
                "Editorial": "editorial",
                "Letter": "letter",
                "News": "news",
                "Correction": "correction",
                "Retraction": "retraction",
                # Add more mappings as needed
            }
        )
        .fillna("other")
    )
    df["url"] = df["URL"]
    df["journal"] = df["Publication Title"]
    df.drop(
        columns=[
            "Publication Year",  # -> "year"
            "Item Title",  # -> "title"
            "Item DOI",  # -> "doi"
            "Book Series Title",  # [nan]
            "Publication Title",  # -> "journal"
            "Journal Volume",  # [nan]
            "Journal Issue",  # [nan]
            "Item DOI",  # -> doi
            "URL",  # -> url
            "Content Type",  # -> type
        ],
        errors="ignore",
        inplace=True,
    )

    # Stop if type is "other"
    if (df["type"] == "other").any():
        raise ValueError("Unsupported article type found")

    # Containers for results
    access_score = []
    access_category = []
    access_section = []
    discipline = []
    category = []
    keywords = []
    availability_score = []
    availability_category = []
    abstract = []
    availability_section = []

    for idx in range(len(df)):
        # if not idx == 25:
        #    continue
        # Initialize containers for fetching content
        out_texts = []
        statuses = []

        # Fetch URL
        url = df["url"].iloc[idx]
        # url = "https://link.springer.com/article/10.1007/s11242-025-02216-x"
        if not url:
            out_texts.append("")
            statuses.append("no-url")
            continue

        # Fetch url
        logging.info("[%d] Fetching %s", idx, url)
        r = fetch_url(url)
        if r is None:
            out_texts.append("")
            statuses.append("fetch-failed")
            logging.warning("Failed to fetch URL: %s", url)
            continue

        # Convert to soup
        soup = BeautifulSoup(r.text, "html.parser")

        # Extract whether article is experimental or computational
        _abstract = extract_section(soup, title=["Abstract"])
        if not _abstract:
            _abstract = extract_meta(soup, content=["Abstract"])

        # If no abstract found, mark as error, save soup for debugging, and fill in
        # the lists with placeholders, continue with the next article
        if not _abstract:
            save_soup_to_file(soup, filename=f"soup_{idx}.html")
            abstract.append("N/A")
            access_section.append("N/A")
            access_score.append(0)
            access_category.append("N/A")
            discipline.append("N/A")
            category.append("N/A")
            keywords.append("N/A")
            availability_section.append("N/A")
            availability_score.append(0)
            availability_category.append("N/A")
            continue
            # raise ValueError(f"Abstract not found for {url}")
        else:
            abstract.append(_abstract)

        # Extract whether article is open access
        rights_and_permissions_section = extract_section(
            soup, title=["rights", "permission"]
        )
        if not rights_and_permissions_section:
            save_soup_to_file(soup, filename=f"soup_{idx}.html")
            raise ValueError(f"Rights and permissions section not found for {url}")
        access_section.append(rights_and_permissions_section)
        _access_score, _access_category = score(
            rights_and_permissions_section,
            open_access_scores_df,
            empty_category="closed access",
        )
        access_score.append(_access_score)
        access_category.append(_access_category)

        # Copy keyword DataFrames and add column "found" initialized to 0 for each item
        _numerical_keywords = numerical_keywords_df.copy()
        _experimental_keywords = experimental_keywords_df.copy()

        # Count occurrences of each keyword in the abstract
        count_occurences(_abstract, _numerical_keywords, "keyword", "keyword_counter")
        count_occurences(
            _abstract, _experimental_keywords, "keyword", "keyword_counter"
        )

        # Post-process: count categories and find dominant
        count_category(_numerical_keywords)
        count_category(_experimental_keywords)
        dominant = find_largest_counter(
            [
                _numerical_keywords,
                _experimental_keywords,
            ],
            "keyword_counter",
        )
        if dominant is None:
            discipline.append("other")
            category.append("other")
        if dominant == 0:
            discipline.append("computational")
            category.append(
                find_frequent_key(_numerical_keywords, "category", "category_counter")
            )
        if dominant == 1:
            discipline.append("experimental")
            category.append(
                find_frequent_key(
                    _experimental_keywords, "category", "category_counter"
                )
            )

        # Extract matching keywords
        matching_keywords = extract_matching_keywords(
            [_numerical_keywords, _experimental_keywords]
        )
        keywords.append(matching_keywords)

        # Extract section on data/code availability
        _availability_section = extract_section(soup, title=["data", "avail"])
        if not _availability_section:
            _availability_section = extract_section(soup, title=["code", "avail"])
        availability_section.append(_availability_section)
        _availability_score, _availability_category = score(
            _availability_section,
            availability_scores_df,
            empty_category="closed access",
        )
        availability_score.append(_availability_score)
        availability_category.append(_availability_category)

        # Debugging
        print()
        print("Debugging")
        print("Access:", access_score[-1], access_category[-1])
        print("Discipline:", discipline[-1])
        print("Category", category[-1])
        print("Keywords:", matching_keywords)
        print("Availability score:", availability_score[-1])
        print("Availability category:", availability_category[-1])

        print(
            "rights_and_permissions_section:",
        )
        print("Rights and permissions section:", access_section[-1])
        print("Abstract", abstract[-1])
        print("Availability section:", availability_section[-1])

    df["article_availability_score"] = access_score
    df["article_availability_category"] = access_category
    df["article_availability_section"] = access_section
    df["abstract"] = abstract
    df["discipline"] = discipline
    df["category"] = category
    df["keywords"] = keywords
    df["data_availability_score"] = availability_score
    df["data_availability_category"] = availability_category
    df["data_availability_section"] = availability_section

    df.to_csv(output_csv, index=False)
    logging.info("Wrote results to %s", output_csv)


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Extract 'Data availability' text from article URLs in a CSV"
    )
    p.add_argument("--input", "-i", required=True, help="input CSV file")
    p.add_argument(
        "--output", "-o", default="with_data_availability.csv", help="output CSV file"
    )
    args = p.parse_args()
    main(args.input, args.output)
