from curses import meta
import numpy as np
import tempfile
import json
from threading import local
from unittest import mock
import logging
import unittest
import sys
from ingestion.caris.util.metadata import (
    extract_metadata,
    get_collected_date,
    get_ihc_results,
    get_med_facil_id,
    get_med_facil_name,
    get_received_date,
    get_ordering_md_name,
    get_ordering_md_npi,
    get_report_date,
    get_report_id,
    get_physician_details,
)
from ingestion.caris.util.structural import extract_structural
from ingestion.caris.util.cnv import extract_cnv
from ingestion.caris.util.detect_genome_ref import detect_caris_gr
from ingestion.caris.util.gene_to_coords import gene_to_coords
from ingestion.caris.process import process_caris
from ingestion.caris.util.ga4gh import create_yaml
from pathlib import Path
import os
import pandas as pd


BASE_PATH = os.path.abspath(os.path.dirname(__file__))

# Sample status to perform tests without global variables.
INGEST_STATUS = {
    "exome_performed": False,
    "cnv_performed": True,
    "ihc_performed": False,
    "structural_performed": True,
    "run_instructions": {
        "som_vcf": False,
        "germ_vcf": False,
        "som_rna": False,
        "som_structural": False,
        "som_cnv": False,
    },
}


class MockLog:
    def info(self, _: str):
        pass


mock_log = MockLog()


def test_json():
    local_output_dir = tempfile.mkdtemp()
    tar_gzipped = f"{BASE_PATH}/resources/carisSample.tar.gz"
    response = process_caris(tar_gzipped, local_output_dir, "carisSample", "sourceFileId")
    assert response == {
        "cnv_genome_reference": "GRCh37",
        "expression_genome_reference": "GRCh37",
        "germline_case_id": "germline_te",
        "germline_genome_reference": "GRCh38",
        "germline_vcf_line_count": 3237,
        "somatic_genome_reference": "GRCh38",
        "somatic_vcf_line_count": 3237,
        "structural_genome_reference": "GRCh38",
    }
    resulting_files = [path.name for path in Path(f"{local_output_dir}").iterdir()]
    assert "carisSample.ga4gh.genomics.yml" in resulting_files


class TestTarHandling(unittest.TestCase):
    def test_tar_handling(self):
        local_output_dir = tempfile.mkdtemp()
        tar = f"{BASE_PATH}/resources/carisSample.tar"
        response = process_caris(tar, local_output_dir, "carisSample", "sourceFileId")
        assert response == {
            "cnv_genome_reference": "GRCh37",
            "expression_genome_reference": "GRCh37",
            "germline_case_id": "germline_te",
            "germline_genome_reference": "GRCh38",
            "germline_vcf_line_count": 3237,
            "somatic_genome_reference": "GRCh38",
            "somatic_vcf_line_count": 3237,
            "structural_genome_reference": "GRCh38",
        }
        resulting_files = [path.name for path in Path(f"{local_output_dir}").iterdir()]
        assert "carisSample.ga4gh.genomics.yml" in resulting_files

        with self.assertRaises(RuntimeError) as cm:
            unapproved_tar = f"{BASE_PATH}/resources/carisSample"
            response = process_caris(
                unapproved_tar, local_output_dir, "carisSample", "sourceFileId"
            )
            self.assertTrue(f"Wrong input format chosen for file" in str(cm.exception))


def test_extract_metadata():
    f = open(f"{BASE_PATH}/resources/TN20-779441.json", "rb")
    all_data = json.load(f)
    data = all_data
    f.close()
    metadata = extract_metadata(
        data, "unit-test", {"pdf": "unit_test.pdf"}, "sourceFileId", INGEST_STATUS, mock_log
    )

    assert metadata == {
        "testType": "MI Profile",
        "indexedDate": "2020-12-08",
        "receivedDate": "2020-12-08",
        "collDate": "2019-12-11",
        "reportDate": "2020-12-11",
        "bodySiteSystem": "http://lifeomic.com/fhir/sequence-body-site",
        "reportID": "TN20-779441",
        "mrn": "LO-CARIS-1234",
        "patientLastName": "Smith",
        "patientDOB": "1950-10-10",
        "medFacilName": "Test Account 1",
        "medFacilID": 50275,
        "orderingMDName": "Test Physician 2, Test",
        "orderingMDNPI": 123453243,
        "indicationSystem": "http://lifeomic.com/fhir/sequence-indication",
        "indication": "Undifferentiated pleomorphic sarcoma",
        "indicationDisplay": "Undifferentiated pleomorphic sarcoma",
        "bodySite": "Ear canal",
        "bodySiteDisplay": "Ear canal",
        "sourceFileId": "sourceFileId",
        "reportFile": ".lifeomic/caris/unit-test/unit_test.pdf",
        "patientInfo": {
            "lastName": "Smith",
            "dob": "1950-10-10",
            "firstName": "Jane",
            "gender": "male",
            "identifiers": [
                {
                    "codingCode": "MR",
                    "codingSystem": "http://hl7.org/fhir/v2/0203",
                    "value": "LO-CARIS-1234",
                }
            ],
        },
        "name": "Caris",
        "reference": "GRCh37",
        "tmb": "high",
        "tmbScore": 33.0,
        "msi": "stable",
        "ihcTests": [],
        "resources": [{"fileName": ".lifeomic/caris/unit-test/unit_test.pdf"}],
    }


def test_extract_structural():
    f = open(f"{BASE_PATH}/resources/TN20-779441.json", "rb")
    all_data = json.load(f)
    data = all_data
    f.close()

    metadata = extract_structural("unit-test", data, INGEST_STATUS, mock_log)

    assert metadata == {
        "fileName": ".lifeomic/caris/unit-test/unit-test.structural.csv",
        "sequenceType": "somatic",
        "type": "structuralVariant",
        "reference": "GRCh38",
    }

    structural_df = pd.read_csv("unit-test.structural.csv")
    os.remove("unit-test.structural.csv")
    assert structural_df.columns.tolist() == [
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
        "in_frame",
        "attributes",
    ]

    assert structural_df.iloc[0].tolist() == [
        "unit-test",
        "TPM3",
        "ALK",
        "Fusion",
        "chr1",
        154142876,
        154142876,
        "chr2",
        29446394,
        29446394,
        "other",
        "Somatic",
        "Yes",
        "{}",
    ]
    assert structural_df.iloc[1].tolist() == [
        "unit-test",
        "TPM3",
        "ALK",
        "Fusion",
        "chr1",
        154142876,
        154142876,
        "chr2",
        29446394,
        29446394,
        "Uncertain significance",
        "Somatic",
        "Yes",
        "{}",
    ]
    assert structural_df.iloc[2].tolist() == [
        "unit-test",
        "FAM20A",
        "PRKCA",
        "Fusion",
        "chr17",
        66596404,
        66596404,
        "chr17",
        64302214,
        64302214,
        "Likely pathogenic",
        "Somatic",
        "Yes",
        "{}",
    ]
    assert structural_df.iloc[3].tolist() == [
        "unit-test",
        "FAM20A",
        "PRKCA",
        "Fusion",
        "chr17",
        66596404,
        66596404,
        "chr17",
        64302214,
        64302214,
        "Pathogenic",
        "Somatic",
        "Yes",
        "{}",
    ]
    assert structural_df.iloc[4].tolist() == [
        "unit-test",
        "EWSR1",
        "OSBP2",
        "Fusion",
        "chr22",
        29683123,
        29683123,
        "chr22",
        31266416,
        31266416,
        "Uncertain significance",
        "Somatic",
        "Unknown",
        "{}",
    ]


def test_extract_cnv():
    data = {
        "tests": [
            {
                "testName": "Exome CNA Panel - Additional Genes",
                "testCode": "CMI1125",
                "platformTechnology": "Exome CNA",
                "testMethodology": "CNA-Seq",
                "testResults": [
                    {
                        "copyNumberAlteration": {
                            "resultCount": "1",
                            "biomarkerName": "ABL1",
                            "gene": "ABL1",
                            "result": "intermediate",
                            "result_group": "No Result",
                            "chromosome": "chr1",
                            "genomicCoordinates": "ABL1:chr1:169076834-169112236",
                            "genomeBuild": "GRCh38/hg38",
                            "genomicSource": "Somatic",
                            "copyNumberType": "intermediate",
                            "copyNumber": "4.10",
                            "dbVarID": "",
                            "interpretation": "",
                            "labSpecific": {
                                "analysisConfigurationName": "NGS5_Exome",
                                "analysisConfigurationVersion": "5.2.5.1",
                                "analysisPipelineName": "NGS",
                                "analysisPipelineVersion": "2.1.3",
                                "NGSPanelName": "Illumina",
                                "NGSPanelVersion": "V12",
                            },
                        }
                    },
                    {
                        "copyNumberAlteration": {
                            "resultCount": "1",
                            "biomarkerName": "ABL1",
                            "gene": "ABL1",
                            "result": "intermediate",
                            "result_group": "No Result",
                            "chromosome": "chr1",
                            "genomicCoordinates": "ABL1:chr1:169076834-169112236",
                            "genomeBuild": "GRCh38/hg38",
                            "genomicSource": "Somatic",
                            "copyNumberType": "intermediate",
                            "copyNumber": "14.10",
                            "dbVarID": "",
                            "interpretation": "",
                            "labSpecific": {
                                "analysisConfigurationName": "NGS5_Exome",
                                "analysisConfigurationVersion": "5.2.5.1",
                                "analysisPipelineName": "NGS",
                                "analysisPipelineVersion": "2.1.3",
                                "NGSPanelName": "Illumina",
                                "NGSPanelVersion": "V12",
                            },
                        }
                    },
                    {
                        "copyNumberAlteration": {
                            "resultCount": "1",
                            "biomarkerName": "ABL1",
                            "gene": "ABL1",
                            "result": "intermediate",
                            "result_group": "wild type",
                            "chromosome": "chr1",
                            "genomicCoordinates": "ABL1:chr1:169076834-169112236",
                            "genomeBuild": "GRCh38/hg38",
                            "genomicSource": "Somatic",
                            "copyNumberType": "intermediate",
                            "copyNumber": "0.10",
                            "dbVarID": "",
                            "interpretation": "",
                            "labSpecific": {
                                "analysisConfigurationName": "NGS5_Exome",
                                "analysisConfigurationVersion": "5.2.5.1",
                                "analysisPipelineName": "NGS",
                                "analysisPipelineVersion": "2.1.3",
                                "NGSPanelName": "Illumina",
                                "NGSPanelVersion": "V12",
                            },
                        }
                    },
                    {
                        "copyNumberAlteration": {
                            "resultCount": "1",
                            "biomarkerName": "ABL1",
                            "gene": "ABL1",
                            "result": "intermediate",
                            "result_group": "No Result",
                            "chromosome": "chr1",
                            "genomicCoordinates": "ABL1:chr1:169076834-169112236",
                            "genomeBuild": "GRCh38/hg38",
                            "genomicSource": "Somatic",
                            "copyNumberType": "intermediate",
                            "copyNumber": "",
                            "dbVarID": "",
                            "interpretation": "",
                            "labSpecific": {
                                "analysisConfigurationName": "NGS5_Exome",
                                "analysisConfigurationVersion": "5.2.5.1",
                                "analysisPipelineName": "NGS",
                                "analysisPipelineVersion": "2.1.3",
                                "NGSPanelName": "Illumina",
                                "NGSPanelVersion": "V12",
                            },
                        }
                    },
                ],
            }
        ]
    }

    metadata = extract_cnv("unit-test", data, INGEST_STATUS, mock_log)
    f = open("unit-test.copynumber.csv", "r")
    result = f.read().splitlines()
    f.close()
    os.remove("unit-test.copynumber.csv")
    assert result == [
        "sample_id,gene,copy_number,status,attributes,chromosome,start_position,end_position,interpretation",
        "unit-test,ABL1,4.10,gain,{},chr1,169076834,169112236,Uncertain significance",
        "unit-test,ABL1,14.10,amplification,{},chr1,169076834,169112236,Uncertain significance",
        "unit-test,ABL1,0.10,loss,{},chr1,169076834,169112236,other",
    ]


def test_extract_cnv_del():
    data = {
        "tests": [
            {
                "testName": "Exome CND Panel - Additional Genes",
                "testCode": "CMI1125",
                "platformTechnology": "Exome CNA",
                "testMethodology": "CNA-Seq",
                "testResults": [
                    {
                        "copyNumberAlteration": {
                            "resultCount": "1",
                            "biomarkerName": "ABL1",
                            "gene": "ABL1",
                            "result": "Deleted",
                            "result_group": "Mutated",
                            "genomeBuild": "GRCh38/hg38",
                            "genomicSource": "Somatic",
                            "copyNumberType": "Deleted",
                            "copyNumber": "0.15",
                            "dbVarID": "",
                            "interpretation": "",
                            "labSpecific": {
                                "analysisConfigurationName": "NGS5_Exome",
                                "analysisConfigurationVersion": "5.2.6.3",
                                "analysisPipelineName": "NGS5",
                                "analysisPipelineVersion": "V5.2.8.3",
                                "NGSPanelName": "SureSelect_ExomeV7_plus_720G",
                                "NGSPanelVersion": "V12.0",
                            },
                        }
                    },
                ],
            }
        ]
    }

    metadata = extract_cnv("unit-test", data, INGEST_STATUS, mock_log)
    f = open("unit-test.copynumber.csv", "r")
    result = f.read().splitlines()
    f.close()
    os.remove("unit-test.copynumber.csv")
    assert result == [
        "sample_id,gene,copy_number,status,attributes,chromosome,start_position,end_position,interpretation",
        "unit-test,ABL1,0.15,loss,{},chr9,133588430,133763062,Pathogenic",
    ]


def test_handle_equivocal():
    f = open(f"{BASE_PATH}/resources/TN20-779441_equivocal.json", "rb")
    all_data = json.load(f)
    data = all_data
    f.close()
    metadata = extract_metadata(
        data, "unit-test", {"pdf": "unit_test.pdf"}, "sourceFileId", INGEST_STATUS, mock_log
    )

    assert metadata == {
        "testType": "MI Profile",
        "indexedDate": "2020-12-08",
        "receivedDate": "2020-12-08",
        "collDate": "2019-12-11",
        "reportDate": "2020-12-11",
        "bodySiteSystem": "http://lifeomic.com/fhir/sequence-body-site",
        "reportID": "TN20-779441",
        "mrn": "LO-CARIS-1234",
        "patientLastName": "Smith",
        "patientDOB": "1950-10-10",
        "medFacilName": "Test Account 1",
        "medFacilID": 50275,
        "orderingMDName": "Test Physician 2, Test",
        "orderingMDNPI": 123453243,
        "indicationSystem": "http://lifeomic.com/fhir/sequence-indication",
        "indication": "Undifferentiated pleomorphic sarcoma",
        "indicationDisplay": "Undifferentiated pleomorphic sarcoma",
        "bodySite": "Ear canal",
        "bodySiteDisplay": "Ear canal",
        "sourceFileId": "sourceFileId",
        "reportFile": ".lifeomic/caris/unit-test/unit_test.pdf",
        "patientInfo": {
            "lastName": "Smith",
            "dob": "1950-10-10",
            "firstName": "Jane",
            "gender": "male",
            "identifiers": [
                {
                    "codingCode": "MR",
                    "codingSystem": "http://hl7.org/fhir/v2/0203",
                    "value": "LO-CARIS-1234",
                }
            ],
        },
        "name": "Caris",
        "reference": "GRCh37",
        "tmb": "high",
        "tmbScore": 33.0,
        "msi": "indeterminate",
        "ihcTests": [],
        "resources": [{"fileName": ".lifeomic/caris/unit-test/unit_test.pdf"}],
    }


def test_handle_msi_unknown():
    f = open(f"{BASE_PATH}/resources/TN20-779441_msi_foo.json", "rb")
    all_data = json.load(f)
    data = all_data
    f.close()
    metadata = extract_metadata(
        data, "unit-test", {"pdf": "unit_test.pdf"}, "sourceFileId", INGEST_STATUS, mock_log
    )

    assert metadata == {
        "testType": "MI Profile",
        "indexedDate": "2020-12-08",
        "receivedDate": "2020-12-08",
        "collDate": "2019-12-11",
        "reportDate": "2020-12-11",
        "bodySiteSystem": "http://lifeomic.com/fhir/sequence-body-site",
        "reportID": "TN20-779441",
        "mrn": "LO-CARIS-1234",
        "patientLastName": "Smith",
        "patientDOB": "1950-10-10",
        "medFacilName": "Test Account 1",
        "medFacilID": 50275,
        "orderingMDName": "Test Physician 2, Test",
        "orderingMDNPI": 123453243,
        "indicationSystem": "http://lifeomic.com/fhir/sequence-indication",
        "indication": "Undifferentiated pleomorphic sarcoma",
        "indicationDisplay": "Undifferentiated pleomorphic sarcoma",
        "bodySite": "Ear canal",
        "bodySiteDisplay": "Ear canal",
        "sourceFileId": "sourceFileId",
        "reportFile": ".lifeomic/caris/unit-test/unit_test.pdf",
        "patientInfo": {
            "lastName": "Smith",
            "dob": "1950-10-10",
            "firstName": "Jane",
            "gender": "male",
            "identifiers": [
                {
                    "codingCode": "MR",
                    "codingSystem": "http://hl7.org/fhir/v2/0203",
                    "value": "LO-CARIS-1234",
                }
            ],
        },
        "name": "Caris",
        "reference": "GRCh37",
        "tmb": "high",
        "tmbScore": 151.0,
        "msi": "foo",
        "ihcTests": [],
        "resources": [{"fileName": ".lifeomic/caris/unit-test/unit_test.pdf"}],
    }


def test_handle_empty_test():
    f = open(f"{BASE_PATH}/resources/TN20-779441_empty_test.json", "rb")
    all_data = json.load(f)
    data = all_data
    f.close()
    metadata = extract_metadata(
        data, "unit-test", {"pdf": "unit_test.pdf"}, "sourceFileId", INGEST_STATUS, mock_log
    )

    print(metadata)
    assert metadata == {
        "testType": "MI Profile",
        "indexedDate": "2020-12-08",
        "receivedDate": "2020-12-08",
        "collDate": "2019-12-11",
        "reportDate": "2020-12-11",
        "bodySiteSystem": "http://lifeomic.com/fhir/sequence-body-site",
        "reportID": "TN20-779441",
        "mrn": "LO-CARIS-1234",
        "patientLastName": "Smith",
        "patientDOB": "1950-10-10",
        "medFacilName": "Test Account 1",
        "medFacilID": 50275,
        "orderingMDName": "Test Physician 2, Test",
        "orderingMDNPI": 123453243,
        "indicationSystem": "http://lifeomic.com/fhir/sequence-indication",
        "indication": "Undifferentiated pleomorphic sarcoma",
        "indicationDisplay": "Undifferentiated pleomorphic sarcoma",
        "bodySite": "Ear canal",
        "bodySiteDisplay": "Ear canal",
        "sourceFileId": "sourceFileId",
        "reportFile": ".lifeomic/caris/unit-test/unit_test.pdf",
        "patientInfo": {
            "lastName": "Smith",
            "dob": "1950-10-10",
            "firstName": "Jane",
            "gender": "male",
            "identifiers": [
                {
                    "codingCode": "MR",
                    "codingSystem": "http://hl7.org/fhir/v2/0203",
                    "value": "LO-CARIS-1234",
                }
            ],
        },
        "name": "Caris",
        "reference": "GRCh37",
        "ihcTests": [],
        "resources": [{"fileName": ".lifeomic/caris/unit-test/unit_test.pdf"}],
    }


def test_equivocal_status():
    f = open(f"{BASE_PATH}/resources/TN20-779441_equivocal_status.json", "rb")
    all_data = json.load(f)
    data = all_data
    f.close()
    metadata = extract_metadata(
        data, "unit-test", {"pdf": "unit_test.pdf"}, "sourceFileId", INGEST_STATUS, mock_log
    )
    assert metadata == {
        "testType": "MI Profile",
        "indexedDate": "2020-12-08",
        "receivedDate": "2020-12-08",
        "collDate": "2019-12-11",
        "reportDate": "2020-12-11",
        "bodySiteSystem": "http://lifeomic.com/fhir/sequence-body-site",
        "reportID": "TN20-779441",
        "mrn": "LO-CARIS-1234",
        "patientLastName": "Smith",
        "patientDOB": "1950-10-10",
        "medFacilName": "Test Account 1",
        "medFacilID": 50275,
        "orderingMDName": "Test Physician 2, Test",
        "orderingMDNPI": 123453243,
        "indicationSystem": "http://lifeomic.com/fhir/sequence-indication",
        "indication": "Undifferentiated pleomorphic sarcoma",
        "indicationDisplay": "Undifferentiated pleomorphic sarcoma",
        "bodySite": "Ear canal",
        "bodySiteDisplay": "Ear canal",
        "sourceFileId": "sourceFileId",
        "reportFile": ".lifeomic/caris/unit-test/unit_test.pdf",
        "patientInfo": {
            "lastName": "Smith",
            "dob": "1950-10-10",
            "firstName": "Jane",
            "gender": "male",
            "identifiers": [
                {
                    "codingCode": "MR",
                    "codingSystem": "http://hl7.org/fhir/v2/0203",
                    "value": "LO-CARIS-1234",
                }
            ],
        },
        "name": "Caris",
        "reference": "GRCh37",
        "lossOfHeterozygosityScore": 11,
        "lossOfHeterozygosityStatus": "equivocal",
        "ihcTests": [],
        "resources": [{"fileName": ".lifeomic/caris/unit-test/unit_test.pdf"}],
    }


def test_high_status():
    f = open(f"{BASE_PATH}/resources/TN20-779441_high.json", "rb")
    all_data = json.load(f)
    data = all_data
    f.close()
    metadata = extract_metadata(
        data, "unit-test", {"pdf": "unit_test.pdf"}, "sourceFileId", INGEST_STATUS, mock_log
    )

    assert metadata == {
        "testType": "MI Profile",
        "indexedDate": "2020-12-08",
        "receivedDate": "2020-12-08",
        "collDate": "2019-12-11",
        "reportDate": "2020-12-11",
        "bodySiteSystem": "http://lifeomic.com/fhir/sequence-body-site",
        "reportID": "TN20-779441",
        "mrn": "LO-CARIS-1234",
        "patientLastName": "Smith",
        "patientDOB": "1950-10-10",
        "medFacilName": "Test Account 1",
        "medFacilID": 50275,
        "orderingMDName": "Test Physician 2, Test",
        "orderingMDNPI": 123453243,
        "indicationSystem": "http://lifeomic.com/fhir/sequence-indication",
        "indication": "Undifferentiated pleomorphic sarcoma",
        "indicationDisplay": "Undifferentiated pleomorphic sarcoma",
        "bodySite": "Ear canal",
        "bodySiteDisplay": "Ear canal",
        "sourceFileId": "sourceFileId",
        "reportFile": ".lifeomic/caris/unit-test/unit_test.pdf",
        "patientInfo": {
            "lastName": "Smith",
            "dob": "1950-10-10",
            "firstName": "Jane",
            "gender": "male",
            "identifiers": [
                {
                    "codingCode": "MR",
                    "codingSystem": "http://hl7.org/fhir/v2/0203",
                    "value": "LO-CARIS-1234",
                }
            ],
        },
        "name": "Caris",
        "reference": "GRCh37",
        "lossOfHeterozygosityScore": 11,
        "lossOfHeterozygosityStatus": "high",
        "ihcTests": [],
        "resources": [{"fileName": ".lifeomic/caris/unit-test/unit_test.pdf"}],
    }


def test_qns_long_status():
    f = open(f"{BASE_PATH}/resources/TN20-779441_qns_long.json", "rb")
    all_data = json.load(f)
    data = all_data
    f.close()
    metadata = extract_metadata(
        data, "unit-test", {"pdf": "unit_test.pdf"}, "sourceFileId", INGEST_STATUS, mock_log
    )

    assert metadata == {
        "testType": "MI Profile",
        "indexedDate": "2020-12-08",
        "receivedDate": "2020-12-08",
        "collDate": "2019-12-11",
        "reportDate": "2020-12-11",
        "bodySiteSystem": "http://lifeomic.com/fhir/sequence-body-site",
        "reportID": "TN20-779441",
        "mrn": "LO-CARIS-1234",
        "patientLastName": "Smith",
        "patientDOB": "1950-10-10",
        "medFacilName": "Test Account 1",
        "medFacilID": 50275,
        "orderingMDName": "Test Physician 2, Test",
        "orderingMDNPI": 123453243,
        "indicationSystem": "http://lifeomic.com/fhir/sequence-indication",
        "indication": "Undifferentiated pleomorphic sarcoma",
        "indicationDisplay": "Undifferentiated pleomorphic sarcoma",
        "bodySite": "Ear canal",
        "bodySiteDisplay": "Ear canal",
        "sourceFileId": "sourceFileId",
        "reportFile": ".lifeomic/caris/unit-test/unit_test.pdf",
        "patientInfo": {
            "lastName": "Smith",
            "dob": "1950-10-10",
            "firstName": "Jane",
            "gender": "male",
            "identifiers": [
                {
                    "codingCode": "MR",
                    "codingSystem": "http://hl7.org/fhir/v2/0203",
                    "value": "LO-CARIS-1234",
                }
            ],
        },
        "name": "Caris",
        "reference": "GRCh37",
        "lossOfHeterozygosityScore": 11,
        "lossOfHeterozygosityStatus": "qns",
        "ihcTests": [],
        "resources": [{"fileName": ".lifeomic/caris/unit-test/unit_test.pdf"}],
    }


def test_qns_status():
    f = open(f"{BASE_PATH}/resources/TN20-779441_qns.json", "rb")
    all_data = json.load(f)
    data = all_data
    f.close()
    metadata = extract_metadata(
        data, "unit-test", {"pdf": "unit_test.pdf"}, "sourceFileId", INGEST_STATUS, mock_log
    )

    assert metadata == {
        "testType": "MI Profile",
        "indexedDate": "2020-12-08",
        "receivedDate": "2020-12-08",
        "collDate": "2019-12-11",
        "reportDate": "2020-12-11",
        "bodySiteSystem": "http://lifeomic.com/fhir/sequence-body-site",
        "reportID": "TN20-779441",
        "mrn": "LO-CARIS-1234",
        "patientLastName": "Smith",
        "patientDOB": "1950-10-10",
        "medFacilName": "Test Account 1",
        "medFacilID": 50275,
        "orderingMDName": "Test Physician 2, Test",
        "orderingMDNPI": 123453243,
        "indicationSystem": "http://lifeomic.com/fhir/sequence-indication",
        "indication": "Undifferentiated pleomorphic sarcoma",
        "indicationDisplay": "Undifferentiated pleomorphic sarcoma",
        "bodySite": "Ear canal",
        "bodySiteDisplay": "Ear canal",
        "sourceFileId": "sourceFileId",
        "reportFile": ".lifeomic/caris/unit-test/unit_test.pdf",
        "patientInfo": {
            "lastName": "Smith",
            "dob": "1950-10-10",
            "firstName": "Jane",
            "gender": "male",
            "identifiers": [
                {
                    "codingCode": "MR",
                    "codingSystem": "http://hl7.org/fhir/v2/0203",
                    "value": "LO-CARIS-1234",
                }
            ],
        },
        "name": "Caris",
        "reference": "GRCh37",
        "lossOfHeterozygosityScore": 11,
        "lossOfHeterozygosityStatus": "qns",
        "ihcTests": [],
        "resources": [{"fileName": ".lifeomic/caris/unit-test/unit_test.pdf"}],
    }


def test_missing_physician_info():
    f = open(f"{BASE_PATH}/resources/TN20-779441_no_phys.json", "rb")
    all_data = json.load(f)
    data = all_data
    f.close()
    metadata = extract_metadata(
        data, "unit-test", {"pdf": "unit_test.pdf"}, "sourceFileId", INGEST_STATUS, mock_log
    )

    assert metadata == {
        "testType": "MI Profile",
        "indexedDate": "2020-12-08",
        "receivedDate": "2020-12-08",
        "collDate": "2019-12-11",
        "reportDate": "2020-12-11",
        "bodySiteSystem": "http://lifeomic.com/fhir/sequence-body-site",
        "reportID": "TN20-779441",
        "mrn": "LO-CARIS-1234",
        "patientLastName": "Smith",
        "patientDOB": "1950-10-10",
        "medFacilName": "",
        "medFacilID": "",
        "orderingMDName": "",
        "orderingMDNPI": "",
        "indicationSystem": "http://lifeomic.com/fhir/sequence-indication",
        "indication": "Undifferentiated pleomorphic sarcoma",
        "indicationDisplay": "Undifferentiated pleomorphic sarcoma",
        "bodySite": "Ear canal",
        "bodySiteDisplay": "Ear canal",
        "sourceFileId": "sourceFileId",
        "reportFile": ".lifeomic/caris/unit-test/unit_test.pdf",
        "patientInfo": {
            "lastName": "Smith",
            "dob": "1950-10-10",
            "firstName": "Jane",
            "gender": "male",
            "identifiers": [
                {
                    "codingCode": "MR",
                    "codingSystem": "http://hl7.org/fhir/v2/0203",
                    "value": "LO-CARIS-1234",
                }
            ],
        },
        "name": "Caris",
        "reference": "GRCh37",
        "tmb": "high",
        "tmbScore": 33.0,
        "msi": "stable",
        "ihcTests": [],
        "resources": [{"fileName": ".lifeomic/caris/unit-test/unit_test.pdf"}],
    }


def test_get_collected_date():
    collected_test_pos = {
        "specimenID": 132456,
        "specimenType": "Tissue Biopsy Paraffin Blocks",
        "specimenAccessionID": "TN21-888143-A",
        "specimenSite": "Lower lobe, lung",
        "specimenCollectionDate": "2021-06-01",
        "specimenReceivedDate": "2021-06-16",
    }

    assert get_collected_date(collected_test_pos) == "2021-06-01"

    collected_test_neg = {
        "specimenID": 132456,
        "specimenType": "Tissue Biopsy Paraffin Blocks",
        "specimenAccessionID": "TN21-888143-A",
        "specimenSite": "Lower lobe, lung",
        "specimenReceivedDate": "2021-06-16",
    }

    assert get_collected_date(collected_test_neg) == ""


def test_get_received_date():
    received_test_pos = {
        "specimenID": 132456,
        "specimenType": "Tissue Biopsy Paraffin Blocks",
        "specimenAccessionID": "TN21-888143-A",
        "specimenSite": "Lower lobe, lung",
        "specimenCollectionDate": "2021-06-01",
        "specimenReceivedDate": "2021-06-16",
    }

    assert get_received_date(received_test_pos) == "2021-06-16"

    received_test_neg = {
        "specimenID": 132456,
        "specimenType": "Tissue Biopsy Paraffin Blocks",
        "specimenAccessionID": "TN21-888143-A",
        "specimenSite": "Lower lobe, lung",
        "specimenCollectionDate": "2021-06-01",
    }

    assert get_received_date(received_test_neg) == ""


def test_get_report_date():
    report_test_pos = {
        "labName": "Caris Life Sciences",
        "orderedDate": "2020-12-08 11:24:06.0",
        "receivedDate": "2020-12-08 11:24:06.0",
        "approvalInformation": {"approvedBy": "TN Signer", "approveDate": "2020-12-11 14:45:50.0"},
    }

    assert get_report_date(report_test_pos, mock_log) == "2020-12-11"

    report_test_neg = {
        "labName": "Caris Life Sciences",
        "orderedDate": "2020-12-08 11:24:06.0",
        "receivedDate": "2020-12-08 11:24:06.0",
        "approvalInformation": {"approvedBy": "TN Signer"},
    }

    assert get_report_date(report_test_neg, mock_log) == ""

    report_test_double_neg = {
        # Approval information completely missing
        "labName": "Caris Life Sciences",
        "orderedDate": "2020-12-08 11:24:06.0",
        "receivedDate": "2020-12-08 11:24:06.0",
    }

    assert get_report_date(report_test_double_neg, mock_log) == ""


def test_get_ordering_md_name():
    md_name_pos = {
        "npi": 123453243,
        "fullName": "First Last",
        "lastName": "Last",
        "firstName": "First",
        "middleName": "and",
        "organization": "Test Account 1",
        "sourceID": 50275,
    }

    assert get_ordering_md_name(md_name_pos) == "Last, First"

    md_name_neg = {
        "npi": 123453243,
        "fullName": "",
        "lastName": "",
        "firstName": "",
        "middleName": "and",
        "organization": "Test Account 1",
        "sourceID": 50275,
    }

    assert get_ordering_md_name(md_name_neg) == ""


def test_get_ordering_md_npi():
    md_npi_pos = {
        "npi": 123453243,
        "fullName": "First Last",
        "lastName": "Last",
        "firstName": "First",
        "middleName": "and",
        "organization": "Test Account 1",
        "sourceID": 50275,
    }

    assert get_ordering_md_npi(md_npi_pos) == 123453243

    md_npi_neg = {
        "npi": "",
        "fullName": "First Last",
        "lastName": "Last",
        "firstName": "First",
        "middleName": "and",
        "organization": "Test Account 1",
        "sourceID": 50275,
    }

    assert get_ordering_md_npi(md_npi_neg) == ""


def test_get_med_facil_name():
    med_facil_name_pos = {
        "npi": 123453243,
        "fullName": "First Last",
        "lastName": "Last",
        "firstName": "First",
        "middleName": "and",
        "organization": "Test Account 1",
        "sourceID": 50275,
    }

    assert get_med_facil_name(med_facil_name_pos) == "Test Account 1"

    med_facil_name_neg = {
        "npi": 123453243,
        "fullName": "First Last",
        "lastName": "Last",
        "firstName": "First",
        "middleName": "and",
        "organization": "",
        "sourceID": 50275,
    }

    assert get_med_facil_name(med_facil_name_neg) == ""


def test_get_med_facil_id():
    med_facil_id_pos = {
        "npi": 123453243,
        "fullName": "First Last",
        "lastName": "Last",
        "firstName": "First",
        "middleName": "and",
        "organization": "Test Account 1",
        "sourceID": 50275,
    }

    assert get_med_facil_id(med_facil_id_pos) == 50275

    med_facil_id_neg = {
        "npi": 123453243,
        "fullName": "First Last",
        "lastName": "Last",
        "firstName": "First",
        "middleName": "and",
        "organization": "Test Account 1",
        "sourceID": "",
    }

    assert get_med_facil_id(med_facil_id_neg) == ""


def test_get_report_id():
    report_id_pos = {
        "labName": "Caris Life Sciences",
        "testName": "Caris MI Profile",
        "testCode": "CMI001",
        "labReportVersion": 1.0,
        "labReportID": "TN20-779441",
        "reportType": "Final",
        "orderedDate": "2020-12-08 11:24:06.0",
        "receivedDate": "2020-12-08 11:24:06.0",
    }

    assert get_report_id(report_id_pos) == "TN20-779441"

    report_id_neg = {
        "labName": "Caris Life Sciences",
        "testName": "Caris MI Profile",
        "testCode": "CMI001",
        "labReportVersion": 1.0,
        "labReportID": "",
        "reportType": "Final",
        "orderedDate": "2020-12-08 11:24:06.0",
        "receivedDate": "2020-12-08 11:24:06.0",
    }

    assert get_report_id(report_id_neg) == ""


def test_get_physician_details():
    physician_data_pos = {
        "testDetails": {
            "labName": "Caris Life Sciences",
            "testName": "Caris MI Profile",
            "testCode": "CMI001",
        },
        "patientInformation": {
            "fullName": "Jane Smith",
            "lastName": "Smith",
            "firstName": "Jane",
        },
        "physicianInformation": {
            "npi": 123453243,
            "fullName": "Test Test Physician 2",
            "lastName": "Test Physician 2",
            "firstName": "Test",
        },
    }

    physician_details_pos = get_physician_details(physician_data_pos)
    assert physician_details_pos == {
        "npi": 123453243,
        "fullName": "Test Test Physician 2",
        "lastName": "Test Physician 2",
        "firstName": "Test",
    }

    physician_data_neg = {
        "testDetails": {
            "labName": "Caris Life Sciences",
            "testName": "Caris MI Profile",
            "testCode": "CMI001",
        },
        "patientInformation": {
            "fullName": "Jane Smith",
            "lastName": "Smith",
            "firstName": "Jane",
        },
    }

    physician_details_neg = get_physician_details(physician_data_neg)
    assert physician_details_neg == {}


def test_get_ihc_results():
    # No tests at all
    no_tests = {
        "clinicalTrials": {
            "nctID": "NCT04551885",
            "titleBrief": "FT516 in Combination With Monoclonal Antibodies in Advanced Solid Tumors",
        },
        "therapies": {"therapyName": ""},
    }
    no_test_results = get_ihc_results(no_tests, mock_log)
    assert no_test_results == []

    # Has tests, none are IHC
    no_ihc_tests = {
        "tests": [
            {
                "testName": "600 Gene Panel - Clinical Genes",
                "testCode": "CMI758",
                "platformTechnology": "NGS Q3",
                "testMethodology": "Seq",
            },
            {
                "testName": "CNA_v1 Panel",
                "testCode": "CMI948",
                "platformTechnology": "CNA",
                "testMethodology": "CNA-Seq",
            },
            {
                "testName": "Transcriptome Detection_v1 Panel",
                "testCode": "CMI1114",
                "platformTechnology": "Transcriptome",
                "testMethodology": "Seq",
            },
        ]
    }

    no_ihc_test_results = get_ihc_results(no_ihc_tests, mock_log)
    assert no_ihc_test_results == []

    # IHC test with ic / tc fields
    ihc_with_ic_tc = {
        "tests": [
            {
                "testName": "PD-L1 FDA(SP142)",
                "testCode": "CMI1099",
                "platformTechnology": "IHC",
                "testMethodology": "IHC",
                "testResults": {
                    "expressionAlteration": {
                        "resultCount": "1",
                        "expressionType": "Protein",
                        "biomarkerName": "PD-L1 IC(SP142)",
                        "result": "Positive",
                        "result_group": "High",
                        "gene": "CD274",
                        "tcResult": "Positive",
                        "tcIntensity": "1+",
                        "tcStainPercent": 50,
                        "tcThreshold": "<50% or <1+ or ≥1+ and ≥50%",
                        "icResult": "Negative",
                        "icStainPercent": 5,
                        "icThreshold": "≥10% or <10%",
                        "isExpressed": "true",
                        "genomicSource": "Somatic",
                        "equivocal": "false",
                        "interpretation": "",
                    }
                },
            }
        ]
    }

    ihc_with_ic_tc_results = get_ihc_results(ihc_with_ic_tc, mock_log)
    assert ihc_with_ic_tc_results == [
        {
            "biomarkerName": "PD-L1 IC(SP142)",
            "result": "Positive",
            "tcResult": "Positive",
            "tcIntensity": "1+",
            "tcStainPercent": 50,
            "tcThreshold": "≥1+ and ≥50%",
            "icResult": "Negative",
            "icStainPercent": 5,
            "icThreshold": "≥10%",
        }
    ]

    # PD-L1 22c3 tests - with cpScore
    ihc_22c3_cp = {
        "tests": [
            {
                "testName": "PD-L1 (22c3)",
                "testCode": "CMI1000",
                "platformTechnology": "IHC",
                "testMethodology": "IHC",
                "testResults": {
                    "expressionAlteration": {
                        "resultCount": "1",
                        "expressionType": "Protein",
                        "biomarkerName": "PD-L1 (22c3)",
                        "result": "Negative",
                        "result_group": "Normal",
                        "gene": "CD274",
                        "cpScore": "0",
                        "threshold": "<1+ or ≥1+",
                        "isExpressed": "false",
                        "genomicSource": "Somatic",
                        "equivocal": "false",
                        "interpretation": "",
                    }
                },
            }
        ]
    }

    ihc_22c3_results_cp = get_ihc_results(ihc_22c3_cp, mock_log)
    assert ihc_22c3_results_cp == [
        {
            "biomarkerName": "PD-L1 (22c3)",
            "result": "Negative",
            "cpScore": 0,
            "threshold": "≥1+",
        }
    ]

    # PD-L1 22c3 tests - with tpScore
    ihc_22c3_tp = {
        "tests": [
            {
                "testName": "PD-L1 (22c3)",
                "testCode": "CMI1000",
                "platformTechnology": "IHC",
                "testMethodology": "IHC",
                "testResults": {
                    "expressionAlteration": {
                        "resultCount": "1",
                        "expressionType": "Protein",
                        "biomarkerName": "PD-L1 (22c3)",
                        "result": "Negative",
                        "result_group": "Normal",
                        "gene": "CD274",
                        "tpScore": "10",
                        "threshold": "<1+ or ≥1+",
                        "isExpressed": "false",
                        "genomicSource": "Somatic",
                        "equivocal": "false",
                        "interpretation": "",
                    }
                },
            }
        ]
    }

    ihc_22c3_results_tp = get_ihc_results(ihc_22c3_tp, mock_log)
    assert ihc_22c3_results_tp == [
        {
            "biomarkerName": "PD-L1 (22c3)",
            "result": "Negative",
            "tpScore": 10,
            "threshold": "≥1+",
        }
    ]

    # [IC] in threshold test
    ihc_with_ic_only = {
        "tests": [
            {
                "testName": "PD-L1 FDA(SP142)",
                "testCode": "CMI1099",
                "platformTechnology": "IHC",
                "testMethodology": "IHC",
                "testResults": {
                    "expressionAlteration": {
                        "resultCount": "1",
                        "expressionType": "Protein",
                        "biomarkerName": "PD-L1 IC(SP142)",
                        "result": "Positive",
                        "result_group": "High",
                        "gene": "CD274",
                        "intensity": "",
                        "stainPercent": 5,
                        "threshold": "≥5[IC] or <5[IC]",
                        "isExpressed": "true",
                        "genomicSource": "Somatic",
                        "equivocal": "false",
                        "interpretation": "",
                    }
                },
            }
        ]
    }

    ihc_with_ic_only_results = get_ihc_results(ihc_with_ic_only, mock_log)
    assert ihc_with_ic_only_results == [
        {
            "biomarkerName": "PD-L1 IC(SP142)",
            "result": "Positive",
            "stainPercent": 5,
            "threshold": "≥5[IC]",
        }
    ]

    # Mismatch repair status test
    ihc_mrs = {
        "tests": [
            {
                "testName": "Mismatch Repair Status",
                "testCode": "CMI1095",
                "platformTechnology": "IHC",
                "testMethodology": "IHC",
                "testResults": {
                    "expressionAlteration": {
                        "resultCount": "1",
                        "expressionType": "Protein",
                        "biomarkerName": "Mismatch Repair Status",
                        "result": "Proficient",
                        "result_group": "Proficient",
                        "gene": [
                            "MLH1",
                            "MSH2",
                            "MSH6",
                            "PMS2",
                        ],
                        "intensity": "",
                        "stainPercent": np.nan,
                        "threshold": "",
                        "isExpressed": "false",
                        "genomicSource": "Somatic",
                        "equivocal": "false",
                        "interpretation": "",
                    }
                },
            }
        ]
    }

    ihc_mrs_results = get_ihc_results(ihc_mrs, mock_log)
    assert ihc_mrs_results == [
        {
            "biomarkerName": "Mismatch Repair Status",
            "result": "Proficient",
        }
    ]

    # Folfox Respodner Similarity test
    ihc_frs = {
        "tests": [
            {
                "testName": "Folfox Responder Similarity Score",
                "testCode": "CMI1120",
                "platformTechnology": "IHC",
                "testMethodology": "IHC",
                "testResults": {
                    "expressionAlteration": {
                        "resultCount": "1",
                        "expressionType": "Protein",
                        "biomarkerName": "Folfox Responder Similarity",
                        "result": "Positive",
                        "result_group": "High",
                        "intensity": "",
                        "stainPercent": "",
                        "threshold": "",
                        "isExpressed": "false",
                        "genomicSource": "Somatic",
                        "equivocal": "false",
                        "interpretation": "",
                    }
                },
            }
        ]
    }
    ihc_frs_results = get_ihc_results(ihc_frs, mock_log)
    assert ihc_frs_results == [
        {
            "biomarkerName": "Folfox Responder Similarity",
            "result": "Positive",
        }
    ]

    # Normal test
    ihc_standard = {
        "tests": [
            {
                "testName": "ALK",
                "testCode": "CMI1742",
                "platformTechnology": "IHC",
                "testMethodology": "IHC",
                "testResults": {
                    "expressionAlteration": {
                        "resultCount": "1",
                        "expressionType": "Protein",
                        "biomarkerName": "ALK",
                        "result": "Positive",
                        "result_group": "High",
                        "gene": "ALK",
                        "intensity": "2+",
                        "stainPercent": 60,
                        "threshold": "=0+ and =100% or ≥1+ and ≥1%",
                        "isExpressed": "true",
                        "genomicSource": "Somatic",
                        "equivocal": "false",
                        "interpretation": "",
                    }
                },
            }
        ]
    }

    ihc_standard_results = get_ihc_results(ihc_standard, mock_log)
    assert ihc_standard_results == [
        {
            "biomarkerName": "ALK",
            "result": "Positive",
            "intensity": "2+",
            "stainPercent": 60,
            "threshold": "≥1+ and ≥1%",
        }
    ]

    # Normal test + Skip first test because No Result
    ihc_skip_and_standard = {
        "tests": [
            {
                "testName": "ALK",
                "testCode": "CMI1742",
                "platformTechnology": "IHC",
                "testMethodology": "IHC",
                "testResults": {
                    "expressionAlteration": {
                        "resultCount": "1",
                        "expressionType": "Protein",
                        "biomarkerName": "ALK",
                        "result": "Positive",
                        "result_group": "High",
                        "gene": "ALK",
                        "intensity": "2+",
                        "stainPercent": 60,
                        "threshold": "=0+ and =100% or ≥1+ and ≥1%",
                        "isExpressed": "true",
                        "genomicSource": "Somatic",
                        "equivocal": "false",
                        "interpretation": "",
                    }
                },
            },
            {
                "testName": "ALK",
                "testCode": "CMI1742",
                "platformTechnology": "IHC",
                "testMethodology": "IHC",
                "testResults": {
                    "expressionAlteration": {
                        "resultCount": "1",
                        "expressionType": "Protein",
                        "biomarkerName": "ALK",
                        "result": "Other",
                        "result_group": "No Result",
                        "gene": "ALK",
                        "intensity": "",
                        "stainPercent": "",
                        "threshold": "",
                        "isExpressed": "false",
                        "genomicSource": "Somatic",
                        "equivocal": "false",
                        "interpretation": "",
                    }
                },
            },
        ]
    }

    ihc_skip_and_standard_results = get_ihc_results(ihc_skip_and_standard, mock_log)
    assert ihc_skip_and_standard_results == [
        {
            "biomarkerName": "ALK",
            "result": "Positive",
            "intensity": "2+",
            "stainPercent": 60,
            "threshold": "≥1+ and ≥1%",
        }
    ]

    # System level test
    f = open(f"{BASE_PATH}/resources/TN20-779441_IHC.json", "rb")
    all_data = json.load(f)
    data = all_data
    f.close()
    metadata = extract_metadata(
        data, "unit-test", {"pdf": "unit_test.pdf"}, "sourceFileId", INGEST_STATUS, mock_log
    )

    assert metadata == {
        "testType": "MI Profile",
        "indexedDate": "2020-12-08",
        "receivedDate": "2020-12-08",
        "collDate": "2019-12-11",
        "reportDate": "2020-12-11",
        "bodySiteSystem": "http://lifeomic.com/fhir/sequence-body-site",
        "reportID": "TN20-779441",
        "mrn": "LO-CARIS-1234",
        "patientLastName": "Smith",
        "patientDOB": "1950-10-10",
        "medFacilName": "Test Account 1",
        "medFacilID": 50275,
        "orderingMDName": "Test Physician 2, Test",
        "orderingMDNPI": 123453243,
        "indicationSystem": "http://lifeomic.com/fhir/sequence-indication",
        "indication": "Undifferentiated pleomorphic sarcoma",
        "indicationDisplay": "Undifferentiated pleomorphic sarcoma",
        "bodySite": "Ear canal",
        "bodySiteDisplay": "Ear canal",
        "sourceFileId": "sourceFileId",
        "reportFile": ".lifeomic/caris/unit-test/unit_test.pdf",
        "patientInfo": {
            "lastName": "Smith",
            "dob": "1950-10-10",
            "firstName": "Jane",
            "gender": "male",
            "identifiers": [
                {
                    "codingCode": "MR",
                    "codingSystem": "http://hl7.org/fhir/v2/0203",
                    "value": "LO-CARIS-1234",
                }
            ],
        },
        "name": "Caris",
        "reference": "GRCh37",
        "tmb": "high",
        "tmbScore": 33.0,
        "msi": "stable",
        "ihcTests": [
            {
                "biomarkerName": "PD-L1 (22c3)",
                "result": "Negative",
                "cpScore": 0.0,
                "threshold": "≥1+",
            },
            {
                "biomarkerName": "PD-L1 IC(SP142)",
                "result": "Positive",
                "tcResult": "Positive",
                "tcIntensity": "1+",
                "tcStainPercent": 50.0,
                "tcThreshold": "≥1+ and ≥50%",
                "icResult": "Negative",
                "icStainPercent": 5.0,
                "icThreshold": "≥10%",
            },
            {
                "biomarkerName": "PD-L1 IC(SP142)",
                "result": "Positive",
                "stainPercent": 5.0,
                "threshold": "≥5[IC]",
            },
            {
                "biomarkerName": "ALK",
                "result": "Positive",
                "intensity": "2+",
                "stainPercent": 60.0,
                "threshold": "≥1+ and ≥1%",
            },
            {
                "biomarkerName": "PMS2",
                "stainPercent": 1.0,
                "result": "Intact nuclear expression",
            },
            {"biomarkerName": "Mismatch Repair Status", "result": "Proficient"},
        ],
        "resources": [{"fileName": ".lifeomic/caris/unit-test/unit_test.pdf"}],
    }


# Tests for checking IHC pattern logging
class TestCase(unittest.TestCase):
    maxDiff = None
    # Check Standard ihc test- Regualr and Irregular

    def test_ihc_logging_standard(self):
        test_log = logging.getLogger()
        with self.assertLogs(test_log) as cm:
            ihc_standard_R = {
                "tests": [
                    {
                        "testName": "ALK",
                        "testCode": "CMI1742",
                        "platformTechnology": "IHC",
                        "testMethodology": "IHC",
                        "testResults": {
                            "expressionAlteration": {
                                "resultCount": "1",
                                "expressionType": "Protein",
                                "biomarkerName": "ALK",
                                "result": "Positive",
                                "result_group": "High",
                                "gene": "ALK",
                                "intensity": "2+",
                                "stainPercent": 60,
                                "threshold": "=0+ and =100% or ≥1+ and ≥1%",
                                "isExpressed": "true",
                                "genomicSource": "Somatic",
                                "equivocal": "false",
                                "interpretation": "",
                            }
                        },
                    }
                ]
            }

            ihc_standard_R_results = get_ihc_results(ihc_standard_R, test_log)
            self.assertEqual(
                cm.output,
                [
                    "INFO:root:Immunohistochemistry tests detected: 1",
                    "INFO:root:All IHC tests matched the expected patterns.",
                ],
            )
        test_log = logging.getLogger()
        with self.assertLogs(test_log) as cm:
            ihc_standard_I = {
                "tests": [
                    {
                        "testName": "ALK",
                        "testCode": "CMI1742",
                        "platformTechnology": "IHC",
                        "testMethodology": "IHC",
                        "testResults": {
                            "expressionAlteration": {
                                "resultCount": "1",
                                "expressionType": "Protein",
                                "biomarkerName": "ALK",
                                # "result": "Positive",
                                "result_group": "High",
                                "gene": "ALK",
                                # "intensity": "2+",
                                # "stainPercent": "60",
                                # "threshold": "=0+ and =100% or ≥1+ and ≥1%",
                                "isExpressed": "true",
                                "genomicSource": "Somatic",
                                "equivocal": "false",
                                "interpretation": "",
                            }
                        },
                    }
                ]
            }

            ihc_standard_I_results = get_ihc_results(ihc_standard_I, test_log)
            self.assertEqual(
                cm.output,
                [
                    "INFO:root:Immunohistochemistry tests detected: 1",
                    "WARNING:root:IHC test ALK has an unexpected pattern for field: result",
                    "WARNING:root:IHC test ALK has an unexpected pattern for field: intensity",
                    "WARNING:root:IHC test ALK has an unexpected pattern for field: stainPercent",
                    "WARNING:root:IHC test ALK has an unexpected pattern for field: threshold",
                ],
            )

    # Check PD-L1 IC / TC - Regualr and Irregular
    def test_ihc_logging_ic_tc_standard(self):
        test_log = logging.getLogger()
        with self.assertLogs(test_log) as cm:
            ihc_PDL1_ic_tc_R = {
                "tests": [
                    {
                        "testName": "PD-L1 FDA(SP142)",
                        "testCode": "CMI1099",
                        "platformTechnology": "IHC",
                        "testMethodology": "IHC",
                        "testResults": {
                            "expressionAlteration": {
                                "resultCount": "1",
                                "expressionType": "Protein",
                                "biomarkerName": "PD-L1 IC(SP142)",
                                "result": "Positive",
                                "result_group": "High",
                                "gene": "CD274",
                                "tcResult": "Positive",
                                "tcIntensity": "1+",
                                "tcStainPercent": 50,
                                "tcThreshold": "<50% or <1+ or ≥1+ and ≥50%",
                                "icResult": "Negative",
                                "icStainPercent": 5,
                                "icThreshold": "≥10% or <10%",
                                "isExpressed": "true",
                                "genomicSource": "Somatic",
                                "equivocal": "false",
                                "interpretation": "",
                            }
                        },
                    }
                ]
            }

            ihc_PDL1_ic_tc_R_results = get_ihc_results(ihc_PDL1_ic_tc_R, test_log)
            self.assertEqual(
                cm.output,
                [
                    "INFO:root:Immunohistochemistry tests detected: 1",
                    "INFO:root:All IHC tests matched the expected patterns.",
                ],
            )
        test_log = logging.getLogger()
        with self.assertLogs(test_log) as cm:
            ihc_PDL1_ic_tc_I = {
                "tests": [
                    {
                        "testName": "PD-L1 FDA(SP142)",
                        "testCode": "CMI1099",
                        "platformTechnology": "IHC",
                        "testMethodology": "IHC",
                        "testResults": {
                            "expressionAlteration": {
                                "resultCount": "1",
                                "expressionType": "Protein",
                                "biomarkerName": "PD-L1 IC(SP142)",
                                "result": "Positive",
                                "result_group": "High",
                                "gene": "CD274",
                                "tcResult": "Positive",
                                # "tcIntensity": "1+",
                                "tcStainPercent": 50,
                                "tcThreshold": "<50% or <1+ or ≥1+ and ≥50%",
                                "icResult": "Negative",
                                # "icStainPercent": "5",
                                "icThreshold": "≥10% or <10%",
                                "isExpressed": "true",
                                "genomicSource": "Somatic",
                                "equivocal": "false",
                                "interpretation": "",
                            }
                        },
                    }
                ]
            }

            ihc_PDL1_ic_tc_I_results = get_ihc_results(ihc_PDL1_ic_tc_I, test_log)
            self.assertEqual(
                cm.output,
                [
                    "WARNING:root:IHC test PD-L1 IC(SP142) has an unexpected pattern: ic/tc field count is 5. Should be 0 or 7(PD-L1).",
                    "INFO:root:Immunohistochemistry tests detected: 1",
                ],
            )

    # Check PD-L1 IC only - Regualr and Irregular
    def test_ihc_logging_PDL1_ic_only(self):
        test_log = logging.getLogger()
        with self.assertLogs(test_log) as cm:
            ihc_PDL1_ic_R = {
                "tests": [
                    {
                        "testName": "PD-L1 FDA(SP142)",
                        "testCode": "CMI1099",
                        "platformTechnology": "IHC",
                        "testMethodology": "IHC",
                        "testResults": {
                            "expressionAlteration": {
                                "resultCount": "1",
                                "expressionType": "Protein",
                                "biomarkerName": "PD-L1 IC(SP142)",
                                "result": "Positive",
                                "result_group": "High",
                                "gene": "CD274",
                                "intensity": "",
                                "stainPercent": 5,
                                "threshold": "≥5[IC] or <5[IC]",
                                "isExpressed": "true",
                                "genomicSource": "Somatic",
                                "equivocal": "false",
                                "interpretation": "",
                            }
                        },
                    }
                ]
            }

            ihc_PDL1_ic_R_results = get_ihc_results(ihc_PDL1_ic_R, test_log)
            self.assertEqual(
                cm.output,
                [
                    "INFO:root:Immunohistochemistry tests detected: 1",
                    "INFO:root:All IHC tests matched the expected patterns.",
                ],
            )
        test_log = logging.getLogger()
        with self.assertLogs(test_log) as cm:
            ihc_PDL1_ic_I = {
                "tests": [
                    {
                        "testName": "PD-L1 FDA(SP142)",
                        "testCode": "CMI1099",
                        "platformTechnology": "IHC",
                        "testMethodology": "IHC",
                        "testResults": {
                            "expressionAlteration": {
                                "resultCount": "1",
                                "expressionType": "Protein",
                                "biomarkerName": "PD-L1 IC(SP142)",
                                "result": "Positive",
                                "result_group": "High",
                                "gene": "CD274",
                                "intensity": "1+",
                                "stainPercent": 5,
                                "threshold": "≥5[IC] or <5[IC]",
                                "isExpressed": "true",
                                "genomicSource": "Somatic",
                                "equivocal": "false",
                                "interpretation": "",
                            }
                        },
                    }
                ]
            }

            ihc_PDL1_ic_I_results = get_ihc_results(ihc_PDL1_ic_I, test_log)
            self.assertEqual(
                cm.output,
                [
                    'WARNING:root:IHC test PD-L1 IC(SP142) has an unexpected pattern for "intensity": value of "1+" was given when None was expected',
                    "INFO:root:Immunohistochemistry tests detected: 1",
                ],
            )

    # Check PD-L1 22c3 - Regular and Irregular
    def test_ihc_logging_PDL1_22c3(self):
        test_log = logging.getLogger()
        with self.assertLogs(test_log) as cm:
            ihc_PDL1_22c3_R = {
                "tests": [
                    {
                        "testName": "PD-L1 (22c3)",
                        "testCode": "CMI1000",
                        "platformTechnology": "IHC",
                        "testMethodology": "IHC",
                        "testResults": {
                            "expressionAlteration": {
                                "resultCount": "1",
                                "expressionType": "Protein",
                                "biomarkerName": "PD-L1 (22c3)",
                                "result": "Negative",
                                "result_group": "Normal",
                                "gene": "CD274",
                                "cpScore": 0,
                                "threshold": "<1+ or ≥1+",
                                "isExpressed": "false",
                                "genomicSource": "Somatic",
                                "equivocal": "false",
                                "interpretation": "",
                            }
                        },
                    }
                ]
            }

            ihc_PDL1_22c3_R_results = get_ihc_results(ihc_PDL1_22c3_R, test_log)
            self.assertEqual(
                cm.output,
                [
                    "INFO:root:Immunohistochemistry tests detected: 1",
                    "INFO:root:All IHC tests matched the expected patterns.",
                ],
            )
        test_log = logging.getLogger()
        with self.assertLogs(test_log) as cm:
            ihc_PDL1_22c3_I = {
                "tests": [
                    {
                        "testName": "PD-L1 (22c3)",
                        "testCode": "CMI1000",
                        "platformTechnology": "IHC",
                        "testMethodology": "IHC",
                        "testResults": {
                            "expressionAlteration": {
                                "resultCount": "1",
                                "expressionType": "Protein",
                                "biomarkerName": "PD-L1 (22c3)",
                                "result": "Negative",
                                "result_group": "Normal",
                                "gene": "CD274",
                                "intensity": "2+",
                                "stainPercent": 60,
                                "threshold": "=0+ and =100% or ≥1+ and ≥1%",
                                "isExpressed": "true",
                                "genomicSource": "Somatic",
                                "equivocal": "false",
                                "interpretation": "",
                            }
                        },
                    }
                ]
            }

            ihc_PDL1_22c3_I_results = get_ihc_results(ihc_PDL1_22c3_I, test_log)
            self.assertEqual(
                cm.output,
                [
                    'WARNING:root:IHC test PD-L1 (22c3) has an unexpected pattern for "intensity": value of "2+" was given when None was expected',
                    'WARNING:root:IHC test PD-L1 (22c3) has an unexpected pattern for "stainPercent": value of "60" was given when None was expected',
                    "INFO:root:Immunohistochemistry tests detected: 1",
                    "WARNING:root:IHC test PD-L1 (22c3) has an unexpected pattern for field: cpScore",
                ],
            )

    # Check Mismatch Repair Status -Regular and Irregular
    def test_ihc_logging_MRS(self):
        test_log = logging.getLogger()
        with self.assertLogs(test_log) as cm:
            ihc_MRS_R = {
                "tests": [
                    {
                        "testName": "Mismatch Repair Status",
                        "testCode": "CMI1095",
                        "platformTechnology": "IHC",
                        "testMethodology": "IHC",
                        "testResults": {
                            "expressionAlteration": {
                                "resultCount": "1",
                                "expressionType": "Protein",
                                "biomarkerName": "Mismatch Repair Status",
                                "result": "Proficient",
                                "result_group": "Proficient",
                                "gene": [
                                    "MLH1",
                                    "MSH2",
                                    "MSH6",
                                    "PMS2",
                                ],
                                "intensity": "",
                                "stainPercent": np.nan,
                                "threshold": "",
                                "isExpressed": "false",
                                "genomicSource": "Somatic",
                                "equivocal": "false",
                                "interpretation": "",
                            }
                        },
                    }
                ]
            }

            ihc_MRS_R_results = get_ihc_results(ihc_MRS_R, test_log)
            self.assertEqual(
                cm.output,
                [
                    "INFO:root:Immunohistochemistry tests detected: 1",
                    "INFO:root:All IHC tests matched the expected patterns.",
                ],
            )
        test_log = logging.getLogger()
        with self.assertLogs(test_log) as cm:
            ihc_MRS_I = {
                "tests": [
                    {
                        "testName": "Mismatch Repair Status",
                        "testCode": "CMI1095",
                        "platformTechnology": "IHC",
                        "testMethodology": "IHC",
                        "testResults": {
                            "expressionAlteration": {
                                "resultCount": "1",
                                "expressionType": "Protein",
                                "biomarkerName": "Mismatch Repair Status",
                                "result": "Proficient",
                                "result_group": "Proficient",
                                "gene": [
                                    "MLH1",
                                    "MSH2",
                                    "MSH6",
                                    "PMS2",
                                ],
                                "intensity": "2+",
                                "stainPercent": 55,
                                "threshold": "≥1+ and ≥50%",
                                "isExpressed": "false",
                                "genomicSource": "Somatic",
                                "equivocal": "false",
                                "interpretation": "",
                            }
                        },
                    }
                ]
            }

            ihc_MRS_I_results = get_ihc_results(ihc_MRS_I, test_log)
            self.assertEqual(
                cm.output,
                [
                    'WARNING:root:IHC test Mismatch Repair Status has an unexpected pattern for "intensity": value of "2+" was given when None was expected',
                    'WARNING:root:IHC test Mismatch Repair Status has an unexpected pattern for "stainPercent": value of "55" was given when None was expected',
                    'WARNING:root:IHC test Mismatch Repair Status has an unexpected pattern for "threshold": value of "≥1+ and ≥50%" was given when None was expected',
                    "INFO:root:Immunohistochemistry tests detected: 1",
                ],
            )


class TestGrDetection(unittest.TestCase):
    def test_detect_caris_gr_structural(self):
        struc_37 = [
            {
                "resultCount": 1,
                "gene": "ALK",
                "biomarkerName": "ALK",
                "result": "Fusion Detected",
                "result_group": "Mutated",
                "genomicSource": "Somatic",
                "genomeBuild": "GRCh37/hg19",
            },
            {
                "resultCount": 1,
                "gene": "ALK",
                "biomarkerName": "ALK",
                "result": "Fusion of Uncertain Significance",
                "result_group": "Mutated",
                "genomicSource": "Somatic",
                "genomeBuild": "GRCh37/hg19",
            },
        ]
        assert detect_caris_gr(struc_37, "structural", mock_log) == "GRCh37"

        struc_38 = [
            {
                "resultCount": 1,
                "gene": "ALK",
                "biomarkerName": "ALK",
                "result": "Fusion Detected",
                "result_group": "Mutated",
                "genomicSource": "Somatic",
                "genomeBuild": "GRCh38/hg38",
            },
            {
                "resultCount": 1,
                "gene": "ALK",
                "biomarkerName": "ALK",
                "result": "Fusion of Uncertain Significance",
                "result_group": "Mutated",
                "genomicSource": "Somatic",
                "genomeBuild": "GRCh38/hg38",
            },
        ]
        assert detect_caris_gr(struc_38, "structural", mock_log) == "GRCh38"

        with self.assertRaises(RuntimeError) as cm:
            struc_mixed = [
                {
                    "resultCount": 1,
                    "gene": "ALK",
                    "biomarkerName": "ALK",
                    "result": "Fusion Detected",
                    "result_group": "Mutated",
                    "genomicSource": "Somatic",
                    "genomeBuild": "GRCh38/hg38",
                },
                {
                    "resultCount": 1,
                    "gene": "ALK",
                    "biomarkerName": "ALK",
                    "result": "Fusion of Uncertain Significance",
                    "result_group": "Mutated",
                    "genomicSource": "Somatic",
                    "genomeBuild": "GRCh37/hg19",
                },
            ]
            detect_caris_gr(struc_mixed, "structural", mock_log)
            self.assertTrue(
                "Mixed genome references detected in structural variants." in str(cm.exception)
            )

        with self.assertRaises(RuntimeError) as cm:
            struc_uk = [
                {
                    "resultCount": 1,
                    "gene": "ALK",
                    "biomarkerName": "ALK",
                    "result": "Fusion Detected",
                    "result_group": "Mutated",
                    "genomicSource": "Somatic",
                    "genomeBuild": "",
                },
                {
                    "resultCount": 1,
                    "gene": "ALK",
                    "biomarkerName": "ALK",
                    "result": "Fusion of Uncertain Significance",
                    "result_group": "Mutated",
                    "genomicSource": "Somatic",
                    "genomeBuild": "",
                },
            ]
            detect_caris_gr(struc_uk, "structural", mock_log)
            self.assertTrue(
                "Unknown genome reference detected in structural variants." in str(cm.exception)
            )

    def test_detect_caris_gr_expression(self):
        expr_37 = [
            "##FlowCellID=230120_A01688_0084_BH2VWCDRX3",
            "##SampleID=TN23-103610",
            "##Lane=Lane1",
            "##AnalysisDateTime=20230121-143041",
            "##WTSExpressionPipelineVersion=1.2.0",
            "##GeneRangeFileVersion=4.0.0",
        ]

        assert detect_caris_gr(expr_37, "expression", mock_log) == "GRCh37"

        expr_38 = [
            "##FlowCellID=230120_A01688_0084_BH2VWCDRX3",
            "##SampleID=TN23-103610",
            "##Lane=Lane1",
            "##AnalysisDateTime=20230121-143041",
            "##WTSExpressionPipelineVersion=1.2.1",
            "##GeneRangeFileVersion=4.0.0",
        ]

        assert detect_caris_gr(expr_38, "expression", mock_log) == "GRCh38"

        with self.assertRaises(RuntimeError) as cm:
            expression_none = [
                "##FlowCellID=230120_A01688_0084_BH2VWCDRX3",
                "##SampleID=TN23-103610",
                "##Lane=Lane1",
                "##AnalysisDateTime=20230121-143041",
                "##GeneRangeFileVersion=4.0.0",
            ]
            detect_caris_gr(expression_none, "expression", mock_log)
            self.assertTrue(
                "No or unknown genome reference detected in expression tsv file."
                in str(cm.exception)
            )


class TestCoordMapping(unittest.TestCase):
    def test_gene_to_coords(self):
        with self.assertRaises(KeyError) as cm:
            gene_to_coords("GRCh37", "FAKEGENE")
            self.assertTrue(
                f"Input gene FAKEGENE does not exist in the reference dictionary."
                in str(cm.exception)
            )
