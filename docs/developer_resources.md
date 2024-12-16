# Developer Resources

## Tests

Tests are run with pytest, e.g.

```bash
    poetry run pytest
```

## Snapshot Testing

Some tests use [syrupy](https://github.com/tophat/syrupy) to compare generated modelica models to saved "snapshots" of the models (saved as .ambr files).

Snapshots should only be updated if we have changed how a model is generated, and we *know* the new version of the model is the correct version. To update all snapshots, you can run the following and commit the new snapshot files.

```bash
    poetry run pytest --snapshot-update
```

## Design Overview

The GMT is designed to create an arbitrary number of user-configured models attached to other user-configured models to represent a district energy system.
GMT has "building blocks" that it uses to define and attach models, which currently include: Energy Transfer Stations (ETSs), Loads, Networks, and Plants.

Each block type is a collection of models, e.g. the Loads includes time series and spawn models. A model in GMT refers to an abstracted Modelica model. It generates Modelica code (the Modelica model) and is used to define attachments to other models.

Each block type can attach to other specific block types. For example, you can attach a load to an ETS, but you cannot attach a load to a network. However, some models (i.e. 5G) have an ETS embedded in them.

Each block type has a corresponding directory inside of `geojson_modelica_translator/model_connectors`, which contains its different model types (e.g. for Loads it contains the Time Series model and others).

Because models are different, even within a block type (e.g., different properties and maybe even ports), the GMT uses the concept of couplings for attaching models. Couplings define how two *specific* models attach in modelica.
For example, a coupling could define how the time series load actually attaches to the heating indirect ETS.

    As an aside, if the GMT reached a point where all models within a block type implemented the same interface then couplings would not be necessary.

## Getting Started as a Developer

There are a few steps that are imperative to complete when starting as a developer of the GMT. First, make sure
to follow the detailed instructions for [Docker Installation](getting_started.md#docker-installation) in the Getting Started guide.

Follow the instructions below in order to configure your local environment:

- Get the Modelica Buildings Library. See the documentation at [MBL Installation](getting_started.md#mbl-installation)

- Clone [the GMT repo](https://github.com/urbanopt/geojson-modelica-translator) into a working directory
  - (optional/as-needed) Add Python 3 to the environment variables
  - As general guidance, we recommend using virtual environments to avoid dependencies colliding between your Python projects. [venv](https://docs.python.org/3/library/venv.html) is the Python native solution that will work everywhere, though other options may be more user-friendly:
    - [pyenv](https://github.com/pyenv/pyenv) and [the virtualenv plugin](https://github.com/pyenv/pyenv-virtualenv) work together nicely for Linux/Mac machines
    - [virtualenv](https://virtualenv.pypa.io/en/latest/)
    - [miniconda](https://docs.conda.io/projects/miniconda/en/latest/)
- For developers, dependency management is through [Poetry](https://python-poetry.org/docs/). Poetry can be acquired by running `pip install poetry`.
  - If you haven't already installed a virtual environment, Poetry will automatically create a simplified environment for your project.
- Move to the GMT root directory and run `poetry install` to install the dependencies.
- Verify that everything is installed correctly by running `poetry run pytest -m 'not compilation and not simulation and not dymola'`. This will run all the unit and integration tests.
- Follow the instructions below to install pre-commit.
- To confirm that models will build and simulate, you can run

```bash
    poetry run pytest -m 'not dymola' --cov-report term-missing --cov .
```

The tests should all pass assuming the libraries, Docker, and all dependencies are installed correctly on your computer. Also, there will be a set
of Modelica models that are created, simulated, and persisted into the `tests/GMT_Lib/output` folder and the
`tests/model_connectors/output` folder.

### Pre-commit

This project uses [pre-commit](https://pre-commit.com/) to ensure code consistency.
To enable pre-commit for your local development process, run the following from the command line from within the git checkout of the
GMT:

```bash
    pre-commit install
```

To run pre-commit against the files without calling git commit, then run the following. This is useful when cleaning up the repo before committing. CI will fail if pre-commit hasn't been run locally.

```bash
    pre-commit run --all-files
```

## Adding New Models

To add a new model you have to do the following:

1. Define the model's python class: First, create a new python file and class under its respective directory in model_connectors. Follow the patterns of existing classes.

2. Create coupling files: For every model that can be linked to, create a <ModelA>_<ModelB> directory in the couplings directory. The two files ComponentDefinitions.mopt and ConnectStatements.mopt must exist in this directory. See more information on the content of the coupling files below in the *Couplings* sections.

3. Create the instance file: In the templates directory, you must define <ModelName>_Instance.mopt which is the template that instantiates the system in the district model.

See the notes below for more information.

### Couplings

A coupling defines the Modelica code necessary for interfacing two specific models, e.g. a time series load and heating indirect ETS.
Each coupling is unique in its requirements:

- What additional components are necessary, for example there might be some sensor between system A and B, or maybe B requires a pump when A is a specific model type
- What ports are connected, for example connecting ports of model A and model B

Thus each coupling must define two template files, ComponentDefinitions.mopt and ConnectStatements.mopt, respectively. These files must be placed in the directory `couplings/templates/<model A>_<model B>/`.
In general, the **order of the names** should **follow the order of system types** if you laid out the district system starting with loads on the far left and plants on the far right (e.g. load before ETS, ETS before network, network before plant).

### District system

A district system is the model which incorporates all of the models and their couplings.

### Templating Flow

When rendering the district system model file, it must:

1. call to_modelica() for each model to generate its Modelica code
2. render the coupling partial templates (ie the Modelica code required for couplings)
3. render the model instance definition (ie the Modelica code which instantiates the model)
4. insert the coupling partials and model instance definitions into the district Modelica file

Refer to [the district template](https://github.com/urbanopt/geojson-modelica-translator/blob/develop/geojson_modelica_translator/model_connectors/districts/templates/DistrictEnergySystem.mot) and [the district code](https://github.com/urbanopt/geojson-modelica-translator/blob/develop/geojson_modelica_translator/model_connectors/districts/district.py) for reference.

Each templating step has access to a particular set of variables, which is defined below.

## Summary of Templating Contexts

### Model Definition

Each model generates one or more Modelica files to define its model. The templating context is implementation dependent, so refer to its `to_modelica()` method.

### Coupling Component Definitions

This is the template which defines new components/variables necessary for a coupling. More specifically, these are the partial template files at model_connectors/couplings/templates/<coupling name>/ComponentDefinitions.mopt. These templates have access to:

- `globals`: global variables (those defined in the district.py, such as medium_w = MediumW)
- `coupling`: contains the coupling id, as well as references to the coupled models under their respective types (e.g. coupling.load.id or coupling.network.id). You should append `coupling.id` to any variable identifiers to prevent name collisions. For example, instead of just writing `parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal` you should do `parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_{{ coupling.id }}` as well as any place where you would reference that variable.
- `graph`: an instance of the CouplingGraph class, where all couplings are located. It can provide useful methods for accessing couplings throughout the entire system. Refer to the python class to see what it can do.
- `sys_params`: an object containing data from the system parameters file
  - `district_system`: contains the data from the district_system portion of the system parameters file
  - `building`: if the coupling includes a load, this object will be included as well -- if there's no as part of the coupling this object will NOT be present. It contains the building-specific system parameters pulled from the system parameters JSON file.

### Coupling Connect Statements

This is the template which defines connect statements to be inserted into the equation section. More specifically, these are the partial template files at model_connectors/couplings/templates/<coupling name>/ConnectStatements.mopt. These templates have access to:

- `globals`: same as Coupling Component Definitions context
- `coupling`: same as Coupling Component Definitions context. Just like with the component definitions template, you should use the coupling.id to avoid variable name collisions.
- `graph`: same as Coupling Component Definitions context
- `sys_params`: same as Coupling Component Definitions context

### Model Instance

This template is used to declare a model instance.

- `globals`
- `graph`
- `couplings`: contains each coupling the model is associated with. For example, if our ETS was coupled to a load and network, couplings would look like `{ load_couplings: [<load coupling>], network_couplings: [<network coupling>] }`. This can be used to access coupling and model ids.
- `model`: contains info about the model instance, including `modelica_type` and `id`. These should be used to define the model, for example `{{ model.modelica_type }} {{ model.id }}(...)`
- `sys_params`: same as Coupling Component Definitions context

## Simulation Mapper Class / Translator

The Simulation Mapper Class can operate at multiple levels:

1. The GeoJSON level -- input: geojson, output: geojson+
2. The Load Model Attachment -- input: geojson+, output: multiple files related to building load models (spawn, rom, csv)
3. The Translation to Modelica -- input: custom format, output: .mo (example inputs: geojson+, system design parameters). The translators are implicit to the load model connectors as each load model requires different paramters to calculate the loads.

In some cases, the Level 3 case (translation to Modelica) is a blackbox method (e.g. TEASER) which prevents a
simulation mapper class from existing at that level.

## Running Simulations

The GeoJSON to Modelica Translator contains a `ModelicaRunner.run_in_docker(...)` method. The test suite uses this to run most of our models with OpenModelica.

## Release Instructions

1. Create a branch named `Release 0.x.`
1. Update version in pyproject.toml
2. Update CHANGELOG using GitHub's "Autogenerate Change Log" feature, using `develop` as the target
3. After tests pass, merge branch into develop
4. From local command line, merge develop into main with: `git checkout main; git pull; git merge --ff-only origin develop; git push`
5. In GitHub, tag the release against main. Copy and paste the changelog entry into the notes. Verify the release is posted to PyPI.

### Build and release the documentation

During development we can [serve docs locally](https://squidfunk.github.io/mkdocs-material/creating-your-site/#previewing-as-you-write) and view updates as they are made.

   1. Start a documentation update branch: `git switch -c <branch_name>`
   1. `poetry run mkdocs serve`
   1. Point browser to [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

- To deploy, push a commit in the `docs` folder to the `main` branch
- Wait a few minutes, then verify the new documentation on the [docs website](https://nrel.github.io/geojson-modelica-translator/)
