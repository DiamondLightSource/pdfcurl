_config_template = """
## pdfgetx3 searches for default configurations in ~/.pdfgetx3.cfg,
## .pdfgetx3.cfg, pdfgetx3.cfg and then loads a custom configuration
## if specified via the "-c" option. You can run
##
##     pdfgetx3 --verbose=info
##
## to verify how and from what file are the parameters set.
##
## Use "pdfgetx3 --createconfig=FILE" to write a new configuration
## file with a description of all supported options.

[DEFAULT]

## Format of input files.  Available formats are: "twotheta", "QA", "Qnm"
## corresponding to a 2-column text data where the first column is either
## twotheta in degrees, Q in inverse Angstroms or Q in inverse nanometers.
dataformat = twotheta

## Optional background intensities from container and air scattering
backgroundfile = kapton_bgrd_300k_nor_2-3.chi

## Types of output files to be saved.  Possible values are
## "iq", "sq", "fq", "gr", also used as filename extensions.
## No files are saved when empty, "none" or "NONE".
outputtype = gr

## X-ray wavelength in Angstroms.  Required for the "twotheta" dataformat.
wavelength = 0.142773

## Chemical composition of the measured sample.  Supported formats are
## "PbTi0.5Zr0.5O3", "Pb (TiZr)0.5 O3" or "Pb 1 (Ti Zr) 1/2 O 3".
## Space characters are ignored, unit counts can be omitted, but it is
## important to use a proper upper and lower case in atom symbols.
## Elements can appear several times in the formula, e.g., "CH3 CH3",
## and the formula may contain parentheses or fractional counts.

# molar composition corresponding to weight ratio Si 90% Ni 10%.
composition = Si 0.95 Ni 0.05

## The Q cutoff for the meaningful input intensities in inverse Angstroms.
## This is the upper boundary for the qmax parameter.  It is also used as
## the upper boundary for the polynomial fits in S(Q) corrections.
qmaxinst = 27

## Lower Q cutoff for Fourier transformation in inverse Angstroms.
## Use 0.0 when not specified.
#qmin = 0.0

## Upper Q cutoff for Fourier transformation in inverse Angstroms.
## Use maximum Q in the data when not specified.
qmax = 26.0

## Limits and spacing for the calculated PDF r-grid.
## All values in Angstroms.
rmin = 0.0
rmax = 30.0
rstep = 0.01
"""

formatted_config_template = """
## pdfgetx3 searches for default configurations in ~/.pdfgetx3.cfg,
## .pdfgetx3.cfg, pdfgetx3.cfg and then loads a custom configuration
## if specified via the "-c" option. You can run
##
##     pdfgetx3 --verbose=info
##
## to verify how and from what file are the parameters set.
##
## Use "pdfgetx3 --createconfig=FILE" to write a new configuration
## file with a description of all supported options.

[DEFAULT]

## Format of input files.  Available formats are: "twotheta", "QA", "Qnm"
## corresponding to a 2-column text data where the first column is either
## twotheta in degrees, Q in inverse Angstroms or Q in inverse nanometers.
dataformat = {dataformat}

## Optional background intensities from container and air scattering
backgroundfile = {backgroundfile}

## Types of output files to be saved.  Possible values are
## "iq", "sq", "fq", "gr", also used as filename extensions.
## No files are saved when empty, "none" or "NONE".
outputtype = {outputs}

## X-ray wavelength in Angstroms.  Required for the "twotheta" dataformat.
wavelength = {wavelength}

## Chemical composition of the measured sample.  Supported formats are
## "PbTi0.5Zr0.5O3", "Pb (TiZr)0.5 O3" or "Pb 1 (Ti Zr) 1/2 O 3".
## Space characters are ignored, unit counts can be omitted, but it is
## important to use a proper upper and lower case in atom symbols.
## Elements can appear several times in the formula, e.g., "CH3 CH3",
## and the formula may contain parentheses or fractional counts.

# molar composition corresponding to weight ratio Si 90% Ni 10%.
composition = {composition}

## The Q cutoff for the meaningful input intensities in inverse Angstroms.
## This is the upper boundary for the qmax parameter.  It is also used as
## the upper boundary for the polynomial fits in S(Q) corrections.
qmaxinst = {qmaxinst}

## Lower Q cutoff for Fourier transformation in inverse Angstroms.
## Use 0.0 when not specified.
qmin = {qmin}

## Upper Q cutoff for Fourier transformation in inverse Angstroms.
## Use maximum Q in the data when not specified.
qmax = {qmax}

## Limits and spacing for the calculated PDF r-grid.
## All values in Angstroms.
rmin = {rmin}
rmax = {rmax}
rstep = {rstep}
"""
