from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import numpy as np
import typer
from module_qc_data_tools import (
    convert_serial_to_name,
    get_layer_from_sn,
    outputDataFrame,
    qcDataFrame,
    save_dict_list,
)

from module_qc_analysis_tools import __version__
from module_qc_analysis_tools.cli.globals import (
    CONTEXT_SETTINGS,
    OPTIONS,
    LogLevel,
)
from module_qc_analysis_tools.utils.analysis import (
    check_layer,
    get_layer,
    perform_qc_analysis,
    print_result_summary,
)
from module_qc_analysis_tools.utils.classification import (
    check_input_yarr_config,
    check_input_yarr_data,
    classify_pixels,
    count_pixels,
    format_pixel_input,
    print_pixel_classification,
    read_json,
)
from module_qc_analysis_tools.utils.misc import (
    bcolors,
    get_qc_config,
)

app = typer.Typer(context_settings=CONTEXT_SETTINGS)

log = logging.getLogger("analysis")


@app.command()
def main(
    input_yarr: Path = OPTIONS["input_yarr_config"],
    qc_criteria_path: Path = OPTIONS["qc_criteria"],
    pixel_classification_path: Path = OPTIONS["pixel_classification"],
    base_output_dir: Path = OPTIONS["output_dir"],
    permodule: bool = OPTIONS["permodule"],
    input_layer: str = OPTIONS["layer"],
    verbosity: LogLevel = OPTIONS["verbosity"],
):
    test_type = Path(__file__).stem
    qc_config = get_qc_config(qc_criteria_path, test_type)

    time_start = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_dir = base_output_dir.joinpath(test_type).joinpath(f"{time_start}")
    output_dir.mkdir(parents=True, exist_ok=False)

    log.setLevel(verbosity.value)
    log.addHandler(logging.FileHandler(f"{output_dir}/output.log"))

    log.info("")
    log.info(" ====================================================")
    log.info(" \tPerforming pixel failure analysis")
    log.info(" ====================================================")
    log.info("")

    input_data = read_json(input_yarr)
    check_input_yarr_config(input_data, path=input_yarr)
    datadir = input_data["datadir"]
    module_sn = input_data["module"]["serialNumber"]
    layer = get_layer_from_sn(module_sn)

    if input_layer == "Unknown":
        try:
            layer = get_layer_from_sn(module_sn)
        except Exception:
            log.error(bcolors.WARNING + " Something went wrong." + bcolors.ENDC)
    else:
        log.warning(
            bcolors.WARNING
            + " Overwriting default layer config {} with manual input {}!".format(
                get_layer_from_sn(module_sn), input_layer
            )
            + bcolors.ENDC
        )
        layer = input_layer
    check_layer(layer)

    pixel_classification = read_json(pixel_classification_path)
    if not pixel_classification.get(test_type):
        log.error(
            bcolors.BADRED
            + f"Pixel failure selection for {test_type} not found in {pixel_classification_path}! Please check. "
            + bcolors.ENDC
        )
        raise RuntimeError()

    alloutput = []
    for c in input_data["chip"]:
        chipSN = c["serialNumber"]
        chipName = convert_serial_to_name(chipSN)
        filepaths = c["filepaths"]
        results = {}
        skip_chip = False

        # Initialize array to track pixel failures
        pix_fail = np.zeros(153600, dtype=np.uint16)

        # Initialize int to track which classifications have been checked
        record_fail = 0

        log.debug(f"Performing pixel failure analysis on chip {c['serialNumber']}")

        """ Prepare output json file """
        outputDF = outputDataFrame()
        outputDF.set_test_type(test_type)
        outputDF.set_serial_num(chipSN)
        data = qcDataFrame()
        data.add_property(
            "ANALYSIS_VERSION",
            __version__,
        )
        data.add_meta_data("QC_LAYER", layer)

        # Loop through pixel failure tests from config file
        for test_name, params in pixel_classification.get(test_type).items():
            log.debug(f"Performing {test_name}")

            test_input = params.get("input")
            test_method = params.get("method")
            test_params = params.get("params")

            # Get layer-specific params if necessary
            if type(test_params) is dict:
                layer_name = get_layer(layer)
                layer_bounds = test_params.get(layer_name)
                if not layer_bounds:
                    log.error(
                        bcolors.ERROR
                        + f" QC selections for {test_name} and {layer_name} do not exist - please check! Skipping."
                        + bcolors.ENDC
                    )
                    continue
                test_params = layer_bounds

            # Check if we have data for that test
            if test_input not in filepaths.keys():
                log.info(
                    bcolors.WARNING
                    + f"YARR data for {test_name} not found in {input_yarr} ({test_input}). PIXEL_FAILURE_ANALYSIS cannot be performed on this chip. Exiting."
                    + bcolors.ENDC
                )
                skip_chip = True
                break

            # Read input YARR scan
            input_data_path = datadir + "/" + filepaths[test_input]
            input_data = read_json(Path(input_data_path))
            check_input_yarr_data(input_data, path=input_data_path)

            pix_data, pix_index = format_pixel_input(input_data.get("Data"))

            # Calculate relevant quantities
            if test_method == "mean":
                if "TDAC" not in test_name:
                    pix_data = pix_data[pix_data > 0]
                results.update({"PIXEL_FAILURE_" + test_name: np.mean(pix_data)})
            elif test_method == "rms":
                if "TDAC" not in test_name:
                    pix_data = pix_data[pix_data > 0]
                results.update({"PIXEL_FAILURE_" + test_name: np.std(pix_data)})
            else:
                log.debug(f"Classifying pixels failing {test_name}")
                pix_fail, record_fail = classify_pixels(
                    pix_data, pix_fail, record_fail, test_name, test_method, test_params
                )
                if np.isscalar(pix_fail):
                    continue

        if skip_chip:
            continue

        chiplog = logging.FileHandler(f"{output_dir}/{chipName}.log")
        log.addHandler(chiplog)
        test_names = pixel_classification.get(test_type).keys()
        failure_summary = count_pixels(pix_fail, record_fail, test_names)
        for fname, nfail in failure_summary.items():
            data.add_parameter(
                "PIXEL_FAILURE_" + fname, round(nfail.get("dependent"), 3)
            )

        print_pixel_classification(failure_summary, test_type, output_dir, chipName)
        total_electrically_failing = list(failure_summary.values())[-1].get(
            "integrated"
        )
        results.update({"ELECTRICALLY_FAILED": total_electrically_failing})
        data.add_parameter(
            "PIXEL_FAILURE_ELECTRICALLY_FAILED", total_electrically_failing
        )

        passes_qc, summary = perform_qc_analysis(test_type, qc_config, layer, results)
        print_result_summary(summary, test_type, output_dir, chipName)
        if passes_qc == -1:
            log.error(
                bcolors.ERROR
                + f" QC analysis for {chipName} was NOT successful. Please fix and re-run. Continuing to next chip.."
                + bcolors.ENDC
            )
            continue
        log.info("")
        if passes_qc:
            log.info(
                f" Chip {chipName} passes QC? "
                + bcolors.OKGREEN
                + f"{passes_qc}"
                + bcolors.ENDC
            )
        else:
            log.info(
                f" Chip {chipName} passes QC? "
                + bcolors.BADRED
                + f"{passes_qc}"
                + bcolors.ENDC
            )
        log.info("")
        log.removeHandler(chiplog)
        chiplog.close()

        # Add placeholders for future selection here
        data.add_parameter("PIXEL_FAILURE_MERGED_BUMPS", -1)
        data.add_parameter("PIXEL_FAILURE_SOURCE_SCAN_DONE", False)
        data.add_parameter("PIXEL_FAILURE_DISCONNECTED_BUMPS_SOURCE_SCAN", -1)
        data.add_parameter("PIXEL_FAILURE_BAD_PIXELS_ZERO_BIAS_SCAN", -1)
        data.add_parameter("PIXEL_FAILURE_DISCONNECTED_BUMPS_ZERO_BIAS_SCAN", -1)
        data.add_parameter("PIXEL_FAILURE_BAD_PIXELS_DISCONNECTED_BUMPS_SCAN", -1)
        data.add_parameter("PIXEL_FAILURE_DISCONNECTED_PIXELS", -1)
        data.add_parameter("PIXEL_FAILURE_FAILING_PIXELS", -1)

        outputDF.set_results(data)
        outputDF.set_pass_flag(passes_qc)

        if permodule:
            alloutput += [outputDF.to_dict(True)]
        else:
            outfile = output_dir.joinpath(f"{chipName}.json")
            log.info(f" Saving output of analysis to: {outfile}")
            save_dict_list(outfile, [outputDF.to_dict(True)])

    if permodule:
        outfile = output_dir.joinpath("module.json")
        log.info(f" Saving output of analysis to: {outfile}")
        save_dict_list(
            outfile,
            alloutput,
        )


if __name__ == "__main__":
    typer.run(main)
