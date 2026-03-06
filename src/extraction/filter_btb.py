"""Filter extracted documents to identify BTB (Transbronchial Biopsies).

Scans PDF/TXT files for BTB keywords and copies matching files to a destination folder.

Usage:
    python -m src.extraction.filter_btb
"""

import logging
import os
import shutil

import fitz  # PyMuPDF

from src.config import EXTRACT_ALL_DIR, EXTRACT_FILTERED_BTB_DIR

log = logging.getLogger(__name__)

INCLUSION_KEYWORDS = [
    "BIOPSIES TRANSBRONCHIQUES",
    "BIOPSIE TRANSBRONCHIQUE",
    "BIOPSIES TRANSBRONCHIQUE",
    "BIOPSIE TRANSBRONCHIQUES",
    "BTB",
    "BIOSPIE TRANSBRONCHIQUE",
]

EXCLUSION_KEYWORDS = ["Annulé"]


def check_keywords(filepath, inclusion_keywords, exclusion_keywords):
    """Check if inclusion/exclusion keywords exist within a PDF document."""
    try:
        doc = fitz.open(filepath)
        has_inclusion, has_exclusion = False, False
        for page in doc:
            page_text = page.get_text().upper()
            if not has_inclusion:
                for keyword in inclusion_keywords:
                    if keyword.upper() in page_text:
                        has_inclusion = True
                        break
            if not has_exclusion:
                for keyword in exclusion_keywords:
                    if keyword.upper() in page_text:
                        has_exclusion = True
                        break
            if has_inclusion and has_exclusion:
                break
        doc.close()
        return has_inclusion, has_exclusion, None
    except ValueError as e:
        if "document closed or encrypted" in str(e):
            return False, False, "encrypted"
        return False, False, str(e)
    except Exception as e:
        return False, False, str(e)


def main(
    source_dir: str | None = None,
    dest_dir: str | None = None,
):
    """Filter documents by BTB keywords and copy matches to destination."""
    source = source_dir or str(EXTRACT_ALL_DIR)
    dest = dest_dir or str(EXTRACT_FILTERED_BTB_DIR)

    os.makedirs(source, exist_ok=True)
    os.makedirs(dest, exist_ok=True)

    all_pdf_files = sorted([f for f in os.listdir(source) if f.endswith(".pdf")])

    # Resume support: skip already processed files
    dest_pdf_files = sorted([f for f in os.listdir(dest) if f.endswith(".pdf")])
    start_index = 0
    if dest_pdf_files:
        last_processed = dest_pdf_files[-1]
        if last_processed in all_pdf_files:
            start_index = all_pdf_files.index(last_processed) + 1
            log.info("Resuming from file %d of %d", start_index, len(all_pdf_files))

    files_to_process = all_pdf_files[start_index:]
    log.info("Total: %d, To process: %d", len(all_pdf_files), len(files_to_process))

    error_log_path = os.path.join(dest, "error_documents.txt")
    error_mode = "a" if os.path.exists(error_log_path) else "w"

    copied = 0
    with open(error_log_path, error_mode) as error_log:
        for filename in files_to_process:
            pdf_path = os.path.join(source, filename)
            try:
                has_inclusion, has_exclusion, error = check_keywords(
                    pdf_path, INCLUSION_KEYWORDS, EXCLUSION_KEYWORDS
                )
                if error:
                    error_log.write(f"{filename}\n")
                    log.warning("Could not process %s: %s", filename, error)
                    continue
                if has_inclusion and not has_exclusion:
                    shutil.copy(pdf_path, dest)
                    copied += 1
            except Exception as e:
                error_log.write(f"{filename}\n")
                log.error("Error processing %s: %s", filename, e)

    log.info("Filtering done: %d files copied to %s", copied, dest)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    main()
