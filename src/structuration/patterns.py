"""Regex patterns for BTB document field extraction.

Each pattern dict has:
    field       -- column name in the output DataFrame
    pattern     -- regex pattern string
    group_index -- which capture group contains the value
"""

# -- Patient identification patterns ------------------------------------------
PATIENT_PATTERNS = [
    {
        "field": "Nom",
        "pattern": r"(?i)((?<!Pré)Nom\s*:\s*|Nom[\s+]*usuel\s*:\s*)(?:Mme\s+)?(([A-Z]+)([\s]*(?:\s*(Pr))?[A-Z]*))(?:\s*(Destinataire))?",
        "group_index": 3,
    },
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
    {
        "field": "Sexe",
        "pattern": r"Sexe\s*:\s*([MF])",
        "group_index": 1,
    },
    {
        "field": "Date de prélèvement",
        "pattern": r"(?i)(Prélevé[\s\xa0]*le[\s\xa0]*[\s\xa0]*:[\s\xa0\D]*)(\d{2}/\d{2}/\d{4})",
        "group_index": 2,
    },
    # Prescripteur is handled by extract_prescripteur() in extractors.py
    # to avoid catastrophic regex backtracking.
]

# -- BTB-specific histology patterns -------------------------------------------
BTB_PATTERNS = [
    {
        "field": "Site",
        "pattern": r"(Site[\s\xa0]*:)([\S]*[^\n]+)",
        "group_index": 2,
    },
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
        "pattern": r"(Fibro(?:-|\s*)?élastose[\s\xa0]*interstitielle [\s\xa0]*\([\s\xa0]*0[\s\xa0]*ou[\s\xa0]*1[\s\xa0]*\)[\s\xa0]*:*:[\s\xa0]*)([\w]*)",
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
        "field": "Matériel étranger d'inhalation",
        "pattern": r"(Matériel[\s\xa0]*étranger[\s\xa0]*d'inhalation[\s\xa0]*(\(oui\/non\)|)?[\s\xa0]*:*:[\s\xa0]*)([\S]*[^\n])",
        "group_index": 3,
    },
    {
        "field": "Conclusion",
        "pattern": r"((Conclusion|C[\s\xa0]O[\s\xa0]N[\s\xa0]C[\s\xa0]L[\s\xa0]U[\s\xa0]S[\s\xa0]I[\s\xa0]O[\s\xa0]N)[\s\xa0]*(:.*|))([\s\S]*)",
        "group_index": 4,
    },
]

# Combined list for the extraction pipeline
ALL_PATTERNS = PATIENT_PATTERNS + BTB_PATTERNS

# -- Column ordering for output Excel -----------------------------------------
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
    "Matériel étranger d'inhalation",
    "Conclusion",
]
