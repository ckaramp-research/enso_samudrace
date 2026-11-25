# ENSO Simulation in a Coupled AI Climate Emulator

Notebooks and derived data to reproduce the figures of "ENSO Simulation in a Coupled AI Climate Emulator".

## Data:
The `data/` directory holds the lightweight derived quantities read by the notebooks. The raw data can be obtained from the following sources:
- CMIP6 piControl simulations, including GFDL-CM4: [ESGF](https://esgf-node.llnl.gov/projects/cmip6/)
- ORAS5 ocean reanalysis: [Copernicus Climate Data Store](https://cds.climate.copernicus.eu)
- ERA5 atmospheric reanalysis: [Copernicus Climate Data Store](https://cds.climate.copernicus.eu)
- SamudrACE-CM4-piControl checkpoint: [Hugging Face](https://huggingface.co/allenai/SamudrACE-CM4-piControl). The control simulations can be regenerated from this checkpoint and are not distributed here.
- CPC teleconnection indices: [NOAA CPC](https://www.cpc.ncep.noaa.gov/data/teledoc/telecontents.shtml)

The recharge oscillator fits use the [XRO](https://github.com/senclimate/XRO) package.

## Notebooks:
Run each notebook from inside `notebooks/`.

- `enso_statistics.ipynb` - Figures 2, 3, and 4
- `enso_dynamics.ipynb` - Figures 8, 9, and 10
- `teleconnections.ipynb` - Figure 15

## Requirements:
- numpy (2.0 or later)
- scipy
- xarray
- netCDF4
- matplotlib
- jupyter

## Contact:
For questions or further information, please contact:

Gerardo Rivera Tello - griverat@hawaii.edu

Christina Karamperidou - ckaramp@hawaii.edu
