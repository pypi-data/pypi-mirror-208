import os

from ingestion.caris.util.json import process_caris_json
from ingestion.caris.util.vcf import process_caris_vcf
from lifeomic_logging import scoped_logger


def process_caris(infile, outpath, file_name, source_file_id):
    ingest_status = {
        "exome_performed": False,
        "cnv_performed": False,
        "ihc_performed": False,
        "structural_performed": False,
        "run_instructions": {
            "som_vcf": False,
            "germ_vcf": False,
            "som_rna": False,
            "som_structural": False,
            "som_cnv": False,
        },
    }

    with scoped_logger(__name__) as log:
        os.makedirs(f"{outpath}", exist_ok=True)
        somatic_vcf_line_count = 0
        germline_vcf_line_count = 0
        result, germline_case_id, file_genome_references = process_caris_json(
            infile, outpath, file_name, source_file_id, ingest_status, log
        )
        if "somatic_vcf" in result:
            somatic_vcf_line_count = process_caris_vcf(
                result["somatic_vcf"], outpath, file_name, log
            )
        if "germline_vcf" in result:
            germline_vcf_line_count = process_caris_vcf(
                result["germline_vcf"], outpath, file_name, log
            )
        case_metadata = {
            "germline_case_id": germline_case_id,
            "somatic_vcf_line_count": somatic_vcf_line_count,
            "germline_vcf_line_count": germline_vcf_line_count,
        }

        if file_genome_references != {}:
            case_metadata.update(file_genome_references)

        return case_metadata
