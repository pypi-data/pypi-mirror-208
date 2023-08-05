from logging import Logger
import os
import copy


def check_args(arguments: dict, log: Logger):
    """
    # Implement checks and logs on the input arguments
    Example structure
    {
        'reference': 'PATH/TO/reference.fa.gz',
        'input': 'PATH/TO/input.vcf.gz',
        'output': 'PATH/TO/output.vcf.gz',
        'filters': 'PASS:sb'
        'decompose': True,
        'normalize': True,
        'unique': True,
        'depth': True,
        'filterContig': True,
     }
    """
    approved_args = [
        "reference",
        "input",
        "output",
        "decompose",
        "normalize",
        "unique",
        "filterContig",
        "depth",
        "filters",
    ]
    log.info(f"Input arguments: {arguments}")

    # Check input arguments and transform if required
    checked_arguments = copy.deepcopy(arguments)

    try:
        assert type(arguments) == dict
    except (AssertionError):
        raise TypeError(f"Arguments must be input as dictionary. {type(arguments)} was provided.")

    # Check args have appropriate keys
    try:
        assert set(list(arguments.keys())) == set(approved_args)
    except (AssertionError):
        raise RuntimeError(
            f"Unapproved input arguments detected. Please correct issues with the following arguments {set(list(arguments.keys())) ^ set(approved_args)}"
        )

    # Check formatting of each value
    if len(str(arguments["filters"])) == 0 and True not in list(arguments.values()):
        log.warning("No operations selected")

    # Check reference
    try:
        assert arguments["reference"].endswith(("37.fa.gz", "38.fa.gz"))
    except (AssertionError):
        raise RuntimeError(
            f"Genome reference .fa.gz must be GRCh38 or GRCh37. Given: {arguments['reference']}"
        )

    try:
        assert os.path.isfile(arguments["reference"])
    except (AssertionError):
        raise RuntimeError(f"Genome reference .fa.gz file not found: {arguments['reference']}")

    # Check filters
    try:
        assert type(arguments["filters"]) == str
    except (AssertionError):
        log.warning(
            "Approved filter string not provided. Filter will be disabled and no variants will be filtered."
        )
        checked_arguments["filters"] = ""

    # Check boolean options
    for arg in ["decompose", "normalize", "unique", "filterContig", "depth"]:
        try:
            assert type(arguments[arg]) == bool
        except (AssertionError):
            log.warning(
                f"Approved boolean value not provided for argument: {arg}. Updating to 'True'."
            )
            checked_arguments[arg] = "True"

    # Check output and transform based on filter status
    suffix = ".nrm.vcf"
    if checked_arguments["filters"]:
        suffix = ".filtered" + suffix

    if arguments["output"] == "":
        if arguments["input"].endswith((".vcf", ".vcf.gz")):
            checked_arguments["output"] = arguments["input"].replace(".vcf", suffix)
        elif arguments["input"].endswith((".tcf", ".tcf.gz")):
            checked_arguments["output"] = arguments["input"].replace(".tcf", suffix)

    else:
        try:
            assert arguments["output"].endswith(("vcf", "vcf.gz", ".tcf", ".tcf.gz"))
        except (AssertionError):
            log.warning(
                f"Specified output file must end in .vcf or .vcf.gz. Given: {arguments['output']} \
             Setting output to .vcf.gz format."
            )
            suffix = suffix + ".gz"
            checked_arguments["output"] = arguments["output"] + suffix

    log.info(f"Input arguments approved. Checked arguments: {checked_arguments}")
    return checked_arguments
