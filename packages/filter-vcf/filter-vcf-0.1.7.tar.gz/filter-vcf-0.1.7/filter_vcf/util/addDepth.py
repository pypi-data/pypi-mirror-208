from logging import Logger


def add_depth(vcf_string: str, log: Logger) -> str:
    # Compute DP (the depth for the genotype) field if it is not present
    # Sums the AD field. This is to be called before the decompose step
    vcf_with_depth = []
    dp_trigger = False

    # Add DP formatting to VCF header
    for line in vcf_string.split("\n"):
        if line != "\n":
            if line.startswith("#"):
                if line.startswith("##FORMAT=<ID=DP"):
                    dp_trigger = True
                elif line.startswith("#CHROM") and dp_trigger == False:
                    vcf_with_depth.append(
                        '##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Read Depth">'
                    )

                vcf_with_depth.append(line)

            # Add DP to variant calls
            elif len(line.split("\t")) > 1:
                working_line = line.split("\t")
                labels = working_line[8].split(":")
                values = working_line[9].split(":")

                if "AD" in labels and "DP" not in labels:
                    variant_dict = dict(zip(labels, values))

                    ad_values = variant_dict.get("AD").split(",")
                    dp_value = sum([int(ad_value) for ad_value in ad_values])

                    labels.append("DP")
                    values.append(f"{dp_value}")

                    working_line[8] = ":".join(labels)
                    working_line[9] = ":".join(values)

                    vcf_with_depth.append("\t".join(working_line))

                else:
                    vcf_with_depth.append(line)

    # Concat to single string, and add newline to end
    vcf_with_depth = "\n".join(vcf_with_depth)
    vcf_with_depth = vcf_with_depth + "\n"

    return vcf_with_depth
