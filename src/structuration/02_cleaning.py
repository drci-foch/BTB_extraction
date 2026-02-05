#TODO : Clean the data like what Natalia asked us to do (Word doc : Processing of BTB data.)
# Version modifiée selon le compte-rendu réunion Cleaning BTB

import pandas as pd
import re
from datetime import datetime

# Charger les données extraites
df = pd.read_excel(".././output/BTB_structurated_txt.xlsx")

# Charger les données LUTECE (transplants.csv) pour le NATT
transplants_df = pd.read_csv("../extraction/transplants.csv", sep=";")
# Renommer les colonnes pour faciliter la jointure
transplants_df = transplants_df.rename(columns={"NIP": "IPP_LUTECE", "LT Date": "NATT"})

# ============================================================================
# 1. DATE DE PRÉLÈVEMENT - Conversion en format date Excel
# ============================================================================
def convert_to_date(text):
    """Convertit une date string DD/MM/YYYY en format datetime pour Excel."""
    if pd.isna(text):
        return None
    text = str(text).strip()
    # Enlever l'heure si présente (ex: "02/07/2024 09:00:00")
    text = text.split()[0] if ' ' in text else text
    try:
        return pd.to_datetime(text, format="%d/%m/%Y")
    except (ValueError, TypeError):
        return None

df['Date de prélèvement'] = df['Date de prélèvement'].apply(convert_to_date)

# ============================================================================
# 2. NETTOYAGE DU NOM - Supprimer préfixe "Pr" et "Destinataire"
# ============================================================================
def clean_nom(text):
    """Nettoie le nom en supprimant le préfixe Pr et Destinataire."""
    if pd.isna(text):
        return None
    text = str(text)
    # Supprimer "Destinataire"
    text = text.replace("Destinataire", "")
    # Supprimer le préfixe "Pr" (avec ou sans espace après)
    text = re.sub(r'^Pr\s+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+Pr\s+', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+Pr$', '', text, flags=re.IGNORECASE)
    # Nettoyer les espaces multiples
    text = re.sub(r'\s+', ' ', text).strip()
    return text

df['Nom'] = df['Nom'].apply(clean_nom)

# ============================================================================
# 3. SITE - Conserver brut, sans cleaning
# ============================================================================
# Ne rien faire sur la colonne Site - on garde les valeurs brutes extraites

# ============================================================================
# 4. VARIABLES - Garder uniquement la version extract (pas de transformation)
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
# 5. GESTION DES DOUBLONS - Garder l'enregistrement le plus récent par Biopsy ID
# ============================================================================
# Trier par Biopsy ID et Date de prélèvement (décroissant) pour garder le plus récent
df_sorted = df.sort_values(by=['Biopsy ID', 'Date de prélèvement'], ascending=[True, False])
# Supprimer les doublons en gardant le premier (le plus récent)
df = df_sorted.drop_duplicates(subset=['Biopsy ID'], keep='first')
print(f"Nombre d'enregistrements après suppression des doublons: {len(df)}")

# ============================================================================
# 6. AJOUTER NATT DEPUIS LUTECE (transplants.csv)
# ============================================================================
# Préparer l'IPP pour la jointure (ajouter le 0 au début si nécessaire)
df['IPP'] = df['IPP'].astype(str).str.zfill(9)
transplants_df['IPP_LUTECE'] = transplants_df['IPP_LUTECE'].astype(str).str.zfill(9)

# Convertir NATT en datetime
transplants_df['NATT'] = pd.to_datetime(transplants_df['NATT'], format="%Y-%m-%d", errors='coerce')

# Un patient peut avoir plusieurs NATT (double transplantation)
# Joindre sur IPP
df = df.merge(
    transplants_df[['IPP_LUTECE', 'NATT']].drop_duplicates(),
    left_on='IPP',
    right_on='IPP_LUTECE',
    how='left'
)
df = df.drop(columns=['IPP_LUTECE'], errors='ignore')

# ============================================================================
# 7. VÉRIFICATION DATE PRÉLÈVEMENT > NATT
# ============================================================================
def check_date_after_natt(row):
    """Vérifie si la date de prélèvement est postérieure au NATT."""
    date_prelev = row['Date de prélèvement']
    natt = row['NATT']

    if pd.isna(date_prelev) or pd.isna(natt):
        return None  # Pas de vérification possible

    if date_prelev > natt:
        return "OK"
    else:
        return "ALERTE: Date prélèvement <= NATT"

df['Verif_Date_NATT'] = df.apply(check_date_after_natt, axis=1)

# ============================================================================
# 8. VÉRIFICATION PATIENTS LUTECE
# ============================================================================
# Liste des patients LUTECE (tous les NIP du fichier transplants.csv)
patients_lutece = set(transplants_df['IPP_LUTECE'].astype(str).str.zfill(9).unique())
patients_btb = set(df['IPP'].unique())

# Vérifier si chaque patient BTB est dans LUTECE
df['Patient_dans_LUTECE'] = df['IPP'].apply(lambda x: "Oui" if x in patients_lutece else "Non")

# Identifier les patients LUTECE non présents dans BTB
patients_lutece_manquants = patients_lutece - patients_btb
print(f"Patients LUTECE non trouvés dans BTB: {len(patients_lutece_manquants)}")

# ============================================================================
# 9. VÉRIFICATION DU NOMBRE DE BIOPSIES PAR PATIENT (9 attendues)
# ============================================================================
biopsies_par_patient = df.groupby('IPP').size().reset_index(name='Nb_Biopsies')
df = df.merge(biopsies_par_patient, on='IPP', how='left')

def check_biopsies_count(nb_biopsies):
    """Vérifie si le patient a le bon nombre de biopsies (9 attendues)."""
    if pd.isna(nb_biopsies):
        return None
    nb = int(nb_biopsies)
    if nb >= 9:
        return "OK"
    else:
        return f"ALERTE: {nb} biopsies (< 9 attendues)"

df['Verif_Nb_Biopsies'] = df['Nb_Biopsies'].apply(check_biopsies_count)

# ============================================================================
# 10. COLONNES DE VÉRIFICATION RÉCAPITULATIVES
# ============================================================================
# Créer une colonne récapitulative des alertes
def recap_verifications(row):
    """Récapitule toutes les vérifications pour faciliter le filtrage."""
    alertes = []

    if row.get('Verif_Date_NATT') and "ALERTE" in str(row.get('Verif_Date_NATT', '')):
        alertes.append("Date/NATT")

    if row.get('Patient_dans_LUTECE') == "Non":
        alertes.append("Patient non LUTECE")

    if row.get('Verif_Nb_Biopsies') and "ALERTE" in str(row.get('Verif_Nb_Biopsies', '')):
        alertes.append("Nb biopsies")

    return "; ".join(alertes) if alertes else "OK"

df['Alertes_Recap'] = df.apply(recap_verifications, axis=1)

# ============================================================================
# EXPORT
# ============================================================================
# S'assurer que les dates sont bien formatées pour Excel
df.to_excel('../output/BTB_structurated_cleaned.xlsx', index=False)

print("Export terminé: BTB_structurated_cleaned.xlsx")
print(f"Nombre total d'enregistrements: {len(df)}")
print(f"Nombre d'alertes: {len(df[df['Alertes_Recap'] != 'OK'])}")
