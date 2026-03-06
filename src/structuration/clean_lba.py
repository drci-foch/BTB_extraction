"""Post-extraction cleaning for LBA (Lavage Bronchoalveolaire) data.

Usage:
    python -m src.structuration.clean_lba
"""

import logging

import pandas as pd

from src.config import OUTPUT_DIR

log = logging.getLogger(__name__)


def parse_numeric_column(
    df: pd.DataFrame, column: str, strip_chars: str = ""
) -> pd.DataFrame:
    """Split a column into numeric and text parts.

    For each value, attempts to parse as float after stripping strip_chars.
    Creates column (float) and column_text (str or None).
    """
    text_col = f"{column}_text"
    df[text_col] = df[column].astype(str)

    numeric_values = []
    text_values = []
    for value in df[text_col]:
        clean = value
        for ch in strip_chars:
            clean = clean.replace(ch, "")
        clean = clean.strip()
        try:
            numeric_values.append(float(clean))
            text_values.append(None)
        except ValueError:
            numeric_values.append(None)
            text_values.append(value)

    df[column] = numeric_values
    df[text_col] = text_values
    return df


def main():
    """Run the LBA cleaning pipeline."""
    input_file = OUTPUT_DIR / "LBA_structurated_raw.xlsx"
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    df = pd.read_excel(str(input_file))
    log.info("Loaded %d rows from %s", len(df), input_file)

    # Select columns
    df = df[
        [
            "Filename",
            "IPP",
            "Biopsy ID",
            "Date de prélèvement",
            "Macrophages",
            "Lymphocytes",
            "Polynucléaires neutrophiles",
            "Polynucléaires éosinophiles",
            "Volume",
            "Numération",
        ]
    ]

    # Convert date
    df["Date de prélèvement"] = df["Date de prélèvement"].astype(
        "datetime64[ns]", errors="ignore"
    )

    # Parse numeric columns
    df = parse_numeric_column(df, "Lymphocytes", strip_chars="%")
    df = parse_numeric_column(df, "Polynucléaires neutrophiles")
    df = parse_numeric_column(df, "Polynucléaires éosinophiles", strip_chars="%")
    df = parse_numeric_column(df, "Volume", strip_chars="ml")
    df = parse_numeric_column(df, "Numération", strip_chars="éléments/ml .")

    # Export
    output_file = OUTPUT_DIR / "LBA_structurated_cleaned.xlsx"
    df.to_excel(str(output_file), index=False)
    log.info("Export done: %s (%d rows)", output_file, len(df))
    return df


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    main()
