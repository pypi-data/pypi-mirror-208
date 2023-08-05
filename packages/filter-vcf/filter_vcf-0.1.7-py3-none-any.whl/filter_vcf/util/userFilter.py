from logging import Logger


def perform_filter_vcf(vcf_string: str, filters: str, log: Logger) -> str:
    # Only keep user specified filters
    # Entries in VCF must strictly consist of allowed filters
    # e.g. filters = Pass:sb
    # entry = sb = KEPT
    # entry = sb;lowQ = DISCARDED

    allowed_filters = filters.split(":")
    allowed_filters_set = set(allowed_filters)
    vcf_filtered = []

    for line in vcf_string.split("\n"):
        if line != "":
            if line.startswith("#"):
                vcf_filtered.append(line)

            else:
                working_line = line.split("\t")
                working_filters = working_line[6].split(";")

                working_filters_set = set(working_filters)

                # if both sets are exact matches, great, lets move on
                if allowed_filters_set == working_filters_set:
                    vcf_filtered.append(line)

                # if they aren't exact matches and working_filter_set has more than one filter values
                # then we discard as we don't let combinations exist in the record for filter
                elif len(working_filters_set) != 1:
                    continue

                elif len(allowed_filters_set.intersection(working_filters_set)) > 0:
                    vcf_filtered.append(line)

    # Concat to single string, and add newline to end
    vcf_filtered = "\n".join(vcf_filtered)
    vcf_filtered = vcf_filtered + "\n"
    return vcf_filtered
