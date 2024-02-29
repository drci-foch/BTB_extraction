import pandas as pd
import warnings
import argparse

warnings.filterwarnings("ignore")

"""
This script is designed for processing and summarizing data from Excel files, specifically tailored for BTB extraction. It performs data comprehension, generates summary statistics including unique value counts, NA counts, and NA counts by year, and saves these summaries into a new Excel file named 'data_summary.xlsx'.

The script is built to handle data with specific columns like 'Date de prélèvement', from which it extracts the year for further analysis. It excludes certain columns from summary statistics to focus on the most relevant data for analysis.

Usage:
The script accepts the path to the target Excel file as a command-line argument. Ensure that pandas and openpyxl libraries are installed in your environment to run this script successfully.

Example command:
python script_name.py path/to/your/data.xlsx

This command processes 'data.xlsx', generating a new Excel file 'data_summary.xlsx' with the data summaries.

Note:
- The script ignores warnings to keep the output clean.
- It requires the 'openpyxl' engine to write to Excel, so ensure this dependency is installed.
"""

def process_and_save_data_summary(excel_file_path):
    """
    Reads an Excel file, cleans data, and generates summary statistics including
    unique values, NA counts, and NA counts by year. It then saves these summaries
    into a new Excel file.

    Parameters:
    - excel_file_path (str): The file path to the Excel file to be processed.

    Outputs:
    - An Excel file named 'data_summary.xlsx' containing the data summaries across
      multiple sheets: 'Unique Values Counts', 'NA Counts', 'NA Counts by Year',
      and 'Unique Values'.
    """
    # Read the Excel file
    df = pd.read_excel(excel_file_path)
    # Convert date column to datetime format, assuming day first
    df["Date de prélèvement"] = pd.to_datetime(df["Date de prélèvement"], dayfirst=True)

    # Prepare summary statistics
    unique_values_dict, skip_columns = prepare_summary_statistics(df)

    # Extract and format unique values for certain columns
    unique_values_df = format_unique_values(unique_values_dict)

    # Count unique values and NAs, group NAs by year
    unique_values_counts, na_counts, na_counts_by_year = count_values(df)

    # Save the summaries to an Excel file
    save_summaries_to_excel(unique_values_counts, na_counts, na_counts_by_year, unique_values_df)

def prepare_summary_statistics(df):
    """
    Prepare the initial summary statistics from the dataframe, focusing on unique
    values in specific columns while excluding others.

    Parameters:
    - df (DataFrame): The dataframe to process.

    Returns:
    - A tuple containing a dictionary of unique values by column and a list of columns to skip.
    """
    # Columns to skip in the summary
    skip_columns = [
        "IPP", "Filename", "Nom", "Prénom", "Date de naissance",
        "Date de prélèvement", "Conclusion",
    ]
    # Dictionary to store unique values for each relevant column
    unique_values_dict = {column: df[column].dropna().unique().tolist() for column in df.columns if column not in skip_columns}

    # Equalize lengths of lists for uniformity
    max_len = max(len(v) for v in unique_values_dict.values())
    for column in unique_values_dict:
        current_len = len(unique_values_dict[column])
        unique_values_dict[column].extend([None] * (max_len - current_len))

    return unique_values_dict, skip_columns

def format_unique_values(unique_values_dict):
    """
    Formats the unique values dictionary into a DataFrame for easy Excel output.

    Parameters:
    - unique_values_dict (dict): A dictionary of unique values by column.

    Returns:
    - DataFrame: A DataFrame representation of the unique values.
    """
    return pd.DataFrame(unique_values_dict)

def count_values(df):
    """
    Counts unique values, NA values, and NA values by year in the DataFrame.

    Parameters:
    - df (DataFrame): The dataframe to process.

    Returns:
    - A tuple of DataFrames/series: unique value counts, NA counts, and NA counts by year.
    """
    unique_values_counts = df.nunique()
    na_counts = df.isna().sum()
    df["Year"] = df["Date de prélèvement"].dt.year
    na_counts_by_year = df.groupby("Year").apply(lambda x: x.isna().sum()).drop("Year", axis=1)

    return unique_values_counts, na_counts, na_counts_by_year

def save_summaries_to_excel(unique_values_counts, na_counts, na_counts_by_year, unique_values_df):
    """
    Saves the calculated summary statistics to an Excel file with multiple sheets.

    Parameters:
    - unique_values_counts (Series): The count of unique values for each column.
    - na_counts (Series): The count of NA values for each column.
    - na_counts_by_year (DataFrame): The count of NA values for each column by year.
    - unique_values_df (DataFrame): The DataFrame of unique values for selected columns.
    """
    with pd.ExcelWriter("./output/data_summary.xlsx", engine="openpyxl", mode="w") as writer:
        unique_values_counts.to_frame(name="Unique Values Count").to_excel(writer, sheet_name="Unique Values Counts")
        na_counts.to_frame(name="NA Counts").to_excel(writer, sheet_name="NA Counts")
        na_counts_by_year.to_excel(writer, sheet_name="NA Counts by Year")
        unique_values_df.to_excel(writer, sheet_name="Unique Values")
    print("DataFrames are saved in 'data_summary.xlsx'.")

def main():
    """
    Main function to handle command-line arguments and call the data processing function.
    """
    parser = argparse.ArgumentParser(description="Process Excel file and save data summary.")
    parser.add_argument("excel_file_path", type=str, help="Path to the Excel file to be processed.")
    args = parser.parse_args()
    process_and_save_data_summary(args.excel_file_path)

if __name__ == "__main__":
    main()
