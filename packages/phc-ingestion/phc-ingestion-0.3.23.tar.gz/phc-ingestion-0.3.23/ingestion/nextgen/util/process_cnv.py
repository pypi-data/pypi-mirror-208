import pandas as pd
from logging import Logger

from ingestion.nextgen.util.variant_table import extract_variant_table
from ingestion.nextgen.util.interpretation import map_interpretation


def calculate_status(copy_type: str, log: Logger) -> str:
    if "gain" in copy_type.lower():
        return "gain"
    elif "loss" in copy_type.lower():
        return "loss"
    else:
        log.error(f"Failed to resolve copy type: {copy_type}")
        return ""


def process_cnv(pdf_in_file: str, root_path: str, prefix: str, log: Logger):
    copy_number_path_name = f"{root_path}/{prefix}.copynumber.csv"
    sample_id = prefix

    copy_number_variant_table = extract_variant_table(pdf=pdf_in_file, variant_type="copy number")
    copy_number_variant_rows = []

    for index, row in copy_number_variant_table.iterrows():

        # Scrape gene / position
        # CDKN2C (chr1:50970354_50970512)
        positions = row["gene"].split(" ")[1]

        gene = row["gene"].split(" ")[0]
        chromosome = positions.split(":")[0].strip("(")
        start_position = positions.split(":")[1].split("_")[0]
        end_position = positions.split(":")[1].split("_")[1].strip(")")

        # Scrape status
        status = calculate_status(row["description"], log)

        # Scrape interpretation
        interpretation = map_interpretation(row["info"], log)

        # Hard-code
        # Copy number is not provided
        copy_number = 0.0
        attributes = {}

        copy_number_variant_rows.append(
            f"{sample_id},{gene},{copy_number},{status},{attributes},{chromosome},{start_position},{end_position},{interpretation}\n"
        )
    log.info(f"Saving file to {copy_number_path_name}")
    with open(copy_number_path_name, "w") as f:
        f.write(
            "sample_id,gene,copy_number,status,attributes,chromosome,start_position,end_position,interpretation\n"
        )
        for cnv_text_row in copy_number_variant_rows:
            f.write(cnv_text_row)

    return copy_number_path_name
