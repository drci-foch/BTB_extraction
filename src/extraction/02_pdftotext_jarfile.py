import os
import subprocess
import shutil

# Define the path to the java executable and the jar file
java_path = "../../jdk-17.0.10_windows-x64_bin/jdk-17.0.10/bin/java.exe"
jar_path = "./pdftotext-jar-with-dependencies.jar"

# Folder containing the PDF files
folder_path = "../../data/extract_easily_btb"

# Output directory for the txt files
output_txt_dir = "../../data/txt"

# Ensure the output directory exists
os.makedirs(output_txt_dir, exist_ok=True)

# Iterate over all files in the folder
for file_name in os.listdir(folder_path):
    # Check if the file is a PDF
    if file_name.endswith(".pdf"):
        # Construct the full file path
        file_path = os.path.join(folder_path, file_name)
        
        # Build the command
        command = [java_path, "-jar", jar_path, file_path]
        
        # Execute the command
        subprocess.run(command)
        
        # Construct the expected output txt file name based on the PDF
        # Assuming the jar utility generates txt files with the same name as the PDF
        txt_file_name = os.path.splitext(file_name)[0] + '.txt'
        
        # Construct the source path of the txt file
        source_txt_path = os.path.join('.', txt_file_name)
        
        # Construct the destination path of the txt file
        destination_txt_path = os.path.join(output_txt_dir, txt_file_name)
        
        # Move the txt file to the desired directory
        shutil.move(source_txt_path, destination_txt_path)

print("Processing complete.")
