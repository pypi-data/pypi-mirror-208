from logging import Logger
from natsort import natsorted


def sort_key(row):
    chrom = row.get("#CHROM")
    pos = int(row.get("POS"))
    ref = row.get("REF")
    alt = row.get("ALT")
    return (chrom, pos, ref, alt)


def sort_vcf(vcf_string, log: Logger) -> str:
    # Perform natural sort on CHROM, POS, REF, and ALT columns
    vcf_string = vcf_string.strip().split("\n")

    headers = [line for line in vcf_string if line.startswith("#")]
    variants = [line.split("\t") for line in vcf_string if not line.startswith("#")]
    col_names = headers[-1].split("\t")

    vcf_dict_rows = [dict(zip(col_names, row)) for row in variants]
    vcf_full_dict = {"header": headers, "rows": vcf_dict_rows}

    vcf_full_dict["rows"] = natsorted(vcf_full_dict["rows"], key=sort_key)

    # Rebuild the VCF
    sorted_vcf_string = "\n".join(vcf_full_dict["header"]) + "\n"
    sorted_vcf_string += "\n".join("\t".join(row.values()) for row in vcf_full_dict["rows"]) + "\n"

    return sorted_vcf_string
