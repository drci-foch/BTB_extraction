import os
import psycopg2
from tqdm import tqdm
from bs4 import BeautifulSoup

from lock_parameters import username_pg, password_pg, hostname_pg, port_pg, database_pg

connection_string = {
    "host": hostname_pg,
    "port": port_pg,
    "database": database_pg,
    "user": username_pg,
    "password": password_pg,
}

base_path = (
    r"C:\Users\benysar\Documents\GitHub\BTB_extraction\data\EDS_archemed_extract"
)
os.makedirs(base_path, exist_ok=True)

# DISTINCT ON pour éviter les doublons du JOIN IPP
query = """
SELECT DISTINCT ON (d.patient_num, d.document_origin_code)
    d.patient_num,
    p.hospital_patient_id,
    d.document_origin_code,
    d.title,
    d.document_date,
    d.displayed_text
FROM dwh.dwh_document d  
JOIN dwh.dwh_patient_ipphist p ON d.patient_num = p.patient_num
WHERE d.document_type = 'EXT' 
AND d.title LIKE '%%Anapath%%'
"""


def html_to_text(html_content):
    """Extrait le texte brut depuis le HTML."""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator="\n", strip=True)


# 1. Connexion
print(f"🔌 Connexion à PostgreSQL ({hostname_pg}:{port_pg}/{database_pg})...")
conn = psycopg2.connect(**connection_string)
print("✅ Connexion réussie")

cursor = conn.cursor()

# 2. Exécution
print("🔍 Exécution de la requête...")
cursor.execute(query)
print("✅ Requête exécutée")

# 3. Résultats
print("📊 Récupération des résultats...")
rows = cursor.fetchall()
print(f"✅ {len(rows)} documents trouvés")

# 4. Sauvegarde
saved = 0
skipped = 0

for row in tqdm(rows, desc="📥 Extraction textes"):
    patient_num = row[0]
    hospital_ipp = str(row[1])
    origin_code = str(row[2])
    title = row[3]
    document_date = row[4]
    displayed_text = row[5]

    if displayed_text:
        # Extraire le texte propre du HTML
        clean_text = html_to_text(displayed_text)

        patient_folder = os.path.join(base_path, hospital_ipp)
        os.makedirs(patient_folder, exist_ok=True)

        date_str = document_date.strftime("%Y%m%d") if document_date else "nodate"
        filename = os.path.join(
            patient_folder, f"{hospital_ipp}_{date_str}_{origin_code}.txt"
        )

        with open(filename, "w", encoding="utf-8") as f:
            f.write(clean_text)
        saved += 1
    else:
        skipped += 1

cursor.close()
conn.close()

print(f"\n✅ Terminé : {saved} fichiers sauvegardés, {skipped} ignorés (texte vide)")
print(f"📁 Dossier : {base_path}")
