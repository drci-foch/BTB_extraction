import fitz  # PyMuPDF
import os
import shutil


def check_keywords(filepath, inclusion_keywords, exclusion_keywords):
    """Check if any of the specified inclusion or exclusion keywords exist within the PDF document."""
    try:
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
        doc.close()
        return has_inclusion_keyword, has_exclusion_keyword, None
    except ValueError as e:
        if "document closed or encrypted" in str(e):
            return False, False, "encrypted"
        else:
            return False, False, str(e)
    except Exception as e:
        return False, False, str(e)


def convert_and_save_if_contains_keyword(
    folder_path, inclusion_keywords, exclusion_keywords, destination_folder
):
    """Convert PDFs containing specified inclusion keywords to text files with preserved formatting unless exclusion keywords are also found. Copies all qualifying PDFs to a destination folder."""
    os.makedirs(destination_folder, exist_ok=True)

    # Get list of all PDF files in source folder and sort them
    all_pdf_files = sorted([f for f in os.listdir(folder_path) if f.endswith(".pdf")])

    # Check if destination folder has any PDF files
    dest_pdf_files = sorted(
        [f for f in os.listdir(destination_folder) if f.endswith(".pdf")]
    )

    start_index = 0
    if dest_pdf_files:
        # Find the last processed file
        last_processed = dest_pdf_files[-1]
        print(f"Last processed file: {last_processed}")

        # Find its index in the source folder
        if last_processed in all_pdf_files:
            last_index = all_pdf_files.index(last_processed)
            start_index = last_index + 1
            print(f"Continuing from file index {start_index} of {len(all_pdf_files)}")
        else:
            print(
                f"Warning: Last processed file {last_processed} not found in source folder. Starting from beginning."
            )
    else:
        print("No files found in destination folder. Starting from the beginning.")

    # Slice the list to get only files after the start_index
    files_to_process = all_pdf_files[start_index:]

    # Create error log file or append to existing one
    error_log_path = os.path.join(destination_folder, "error_documents.txt")
    error_mode = "a" if os.path.exists(error_log_path) else "w"

    print(
        f"Total files: {len(all_pdf_files)}, Files to process: {len(files_to_process)}"
    )

    with open(error_log_path, error_mode) as error_log:
        for filename in files_to_process:
            pdf_path = os.path.join(folder_path, filename)
            try:
                has_inclusion_keyword, has_exclusion_keyword, error = check_keywords(
                    pdf_path, inclusion_keywords, exclusion_keywords
                )

                if error:
                    # Log the problematic document
                    error_log.write(f"{filename}\n")
                    print(f"Could not process {filename}. Reason: {error}")
                    continue

                if has_inclusion_keyword and not has_exclusion_keyword:
                    shutil.copy(pdf_path, destination_folder)
                    print(
                        f"Copied {filename} into {destination_folder} because it contains the inclusion keyword(s) and not the exclusion keyword."
                    )
            except Exception as e:
                # Log any other unexpected errors
                error_log.write(f"{filename}\n")
                print(f"Error processing {filename}: {str(e)}")


folder_path = "../../data/extract_all/"
inclusion_keywords = [
    "BIOPSIES TRANSBRONCHIQUES",
    "BIOPSIE TRANSBRONCHIQUE",
    "BIOPSIES TRANSBRONCHIQUE",
    "BIOPSIE TRANSBRONCHIQUES",
    "BTB",
    "BIOSPIE TRANSBRONCHIQUE",
]
# inclusion_keywords = ["LAVAGE BRONCHO ALVEOLAIRE", "LAVAGE BRONCHOALVEOLAIRE", "LAVAGE BRONCHO-ALVEOLAIRE", "LBA", "BIOSPIE TRANSBRONCHIQUE"]
exclusion_keywords = ["Annulé"]
destination_folder = "../../data/extract_filter_btb/"
convert_and_save_if_contains_keyword(
    folder_path, inclusion_keywords, exclusion_keywords, destination_folder
)
