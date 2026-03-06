"""Extract structured data from BTB text files.

Usage:
    python -m src.structuration.extract_btb <directory_path>
"""

import argparse
import logging
import os

import pandas as pd
from tqdm import tqdm

from src.config import OUTPUT_DIR, EXTRACT_FILTERED_BTB_DIR, EXTRACT_BTB_TXT_DIR
from src.structuration.extractors import (
    extract_information,
    extract_niveaux_coupes,
    extract_prescripteur,
    extract_prenom_before_docteur,
    extract_technique,
    detect_modele_btb,
    extract_texte_libre_complet,
    read_text_file,
    remove_illegal_chars,
)
from src.structuration.patterns import ALL_PATTERNS, COLUMN_ORDER

log = logging.getLogger(__name__)


def process_text_files(directory_path: str) -> pd.DataFrame:
    """Process all .txt files in a directory and extract BTB information."""
    data = []
    txt_files = [f for f in os.listdir(directory_path) if f.endswith(".txt")]
    log.info("Found %d .txt files in %s", len(txt_files), directory_path)

    errors = []
    pbar = tqdm(txt_files, desc="Extracting BTB", unit="file")
    for filename in pbar:
        pbar.set_postfix_str(filename[:40], refresh=False)
        file_path = os.path.join(directory_path, filename)
        try:
            text = read_text_file(file_path)

            info = extract_information(text, ALL_PATTERNS)
            info["Technique"] = extract_technique(text, option="lba")
            info["Prescripteur"] = extract_prescripteur(text)
            info["Prénom"] = extract_prenom_before_docteur(text)
            info["Filename"] = filename
            info["IPP"] = filename.split("_")[0]
            info["Niveaux de coupes"] = extract_niveaux_coupes(text)

            date_prelev = info.get("Date de prélèvement")
            info["Modele_BTB"] = detect_modele_btb(text, date_prelev)
            info["Texte_libre_complet"] = extract_texte_libre_complet(
                text, info["Modele_BTB"]
            )

            data.append(info)
        except Exception as e:
            log.warning("Skipping %s: %s", filename, e)
            errors.append(filename)
            continue

    if errors:
        log.warning("%d files skipped due to errors", len(errors))

    if not data:
        log.warning("No data extracted")
        return pd.DataFrame()

    all_columns = set()
    for d in data:
        all_columns.update(d.keys())
    column_order = COLUMN_ORDER + [c for c in all_columns if c not in COLUMN_ORDER]
    return pd.DataFrame(data, columns=[c for c in column_order if c in all_columns])


def _default_input_dir() -> str:
    """Pick the best available input directory."""
    for d in [EXTRACT_BTB_TXT_DIR, EXTRACT_FILTERED_BTB_DIR]:
        if d.is_dir() and any(f.endswith(".txt") for f in os.listdir(d)):
            return str(d)
    return str(EXTRACT_BTB_TXT_DIR)


def main(directory_path: str | None = None):
    """Run BTB extraction on a directory."""
    if directory_path is None:
        # When called from pipeline: use default directory
        # When called from CLI: parse args
        if __name__ == "__main__" or not any(
            d.is_dir() for d in [EXTRACT_BTB_TXT_DIR, EXTRACT_FILTERED_BTB_DIR]
        ):
            parser = argparse.ArgumentParser(
                description="Extract BTB data from text files."
            )
            parser.add_argument(
                "directory_path",
                type=str,
                nargs="?",
                default=_default_input_dir(),
                help="Directory containing .txt files",
            )
            args = parser.parse_args()
            directory_path = args.directory_path
        else:
            directory_path = _default_input_dir()

    os.makedirs(directory_path, exist_ok=True)
    if not os.path.isdir(directory_path):
        raise FileNotFoundError(f"Directory not found: {directory_path}")

    df = process_text_files(directory_path)
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].apply(remove_illegal_chars)

    os.makedirs(str(OUTPUT_DIR), exist_ok=True)
    output_file = OUTPUT_DIR / "BTB_structurated_txt.xlsx"
    df.to_excel(str(output_file), index=False)
    log.info("Extraction complete: %s (%d rows)", output_file, len(df))
    return df


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    main()
