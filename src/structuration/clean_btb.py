"""Post-extraction cleaning for BTB data.

Reads BTB_structurated_txt.xlsx, cleans fields, merges with transplant data,
performs verifications, and exports BTB_structurated_cleaned.xlsx.

Usage:
    python -m src.structuration.clean_btb
"""

import logging
import re

import pandas as pd

from src.config import OUTPUT_DIR, TRANSPLANTS_CSV

log = logging.getLogger(__name__)

# -- Header pattern to remove --------------------------------------------------
ENTETE_HOPITAL_FOCH = (
    r"SERVICE D.ANATOMIE ET DE CYTOLOGIE PATHOLOGIQUES\s+"
    r"HOPITAL FOCH\s+"
    r"40 rue WORTH\s*-\s*BP 36\s*-\s*92151\s*-\s*SURESNES CEDEX\s+"
    r"[.\s]*:?\s*01[\s.]46[\s.]25[\s.]23[\s.]12\s+"
    r"Fax\s*:\s*01[\s.]46[\s.]25[\s.]26[\s.]45"
)


def convert_to_date(text):
    """Convert DD/MM/YYYY string to datetime for Excel."""
    if pd.isna(text):
        return None
    text = str(text).strip()
    text = text.split()[0] if " " in text else text
    try:
        return pd.to_datetime(text, format="%d/%m/%Y")
    except (ValueError, TypeError):
        return None


def clean_nom(text):
    """Clean name by removing 'Pr' prefix and 'Destinataire'."""
    if pd.isna(text):
        return None
    text = str(text)
    text = text.replace("Destinataire", "")
    text = re.sub(r"^Pr\s+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+Pr\s+", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+Pr$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def find_matching_transplant(row, transplants):
    """Find the most recent transplant date <= biopsy date for a given biopsy."""
    ipp = row["IPP"]
    date_prelev = row["Date de prélèvement"]

    patient_transplants = transplants[transplants["IPP_LUTECE"] == ipp]
    if patient_transplants.empty:
        return pd.Series({"NATT": None, "LT_date": None})

    if pd.isna(date_prelev):
        return pd.Series({"NATT": None, "LT_date": None})

    valid_transplants = patient_transplants[
        patient_transplants["LT_date"] <= date_prelev
    ]

    if valid_transplants.empty:
        earliest = patient_transplants.loc[patient_transplants["LT_date"].idxmin()]
        return pd.Series({"NATT": earliest["NATT"], "LT_date": earliest["LT_date"]})

    best = valid_transplants.loc[valid_transplants["LT_date"].idxmax()]
    return pd.Series({"NATT": best["NATT"], "LT_date": best["LT_date"]})


def check_date_after_lt(row):
    """Check if biopsy date is after transplant date."""
    date_prelev = row["Date de prélèvement"]
    lt_date = row["LT_date"]
    if pd.isna(date_prelev) or pd.isna(lt_date):
        return None
    return "OK" if date_prelev >= lt_date else "ALERTE: Date prélèvement < LT_date"


def check_biopsies_count(nb_biopsies):
    """Check if patient has expected number of biopsies (>= 9)."""
    if pd.isna(nb_biopsies):
        return None
    nb = int(nb_biopsies)
    return "OK" if nb >= 9 else f"ALERTE: {nb} biopsies (< 9 attendues)"


def recap_verifications(row):
    """Summarize all verification alerts."""
    alertes = []
    if row.get("Verif_Date_LT") and "ALERTE" in str(row.get("Verif_Date_LT", "")):
        alertes.append("Date/LT_date")
    if row.get("Patient_dans_LUTECE") == "Non":
        alertes.append("Patient non LUTECE")
    if row.get("Verif_Nb_Biopsies") and "ALERTE" in str(
        row.get("Verif_Nb_Biopsies", "")
    ):
        alertes.append("Nb biopsies")
    return "; ".join(alertes) if alertes else "OK"


def main():
    """Run the full BTB cleaning pipeline."""
    input_file = OUTPUT_DIR / "BTB_structurated_txt.xlsx"
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    df = pd.read_excel(str(input_file))
    log.info("Loaded %d rows from %s", len(df), input_file)

    # 1. Clean free-text header
    if "Texte_libre_complet" in df.columns:
        df["Texte_libre_complet"] = (
            df["Texte_libre_complet"]
            .astype(str)
            .str.replace(ENTETE_HOPITAL_FOCH, "", regex=True)
            .str.strip()
        )
        df.loc[
            df["Texte_libre_complet"].isin(["", "nan", "None"]),
            "Texte_libre_complet",
        ] = None
        log.info("Header cleanup done on Texte_libre_complet")

    # 2. Convert dates
    df["Date de prélèvement"] = df["Date de prélèvement"].apply(convert_to_date)

    # 3. Clean names
    df["Nom"] = df["Nom"].apply(clean_nom)

    # 4. Remove duplicates by Biopsy ID (keep most recent)
    df_sorted = df.sort_values(
        by=["Biopsy ID", "Date de prélèvement"], ascending=[True, False]
    )
    df = df_sorted.drop_duplicates(subset=["Biopsy ID"], keep="first")
    log.info("After dedup: %d rows", len(df))

    # 5. Merge with LUTECE transplant data
    transplants_df = pd.read_csv(
        str(TRANSPLANTS_CSV), sep=";", encoding="latin-1"
    )
    transplants_df = transplants_df.rename(
        columns={"NIP": "IPP_LUTECE", "LT Date": "LT_date"}
    )

    df["IPP"] = df["IPP"].astype(str).str.zfill(9)
    transplants_df["IPP_LUTECE"] = (
        transplants_df["IPP_LUTECE"].astype(str).str.zfill(9)
    )
    transplants_df["LT_date"] = pd.to_datetime(
        transplants_df["LT_date"], format="%Y-%m-%d", errors="coerce"
    )

    df[["NATT", "LT_date"]] = df.apply(
        find_matching_transplant, axis=1, transplants=transplants_df
    )
    log.info(
        "Biopsies with transplant: %d", df["NATT"].notna().sum()
    )

    # 6. Date verification
    df["Verif_Date_LT"] = df.apply(check_date_after_lt, axis=1)

    # 7. LUTECE patient verification
    patients_lutece = set(
        transplants_df["IPP_LUTECE"].astype(str).str.zfill(9).unique()
    )
    patients_btb = set(df["IPP"].unique())

    df["Patient_dans_LUTECE"] = df["IPP"].apply(
        lambda x: "Oui" if x in patients_lutece else "Non"
    )

    patients_lutece_manquants = patients_lutece - patients_btb
    log.info("LUTECE patients not in BTB: %d", len(patients_lutece_manquants))

    # 8. Biopsy count verification
    biopsies_par_patient = df.groupby("IPP").size().reset_index(name="Nb_Biopsies")
    df = df.merge(biopsies_par_patient, on="IPP", how="left")
    df["Verif_Nb_Biopsies"] = df["Nb_Biopsies"].apply(check_biopsies_count)

    # 9. Summary alerts
    df["Alertes_Recap"] = df.apply(recap_verifications, axis=1)

    # Export
    output_file = OUTPUT_DIR / "BTB_structurated_cleaned.xlsx"
    df.to_excel(str(output_file), index=False)
    log.info(
        "Export done: %s (%d rows, %d alerts)",
        output_file,
        len(df),
        len(df[df["Alertes_Recap"] != "OK"]),
    )

    return df


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    main()
