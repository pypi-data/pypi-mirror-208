from logging import Logger


def keep_unique_variants(vcf_string: str, log: Logger) -> str:
    # Remove any duplicate variants from VCF
    vcf_unique = []
    key = ""

    for line in vcf_string.split("\n"):
        if line != "":
            if line.startswith("#"):
                vcf_unique.append(line)

            else:
                working_line = line.split("\t")
                working_key = ":".join(working_line[0:5])

                # Check if working_key is the same as the previous key
                if working_key != key:
                    vcf_unique.append(line)
                    key = working_key

    # Concat to single string, and add newline to end
    vcf_unique = "\n".join(vcf_unique)
    vcf_unique = vcf_unique + "\n"

    return vcf_unique
