import os
import logging
from fuc import pyvcf
import unittest


from filter_vcf.filter_vcf import filter_vcf
from filter_vcf.util.userFilter import perform_filter_vcf
from filter_vcf.util.sortVcf import sort_vcf
from filter_vcf.util.readVcf import read_vcf
from filter_vcf.util.writeVcf import write_vcf
from filter_vcf.util.addDepth import add_depth
from filter_vcf.util.cleanAD import clean_ad
from filter_vcf.util.cleanGT import remove_gt_dot, fix_gt_extra, clean_gt
from filter_vcf.util.removeNonRef import filter_non_ref
from filter_vcf.util.detectVcf import detect_vcf
from filter_vcf.util.convertChrName import convert_chr_name
from filter_vcf.util.unique import keep_unique_variants
from filter_vcf.util.checkArgs import check_args

from filter_vcf.process import normalize_vcf


class MockLog:
    def info(self, _: str):
        return None

    def error(self, _: str):
        return None


mock_log = MockLog()

BASE_PATH = os.path.abspath(os.path.dirname(__file__))


def test_filter_vcf():

    vcf_file = f"{BASE_PATH}/resources/sample.nrm.vcf.gz"

    result = filter_vcf(vcf_file, "PASS:sb", mock_log)

    os.remove(vcf_file.replace("nrm.vcf.gz", "nrm.filtered.vcf.gz"))

    assert result is not None


def test_perform_filter_vcf():

    vcf_for_filtering = str(
        """##fileformat=VCFv4.0
##fileDate=20180419
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	
1	35885022	rs1474253187	T	C	.	PASS	
2	44622946	rs9291422989	C	G	.	sb	
9	30912459	rs1330713521	A	G	.	lowQ	
11	42641414	rs1006891614	C	T	.	PASS;sb	
12	65138464	rs1531215484	A	T	.	lowQ;sb	
"""
    )

    filtered_vcf = perform_filter_vcf(vcf_for_filtering, "PASS:sb", mock_log)

    assert filtered_vcf == str(
        """##fileformat=VCFv4.0
##fileDate=20180419
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	
1	35885022	rs1474253187	T	C	.	PASS	
2	44622946	rs9291422989	C	G	.	sb	
11	42641414	rs1006891614	C	T	.	PASS;sb	
"""
    )


def test_read_vcf():
    unsorted_vcf = read_vcf(f"{BASE_PATH}/resources/unsorted.vcf", mock_log)
    unsorted_vcf_gzip = read_vcf(f"{BASE_PATH}/resources/unsorted.vcf.gz", mock_log)

    assert unsorted_vcf.to_string() == unsorted_vcf_gzip.to_string()


# Test Read VCF Logging Statements
class ReadVcfTest(unittest.TestCase):
    def test_read_vcf_logging(self):
        test_log = logging.getLogger()
        with self.assertLogs(test_log) as cm:
            missing_file = f"{BASE_PATH}/resources/missing.vcf"
            missing_vcf_file = read_vcf(missing_file, test_log)
            self.assertEqual(
                cm.output,
                [
                    f'ERROR:root:Given file path "{missing_file}" could not be located',
                ],
            )

        test_log = logging.getLogger()
        with self.assertLogs(test_log) as cm:
            wrong_format_file = f"{BASE_PATH}/resources/vcf.txt"
            wrong_format_vcf_file = read_vcf(wrong_format_file, test_log)
            self.assertEqual(
                cm.output,
                [
                    f'ERROR:root:Given file "{wrong_format_file}" must be in vcf or vcf.gz format',
                ],
            )


def test_write_vcf():
    os.makedirs(f"{BASE_PATH}/resources/tmp/", exist_ok=True)

    def cleanup():
        os.system(f"rm {BASE_PATH}/resources/tmp/written.vcf.gz")

    working_vcf = str(
        """##fileformat=VCFv4.0
##fileDate=20180419
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
1	35885022	rs1474253187	T	C	.	.	RS=1474253187;RSPOS=35885022;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000020005000002000100;GENEINFO=KCNE1:3753
2	44622946	rs929142298	C	G	.	.	RS=929142298;RSPOS=44622946;dbSNPBuildID=150;SSR=0;SAO=0;VP=0x050000000005000002000100
9	30912459	rs1330713521	A	G	.	.	RS=1330713521;RSPOS=30912459;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=GRIK1:2897
11	42641414	rs1006891614	C	T	.	.	RS=1006891614;RSPOS=42641414;dbSNPBuildID=150;SSR=0;SAO=0;VP=0x050000000005000002000100
"""
    )

    write_vcf(
        working_vcf,
        f"{BASE_PATH}/resources/tmp/written.vcf.gz",
        compression=True,
        log=mock_log,
    )

    assert os.path.exists(f"{BASE_PATH}/resources/tmp/written.vcf.gz") == True
    cleanup()


def test_sort_vcf():
    presorted_vcf = str(
        """##fileformat=VCFv4.0
##fileDate=20180419
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
1	35885022	rs1474253187	T	C	.	.	RS=1474253187;RSPOS=35885022;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000020005000002000100;GENEINFO=KCNE1:3753
1	35910077	rs1293956811	A	G	.	.	RS=1293956811;RSPOS=35910077;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=RCAN1:1827
2	44578967	rs562685327	G	A	.	.	RS=562685327;RSPOS=44578967;dbSNPBuildID=142;SSR=0;SAO=0;VP=0x050000000005000026000100
2	44622946	rs929142298	C	G	.	.	RS=929142298;RSPOS=44622946;dbSNPBuildID=150;SSR=0;SAO=0;VP=0x050000000005000002000100
5	9429578	rs1204957390	C	T	.	.	RS=1204957390;RSPOS=9429578;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000000005000002000100
7	46901014	rs1299817526	CCTCCGACCTCTCTGGCCCTGTGGGT	C	.	.	RS=1299817526;RSPOS=46901015;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000200;GENEINFO=COL18A1:80781
7	48089886	rs1324953777	A	A	.	.	RS=1324953777;RSPOS=48089886;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000000005000002000100
7	48089886	rs1432456686	A	T	.	.	RS=1432456686;RSPOS=48079549;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000880005000002000100;GENEINFO=PRMT2:3275
7	48089886	rs1432456686	T	A	.	.	RS=1432456686;RSPOS=48079549;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000880005000002000100;GENEINFO=PRMT2:3275
7	48089886	rs1432456686	T	T	.	.	RS=1432456686;RSPOS=48079549;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000880005000002000100;GENEINFO=PRMT2:3275
9	30912459	rs1330713521	A	G	.	.	RS=1330713521;RSPOS=30912459;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=GRIK1:2897
11	42641414	rs1006891614	C	T	.	.	RS=1006891614;RSPOS=42641414;dbSNPBuildID=150;SSR=0;SAO=0;VP=0x050000000005000002000100
"""
    )

    unsorted_vcf = pyvcf.VcfFrame.from_file(f"{BASE_PATH}/resources/unsorted.vcf")

    sorted_vcf = sort_vcf(unsorted_vcf.to_string(), mock_log)
    assert presorted_vcf == sorted_vcf


def test_add_depth():
    no_dp_vcf = str(
        """##fileformat=VCFv4.0
##fileDate=20180419
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=VF,Number=1,Type=Float,Description="Variant Frequency">
##FORMAT=<ID=AD,Number=.,Type=Integer,Description="Allele Depth">
##FORMAT=<ID=SB,Number=1,Type=String,Description="Strand Bias with read numbers (Fw/Rv)">
##FORMAT=<ID=SA,Number=2,Type=String,Description="Number of 1) forward ref alleles; 2) reverse ref; 3) forward non-ref; 4) reverse non-ref alleles, used in variant calling">
##FORMAT=<ID=SP,Number=1,Type=Float,Description="Phred of Chi-square p-value for strand bias">
##FORMAT=<ID=SO,Number=1,Type=String,Description="abs(log10( (RefFw*AltRv)/(RefRv*AltFw) )) for strand bias">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT  CASE-ID
chr1	2556714	rs4870	A	G	0.0	Benign	DP=681;TI=NM_003820.3;GI=TNFRSF14;FC=Missense;PC=K17R;DC=c.50A>G;LO=EXON;EXON=1;CI=Benign	GT:VF:AD:SB:SA:SP:SO	1/1:1.000:0,681:327/354:0/0,327/354:0
chr1	2562891	rs2234167	G	A	0.0	Benign	DP=958;TI=NM_003820.3;GI=TNFRSF14;FC=Missense;PC=V241I;DC=c.721G>A;LO=EXON;EXON=7;CI=Benign	GT:VF:AD:SB:SA:SP:SO	0/1:0.453:524,434:417/541:234/290,183/251:4
chr1	7677739	rs3011926	A	G	0.0	rs	DP=1359;TI=NM_015215.3;GI=CAMTA1;FC=Silent;DC=c.2914+6A>G;LO=INTRON;EXON=11	GT:VF:AD:SB:SA:SP:SO	1/1:1.000:0,1359:555/804:0/0,555/804:0
"""
    )

    with_dp_vcf = add_depth(no_dp_vcf, mock_log)
    assert with_dp_vcf == str(
        """##fileformat=VCFv4.0
##fileDate=20180419
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=VF,Number=1,Type=Float,Description="Variant Frequency">
##FORMAT=<ID=AD,Number=.,Type=Integer,Description="Allele Depth">
##FORMAT=<ID=SB,Number=1,Type=String,Description="Strand Bias with read numbers (Fw/Rv)">
##FORMAT=<ID=SA,Number=2,Type=String,Description="Number of 1) forward ref alleles; 2) reverse ref; 3) forward non-ref; 4) reverse non-ref alleles, used in variant calling">
##FORMAT=<ID=SP,Number=1,Type=Float,Description="Phred of Chi-square p-value for strand bias">
##FORMAT=<ID=SO,Number=1,Type=String,Description="abs(log10( (RefFw*AltRv)/(RefRv*AltFw) )) for strand bias">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Read Depth">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT  CASE-ID
chr1	2556714	rs4870	A	G	0.0	Benign	DP=681;TI=NM_003820.3;GI=TNFRSF14;FC=Missense;PC=K17R;DC=c.50A>G;LO=EXON;EXON=1;CI=Benign	GT:VF:AD:SB:SA:SP:SO:DP	1/1:1.000:0,681:327/354:0/0,327/354:0:681
chr1	2562891	rs2234167	G	A	0.0	Benign	DP=958;TI=NM_003820.3;GI=TNFRSF14;FC=Missense;PC=V241I;DC=c.721G>A;LO=EXON;EXON=7;CI=Benign	GT:VF:AD:SB:SA:SP:SO:DP	0/1:0.453:524,434:417/541:234/290,183/251:4:958
chr1	7677739	rs3011926	A	G	0.0	rs	DP=1359;TI=NM_015215.3;GI=CAMTA1;FC=Silent;DC=c.2914+6A>G;LO=INTRON;EXON=11	GT:VF:AD:SB:SA:SP:SO:DP	1/1:1.000:0,1359:555/804:0/0,555/804:0:1359
"""
    )

    prexisting_dp_vcf = str(
        """##fileformat=VCFv4.0
##fileDate=20180419
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=VF,Number=1,Type=Float,Description="Variant Frequency">
##FORMAT=<ID=AD,Number=.,Type=Integer,Description="Allele Depth">
##FORMAT=<ID=SB,Number=1,Type=String,Description="Strand Bias with read numbers (Fw/Rv)">
##FORMAT=<ID=SA,Number=2,Type=String,Description="Number of 1) forward ref alleles; 2) reverse ref; 3) forward non-ref; 4) reverse non-ref alleles, used in variant calling">
##FORMAT=<ID=SP,Number=1,Type=Float,Description="Phred of Chi-square p-value for strand bias">
##FORMAT=<ID=SO,Number=1,Type=String,Description="abs(log10( (RefFw*AltRv)/(RefRv*AltFw) )) for strand bias">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Read Depth">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT  CASE-ID
chr1	2556714	rs4870	A	G	0.0	Benign	DP=681;TI=NM_003820.3;GI=TNFRSF14;FC=Missense;PC=K17R;DC=c.50A>G;LO=EXON;EXON=1;CI=Benign	GT:VF:AD:SB:SA:SP:SO:AD:DP	1/1:1.000:0,681:327/354:0/0,327/354:0:INF:681
chr1	2562891	rs2234167	G	A	0.0	Benign	DP=958;TI=NM_003820.3;GI=TNFRSF14;FC=Missense;PC=V241I;DC=c.721G>A;LO=EXON;EXON=7;CI=Benign	GT:VF:AD:SB:SA:SP:SO:AD:DP	0/1:0.453:524,434:417/541:234/290,183/251:4:0.0:958
chr1	7677739	rs3011926	A	G	0.0	rs	DP=1359;TI=NM_015215.3;GI=CAMTA1;FC=Silent;DC=c.2914+6A>G;LO=INTRON;EXON=11	GT:VF:AD:SB:SA:SP:SO:AD:DP	1/1:1.000:0,1359:555/804:0/0,555/804:0:INF:1359
"""
    )

    assert add_depth(prexisting_dp_vcf, mock_log) == str(
        """##fileformat=VCFv4.0
##fileDate=20180419
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=VF,Number=1,Type=Float,Description="Variant Frequency">
##FORMAT=<ID=AD,Number=.,Type=Integer,Description="Allele Depth">
##FORMAT=<ID=SB,Number=1,Type=String,Description="Strand Bias with read numbers (Fw/Rv)">
##FORMAT=<ID=SA,Number=2,Type=String,Description="Number of 1) forward ref alleles; 2) reverse ref; 3) forward non-ref; 4) reverse non-ref alleles, used in variant calling">
##FORMAT=<ID=SP,Number=1,Type=Float,Description="Phred of Chi-square p-value for strand bias">
##FORMAT=<ID=SO,Number=1,Type=String,Description="abs(log10( (RefFw*AltRv)/(RefRv*AltFw) )) for strand bias">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Read Depth">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT  CASE-ID
chr1	2556714	rs4870	A	G	0.0	Benign	DP=681;TI=NM_003820.3;GI=TNFRSF14;FC=Missense;PC=K17R;DC=c.50A>G;LO=EXON;EXON=1;CI=Benign	GT:VF:AD:SB:SA:SP:SO:AD:DP	1/1:1.000:0,681:327/354:0/0,327/354:0:INF:681
chr1	2562891	rs2234167	G	A	0.0	Benign	DP=958;TI=NM_003820.3;GI=TNFRSF14;FC=Missense;PC=V241I;DC=c.721G>A;LO=EXON;EXON=7;CI=Benign	GT:VF:AD:SB:SA:SP:SO:AD:DP	0/1:0.453:524,434:417/541:234/290,183/251:4:0.0:958
chr1	7677739	rs3011926	A	G	0.0	rs	DP=1359;TI=NM_015215.3;GI=CAMTA1;FC=Silent;DC=c.2914+6A>G;LO=INTRON;EXON=11	GT:VF:AD:SB:SA:SP:SO:AD:DP	1/1:1.000:0,1359:555/804:0/0,555/804:0:INF:1359
"""
    )


def test_remove_gt_dot():
    vcf_with_gt_dots = str(
        """##fileformat=VCFv4.0
##fileDate=20180419
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=AD,Number=.,Type=Integer,Description="Allele Depth">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Total read depth at the locus">
##INFO=<ID=DP,Number=1,Type=Integer,Description="Total read depth at the locus">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT  SAMPLE1
chrX	154766321	rs2728532	G	A	0	rs	DP=908	GT:AD:DP	0/1/2/3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/./2/3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/././3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/././.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	./1/2/3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	././2/3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	./././3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	./1/./3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/./2/.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/1/2/.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/0/1/1:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/0/1/2:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/./0/.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/././0:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	./0/1/.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	./0/0/.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/0/0/.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/0/1/.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	.|0|.|.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	.|.|0|.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	.|.|.|0:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/1:146:0,10,62,84
"""
    )
    vcf_with_corrected_gt = remove_gt_dot(vcf_with_gt_dots, mock_log)
    assert vcf_with_corrected_gt == str(
        """##fileformat=VCFv4.0
##fileDate=20180419
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=AD,Number=.,Type=Integer,Description="Allele Depth">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Total read depth at the locus">
##INFO=<ID=DP,Number=1,Type=Integer,Description="Total read depth at the locus">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT  SAMPLE1
chrX	154766321	rs2728532	G	A	0	rs	DP=908	GT:AD:DP	0/1/2/3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/./2/3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/././.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	./1/2/3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	2/3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	./././3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	1/3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/2:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/1/2/.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/0/1/1:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/0/1/2:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/0:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/0:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/1:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/0:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/0/0/.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/0/1/.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	.|0|.|.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	.|.|0|.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	.|.|.|0:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/1:146:0,10,62,84
"""
    )


def test_fix_gt_extra():
    vcf_with_gt_extra = str(
        """##fileformat=VCFv4.0
##fileDate=20180419
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=AD,Number=.,Type=Integer,Description="Allele Depth">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Total read depth at the locus">
##INFO=<ID=DP,Number=1,Type=Integer,Description="Total read depth at the locus">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT  SAMPLE1
chrX	154766321	rs2728532	G	A	0	rs	DP=908	GT:AD:DP	0/1/2/3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/./2/3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/././.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	./1/2/3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	2/3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	./././3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	1/3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/2:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/1/2/.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/0/1/1:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/0/1/2:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/0:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/0:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/1:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/0:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/0/0/.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/0/1/.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	.|0|.|.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	.|.|0|.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	.|.|.|0:146:0,10,62,84
"""
    )
    vcf_with_corrected_gt = fix_gt_extra(vcf_with_gt_extra, mock_log)
    assert vcf_with_corrected_gt == str(
        """##fileformat=VCFv4.0
##fileDate=20180419
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=AD,Number=.,Type=Integer,Description="Allele Depth">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Total read depth at the locus">
##INFO=<ID=DP,Number=1,Type=Integer,Description="Total read depth at the locus">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT  SAMPLE1
chrX	154766321	rs2728532	G	A	0	rs	DP=908	GT:AD:DP	0/1:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	./1:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	2/3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	./3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	1/3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/2:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/1:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/1:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/1:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/0:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/0:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/1:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/0:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/1:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	.|0:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	.|0:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	.|0:146:0,10,62,84
"""
    )


def test_cleanGT():
    vcf_for_clean_gt = str(
        """##fileformat=VCFv4.0
##fileDate=20180419
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=AD,Number=.,Type=Integer,Description="Allele Depth">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Total read depth at the locus">
##INFO=<ID=DP,Number=1,Type=Integer,Description="Total read depth at the locus">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT  SAMPLE1
chrX	154766321	rs2728532	G	A	0	rs	DP=908	GT:AD:DP	0/1/2/3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/./2/3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/././3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/././.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	./1/2/3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	././2/3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	./././3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	./1/./3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/./2/.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/1/2/.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/0/1/1:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/0/1/2:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/./0/.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/././0:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	./0/1/.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	./0/0/.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/0/0/.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/0/1/.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	.|0|.|.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	.|.|0|.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	.|.|.|0:146:0,10,62,84
"""
    )
    vcf_with_corrected_gt = clean_gt(vcf_for_clean_gt, mock_log)
    assert vcf_with_corrected_gt == str(
        """##fileformat=VCFv4.0
##fileDate=20180419
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=AD,Number=.,Type=Integer,Description="Allele Depth">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Total read depth at the locus">
##INFO=<ID=DP,Number=1,Type=Integer,Description="Total read depth at the locus">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT  SAMPLE1
chrX	154766321	rs2728532	G	A	0	rs	DP=908	GT:AD:DP	0/1:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	./1:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	2/3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	./3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	1/3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/2:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/1:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/1:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/1:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/0:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/0:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/1:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/0:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/.:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/1:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	.|0:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	.|0:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	.|0:146:0,10,62,84
"""
    )


def test_clean_ad():
    decomposed_vcf = str(
        """##fileformat=VCFv4.0
##fileDate=20180419
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=VF,Number=1,Type=Float,Description="Variant Frequency">
##FORMAT=<ID=AD,Number=.,Type=Integer,Description="Allele Depth">
##FORMAT=<ID=SB,Number=1,Type=String,Description="Strand Bias with read numbers (Fw/Rv)">
##FORMAT=<ID=SA,Number=2,Type=String,Description="Number of 1) forward ref alleles; 2) reverse ref; 3) forward non-ref; 4) reverse non-ref alleles, used in variant calling">
##FORMAT=<ID=SP,Number=1,Type=Float,Description="Phred of Chi-square p-value for strand bias">
##FORMAT=<ID=SO,Number=1,Type=String,Description="abs(log10( (RefFw*AltRv)/(RefRv*AltFw) )) for strand bias">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT  CASE-ID
chr1	2556714	rs4870	A	G	0.0	Benign	DP=681;TI=NM_003820.3;GI=TNFRSF14;FC=Missense;PC=K17R;DC=c.50A>G;LO=EXON;EXON=1;CI=Benign	GT:VF:AD:SB:SA:SP:SO	1/1:1.000:0,681:327/354:0/0,327/354:0
chrX	154766321	rs2728532	G	A	0	rs	DP=908;TI=NM_001363.4;GI=DKC1;FC=Synonymous;PC=T123=;DC=c.369G>T;LO=EXON;EXON=5;OLD_MULTIALLELIC=chrX:154766321:G/A/T	GT:VF:AD:SB:SA:SP:SO:DP	1/.:1:0,900,8:425/483:0/0,425/483:0:INF:908
chrX	154766321	rs2728532	G	T	0	rs	DP=908;TI=NM_001363.4;GI=DKC1;FC=Synonymous;PC=T123=;DC=c.369G>T;LO=EXON;EXON=5;OLD_MULTIALLELIC=chrX:154766321:G/A/T	GT:VF:AD:SB:SA:SP:SO:DP	./1:1:0,900,8:425/483:0/0,425/483:0:INF:908
"""
    )

    cleaned_ad_vcf = clean_ad(decomposed_vcf, mock_log)
    assert cleaned_ad_vcf == str(
        """##fileformat=VCFv4.0
##fileDate=20180419
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=VF,Number=1,Type=Float,Description="Variant Frequency">
##FORMAT=<ID=AD,Number=.,Type=Integer,Description="Allele Depth">
##FORMAT=<ID=SB,Number=1,Type=String,Description="Strand Bias with read numbers (Fw/Rv)">
##FORMAT=<ID=SA,Number=2,Type=String,Description="Number of 1) forward ref alleles; 2) reverse ref; 3) forward non-ref; 4) reverse non-ref alleles, used in variant calling">
##FORMAT=<ID=SP,Number=1,Type=Float,Description="Phred of Chi-square p-value for strand bias">
##FORMAT=<ID=SO,Number=1,Type=String,Description="abs(log10( (RefFw*AltRv)/(RefRv*AltFw) )) for strand bias">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT  CASE-ID
chr1	2556714	rs4870	A	G	0.0	Benign	DP=681;TI=NM_003820.3;GI=TNFRSF14;FC=Missense;PC=K17R;DC=c.50A>G;LO=EXON;EXON=1;CI=Benign	GT:VF:AD:SB:SA:SP:SO	1/1:1.000:0,681:327/354:0/0,327/354:0
chrX	154766321	rs2728532	G	A	0	rs	DP=908;TI=NM_001363.4;GI=DKC1;FC=Synonymous;PC=T123=;DC=c.369G>T;LO=EXON;EXON=5;OLD_MULTIALLELIC=chrX:154766321:G/A/T	GT:VF:AD:SB:SA:SP:SO:DP	1/.:1:0,900:425/483:0/0,425/483:0:INF:908
chrX	154766321	rs2728532	G	T	0	rs	DP=908;TI=NM_001363.4;GI=DKC1;FC=Synonymous;PC=T123=;DC=c.369G>T;LO=EXON;EXON=5;OLD_MULTIALLELIC=chrX:154766321:G/A/T	GT:VF:AD:SB:SA:SP:SO:DP	./1:1:0,8:425/483:0/0,425/483:0:INF:908
"""
    )


def test_remove_non_ref():
    vcf_with_non_ref = str(
        """##fileformat=VCFv4.0
##fileDate=20180419
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=AD,Number=.,Type=Integer,Description="Allele Depth">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Total read depth at the locus">
##INFO=<ID=DP,Number=1,Type=Integer,Description="Total read depth at the locus">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT  SAMPLE1
chrX	154766321	rs2728532	G	<NON_REF>	0	rs	DP=908	GT:AD:DP	1/3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	1/3:146:0,10,62,84
chrX	154766321	rs2728532	G	<NON_REF>	0	rs	DP=908	GT:AD:DP	1/3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/1:146:0,10,62,84
"""
    )

    vcf_without_non_ref = filter_non_ref(vcf_with_non_ref, mock_log)

    assert vcf_without_non_ref == str(
        """##fileformat=VCFv4.0
##fileDate=20180419
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=AD,Number=.,Type=Integer,Description="Allele Depth">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Total read depth at the locus">
##INFO=<ID=DP,Number=1,Type=Integer,Description="Total read depth at the locus">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT  SAMPLE1
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	1/3:146:0,10,62,84
chrX	154766321	rs2728532	G	T	0	rs	DP=908	GT:AD:DP	0/1:146:0,10,62,84
"""
    )


def test_detect_vcf():
    num_vcf = str(
        """##fileformat=VCFv4.0
##fileDate=20180419
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
1	35910077	rs1293956811	A	G	.	.	RS=1293956811;RSPOS=35910077;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=RCAN1:1827
2	44578967	rs562685327	G	A	.	.	RS=562685327;RSPOS=44578967;dbSNPBuildID=142;SSR=0;SAO=0;VP=0x050000000005000026000100
7	46901014	rs1299817526	CCTCCGACCTCTCTGGCCCTGTGGGT	C	.	.	RS=1299817526;RSPOS=46901015;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000200;GENEINFO=COL18A1:80781
5	9429578	rs1204957390	C	T	.	.	RS=1204957390;RSPOS=9429578;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000000005000002000100
7	48089886	rs1324953777	A	A	.	.	RS=1324953777;RSPOS=48089886;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000000005000002000100
2	44622946	rs929142298	C	G	.	.	RS=929142298;RSPOS=44622946;dbSNPBuildID=150;SSR=0;SAO=0;VP=0x050000000005000002000100
7	48089886	rs1432456686	T	T	.	.	RS=1432456686;RSPOS=48079549;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000880005000002000100;GENEINFO=PRMT2:3275
11	42641414	rs1006891614	C	T	.	.	RS=1006891614;RSPOS=42641414;dbSNPBuildID=150;SSR=0;SAO=0;VP=0x050000000005000002000100
9	30912459	rs1330713521	A	G	.	.	RS=1330713521;RSPOS=30912459;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=GRIK1:2897
"""
    )

    num_var = detect_vcf(num_vcf, mock_log)

    assert num_var == "num"

    chr_vcf = str(
        """##fileformat=VCFv4.0
##fileDate=20180419
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
chr1	35910077	rs1293956811	A	G	.	.	RS=1293956811;RSPOS=35910077;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=RCAN1:1827
chr2	44578967	rs562685327	G	A	.	.	RS=562685327;RSPOS=44578967;dbSNPBuildID=142;SSR=0;SAO=0;VP=0x050000000005000026000100
chr7	46901014	rs1299817526	CCTCCGACCTCTCTGGCCCTGTGGGT	C	.	.	RS=1299817526;RSPOS=46901015;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000200;GENEINFO=COL18A1:80781
chr5	9429578	rs1204957390	C	T	.	.	RS=1204957390;RSPOS=9429578;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000000005000002000100
chr7	48089886	rs1324953777	A	A	.	.	RS=1324953777;RSPOS=48089886;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000000005000002000100
chr2	44622946	rs929142298	C	G	.	.	RS=929142298;RSPOS=44622946;dbSNPBuildID=150;SSR=0;SAO=0;VP=0x050000000005000002000100
chr7	48089886	rs1432456686	T	T	.	.	RS=1432456686;RSPOS=48079549;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000880005000002000100;GENEINFO=PRMT2:3275
chr11	42641414	rs1006891614	C	T	.	.	RS=1006891614;RSPOS=42641414;dbSNPBuildID=150;SSR=0;SAO=0;VP=0x050000000005000002000100
chr9	30912459	rs1330713521	A	G	.	.	RS=1330713521;RSPOS=30912459;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=GRIK1:2897
"""
    )

    chr_var = detect_vcf(chr_vcf, mock_log)

    assert chr_var == "chr"


def test_convert_chr_name():
    num_to_chr_vcf = str(
        """##fileformat=VCFv4.0
##fileDate=20180419
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
1	35910077	rs1293956811	A	G	.	.	RS=1293956811;RSPOS=35910077;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=RCAN1:1827
2	44578967	rs562685327	G	A	.	.	RS=562685327;RSPOS=44578967;dbSNPBuildID=142;SSR=0;SAO=0;VP=0x050000000005000026000100
7	46901014	rs1299817526	CCTCCGACCTCTCTGGCCCTGTGGGT	C	.	.	RS=1299817526;RSPOS=46901015;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000200;GENEINFO=COL18A1:80781
5	9429578	rs1204957390	C	T	.	.	RS=1204957390;RSPOS=9429578;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000000005000002000100
7	48089886	rs1324953777	A	A	.	.	RS=1324953777;RSPOS=48089886;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000000005000002000100
2	44622946	rs929142298	C	G	.	.	RS=929142298;RSPOS=44622946;dbSNPBuildID=150;SSR=0;SAO=0;VP=0x050000000005000002000100
7	48089886	rs1432456686	T	T	.	.	RS=1432456686;RSPOS=48079549;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000880005000002000100;GENEINFO=PRMT2:3275
11	42641414	rs1006891614	C	T	.	.	RS=1006891614;RSPOS=42641414;dbSNPBuildID=150;SSR=0;SAO=0;VP=0x050000000005000002000100
MT	30912459	rs1330713521	A	G	.	.	RS=1330713521;RSPOS=30912459;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=GRIK1:2897
"""
    )

    converted_num_to_chr = convert_chr_name(num_to_chr_vcf, chr_var="chr", log=mock_log)

    assert converted_num_to_chr == str(
        """##fileformat=VCFv4.0
##fileDate=20180419
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
chr1	35910077	rs1293956811	A	G	.	.	RS=1293956811;RSPOS=35910077;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=RCAN1:1827
chr2	44578967	rs562685327	G	A	.	.	RS=562685327;RSPOS=44578967;dbSNPBuildID=142;SSR=0;SAO=0;VP=0x050000000005000026000100
chr7	46901014	rs1299817526	CCTCCGACCTCTCTGGCCCTGTGGGT	C	.	.	RS=1299817526;RSPOS=46901015;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000200;GENEINFO=COL18A1:80781
chr5	9429578	rs1204957390	C	T	.	.	RS=1204957390;RSPOS=9429578;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000000005000002000100
chr7	48089886	rs1324953777	A	A	.	.	RS=1324953777;RSPOS=48089886;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000000005000002000100
chr2	44622946	rs929142298	C	G	.	.	RS=929142298;RSPOS=44622946;dbSNPBuildID=150;SSR=0;SAO=0;VP=0x050000000005000002000100
chr7	48089886	rs1432456686	T	T	.	.	RS=1432456686;RSPOS=48079549;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000880005000002000100;GENEINFO=PRMT2:3275
chr11	42641414	rs1006891614	C	T	.	.	RS=1006891614;RSPOS=42641414;dbSNPBuildID=150;SSR=0;SAO=0;VP=0x050000000005000002000100
chrM	30912459	rs1330713521	A	G	.	.	RS=1330713521;RSPOS=30912459;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=GRIK1:2897
"""
    )

    chr_to_num_vcf = str(
        """##fileformat=VCFv4.0
##fileDate=20180419
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
chr1	35910077	rs1293956811	A	G	.	.	RS=1293956811;RSPOS=35910077;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=RCAN1:1827
chr2	44578967	rs562685327	G	A	.	.	RS=562685327;RSPOS=44578967;dbSNPBuildID=142;SSR=0;SAO=0;VP=0x050000000005000026000100
chr7	46901014	rs1299817526	CCTCCGACCTCTCTGGCCCTGTGGGT	C	.	.	RS=1299817526;RSPOS=46901015;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000200;GENEINFO=COL18A1:80781
chr5	9429578	rs1204957390	C	T	.	.	RS=1204957390;RSPOS=9429578;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000000005000002000100
chr7	48089886	rs1324953777	A	A	.	.	RS=1324953777;RSPOS=48089886;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000000005000002000100
chr2	44622946	rs929142298	C	G	.	.	RS=929142298;RSPOS=44622946;dbSNPBuildID=150;SSR=0;SAO=0;VP=0x050000000005000002000100
chr7	48089886	rs1432456686	T	T	.	.	RS=1432456686;RSPOS=48079549;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000880005000002000100;GENEINFO=PRMT2:3275
chr11	42641414	rs1006891614	C	T	.	.	RS=1006891614;RSPOS=42641414;dbSNPBuildID=150;SSR=0;SAO=0;VP=0x050000000005000002000100
chrM	30912459	rs1330713521	A	G	.	.	RS=1330713521;RSPOS=30912459;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=GRIK1:2897
"""
    )

    converted_chr_to_num = convert_chr_name(chr_to_num_vcf, chr_var="num", log=mock_log)

    assert converted_chr_to_num == str(
        """##fileformat=VCFv4.0
##fileDate=20180419
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
1	35910077	rs1293956811	A	G	.	.	RS=1293956811;RSPOS=35910077;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=RCAN1:1827
2	44578967	rs562685327	G	A	.	.	RS=562685327;RSPOS=44578967;dbSNPBuildID=142;SSR=0;SAO=0;VP=0x050000000005000026000100
7	46901014	rs1299817526	CCTCCGACCTCTCTGGCCCTGTGGGT	C	.	.	RS=1299817526;RSPOS=46901015;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000200;GENEINFO=COL18A1:80781
5	9429578	rs1204957390	C	T	.	.	RS=1204957390;RSPOS=9429578;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000000005000002000100
7	48089886	rs1324953777	A	A	.	.	RS=1324953777;RSPOS=48089886;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000000005000002000100
2	44622946	rs929142298	C	G	.	.	RS=929142298;RSPOS=44622946;dbSNPBuildID=150;SSR=0;SAO=0;VP=0x050000000005000002000100
7	48089886	rs1432456686	T	T	.	.	RS=1432456686;RSPOS=48079549;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000880005000002000100;GENEINFO=PRMT2:3275
11	42641414	rs1006891614	C	T	.	.	RS=1006891614;RSPOS=42641414;dbSNPBuildID=150;SSR=0;SAO=0;VP=0x050000000005000002000100
MT	30912459	rs1330713521	A	G	.	.	RS=1330713521;RSPOS=30912459;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=GRIK1:2897
"""
    )


def test_keep_unique_variants():
    vcf_with_dups = str(
        """##fileformat=VCFv4.0
##fileDate=20180419
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
1	35910077	rs1293956811	A	G	.	.	RS=1293956811;RSPOS=35910077;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=RCAN1:1827
1	35910077	rs1293956811	A	G	.	.	RS=1293956811;RSPOS=35910077;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=RCAN1:1827
2	44578967	rs562685327	G	A	.	.	RS=562685327;RSPOS=44578967;dbSNPBuildID=142;SSR=0;SAO=0;VP=0x050000000005000026000100
7	46901014	rs1299817526	CCTCCGACCTCTCTGGCCCTGTGGGT	C	.	.	RS=1299817526;RSPOS=46901015;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000200;GENEINFO=COL18A1:80781
9	46901014	rs1299817526	CCTCCGACCTCTCTGGCCCTGTGGGT	C	.	.	RS=1299817526;RSPOS=46901015;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000200;GENEINFO=COL18A1:80781
"""
    )

    vcf_no_dups = keep_unique_variants(vcf_with_dups, log=mock_log)

    assert vcf_no_dups == str(
        """##fileformat=VCFv4.0
##fileDate=20180419
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
1	35910077	rs1293956811	A	G	.	.	RS=1293956811;RSPOS=35910077;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000100;GENEINFO=RCAN1:1827
2	44578967	rs562685327	G	A	.	.	RS=562685327;RSPOS=44578967;dbSNPBuildID=142;SSR=0;SAO=0;VP=0x050000000005000026000100
7	46901014	rs1299817526	CCTCCGACCTCTCTGGCCCTGTGGGT	C	.	.	RS=1299817526;RSPOS=46901015;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000200;GENEINFO=COL18A1:80781
9	46901014	rs1299817526	CCTCCGACCTCTCTGGCCCTGTGGGT	C	.	.	RS=1299817526;RSPOS=46901015;dbSNPBuildID=151;SSR=0;SAO=0;VP=0x050000080005000002000200;GENEINFO=COL18A1:80781
"""
    )


class checkArgsErrors(unittest.TestCase):
    def test_check_args_errors(self):
        with self.assertRaises(TypeError) as cm:
            arguments = [
                {
                    "reference": f"{BASE_PATH}/resources/GRCh37.fa.gz",
                    "input": f"{BASE_PATH}/resources/foundationSample.tcf.gz",
                    "output": "",
                    "decompose": True,
                    "normalize": True,
                    "unique": True,
                    "filterContig": True,
                    "depth": True,
                    "filters": "PASS:sb",
                }
            ]

            check_args(arguments, mock_log)

            self.assertTrue(
                f"Arguments must be input as dictionary. str was provided." in str(cm.exception)
            )

        with self.assertRaises(RuntimeError) as cm:
            arguments = {
                "reference": f"{BASE_PATH}/resources/GRCh37.fa.gz",
                "input": f"{BASE_PATH}/resources/foundationSample.tcf.gz",
                "output": "",
                "INCORRECT": True,
                "normalize": True,
                "unique": True,
                "filterContig": True,
                "depth": True,
                "filters": "PASS:sb",
            }

            check_args(arguments, mock_log)

            self.assertTrue(
                f"Unapproved input arguments detected. Please correct issues with the following arguments {{'INCORRECT', 'decompose'}}"
                in str(cm.exception)
            )

        with self.assertRaises(RuntimeError) as cm:
            arguments = {
                "reference": f"{BASE_PATH}/resources/GRCh99.fa.gz",
                "input": f"{BASE_PATH}/resources/foundationSample.tcf.gz",
                "output": "",
                "decompose": True,
                "normalize": True,
                "unique": True,
                "filterContig": True,
                "depth": True,
                "filters": "PASS:sb",
            }

            check_args(arguments, mock_log)

            self.assertTrue(
                f"Genome reference .fa.gz must be GRCh38 or GRCh37. Given: {arguments['reference']}"
                in str(cm.exception)
            )

        with self.assertRaises(RuntimeError) as cm:
            arguments = {
                "reference": f"{BASE_PATH}/resources/GRCh38.fa.gz",
                "input": f"{BASE_PATH}/resources/foundationSample.tcf.gz",
                "output": "",
                "decompose": True,
                "normalize": True,
                "unique": True,
                "filterContig": True,
                "depth": True,
                "filters": "PASS:sb",
            }

            check_args(arguments, mock_log)

            self.assertTrue(
                f"Genome reference .fa.gz file not found: {arguments['reference']}"
                in str(cm.exception)
            )


class checkArgsLogs(unittest.TestCase):
    def test_check_args_logs(self):
        test_log = logging.getLogger()

        with self.assertLogs(test_log) as cm:
            arguments = {
                "reference": f"{BASE_PATH}/resources/GRCh37.fa.gz",
                "input": f"{BASE_PATH}/resources/foundationSample.tcf.gz",
                "output": "",
                "decompose": False,
                "normalize": False,
                "unique": False,
                "filterContig": False,
                "depth": False,
                "filters": "",
            }

            check_args(arguments, test_log)

            self.assertTrue(
                cm.output[1],
                f"WARN:root:No operations selected",
            )

        with self.assertLogs(test_log) as cm:
            arguments = {
                "reference": f"{BASE_PATH}/resources/GRCh37.fa.gz",
                "input": f"{BASE_PATH}/resources/foundationSample.tcf.gz",
                "output": "",
                "decompose": True,
                "normalize": True,
                "unique": True,
                "filterContig": True,
                "depth": True,
                "filters": True,
            }

            check_args(arguments, test_log)

            self.assertTrue(
                cm.output[1],
                "Approved filter string not provided. Filter will be disabled and no variants will be filtered.",
            )

        with self.assertLogs(test_log) as cm:
            arguments = {
                "reference": f"{BASE_PATH}/resources/GRCh37.fa.gz",
                "input": f"{BASE_PATH}/resources/foundationSample.tcf.gz",
                "output": "",
                "decompose": "Yes",
                "normalize": "Yes",
                "unique": "Yes",
                "filterContig": "Yes",
                "depth": "Yes",
                "filters": "PASS:sb",
            }

            check_args(arguments, test_log)

            self.assertTrue(
                cm.output[1],
                "Approved boolean value not provided for argument: decompose. Updating to 'True'.",
            )
            self.assertTrue(
                cm.output[2],
                "Approved boolean value not provided for argument: normalize. Updating to 'True'.",
            )
            self.assertTrue(
                cm.output[3],
                "Approved boolean value not provided for argument: unique. Updating to 'True'.",
            )
            self.assertTrue(
                cm.output[4],
                "Approved boolean value not provided for argument: filterContig. Updating to 'True'.",
            )
            self.assertTrue(
                cm.output[5],
                "Approved boolean value not provided for argument: depth. Updating to 'True'.",
            )

        with self.assertLogs(test_log) as cm:
            arguments = {
                "reference": f"{BASE_PATH}/resources/GRCh37.fa.gz",
                "input": f"{BASE_PATH}/resources/foundationSample.tcf.gz",
                "output": "testOutput",
                "decompose": True,
                "normalize": True,
                "unique": True,
                "filterContig": True,
                "depth": True,
                "filters": "PASS:sb",
            }

            check_args(arguments, test_log)

            self.assertTrue(
                cm.output[1],
                f"Specified output file must end in .vcf or .vcf.gz. Given: testOutput \
             Setting output to .vcf.gz format.",
            )

        with self.assertLogs(test_log) as cm:
            arguments = {
                "reference": f"{BASE_PATH}/resources/GRCh37.fa.gz",
                "input": f"{BASE_PATH}/resources/foundationSample.tcf.gz",
                "output": "",
                "decompose": True,
                "normalize": True,
                "unique": True,
                "filterContig": True,
                "depth": "Yes",
                "filters": "",
            }

            check_args(arguments, test_log)

            self.assertTrue(
                cm.output[0],
                f'Input arguments approved. Checked arguments: {{ "reference": f"{BASE_PATH}/resources/GRCh37.fa.gz", "input": f"{BASE_PATH}/resources/foundationSample.tcf.gz", "output": "", "decompose": True, "normalize": True, "unique": True, "filterContig": True, "depth": "Yes", "filters": "PASS:sb"}}',
            )
            self.assertTrue(
                cm.output[2],
                f'Input arguments approved. Checked arguments: {{ "reference": f"{BASE_PATH}/resources/GRCh37.fa.gz", "input": f"{BASE_PATH}/resources/foundationSample.tcf.gz", "output": f"{BASE_PATH}/resources/foundationSample.nrm.vcf.gz", "decompose": True, "normalize": True, "unique": True, "filterContig": True, "depth": True, "filters": "PASS:sb"}}',
            )


# System test - can't test some args without containerizing due to reliance on command line tools
def test_normalize_vcf():
    arguments = {
        "reference": f"{BASE_PATH}/resources/GRCh37.fa.gz",
        "input": f"{BASE_PATH}/resources/carisSample.lifted.modified.somatic.vcf.gz",
        "output": "",
        "decompose": False,
        "normalize": False,
        "unique": True,
        "filterContig": False,
        "depth": True,
        "filters": "PASS",
    }

    args = normalize_vcf(arguments)

    assert (
        os.path.exists(
            f"{BASE_PATH}/resources/carisSample.lifted.modified.somatic.filtered.nrm.vcf.gz"
        )
        == True
    )
    os.remove(f"{BASE_PATH}/resources/carisSample.lifted.modified.somatic.filtered.nrm.vcf.gz")

    assert args == {
        "reference": f"{BASE_PATH}/resources/GRCh37.fa.gz",
        "input": f"{BASE_PATH}/resources/carisSample.lifted.modified.somatic.vcf.gz",
        "output": f"{BASE_PATH}/resources/carisSample.lifted.modified.somatic.filtered.nrm.vcf.gz",
        "decompose": False,
        "normalize": False,
        "unique": True,
        "filterContig": False,
        "depth": True,
        "filters": "PASS",
    }
