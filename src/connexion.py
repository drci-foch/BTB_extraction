import pyodbc

from lock_parameters import server, database, username, password


connection = pyodbc.connect(driver='{SQL Server}', host=server, port=1433, database=database,
                      trusted_connection='No', user=username, password=password)

cursor = connection.cursor()

# Sample query
query = """select p.pat_ipp, d.doc_nom, d.doc_creation_date, d.doc_realisation_date, d.doc_stockage_id, fil_data
            from METADONE.metadone.DOCUMENTS d
                  left join NOYAU.patient.PATIENT p on d.doc_pat_id = p.pat_id
                  left join STOCKAGE.stockage.FILES f on f.fil_id = d.doc_stockage_id
            where doc_nom like '%%'
                  and p.pat_ipp in ('0300758425')"""

# Executing the query
i=0
with connection.cursor() as cursor:
    cursor.execute(query)
    while True:
        i+=1
        row = cursor.fetchone()
        if row is None:
            break
        if (row[5] is not None):
            newfile = open('.././data/extract/'+str(i)+".pdf", 'wb')
            newfile.write(row[5])
            newfile.close()
# Closing cursor and connection
cursor.close()
connection.close()