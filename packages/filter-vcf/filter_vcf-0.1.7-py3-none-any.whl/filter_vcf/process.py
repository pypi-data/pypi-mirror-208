import subprocess
import os
import shutil
import uuid
from fuc import pyvcf
from lifeomic_logging import scoped_logger

from filter_vcf.util.userFilter import perform_filter_vcf
from filter_vcf.util.readVcf import read_vcf
from filter_vcf.util.writeVcf import write_vcf
from filter_vcf.util.sortVcf import sort_vcf
from filter_vcf.util.addDepth import add_depth
from filter_vcf.util.cleanAD import clean_ad
from filter_vcf.util.cleanGT import clean_gt
from filter_vcf.util.removeNonRef import filter_non_ref
from filter_vcf.util.detectVcf import detect_vcf
from filter_vcf.util.convertChrName import convert_chr_name
from filter_vcf.util.unique import keep_unique_variants
from filter_vcf.util.checkArgs import check_args


def normalize_vcf(arguments: dict):
    """
    Arguments:
        reference - path to reference genome
            GRCh37 or GRCh38

        input - Path to input vcf file(s) (.vcf/.tcf or .vcf.gz/.tcf.gz).

        output - path for output VCF (.vcf or .vcf.gz)

        decompose - default set to True
            Splits multiallelic variants.

        normalize - default set to True
            Parsimony and left alignment pertaining to the nature of a variant's length and position

        unique - default set to True
            Remove any duplicate variants from VCF

        filterContig - default set to False
            Filters out unsupported contigs from VCF

        depth - default set to True
            Calculate DP (depth) from summing the AD genotype field.

        filters - default set to "PASS"
            List of user specified FILTER labels to keep formatted as string with ":" delimiter. i.e. "PASS:sb"
    """

    with scoped_logger(__name__) as log:
        # Setup file paths and working variables
        args = check_args(arguments, log)

        tmp_dir = f"/tmp/normalize_vcf_{str(uuid.uuid4().hex)[:16]}"
        os.makedirs(f"{tmp_dir}/ref/")

        if args["reference"].endswith("37.fa.gz"):
            ref_file = f"{tmp_dir}/ref/GRCh37.fa.gz"
        elif args["reference"].endswith("38.fa.gz"):
            ref_file = f"{tmp_dir}/ref/GRCh38.fa.gz"
        shutil.copyfile(f"{args['reference']}", ref_file)

        file_name = args["input"].split("/")[-1].replace(" ", "")
        in_file = f"{tmp_dir}/{file_name}"
        if not in_file.endswith(".gz"):
            in_file = in_file + ".gz"

        # Begin vcf processing
        vcf_in = read_vcf(args["input"], log)

        if args["filters"] != "":
            vcf_in = perform_filter_vcf(vcf_in.to_string(), args["filters"], log)

        sorted_vcf = sort_vcf(vcf_in, log)

        write_vcf(vcf_in=sorted_vcf, vcf_out=in_file, compression=True, log=log)

        if args["filterContig"]:
            subprocess.run(f"tabix -p vcf {in_file}", shell=True, check=True)
            regions = ",".join(
                ["chr" + str(i) for i in range(1, 23)]
                + [str(i) for i in range(1, 23)]
                + ["X", "Y", "M", "MT", "chrX", "chrY", "chrM", "chrMT"]
            )
            subprocess.run(
                f'bcftools view  -r "{regions}" {in_file} -o {tmp_dir}/regions.vcf.gz -O z ',
                shell=True,
                check=True,
            )
            os.rename(f"{tmp_dir}/regions.vcf.gz", in_file)

        # Always performed
        working_vcf = read_vcf(in_file, log).to_string()

        if args["depth"]:
            working_vcf = add_depth(working_vcf, log)

        if args["decompose"]:
            write_vcf(working_vcf, in_file, compression=True, log=log)
            subprocess.run(
                f"vt decompose -s {in_file} -o {tmp_dir}/decomposed.vcf", shell=True, check=True
            )
            os.system(f"gzip {tmp_dir}/decomposed.vcf")
            os.rename(f"{tmp_dir}/decomposed.vcf.gz", in_file)
            working_vcf = read_vcf(in_file, log).to_string()
            working_vcf = clean_gt(working_vcf, log)
            working_vcf = clean_ad(working_vcf, log)

        # Always performed
        working_vcf = filter_non_ref(working_vcf, log)

        if args["normalize"]:
            vcfChr = detect_vcf(working_vcf, log)
            log.info(f"Input vcf file <{in_file}> has type <{ vcfChr }>")

            if vcfChr == "chr" and "GRCh37" in args["reference"]:
                working_vcf = convert_chr_name(working_vcf, "num", log)
                write_vcf(working_vcf, in_file, True, log)
                if os.path.exists(f"{in_file}.tbi"):
                    os.remove(f"{in_file}.tbi")
                subprocess.run(f"tabix -p vcf {in_file}", shell=True, check=True)
                subprocess.run(
                    f"vt normalize -n -r {ref_file} {in_file} -o {tmp_dir}/normalized.vcf",
                    shell=True,
                    check=True,
                )
                os.system(f"gzip {tmp_dir}/normalized.vcf")
                os.rename(f"{tmp_dir}/normalized.vcf.gz", in_file)
                working_vcf = read_vcf(in_file, log).to_string()
                working_vcf = convert_chr_name(working_vcf, "chr", log)

            else:
                write_vcf(working_vcf, in_file, True, log)
                if args["filterContig"] == False:
                    subprocess.run(f"tabix -p vcf {in_file}", shell=True, check=True)
                subprocess.run(
                    f"vt normalize -n -r {ref_file} {in_file} -o {tmp_dir}/normalized.vcf",
                    shell=True,
                    check=True,
                )
                os.system(f"gzip {tmp_dir}/normalized.vcf")
                os.rename(f"{tmp_dir}/normalized.vcf.gz", in_file)
                working_vcf = read_vcf(in_file, log).to_string()

        # Always performed
        working_vcf = sort_vcf(working_vcf, log)

        if args["unique"]:
            working_vcf = keep_unique_variants(working_vcf, log)

        log.info(f"Writing output to {args['output']}")
        write_vcf(working_vcf, args["output"], compression=True, log=log)

        return args
