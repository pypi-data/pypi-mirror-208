from ruamel.yaml import YAML
from logging import Logger
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal


def transform_date(date: str):
    """mm/dd/yyyy -> yyyy-mm-dd"""
    date_list = date.split("/")
    new_date = f"{date_list[2]}-{date_list[0]}-{date_list[1]}"
    return new_date


def extract_pdf_text(pdf_in_file: str):
    pdf_text = {}
    for page_layout in extract_pages(pdf_in_file, maxpages=1):
        for element in page_layout:
            if isinstance(element, LTTextBoxHorizontal):
                if "PCM Result" in element.get_text():
                    return pdf_text

                else:
                    row_text = element.get_text().strip()
                    row_text_lower = row_text.lower().strip()
                    pdf_text[row_text_lower] = row_text


def extract_patient_data(pdf_text: dict):
    patient_data = {}
    patient_data["patientInfo"] = {}

    for row_text_lower, row_text in pdf_text.items():
        if "patientLastName" not in patient_data and "Patient Name".lower() in row_text_lower:
            patientNameArray = row_text.split(":")[1].strip().split(",")
            first = patientNameArray[1].strip()
            last = patientNameArray[0].strip()
            patient_data["patientInfo"]["firstName"] = first
            patient_data["patientInfo"]["lastName"] = last
            patient_data["patientLastName"] = last

        elif "patientDOB" not in patient_data and "Birthdate".lower() in row_text_lower:
            dob = row_text.split(":")[1].strip()
            patient_data["patientDOB"] = transform_date(dob)
            patient_data["patientInfo"]["dob"] = transform_date(dob)

        elif "mrn" not in patient_data and "MRN #".lower() in row_text_lower:
            mrn = row_text.split(":")[1].strip()
            patient_data["mrn"] = mrn
            patient_data["patientInfo"]["identifiers"] = [
                {
                    "codingCode": "MR",
                    "codingSystem": "http://hl7.org/fhir/v2/0203",
                    "value": mrn,
                }
            ]

        elif "gender" not in patient_data["patientInfo"] and "Gender".lower() in row_text_lower:
            gender = row_text.split(":")[1].strip()
            if gender == "F":
                gender = "female"
            elif gender == "M":
                gender = "male"
            else:
                gender = "other"
            patient_data["patientInfo"]["gender"] = gender

    return patient_data


def extract_test_data(pdf_text: dict):
    # Initialize manifest and hard-code some values
    manifest = {}
    manifest["testType"] = "NextGen"
    manifest["name"] = "IU Diagnostic Genomics"
    manifest["reference"] = "GRCh38"

    manifest["ihcTests"] = []
    manifest["tumorTypePredictions"] = []
    manifest["orderingMDNPI"] = ""

    manifest["bodySiteSystem"] = "http://lifeomic.com/fhir/sequence-body-site"
    manifest["indicationSystem"] = "http://lifeomic.com/fhir/sequence-indication"

    manifest["medFacilID"] = ""
    manifest["medFacilName"] = "IU Health"

    manifest["reportDate"] = transform_date(list(pdf_text)[1])

    for row_text_lower, row_text in pdf_text.items():
        if "collected" in row_text_lower:
            coll_date = pdf_text.get(row_text_lower, "")
            if coll_date != "":
                coll_date = transform_date(coll_date.split(":")[1].strip())
            manifest["collDate"] = coll_date

        elif "received" in row_text_lower:
            rec_date = pdf_text.get(row_text_lower, "")
            if rec_date != "":
                rec_date = transform_date(rec_date.split(":")[1].strip())
            manifest["receivedDate"] = rec_date

        elif "accession" in row_text_lower:
            report_id = pdf_text.get(row_text_lower, "")
            if report_id != "":
                report_id = report_id.split(":")[1].strip()
            manifest["reportID"] = report_id

        elif "physician" in row_text_lower:
            phys_name = pdf_text.get(row_text_lower, "")
            if phys_name != "":
                phys_name = phys_name.split(":")[1].strip()
            manifest["orderingMDName"] = phys_name

        elif "reason for referral" in row_text_lower:
            indication = pdf_text.get(row_text_lower, "")
            if indication != "":
                indication = indication.split(":")[1].strip()
            manifest["indication"] = indication
            manifest["indicationDisplay"] = indication

        elif "specimen" in row_text_lower:
            body_site = pdf_text.get(row_text_lower, "")
            if body_site != "":
                body_site = body_site.split(":")[1].strip("\nAge").strip()
            manifest["bodySite"] = body_site
            manifest["bodySiteDisplay"] = body_site

    return manifest


def process_manifest(pdf_in_file: str, source_file_id: str, prefix: str, log: Logger):
    pdf_text = extract_pdf_text(pdf_in_file)
    manifest = extract_test_data(pdf_text)
    manifest.update(extract_patient_data(pdf_text))

    manifest["reportFile"] = f".lifeomic/nextgen/{prefix}/{prefix}.pdf"
    manifest["sourceFileId"] = source_file_id
    manifest["resources"] = [
        {"fileName": f".lifeomic/nextgen/{prefix}/{prefix}.pdf"},
        {"fileName": f".lifeomic/nextgen/{prefix}/{prefix}.modified.somatic.vcf.gz"},
        {"fileName": f".lifeomic/nextgen/{prefix}/{prefix}.modified.germline.vcf.gz"},
        {"fileName": f".lifeomic/nextgen/{prefix}/{prefix}.somatic.updated.bam"},
        {"fileName": f".lifeomic/nextgen/{prefix}/{prefix}.germline.updated.bam"},
        {"fileName": f".lifeomic/nextgen/{prefix}/{prefix}.xml"},
    ]

    manifest["files"] = [
        {
            "fileName": f".lifeomic/nextgen/{prefix}/{prefix}.copynumber.csv",
            "sequenceType": "somatic",
            "type": "copyNumberVariant",
        },
        {
            "fileName": f".lifeomic/nextgen/{prefix}/{prefix}.structural.csv",
            "sequenceType": "somatic",
            "type": "structuralVariant",
        },
        {
            "fileName": f".lifeomic/nextgen/{prefix}/{prefix}.modified.somatic.vcf.gz",
            "sequenceType": "somatic",
            "type": "shortVariant",
        },
        {
            "fileName": f".lifeomic/nextgen/{prefix}/{prefix}.modified.germline.vcf.gz",
            "sequenceType": "germline",
            "type": "shortVariant",
        },
    ]

    return manifest
