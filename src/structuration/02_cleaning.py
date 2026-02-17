# TODO : Clean the data like what Natalia asked us to do (Word doc : Processing of BTB data.)
# Version modifiée selon le compte-rendu réunion Cleaning BTB

import pandas as pd
import re
from datetime import datetime

# Charger les données extraites
df = pd.read_excel(".././output/BTB_structurated_txt.xlsx")

# Charger les données LUTECE (transplants.csv) pour le NATT
transplants_df = pd.read_csv(
    "../extraction/transplants.csv", sep=";", encoding="latin-1"
)
# Renommer les colonnes pour faciliter la jointure
# NATT = numéro de transplantation, LT Date = date de transplantation
transplants_df = transplants_df.rename(
    columns={"NIP": "IPP_LUTECE", "LT Date": "LT_date"}
)

# ============================================================================
# 1. NETTOYAGE TEXTE LIBRE - Supprimer l'en-tête récurrent Hôpital Foch
# ============================================================================
ENTETE_HOPITAL_FOCH = (
    r"SERVICE D.ANATOMIE ET DE CYTOLOGIE PATHOLOGIQUES\s+"
    r"HOPITAL FOCH\s+"
    r"40 rue WORTH\s*-\s*BP 36\s*-\s*92151\s*-\s*SURESNES CEDEX\s+"
    r"[.\s]*:?\s*01[\s.]46[\s.]25[\s.]23[\s.]12\s+"
    r"Fax\s*:\s*01[\s.]46[\s.]25[\s.]26[\s.]45"
)

if "Texte_libre_complet" in df.columns:
    df["Texte_libre_complet"] = (
        df["Texte_libre_complet"]
        .astype(str)
        .str.replace(ENTETE_HOPITAL_FOCH, "", regex=True)
        .str.strip()
    )
    # Remettre les NaN pour les cellules qui étaient vides ou "nan"
    df.loc[
        df["Texte_libre_complet"].isin(["", "nan", "None"]), "Texte_libre_complet"
    ] = None
    print("Nettoyage en-tête Hôpital Foch effectué sur Texte_libre_complet")


# ============================================================================
# 2. DATE DE PRÉLÈVEMENT - Conversion en format date Excel
# ============================================================================
def convert_to_date(text):
    """Convertit une date string DD/MM/YYYY en format datetime pour Excel."""
    if pd.isna(text):
        return None
    text = str(text).strip()
    # Enlever l'heure si présente (ex: "02/07/2024 09:00:00")
    text = text.split()[0] if " " in text else text
    try:
        return pd.to_datetime(text, format="%d/%m/%Y")
    except (ValueError, TypeError):
        return None


df["Date de prélèvement"] = df["Date de prélèvement"].apply(convert_to_date)


# ============================================================================
# 3. NETTOYAGE DU NOM - Supprimer préfixe "Pr" et "Destinataire"
# ============================================================================
def clean_nom(text):
    """Nettoie le nom en supprimant le préfixe Pr et Destinataire."""
    if pd.isna(text):
        return None
    text = str(text)
    # Supprimer "Destinataire"
    text = text.replace("Destinataire", "")
    # Supprimer le préfixe "Pr" (avec ou sans espace après)
    text = re.sub(r"^Pr\s+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+Pr\s+", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+Pr$", "", text, flags=re.IGNORECASE)
    # Nettoyer les espaces multiples
    text = re.sub(r"\s+", " ", text).strip()
    return text


df["Nom"] = df["Nom"].apply(clean_nom)

# ============================================================================
# 4. SITE - Conserver brut, sans cleaning
# ============================================================================
# Ne rien faire sur la colonne Site - on garde les valeurs brutes extraites

# ============================================================================
# 5. VARIABLES - Garder uniquement la version extract (pas de transformation)
# ============================================================================
# Les colonnes suivantes sont gardées telles quelles (extraites brutes):
# - Infiltrat
# - Bronchiolite Lymphocytaire
# - Technique
# - Niveaux de coupes
# - Nombre de fragment alvéolaire
# - Bronches/Bronchioles
# - Inflammation Lymphocytaire
# - Bronchiolite oblitérante
# - Fibro-élastose interstitielle
# - PNN dans les cloisons alvéolaires
# - Cellules mononucléées
# - Dilatation des capillaires alvéolaires
# - Œdème des cloisons alvéolaires
# - Thrombi fibrineux dans les capillaires alvéolaires
# - Débris cellulaires dans les cloisons alvéolaires
# - Epaississement fibreux des cloisons alvéolaires
# - Hyperplasie pneumocytaire
# - PNN dans les espaces alvéolaires
# - Macrophages dans les espaces alvéolaires
# - Bourgeons conjonctifs dans les espaces alvéolaires
# - Hématies dans les espaces alvéolaires
# - Membranes hyalines
# - Fibrine dans les espaces alvéolaires
# - Inflammation sous-pleurale, septale, bronchique ou bronchiolaire
# - BALT
# - Thrombus fibrino-cruorique
# - Nécrose ischémique
# - Inclusions virales
# - Agent pathogène
# - Eosinophilie (interstitielle/alvéolaire)
# - Remodelage vasculaire
# - Matériel étranger d'inhalation

# ============================================================================
# 6. GESTION DES DOUBLONS - Garder l'enregistrement le plus récent par Biopsy ID
# ============================================================================
# Trier par Biopsy ID et Date de prélèvement (décroissant) pour garder le plus récent
df_sorted = df.sort_values(
    by=["Biopsy ID", "Date de prélèvement"], ascending=[True, False]
)
# Supprimer les doublons en gardant le premier (le plus récent)
df = df_sorted.drop_duplicates(subset=["Biopsy ID"], keep="first")
print(f"Nombre d'enregistrements après suppression des doublons: {len(df)}")

# ============================================================================
# 7. AJOUTER NATT DEPUIS LUTECE (transplants.csv)
# ============================================================================
# Préparer l'IPP pour la jointure (ajouter le 0 au début si nécessaire)
df["IPP"] = df["IPP"].astype(str).str.zfill(9)
transplants_df["IPP_LUTECE"] = transplants_df["IPP_LUTECE"].astype(str).str.zfill(9)

# Convertir LT_date en datetime
transplants_df["LT_date"] = pd.to_datetime(
    transplants_df["LT_date"], format="%Y-%m-%d", errors="coerce"
)

# Un patient peut avoir plusieurs transplantations (double transplantation).
# Pour chaque biopsie, on associe la transplantation la plus récente
# dont la date (LT_date) est <= à la date de prélèvement de la biopsie.
# Exemple: Patient avec LT_date1=2020-01-15 et LT_date2=2023-06-01
#          Biopsie du 2024-03-10 → on associe LT_date2 (2023-06-01) et son NATT


def find_matching_transplant(row, transplants):
    """Pour une biopsie, trouve la transplantation la plus récente antérieure au prélèvement.
    Retourne un tuple (NATT, LT_date) correspondant à la bonne transplantation."""
    ipp = row["IPP"]
    date_prelev = row["Date de prélèvement"]

    # Récupérer toutes les transplantations de ce patient
    patient_transplants = transplants[transplants["IPP_LUTECE"] == ipp]

    if patient_transplants.empty:
        return pd.Series({"NATT": None, "LT_date": None})

    if pd.isna(date_prelev):
        # Pas de date de prélèvement : on ne peut pas déterminer la bonne transplantation
        return pd.Series({"NATT": None, "LT_date": None})

    # Filtrer les transplantations antérieures ou égales à la date de prélèvement
    valid_transplants = patient_transplants[
        patient_transplants["LT_date"] <= date_prelev
    ]

    if valid_transplants.empty:
        # Aucune transplantation antérieure au prélèvement → alerte
        # On retourne la plus ancienne pour investigation
        earliest = patient_transplants.loc[patient_transplants["LT_date"].idxmin()]
        return pd.Series({"NATT": earliest["NATT"], "LT_date": earliest["LT_date"]})

    # Retourner la transplantation la plus récente parmi celles antérieures
    best = valid_transplants.loc[valid_transplants["LT_date"].idxmax()]
    return pd.Series({"NATT": best["NATT"], "LT_date": best["LT_date"]})


df[["NATT", "LT_date"]] = df.apply(
    find_matching_transplant, axis=1, transplants=transplants_df
)

print(f"Nombre de biopsies avec transplantation associée: {df['NATT'].notna().sum()}")


# ============================================================================
# 8. VÉRIFICATION DATE PRÉLÈVEMENT > LT_date
# ============================================================================
def check_date_after_lt(row):
    """Vérifie si la date de prélèvement est postérieure à la date de transplantation."""
    date_prelev = row["Date de prélèvement"]
    lt_date = row["LT_date"]

    if pd.isna(date_prelev) or pd.isna(lt_date):
        return None  # Pas de vérification possible

    if date_prelev >= lt_date:
        return "OK"
    else:
        return "ALERTE: Date prélèvement < LT_date"


df["Verif_Date_LT"] = df.apply(check_date_after_lt, axis=1)

# ============================================================================
# 9. VÉRIFICATION PATIENTS LUTECE
# ============================================================================
# Liste des patients LUTECE (tous les NIP du fichier transplants.csv)
patients_lutece = set(transplants_df["IPP_LUTECE"].astype(str).str.zfill(9).unique())
patients_btb = set(df["IPP"].unique())

# Vérifier si chaque patient BTB est dans LUTECE
df["Patient_dans_LUTECE"] = df["IPP"].apply(
    lambda x: "Oui" if x in patients_lutece else "Non"
)

# Identifier les patients LUTECE non présents dans BTB
patients_lutece_manquants = patients_lutece - patients_btb
print(f"Patients LUTECE non trouvés dans BTB: {len(patients_lutece_manquants)}")

# ============================================================================
# 10. VÉRIFICATION DU NOMBRE DE BIOPSIES PAR PATIENT (9 attendues)
# ============================================================================
biopsies_par_patient = df.groupby("IPP").size().reset_index(name="Nb_Biopsies")
df = df.merge(biopsies_par_patient, on="IPP", how="left")


def check_biopsies_count(nb_biopsies):
    """Vérifie si le patient a le bon nombre de biopsies (9 attendues)."""
    if pd.isna(nb_biopsies):
        return None
    nb = int(nb_biopsies)
    if nb >= 9:
        return "OK"
    else:
        return f"ALERTE: {nb} biopsies (< 9 attendues)"


df["Verif_Nb_Biopsies"] = df["Nb_Biopsies"].apply(check_biopsies_count)


# ============================================================================
# 11. COLONNES DE VÉRIFICATION RÉCAPITULATIVES
# ============================================================================
# Créer une colonne récapitulative des alertes
def recap_verifications(row):
    """Récapitule toutes les vérifications pour faciliter le filtrage."""
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


df["Alertes_Recap"] = df.apply(recap_verifications, axis=1)

# ============================================================================
# EXPORT
# ============================================================================
# S'assurer que les dates sont bien formatées pour Excel
df.to_excel("../output/BTB_structurated_cleaned.xlsx", index=False)

print("Export terminé: BTB_structurated_cleaned.xlsx")
print(f"Nombre total d'enregistrements: {len(df)}")
print(f"Nombre d'alertes: {len(df[df['Alertes_Recap'] != 'OK'])}")
