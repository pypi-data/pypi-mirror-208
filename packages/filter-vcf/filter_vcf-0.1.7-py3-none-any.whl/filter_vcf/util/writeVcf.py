from fuc import pyvcf
from logging import Logger


def write_vcf(
    vcf_in,
    vcf_out: str,
    compression: bool,
    log: Logger,
):
    if isinstance(vcf_in, str) == True:
        vcf_in = pyvcf.VcfFrame.from_string(vcf_in)

    vcf_in.to_file(vcf_out, compression)
