
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

Summary of Templating Contexts
++++++++++++++++++++++++++++++

Base model
**********

This is the model that might use templates in to_modelica(), and the context is implementation depenedent.

Component Definitions
*********************

This is the template which defines new components/variables necessary for a coupling. It has access to:

- :code:`globals`: global variables (those defined in the district.py, such as medium_w = MediumW)
- :code:`coupling`: contains the couling id, as well as references to the coupled models under their respective types (e.g. coupling.load.id or coupling.network.id). You should append :code:`coupling.id` to any variable identifiers to prevent name collisions. For example, instead of just writing :code:`parameter Modelica.SIunits.MassFlowRate mDis_flow_nominal` you should do :code:`parameter Modelica.SIunits.MassFlowRate mDis_flow_nominal_{{ coupling.id }}` as well as any place where you would reference that variable.
- :code:`graph`: an instance of the CouplingGraph class, where all couplings are located. It can provide useful methods for accessing couplings throughout the entire system. Refer to the python class to see what it can do.

Connect Statements
******************

This is the template which defines connect statements to be inserted into the equation section.

- :code:`globals`
- :code:`coupling`: just like with the component definitions template, you should use the coupling.id to avoid variable name collisions.
- :code:`graph`

Model Instance
**************

This template is used to declare a model instance.

- :code:`globals`
- :code:`graph`
- :code:`couplings`: contains each coupling the model is associated with. For example, if our ETS was coupled to a load and network, couplings would look like :code:`{ load_couplings: [<load coupling>], network_couplings: [<network coupling>] }`. This can be used to access coupling and model ids.
- :code:`model`: contains info about the model instance, including :code:`modelica_type` and :code:`id`. These should be used to define the model, for example :code:`{{ model.modelica_type }} {{ model.id }}(...)`
