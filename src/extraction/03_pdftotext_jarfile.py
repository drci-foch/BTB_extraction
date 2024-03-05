import os
import subprocess
import shutil

java_path = "../../jdk-17.0.10/bin/java.exe"
jar_path = "./pdftotext-jar-with-dependencies.jar"
folder_path = "../../data/extract_easily_btb/"
output_txt_dir = "../../data/txt"

os.makedirs(output_txt_dir, exist_ok=True)

for file_name in os.listdir(folder_path):
    if file_name.endswith(".pdf"):
        file_path = os.path.join(folder_path, file_name)
        print(file_path)
        command = [java_path, "-jar", jar_path, file_path]
        
        subprocess.run(command)
    
        txt_file_name = os.path.splitext(file_name)[0] + '.txt'
        source_txt_path = os.path.join('.', txt_file_name)
        destination_txt_path = os.path.join(output_txt_dir, txt_file_name)
        
        shutil.move(source_txt_path, destination_txt_path)

print("Processing complete.")
