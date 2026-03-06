"""Shared text extraction functions for BTB/LBA documents."""

import logging
import re
from datetime import datetime

import chardet

log = logging.getLogger(__name__)


def read_text_file(file_path: str) -> str:
    """Read a text file with encoding auto-detection via chardet."""
    with open(file_path, "rb") as f:
        raw_data = f.read()

    # Only feed the first 10 KB to chardet – enough for reliable detection
    # and avoids very slow analysis on large files.
    detected = chardet.detect(raw_data[:10_000])
    encoding = detected.get("encoding") or "utf-8"

    try:
        return raw_data.decode(encoding)
    except (UnicodeDecodeError, LookupError):
        pass

    for fallback in ("iso-8859-1", "utf-8", "latin-1", "cp1252"):
        try:
            return raw_data.decode(fallback)
        except (UnicodeDecodeError, LookupError):
            continue

    return raw_data.decode("utf-8", errors="replace")


def extract_prescripteur(text: str) -> str | None:
    """Extract the prescriber (Docteur) name from text.

    Looks for "Docteur <NAME>" followed on the same or next lines by one of:
      - ", Compte-rendu"
      - "ADICAP"
      - a date dd/mm/yyyy
    Uses a two-step approach to avoid catastrophic regex backtracking.
    """
    for m in re.finditer(r"Docteur\s+([^\n]{1,120})", text):
        name = m.group(1).strip()
        # Check the text immediately after the match (same line + next lines)
        after = text[m.end():m.end() + 200]
        if (re.match(r"\s*,\s*Compte-rendu", after)
                or re.match(r"\s*\n\s*ADICAP", after)
                or re.match(r"\s*\n[\s\S]{0,40}\d{2}/\d{2}/\d{4}", after)):
            # Strip trailing whitespace/punctuation from name
            name = re.sub(r"[\s\.\-]+$", "", name)
            return name
    return None


def extract_prenom_before_docteur(text: str) -> str | None:
    """Extract the first name from the 'Prenom:' field."""
    pattern = r"Prénom\s*:\s*([A-Z\s]+)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        before_docteur = match.group(1)
        first_name = before_docteur.split()[0] if before_docteur else None
        return first_name
    return None


def extract_technique(text: str, option: str = "lba") -> str | None:
    """Extract the medical technique (BTB or LBA) from text with multi-level fallback."""
    if option.lower() == "btb":
        technique_pattern = r"(2\.|II\.|I\.|2/|2°/)[\s+]*(Biopsies\s+trans[ -]*bronchiques|Biopsies\s+transbronchiques|Biospies\s+transbronchiques|BTB)(?:(?!LAVAGE)[\s\S]){0,3000}?Technique[^\S\r\n]*:[^\S\r\n]*([^;]+)"
        fallback_technique_pattern = r"(Biopsies\s+trans[ -]*bronchiques|Biopsies\s+transbronchiques|Biospies\s+transbronchiques|BTB)(?:(?!LAVAGE)[\s\S]){0,3000}?Technique\s*:\s*([^;]+)"
        fallback_technique_mention = "HES"
    elif option.lower() == "lba":
        technique_pattern = r"(1\.|I\.|I\.|1/|1°/)[\s+]*(Lavage\s+bronchoalvéolaire|Lavage\s+broncho-alvéolaire|LBA)(?:(?!BIOPSIE)[\s\S]){0,3000}?Technique[^\S\r\n]*:[^\S\r\n]*([^;]+)"
        fallback_technique_pattern = r"(Lavage\s+bronchoalvéolaire|Lavage\s+broncho-alvéolaire|LBA)(?:(?!BIOPSIE)[\s\S]){0,3000}?Technique\s*:\s*([^;]+)"
        fallback_technique_mention = "cytocentrifugation"
    else:
        raise ValueError("Invalid option. Choose 'btb' or 'lba'.")

    technique_match = re.search(technique_pattern, text, re.DOTALL | re.IGNORECASE)
    if technique_match:
        return technique_match.group(3).strip()

    fallback_match = re.search(
        fallback_technique_pattern, text, re.DOTALL | re.IGNORECASE
    )
    if fallback_match:
        return fallback_match.group(2).strip()

    if fallback_technique_mention.lower() in text.lower():
        return fallback_technique_mention

    technique_search_pattern = r"Technique\s*:\s*([^;]+)"
    technique_matches = re.findall(
        technique_search_pattern, text, re.IGNORECASE | re.DOTALL
    )
    if technique_matches:
        return technique_matches[0].strip()

    last_fallback_pattern = r"Technique\s*:\s*([^;]+)"
    last_fallback_match = re.search(last_fallback_pattern, text, re.DOTALL)
    if last_fallback_match:
        return last_fallback_match.group(1).strip()

    return None


def extract_niveaux_coupes(text: str) -> str | None:
    """Extract the levels of cuts (niveaux de coupes) with multi-level fallback."""
    # Direct: "X niveaux de coupes" after "Technique : HES ;"
    direct_pattern = r"Technique\s*:\s*HES\s*;\s*(\d+)\s*niveaux?\s*de\s*coupes?"
    direct_match = re.search(direct_pattern, text, re.IGNORECASE)
    if direct_match:
        return direct_match.group(1).strip()

    # Alt: "X niveaux de coupes" anywhere
    alt_pattern = r"(\d+)\s*niveaux?\s*de\s*coupes?"
    alt_match = re.search(alt_pattern, text, re.IGNORECASE)
    if alt_match:
        return alt_match.group(1).strip()

    # Numbered section pattern
    pattern = r"(2\.|II\.|I\.|2/|2°/)[\s+]*(Biopsies\s+trans[ -]*bronchiques|Biopsies\s+transbronchiques|Biospies\s+transbronchiques|BTB)[\s\S]{0,3000}?Technique\s*:\s*([^;]+);\s*([^n]+)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(4).strip()

    # Unnumbered section fallback
    fallback_pattern = r"(Biopsies\s+trans[ -]*bronchiques|Biopsies\s+transbronchiques|Biospies\s+transbronchiques|BTB)(?:(?!LAVAGE)[\s\S]){0,3000}?Technique\s*:\s*([^;]+);\s*([^n]+)"
    fallback_match = re.search(fallback_pattern, text, re.DOTALL)
    if fallback_match:
        return fallback_match.group(3).strip()

    if "HES" in text:
        return None

    # Split by "Technique:" sections
    parts = re.split(r"(?=Technique\s*:)", text, flags=re.IGNORECASE)
    if len(parts) > 2:
        two_parts_pattern = r"Technique\s*:\s*([^;]+);\s*([^n]+)"
        two_parts_match = re.search(two_parts_pattern, parts[-1], re.DOTALL)
        if two_parts_match:
            return two_parts_match.group(2).strip()

    # Last fallback
    last_pattern = r"Technique\s*:\s*([^;]+);\s*([^n]+)"
    last_match = re.search(last_pattern, text, re.DOTALL)
    if last_match:
        return last_match.group(2).strip()

    return None


def detect_modele_btb(text: str, date_prelevement: str | None = None) -> str:
    """Detect whether a BTB document is free-text or semi-structured."""
    if date_prelevement:
        try:
            if isinstance(date_prelevement, str):
                date_obj = datetime.strptime(date_prelevement, "%d/%m/%Y")
                if date_obj.year < 2011:
                    return "texte_libre"
        except (ValueError, TypeError):
            pass

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

    structured_count = sum(
        1 for p in structured_patterns if re.search(p, text, re.IGNORECASE)
    )

    if structured_count >= 3:
        return "semi_structure"
    return "texte_libre"


def extract_texte_libre_complet(text: str, modele_btb: str) -> str | None:
    """Return the full text if the document is free-text, None otherwise."""
    if modele_btb == "texte_libre":
        cleaned_text = re.sub(r"[ \t]+", " ", text)
        cleaned_text = re.sub(r"\n\s*\n", "\n\n", cleaned_text)
        return cleaned_text.strip()
    return None


def extract_information(text: str, patterns: list[dict]) -> dict:
    """Extract information from text based on a list of regex pattern definitions."""
    results = {}
    for item in patterns:
        field = item["field"]
        pattern = item["pattern"]
        group_index = item.get("group_index")

        try:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                if field == "Nom" and len(match.groups()) >= 4:
                    part3 = match.group(3) or ""
                    part4 = match.group(4) or ""
                    results[field] = (part3 + part4).strip()
                else:
                    if group_index and group_index <= len(match.groups()):
                        results[field] = match.group(group_index).strip()
                    else:
                        results[field] = None
            else:
                results[field] = None
        except (re.error, IndexError) as e:
            log.warning("Pattern error for field '%s': %s", field, e)
            results[field] = None

    return results


def remove_illegal_chars(s):
    """Remove Excel-illegal control characters from a string."""
    if isinstance(s, str):
        return re.sub(r"[\x00-\x1F\x7F]", "", s)
    return s
