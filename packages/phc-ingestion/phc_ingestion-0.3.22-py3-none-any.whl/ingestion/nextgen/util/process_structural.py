import pandas as pd
from logging import Logger

from ingestion.nextgen.util.variant_table import extract_variant_table
from ingestion.nextgen.util.interpretation import map_interpretation


def process_structural(pdf_in_file: str, root_path: str, prefix: str, log: Logger):
    structural_variant_path_name = f"{root_path}/{prefix}.structural.csv"
    sample_id = prefix

    structural_variant_table = extract_variant_table(pdf=pdf_in_file, variant_type="structural")
    structural_variant_rows = []

    for index, row in structural_variant_table.iterrows():

        # Scrape gene / position
        # IGH-PPCDC (chr14:105609762;chr15:75066286)
        genes = row["gene"].split(" ")[0]
        positions = row["gene"].split(" ")[1]

        gene1 = genes.split("-")[0]
        gene2 = genes.split("-")[1]
        chromosome1 = positions.split(";")[0].split(":")[0].strip("(")
        start_position1 = positions.split(";")[0].split(":")[1]
        end_position1 = positions.split(";")[0].split(":")[1]
        chromosome2 = positions.split(";")[1].split(":")[0]
        start_position2 = positions.split(";")[1].split(":")[1].strip(")")
        end_position2 = positions.split(";")[1].split(":")[1].strip(")")

        # Scrape effect
        effect = row["type"]

        # Scrape interpretation
        interpretation = map_interpretation(row["info"], log)

        # Hard-code
        sequence_type = "Somatic"
        in_frame = "Unknown"
        attributes = {}

        structural_variant_rows.append(
            f"{sample_id},{gene1},{gene2},{effect},{chromosome1},{start_position1},{end_position1},{chromosome2},{start_position2},{end_position2},{interpretation},{sequence_type},{in_frame},{attributes}\n"
        )

    log.info(f"Saving file to {structural_variant_path_name}")
    with open(structural_variant_path_name, "w+") as f:
        f.write(
            "sample_id,gene1,gene2,effect,chromosome1,start_position1,end_position1,chromosome2,start_position2,end_position2,interpretation,sequence_type,in-frame,attributes\n"
        )
        for sv_text_row in structural_variant_rows:
            f.write(sv_text_row)

    return structural_variant_path_name
