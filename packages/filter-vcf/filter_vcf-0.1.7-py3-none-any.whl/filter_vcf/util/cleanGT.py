from logging import Logger


def remove_gt_dot(vcf_string: str, log: Logger) -> str:
    # Check the GT in genotype field if there more than 2 entries,
    # remove "." values if number of "." - total entries == 2
    # otherwise leave it the same

    vcf_with_corrected_gt = []

    for line in vcf_string.split("\n"):
        if line != "":
            if line.startswith("#"):
                vcf_with_corrected_gt.append(line)

            else:
                working_line = line.split("\t")

                labels = working_line[8].split(":")
                values = working_line[9].split(":")
                variant_dict = dict(zip(labels, values))

                gt_values = variant_dict.get("GT")

                # Detect and set separator
                if "|" in gt_values:
                    sep = "|"
                else:
                    sep = "/"

                gt_split = gt_values.split(sep)

                # Processing if there are more than two values in GT array
                if len(gt_split) > 2:
                    new_gt_vals = []
                    dot_count = 0

                    for item in gt_split:
                        if item == ".":
                            dot_count += 1
                        else:
                            new_gt_vals.append(f"{sep}{item}")

                    if len(gt_split) - dot_count == 2:
                        new_gt_string = "".join(new_gt_vals).strip(sep)
                        variant_dict.update({"GT": new_gt_string})

                        working_line[9] = ":".join(list(variant_dict.values()))
                        vcf_with_corrected_gt.append("\t".join(working_line))

                    else:
                        vcf_with_corrected_gt.append(line)

                else:
                    vcf_with_corrected_gt.append(line)

    # Concat to single string, and add newline to end
    vcf_with_corrected_gt = "\n".join(vcf_with_corrected_gt)
    vcf_with_corrected_gt = vcf_with_corrected_gt + "\n"

    return vcf_with_corrected_gt


def fix_gt_extra(vcf_string: str, log: Logger):
    # Check the alt field to be single value but the genotype field has more
    # than 2 entries or contain enumeration 2 or higher
    # e.g.
    # chr1	11138938	rs17417751	C	T	8355.2	PASS	.	GT:AD:DP:GQ:PL	0/0/1/1:324,290:617:99:8382,307,0,455,2147483647

    vcf_with_corrected_gt = []

    for line in vcf_string.split("\n"):
        if line != "":
            if line.startswith("#"):
                vcf_with_corrected_gt.append(line)

            else:
                working_line = line.split("\t")

                alt = working_line[4].split(",")

                labels = working_line[8].split(":")
                values = working_line[9].split(":")
                variant_dict = dict(zip(labels, values))

                gt_values = variant_dict.get("GT")

                # Detect and set separator
                if "|" in gt_values:
                    sep = "|"
                else:
                    sep = "/"

                gt_split = gt_values.split(sep)

                # Processing if there is a single ALT value and multiple GT values
                if len(alt) == 1 and len(gt_split) > 2:
                    # Log each value, add to a list if it's novel. max length of two. return it.
                    new_gt_vals = []

                    for item in gt_split:
                        if item not in new_gt_vals and len(new_gt_vals) < 2:
                            new_gt_vals.append(item)

                    new_gt_string = f"{sep}".join(new_gt_vals)
                    variant_dict.update({"GT": new_gt_string})

                    working_line[9] = ":".join(list(variant_dict.values()))
                    vcf_with_corrected_gt.append("\t".join(working_line))

                else:
                    vcf_with_corrected_gt.append(line)

    # Concat to single string, and add newline to end
    vcf_with_corrected_gt = "\n".join(vcf_with_corrected_gt)
    vcf_with_corrected_gt = vcf_with_corrected_gt + "\n"

    return vcf_with_corrected_gt


def clean_gt(vcf_string, log: Logger):
    gt_no_dot = remove_gt_dot(vcf_string, log)
    gt_no_extra = fix_gt_extra(gt_no_dot, log)

    return gt_no_extra
