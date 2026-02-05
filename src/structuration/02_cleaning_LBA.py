import pandas as pd
import re 

# Read the input Excel file
df = pd.read_excel(r"C:\Users\benysar\Documents\GitHub\BTB_extraction\src\output\LBA_structurated_raw.xlsx")
df.head()

# Choose only the columns selected by Natalia
df = df[["Filename","IPP","Biopsy ID", "Date de prélèvement", "Macrophages", 
         "Lymphocytes","Polynucléaires neutrophiles", "Polynucléaires éosinophiles", "Volume","Numération"]]

# Convert date column to datetime
df["Date de prélèvement"] = df["Date de prélèvement"].astype("datetime64[ns]", errors="ignore")

# Process Lymphocytes
df['Lymphocytes_text'] = df['Lymphocytes'].astype(str)
numeric_values = []
text_values = []
for value in df['Lymphocytes_text']:
    clean_value = value.replace('%', '')
    try:
        numeric_values.append(float(clean_value))
        text_values.append(None)
    except ValueError:
        numeric_values.append(None)
        text_values.append(value)
df['Lymphocytes'] = numeric_values
df['Lymphocytes_text'] = text_values

# Process Polynucléaires neutrophiles
df['Polynucléaires neutrophiles_text'] = df['Polynucléaires neutrophiles'].astype(str)
numeric_values = []
text_values = []
for value in df['Polynucléaires neutrophiles_text']:
    try:
        numeric_values.append(float(value))
        text_values.append(None)
    except ValueError:
        numeric_values.append(None)
        text_values.append(value)
df['Polynucléaires neutrophiles'] = numeric_values
df['Polynucléaires neutrophiles_text'] = text_values

# Process Polynucléaires éosinophiles
df['Polynucléaires éosinophiles_text'] = df['Polynucléaires éosinophiles'].astype(str)
numeric_values = []
text_values = []
for value in df['Polynucléaires éosinophiles_text']:
    clean_value = value.replace('%', '')
    try:
        numeric_values.append(float(clean_value))
        text_values.append(None)
    except ValueError:
        numeric_values.append(None)
        text_values.append(value)
df['Polynucléaires éosinophiles'] = numeric_values
df['Polynucléaires éosinophiles_text'] = text_values

# Process Volume
df['Volume_text'] = df['Volume'].astype(str)
numeric_values = []
text_values = []
for value in df['Volume_text']:
    clean_value = value.replace('ml', '')
    try:
        numeric_values.append(float(clean_value))
        text_values.append(None)
    except ValueError:
        numeric_values.append(None)
        text_values.append(value)
df['Volume'] = numeric_values
df['Volume_text'] = text_values

# Process Numération
df['Numération_text'] = df['Numération'].astype(str)
numeric_values = []
text_values = []
for value in df['Numération_text']:
    clean_value = value.replace('éléments/ml', '')\
                      .replace(' ', '')\
                      .replace('.', '')\
                      .strip()
    try:
        num = float(clean_value)
        numeric_values.append(num)
        text_values.append(None)
    except ValueError as e:
        numeric_values.append(None)
        text_values.append(value)
df['Numération'] = numeric_values
df['Numération_text'] = text_values

# Save the processed data to a new Excel file
df.to_excel(r"C:\Users\benysar\Documents\GitHub\BTB_extraction\src\output\LBA_structurated_cleaned.xlsx")