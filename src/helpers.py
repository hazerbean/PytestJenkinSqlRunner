import json
import os
from pathlib import Path
import pandas as pd
from src.configs import configurations
from src.utilities import customlogger
import pytest

logger = customlogger.custom_logger()

def verify_file_exists(folder_location, file_name):
    file_path = configurations.get_relative_path(folder_location, file_name)
    try:
        if not os.path.exists(file_path):
            return False
        else:
            return True
    except Exception as e:
        logger.error(f"{e}")

def find_file(file_name, search_path):
    for root, dirs, files in os.walk(search_path):
        if file_name in files:
            return os.path.join(root, file_name)
    return None

def compare_row_count_of_files(file_1, file_2):
    df1 = pd.read_csv(file_1)
    df2 = pd.read_csv(file_2)
    if df1.shape == df2.shape:
        return True
    else:
        return False

def generate_column_wise_counts(csv_file):
    df = pd.read_csv(csv_file)
    columns = df.columns
    counts, null_counts, distinct_counts, min_values, max_values = [], [], [], [], []

    for column in columns:
        # Count the number of non-null values in the column
        counts.append(df[column].count())
        # Count the number of null values in the column
        null_counts.append(df[column].isnull().sum())
        # Count the number of unique values in the column
        distinct_counts.append(df[column].nunique())

        try:
            # Select the string values in the column
            string_values = df[column].select_dtypes(include="object")
            if not string_values.empty:
                # Get the minimum and maximum string lengths
                min_values.append(string_values.str.len().min())
                max_values.append(string_values.str.len().max())
            else:
                min_values.append("Null")
                max_values.append("Null")
        except Exception as e:
            logger.info(f"An error occurred while processing column '{column}': {e}")
            min_values.append("Null")
            max_values.append("Null")

    # Create a dataframe with the counts
    result_df = pd.DataFrame({
        "Column": columns,
        "Count": counts,
        "Null Count": null_counts,
        "Distinct Count": distinct_counts,
        "Min Value (length)": min_values,
        "Max Value (length)": max_values
    })

    return result_df

def compare_dataframes(csv_1_path, csv_2_path):
    df1 = pd.read_csv(csv_1_path)
    df2 = pd.read_csv(csv_2_path)
    return df1.apply(tuple, 1).isin(df2.apply(tuple, 1))

def compare_dataframes_counts(csv_file1, csv_file2):
    # Generate counts for each dataframe and compare them
    return compare_dataframes(generate_column_wise_counts(csv_file1), generate_column_wise_counts(csv_file2))

def compare_schemas(df1, df2, output_folder, mismatching_columns_csv_file):
    # Check if either of the input DataFrames is empty
    if df1.empty or df2.empty:
        raise ValueError("One or both input DataFrames are empty")

    # Create a DataFrame that contains the column names and data types of the columns in the first DataFrame
    schema_df1 = pd.DataFrame({
        "Column": df1.columns,
        "Type": df1.dtypes
    })

    # Create a DataFrame that contains the column names and data types of the columns in the second DataFrame
    schema_df2 = pd.DataFrame({
        "Column": df2.columns,
        "Type": df2.dtypes
    })

    # Merge the two schema DataFrames into a single DataFrame using the column names as the keys
    merged_schemas = pd.merge(schema_df1, schema_df2, on="Column", how="outer", suffixes=("_df1", "_df2"))

    # Check if the data types in both DataFrames match for each column
    mismatching_columns = merged_schemas[merged_schemas["Type_df1"] != merged_schemas["Type_df2"]]

    # If there are mismatching columns, export them to a CSV file and return False
    if not mismatching_columns.empty:
        mismatching_columns.to_csv(rf"{output_folder}/" + f"{mismatching_columns_csv_file}.csv", index=False)
        return False

    # If all data types match, return True
    return True

def convert_json_to_dict(json_file_location):
    json_file = Path(json_file_location)
    if json_file.exists():
        data_dict = json.loads(json_file.read_text())
        return data_dict
    else:
        raise FileNotFoundError

def read_data_table_from_feature_file(table_with_headers):
    list_table_rows = table_with_headers.split("\n")
    list_headers = str(list_table_rows[0]).strip("|").split("|")
    dict_table = {}
    for header in list_headers:
        header_text = header.strip()
        lst_row = []
        for i in range(1, list_table_rows.__len__()):
            list_temp = list_table_rows[i].strip("|").split("|")
            lst_row.append(list_temp[list_headers.index(header)].strip())

        dict_table[header_text] = lst_row

    return dict_table
