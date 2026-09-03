import subprocess
import tempfile
from pathlib import Path
from typing import Literal

import matplotlib.pyplot as plt
from diffpy.pdfgetx import plotdata
from pydantic import BaseModel, computed_field, model_validator

from pdfcurl.logger import logger
from pdfcurl.templates import formatted_config_template

OUTPUT_TYPES = Literal["iq", "sq", "fq", "gr"]


class PDFGetConfig(BaseModel):
    dataformat: Literal["QA", "Qnm", "twotheta"] = "twotheta"
    backgroundfile: str | Path | None
    outputtypes: OUTPUT_TYPES | list[OUTPUT_TYPES] = "gr"
    wavelength: float | None = None
    composition: str
    qmaxinst: float
    qmin: float = 0.0
    qmax: float = 50.0
    rmin: float = 0.0
    rmax: float = 20.0
    rstep: float = 0.01

    @model_validator(mode="after")
    def check_two_wavelength(self):
        if self.dataformat == "twotheta" and self.wavelength is None:
            raise KeyError("If dataformat = twotheta then wavelength must not be None")
        return self

    @model_validator(mode="after")
    def set_rmin(self):
        if self.rmin == 0:
            self.rmin = self.rstep
        return self

    @computed_field
    def outputs(self) -> str:
        if isinstance(self.outputtypes, list):
            return ", ".join(self.outputtypes)
        else:
            return self.outputtypes


def run_pdfgetx3_config(
    formatted_config: str,
    input_file: str | Path,
    output_file: str | Path | None = None,
    force: bool = False,
):
    """
    Convert a measured 1D diffraction pattern into a pair distribution
    function using PDFgetX3.

    Parameters
    ----------
    input_file : str
        Path to a two-column diffraction file.

        Either:
            Q(Å⁻¹) intensity

        or:
            2theta(deg) intensity

    output_dir : str or None
        Output folder.

    Returns
    -------
    r : ndarray
    g : ndarray
    pdf_file : str
    """

    input_file = Path(input_file)

    if output_file is None:
        output_dir = input_file.parent
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"{input_file.stem}.gr"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".cfg", delete=False) as f:
        f.write(formatted_config)
        cfg_file = f.name

    cmd = ["pdfgetx3", "--config", cfg_file, str(input_file), "--output", output_file]

    if force:
        cmd.append("--force=yes")

    with subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    ) as proc:
        if proc is not None:
            for line in proc.stdout:  # type: ignore
                logger.info(line.strip())

    return str(output_file)


def diffraction_to_pdf_from_config(
    input_file: str | Path,
    config: PDFGetConfig,
    output_file: str | Path | None = None,
    force: bool = False,
    plot: bool = False,
):

    config_kwargs = config.model_dump()
    formatted_config = formatted_config_template.format(**config_kwargs)

    print(formatted_config)

    if config.backgroundfile is None:
        formatted_config = formatted_config.replace(
            "backgroundfile = None", "# backgroundfile = None"
        )

    output_file = run_pdfgetx3_config(
        input_file=input_file,
        output_file=output_file,
        formatted_config=formatted_config,
        force=force,
    )

    if plot:
        plt.xlabel(f"{config.outputtypes}")
        plt.ylabel("Intensity")
        plotdata.plotdata(output_file)
        plt.show()


if __name__ == "__main__":
    # diffraction_to_pdf()

    input_path = "workspaces/pdfcurl/examples/Si_pe2_i15_1.xy"
    output_path = "workspaces/pdfcurl/examples/Si_pe2_i15_1_pdf.xy"

    DEFAULT_CONFIG = PDFGetConfig(
        dataformat="twotheta",
        wavelength=0.16,
        backgroundfile=None,
        composition="Si",
        qmaxinst=20,
        outputtypes=["gr", "sq"],
    )

    diffraction_to_pdf_from_config(
        config=DEFAULT_CONFIG,
        input_file=input_path,
        output_file=None,
        force=True,
        plot=True,
    )
