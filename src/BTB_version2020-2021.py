import argparse
import os
import re
import warnings

import pandas as pd

warnings.filterwarnings("ignore")

"""
This script is designed to extract information from BTB documents in .txt version, specifically targeting documents dated from 2021 to 2019. It has been tailored to understand and process the formatting and content specific to these years. Users can run this script to parse directories containing text files of BTB documents and extract relevant information into a structured Excel spreadsheet.

Please note that while this script is optimized for documents from 2021 to 2019, it has not been extensively tested on documents from years prior to 2019. If you need to process documents from before 2019, additional testing and potentially some modifications to the script may be necessary to ensure accurate extraction of information.

Usage:
To run this script, provide the directory path containing the BTB text documents as a command-line argument. The script will process all text files within the specified directory, extract the relevant information, and compile it into an Excel file named 'BTBextract_2020-2021.xlsx'.

Example:
python your_script_name.py <path_to_your_folder>

Dependencies:
- Python 3.11
- pandas library
- openpyxl library (for writing to Excel)

Make sure these dependencies are installed in your Python environment before running the script.
"""


def read_text_file(file_path):
    """
    Reads the content of a text file and returns it as a string.

    Parameters:
    - file_path (str): The path to the text file.

    Returns:
    - str: The content of the file.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def extract_prenom_before_docteur(text):
    """
    Extracts the first name (prénom) from a string that precedes a specific pattern, typically "Docteur".

    Parameters:
    - text (str): The string from which the first name is to be extracted.

    Returns:
    - str or None: The extracted first name if found, otherwise None.
    """
    pattern = r"Prénom\s*:\s*([A-Z\s]+)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        # Extract the captured group before "Docteur"
        before_docteur = match.group(1)
        first_name = before_docteur.split()[0] if before_docteur else None
        return first_name
    return None


def extract_technique(text):
    """
    Extracts the BTB technique from a given text based on various patterns. It handles multiple patterns to
    account for variations in the text formatting and terminology.

    Parameters:
    - text (str): The text from which the medical technique is to be extracted.

    Returns:
    - str or None: The extracted technique if found, otherwise None.
    """
    # Most found pattern
    technique_pattern = r"(2\.|II\.|I\.|2/|2°/)[\s+]*(Biopsies\s+trans[ -]*bronchiques|Biopsies\s+transbronchiques|Biospies\s+transbronchiques|BTB)[\s\S+]*?Technique[^\S\r\n]*:[^\S\r\n]*([^;]+)"
    technique_match = re.search(
        technique_pattern, text, re.DOTALL | re.IGNORECASE)

    if not technique_match:
        # Sometimes, there isn't the numbers, only "Biopsie" in text etc..
        fallback_technique_pattern = r"(Biopsies\s+trans[ -]*bronchiques|Biopsies\s+transbronchiques|Biospies\s+transbronchiques|BTB)[\s\S+]*?Technique\s*:\s*([^;]+)"
        fallback_match = re.search(fallback_technique_pattern, text, re.DOTALL)
        if fallback_match:
            return fallback_match.group(2).strip()

        else:
            # No mention of biopsie or lavage, just the mention of techniques two times. The BTB technique is always second.
            parts = re.split(r"(?=Technique\s*:)", text, flags=re.IGNORECASE)
            two_parts_fallback_technique_pattern = r"Technique\s*:\s*([^;]+)"
            if len(parts) > 2:
                two_parts_fallback_match = re.search(
                    two_parts_fallback_technique_pattern, parts[-1], re.DOTALL
                )
                if two_parts_fallback_match:
                    return two_parts_fallback_match.group(1).strip()

            # Else, look at any mention of technique in the document
            else:
                last_fallback_technique_pattern = r"Technique\s*:\s*([^;]+)"
                last_fallback_match = re.search(
                    last_fallback_technique_pattern, text, re.DOTALL
                )
                if last_fallback_match:
                    return last_fallback_match.group(1).strip()

    return technique_match.group(3).strip() if technique_match else None


def extract_niveaux_coupes(text):
    """
    Extracts the levels of cuts (niveaux de coupes) from a given text, reusing the patterns defined for extracting
    techniques. It specifically looks for the group right after a semi-colon that follows the technique pattern.

    Parameters:
    - text (str): The text from which the levels of cuts are to be extracted.

    Returns:
    - str or None: The extracted levels of cuts if found, otherwise None.
    """
    # Most found pattern
    pattern = r"(2\.|II\.|I\.|2/|2°/)[\s+]*(Biopsies\s+trans[ -]*bronchiques|Biopsies\s+transbronchiques|Biospies\s+transbronchiques|BTB)[\s\S+]*?Technique\s*:\s*([^;]+);\s*([^n]+)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)

    if not match:
        # Sometimes, there isn't the numbers, only "Biopsie" in text etc..
        fallback_pattern = r"(Biopsies\s+trans[ -]*bronchiques|Biopsies\s+transbronchiques|Biospies\s+transbronchiques|BTB)[\s\S+]*?Technique\s*:\s*([^;]+);\s*([^n]+)"
        fallback_match = re.search(fallback_pattern, text, re.DOTALL)
        if fallback_match:
            return fallback_match.group(3).strip()

        else:
            # No mention of biopsie or lavage, just the mention of techniques two times. The BTB technique is always second.
            parts = re.split(r"(?=Technique\s*:)", text, flags=re.IGNORECASE)
            two_parts_fallback_pattern = r"Technique\s*:\s*([^;]+);\s*([^n]+)"
            if len(parts) > 2:
                two_parts_fallback_match = re.search(
                    two_parts_fallback_pattern, parts[-1], re.DOTALL
                )
                if two_parts_fallback_match:
                    return two_parts_fallback_match.group(2).strip()

            # Else, look at any mention of technique in the document
            else:
                last_fallback_pattern = r"Technique\s*:\s*([^;]+);\s*([^n]+)"
                last_fallback_match = re.search(
                    last_fallback_pattern, text, re.DOTALL)
                if last_fallback_match:
                    return last_fallback_match.group(2).strip()

    return match.group(4).strip() if match else None


def extract_information(text, patterns):
    """
    Extracts information based on specified patterns from a given text. Each pattern corresponds to a specific field
    that needs to be extracted.

    Parameters:
    - text (str): The text to extract information from.
    - patterns (list of dict): A list of dictionaries, each containing 'field', 'pattern', and 'group_index' keys,
      where 'field' is the name of the field to extract, 'pattern' is the regex pattern, and 'group_index' is the
      index of the group in the pattern that contains the desired information.

    Returns:
    - dict: A dictionary where each key is a 'field' from the patterns list and each value is the extracted information
      for that field, or None if the information could not be found.
    """
    results = {}
    for item in patterns:
        field = item["field"]
        pattern = item["pattern"]
        group_index = item["group_index"]
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            results[field] = match.group(group_index).strip()
        else:
            results[field] = None
    return results


def process_text_files_in_directory(directory_path):
    """
    Processes all text files in a given directory, extracting specified information from each file and compiling
    it into a pandas DataFrame.

    Parameters:
    - directory_path (str): The path to the directory containing the text files to be processed.

    Returns:
    - pandas.DataFrame: A DataFrame where each row corresponds to a text file and each column corresponds to a
      field of information extracted from the files. If no data is found, returns an empty DataFrame.
    """
    data = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()

            info = extract_information(text, PATTERNS)
            info["Prénom"] = extract_prenom_before_docteur(text)
            # Directly add or update keys in the dictionary
            info["Filename"] = filename
            info["IPP"] = filename[:9]
            info["Technique"] = extract_technique(text)
            info["Niveaux de coupes"] = extract_niveaux_coupes(text)
            data.append(info)

    if data:
        all_columns = list(data[0].keys())
        column_order = COLUMN_ORDER + [
            col for col in all_columns if col not in COLUMN_ORDER
        ]
        df = pd.DataFrame(data, columns=column_order)
    else:
        df = pd.DataFrame(data)

    return df


PATTERNS = [
    {
        "field": "Nom",
        "pattern": r"(?i)(^Nom\s*:\s*|Nom[\s+]*usuel\s*:\s*|Nom\s*:\s*)([A-Z]+)",
        "group_index": 2,
    },
    # Prénom -> Propre fonction
    {
        "field": "Date de naissance",
        "pattern": r"(?i)(Date[\s+]*de[\s+]*naissance\s*:\s*)(\d{2}/\d{2}/\d{4})",
        "group_index": 2,
    },
    {"field": "Sexe", "pattern": r"Sexe\s*:\s*([MF])", "group_index": 1},
    {
        "field": "Date de prélèvement",
        "pattern": r"(?i)(Prélevé le \s*:\s*|Prélevé[\s+]*le\s*:\s*)(\d{2}/\d{2}/\d{4})",
        "group_index": 2,
    },
    # Technique -> Trop particulier, on a la propre fonction
    # Niveau de coupes -> De même
    {"field": "Site",
        "pattern": r"(Site[\s\xa0]*:)([\S]*[^\n]+)", "group_index": 2},
    {
        "field": "Nombre de fragment alvéolaire",
        "pattern": r"(Nombre[\s\xa0]*de[\s\xa0]*fragments[\s\xa0]*alvéolaires[\s\xa0]*:)([\S]*[^\n]+)",
        "group_index": 2,
    },
    {
        "field": "Bronches/Bronchioles",
        "pattern": r"(Bronches\/Bronchioles[\s\xa0]*:[\s\xa0]*|Bronches[\s\xa0]*\/[\s\xa0]*Bronchioles[\s\xa0]*:[\s\xa0]*)([\S]*[^\n]+)",
        "group_index": 2,
    },
    {
        "field": "Infiltrat",
        "pattern": r"(Infiltrat[\s\xa0]*mononucléé[\s\xa0]*péri(?:-|\s*)?vasculaire[\s\xa0]*\(A0[\s\xa0]*à[\s\xa0]*A4[\s\xa0]*\/[\s\xa0]*AX\)[\s\xa0]*:*:[\s\xa0]*|Infiltrat[\s\xa0]*mononucléé[\s\xa0]*péri(?:-|\s*)?vasculaire[\s\xa0]*\(A[\s\xa0]*\)[\s\xa0]*:*:[\s\xa0]*)([\S]*[^\n]+)",
        "group_index": 2,
    },
    {
        "field": "Bronchiolite Lymphocytaire",
        "pattern": r"(Bronchiolite[\s\xa0]*lymphocytaire[\s\xa0]*\(B0[\s\xa0]*\/[\s\xa0]*1R[\s\xa0]*\/[\s\xa0]*2R[\s\xa0]*\/[\s\xa0]*BX\)[\s\xa0]*:*:[\s\xa0]*|Bronchiolite[\s\xa0]*lymphocytaire[\s\xa0]*\(B[\s\xa0]*\)[\s\xa0]*:*:[\s\xa0]*)([\w]*)",
        "group_index": 2,
    },
    {
        "field": "Inflammation Lymphocytaire",
        "pattern": r"(Inflammation[\s\xa0]*lymphocytaire[\s\xa0]*bronchique[\s\xa0]*\([\s\xa0]*oui[\s\xa0]*\/[\s\xa0]*non[\s\xa0]*\)[\s\xa0]*:*:[\s\xa0]*)([\w]*)",
        "group_index": 2,
    },
    {
        "field": "Bronchiolite oblitérante",
        "pattern": r"Bronchiolite[\s\xa0]*(oblitérante|constrictive)[\s\xa0]*:*[\s\xa0]*([\w\s]*)",
        "group_index": 2,
    },
    {
        "field": "Fibro-élastose interstitielle",
        "pattern": r"(Fibro(?:-|\s*)?élastose[\s\xa0]*interstitielle [\s\xa0]*\([\s\xa0]*0[\s\xa0]*ou[\s\xa0]*1[\s\xa0]*\)[\s\xa0]*:*:[\s\xa0]*)([\w]*)",
        "group_index": 2,
    },
    {
        "field": "PNN dans les cloisons alvéolaires",
        "pattern": r"((PNN[\s\xa0]*dans[\s\xa0]*les[\s\xa0]*capillaires[\s\xa0]*alvéolaires[\s\xa0]*\(0[\s\xa0]*à[\s\xa0]*\+\+\+[\s\xa0]*\)[\s\xa0]*:*:[\s\xa0]*|PNN[\s\xa0]*dans[\s\xa0]*les[\s\xa0]*cloisons[\s\xa0]*alvéolaires[\s\xa0]*\(0[\s\xa0]*à[\s\xa0]*\+\+\+[\s\xa0]*\)[\s\xa0]*:*:[\s\xa0]*)([^\n]+))",
        "group_index": 3,
    },
    {
        "field": "Cellules mononucléées",
        "pattern": r"(Cellules[\s\xa0]*mononucléées[\s\xa0]*dans[\s\xa0]*les[\s\xa0]*capillaires[\s\xa0]*alvéolaires[\s\xa0]*\(0[\s\xa0]*à[\s\xa0]*\+\+\+[\s\xa0]*\)[\s\xa0]*:*:[\s\xa0]*|Cellules[\s\xa0]*mononuclées[\s\xa0]*\(lymphocytes[\s\xa0]*ou[\s\xa0]*macrophages[\s\xa0]*dans[\s\xa0]*les[\s\xa0]*cloisons[\s\xa0]*alvéolaires\)[\s\xa0]*\(0[\s\xa0]*à[\s\xa0]*\+\+\+[\s\xa0]*\)[\s\xa0]*:*:[\s\xa0]*)([\S]*[^\n]+)",
        "group_index": 2,
    },
    {
        "field": "Dilatation des capillaires alvéolaires",
        "pattern": r"(Dilatation[\s\xa0]*des[\s\xa0]*capillaires[\s\xa0]*alvéolaires[\s\xa0]*\(0[\s\xa0]*à[\s\xa0]*\+\+\+[\s\xa0]*\)[\s\xa0]*:*:[\s\xa0]*)([\S]*[^\n]+)",
        "group_index": 2,
    },
    {
        "field": "Œdème des cloisons alvéolaires",
        "pattern": r"((Œdème|Oedème)[\s\xa0]*des[\s\xa0]*cloisons[\s\xa0]*alvéolaires[\s\xa0]*\(0[\s\xa0]*à[\s\xa0]*\+\+\+[\s\xa0]*\)[\s\xa0]*:*:[\s\xa0]*)([\S]*[^\n])",
        "group_index": 3,
    },
    {
        "field": "Thrombi fibrineux dans les capillaires alvéolaires",
        "pattern": r"(Thrombi[\s\xa0]*fibrineux[\s\xa0]*dans[\s\xa0]*les[\s\xa0]*capillaires[\s\xa0]*alvéolaires[\s\xa0]*\(0[\s\xa0]*à[\s\xa0]*\+\+\+[\s\xa0]*\)[\s\xa0]*:*:[\s\xa0]*)([\S]*[^\n])",
        "group_index": 2,
    },
    {
        "field": "Débris cellulaires dans les cloisons alvéolaires",
        "pattern": r"(Débris[\s\xa0]*cellulaires[\s\xa0]*dans[\s\xa0]*les[\s\xa0]*cloisons[\s\xa0]*alvéolaires[\s\xa0]*\(0[\s\xa0]*à[\s\xa0]*\+\+\+[\s\xa0]*\)[\s\xa0]*:*:[\s\xa0]*)([\S]*[^\n])",
        "group_index": 2,
    },
    {
        "field": "Epaississement fibreux des cloisons alvéolaires",
        "pattern": r"(Epaississement[\s\xa0]*fibreux[\s\xa0]*des[\s\xa0]*cloisons[\s\xa0]*alvéolaires[\s\xa0]*(?:\w*)?\(0[\s\xa0]*à[\s\xa0]*\+\+\+[\s\xa0]*\)[\s\xa0]*:*:[\s\xa0]*)([\S]*[^\n])",
        "group_index": 2,
    },
    {
        "field": "Hyperplasie pneumocytaire",
        "pattern": r"(Hyperplasie[\s\xa0]*pneumocytaire[\s\xa0]*\(0[\s\xa0]*à[\s\xa0]*\+\+\+[\s\xa0]*\)[\s\xa0]*:*:[\s\xa0]*)([\S]*[^\n])",
        "group_index": 2,
    },
    {
        "field": "PNN dans les espaces alvéolaires",
        "pattern": r"(PNN[\s\xa0]*dans[\s\xa0]*les[\s\xa0]*espaces[\s\xa0]*alvéolaires[\s\xa0]*\(0[\s\xa0]*à[\s\xa0]*\+\+\+[\s\xa0]*\)[\s\xa0]*:*:[\s\xa0]*|PNN[\s\xa0]*dans[\s\xa0]*les[\s\xa0]*espaces[\s\xa0]*alvéolaires[\s\xa0]*\(0[\s\xa0]*à[\s\xa0]*\+\+\+[\s\xa0]*\)[\s\xa0]*:*:[\s\xa0]*)([^\n]+)",
        "group_index": 2,
    },
    {
        "field": "Macrophages dans les espaces alvéolaires",
        "pattern": r"(Macrophages[\s\xa0]*dans[\s\xa0]*les[\s\xa0]*espaces[\s\xa0]*alvéolaires[\s\xa0]*\(0[\s\xa0]*à[\s\xa0]*\+\+\+[\s\xa0]*\)[\s\xa0]*:*:[\s\xa0]*)([\S]*[^\n])",
        "group_index": 2,
    },
    {
        "field": "Bourgeons conjonctifs dans les espaces alvéolaires",
        "pattern": r"(Bourgeons[\s\xa0]*conjonctifs[\s\xa0]*dans[\s\xa0]*les[\s\xa0]*espaces[\s\xa0]*alvéolaires[\s\xa0]*\(0[\s\xa0]*à[\s\xa0]*\+\+\+[\s\xa0]*\)[\s\xa0]*:*:[\s\xa0]*)([\S]*[^\n])",
        "group_index": 2,
    },
    {
        "field": "Hématies dans les espaces alvéolaires",
        "pattern": r"(Hématies[\s\xa0]*dans[\s\xa0]*les[\s\xa0]*espaces[\s\xa0]*alvéolaires[\s\xa0]*\(0[\s\xa0]*à[\s\xa0]*\+\+\+[\s\xa0]*\)[\s\xa0]*:*:[\s\xa0]*)([\S]*[^\n])",
        "group_index": 2,
    },
    {
        "field": "Membranes hyalines",
        "pattern": r"(Membranes[\s\xa0]*hyalines[\s\xa0]*\(0[\s\xa0]*à[\s\xa0]*\+\+\+[\s\xa0]*\)[\s\xa0]*:*:[\s\xa0]*)([\S]*[^\n])",
        "group_index": 2,
    },
    {
        "field": "Fibrine dans les espaces alvéolaires",
        "pattern": r"(Fibrine[\s\xa0]*dans[\s\xa0]*les[\s\xa0]*espaces[\s\xa0]*alvéolaires[\s\xa0]*\(0[\s\xa0]*à[\s\xa0]*\+\+\+[\s\xa0]*\)[\s\xa0]*:*:[\s\xa0]*)([\S]*[^\n])",
        "group_index": 2,
    },
    {
        "field": "Inflammation sous-pleurale, septale, bronchique ou bronchiolaire",
        "pattern": r"(Inflammation[\s\xa0]*sous(\-|[\s\xa0])?pleurale,[\s\xa0]*septale,[\s\xa0]*bronchique[\s\xa0]*ou[\s\xa0]*bronchiolaire[\s\xa0]*\(0[\s\xa0]*à[\s\xa0]*\+\+\+[\s\xa0]*\)[\s\xa0]*:*:[\s\xa0]*)([\S]*[^\n])",
        "group_index": 3,
    },
    {
        "field": "BALT",
        "pattern": r"(BALT[\s\xa0]*\(oui\/non\)[\s\xa0]*:*:[\s\xa0]*)([\S]*[^\n])",
        "group_index": 2,
    },
    {
        "field": "Thrombus fibrino-cruorique",
        "pattern": r"(Thrombus[\s\xa0]*fibrino(\-|[\s\xa0]|)?cruorique[\s\xa0]*(\(oui\/non\)|)?[\s\xa0]*:*:[\s\xa0]*)([\S]*[^\n])",
        "group_index": 4,
    },
    {
        "field": "Nécrose ischémique",
        "pattern": r"(Nécrose[\s\xa0]*ischémique[\s\xa0]*(\(oui\/non\)|)?[\s\xa0]*:*:[\s\xa0]*)([\S]*[^\n])",
        "group_index": 3,
    },
    {
        "field": "Inclusions virales",
        "pattern": r"(Inclusions[\s\xa0]*virales[\s\xa0]*(\(oui\/non\)|)?[\s\xa0]*:*:[\s\xa0]*)([\S]*[^\n])",
        "group_index": 3,
    },
    {
        "field": "Agent pathogène",
        "pattern": r"(Agent[\s\xa0]*pathogène[\s\xa0]*(\(oui\/non\)|)?[\s\xa0]*:*:[\s\xa0]*)([\S]*[^\n])",
        "group_index": 3,
    },
    {
        "field": "Eosinophilie (interstitielle/alvéolaire)",
        "pattern": r"(Eosinophilie[\s\xa0]*(\(interstitielle\/alvéolaire\)|)?[\s\xa0]*(\(oui\/non\)|)?[\s\xa0]*:*:[\s\xa0]*)([\S]*[^\n])",
        "group_index": 4,
    },
    {
        "field": "Remodelage vasculaire",
        "pattern": r"(Remodelage[\s\xa0]*vasculaire[\s\xa0]*[\s\xa0]*(\(oui\/non\)|)?[\s\xa0]*:*:[\s\xa0]*)([\S]*[^\n])",
        "group_index": 3,
    },
    {
        "field": "Matériel étranger d’inhalation",
        "pattern": r"(Matériel[\s\xa0]*étranger[\s\xa0]*d’inhalation[\s\xa0]*(\(oui\/non\)|)?[\s\xa0]*:*:[\s\xa0]*)([\S]*[^\n])",
        "group_index": 3,
    },
    {
        "field": "Conclusion",
        "pattern": r"(Conclusion[\s\xa0]*(:.*|)?)([\s\S]*)",
        "group_index": 3,
    },
]

COLUMN_ORDER = [
    "Filename",
    "IPP",
    "Nom",
    "Prénom",
    "Date de naissance",
    "Sexe",
    "Date de Prélèvement",
    "Technique",
    "Niveaux de coupes",
    "Site",
    "Nombre de fragment alvéolaire",
    "Bronches/Bronchioles",
    "Infiltrat",
    "Bronchiolite Lymphocytaire",
    "Inflammation Lymphocytaire",
    "Bronchiolite oblitérante",
    "Fibro-élastose interstitielle",
    "PNN dans les cloisons alvéolaires",
    "Cellules mononucléées",
    "Dilatation des capillaires alvéolaires",
    "Œdème des cloisons alvéolaires",
    "Thrombi fibrineux dans les capillaires alvéolaires",
    "Débris cellulaires dans les cloisons alvéolaires",
    "Epaississement fibreux des cloisons alvéolaires",
    "Hyperplasie pneumocytaire",
    "PNN dans les espaces alvéolaires",
    "Macrophages dans les espaces alvéolaires",
    "Bourgeons conjonctifs dans les espaces alvéolaires",
    "Hématies dans les espaces alvéolaires",
    "Membranes hyalines",
    "Fibrine dans les espaces alvéolaires",
    "Inflammation sous-pleurale, septale, bronchique ou bronchiolaire",
    "BALT",
    "Thrombus fibrino-cruorique",
    "Nécrose ischémique",
    "Inclusions virales",
    "Agent pathogène",
    "Eosinophilie (interstitielle/alvéolaire)",
    "Remodelage vasculaire",
    "Matériel étranger d’inhalation",
    "Conclusion",
]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process BTB text files in a folder and extract information into an Excel file."
    )
    parser.add_argument(
        "directory_path",
        type=str,
        help="The path to the folder containing text files to process.",
    )
    args = parser.parse_args()

    directory_path = args.directory_path
    df = process_text_files_in_directory(directory_path)

    df.to_excel("BTBextract_2020-2021.xlsx", index=False)
    print(
        "Extraction complete! You can see the result in the Extractor folder named as 'BTBextract_2020-2021.xlsx'"
    )
