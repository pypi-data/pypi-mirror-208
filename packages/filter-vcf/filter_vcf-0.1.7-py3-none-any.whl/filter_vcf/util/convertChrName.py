from logging import Logger


def convert_chr_name(vcf_string: str, chr_var: str, log: Logger) -> str:
    # Convert chromosome name to either add or remove 'chr' prefix
    vcf_converted = []

    if chr_var == "chr":
        # Change MT -> M, add chr to every entry.
        for line in vcf_string.split("\n"):
            if line != "":
                if line.startswith("#"):
                    vcf_converted.append(line)

                else:
                    working_line = line.split("\t")
                    chromosome = working_line[0]
                    if chromosome == "MT":
                        chromosome = "M"
                    converted_chromosome = "chr" + chromosome
                    working_line[0] = converted_chromosome
                    vcf_converted.append("\t".join(working_line))

    elif chr_var == "num":
        # Change M -> MT, remove chr from every entry.
        for line in vcf_string.split("\n"):
            if line != "":
                if line.startswith("#"):
                    vcf_converted.append(line)

                else:
                    working_line = line.split("\t")
                    chromosome = working_line[0]
                    converted_chromosome = chromosome.strip("chr")
                    if converted_chromosome == "M":
                        converted_chromosome = "MT"
                    working_line[0] = converted_chromosome
                    vcf_converted.append("\t".join(working_line))

    else:
        log.error(f'Improper input for chr_var. Must be "num" or "chr". Given: {chr_var}')

    # Concat to single string, and add newline to end
    vcf_converted = "\n".join(vcf_converted)
    vcf_converted = vcf_converted + "\n"

    return vcf_converted
