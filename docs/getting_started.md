# Getting Started

There are three major steps to running the GeoJSON to Modelica Translator (GMT):

1. Generating the GeoJSON and System Parameter JSON files,
1. Creating of the Modelica package containing the district system, and
1. Running the Modelica package.

Depending on the use case, the need to run all the steps above may not be needed. For example:
it may be desirable to only generate the Modelica package and then open and run the model
in a Modelica user interface such as [Dymola](https://www.3ds.com/products/catia/dymola). Or, there may be a case to simply generate the
System Parameter file from results of an [URBANopt SDK](https://docs.urbanopt.net/) simulation. These files can then be
customized by hand to build a district system to meet your needs.

Therefore, this Getting Started guide is broken up into three major setup steps. Each one requires all previous steps to be completed first.

1. Installing the [GMT from PyPI](https://pypi.org/project/geojson-modelica-translator/)
1. Installing and configuring the [Modelica Buildings Library](https://simulationresearch.lbl.gov/modelica/index.html) (MBL)
1. Installing and configuring [Docker](https://docs.docker.com/get-docker/) in order to run simulations using [OpenModelica](https://openmodelica.org/).

## GMT Installation

You must have PIP and Python 3.10 or later installed (run `python --version` to see what version you're using). After installing Python and PIP run the following in a terminal:

```bash
pip install geojson-modelica-translator
```

After installation of the GMT, a new command line interface (called the URBANopt District Energy Systems [UO DES] CLI) can be used to run various commands. Without needing to install the [MBL](https://simulationresearch.lbl.gov/modelica/index.html) the user can use the CLI to build the system parameters file from the results of the URBANopt SDK. For more information run the following:

```bash
uo_des -h
uo_des build-sys-param -h
```

The command below is only an example; however, it will run if the repository is checked out and run in the following path: `./tests/management/data/sdk_project_scraps`

```bash
uo_des build-sys-param sys_param.json baseline_scenario.csv example_project.json
```

## MBL Installation

The Modelica Buildings Library contains many models that are needed to assemble the district systems. Follow the instructions below to install the MBL needed for the GMT:

* Download and extract the appropriate version of the MBL from [https://simulationresearch.lbl.gov/modelica/downloads/archive/modelica-buildings.html](https://simulationresearch.lbl.gov/modelica/downloads/archive/modelica-buildings.html)
  * The appropriate version can be found in the right-hand column of the [installer matrix](https://docs.urbanopt.net/developer_resources/compatibility_matrix.html#urbanopt-installer-matrix) (may need to scroll to show that column).
* Add the Modelica Buildings Library path to your MODELICAPATH environment variable (e.g., `export MODELICAPATH=${MODELICAPATH}:$HOME/path/to/modelica-buildings`).
  * For help setting env vars on Windows, this documentation may help: [https://www.howtogeek.com/787217/how-to-edit-environment-variables-on-windows-10-or-11/](https://www.howtogeek.com/787217/how-to-edit-environment-variables-on-windows-10-or-11/)
* Restart your terminal to ensure that the environment variable for the MBL library is exported correctly.

Once the MBL is installed, then the CLI can be used to create the model with the following command:

```bash
uo_des create-model -h
```

The command below is only an example; however, it will run if the repository is checked out and run in the following path: `./tests/management/data/sdk_project_scraps`

```bash
uo_des create-model sys_param.json example_project.json model_from_sdk
```

The resulting Modelica package will be created and can be opened in a Modelica editor. Open the `package.mo` file in the root directory of the generated package. You will also need to
load the MBL into your Modelica editor.

Most models can be simulated for free using [OpenModelica](https://openmodelica.org/), which is included via Docker.

[Dymola](https://www.3ds.com/products/catia/dymola) is a commercial alternative to OpenModelica. Licenses for use can be purchased from them.

## Docker Installation

Version 0.5.0+ of the GMT enables running the models using OpenModelica which requires the installation of [Docker](https://docs.docker.com/get-docker/).
To configure Docker, do the following:

* Install [Docker](https://docs.docker.com/get-docker/) for your system.
* Configure Docker Desktop to have at least 4 GB Ram and 2 cores. This is configured under the Docker Preferences.
  * Windows users can refer to [these instructions](https://docs.docker.com/desktop/settings/windows/) for more detail on adjusting Docker resources and may also be helped by [this page](https://learn.microsoft.com/en-us/windows/wsl/wsl-config#wslconfig), which documents how to change resources in WSL.
  * Larger models (more buildings) may require more resources in Docker.
* We recommend testing the Docker installation by simply running `docker run hello-world` in a terminal to confirm it is working as intended.

After Docker is installed and configured, you can use the CLI to run the model using the following
command:

```bash
uo_des run-model -h
```

The command below is only an example; however, it will run if the repository is checked out and run in the following path: `./tests/management/data/sdk_project_scraps`

```bash
uo_des run-model model_from_sdk
```
