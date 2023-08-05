from logging import Logger


def detect_vcf(vcf_string: str, log: Logger) -> str:
    # Detects whether variants are prefixed with 'chr' or not.
    # Return variable for input int convertChrName.py

    first_fields = []

    for line in vcf_string.split("\n"):
        if line != "" and not line.startswith("#"):
            working_line = line.split("\t")
            first_fields.append(working_line[0])

    # Identify if we have any 'chr' first fields or not
    uniq_first_fields = [i for i in set(first_fields) if i.startswith("chr")]
    if len(uniq_first_fields) == 0:
        return "num"
    else:
        return "chr"
