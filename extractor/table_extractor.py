import camelot
import pandas as pd
from tabulate import tabulate

def extract_tables_from_pdf(file_path, pages):
    try:
        tables = camelot.read_pdf(file_path, pages=pages)
        return tables
    except Exception as e:
        print(f"Error extracting tables: {e}")
        return []

def table_to_formats(table, file_name, page_no, index):
    df = table.df

    json_data = df.to_dict(orient="records")
    markdown = tabulate(df, headers='keys', tablefmt='pipe')

    return {
        "file": file_name,
        "page": page_no,
        "table_index": index,
        "json": json_data,
        "markdown": markdown
    }