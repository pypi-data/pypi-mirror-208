import tempfile
from threading import local
from unittest import mock
from pathlib import Path
import unittest
import os
import csv
import logging
import shutil

from ingestion.nextgen import process
from ingestion.nextgen.util.process_manifest import process_manifest
from ingestion.nextgen.util.process_vcf import Variant, transform_vcf, process_vcf
from ingestion.nextgen.util.process_structural import process_structural
from ingestion.nextgen.util.process_cnv import process_cnv

BASE_PATH = os.path.abspath(os.path.dirname(__file__))


class MockLog:
    def info(self, _: str):
        pass


mock_log = MockLog()

files = {
    "somaticVcfFile": f"{BASE_PATH}/resources/Fankhauser_PA33390-BM2_output-tnscope.vcf.gz",
    "germlineVcfFile": f"{BASE_PATH}/resources/Fankhauser_PA33390-S2_output-dnascope.vcf.gz",
    "pdfFile": f"{BASE_PATH}/resources/RPT28095.pdf",
    "somaticBamFile": f"{BASE_PATH}/resources/Fankhauser_PA33390-BM2_recal.bam",
    "germlineBamFile": f"{BASE_PATH}/resources/Fankhauser_PA33390-S2_recal.bam.bai",
    "xmlFile": f"{BASE_PATH}/resources/RPT28095.xml",
}


def test_process():
    local_output_dir = f"{tempfile.TemporaryDirectory().name}/PA33391"
    os.makedirs(local_output_dir, exist_ok=True)
    response = process(
        account_id="account-id",
        project_id="project-id",
        vendor_files=files,
        local_output_dir=local_output_dir,
        source_file_id="archive_file_id",
        ingestion_id="ingestion-id",
        prefix="PA33391",
    )

    assert response == {
        "manifest_path_name": f"{local_output_dir}/PA33391.ga4gh.genomics.yml",
        "cnv_path_name": f"{local_output_dir}/PA33391.copynumber.csv",
        "cnv_genome_reference": "GRCh38",
        "structural_path_name": f"{local_output_dir}/PA33391.structural.csv",
        "structural_genome_reference": "GRCh38",
        "somatic_vcf_meta_data": {
            "vcf_path_name": f"{local_output_dir}/PA33391.modified.somatic.vcf.gz",
            "vcf_line_count": 1256226,
        },
        "somatic_genome_reference": "GRCh38",
        "germline_vcf_meta_data": {
            "vcf_path_name": f"{local_output_dir}/PA33391.modified.germline.vcf.gz",
            "vcf_line_count": 5462,
        },
        "germline_genome_reference": "GRCh38",
    }
    resulting_files = [path.name for path in Path(f"{local_output_dir}").iterdir()]
    assert "PA33391.copynumber.csv" in resulting_files
    assert "PA33391.ga4gh.genomics.yml" in resulting_files
    assert "PA33391.structural.csv" in resulting_files
    assert "PA33391.modified.somatic.vcf.gz" in resulting_files
    assert "PA33391.modified.germline.vcf.gz" in resulting_files


def test_transform_somatic_vcf():
    headers = [
        "##fileformat=VCFv4.2",
        "#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	Fankhauser_PA33390-TEST",
    ]

    # Test Variant Class somatic transformations
    somatic_variant = [
        "chr1\t16536006\t.\tT\tC\t21.01\tPASS\tECNT=3;FS=0.000\tGT:AD:AF:AFDP\t0/1:2,2:0.5:4"
    ]

    split_var = somatic_variant[0].split("\t")
    chr_pos = f"{split_var[0]} {split_var[1]}"
    info = split_var[7].split(";")
    frmt = split_var[8].split(":")
    smpl = split_var[9].split(":")
    working_s_var = Variant([chr_pos, info, frmt, smpl])

    working_s_var.move_af_value()
    assert working_s_var.info == ["AF=0.5000"]

    working_s_var.afdp_to_dp()
    assert working_s_var.frmt == ["GT", "AD", "AF", "DP"]

    working_s_var.prune_var()
    assert working_s_var.pruned_info == "AF=0.5000"
    assert working_s_var.pruned_frmt == "GT:AD:DP"
    assert working_s_var.pruned_smpl == "0/1:2,2:4"

    # Full somatic transform test
    somatic_variants = [
        "chr8	127837042	.	C	T	0.00	t_lod_fstar	ECNT=34;FS=0.000;HCNT=1;MAX_ED=280;MIN_ED=9;NLOD=0.00;NLODF=0.00;SOR=0.647;TLOD=1.43	GT:AD:AF:AFDP:ALTHC:ALT_F1R2:ALT_F2R1:BaseQRankSumPS:ClippingRankSumPS:DPHC:FOXOG:MQRankSumPS:NBQPS:QSS:REF_F1R2:REF_F2R1:ReadPosEndDistPS:ReadPosRankSumPS	0/1:1976,2:0.00101112:1978:2:2:0:0.085:0.000:1973:0.000:0.000:25.000:49225,50:1018:958:32.886:-0.440",
        "chr12	39978764	.	C	T	15.88	PASS	ECNT=1;FS=0.000;HCNT=1;MAX_ED=.;MIN_ED=.;NLOD=0.00;NLODF=0.00;SOR=1.179;TLOD=7.88	GT:AD:AF:AFDP:ALTHC:ALT_F1R2:ALT_F2R1:DPHC:FOXOG:NBQPS:QSS:REF_F1R2:REF_F2R1:ReadPosEndDistPS	0/1:0,3:1:3:3:1:2:3:0.667:25.000:0,75:0:0:32.000",
    ]

    new_somatic_vcf = transform_vcf(
        vcf_in_file="test",
        headers=headers,
        variants=somatic_variants,
        sequence_type="somatic",
        log=mock_log,
    )
    assert new_somatic_vcf == str(
        """##fileformat=VCFv4.2
##INFO=<ID=AF,Number=A,Type=Float,Description="Allele frequency, for each ALT allele, in the same order as listed">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Read depth">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	Fankhauser_PA33390-TEST
chr8	127837042	.	C	T	0.00	t_lod_fstar	AF=0.0010	GT:AD:DP	0/1:1976,2:1978
chr12	39978764	.	C	T	15.88	PASS	AF=1.0000	GT:AD:DP	0/1:0,3:3
"""
    )


def test_transform_germline_vcf():
    headers = [
        "##fileformat=VCFv4.2",
        "#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	Fankhauser_PA33390-TEST",
    ]

    # Test Variant Class germline transformations
    germline_variant = [
        "chr1\t16536006\t.\tT\tC\t21.01\tPASS\tECNT=3;FS=0.000;AF=1\tGT:AD:DP:GQ\t0/1:2,19:21:39",
    ]
    split_var = germline_variant[0].split("\t")
    chr_pos = f"{split_var[0]} {split_var[1]}"
    info = split_var[7].split(";")
    frmt = split_var[8].split(":")
    smpl = split_var[9].split(":")
    working_g_var = Variant([chr_pos, info, frmt, smpl])

    working_g_var.calculate_af()
    assert working_g_var.info == ["AF=0.9048"]

    working_g_var.prune_var()
    assert working_g_var.pruned_info == "AF=0.9048"
    assert working_g_var.pruned_frmt == "GT:AD:DP"
    assert working_g_var.pruned_smpl == "0/1:2,19:21"

    # Full germline transform test
    # Normal + multiallelic
    germline_variants = [
        "chr1	1349560	.	A	C	62.74	.	AC=2;AF=1;AN=2;DP=2;ExcessHet=3.0103;FS=0.000;MLEAC=2;MLEAF=1;MQ=60.00;QD=31.37;SOR=0.693	GT:AD:DP:GQ:PGT:PID:PL	1/1:0,2:2:6:0|1:1349554_A_C:90,6,0",
        "chr2	17727505	.	TTATA	T,TTA	374.73	.	AC=1,1;AF=0.5,0.5;AN=2;DP=11;ExcessHet=3.0103;FS=0.000;MLEAC=1,1;MLEAF=0.5,0.5;MQ=60.00;QD=34.07;SOR=0.859	GT:AD:DP:GQ:PL	1/2:0,7,4:11:98:412,119,98,227,0,197",
    ]
    new_germline_vcf = transform_vcf(
        vcf_in_file="test",
        headers=headers,
        variants=germline_variants,
        sequence_type="germline",
        log=mock_log,
    )
    assert new_germline_vcf == str(
        """##fileformat=VCFv4.2
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	Fankhauser_PA33390-TEST
chr1	1349560	.	A	C	62.74	.	AF=1.0000	GT:AD:DP	1/1:0,2:2
chr2	17727505	.	TTATA	T,TTA	374.73	.	AF=0.6364,0.3636	GT:AD:DP	1/2:0,7,4:11
"""
    )


class VcfErrors(unittest.TestCase):
    def test_transform_vcf_errors(self):
        headers = [
            "##fileformat=VCFv4.2",
            "##reference=file:///N/project/DG_Multiple_Myeloma/GoldenHelix/Secondary-Analysis/resources/hg38/Homo_sapiens_assembly38.fasta",
            "#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	Fankhauser_PA33390-TEST",
        ]

        with self.assertRaises(RuntimeError) as cm:
            # RuntimeError for bad VCF format
            variants_bad_columns = [
                "chr1\t16536006\t.\tT\tC\t21.01\tPASS\tECNT=3;FS=0.000\tGT:AD:AF:AFDP\t0/1:2,2:0.5:4",
                "chr1\t16536007\t.\tA\tG\t21.01\tPASS\tECNT=3;FS=0.000",
            ]
            transform_vcf(
                vcf_in_file="TEST",
                headers=headers,
                variants=variants_bad_columns,
                sequence_type="somatic",
                log=mock_log,
            )
        self.assertTrue(
            f"Variant does not contain correct number of fields. Should be 10 when 8 were detected: chr1\t16536007"
            in str(cm.exception)
        )

        with self.assertRaises(RuntimeError) as cm:
            # RuntimeError for bad AF - somatic
            variants_bad_af = [
                "chr1\t16536006\t.\tT\tC\t21.01\tPASS\tECNT=3;FS=0.000\tGT:AD:AF:AFDP\t0/1:2,2:0.5:4",
                "chr1\t16536007\t.\tA\tG\t21.01\tPASS\tECNT=3;FS=0.000\tGT:AD:AFDP\t0/1:2,2:4",
            ]
            transform_vcf(
                vcf_in_file="TEST",
                headers=headers,
                variants=variants_bad_af,
                sequence_type="somatic",
                log=mock_log,
            )
        self.assertTrue("Failed to find AF for variant: chr1 16536007" in str(cm.exception))

        with self.assertRaises(RuntimeError) as cm:
            # RuntimeError for bad AFDP - somatic
            variants_bad_afdp = [
                "chr1\t16536006\t.\tT\tC\t21.01\tPASS\tECNT=3;FS=0.000\tGT:AD:AF:AFDP\t0/1:2,2:0.5:4",
                "chr1\t16536007\t.\tA\tG\t21.01\tPASS\tECNT=3;FS=0.000\tGT:AD:AF\t0/1:2,2:0.5",
            ]
            transform_vcf(
                vcf_in_file="TEST",
                headers=headers,
                variants=variants_bad_afdp,
                sequence_type="somatic",
                log=mock_log,
            )
        self.assertTrue("Failed to find AFDP for variant: chr1 16536007" in str(cm.exception))

        with self.assertRaises(RuntimeError) as cm:
            # RuntimeError for bad AD - germline
            variants_bad_ad = [
                "chr1\t16536006\t.\tT\tC\t21.01\tPASS\tECNT=3;FS=0.000;AF=1\tGT:AD:DP\t0/1:2,19:21",
                "chr1\t16536007\t.\tT\tC\t21.01\tPASS\tECNT=3;FS=0.000;AF=1\tGT:DP\t0/1:21",
            ]
            transform_vcf(
                vcf_in_file="TEST",
                headers=headers,
                variants=variants_bad_ad,
                sequence_type="germline",
                log=mock_log,
            )
        self.assertTrue("Failed to find AD for variant: chr1 16536007" in str(cm.exception))


class VcfLogs(unittest.TestCase):
    def test_process_vcf_logs(self):
        empty_vcf = f"{BASE_PATH}/resources/empty.vcf.gz"
        headers_only_vcf = f"{BASE_PATH}/resources/no_variants.vcf.gz"
        test_log = logging.getLogger()

        with self.assertLogs(test_log) as cm:
            # Logging / Line Count if VCF empty
            result = process_vcf(
                vcf_in_file=empty_vcf,
                root_path=f"{BASE_PATH}/resources",
                prefix="test",
                sequence_type="somatic",
                log=test_log,
            )
            self.assertEqual(
                cm.output,
                [
                    f"ERROR:root:Input VCF file {empty_vcf} is empty",
                    f"INFO:root:Copying file to {BASE_PATH}/resources/test.modified.somatic.vcf.gz",
                ],
            )
            assert result == {
                "vcf_path_name": f"{BASE_PATH}/resources/test.modified.somatic.vcf.gz",
                "vcf_line_count": 0,
            }
            os.remove(f"{BASE_PATH}/resources/test.modified.somatic.vcf.gz")

        with self.assertLogs(test_log) as cm:
            # Logging / Line Count if VCF headers only
            result = process_vcf(
                vcf_in_file=headers_only_vcf,
                root_path=f"{BASE_PATH}/resources",
                prefix="test",
                sequence_type="germline",
                log=test_log,
            )
            self.assertEqual(
                cm.output,
                [
                    f"ERROR:root:Input VCF file {headers_only_vcf} contains headers but no variants",
                    f"INFO:root:Copying file to {BASE_PATH}/resources/test.modified.germline.vcf.gz",
                ],
            )
            assert result == {
                "vcf_path_name": f"{BASE_PATH}/resources/test.modified.germline.vcf.gz",
                "vcf_line_count": 5,
            }
            os.remove(f"{BASE_PATH}/resources/test.modified.germline.vcf.gz")


def test_process_structural():
    mock_log = MockLog()

    structural_path = process_structural(
        pdf_in_file=f"{BASE_PATH}/resources/RPT28095.pdf",
        root_path=BASE_PATH,
        prefix="PA33390",
        log=mock_log,
    )

    assert structural_path == f"{BASE_PATH}/PA33390.structural.csv"

    with open(f"{BASE_PATH}/PA33390.structural.csv", newline="") as test_in:
        csv_reader = csv.reader(test_in)
        test_data = list(csv_reader)

        # Check header is correct
        assert test_data[0] == [
            "sample_id",
            "gene1",
            "gene2",
            "effect",
            "chromosome1",
            "start_position1",
            "end_position1",
            "chromosome2",
            "start_position2",
            "end_position2",
            "interpretation",
            "sequence_type",
            "in-frame",
            "attributes",
        ]
        # Check scraping is correct
        assert test_data[1] == [
            "PA33390",
            "IGH",
            "PPCDC",
            "Translocation",
            "chr14",
            "105609762",
            "105609762",
            "chr15",
            "75066286",
            "75066286",
            "Uncertain significance",
            "Somatic",
            "Unknown",
            "{}",
        ]

        os.remove(f"{BASE_PATH}/PA33390.structural.csv")


def test_process_copy_number():
    mock_log = MockLog()

    cnv_path = process_cnv(
        pdf_in_file=f"{BASE_PATH}/resources/RPT28095.pdf",
        root_path=BASE_PATH,
        prefix="PA33390",
        log=mock_log,
    )

    assert cnv_path == f"{BASE_PATH}/PA33390.copynumber.csv"

    with open(f"{BASE_PATH}/PA33390.copynumber.csv", newline="") as test_in:
        csv_reader = csv.reader(test_in)
        test_data = list(csv_reader)

        # Check header is correct
        assert test_data[0] == [
            "sample_id",
            "gene",
            "copy_number",
            "status",
            "attributes",
            "chromosome",
            "start_position",
            "end_position",
            "interpretation",
        ]
        # Check scraping is correct for loss
        assert test_data[1] == [
            "PA33390",
            "CDKN2C",
            "0.0",
            "loss",
            "{}",
            "chr1",
            "50970354",
            "50970512",
            "Pathogenic",
        ]

        # Check scraping is correct for gain
        assert test_data[2] == [
            "PA33390",
            "CKS1B",
            "0.0",
            "gain",
            "{}",
            "chr1",
            "154978700",
            "154978800",
            "Pathogenic",
        ]

        os.remove(f"{BASE_PATH}/PA33390.copynumber.csv")


def test_process_manifest():
    mock_log = MockLog()

    manifest = process_manifest(
        pdf_in_file=f"{BASE_PATH}/resources/RPT28095.pdf",
        source_file_id="source-file-id",
        prefix="PA33390",
        log=mock_log,
    )

    assert manifest == {
        "testType": "NextGen",
        "name": "IU Diagnostic Genomics",
        "reference": "GRCh38",
        "ihcTests": [],
        "tumorTypePredictions": [],
        "orderingMDNPI": "",
        "bodySiteSystem": "http://lifeomic.com/fhir/sequence-body-site",
        "indicationSystem": "http://lifeomic.com/fhir/sequence-indication",
        "medFacilID": "",
        "medFacilName": "IU Health",
        "reportDate": "2023-03-10",
        "orderingMDName": "Abonour, Rafat",
        "reportID": "R31516",
        "indication": "Myeloma",
        "indicationDisplay": "Myeloma",
        "bodySite": "Bone Marrow",
        "bodySiteDisplay": "Bone Marrow",
        "collDate": "2023-02-13",
        "receivedDate": "2023-02-14",
        "patientInfo": {
            "firstName": "xxx",
            "lastName": "Fankhauser",
            "dob": "xxxx-xx-xx",
            "gender": "female",
            "identifiers": [
                {
                    "codingCode": "MR",
                    "codingSystem": "http://hl7.org/fhir/v2/0203",
                    "value": "xxxxxxx",
                }
            ],
        },
        "patientLastName": "Fankhauser",
        "patientDOB": "xxxx-xx-xx",
        "mrn": "xxxxxxx",
        "reportFile": ".lifeomic/nextgen/PA33390/PA33390.pdf",
        "sourceFileId": "source-file-id",
        "resources": [
            {"fileName": ".lifeomic/nextgen/PA33390/PA33390.pdf"},
            {"fileName": ".lifeomic/nextgen/PA33390/PA33390.modified.somatic.vcf.gz"},
            {"fileName": ".lifeomic/nextgen/PA33390/PA33390.modified.germline.vcf.gz"},
            {"fileName": ".lifeomic/nextgen/PA33390/PA33390.somatic.updated.bam"},
            {"fileName": ".lifeomic/nextgen/PA33390/PA33390.germline.updated.bam"},
            {"fileName": ".lifeomic/nextgen/PA33390/PA33390.xml"},
        ],
        "files": [
            {
                "fileName": ".lifeomic/nextgen/PA33390/PA33390.copynumber.csv",
                "sequenceType": "somatic",
                "type": "copyNumberVariant",
            },
            {
                "fileName": ".lifeomic/nextgen/PA33390/PA33390.structural.csv",
                "sequenceType": "somatic",
                "type": "structuralVariant",
            },
            {
                "fileName": ".lifeomic/nextgen/PA33390/PA33390.modified.somatic.vcf.gz",
                "sequenceType": "somatic",
                "type": "shortVariant",
            },
            {
                "fileName": ".lifeomic/nextgen/PA33390/PA33390.modified.germline.vcf.gz",
                "sequenceType": "germline",
                "type": "shortVariant",
            },
        ],
    }
