import argparse
import os
import re
import warnings
from datetime import datetime

import pandas as pd

warnings.filterwarnings("ignore")

"""
This script is designed to extract information from BTB documents in .txt version, specifically targeting documents dated from 2021 to 2019. It has been tailored to understand and process the formatting and content specific to these years. Users can run this script to parse directories containing text files of BTB documents and extract relevant information into a structured Excel spreadsheet.

Please note that while this script is optimized for documents from 2021 to 2019, it has not been extensively tested on documents from years prior to 2019. If you need to process documents from before 2019, additional testing and potentially some modifications to the script may be necessary to ensure accurate extraction of information.

Usage:
To run this script, provide the directory path containing the BTB text documents as a command-line argument. The script will process all text files within the specified directory, extract the relevant information, and compile it into an Excel file named 'BTBextract_2020-2021.xlsx'.

Example:
python your_script_name.py <path_to_your_folder>

Make sure these dependencies are installed in your Python environment before running the script.
"""


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
def extract_technique(text, option="lba"):
    """
    Extracts the medical technique (BTB or LBA) from a given text based on various patterns.
    """
    if option.lower() == "btb":
        # Patterns for BTB (Biopsies Transbronchiques)
        technique_pattern = r"(2\.|II\.|I\.|2/|2°/)[\s+]*(Biopsies\s+trans[ -]*bronchiques|Biopsies\s+transbronchiques|Biospies\s+transbronchiques|BTB)(?:(?!LAVAGE)[\s\S+])*?Technique[^\S\r\n]*:[^\S\r\n]*([^;]+)"
        fallback_technique_pattern = r"(Biopsies\s+trans[ -]*bronchiques|Biopsies\s+transbronchiques|Biospies\s+transbronchiques|BTB)(?:(?!LAVAGE)[\s\S])*?Technique\s*:\s*([^;]+)"
        fallback_technique_mention = "HES"
    elif option.lower() == "lba":
        # Patterns for LBA (Lavage Bronchoalvéolaire)
        technique_pattern = r"(1\.|I\.|I\.|1/|1°/)[\s+]*(Lavage\s+bronchoalvéolaire|Lavage\s+broncho-alvéolaire|LBA)(?:(?!BIOPSIE)[\s\S+])*?Technique[^\S\r\n]*:[^\S\r\n]*([^;]+)"
        fallback_technique_pattern = r"(Lavage\s+bronchoalvéolaire|Lavage\s+broncho-alvéolaire|LBA)(?:(?!BIOPSIE)[\s\S])*?Technique\s*:\s*([^;]+)"
        fallback_technique_mention = "cytocentrifugation"
    else:
        raise ValueError("Invalid option. Choose 'btb' or 'lba'.")

    # Primary pattern search
    technique_match = re.search(technique_pattern, text, re.DOTALL | re.IGNORECASE)
    if technique_match:
        return technique_match.group(3).strip()

    # Fallback pattern search
    fallback_match = re.search(fallback_technique_pattern, text, re.DOTALL | re.IGNORECASE)
    if fallback_match:
        return fallback_match.group(2).strip()

    # Check for fallback mention if no patterns match
    if fallback_technique_mention.lower() in text.lower():
        return fallback_technique_mention

    # No mention of biopsie or lavage, just the mention of techniques two times
    # Replace split with a simpler search
    technique_search_pattern = r"Technique\s*:\s*([^;]+)"
    technique_matches = re.findall(technique_search_pattern, text, re.IGNORECASE | re.DOTALL)
    if technique_matches:
        return technique_matches[0].strip()

    # Last fallback: look for any mention of technique in the document
    last_fallback_technique_pattern = r"Technique\s*:\s*([^;]+)"
    last_fallback_match = re.search(last_fallback_technique_pattern, text, re.DOTALL)
    if last_fallback_match:
        return last_fallback_match.group(1).strip()

    return None


def extract_niveaux_coupes(text):
    """
    Extracts the levels of cuts (niveaux de coupes) from a given text.
    Specifically looks for patterns like "X niveaux de coupes" after technique specification.

    Parameters:
    - text (str): The text from which the levels of cuts are to be extracted.

    Returns:
    - str or None: The extracted levels of cuts if found, otherwise None.
    """
    # Pattern direct: chercher "X niveaux de coupes" après "Technique : HES ;"
    direct_pattern = r"Technique\s*:\s*HES\s*;\s*(\d+)\s*niveaux?\s*de\s*coupes?"
    direct_match = re.search(direct_pattern, text, re.IGNORECASE)
    if direct_match:
        return direct_match.group(1).strip()

    # Pattern alternatif: chercher juste "X niveaux de coupes" n'importe où
    alt_pattern = r"(\d+)\s*niveaux?\s*de\s*coupes?"
    alt_match = re.search(alt_pattern, text, re.IGNORECASE)
    if alt_match:
        return alt_match.group(1).strip()

    # Most found pattern (ancien pattern)
    pattern = r"(2\.|II\.|I\.|2/|2°/)[\s+]*(Biopsies\s+trans[ -]*bronchiques|Biopsies\s+transbronchiques|Biospies\s+transbronchiques|BTB)[\s\S+]*?Technique\s*:\s*([^;]+);\s*([^n]+)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(4).strip()

    # Sometimes, there isn't the numbers, only "Biopsie" in text etc..
    fallback_pattern = r"(Biopsies\s+trans[ -]*bronchiques|Biopsies\s+transbronchiques|Biospies\s+transbronchiques|BTB)(?:(?!LAVAGE)[\s\S])*?Technique\s*:\s*([^;]+);\s*([^n]+)"
    fallback_match = re.search(fallback_pattern, text, re.DOTALL)
    if fallback_match:
        return fallback_match.group(3).strip()

    # Check for HES after failing to find the first two patterns
    if "HES" in text:
        return None

    # No mention of biopsie or lavage, just the mention of techniques two times. The BTB technique is always second.
    parts = re.split(r"(?=Technique\s*:)", text, flags=re.IGNORECASE)
    if len(parts) > 2:
        two_parts_fallback_technique_pattern = r"Technique\s*:\s*([^;]+);\s*([^n]+)"
        two_parts_fallback_match = re.search(
            two_parts_fallback_technique_pattern, parts[-1], re.DOTALL
        )
        if two_parts_fallback_match:
            return two_parts_fallback_match.group(2).strip()

    # Else, look at any mention of technique in the document
    last_fallback_technique_pattern = r"Technique\s*:\s*([^;]+);\s*([^n]+)"
    last_fallback_match = re.search(
        last_fallback_technique_pattern, text, re.DOTALL
    )
    if last_fallback_match:
        return last_fallback_match.group(2).strip()

    return None


def detect_modele_btb(text, date_prelevement=None):
    """
    Détecte si le document BTB est en texte libre ou semi-structuré.

    Critères:
    - Avant 2011: considéré comme texte libre
    - Présence de champs structurés (Site:, Infiltrat:, etc.): semi-structuré

    Parameters:
    - text (str): Le contenu du document BTB
    - date_prelevement (str): La date de prélèvement au format DD/MM/YYYY

    Returns:
    - str: "texte_libre" ou "semi_structure"
    """
    # Vérifier la date de prélèvement
    if date_prelevement:
        try:
            # Essayer de parser la date
            if isinstance(date_prelevement, str):
                date_obj = datetime.strptime(date_prelevement, "%d/%m/%Y")
                if date_obj.year < 2011:
                    return "texte_libre"
        except (ValueError, TypeError):
            pass

    # Chercher des patterns de champs structurés typiques du format semi-structuré
    structured_patterns = [
        r"Site\s*:",
        r"Infiltrat\s*mononucléé",
        r"Bronchiolite\s*lymphocytaire",
        r"Nombre\s*de\s*fragments?\s*alvéolaires?",
        r"Rejet\s*cellulaire\s*:",
        r"Rejet\s*chronique\s*:",
        r"Atteinte\s*du\s*compartiment",
        r"PNN\s*dans\s*les\s*cloisons",
        r"Bronchiolite\s*oblitérante\s*\(",
    ]

    structured_count = 0
    for pattern in structured_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            structured_count += 1

    # Si au moins 3 patterns structurés sont trouvés, c'est semi-structuré
    if structured_count >= 3:
        return "semi_structure"

    return "texte_libre"


def extract_texte_libre_complet(text, modele_btb):
    """
    Si le document est en texte libre, retourne l'intégralité du texte.

    Parameters:
    - text (str): Le contenu du document BTB
    - modele_btb (str): Le type de modèle ("texte_libre" ou "semi_structure")

    Returns:
    - str or None: Le texte complet si texte libre, None sinon
    """
    if modele_btb == "texte_libre":
        # Nettoyer les espaces excessifs mais garder la structure
        cleaned_text = re.sub(r'[ \t]+', ' ', text)
        cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)
        return cleaned_text.strip()
    return None


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
        group_index = item.get("group_index")
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        
        if match:
            # Special handling for the "Nom" field to concatenate groups 3 and 4
            if field == "Nom" and len(match.groups()) >= 4:
                # Assuming groups 3 and 4 may contain the parts of the name you're interested in
                part3 = match.group(3) if match.group(3) is not None else ''
                part4 = match.group(4) if match.group(4) is not None else ''
                # Concatenate the parts, trimming any leading/trailing whitespace
                results[field] = (part3 + part4).strip()
            else:
                # For all other fields, or if "Nom" does not have groups 3 and 4
                results[field] = match.group(group_index).strip()
        else:
            results[field] = None
    return results
import chardet

def read_text_file(file_path):
    """
    Reads the content of a text file and returns it as a string.
    Uses chardet to detect the correct encoding.
    """
    # D'abord detecter l'encodage avec chardet
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        detected = chardet.detect(raw_data)
        encoding = detected['encoding']
        
    # Utiliser l'encodage détecté pour lire le fichier
    try:
        with open(file_path, 'r', encoding=encoding) as file:
            text = file.read()
            print(f"Encodage détecté: {encoding}")
            return text
    except:
        # Fallback sur une lecture binaire avec décodage forcé
        try:
            return raw_data.decode('iso-8859-1')
        except:
            return raw_data.decode('utf-8', errors='replace')
        
    
def process_text_files_in_directory(directory_path):
    data = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory_path, filename)
            text = read_text_file(file_path)  # Utilisation de la fonction read_text_file
            print("Début du texte:", text[:200].replace('\n', '\\n'))  # Debug

            # Debug - cherchons les patterns manuellement
            biopsy_pattern = r"(?:^|\n)[\s\xa0]*N°[\s\xa0]*(?:de\s*demande\s*:\s*|P[\s\xa0]*)([.\w-]+)"
            date_pattern = r"Prélevé[\s\xa0]*le[\s\xa0]*:[\s\xa0]*(\d{2}/\d{2}/\d{4})"

            biopsy_match = re.search(biopsy_pattern, text, re.DOTALL | re.IGNORECASE)
            date_match = re.search(date_pattern, text, re.DOTALL | re.IGNORECASE)

            print(f"\nFichier: {filename}")
            print(f"Biopsy match: {biopsy_match.group(1) if biopsy_match else None}")
            print(f"Date match: {date_match.group(1) if date_match else None}")

            info = extract_information(text, PATTERNS)
            info["Technique"] = extract_technique(text, option="lba")
            info["Prénom"] = extract_prenom_before_docteur(text)
            info["Filename"] = filename
            info["IPP"] = filename.split("_")[0]

            # Extraction améliorée du niveau de coupes
            info["Niveaux de coupes"] = extract_niveaux_coupes(text)

            # Détection du modèle BTB (texte libre vs semi-structuré)
            date_prelevement = info.get("Date de prélèvement")
            info["Modele_BTB"] = detect_modele_btb(text, date_prelevement)

            # Si texte libre, conserver le texte complet
            info["Texte_libre_complet"] = extract_texte_libre_complet(text, info["Modele_BTB"])

            data.append(info)

    if data:
        all_columns = list(data[0].keys())
        print(f"Available columns: {all_columns}")
        column_order = COLUMN_ORDER + [
            col for col in all_columns if col not in COLUMN_ORDER
        ]
        df = pd.DataFrame(data, columns=column_order)
    else:
        df = pd.DataFrame(data)

    return df

def sanitize_for_excel(value):
    # Remove characters that are illegal in Excel sheet names
    if isinstance(value, str):
        # This regex removes control characters (\x00-\x1F) and (\x7F)
        sanitized_value = re.sub(r'[\x00-\x1F\x7F]', '', value)
 
        return sanitized_value
    
    return value

def remove_illegal_chars(s):
    # This will remove control characters while preserving accented characters
    if isinstance(s, str):
        # Remove control characters (ASCII 0-31 and 127) but keep accented characters
        return re.sub(r'[\x00-\x1F\x7F]', '', s)
    return s

PATTERNS = [
    {
        "field": "Nom",
        "pattern": r"(?i)((?<!Pré)Nom\s*:\s*|Nom[\s+]*usuel\s*:\s*)(?:Mme\s+)?(([A-Z]+)([\s]*(?:\s*(Pr))?[A-Z]*))(?:\s*(Destinataire))?",
        "group_index": 3,
    },
    # Prénom -> Propre fonction
    {
        "field": "Date de naissance",
        "pattern": r"(?i)(Date[\s+]*de[\s+]*naissance\s*:\s*)(\d{2}/\d{2}/\d{4})",
        "group_index": 2,
    },

    {
        "field": "Biopsy ID",
        "pattern": r"((N°\s+de\s+demande\s+:\s+)|(N°\s+P\s+)|(N°\s+S\s+))(\w+-\w+|\w+.\w+)",
        "group_index": 5,
    },

    {"field": "Sexe", "pattern": r"Sexe\s*:\s*([MF])", "group_index": 1},
    {
        "field": "Date de prélèvement",
        "pattern": r"(?i)(Prélevé[\s\xa0]*le[\s\xa0]*[\s\xa0]*:[\s\xa0\D]*)(\d{2}/\d{2}/\d{4})",
        "group_index": 2,
    },

    {"field": "Prescripteur", "pattern": r"Docteur\s+([A-Za-zÀ-ÿ\s\.-]+?)(?=(?:,\s*Compte-rendu|\s*\n\s*ADICAP|\s*\n\s*(?:\n\s*)*\d{2}\/\d{2}\/\d{4}))", "group_index": 1},

    #---------------------EXTRACTION BTB----------------------

    # Technique -> Trop particulier, on a la propre fonction
    # Niveau de coupes -> De même

    {"field": "Site",
        "pattern": r"(Site[\s\xa0]*:)([\S]*[^\n]+)", "group_index": 2},
    {
        "field": "Nombre de fragment alvéolaire",
        "pattern": r"(Nombre[\s\xa0]*de[\s\xa0]*fragments[\s\xa0]*alvéolaires[\s\xa0]*:|Nombre[\s\xa0]*de[\s\xa0]*fragments[\s\xa0]*de[\s\xa0]*tissu(s)?[\s\xa0]*alvéolaire(s)?[\s\xa0]*:)([\S]*[^\n]+)",
        "group_index": 4,
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
        "pattern": r"Bronchiolite[\s\xa0]*(oblitérante|constrictive)(?:[\s\xa0]*\((0[\s\xa0]*ou[\s\xa0]*1)\))?[\s\xa0]*:[\s\xa0]*(\w)",
        "group_index": 3,
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
        "pattern": r"((Conclusion|C[\s\xa0]O[\s\xa0]N[\s\xa0]C[\s\xa0]L[\s\xa0]U[\s\xa0]S[\s\xa0]I[\s\xa0]O[\s\xa0]N)[\s\xa0]*(:.*|))([\s\S]*)",
        "group_index": 4,
    },

    #-------------------------------------------------------------------------------------------------------------
    
    #---------------------EXTRACTION LBA----------------------


    # {
    #     "field": "Technique",
    #     "pattern": r"(?:^|\n)[\s\xa0]*Technique[\s\xa0]*:[\s\xa0]*([^\.]+)(?=\.)",
    #     "group_index": 1,
    # },
    # {
    #     "field": "Colorations",
    #     "pattern": r"Colorations[\s\xa0]*:[\s\xa0]*([^\.]+?)(?=\.|\s*Volume|\n|$)",
    #     "group_index": 1,
    # },
    # {
    #     "field": "Volume",
    #     "pattern": r"(?:^|\n)[\s\xa0]*Volume[\s\xa0]*:[\s\xa0]*(\d+(?:[\s\xa0]*(?:[mM][lL]|[lL]|ML))?)(?=\.|\n|$)",
    #     "group_index": 1,
    # },
    # {
    #     "field": "Aspect",
    #     "pattern": r"Aspect[\s\xa0]*:[\s\xa0]*([^\n]+?)[\s\xa0]*(?:\n|$)",
    #     "group_index": 1,
    # },

    # {
    #     "field": "Numération",
    #     "pattern": r"(Numération[\s\xa0]*:[\s\xa0]*)([\d\s\.,]+.*?(?=\n|$))",
    #     "group_index": 2,
    # },

    # {
    #     "field": "Macrophages",
    #     "pattern": r"-[\s\xa0]*Macrophages[\s\xa0]*:[\s\xa0]*(\d+)(?:\s*%)",
    #     "group_index": 1,
    # },

    # {
    #     "field": "Sidérophages",
    #     "pattern": r"\(?Sidérophages(?:[\s\xa0]*[^:\n\()]+)?[\s\xa0]*:[\s\xa0]*([^%\n\.]+?)(?=%|\.|$)",
    #     "group_index": 1,
    # },


    # # {
    # #     "field": "Intensité",
    # #     "pattern": r"Intensité(?:[\s\xa0]+[^:\n]+)?[\s\xa0]*:[\s\xa0]*([^\.]+)(?=\.)",
    # #     "group_index": 1,
    # # },

    # {
    #     "field": "Score_Golde",
    #     "pattern": r"Score[\s\xa0]*de[\s\xa0]*Golde(?:[\s\xa0]+[^:\n]+)?[\s\xa0]*:[\s\xa0]*([^\n\.\w]*?)(?=\.|\n|Lymphocytes|$)",
    #     "group_index": 1,
    # },


    # {
    #     "field": "Lymphocytes",
    #     "pattern": r"(Lymphocytes[\s\xa0]*(\(oui\/non\)|)?[\s\xa0]*:*:[\s\xa0]*)([\S]*[^\n])",
    #     "group_index": 3,
    # },

    # {
    #     "field": "Polynucléaires neutrophiles",
    #     "pattern": r"Polynucléaires[\s\xa0]*(neutrophiles)(?:[\s\xa0]*\((0[\s\xa0]*ou[\s\xa0]*1)\))?[\s\xa0]*:[\s\xa0]*(\w*)",
    #     "group_index": 3,
    # },

    # {
    #     "field": "Polynucléaires éosinophiles",
    #     "pattern": r"(Polynucléaires[\s\xa0]*éosinophiles[\s\xa0]*(\(oui\/non\)|)?[\s\xa0]*:*:[\s\xa0]*)([\S]*[^\n])",
    #     "group_index": 3,
    # },

    # {
    #     "field": "Autres éléments",
    #     "pattern": r"(Autres[\s\xa0]*éléments[\s\xa0]*(\(oui\/non\)|)?[\s\xa0]*:*:[\s\xa0]*)([\S]*[^\n])+",
    #     "group_index": 3,
    # },

    # {
    # "field": "Agents_pathogenes",
    # "pattern": r"(?:^|\n)[\s\xa0]*Agents[\s\xa0]*pathogènes[\s\xa0]*:[\s\xa0]*([^\n]+)",
    # "group_index": 1,
    # },


    # {
    #     "field": "Pneumocystis",
    #     "pattern": r"-\s*Pneumocystis\s+Jorivecii\s*:\s*([^\n]+)",
    #     "group_index": 1,
    # },

    # {
    #     "field": "Mycoses",
    #     "pattern": r"-\s*Mycoses\s*:\s*([^\n]+)",
    #     "group_index": 1,
    # },

    #     {
    #     "field": "Mycobacteries",
    #     "pattern": r"-\s*Mycobactéries\s*:\s*([^\n]+)",
    #     "group_index": 1,
    # },
    # {
    #     "field": "CMV",
    #     "pattern": r"-\s*CMV\s*:\s*([^\n]+)",
    #     "group_index": 1,
    # },
    # {
    #     "field": "Elements_bacteriens",
    #     "pattern": r"-\s*Eléments\s+bactériens\s*:\s*([^\n]+)",
    #     "group_index": 1,
    # },

    # {
    # "field": "Commentaires",
    # "pattern": r"(?:^|\n)[\s\xa0]*Commentaires[\s\xa0]*:[\s\xa0]*([^\n]+)",
    # "group_index": 1,
    # }
    #-----------------------------------------------------------

]

COLUMN_ORDER = [
    "Filename",
    "IPP",
    "Biopsy ID",
    "Nom",
    "Prénom",
    "Date de naissance",
    "Sexe",
    "Date de prélèvement",
    "Prescripteur",
    "Modele_BTB",
    "Texte_libre_complet",
   #---------------------EXTRACTION LBA----------------------
    # "Macrophages",
    # "Lymphocytes",
    # "Polynucléaires neutrophiles",
    # "Polynucléaires éosinophiles",
    # "Autres éléments",
    # "Technique",
    # "Colorations",
    # "Volume",
    # "Aspect",
    # "Numération",
    # "Sidérophages",
    # #"Intensité",
    # "Score_Golde",
    # "Agents_pathogenes",
    # "Pneumocystis",
    # "Mycoses",
    # "Mycobacteries",
    # "CMV",
    # "Elements_bacteriens",
    # "Commentaires"
    #-----------------------------------------------------------


    #---------------------EXTRACTION BTB----------------------
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
    #-----------------------------------------------------------
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
    for col in df.select_dtypes(include=['object']).columns: 
        df[col] = df[col].apply(remove_illegal_chars)
    #df['Conclusion'] = df['Conclusion'].apply(sanitize_for_excel)

    filename = "BTB_structurated_txt"
    df.to_excel(f".././output/{filename}.xlsx", index=False)
    print(
        f"Extraction complete! You can see the result in the output folder named as '{filename}.xlsx'"
    )
