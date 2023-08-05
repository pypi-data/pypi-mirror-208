This is a module to wrap some functions of XMM SAS into python.

It is meant to extract spectra and light curves from a single point source in the field of view from the MOS cameras. No support for RGS is present.

It works for PN in maging mode and MOS in both imaging (small and full window) and timing mode.

Esamples are wrapped into jupyter notebooks and will be made available.

It contains also many functions to perform spectral fits through xspec using the pyxspec and bxa interfaces.

To perform actual SAS extraction on a local computer, it assumes sas is in
/opt/sas
and CCF is in
/opt/CalDB/ccf/

It assumes that you work in a location into which the ODF files are in a subfolder called 'odf'.
A docker container is under development to run the S/W.

The adaptive rebinning is not currently distributed.

This module has been used for the paper:
Ferrigno, Bozzo et al. (2020)

To install it:
pip install pyxmmsas (preferred)
or
python setup.py install (for development)
