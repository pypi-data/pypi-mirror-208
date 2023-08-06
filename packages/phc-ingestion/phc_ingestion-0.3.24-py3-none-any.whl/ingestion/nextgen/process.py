from enum import Enum
from lifeomic_logging import scoped_logger

from ruamel.yaml import YAML
from ingestion.nextgen.util.process_cnv import process_cnv
from ingestion.nextgen.util.process_manifest import process_manifest
from ingestion.nextgen.util.process_structural import process_structural
from ingestion.nextgen.util.process_vcf import process_vcf


def process(
    account_id: str,
    project_id: str,
    vendor_files: dict,
    local_output_dir: str,
    source_file_id: str,
    prefix: str,
    ingestion_id: str,
    phc_output_dir: str = ".lifeomic/nextgen",
) -> None:
    log_context = {
        "accountId": account_id,
        "projectId": project_id,
        "archiveFileId": source_file_id,
        "caseId": prefix,
        "ingestion_id": ingestion_id,
    }
    with scoped_logger(__name__, log_context) as log:
        cnv_path_name = process_cnv(
            pdf_in_file=vendor_files["pdfFile"],
            root_path=local_output_dir,
            prefix=prefix,
            log=log,
        )
        manifest = process_manifest(
            pdf_in_file=vendor_files["pdfFile"],
            source_file_id=source_file_id,
            prefix=prefix,
            log=log,
        )
        structural_path_name = process_structural(
            pdf_in_file=vendor_files["pdfFile"],
            root_path=local_output_dir,
            prefix=prefix,
            log=log,
        )
        somatic_vcf_meta_data = process_vcf(
            vcf_in_file=vendor_files["somaticVcfFile"],
            root_path=local_output_dir,
            prefix=prefix,
            sequence_type="somatic",
            log=log,
        )
        germline_vcf_meta_data = process_vcf(
            vcf_in_file=vendor_files["germlineVcfFile"],
            root_path=local_output_dir,
            prefix=prefix,
            sequence_type="germline",
            log=log,
        )

    manifest_path_name = f"{local_output_dir}/{prefix}.ga4gh.genomics.yml"
    log.info(f"Saving file to {manifest_path_name}")
    with open(manifest_path_name, "w") as file:
        yaml = YAML()
        yaml.dump(manifest, file)

    # Hard-code genome reference for nextgen
    genome_reference = "GRCh38"

    return {
        "manifest_path_name": manifest_path_name,
        "cnv_path_name": cnv_path_name,
        "cnv_genome_reference": genome_reference,
        "structural_path_name": structural_path_name,
        "structural_genome_reference": genome_reference,
        "somatic_vcf_meta_data": somatic_vcf_meta_data,
        "somatic_genome_reference": genome_reference,
        "germline_vcf_meta_data": germline_vcf_meta_data,
        "germline_genome_reference": genome_reference,
    }
