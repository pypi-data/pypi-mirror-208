from logging import Logger


def filter_non_ref(vcf_string: str, log: Logger):
    # Original: awk -F \'\t\' -v OFS=\'\t\' \'{ if ($1 ~/^#/ || $5 != "<NON_REF>") print $0 }
    vcf_without_non_ref = []

    for line in vcf_string.split("\n"):
        if line != "":
            if line.startswith("#"):
                vcf_without_non_ref.append(line)

            else:
                working_line = line.split("\t")
                if working_line[4] != "<NON_REF>":
                    vcf_without_non_ref.append(line)

    # Concat to single string, and add newline to end
    vcf_without_non_ref = "\n".join(vcf_without_non_ref)
    vcf_without_non_ref = vcf_without_non_ref + "\n"

    return vcf_without_non_ref
