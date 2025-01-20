import fitz  # PyMuPDF
import os
import shutil


def check_keywords(filepath, inclusion_keywords, exclusion_keywords):
    """Check if any of the specified inclusion or exclusion keywords exist within the PDF document."""
    doc = fitz.open(filepath)
    has_inclusion_keyword, has_exclusion_keyword = False, False
    for page in doc:
        page_text = page.get_text().upper()
        if not has_inclusion_keyword:
            for keyword in inclusion_keywords:
                if keyword.upper() in page_text:
                    has_inclusion_keyword = True
                    break  # Stop checking if we've found an inclusion keyword
        if not has_exclusion_keyword:
            for keyword in exclusion_keywords:
                if keyword.upper() in page_text:
                    has_exclusion_keyword = True
                    break  # Stop checking if we've found an exclusion keyword
        if has_inclusion_keyword and has_exclusion_keyword:
            break  # No need to check further if both conditions are met
    return has_inclusion_keyword, has_exclusion_keyword

def convert_and_save_if_contains_keyword(folder_path, inclusion_keywords, exclusion_keywords, destination_folder):
    """Convert PDFs containing specified inclusion keywords to text files with preserved formatting unless exclusion keywords are also found. Copies all qualifying PDFs to a destination folder."""
    os.makedirs(destination_folder, exist_ok=True)
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            has_inclusion_keyword, has_exclusion_keyword = check_keywords(pdf_path, inclusion_keywords, exclusion_keywords)
            if has_inclusion_keyword and not has_exclusion_keyword:

                shutil.copy(pdf_path, destination_folder)
                
                print(f"Copied {filename} into {destination_folder} because it contains the inclusion keyword(s) and not the exclusion keyword.")

folder_path = "../../data/extract_landscape/"
inclusion_keywords = ["BIOPSIES TRANSBRONCHIQUES", "BIOPSIE TRANSBRONCHIQUE", "BIOPSIES TRANSBRONCHIQUE", "BIOPSIE TRANSBRONCHIQUES", "BTB", "BIOSPIE TRANSBRONCHIQUE"]
#inclusion_keywords = ["LAVAGE BRONCHO ALVEOLAIRE", "LAVAGE BRONCHOALVEOLAIRE", "LAVAGE BRONCHO-ALVEOLAIRE", "LBA", "BIOSPIE TRANSBRONCHIQUE"]

exclusion_keywords = ["Annulé"] 
destination_folder = "../../data/extract_landscape_btb/"
convert_and_save_if_contains_keyword(folder_path, inclusion_keywords, exclusion_keywords, destination_folder)