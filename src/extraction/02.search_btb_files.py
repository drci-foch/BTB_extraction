import os
import re
import shutil
import fitz
from tqdm import tqdm


def normalize_text(text):
    """
    Normalise le texte pour gérer les artefacts de conversion HTML→TXT :
    - Supprime les espaces multiples/insérés dans les mots
    - Supprime les accents
    - Met en majuscule
    """
    text = text.upper()
    # Supprimer tous les espaces, retours à la ligne, tabs
    text_no_spaces = re.sub(r"\s+", "", text)
    return text_no_spaces


def build_flexible_pattern(keyword):
    """
    Construit un regex qui tolère des espaces/retours à la ligne
    entre chaque caractère du mot-clé.
    Ex: "BTB" → r"B\s*T\s*B"
    """
    keyword_upper = keyword.upper().strip()
    # Insérer \s* entre chaque caractère
    chars = list(keyword_upper)
    pattern = r"\s*".join(re.escape(c) for c in chars)
    return re.compile(pattern, re.IGNORECASE)


# Mots-clés avec variantes (fautes de frappe, abréviations, singulier/pluriel)
INCLUSION_KEYWORDS = [
    "BIOPSIES TRANSBRONCHIQUES",
    "BIOPSIE TRANSBRONCHIQUE",
    "BIOPSIES TRANS BRONCHIQUES",
    "BIOPSIE TRANS BRONCHIQUE",
    "BIOSPIE TRANSBRONCHIQUE",  # typo connue
    "BIOPSIE TRANS-BRONCHIQUE",
    "BIOPSIES TRANS-BRONCHIQUES",
]

EXCLUSION_KEYWORDS = [
    "ANNULÉ",
    "ANNULE",
]

# Pré-compiler les regex flexibles
INCLUSION_PATTERNS = [build_flexible_pattern(kw) for kw in INCLUSION_KEYWORDS]
EXCLUSION_PATTERNS = [build_flexible_pattern(kw) for kw in EXCLUSION_KEYWORDS]


def check_keywords_flexible(text):
    """Vérifie les mots-clés avec double stratégie : regex flexible + texte sans espaces."""
    text_upper = text.upper()
    text_no_spaces = normalize_text(text)

    # Stratégie 1 : regex flexible (tolère espaces insérés)
    has_inclusion = any(p.search(text_upper) for p in INCLUSION_PATTERNS)

    # Stratégie 2 : fallback sur texte sans espace (attrape les cas extrêmes)
    if not has_inclusion:
        keywords_no_spaces = [
            re.sub(r"\s+", "", kw.upper()) for kw in INCLUSION_KEYWORDS
        ]
        has_inclusion = any(kw in text_no_spaces for kw in keywords_no_spaces)

    has_exclusion = any(p.search(text_upper) for p in EXCLUSION_PATTERNS)
    if not has_exclusion:
        excl_no_spaces = [re.sub(r"\s+", "", kw.upper()) for kw in EXCLUSION_KEYWORDS]
        has_exclusion = any(kw in text_no_spaces for kw in excl_no_spaces)

    return has_inclusion, has_exclusion


def check_file(filepath):
    """Lit et vérifie un fichier PDF ou TXT."""
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == ".pdf":
            doc = fitz.open(filepath)
            text = "\n".join(page.get_text() for page in doc)
            doc.close()
        elif ext == ".txt":
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        else:
            return False, False, f"unsupported: {ext}"

        has_incl, has_excl = check_keywords_flexible(text)
        return has_incl, has_excl, None

    except Exception as e:
        return False, False, str(e)


def collect_files(folder_path, extensions=(".pdf", ".txt")):
    all_files = []
    for root, dirs, files in os.walk(folder_path):
        for f in files:
            if f.lower().endswith(extensions):
                all_files.append(os.path.join(root, f))
    return sorted(all_files)


def filter_and_copy(folder_path, destination_folder):
    os.makedirs(destination_folder, exist_ok=True)

    all_files = collect_files(folder_path)
    print(f"📂 {len(all_files)} fichiers trouvés (récursif)")

    error_log_path = os.path.join(destination_folder, "error_documents.txt")
    saved = 0
    errors = 0

    with open(error_log_path, "w") as error_log:
        for filepath in tqdm(all_files, desc="🔍 Filtrage"):
            has_incl, has_excl, error = check_file(filepath)
            if error:
                error_log.write(f"{filepath} | {error}\n")
                errors += 1
                continue
            if has_incl and not has_excl:
                shutil.copy(filepath, destination_folder)
                saved += 1

    print(f"\n✅ {saved} fichiers copiés, ❌ {errors} erreurs")
    print(f"📁 Destination : {os.path.abspath(destination_folder)}")


folder_path = (
    r"C:\Users\benysar\Documents\GitHub\BTB_extraction\data\EDS_archemed_extract"
)
destination_folder = r"C:\Users\benysar\Documents\GitHub\BTB_extraction\data\extract_filtrer_btb_archemed"

filter_and_copy(folder_path, destination_folder)
