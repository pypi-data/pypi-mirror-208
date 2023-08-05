from logging import Logger


def clean_ad(vcf_string: str, log: Logger) -> str:
    # Re-compute AD (allelic depth) field for multi-allelic variants after decomposition
    vcf_with_corrected_ad = []

    for line in vcf_string.split("\n"):
        if line != "":
            if line.startswith("#"):
                vcf_with_corrected_ad.append(line)

            else:
                working_line = line.split("\t")
                info = working_line[7]

                # Processing for if we find decomposed variants
                if "OLD_MULTIALLELIC" in info:
                    labels = working_line[8].split(":")
                    values = working_line[9].split(":")
                    variant_dict = dict(zip(labels, values))

                    gt_value = variant_dict.get("GT")
                    ad_values = variant_dict.get("AD").split(",")

                    if len(ad_values) == 2:
                        new_ad_values = [ad_values[0], ad_values[1]]
                        variant_dict.update({"AD": ",".join(new_ad_values)})

                        working_line[9] = ":".join(list(variant_dict.values()))
                        vcf_with_corrected_ad.append("\t".join(working_line))

                    # First variant will correspond with first and second AD values
                    else:
                        if gt_value == "1/.":
                            new_ad_values = [ad_values[0], ad_values[1]]
                            variant_dict.update({"AD": ",".join(new_ad_values)})

                            working_line[9] = ":".join(list(variant_dict.values()))
                            vcf_with_corrected_ad.append("\t".join(working_line))

                        # Second variant will correspond with first and third AD values
                        elif gt_value == "./1":
                            new_ad_values = [ad_values[0], ad_values[2]]
                            variant_dict.update({"AD": ",".join(new_ad_values)})

                            working_line[9] = ":".join(list(variant_dict.values()))
                            vcf_with_corrected_ad.append("\t".join(working_line))

                else:
                    vcf_with_corrected_ad.append(line)

    # Concat to single string, and add newline to end
    vcf_with_corrected_ad = "\n".join(vcf_with_corrected_ad)
    vcf_with_corrected_ad = vcf_with_corrected_ad + "\n"

    return vcf_with_corrected_ad
