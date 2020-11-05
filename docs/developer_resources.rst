
Adding New Models
=================

If adding a new model, there are a few things that must be done for it to be usable by GMT.

1. Define the model's python class: First, create a new python file and class under its respective directory in model_connectors. Follow the patterns of existing classes.

2. Create coupling files: For every system that it should be able to be linked to, create a <ModelA>_<ModelB> directory in the couplings directory. The two files ComponentDefinitions.mopt and ConnectStatements.mopt must exist in this directory.

3. Create the instance file: In the templates directory, you must define <ModelName>_Instance.mopt which is the template that instantiates the system in the district model.

See the notes below for more information.

Couplings
=========

A coupling is a pair of two connected systems, e.g. a load and ets.
Each coupling is unique in its requrements:

- what additional components are necessary, for example system B might require using system A.foo
- what things are connected, for example connecting two ports of A and B

Thus each valid coupling must define two template files, ComponentDefinitions.mopt and ConnectStatements.mopt, respectively.

District system
===============

A district system is the model which incorporates all of the models and their couplings.

Templating Flow
---------------

When rendering the district system model file, it must:

1. call to_modelica() for each model
2. render the coupling partial templates
3. render the model instance definition
4. insert the coupling partials and model instance definitions into the district modelica file

Refer to DistrictEnergySystem.mot and district.py for reference.

Each templating step has access to a particular set of variables, which is defined below.
To avoid collisions of modelica variable identifiers (ie variable names), the templating flow allows you to include jinja variables which wouldn't be provided in the templating context.
As a note, name collisions could occur if you had two couplings linking the same system types.
If they both declare a component with the name "foo" in the modelica file, the model will be invalid.

For a jinja variable to be generated, it must meet these requirements:

1. It must be included in the ComponentDefinitions template.
2. The jinja variable name must end with _id. For example, "my_variable" would not be generated, but "my_variable_id" would.

The generated variable names are then accessible in the other templating steps as well.

Summary of Templating Contexts
++++++++++++++++++++++++++++++

Base model
**********

This is the model that might use templates in to_modelica(), and the context is implementation depenedent.

Component Definitions
*********************

This is the template which defines new components/variables necessary for a coupling. It has access to:

- global variables (those defined in the district.py, such as medium_w = MediumW)
- generated variable identifiers
- load_id, ets_id, and/or network_id, which contains the identifier of the model instances being coupled. For example, if we were coupling TimeSeries load and CoolingIndirect ets, the template would have access to load_id and ets_id.

Connect Statements
******************

This is the template which defines connect statements to be inserted into the equation section.

- global variables
- generated variable ids
- load_id, ets_id, and/or network_id

Model Instance
**************

This template is used to declare a model instance.

- global vars defined in district.py
- generated variable ids
- type_path, which contains a path to the base model file (should be used for defining the instance type). This is derived from the python class's get_modelica_type() method
- unique_id, which contains a unique ID for the model (should be used in place of a variable name for the component). This is derived from the python class's identifier attribute
