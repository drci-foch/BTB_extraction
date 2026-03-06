"""Extract anapath documents from SQL Server (Easily/METADONE).

Usage:
    python -m src.extraction.db_easily
"""

import logging
import os

import pandas as pd
import pyodbc

from src.config import EASILY_DB, TRANSPLANTS_CSV, EXTRACT_ALL_DIR

log = logging.getLogger(__name__)


def main():
    """Connect to Easily DB and download anapath PDF documents."""
    if not TRANSPLANTS_CSV.exists():
        raise FileNotFoundError(f"Transplants file not found: {TRANSPLANTS_CSV}")

    df = pd.read_csv(str(TRANSPLANTS_CSV), sep=";", encoding="latin-1")

    log.info(
        "Connecting to SQL Server (%s/%s)...",
        EASILY_DB["server"],
        EASILY_DB["database"],
    )
    connection = pyodbc.connect(
        driver="{SQL Server}",
        host=EASILY_DB["server"],
        port=1433,
        database=EASILY_DB["database"],
        trusted_connection="No",
        user=EASILY_DB["username"],
        password=EASILY_DB["password"],
    )
    log.info("Connected")

    # Filter valid IPPs and build batches
    filtered_identifiers = df.loc[
        df["NIP"].astype(str).str.strip().str[0].str.isdigit(), "NIP"
    ].tolist()

    batch_size = 450
    batches = [
        filtered_identifiers[i : i + batch_size]
        for i in range(0, len(filtered_identifiers), batch_size)
    ]

    os.makedirs(str(EXTRACT_ALL_DIR), exist_ok=True)

    # Process each batch with parameterized queries
    total_saved = 0
    for batch in batches:
        placeholders = ", ".join("?" for _ in batch)
        query = f"""
            SELECT p.pat_ipp, d.doc_nom, d.doc_creation_date,
                   d.doc_realisation_date, d.doc_stockage_id, fil_data
            FROM METADONE.metadone.DOCUMENTS d
            LEFT JOIN NOYAU.patient.PATIENT p ON d.doc_pat_id = p.pat_id
            LEFT JOIN STOCKAGE.stockage.FILES f ON f.fil_id = d.doc_stockage_id
            WHERE doc_nom LIKE '%Anapath%'
              AND p.pat_ipp IN ({placeholders})
        """

        with connection.cursor() as cursor:
            cursor.execute(query, batch)
            while True:
                row = cursor.fetchone()
                if row is None:
                    break
                if row[5] is not None:
                    pat_ipp = row[0]
                    doc_stockage_id = row[4]
                    fil_data = row[5]
                    filename = EXTRACT_ALL_DIR / f"{pat_ipp}_{doc_stockage_id}.pdf"
                    with open(str(filename), "wb") as f:
                        f.write(fil_data)
                    total_saved += 1

    connection.close()
    log.info("Extraction complete: %d documents saved to %s", total_saved, EXTRACT_ALL_DIR)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    main()
