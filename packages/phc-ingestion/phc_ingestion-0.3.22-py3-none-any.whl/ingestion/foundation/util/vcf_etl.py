import gzip
from natsort import natsorted
import re
import os
import errno


def vcf_etl(in_vcf: str, out_vcf: str, base_xml_name: str) -> int:
    headers = []
    vars = []

    if not os.path.exists(os.path.dirname(out_vcf)):
        try:
            os.makedirs(os.path.dirname(out_vcf))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

    with open(in_vcf) as f:
        lines = f.readlines()
        line_count = len(lines)
        if line_count == 0:
            return line_count
        else:
            for line in lines:
                if line.startswith("#"):
                    headers.append(line)
                else:
                    vars.append(line)

            sorted_vars = natsorted(vars)

            with gzip.open(f"{out_vcf}.gz", "wt") as w:
                for header in headers:
                    if "=af," in header:
                        header = header.replace("=af", "=AF")

                    if "#CHROM" in header:
                        w.write('##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Read Depth">\n')
                        w.write('##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">\n')
                        w.write(
                            '##FORMAT=<ID=AD,Number=.,Type=Integer,Description="Number of reads harboring allele (in order specified by GT)">\n'
                        )
                        header = header.strip("\n") + "\tFORMAT\t" + base_xml_name + "\n"

                    w.write(header)

                for var in sorted_vars:
                    var = var.replace("af=", "AF=")
                    var = transform_scientific_notation_in_af(var)
                    af_match = re.search(r"AF=(\d*\.?\d*)", var)
                    if not af_match:
                        raise RuntimeError("Failed to find AF for var")
                    af = float(af_match.group(1))
                    depth_match = re.search(r"depth=(\d*\.?\d*)", var)
                    if not depth_match:
                        raise RuntimeError("Failed to find depth for var")
                    depth = int(depth_match.group(1))
                    alt_depth = int(round(depth * af))
                    ref_depth = depth - alt_depth
                    ad = f"{ref_depth},{alt_depth}"
                    gt = "1/1" if af > 0.9 else "0/1"
                    vcf_format = "GT:DP:AD"
                    sample = ":".join([gt, str(depth), ad])
                    var = var.strip("\n") + f"\t{vcf_format}\t{sample}\n"
                    w.write(var)

            return line_count


def transform_scientific_notation_in_af(var: str) -> str:
    var_split = var.split("\t")
    var_info = var_split[-1]
    var_info_split = var_info.split(";")
    var_info_list = [x for x in var_info_split if x.startswith("AF=")]

    # No AF= in line so lets return as is and move on
    if len(var_info_list) != 1:
        return var
    var_info_af = var_info_list[0]
    af_split = var_info_af.split("=")
    af_original_value = af_split[1]
    af_float_value = float(af_original_value)
    var = var.replace(af_original_value, str(af_float_value))
    return var
