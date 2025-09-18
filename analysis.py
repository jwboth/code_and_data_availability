import argparse
import logging
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text as extract_pdf_text

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; DataAvailabilityBot/1.0)"}


def fetch_url(url, timeout=20):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return r
    except Exception as e:
        logging.warning("Request failed for %s: %s", url, e)
        return None


# ...existing code...
def extract_from_html(html, key):
    soup = BeautifulSoup(html, "html.parser")

    key_lc = (key or "").strip().lower()
    if not key_lc:
        key_lc = "data"

    # 1) Try structural: find section with id/class containing key and "availability"
    sel = soup.find(
        lambda tag: tag.name in ["section", "div"]
        and tag.get("id")
        and key_lc in tag.get("id", "").lower()
        and "avail" in tag.get("id", "").lower()
    )

    if not sel:
        sel = soup.find(
            lambda tag: tag.name in ["section", "div"]
            and tag.get("class")
            and any(
                key_lc in c.lower() and "avail" in c.lower()
                for c in (tag.get("class") or [])
            )
        )

    if sel:
        text = sel.get_text(separator="\n").strip()
        if text:
            print(text)
            return text

    # 2) Find headings that mention "<key> availability" (any heading level or strong tags)
    pattern = re.compile(rf"{re.escape(key_lc)}\s+availability", re.I)
    heading = soup.find(
        lambda tag: tag.name
        in ["h1", "h2", "h3", "h4", "h5", "h6", "p", "strong", "div", "span"]
        and tag.get_text(strip=True)
        and pattern.search(tag.get_text())
    )
    if heading:
        parts = []
        # Collect the heading text
        parts.append(heading.get_text(" ", strip=True))
        # gather following siblings until next heading tag (h1-h6) or until reasonable limit
        for sib in heading.find_next_siblings():
            if sib.name and re.match(r"h[1-6]", sib.name, re.I):
                break
            parts.append(sib.get_text(" ", strip=True))
            if len(" ".join(parts)) > 4000:
                break
        text = "\n".join([p for p in parts if p]).strip()
        if text:
            print(text)
            return text

    # 3) Fallback: search page text and extract a snippet around the phrase "<key> availability"
    page_text = soup.get_text("\n")
    fallback_re = re.compile(
        rf"({re.escape(key_lc)}\s+availability[:\s\-–—]*)([\s\S]{{0,2000}})", re.I
    )
    match = fallback_re.search(page_text)
    if match:
        snippet = (match.group(1) + match.group(2)).strip()
        # Stop at next large section break (two newlines or a line of all caps)
        end = re.split(r"\n{2,}|\n[A-Z0-9 \-]{3,}\n", snippet)
        print(end[0].strip())
        return end[0].strip()

    return None


def extract_from_response(r):
    ctype = r.headers.get("Content-Type", "").lower()
    if "application/pdf" in ctype or r.url.lower().endswith(".pdf"):
        assert False
    else:
        data_availability = extract_from_html(r.text, "data")
        code_availability = extract_from_html(r.text, "code")
        return data_availability, code_availability


def main(input_csv, url_col, output_csv):
    df = pd.read_csv(input_csv, dtype=str)
    if url_col not in df.columns:
        logging.error(
            "URL column '%s' not found in CSV columns: %s", url_col, list(df.columns)
        )
        return

    out_texts = []
    statuses = []
    data_out_texts = []
    code_out_texts = []
    data_statuses = []
    code_statuses = []

    for idx, url in df[url_col].fillna("").items():
        if not url:
            out_texts.append("")
            statuses.append("no-url")
            continue

        logging.info("[%d] Fetching %s", idx, url)
        r = fetch_url(url)
        if r is None:
            out_texts.append("")
            statuses.append("fetch-failed")
            continue

        data_availability, code_availability = extract_from_response(r)
        if data_availability:
            data_out_texts.append(data_availability)
            data_statuses.append("found")
        else:
            data_out_texts.append("")
            data_statuses.append("not-found")
        if code_availability:
            code_out_texts.append(code_availability)
            code_statuses.append("found")
        else:
            code_out_texts.append("")
            code_statuses.append("not-found")

    df["data_availability_text"] = data_out_texts
    df["data_availability_status"] = data_statuses
    df["code_availability_text"] = code_out_texts
    df["code_availability_status"] = code_statuses

    df.to_csv(output_csv, index=False)
    logging.info("Wrote results to %s", output_csv)


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Extract 'Data availability' text from article URLs in a CSV"
    )
    p.add_argument("--input", "-i", required=True, help="input CSV file")
    p.add_argument(
        "--url-col",
        "-u",
        default="url",
        help="column name with article URL (default 'url')",
    )
    p.add_argument(
        "--output", "-o", default="with_data_availability.csv", help="output CSV file"
    )
    args = p.parse_args()
    main(args.input, args.url_col, args.output)
