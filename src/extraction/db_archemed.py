"""Extract anapath documents from PostgreSQL (DWH ARCHEMED).

Usage:
    python -m src.extraction.db_archemed
"""

import logging
import os

import psycopg2
from bs4 import BeautifulSoup
from tqdm import tqdm

from src.config import PG_DB, EXTRACT_ARCHEMED_DIR

log = logging.getLogger(__name__)

QUERY = """
SELECT DISTINCT ON (d.patient_num, d.document_origin_code)
    d.patient_num,
    p.hospital_patient_id,
    d.document_origin_code,
    d.title,
    d.document_date,
    d.displayed_text
FROM dwh.dwh_document d
JOIN dwh.dwh_patient_ipphist p ON d.patient_num = p.patient_num
WHERE d.document_type = 'EXT'
AND d.title LIKE '%%Anapath%%'
"""


def html_to_text(html_content: str) -> str:
    """Extract plain text from HTML content."""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator="\n", strip=True)


def main():
    """Connect to ARCHEMED PostgreSQL and extract anapath documents as text."""
    os.makedirs(str(EXTRACT_ARCHEMED_DIR), exist_ok=True)

    log.info(
        "Connecting to PostgreSQL (%s:%s/%s)...",
        PG_DB["host"],
        PG_DB["port"],
        PG_DB["database"],
    )
    conn = psycopg2.connect(**PG_DB)
    log.info("Connected")

    cursor = conn.cursor()
    log.info("Executing query...")
    cursor.execute(QUERY)

    rows = cursor.fetchall()
    log.info("%d documents found", len(rows))

    saved = 0
    skipped = 0

    for row in tqdm(rows, desc="Extracting texts"):
        hospital_ipp = str(row[1])
        origin_code = str(row[2])
        document_date = row[4]
        displayed_text = row[5]

        if displayed_text:
            clean_text = html_to_text(displayed_text)

            patient_folder = EXTRACT_ARCHEMED_DIR / hospital_ipp
            os.makedirs(str(patient_folder), exist_ok=True)

            date_str = (
                document_date.strftime("%Y%m%d") if document_date else "nodate"
            )
            filename = patient_folder / f"{hospital_ipp}_{date_str}_{origin_code}.txt"

            with open(str(filename), "w", encoding="utf-8") as f:
                f.write(clean_text)
            saved += 1
        else:
            skipped += 1

    cursor.close()
    conn.close()
    log.info("Done: %d saved, %d skipped (empty text)", saved, skipped)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    main()
