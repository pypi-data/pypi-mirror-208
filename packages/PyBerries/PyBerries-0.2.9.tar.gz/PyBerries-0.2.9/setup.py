import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyBerries",
    version="0.2.9",
    author="Daniel Thedie",
    author_email="daniel.thedie@ed.ac.uk",
    description="Processing of Bacmman measurement tables",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/MEKlab/pyberries",
    packages=setuptools.find_packages(),
    python_requires='>=3.9',
    install_requires=['numpy>=1.24.3', 'scipy>=1.10', 'pandas>=2.0', 'matplotlib>=3.7', 'tifffile>=2023.4.12', 'h5py>=3.8.0','seaborn>=0.12.2', 'pybacmman>=0.5.1', 'IPython>=8.13.2']
)
