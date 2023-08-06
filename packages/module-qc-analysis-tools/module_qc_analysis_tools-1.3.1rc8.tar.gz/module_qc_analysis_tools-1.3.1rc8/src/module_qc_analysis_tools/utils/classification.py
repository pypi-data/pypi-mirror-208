#!/usr/bin/env python3
from __future__ import annotations

import json
import logging
from pathlib import Path

import jsonschema
import matplotlib.pyplot as plt
import numpy as np
from jsonschema import validate

from module_qc_analysis_tools import data
from module_qc_analysis_tools.utils.misc import bcolors

log = logging.getLogger("analysis")


def format_text_short():
    return " {:^30}: {:^20}"


testbit_map = {
    "DEAD_DIGITAL": 0,
    "BAD_DIGITAL": 1,
    "DEAD_ANALOG": 2,
    "BAD_ANALOG": 3,
    "THRESHOLD_FAILED_FITS": 4,
    "TUNING_BAD": 5,
    "HIGH_ENC": 6,
    "HIGH_NOISE": 7,
    "TOT_MEM": 8,
    "HIGH_XTALK": 9,
}

required_tests = {
    "MIN_HEALTH_TEST": [
        "std_digitalscan",
        "std_analogscan",
        "std_thresholdscan_hr",
        "std_totscan",
    ],
    "TUNING": [
        "std_tune_globalthreshold",
        "std_thresholdscan_hr",
        "std_tune_pixelthreshold",
        "std_retune_globalthreshold",
        "std_retune_pixelthreshold",
        "std_thresholdscan_hd",
        "std_totscan",
    ],
    "PIXEL_FAILURE_ANALYSIS": [
        "std_digitalscan",
        "std_analogscan",
        "std_thresholdscan_hd",
        "std_noisescan",
        "std_discbumpscan",
    ],
}


def get_fail_bit(name):
    if name not in testbit_map:
        log.error(
            bcolors.BADRED
            + f"Asking for bit for {name}, but {name} not present in {testbit_map} - please check!"
            + bcolors.ENDC
        )
        raise RuntimeError()
    return testbit_map.get(name)


def get_name_from_bit(bit):
    try:
        index = list(testbit_map.values()).index(bit)
        name = list(testbit_map.keys())[index]
        return name
    except Exception as err:
        log.error(
            bcolors.BADRED
            + f"Problem finding test name for bit {bit}, please check test name - bit mapping"
            + bcolors.ENDC
        )
        raise RuntimeError() from err


def set_bit(value, bit):
    return value | (1 << bit)


def clear_bit(value, bit):
    return value & ~(1 << bit)


def read_json(input_file):
    try:
        input_data = json.loads(input_file.read_text())
    except Exception as e:
        log.error(
            bcolors.BADRED + f"{input_file} is ill-formatted, please fix" + bcolors.ENDC
        )
        raise RuntimeError() from e
    return input_data


def check_input_yarr_config(input_data, path):
    info_schema_path = str(data / "schema/info_schema.json")
    with Path(info_schema_path).open() as inFile:
        info_schema = json.load(inFile)
    try:
        validate(instance=input_data, schema=info_schema)
    except jsonschema.exceptions.ValidationError as err:
        log.error(
            bcolors.BADRED
            + "Input YARR config fails schema check with the following error:"
            + bcolors.ENDC
        )
        log.error(bcolors.BADRED + f"Input YARR config: {path}" + bcolors.ENDC)
        log.error(bcolors.BADRED + f"Json Schema: {info_schema_path}" + bcolors.ENDC)
        log.error(err.message)
        raise RuntimeError() from None


def check_input_yarr_data(input_data, path, config=False):
    if config:
        input_chipconfig_schema_path = str(data / "schema/input_chipconfig_schema.json")
        with Path(input_chipconfig_schema_path).open() as inFile:
            input_chipconfig_schema = json.load(inFile)
        try:
            validate(instance=input_data, schema=input_chipconfig_schema)
        except jsonschema.exceptions.ValidationError as err:
            log.error(
                bcolors.BADRED
                + "Input chip configuration fails schema check with the following error:"
                + bcolors.ENDC
            )
            log.error(bcolors.BADRED + f"Input chip config: {path}" + bcolors.ENDC)
            log.error(
                bcolors.BADRED
                + f"Json Schema: {input_chipconfig_schema_path}"
                + bcolors.ENDC
            )
            log.error(err.message[0:200] + " ... " + err.message[-200:])
            raise RuntimeError() from None
    else:
        input_yarr_schema_path = str(data / "schema/input_yarr_schema.json")
        with Path(input_yarr_schema_path).open() as inFile:
            input_yarr_schema = json.load(inFile)
        try:
            validate(instance=input_data, schema=input_yarr_schema)
        except jsonschema.exceptions.ValidationError as err:
            log.error(
                bcolors.BADRED
                + "Input YARR data fails schema check with the following error:"
                + bcolors.ENDC
            )
            log.error(bcolors.BADRED + f"Input YARR data: {path}" + bcolors.ENDC)
            log.error(
                bcolors.BADRED + f"Json Schema: {input_yarr_schema_path}" + bcolors.ENDC
            )
            log.error(err.message[0:200] + " ... " + err.message[-200:])
            raise RuntimeError() from None


def format_pixel_input(data):
    data = np.array(data).transpose()
    num_rows, num_cols = data.shape
    data = data.flatten()
    pix_index = np.empty(1)
    pix_index = np.arange(0, 400, dtype=int)
    for r in range(1, num_rows):
        pix_index = np.append(pix_index, np.arange(r * 400, r * 400 + 400, dtype=int))
    return data, pix_index


def format_config_input(config):
    data = config[0].get("TDAC")
    pix_index = np.arange(0, 384 * 400, 400, dtype=int)
    for c in range(1, len(config)):
        data = np.append(data, config[c].get("TDAC"))
        pix_index = np.append(pix_index, np.arange(c, 384 * 400 + c, 400, dtype=int))
    return data, pix_index


def check_test_method(test_method, test_params):
    if test_method == "MinBound":
        if len(test_params) != 1:
            log.error(
                bcolors.BADRED + "MinBound cut requested, but ",
                len(test_params),
                " params provided! Please only provide single lower bound"
                + bcolors.ENDC,
            )
            raise RuntimeError()
    elif test_method == "MaxBound":
        if len(test_params) != 1:
            log.error(
                bcolors.BADRED + "MaxBound cut requested, but ",
                len(test_params),
                " params provided! Please only provide single upper bound"
                + bcolors.ENDC,
            )
            raise RuntimeError()
    elif test_method == "MinMaxBound":
        if len(test_params) != 2:
            log.error(
                bcolors.BADRED + "MinMaxBound cut requested, but ",
                len(test_params),
                " params provided! Please only provide single lower and upper params"
                + bcolors.ENDC,
            )
            raise RuntimeError()
    elif test_method == "RemoveOneValue":
        if len(test_params) != 1:
            log.error(
                bcolors.BADRED + "RemoveOneValue cut requested, but ",
                len(test_params),
                " params provided! Please only provide single value to remove"
                + bcolors.ENDC,
            )
            raise RuntimeError()
    elif test_method == "Outlier":
        if len(test_params) != 1:
            log.error(
                bcolors.BADRED + "Outlier cut requested, but ",
                len(test_params),
                " params provided! Please only provide single value to determine outliers"
                + bcolors.ENDC,
            )
            raise RuntimeError()
    elif test_method == "percentile":
        if len(test_params) != 1:
            log.error(
                bcolors.BADRED + "Percentile cut requested, but ",
                len(test_params),
                " params provided! Please only provide single percentile"
                + bcolors.ENDC,
            )
            raise RuntimeError()
    else:
        log.error(
            bcolors.BADRED
            + f"Method {test_method} not recognized. Skipping"
            + bcolors.ENDC
        )
        return -1
    return 0


def check_record(record_fail, test_name):
    test_bit = set_bit(0, get_fail_bit(test_name))
    return record_fail & test_bit == test_bit


def count_pixels(fail, fail_record, test_names):
    log.info("")
    log.info("Classifying pixel failures!")
    log.info("")
    # Counts pixels that have been classified
    failures = {}
    total_failures = 0
    for t in testbit_map:
        # Skip tests that do not classify pixels
        if t not in test_names:
            log.debug(
                bcolors.WARNING
                + f"count_pixels: {t} not used to classify pixels, skipping "
                + bcolors.ENDC
            )
            continue

        # Only store results that were recorded
        if not check_record(fail_record, t):
            log.debug(
                bcolors.WARNING
                + f"count_pixels: {t} not checked, skipping "
                + bcolors.ENDC
            )
            continue

        failures.update({t: {}})
        fail_bit = set_bit(0, get_fail_bit(t))

        nfail_independent = len(fail[fail & fail_bit == fail_bit])
        failures.get(t).update({"independent": nfail_independent})

        # Count how many pixels have failed this test, and passed all previous tests
        test_bit = 0
        for i in range(0, get_fail_bit(t) + 1):
            if not check_record(fail_record, get_name_from_bit(i)):
                continue
            test_bit = set_bit(test_bit, i)
        nfail_dependent = len(fail[fail & test_bit == fail_bit])
        failures.get(t).update({"dependent": nfail_dependent})
        total_failures += nfail_dependent
        failures.get(t).update({"integrated": total_failures})
    return failures

    # Count failures
    test_bit = set_bit(0, fail_bit)
    return None


def classify_pixels(data, fail, record, test_name, test_method, test_params):
    pix_fail = np.copy(fail)
    fail_bit = get_fail_bit(test_name)

    # Check pixel classification
    error_code = check_test_method(test_method, test_params)
    if error_code:
        return error_code

    # Identify failures
    if test_method == "MinBound":
        failures = np.where(data < test_params[0])

    elif test_method == "MaxBound":
        failures = np.where(data > test_params[0])

    elif test_method == "MinMaxBound":
        failures = np.where((data < test_params[0]) | (data > test_params[1]))

    elif test_method == "RemoveOneValue":
        failures = np.where(data == test_params[0])

    elif test_method == "Outlier":
        mean = np.mean(data)
        failures = np.where(np.abs(data - mean) > test_params[0])

    # Record failures
    record = set_bit(record, fail_bit)
    for f in failures:
        pix_fail[f] = set_bit(fail[f], fail_bit)

    return pix_fail, record


def print_pixel_classification(failure_summary, test_type, outputdir, chipname):
    txt = format_text_short()
    log.info(txt.format("Classification", "Number of pixels"))
    log.info("------------------------------------------------------------------")
    counts_dep = []
    counts_indep = []
    binlabels = []
    for criteria, failures in failure_summary.items():
        log.info(txt.format(criteria, failures.get("dependent")))
        counts_dep += [failures.get("dependent")]
        counts_indep += [failures.get("independent")]
        binlabels += [criteria.replace("_", "\n")]
    log.info("------------------------------------------------------------------")
    log.info(
        txt.format(
            "TOTAL FAILING", list(failure_summary.values())[-1].get("integrated")
        )
    )
    counts_dep += [list(failure_summary.values())[-1].get("integrated")]
    counts_indep += [list(failure_summary.values())[-1].get("integrated")]
    binlabels += ["TOTAL\nFAILING"]
    bins = range(len(counts_dep) + 1)
    log.info("------------------------------------------------------------------")

    # Turn off matplotlib DEBUG messages
    plt.set_loglevel(level="warning")

    # Plot dependent categorization
    fig, ax = plt.subplots()
    ax.set_title(f"{chipname} ({test_type})")
    ax.set_ylim(0, max(counts_dep) + max(counts_dep) / 2)
    plt.stairs(counts_dep[:-1], bins[:-1], fill=True, color="cornflowerblue")
    plt.stairs([counts_dep[-1]], bins[-2:], fill=True, color="lightcoral")

    # Label bins
    plt.xticks([x + 0.5 for x in range(len(counts_dep))], labels=binlabels, rotation=0)
    ax.set_ylabel("Number of pixels")
    plt.text(0.02, 0.92, "Dependent categorization", transform=ax.transAxes)
    plt.text(
        0.02,
        0.85,
        "(Failing pixels included in single category)",
        transform=ax.transAxes,
    )

    # Print bin contents
    for i in range(0, len(counts_dep)):
        if counts_dep[i] > 0:
            plt.text(
                i + 0.5,
                counts_dep[i] + max(counts_dep) / 60,
                counts_dep[i],
                ha="center",
            )

    fig.tight_layout()
    plt.subplots_adjust(bottom=0.3)
    plt.savefig(outputdir.joinpath(f"{chipname}_depclassification.png"))
    log.info("Saving " + str(outputdir.joinpath(f"{chipname}_depclassification.png")))
    plt.close()

    # Plot independent categorization
    fig, ax = plt.subplots()
    ax.set_title(f"{chipname} ({test_type})")
    ax.set_ylim(0, max(counts_indep) + max(counts_indep) / 2)
    plt.stairs(counts_indep[:-1], bins[:-1], fill=True, color="mediumseagreen")
    plt.stairs([counts_indep[-1]], bins[-2:], fill=True, color="lightcoral")

    # Label bins
    plt.xticks(
        [x + 0.5 for x in range(len(counts_indep))], labels=binlabels, rotation=0
    )
    ax.set_ylabel("Number of pixels")
    plt.text(0.02, 0.92, "Independent categorization", transform=ax.transAxes)
    plt.text(
        0.02,
        0.85,
        "(Failing pixels can be included in several categories)",
        transform=ax.transAxes,
    )

    # Print bin contents
    for i in range(0, len(counts_indep)):
        if counts_indep[i] > 0:
            plt.text(
                i + 0.5,
                counts_indep[i] + max(counts_indep) / 60,
                counts_indep[i],
                ha="center",
            )

    fig.tight_layout()
    plt.subplots_adjust(bottom=0.3)
    plt.savefig(outputdir.joinpath(f"{chipname}_indepclassification.png"))
    log.info("Saving " + str(outputdir.joinpath(f"{chipname}_indepclassification.png")))
    plt.close()
