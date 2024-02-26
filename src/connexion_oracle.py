import oracledb
import os

dsn = oracledb.makedsn('srvapp522', '1521', service_name='dwh')
conn = oracledb.connect(user='drci002', password='Gbu!459deux3', dsn=dsn)

output_dir = './data/extracted_files'
os.makedirs(output_dir, exist_ok=True)

# SQL to select the BLOBs
sql = "SELECT blob_column, file_name, file_type_column FROM your_table_name"

with conn.cursor() as cursor:
    cursor.execute(sql)
    
    for blob_content, file_name, file_type in cursor:
        file_path = os.path.join(output_dir, file_name)
        
        with open(file_path, 'wb') as file_output:
            blob_data = blob_content.read()  
            file_output.write(blob_data)  

        print(f"File saved: {file_path}")

conn.close()
print("All files have been extracted.")


