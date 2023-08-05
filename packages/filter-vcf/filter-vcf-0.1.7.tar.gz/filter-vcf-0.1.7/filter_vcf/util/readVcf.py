import os
import gzip
from fuc import pyvcf
from logging import Logger


def read_vcf(vcf_file: str, log: Logger) -> pyvcf.VcfFrame:
    # Load in vcf
    fn = vcf_file

    # Check if file exists. Log if it doesn't.
    if os.path.exists(fn) == False:
        log.error(f'Given file path "{fn}" could not be located')
        return None

    else:
        # Check if it ends in either .vcf or .vcf.gz
        if fn.endswith(".gz"):
            with gzip.open(vcf_file, "rb+") as filein:
                contents = str(filein.read(), "utf-8")
            vf = pyvcf.VcfFrame.from_string(contents)
            return vf

        elif fn.endswith(".vcf"):
            vf = pyvcf.VcfFrame.from_file(fn)
            return vf

        else:
            log.error(f'Given file "{fn}" must be in vcf or vcf.gz format')
