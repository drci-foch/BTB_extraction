import os
import subprocess
import shutil

# Configuration
JAVA_HOME = r"C:\Path\To\Java11\bin"  # Update this path
java_path = r"C:\Program Files\Java\jdk-21.0.5\bin\java.exe"  # Adjust based on your installation path
jar_path = "./pdftotext-jar-with-dependencies.jar"
folder_path = "../../data/extract_landscape_btb/"
output_txt_dir = "../../data/txt_landscape"


def main():
    # Create output directory
    os.makedirs(output_txt_dir, exist_ok=True)

    # Process PDF files
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(folder_path, file_name)
            print(f"\nProcessing: {file_path}")
            
            try:
                command = [java_path, "-jar", jar_path, file_path]
                result = subprocess.run(command, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    txt_file_name = os.path.splitext(file_name)[0] + '.txt'
                    source_txt_path = os.path.join('.', txt_file_name)
                    destination_txt_path = os.path.join(output_txt_dir, txt_file_name)
                    
                    if os.path.exists(source_txt_path):
                        shutil.move(source_txt_path, destination_txt_path)
                        print(f"Successfully converted: {file_name}")
                    else:
                        print(f"Conversion produced no output file for: {file_name}")
                else:
                    print(f"Conversion failed for {file_name}")
                    print(f"Error output: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                print(f"Timeout while processing {file_name}")
            except Exception as e:
                print(f"Error processing {file_name}: {str(e)}")

if __name__ == "__main__":
    main()