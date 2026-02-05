import argparse
import os
import re
import warnings
import pandas as pd
import chardet
warnings.filterwarnings("ignore")

"""
This script is designed to extract information from BTB documents in .txt version, specifically targeting documents dated from 2021 to 2019.
It has been tailored to understand and process the formatting and content specific to these years.
"""

def extract_prenom_before_docteur(text):
    """
    Extracts the first name (prénom) from a string that precedes a specific pattern, typically "Docteur".
    """
    pattern = r"Prénom\s*:\s*([A-Z\s]+)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        before_docteur = match.group(1)
        first_name = before_docteur.split()[0] if before_docteur else None
        return first_name
    return None

def extract_technique(text, option="lba"):
    """
    Extracts the medical technique (BTB or LBA) from a given text based on various patterns.
    """
    if option.lower() == "btb":
        # Patterns for BTB (Biopsies Transbronchiques)
        technique_pattern = r"(2\.|II\.|I\.|2/|2°/)[\s+]*(Biopsies\s+trans[ -]*bronchiques|Biopsies\s+transbronchiques|Biospies\s+transbronchiques|BTB)(?:(?!LAVAGE)[\s\S+])*?Technique[^\S\r\n]*:[^\S\r\n]*([^;]+)"
        fallback_technique_pattern = r"(Biopsies\s+trans[ -]*bronchiques|Biopsies\s+transbronchiques|Biospies\s+transbronchiques|BTB)(?:(?!LAVAGE)[\s\S])*?Technique\s*:\s*([^;]+)"
        fallback_technique_mention = "HES"
    elif option.lower() == "lba":
        # Patterns for LBA (Lavage Bronchoalvéolaire)
        technique_pattern = r"(1\.|I\.|I\.|1/|1°/)[\s+]*(Lavage\s+bronchoalvéolaire|Lavage\s+broncho-alvéolaire|LBA)(?:(?!BIOPSIE)[\s\S+])*?Technique[^\S\r\n]*:[^\S\r\n]*([^;]+)"
        fallback_technique_pattern = r"(Lavage\s+bronchoalvéolaire|Lavage\s+broncho-alvéolaire|LBA)(?:(?!BIOPSIE)[\s\S])*?Technique\s*:\s*([^;]+)"
        fallback_technique_mention = "cytocentrifugation"
    else:
        raise ValueError("Invalid option. Choose 'btb' or 'lba'.")
    
    # Primary pattern search
    technique_match = re.search(technique_pattern, text, re.DOTALL | re.IGNORECASE)
    if technique_match:
        return technique_match.group(3).strip()
    
    # Fallback pattern search
    fallback_match = re.search(fallback_technique_pattern, text, re.DOTALL | re.IGNORECASE)
    if fallback_match:
        return fallback_match.group(2).strip()
    
    # Check for fallback mention if no patterns match
    if fallback_technique_mention.lower() in text.lower():
        return fallback_technique_mention
    
    # No mention of biopsie or lavage, just the mention of techniques two times
    technique_search_pattern = r"Technique\s*:\s*([^;]+)"
    technique_matches = re.findall(technique_search_pattern, text, re.IGNORECASE | re.DOTALL)
    if technique_matches:
        return technique_matches[0].strip()
    
    # Last fallback: look for any mention of technique in the document
    last_fallback_technique_pattern = r"Technique\s*:\s*([^;]+)"
    last_fallback_match = re.search(last_fallback_technique_pattern, text, re.DOTALL)
    if last_fallback_match:
        return last_fallback_match.group(1).strip()
    
    return None

def extract_niveaux_coupes(text):
    """
    Extracts the levels of cuts (niveaux de coupes) from a given text.
    """
    # Most found pattern
    pattern = r"(2\.|II\.|I\.|2/|2°/)[\s+]*(Biopsies\s+trans[ -]*bronchiques|Biopsies\s+transbronchiques|Biospies\s+transbronchiques|BTB)[\s\S+]*?Technique\s*:\s*([^;]+);\s*([^n]+)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(4).strip()
    
    # Sometimes, there isn't the numbers, only "Biopsie" in text etc..
    fallback_pattern = r"(Biopsies\s+trans[ -]*bronchiques|Biopsies\s+transbronchiques|Biospies\s+transbronchiques|BTB)(?:(?!LAVAGE)[\s\S])*?Technique\s*:\s*([^;]+);\s*([^n]+)"
    fallback_match = re.search(fallback_pattern, text, re.DOTALL)
    if fallback_match:
        return fallback_match.group(3).strip()
    
    # Check for HES after failing to find the first two patterns
    if "HES" in text:
        return None
    
    # No mention of biopsie or lavage, just the mention of techniques two times. The BTB technique is always second.
    parts = re.split(r"(?=Technique\s*:)", text, flags=re.IGNORECASE)
    if len(parts) > 2:
        two_parts_fallback_technique_pattern = r"Technique\s*:\s*([^;]+);\s*([^n]+)"
        two_parts_fallback_match = re.search(
            two_parts_fallback_technique_pattern, parts[-1], re.DOTALL
        )
        if two_parts_fallback_match:
            return two_parts_fallback_match.group(2).strip()
    
    # Else, look at any mention of technique in the document
    last_fallback_technique_pattern = r"Technique\s*:\s*([^;]+);\s*([^n]+)"
    last_fallback_match = re.search(
        last_fallback_technique_pattern, text, re.DOTALL
    )
    if last_fallback_match:
        return last_fallback_match.group(2).strip()
    
    return None

def extract_information(text, patterns):
    """
    Extracts information based on specified patterns from a given text.
    """
    results = {}
    for item in patterns:
        field = item["field"]
        pattern = item["pattern"]
        group_index = item.get("group_index", 1)
        
        try:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            
            if match:
                # Special handling for the "Nom" field to concatenate groups 3 and 4
                if field == "Nom" and len(match.groups()) >= 4:
                    # Assuming groups 3 and 4 may contain the parts of the name you're interested in
                    part3 = match.group(3) if match.group(3) is not None else ''
                    part4 = match.group(4) if match.group(4) is not None else ''
                    # Concatenate the parts, trimming any leading/trailing whitespace
                    results[field] = (part3 + part4).strip()
                else:
                    # For all other fields, or if "Nom" does not have groups 3 and 4
                    if group_index <= len(match.groups()):
                        results[field] = match.group(group_index).strip()
                    else:
                        print(f"Warning: Group index {group_index} is out of range for pattern {pattern}")
                        results[field] = None
            else:
                results[field] = None
        except Exception as e:
            print(f"Error extracting {field}: {str(e)}")
            results[field] = None
    
    return results

def read_text_file(file_path):
    """
    Reads the content of a text file and returns it as a string.
    Uses chardet to detect the correct encoding.
    """
    try:
        # First detect encoding with chardet
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            detected = chardet.detect(raw_data)
            encoding = detected['encoding']
            
        print(f"Detected encoding for {os.path.basename(file_path)}: {encoding}")
        
        # Use the detected encoding to read the file
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                text = file.read()
                return text
        except UnicodeDecodeError:
            # Fallback to common encodings
            for enc in ['iso-8859-1', 'utf-8', 'latin-1', 'cp1252']:
                try:
                    with open(file_path, 'r', encoding=enc) as file:
                        text = file.read()
                        print(f"Successfully read with {enc} encoding")
                        return text
                except UnicodeDecodeError:
                    continue
            
            # Last resort: binary read with forced decoding
            return raw_data.decode('utf-8', errors='replace')
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return ""

def process_text_files_in_directory(directory_path):
    data = []
    # Verify directory exists
    if not os.path.isdir(directory_path):
        print(f"Directory not found: {directory_path}")
        return pd.DataFrame()
    
    # Get list of text files
    txt_files = [f for f in os.listdir(directory_path) if f.endswith(".txt")]
    print(f"Found {len(txt_files)} text files in directory")
    
    if not txt_files:
        print("No .txt files found in the directory")
        return pd.DataFrame()
    
    # Process each file
    for filename in txt_files:
        try:
            file_path = os.path.join(directory_path, filename)
            print(f"\nProcessing file: {filename}")
            
            # Read file content
            text = read_text_file(file_path)
            if not text:
                print(f"Empty or unreadable file: {filename}")
                continue
                
            print(f"File length: {len(text)} characters")
            print("First 100 characters:", text[:100].replace('\n', '\\n'))
            
            # Debug - search for specific patterns manually
            biopsy_pattern = r"(?:^|\n)[\s\xa0]*N°[\s\xa0]*P[\s\xa0]*(\d+\.?\d*)"
            date_pattern = r"Prélevé[\s\xa0]*le[\s\xa0]*:[\s\xa0]*(\d{2}/\d{2}/\d{4})"
            
            biopsy_match = re.search(biopsy_pattern, text, re.DOTALL | re.IGNORECASE)
            date_match = re.search(date_pattern, text, re.DOTALL | re.IGNORECASE)
            
            print(f"Biopsy ID match: {biopsy_match.group(1) if biopsy_match else 'Not found'}")
            print(f"Date match: {date_match.group(1) if date_match else 'Not found'}")
            
            # Extract all information based on patterns
            info = extract_information(text, PATTERNS)
            
            # Add additional fields
            info["Technique"] = extract_technique(text, option="lba")
            info["Prénom"] = extract_prenom_before_docteur(text)
            info["Filename"] = filename
            
            # Extract IPP from filename if possible
            try:
                info["IPP"] = filename.split("_")[0]
            except:
                info["IPP"] = None
                
            # Check if we've extracted any meaningful data
            non_empty_values = sum(1 for v in info.values() if v is not None and v != "")
            print(f"Extracted {non_empty_values} non-empty values from file")
            
            if non_empty_values > 2:  # At least some data beyond filename and IPP
                data.append(info)
            else:
                print(f"WARNING: Minimal data extracted from {filename}, might be a formatting issue")
        except Exception as e:
            print(f"Error processing file {filename}: {str(e)}")
    
    # Create DataFrame only if we have data
    if data:
        print(f"\nSuccessfully processed {len(data)} files with meaningful data")
        all_columns = list(data[0].keys())
        print(f"Available columns: {all_columns}")
        
        # Ensure all dictionaries have the same keys
        all_keys = set()
        for d in data:
            all_keys.update(d.keys())
        
        # Fill in missing keys with None
        for d in data:
            for key in all_keys:
                if key not in d:
                    d[key] = None
        
        # Order columns based on COLUMN_ORDER, adding any new columns at the end
        column_order = COLUMN_ORDER + [col for col in all_keys if col not in COLUMN_ORDER]
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Reorder columns - only use columns that exist in the DataFrame
        valid_columns = [col for col in column_order if col in df.columns]
        df = df[valid_columns]
        
        return df
    else:
        print("No data was successfully extracted from any files")
        return pd.DataFrame()

def remove_illegal_chars(s):
    # Remove control characters while preserving accented characters
    if isinstance(s, str):
        return re.sub(r'[\x00-\x1F\x7F]', '', s)
    return s

# Define patterns for information extraction
PATTERNS = [
    {
        "field": "Nom",
        "pattern": r"(?i)((?<!Pré)Nom\s*:\s*|Nom[\s+]*usuel\s*:\s*)(?:Mme\s+)?(([A-Z]+)([\s]*(?:\s*(Pr))?[A-Z]*))(?:\s*(Destinataire))?",
        "group_index": 3,
    },
    {
        "field": "Date de naissance",
        "pattern": r"(?i)(Date[\s+]*de[\s+]*naissance\s*:\s*)(\d{2}/\d{2}/\d{4})",
        "group_index": 2,
    },
    {
        "field": "Biopsy ID",
        "pattern": r"((N°\s+de\s+demande\s+:\s+)|(N°\s+P\s+)|(N°\s+S\s+)|(?:^|\n)[\s\xa0]*N°[\s\xa0]*P[\s\xa0]*)(\w+-\w+|\w+.\w+|\d+\.?\d*)",
        "group_index": 5,
    },
    {"field": "Sexe", "pattern": r"Sexe\s*:\s*([MF])", "group_index": 1},
    {
        "field": "Date de prélèvement",
        "pattern": r"(?i)(Prélevé[\s\xa0]*le[\s\xa0]*[\s\xa0]*:[\s\xa0\D]*)(\d{2}/\d{2}/\d{4})",
        "group_index": 2,
    },
    {"field": "Prescripteur", "pattern": r"Docteur\s+([A-Za-zÀ-ÿ\s\.-]+?)(?=(?:,\s*Compte-rendu|\s*\n\s*ADICAP|\s*\n\s*(?:\n\s*)*\d{2}\/\d{2}\/\d{4}))", "group_index": 1},
]

# Define column order for output Excel
COLUMN_ORDER = [
    "Filename",
    "IPP",
    "Biopsy ID",
    "Nom",
    "Prénom",
    "Date de naissance",
    "Sexe",
    "Date de prélèvement",
    "Prescripteur",
    "Technique",
]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process BTB text files in a folder and extract information into an Excel file."
    )
    parser.add_argument(
        "directory_path",
        type=str,
        help="The path to the folder containing text files to process.",
    )
    args = parser.parse_args()
    directory_path = args.directory_path
    
    print(f"Starting extraction from directory: {directory_path}")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")
        except Exception as e:
            print(f"Could not create output directory: {str(e)}")
            output_dir = "."
    
    # Process files and create DataFrame
    df = process_text_files_in_directory(directory_path)
    
    if not df.empty:
        # Clean up data
        for col in df.select_dtypes(include=['object']).columns: 
            df[col] = df[col].apply(remove_illegal_chars)
        
        # Save to Excel
        output_file = os.path.join(output_dir, "BTB_structurated_raw.xlsx")
        df.to_excel(output_file, index=False)
        print(f"Extraction complete! Results saved to: {output_file}")
        print(f"Extracted data for {len(df)} files")
    else:
        print("No data was extracted. Excel file not created.")