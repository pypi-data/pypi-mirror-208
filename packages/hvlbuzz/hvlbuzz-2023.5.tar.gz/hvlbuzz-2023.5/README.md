[![python version](https://img.shields.io/pypi/pyversions/hvlbuzz.svg?logo=python&logoColor=white)](https://pypi.org/project/hvlbuzz)
[![latest version](https://img.shields.io/pypi/v/hvlbuzz.svg)](https://pypi.org/project/hvlbuzz)
[![pipeline status](https://gitlab.com/ethz_hvl/hvlbuzz/badges/main/pipeline.svg)](https://gitlab.com/ethz_hvl/hvlbuzz/-/commits/main)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Checked with pylint](https://img.shields.io/badge/pylint-checked-blue)](https://github.com/PyCQA/pylint)

# HVLBuzz

Actual docs 📖 can be found [here](https://ethz_hvl.gitlab.io/hvlbuzz/).

HVLBuzz is a simulation tool to calculate the surface gradient of overhead power lines and predict the audible noise and electromagnetic field at ground. It was designed as a Student Thesis of Aldo Tobler, supervised by Soren Hedtke and Christian Franck from the High Voltage Lab (HVL), D-ITET, ETH.

This tool is completely free to use as is and only requires freely available [Python](https://www.python.org/) libraries to run. The GUI is based on the [Kivy](https://kivy.org/#home) framework, while the mathematical computations and plot generation rely the widely used [NumPy](https://numpy.org/) and [Matplotlib](https://matplotlib.org/).

## Installation

It is recommended that you use a Python virtual envioronement to run HVLBuzz. Run the following command to create folder called `kivy_venv` inside which your environement will live. **The latest version of Python this code has been tested with was 3.11**

```bash
python -m virtualenv kivy_venv
```

Activate your virtual environement by running

```bash
kivy_venv\Scripts\activate.bat # 🪟
. kivy_venv/bin/activate # 🐧 / 🍏
```

Then install hvlbuzz into your environement as follows

```bash
pip install .
```

This will also install an executable python script in your environments `bin` folder.

## Usage

To run the binary obtained in the install part, run

```sh
hvlbuzz
```

Alternatively, the module is can also be started from python:

```sh
python -m hvlbuzz
```
or

```sh
python hvlbuzz
```

## Packaged version

The current version (for 64-bit Windows) can be found [here](https://gitlab.com/ethz_hvl/hvlbuzz/-/releases).

In order to run properly, the `buzz.exe` executalbe needs to be able to have recursive read and write access to the folder it finds itself in; in particualr to the file `buzz.ini` as well as for the subfolder called `temp` in which temporary files are created when the Export PDF function of the application is used.

## Compiling your own packaged version

The source code can also be compiled by yourself using [PyInstaller](https://www.pyinstaller.org/) using the provided [hvlbuzz/buzz.spec](hvlbuzz/buzz.spec) file.

```bash
pyinstaller hvlbuzz/buzz.spec
```

A `buzz.exe` binary will be available in a (newly created if non-existing) `dist\buzz` folder.
