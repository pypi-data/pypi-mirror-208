from logging import Logger
from packaging import version


def detect_caris_gr(data, file_type, log: Logger):
    # Detect genome ref used for structural, cnv, and expression files.
    # Returns: GRCh37 or GRCh38

    if file_type == "structural":
        genome_builds = [entry.get("genomeBuild", "") for entry in data]
        if len(set(genome_builds)) > 1:
            raise RuntimeError(f"Mixed genome references detected in {file_type} variants.")
        else:
            genome_reference = genome_builds[0].split("/")[0]

        if genome_reference not in ["GRCh37", "GRCh38"]:
            raise RuntimeError(f"Unknown genome reference detected in {file_type} variants.")

    elif file_type == "expression":
        # Look for the pipeline version number
        pipeline = [
            line
            for line in data
            if "WTSExpressionPipelineVersion" in str(line)
            or "WTSFusionPipelineVersion" in str(line)
        ]
        if len(pipeline) == 0:
            raise RuntimeError(f"No genome reference detected in expression tsv file.")

        pipeline_version = pipeline[0].split("=")[-1]
        if version.parse(pipeline_version) >= version.parse("1.2.1"):
            genome_reference = "GRCh38"
        else:
            genome_reference = "GRCh37"

    return genome_reference
