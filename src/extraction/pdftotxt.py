import fitz  # PyMuPDF
import os
import shutil

def contains_keyword(filepath, keywords):
    doc = fitz.open(filepath)
    for page in doc:
        page_text = page.get_text().upper()  # Convert page text to upper case once
        for keyword in keywords:
            if keyword.upper() in page_text:  # Convert each keyword to upper case for comparison
                return True
    return False


def convert_and_save_if_contains_keyword(folder_path, keyword, destination_folder):
    os.makedirs(destination_folder, exist_ok=True)
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            if contains_keyword(pdf_path, keywords):
                doc = fitz.open(pdf_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                output_txt_path = pdf_path.replace('.pdf', '.txt')
                with open(output_txt_path, 'w', encoding='utf-8') as file:
                    file.write(text)
                # Copy the PDF file to the destination folder
                shutil.copy(pdf_path, destination_folder)
                print(f"Processed and saved {filename} because it contains the keyword.")


folder_path = "..//..//./data//extract_easily//"
keywords = ["BIOPSIES TRANSBRONCHIQUES", "BIOPSIE TRANSBRONCHIQUE", "BIOPSIES TRANSBRONCHIQUE", "BIOPSIE TRANSBRONCHIQUES", "BTB", "BIOSPIE TRANSBRONCHIQUE"]
destination_folder = "..//..//./data//extract_easily_btb//"
convert_and_save_if_contains_keyword(folder_path, keywords, destination_folder)
