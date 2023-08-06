# PyBerries

PyBerries is a Python package that can be used to import, manipulate and plot data from Bacmman measurement tables.

It relies mainly on Pandas for data handling and Seaborn/Matplotlib for plotting.


## Installation

### Optional: install Jupyter-lab (to run Jupyter Notebooks)

#### Anaconda (recommended)

  Anaconda will install both Python and Jupyter-lab (used to run Python notebooks) easily. Note however that it requires ~5 Gb free disk space.
  For a lighter installation procedure, see the next section "Command line install".

  - Download Anaconda from the [official website](https://www.anaconda.com/)
  - Run the installer (leave all options as default)
  - Start "Anaconda Navigator"
  - In Anaconda, launch the "Jupyter Lab" module (you might need to click on "Install" first)

#### Command line install

  - Open a terminal (macOS/Linux) or Powershell (Windows)
  - Install Python
      - Enter the command `python --version`
      - If an error or a version < 3.9 is shown, download and install Python from the [official website](https://www.python.org/downloads/)
  - After installing, restart your terminal/powershell; the `python --version` command should display a version number > 3.9
  - Install Jupyter Lab
      - In a terminal/powershell, run the command `python -m pip install jupyterlab`
      - After the installation completes, Jupyter Lab can be started using the command `jupyter-lab`

### Installing the package

To install the package, use the following command in a terminal:

`python -m pip install PyBerries`

You can also install a specific version number (useful e.g. to make sure you code won't be broken by a future update):

`python -m pip install PyBerries==0.2.8`

In a jupyter notebook, use the command:

`%pip install PyBerries`, or `%pip install PyBerries==0.2.8` for a specific version.


## Getting started

Try downloading and running the [tutorial notebook](https://gitlab.com/MEKlab/pyberries/-/raw/main/Tutorial/Tutorial.ipynb?inline=false) to get acquainted with data import and plotting in PyBerries.

For further details, see the [main functionalities](https://gitlab.com/MEKlab/pyberries/-/blob/main/doc/PyBerries_main_functionalities.md) documentation, as well as the [DatasetPool](https://gitlab.com/MEKlab/pyberries/-/blob/main/doc/DatasetPool.md) documentation.

For info and examples on plots, see the [preset plots gallery](https://gitlab.com/MEKlab/pyberries/-/blob/main/doc/Plot_preset_gallery.md) and the [Seaborn documentation](https://seaborn.pydata.org/index.html)
