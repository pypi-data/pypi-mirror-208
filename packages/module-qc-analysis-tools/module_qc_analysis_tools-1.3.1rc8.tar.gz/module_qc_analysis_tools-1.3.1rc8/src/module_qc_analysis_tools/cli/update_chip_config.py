from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
import typer
from module_qc_data_tools import convert_name_to_serial

from module_qc_analysis_tools.cli.globals import CONTEXT_SETTINGS, OPTIONS
from module_qc_analysis_tools.utils.misc import get_inputs, lookup

log = logging.getLogger(__name__)
log.setLevel("INFO")


class WriteConfig:
    ##############
    # This class converts a parameter in a chip config to a given value.
    # `in_path` must be the path to the output directory of the analysis.
    # `config_path` must be the path to the directory ofchip config file in Yarr.
    # If `permodule`, the paths provided much be the path of the correct directory.
    ##############
    def __init__(
        self,
        in_path: Path | None = None,
        config_path: Path | None = None,
        config_type: str | None = None,
        override: bool | None = None,
    ):
        self.in_path = in_path or Path()
        _config_path = config_path or Path()
        self.config_path = (
            _config_path.joinpath(config_type) if config_type else _config_path
        )
        self.stack = []
        self.all_test_types = [
            "ADC_CALIBRATION",
            "ANALOG_READBACK",
            "VCAL_CALIBRATION",
            "INJECTION_CAPACITANCE",
        ]
        self.config_chip_name = ""
        self.in_files = get_inputs(self.in_path)
        self.config_files = get_inputs(self.config_path)
        self.override = override

    def reset_stack(self):
        self.stack = []

    def set_ADCcalPar(self, in_file, config_file):
        # Set the calibrated ADC parameters from the analysis.
        ADC_CALIBRATION_SLOPE = float(lookup(in_file, "ADC_CALIBRATION_SLOPE"))
        ADC_CALIBRATION_OFFSET = float(lookup(in_file, "ADC_CALIBRATION_OFFSET"))
        self.overwrite(config_file, "ADCcalPar", ADC_CALIBRATION_SLOPE, index=1)
        self.overwrite(config_file, "ADCcalPar", ADC_CALIBRATION_OFFSET, index=0)

    def set_trim(self, in_file, config_file):
        # Set the trim values that gives the closest to nominal vdd value.
        vdda = np.array(lookup(in_file, "AR_VDDA_VS_TRIM"))
        vddd = np.array(lookup(in_file, "AR_VDDD_VS_TRIM"))
        SldoTrimA = int(np.absolute(vdda - 1.2).argmin())
        SldoTrimD = int(np.absolute(vddd - 1.2).argmin())
        self.overwrite(config_file, "SldoTrimA", SldoTrimA)
        self.overwrite(config_file, "SldoTrimD", SldoTrimD)

    def set_VcalPar(self, in_file, config_file):
        # Set the calibrated VCAL parameters from the analysis.
        VCAL_MED_SLOPE = float(lookup(in_file, "VCAL_MED_SLOPE"))
        VCAL_MED_OFFSET = float(lookup(in_file, "VCAL_MED_OFFSET"))
        self.overwrite(config_file, "VcalPar", [VCAL_MED_OFFSET, VCAL_MED_SLOPE])

    def set_InjCap(self, in_file, config_file):
        # Set the Injection Capacitance value from the analysis.
        INJ_CAPACITANC = float(lookup(in_file, "INJ_CAPACITANCE"))
        self.overwrite(config_file, "InjCap", INJ_CAPACITANC)

    def overwrite(self, config_file, search_key, set_value, index=None):
        # search_key is a string which is the name of the parameter that will be overwritten.
        # set_value is the value the parameter that will be overwritten to.
        with config_file.open() as jsonFile:
            config_file_data = json.load(jsonFile)
        self.reset_stack()
        original_search_key = lookup(config_file_data, search_key, self.stack)
        if original_search_key is None:
            msg = f"Parameter not found in config file {config_file}! "
            raise KeyError(msg)
        log.info(
            f"Chip {self.config_chip_name} [{search_key}] change from {original_search_key} to {set_value}."
        )
        if index is None:
            original_search_key = set_value
        else:
            original_search_key[index] = set_value

        self.stack.reverse()

        part_config_file_data = config_file_data
        for k in self.stack:
            part_config_file_data = part_config_file_data[k]
        part_config_file_data[search_key] = original_search_key

        with config_file.open("w") as jsonFile:
            json.dump(config_file_data, jsonFile, indent=4)

    def update_config(self):
        for config_file in self.config_files:
            with config_file.open() as jsonFile:
                config_file_data = json.load(jsonFile)

            out_file = self.in_path.joinpath(f"{config_file.name}.before")
            if out_file.exists():
                log.warning(f"File {out_file} already exists! Skip overwriting!")
            else:
                with out_file.open("w") as fp:
                    json.dump(config_file_data, fp, indent=4)
            self.config_chip_name = lookup(config_file_data, "Name")
            config_chip_serial = convert_name_to_serial(self.config_chip_name)

            # overwrite the parameter
            for in_file in self.in_files:
                found_chip = False
                with in_file.open() as jsonFile:
                    in_file_data = json.load(jsonFile)
                for chip_data in in_file_data:
                    # Check if chip name matched
                    in_chip_serial = lookup(chip_data, "serialNumber")
                    if in_chip_serial is None:
                        log.warning(
                            f"Chip {self.config_chip_name} not found in the input files! Please check the input files."
                        )
                        continue
                    if in_chip_serial != config_chip_serial:
                        log.debug(
                            f"Chip {self.config_chip_name} not found in config. Checking the next chip."
                        )
                    else:
                        found_chip = True
                        in_chip_passqc = lookup(chip_data, "passed")
                        if not in_chip_passqc:
                            log.warning(
                                f"Chip {self.config_chip_name} does not pass QC."
                            )
                            if self.override:
                                log.warning(
                                    "Option --override has been provided; therefore chip configuration will be updated even if the chip failed QC"
                                )
                            else:
                                log.warning(
                                    "Will not update parameters. Re-run with --override if you would like to update the chip configuration even if the chip failed QC"
                                )
                                continue

                        test_type = lookup(chip_data, "testType")
                        if test_type == "ADC_CALIBRATION":
                            self.set_ADCcalPar(chip_data, config_file)
                        elif test_type == "ANALOG_READBACK":
                            self.set_trim(chip_data, config_file)
                        elif test_type == "VCAL_CALIBRATION":
                            self.set_VcalPar(chip_data, config_file)
                        elif test_type == "INJECTION_CAPACITANCE":
                            self.set_InjCap(chip_data, config_file)
                        else:
                            log.warning(
                                f"No test type {test_type} found in the input directory {self.in_path}. Skipping."
                            )
                            continue
                        break
                if found_chip:
                    break
            with config_file.open() as jsonFile:
                config_file_data = json.load(jsonFile)

            out_file = self.in_path.joinpath(f"{config_file.name}.after")
            with out_file.open("w") as fp:
                json.dump(config_file_data, fp, indent=4)
            if not found_chip:
                log.warning(
                    f"Chip {self.config_chip_name} with serial number {config_chip_serial} not found! The corresponding config will not be updated."
                )
                continue


app = typer.Typer(context_settings=CONTEXT_SETTINGS)


@app.command()
def main(
    input_dir: Path = OPTIONS["input_dir"],
    config_dir: Path = OPTIONS["config_dir"],
    config_type: str = OPTIONS["config_type"],
    override: bool = OPTIONS["override"],
):
    log.info(" ==========================================")
    wc = WriteConfig(input_dir, config_dir, config_type, override)
    wc.update_config()


if __name__ == "__main__":
    typer.run(main)
