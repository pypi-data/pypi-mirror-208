from logging import Logger
from pathlib import Path
from filter_vcf.util.readVcf import read_vcf
from filter_vcf.util.userFilter import perform_filter_vcf
from filter_vcf.util.writeVcf import write_vcf


def filter_vcf(vcf_in: str, filters: str, log: Logger):
    working_vcf = read_vcf(vcf_in, log=log).to_string()

    log.info("Filtering VCF using filters: {}".format(filters))
    working_vcf = perform_filter_vcf(vcf_string=working_vcf, filters=filters, log=log)

    vcf_out = vcf_in.replace("nrm.vcf.gz", "nrm.filtered.vcf.gz")
    print(f"saving file {vcf_out}")
    write_vcf(vcf_in=working_vcf, vcf_out=vcf_out, compression=True, log=log)

    return Path(vcf_out)
