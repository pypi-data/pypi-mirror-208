from logging import Logger
import pandas as pd
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal


def extract_variant_table(pdf: str, variant_type: str):
    # Narrow down to variant table entries
    in_range_trigger = False
    table_entries = []
    for page_layout in extract_pages(pdf, maxpages=2):
        for element in page_layout:
            if isinstance(element, LTTextBoxHorizontal):
                if "Clinical\nInformation\n" in element.get_text():
                    in_range_trigger = True
                    continue
                if "INTERPRETATION" in element.get_text():
                    in_range_trigger = False
                    break
                if in_range_trigger == True:
                    table_entries.append(element)

    # Remove stray "p.\n" entries
    table_entries = [i for i in table_entries if "p.\n" not in i.get_text()]

    # Get a set of column coordinates for each table entry
    coordinate_set = set([round(int(entry.bbox[0]), -1) for entry in table_entries])

    # Group by column coordinates -> df
    table_columns = []
    for coordinate in sorted(list(coordinate_set)):
        column = []
        for entry in table_entries:
            if round(int(entry.bbox[0]), -1) == coordinate:
                column.append(entry.get_text().strip().replace("\n", " "))
        table_columns.append(column)

    variant_df = pd.DataFrame(
        {
            "gene": table_columns[0],
            "type": table_columns[1],
            "description": table_columns[2],
            "vaf": table_columns[3],
            "info": table_columns[4],
        }
    )

    # Drop by variant type
    if variant_type == "copy number":
        variant_df = variant_df[variant_df["type"] == "CNV"]
    elif variant_type == "structural":
        variant_df = variant_df[variant_df["type"] == "Translocation"]

    return variant_df
