import pyodbc
import pandas as pd 

from lock_parameters import server, database, username, password

excel_file = "./ipp_list.xlsx" 
df = pd.read_excel(excel_file)

connection = pyodbc.connect(driver='{SQL Server}', host=server, port=1433, database=database,
                      trusted_connection='No', user=username, password=password)

cursor = connection.cursor()


filtered_identifiers = df[df['IPP'].astype(str).str.startswith('0')]['IPP'].tolist()

batch_size = 499
batches = [filtered_identifiers[i:i+batch_size] for i in range(0, len(filtered_identifiers), batch_size)]
formatted_batches = []
for batch in batches:
    formatted_batch = ", ".join(f"'{id}'" for id in batch)
    formatted_batches.append(f"(p.pat_ipp in ({formatted_batch}))")


result_string = " OR ".join(formatted_batches)


# Sample query
query = f"""select p.pat_ipp, d.doc_nom, d.doc_creation_date, d.doc_realisation_date, d.doc_stockage_id, fil_data
        from METADONE.metadone.DOCUMENTS d
        left join NOYAU.patient.PATIENT p on d.doc_pat_id = p.pat_id
         left join STOCKAGE.stockage.FILES f on f.fil_id = d.doc_stockage_id
            WHERE doc_nom LIKE '%Anapath%'
            and ({result_string})"""

print(query)
with connection.cursor() as cursor:
    cursor.execute(query)
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        if row[5] is not None:
            pat_ipp = row[0]  # Get pat_ipp
            doc_stockage_id = row[4]  # Get doc_stockage_id (original file name)
            fil_data = row[5]  # Get file data
            filename = f"..//..//./data//extract//{pat_ipp}_{doc_stockage_id}.pdf"
            with open(filename, 'wb') as newfile:
                newfile.write(fil_data)
# Closing cursor and connection
cursor.close()
connection.close()