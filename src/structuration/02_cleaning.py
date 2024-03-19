#TODO : Clean the data like what Natalia asked us to do (Word doc : Processing of BTB data.)

import pandas as pd
import re 

df = pd.read_excel(".././output/BTB_structurated_raw.xlsx")

def clean_infiltrat(text):
    if pd.isna(text):
        return None
    text = str(text)
    grade_pattern = re.compile(r'(A(?:\s+)?[0-4]|Ax|A1-)', re.IGNORECASE)
    match = grade_pattern.search(text)
    return (match.group(1).upper() if match else text) 

df['Infiltrat'] = df['Infiltrat'].apply(clean_infiltrat)

def clean_bronche(text):
    if pd.isna(text):
        return None
    text = str(text)
    grade_pattern = re.compile(r'(B[0-4]|Bx|BX)')
    match = grade_pattern.search(text)
    return (match.group(1).upper() if match else None)  

df['Bronchiolite Lymphocytaire'] = df['Bronchiolite Lymphocytaire'].apply(clean_bronche)


def clean_technique(text):
    if pd.isna(text):
        return None
    text = str(text)
    grade_pattern = re.compile(r'HES')
    match = grade_pattern.search(text)
    return (match.group().upper() if match else None)  

df['Technique'] = df['Technique'].apply(clean_technique)


def clean_nivcoupes(text):
    if pd.isna(text):
        return None
    text = str(text)
    grade_pattern = re.compile(r'\d+')
    match = grade_pattern.search(text)
    return (match.group().upper() if match else None)  

df['Niveaux de coupes'] = df['Niveaux de coupes'].apply(clean_nivcoupes)


def clean_site(site):
    if isinstance(site, str):
        site = site.strip().lower()  # Convert to lowercase and remove leading/trailing spaces
        
        # Replace multiple spaces with a single space
        site = ' '.join(site.split())

        site = site.replace('non precisée', '').replace('non precisé', '').replace('non communiqué', '').replace("#",'').replace('inconnu','')
        site = site.replace('non prcisée', '').replace('non prcis', '').replace('non prci','').replace("non prci",'').replace('non prcis','').replace('non communiqu', '').replace(".",'').replace('precise','').replace("non",'')
        site = site.replace('non communique', '').replace('non communiqu', '').replace('np', '').replace("non indiqu", "").replace('non communinqu','').replace('communinqu','').replace('communinq','').replace('indiqu','').replace('*','').replace("nc",'')
        site = site.replace('prci', '').replace("%",'').replace('btb n','').replace("nelson","").replace("communique","").replace("communiqu","").replace("(","").replace(")","").replace("commubuy","") 


        site = site.replace('/', ',').replace('+',',').replace('-',',').replace('et',',')
        site = re.sub(r'\d+', '', site)

        # Replace abbreviations
        site = site.replace('lm', 'right middle lobe')
        site = site.replace('lid', 'right lower lobe')
        site = site.replace('lim', 'middle lower lobe')
        site = site.replace('lig', 'left lower lobe')
        site = site.replace('lsd', 'right upper lobe')
        site = site.replace('lsg', 'left upper lobe')
        site = site.replace('lmd', 'right middle lobe')
        site = site.replace('lingula', ' lingula')
        site = site.replace('lin ', ' lingula')
        site = site.replace('lobemoyen', 'right middle lobe')
        site = site.replace('li ', 'right lower lobe ')
        site = site.replace(' li ', ' right lower lobe')
        site = site.replace(',li ', ', right lower lobe ')
        site = site.replace('li,', 'right lower lobe, ')

        site = site.replace('lobe infrieur gauche', 'left lower lobe')
        site = site.replace('lobe infrieur', 'right lower lobe')
        site = site.replace('infrieur gauche', 'left lower lobe')
        site = site.replace('lobeinfrieurgauche', 'left lower lobe')
        site = site.replace('lobe infrieur droit', 'right lower lobe')
        site = site.replace('infrieur droit', 'right lower lobe')
        site = site.replace('lobeinfrieurdroit', 'right lower lobe')
        
        site = site.replace('ld', 'right')
        site = site.replace('gauche', 'left')
        site = site.replace('droite', 'right')
        site = site.replace('droit', 'right')
        site = site.replace('pyramide basale right', 'right lower lobe ')
        site = site.replace('pyramide basale left', 'left lower lobe ')
        site = site.replace('pyramidebasaleleft', 'left lower lobe ')
        site = site.replace('pyramidebasaleright', 'right lower lobe ')


        
        site = site.replace('pyramidebasale', 'lower lobe ')
        site = site.replace('pyramidebasale', 'lower lobe ')


        if site == '*':
            site = ''
        if site == ',':
            site = ''
        if len(site) <=1:
            site=''


    return site


def process_df_column(column):
    # Function to process each string value
    def process_value(value):
        # Remove characters like ','
        value = str(value).replace(',', ' ')
        
        # Split the value into words to check for 'lobe' and 'lingula'
        words = value.split()
        
        # Process words, add ',' after 'lobe' or 'lingula' if they are not the last word
        processed_words = []
        for i, word in enumerate(words):
            if word in ['lobe', 'lingula'] and i != len(words) - 1:
                processed_words.append(word + ',')
            else:
                processed_words.append(word)
        
        # Join the processed words back into a string
        processed_value = ' '.join(processed_words)
        
        # Trim spaces around ','
        processed_value = ', '.join(segment.strip() for segment in processed_value.split(','))
        
        return processed_value

    # Apply the processing function to each value in the column
    return column.apply(process_value)
    

df['Site'] = df['Site'].apply(clean_site)
df["Site"] = process_df_column(df['Site'])
df['Site'] = df['Site'].str.replace("nan", "", regex=False)
df['Site'] = df['Site'].str.strip()
site_value_counts = df['Site'].value_counts()
site_value_counts.to_csv("value_counts.txt")


def clean_fragmentalveo(text):
    if pd.isna(text):
        return None
    text = str(text)
    grade_pattern = re.compile(r'\d+')
    match = grade_pattern.search(text)
    return (match.group().upper() if match else text)  

df['Nombre de fragment alvéolaire'] = df['Nombre de fragment alvéolaire'].apply(clean_fragmentalveo)

def clean_bronche(text):
    if pd.isna(text):
        return None
    text = str(text)
    grade_pattern = re.compile(r'\d+')
    match = grade_pattern.search(text)
    return (match.group().upper() if match else text)  

df['Bronches/Bronchioles'] = df['Bronches/Bronchioles'].apply(clean_bronche)


def standardize_values_inflammation_lymphocy(val):
    if pd.isna(val):
        return None
    val = str(val)  # Ensure the value is a string
    if val.lower() in ["non", "nonn", "nonl","rejet"]:
        return "Non"
    elif val.lower() in ["oui"]:
        return "Oui"
    elif val == "0":
        # Assuming "0" means "Non"; adjust based on actual meaning/context
        return "Non"
    else:
        # Return the value as is for specific conditions or statuses
        return val
df['Inflammation Lymphocytaire'] = df['Inflammation Lymphocytaire'].apply(standardize_values_inflammation_lymphocy)

def standardize_values_brochioliobli(val):
    if pd.isna(val):
        return None
    val = str(val)  
    if val.lower() in ["0", "n"]:
        return "0"
    elif val.lower() in ["p","o"]:
        return "1"

    else:
        return ""


df['Bronchiolite oblitérante'] = df['Bronchiolite oblitérante'].apply(standardize_values_brochioliobli)

def standardize_values_fibroelastoseinters(val):
    if pd.isna(val):
        return None
    val = str(val)  
    if val.lower() in ["0", "non"]:
        return "0"
    elif val.lower() in ["1","atteinte"]:
        return "1"

    else:
        return ""
    
df['Fibro-élastose interstitielle'] = df['Fibro-élastose interstitielle'].apply(standardize_values_fibroelastoseinters)

def clean_pnnca(text):
    if pd.isna(text):
        return None
    text = str(text)
    # This pattern matches one or more '+' signs, or specific keywords
    grade_pattern = re.compile(r'(\++)|(focal+)|(rare+)|(quelque+)', re.IGNORECASE)
    match = grade_pattern.search(text)
    if match:
        if match.group(1):  # If the match is for '+' signs
            return str(len(match.group(1)))  # Return the count of '+' signs
        else:
            return "1"  # For 'focal', 'rare', 'quelque', return "1"
    else:
        return "0"

df['PNN dans les cloisons alvéolaires'] = df['PNN dans les cloisons alvéolaires'].apply(clean_pnnca)


def clean_cellulemono(text):
    if pd.isna(text):
        return None
    text = str(text)
    # This pattern matches one or more '+' signs, or specific keywords
    grade_pattern = re.compile(r'(\++)|(focal+)|(rare+)|(quelque+)', re.IGNORECASE)
    match = grade_pattern.search(text)
    if match:
        if match.group(1):  # If the match is for '+' signs
            return str(len(match.group(1)))  # Return the count of '+' signs
        else:
            return "1"  # For 'focal', 'rare', 'quelque', return "1"
    else:
        return "0"


df['Cellules mononucléées'] = df['Cellules mononucléées'].apply(clean_cellulemono)

def clean_dilatation(text):
    if pd.isna(text):
        return None
    text = str(text)
    # This pattern matches one or more '+' signs, or specific keywords
    grade_pattern = re.compile(r'(\++)|(focal+)|(rare+)|(quelque+)', re.IGNORECASE)
    match = grade_pattern.search(text)
    if match:
        if match.group(1):  # If the match is for '+' signs
            return str(len(match.group(1)))  # Return the count of '+' signs
        else:
            return "1"  # For 'focal', 'rare', 'quelque', return "1"
    else:
        return "0"

df['Dilatation des capillaires alvéolaires'] = df['Dilatation des capillaires alvéolaires'].apply(clean_dilatation)


def clean_oedeme(text):
    if pd.isna(text):
        return None
    text = str(text)
    # This pattern matches one or more '+' signs, or specific keywords
    grade_pattern = re.compile(r'(\++)|(focal+)|(rare+)|(quelque+)', re.IGNORECASE)
    match = grade_pattern.search(text)
    if match:
        if match.group(1):  # If the match is for '+' signs
            return str(len(match.group(1)))  # Return the count of '+' signs
        else:
            return "1"  # For 'focal', 'rare', 'quelque', return "1"
    else:
        return "0"

df['Œdème des cloisons alvéolaires'] = df['Œdème des cloisons alvéolaires'].apply(clean_oedeme)

def clean_thrombi(text):
    if pd.isna(text):
        return None
    text = str(text)
    # This pattern matches one or more '+' signs, or specific keywords
    grade_pattern = re.compile(r'(\++)|(focal+)|(rare+)|(quelque+)', re.IGNORECASE)
    match = grade_pattern.search(text)
    if match:
        if match.group(1):  # If the match is for '+' signs
            return str(len(match.group(1)))  # Return the count of '+' signs
        else:
            return "1"  # For 'focal', 'rare', 'quelque', return "1"
    else:
        return "0"
df['Thrombi fibrineux dans les capillaires alvéolaires'] = df['Thrombi fibrineux dans les capillaires alvéolaires'].apply(clean_thrombi)

def clean_debri(text):
    if pd.isna(text):
        return None
    text = str(text)
    # This pattern matches one or more '+' signs, or specific keywords
    grade_pattern = re.compile(r'(\++)|(focal+)|(rare+)|(quelque+)', re.IGNORECASE)
    match = grade_pattern.search(text)
    if match:
        if match.group(1):  # If the match is for '+' signs
            return str(len(match.group(1)))  # Return the count of '+' signs
        else:
            return "1"  # For 'focal', 'rare', 'quelque', return "1"
    else:
        return "0"


df['Débris cellulaires dans les cloisons alvéolaires'] = df['Débris cellulaires dans les cloisons alvéolaires'].apply(clean_debri)


def clean_epaiss(text):
    if pd.isna(text):
        return None
    text = str(text)
    # This pattern matches one or more '+' signs, or specific keywords
    grade_pattern = re.compile(r'(\++(?:\S+)?(?:\w+)?|focal+|discr+|lger+|leger+|atteinte+)', re.IGNORECASE)
    match = grade_pattern.search(text)
    if match:
        if match.group(1):  # If the match is for '+' signs
            return str(len(match.group(1)))  # Return the count of '+' signs
        else:
            return "1"  # For 'focal', 'rare', 'quelque', return "1"
    else:
        return "0"

df['Epaississement fibreux des cloisons alvéolaires'] = df['Epaississement fibreux des cloisons alvéolaires'].apply(clean_epaiss)


def clean_hyperplasie(text):
    if pd.isna(text):
        return None
    text = str(text)
    # This pattern matches one or more '+' signs, or specific keywords
    grade_pattern = re.compile(r'(\++(?:\S+)?(?:\w+)?|focal+|discr+|lger+|leger+|atteinte+)', re.IGNORECASE)
    match = grade_pattern.search(text)
    if match:
        if match.group(1):  # If the match is for '+' signs
            return str(len(match.group(1)))  # Return the count of '+' signs
        else:
            return "1"  # For 'focal', 'rare', 'quelque', return "1"
    else:
        return "0"

df['Hyperplasie pneumocytaire'] = df['Hyperplasie pneumocytaire'].apply(clean_hyperplasie)

def clean_pnnespace(text):
    if pd.isna(text):
        return None
    text = str(text)
    # This pattern matches one or more '+' signs, or specific keywords
    grade_pattern = re.compile(r'(\++(?:\S+)?(?:\w+)?|focal+|discr+|rare+|prsence+|quelque+)', re.IGNORECASE)
    match = grade_pattern.search(text)
    if match:
        if match.group(1):  # If the match is for '+' signs
            return str(len(match.group(1)))  # Return the count of '+' signs
        else:
            return "1"  # For 'focal', 'rare', 'quelque', return "1"
    else:
        return "0"
 
df['PNN dans les espaces alvéolaires'] = df['PNN dans les espaces alvéolaires'].apply(clean_pnnespace)

def clean_macrophage(text):
    if pd.isna(text):
        return None
    text = str(text)
    # This pattern matches one or more '+' signs, or specific keywords
    grade_pattern = re.compile(r'(\++(?:\S+)?(?:\w+)?|focal+|discr+|rare+|prsence+|quelque+)', re.IGNORECASE)
    match = grade_pattern.search(text)
    if match:
        if match.group(1):  # If the match is for '+' signs
            return str(len(match.group(1)))  # Return the count of '+' signs
        else:
            return "1"  # For 'focal', 'rare', 'quelque', return "1"
    else:
        return "0" 
df['Macrophages dans les espaces alvéolaires'] = df['Macrophages dans les espaces alvéolaires'].apply(clean_macrophage)


def clean_bourgeons(text):
    if pd.isna(text):
        return None
    text = str(text)
    # This pattern matches one or more '+' signs, or specific keywords
    grade_pattern = re.compile(r'(\++(?:\S+)?(?:\w+)?|focal+|discr+|rare+|prsence+|quelque+|bauches+|petite+)', re.IGNORECASE)
    match = grade_pattern.search(text)
    if match:
        if match.group(1):  # If the match is for '+' signs
            return str(len(match.group(1)))  # Return the count of '+' signs
        else:
            return "1"  # For 'focal', 'rare', 'quelque', return "1"
    else:
        return "0"

df['Bourgeons conjonctifs dans les espaces alvéolaires'] = df['Bourgeons conjonctifs dans les espaces alvéolaires'].apply(clean_bourgeons)

def clean_hemati(text):
    if pd.isna(text):
        return None
    text = str(text)
    # This pattern matches one or more '+' signs, or specific keywords
    grade_pattern = re.compile(r'(\++(?:\S+)?(?:\w+)?|focal+|discr+|rare+|prsence+|quelque+|bauches+|petite+)', re.IGNORECASE)
    match = grade_pattern.search(text)
    if match:
        if match.group(1):  # If the match is for '+' signs
            return str(len(match.group(1)))  # Return the count of '+' signs
        else:
            return "1"  # For 'focal', 'rare', 'quelque', return "1"
    else:
        return "0"

df['Hématies dans les espaces alvéolaires'] = df['Hématies dans les espaces alvéolaires'].apply(clean_hemati)

def clean_membrane(text):
    if pd.isna(text):
        return None
    text = str(text)
    # This pattern matches one or more '+' signs, or specific keywords
    grade_pattern = re.compile(r'(\++(?:\S+)?(?:\w+)?|focal+|discr+|rare+|prsence+|quelque+|bauches+|petite+)', re.IGNORECASE)
    match = grade_pattern.search(text)
    if match:
        if match.group(1):  # If the match is for '+' signs
            return str(len(match.group(1)))  # Return the count of '+' signs
        else:
            return "1"  # For 'focal', 'rare', 'quelque', return "1"
    else:
        return "0"
    
df['Membranes hyalines'] = df['Membranes hyalines'].apply(clean_membrane)

def clean_fibrine(text):
    if pd.isna(text):
        return None
    text = str(text)
    # This pattern matches one or more '+' signs, or specific keywords
    grade_pattern = re.compile(r'(\++(?:\S+)?(?:\w+)?|focal+|discr+|rare+|prsence+|quelque+|bauches+|petite+)', re.IGNORECASE)
    match = grade_pattern.search(text)
    if match:
        if match.group(1):  # If the match is for '+' signs
            return str(len(match.group(1)))  # Return the count of '+' signs
        else:
            return "1"  # For 'focal', 'rare', 'quelque', return "1"
    else:
        return "0"
df['Fibrine dans les espaces alvéolaires'] = df['Fibrine dans les espaces alvéolaires'].apply(clean_fibrine)

def clean_inflammation(text):

    text = str(text)
    if len(text)<=1:
        return ""
    # This pattern matches one or more '+' signs, or specific keywords
    grade_pattern = re.compile(r'(\++(?:\S+)?(?:\w+)?|focal+|discr+|rare+|prsence+|quelque+|minim+|petite+)', re.IGNORECASE)
    match = grade_pattern.search(text)
    if match:
        if match.group(1):  # If the match is for '+' signs
            return str(len(match.group(1)))  # Return the count of '+' signs
        else:
            return "1"  # For 'focal', 'rare', 'quelque', return "1"
    else:
        return "0"
df['Inflammation sous-pleurale, septale, bronchique ou bronchiolaire'] = df['Inflammation sous-pleurale, septale, bronchique ou bronchiolaire'].apply(clean_inflammation)


def clean_BALT(text):
    if pd.isna(text):
        return None
    text = str(text)
    grade_pattern = re.compile(r'(\++|oui+|pres+)', re.IGNORECASE)    
    match = grade_pattern.search(text)
    if match:
        return "1"
    else:
        return "0"


df['BALT'] = df['BALT'].apply(clean_BALT)

def clean_thrombusfibrino(text):
    if pd.isna(text):
        return None
    text = str(text)
    grade_pattern = re.compile(r'(\++|oui+|pres+|1|2|prs+)', re.IGNORECASE)    
    match = grade_pattern.search(text)
    if match:
        return "1"
    else:
        return "0"


df['Thrombus fibrino-cruorique'] = df['Thrombus fibrino-cruorique'].apply(clean_thrombusfibrino)

def clean_necrose(text):
    if pd.isna(text):
        return None
    text = str(text)
    grade_pattern = re.compile(r'(\++|oui+|pres+|1|2|prs+)', re.IGNORECASE)    
    match = grade_pattern.search(text)
    if match:
        return "1"
    else:
        return "0"


df['Nécrose ischémique'] = df['Nécrose ischémique'].apply(clean_necrose)

def clean_inclusionvirale(text):
    if pd.isna(text):
        return None
    text = str(text)
    grade_pattern = re.compile(r'(\++|oui+|pres+|1|2|prs+)', re.IGNORECASE)    
    match = grade_pattern.search(text)
    if match:
        return "1"
    else:
        return "0"


df['Inclusions virales'] = df['Inclusions virales'].apply(clean_inclusionvirale)

def clean_agentpath(text):
    if pd.isna(text):
        return None
    text = str(text)
    grade_pattern = re.compile(r'(\++|oui+|pres+|1|2|prs+)', re.IGNORECASE)    
    match = grade_pattern.search(text)
    if match:
        return "1"
    else:
        return "0"


df['Agent pathogène'] = df['Agent pathogène'].apply(clean_agentpath)

def clean_esino(text):
    if pd.isna(text):
        return None
    text = str(text)
    grade_pattern = re.compile(r'(\++|oui+|pres+|1|2|prs+|poss+|pren+)', re.IGNORECASE)    
    match = grade_pattern.search(text)
    if match:
        return "1"
    else:
        return "0"


df['Eosinophilie (interstitielle/alvéolaire)'] = df['Eosinophilie (interstitielle/alvéolaire)'].apply(clean_agentpath)
df['Remodelage vasculaire'] = df['Remodelage vasculaire'].apply(clean_agentpath)
df['Matériel étranger d’inhalation'] = df['Matériel étranger d’inhalation'].apply(clean_agentpath)
df['IPP'] = "0" + df['IPP'].astype(str)

df.to_excel('../output/BTB_structurated_cleaned.xlsx', index=False)
