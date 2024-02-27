import pyodbc
import pandas as pd 

from lock_parameters import server, database, username, password


connection = pyodbc.connect(driver='{SQL Server}', host=server, port=1433, database=database,
                      trusted_connection='No', user=username, password=password)

cursor = connection.cursor()
df = pd.read_excel("./ipp_list.xlsx")
ipp_list = df['IPP'].unique().tolist()  # Get unique IPPs
ipp_str = ','.join([f"'{ipp}'" for ipp in ipp_list])
print(ipp_str)
# Sample query
query = """select p.pat_ipp, d.doc_nom, d.doc_creation_date, d.doc_realisation_date, d.doc_stockage_id, fil_data
            from METADONE.metadone.DOCUMENTS d
                  left join NOYAU.patient.PATIENT p on d.doc_pat_id = p.pat_id
                  left join STOCKAGE.stockage.FILES f on f.fil_id = d.doc_stockage_id
            where doc_nom like '%Anapath%'
                  and p.pat_ipp in ({ipp_str})"""

# Executing the query
with connection.cursor() as cursor:
    cursor.execute(query)
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        if row[5] is not None:
            pat_ipp = row[0]  # Get pat_ipp
            doc_nom = row[1]  # Get doc_nom (original file name)
            fil_data = row[5]  # Get file data
            filename = f"../.././data/extract/{pat_ipp}_{doc_nom}.pdf"
            with open(filename, 'wb') as newfile:
                newfile.write(fil_data)
# Closing cursor and connection
cursor.close()
connection.close()