# BTB Extraction - Transbronchial Biopsy Document Extractor

Pipeline d'extraction et de structuration automatique de comptes-rendus de biopsies transbronchiques (BTB) depuis les bases de donnees hospitalieres.

## Architecture

```
src/
  config.py                  # Configuration centralisee (chemins, credentials)
  extraction/
    db_easily.py             # Extraction SQL Server (Easily/METADONE)
    db_archemed.py           # Extraction PostgreSQL (EDS - ARCHEMED)
    filter_btb.py            # Filtrage documents BTB par mots-cles
    pdf_to_text.py           # Conversion PDF -> TXT (JAR Java)
  structuration/
    patterns.py              # 38 patterns regex pour l'extraction BTB
    extractors.py            # Fonctions partagees d'extraction de texte
    extract_btb.py           # Extraction des champs BTB depuis les fichiers .txt
    clean_btb.py             # Nettoyage, deduplication, merge LUTECE
    clean_lba.py             # Nettoyage LBA (Lavage Bronchoalveolaire)
    verify.py                # Rapport qualite des donnees
  output/                    # Fichiers Excel generes
run_pipeline.py              # Point d'entree unique
```

## Installation

```bash
git clone https://github.com/drci-foch/BTB_extraction.git
cd BTB_extraction
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

Copier le fichier de configuration et renseigner les credentials :

```bash
cp .env.example .env
# Editer .env avec les identifiants de connexion aux bases
```

## Usage

### Lancer le pipeline standard

```bash
python run_pipeline.py --all
```

Cela execute dans l'ordre : `extract_easily`  -> `filter` ->  `pdf_to_text` -> `extract_btb` -> `clean`.

Les dossiers manquants sont crees automatiquement.

### Extraction ARCHEMED (one-shot)

L'extraction depuis l'EDS pour récupérer les BTB d'ARCHMEMED n'est pas incluse dans `--all` car elle ne doit etre lancee qu'une seule fois. Pour l'executer :

```bash
python run_pipeline.py --steps extract_archemed
```

### Lancer des etapes specifiques

```bash
python run_pipeline.py --steps extract_btb clean verify
```

### Lister les etapes disponibles

```bash
python run_pipeline.py --list
```

**Etapes `--all` (pipeline standard) :**

| Etape | Description |
|-------|-------------|
| `extract_easily` | Extraction depuis la BDD Easily (SQL Server) |
| `pdf_to_text` | Conversion PDF vers TXT via JAR Java |
| `filter` | Filtrage des documents contenant des BTB |
| `extract_btb` | Extraction regex des 38 champs medicaux |
| `clean` | Nettoyage, deduplication, merge avec LUTECE |
| `clean_lba` | Nettoyage des donnees LBA |
| `verify` | Generation du rapport qualite (BTB_summary.xlsx) |

**Etapes supplementaires (sur demande) :**

| Etape | Description |
|-------|-------------|
| `extract_archemed` | Extraction depuis la BDD ARCHEMED (PostgreSQL) |

### Lancer un script individuellement

```bash
python -m src.structuration.extract_btb <dossier_txt>
python -m src.structuration.clean_btb
python -m src.structuration.verify
```

## Configuration

Les credentials de base de donnees et les chemins sont geres via :

- **`.env`** : variables d'environnement (non commite, voir `.env.example`)
- **`src/config.py`** : chemins resolus relativement a la racine du projet

## Donnees extraites

Le pipeline extrait 38+ champs depuis les comptes-rendus BTB :

- **Identification** : IPP, Nom, Prenom, Date de naissance, Sexe
- **Prelevement** : Date, Prescripteur, Technique, Site, Niveaux de coupes
- **Histologie** : Infiltrat, Bronchiolite, Inflammation, Fibrose, PNN, etc.
- **Validation** : Alertes dates, verification LUTECE, comptage biopsies

## Fichiers de sortie

| Fichier | Description |
|---------|-------------|
| `BTB_structurated_txt.xlsx` | Extraction brute des champs |
| `BTB_structurated_cleaned.xlsx` | Donnees nettoyees avec alertes |
| `LBA_structurated_cleaned.xlsx` | Donnees LBA nettoyees |
| `BTB_summary.xlsx` | Rapport qualite (valeurs uniques, NA par annee) |

## Pre-requis

- Python 3.11+
- Java JDK 21+ (pour la conversion PDF)
- Acces reseau aux bases hospitalieres (pour les etapes `extract_easily` / `extract_archemed`)
