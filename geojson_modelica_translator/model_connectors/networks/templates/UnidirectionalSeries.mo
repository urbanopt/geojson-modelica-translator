within geojson_modelica_translator.model_connectors.templates;
model UnidirectionalSeries
  "Hydronic network for unidirectional series DHC system"
  extends Buildings.DHC.Networks.BaseClasses.PartialDistribution1Pipe(
    tau=5*60,
    redeclare Networks.ConnectionSeriesAutosize con[nCon](
      final lDis=lDis,
      final lCon=lCon,
      final dhDis=dhDis,
      final dhCon=dhCon,
      each final dp_length_nominal=dp_length_nominal,
      each final dIns=dIns,
      each final kIns=kIns,
      each final thickness=thickness,
      each final roughness=roughness,
      each final cPip=cPip,
      each final rhoPip=rhoPip),
    redeclare model Model_pipDis=Buildings.Fluid.FixedResistances.PlugFlowPipe(
      fac=1.5,
      final dIns=dIns,
      final kIns=kIns,
      final thickness=thickness,
      final roughness=roughness,
      final cPip=cPip,
      final rhoPip=rhoPip,
      final dh(
        fixed=true)=dhEnd,
      final length=lEnd));
  parameter Real dp_length_nominal(
    unit="Pa/m")=250
    "Pressure drop per pipe length at nominal flow rate";
  parameter Modelica.Units.SI.Length lDis[nCon]
    "Length of the distribution pipe before each connection";
  parameter Modelica.Units.SI.Length lCon[nCon]
    "Length of each connection pipe (supply only, not counting return line)";
  parameter Modelica.Units.SI.Length lEnd
    "Length of the end of the distribution line (after last connection)";
  parameter Modelica.Units.SI.Length dhDis[nCon]
    "Hydraulic diameter of the distribution pipe before each connection";
  parameter Modelica.Units.SI.Length dhCon[nCon](
    each fixed=false,
    each min=0.01,
    each start=0.05)
    "Hydraulic diameter of each connection pipe";
  parameter Modelica.Units.SI.Length dhEnd
    "Hydraulic diameter of of the end of the distribution line (after last connection)";
  parameter Modelica.Units.SI.Length dIns
    "Thickness of pipe insulation, used to compute R"
    annotation (Dialog(group="Pipe material"));
  parameter Modelica.Units.SI.ThermalConductivity kIns
    "Heat conductivity of pipe insulation, used to compute R"
    annotation (Dialog(group="Pipe material"));
  parameter Modelica.Units.SI.Length thickness=0.0035
    "Pipe wall thickness"
    annotation (Dialog(group="Pipe material"));
  parameter Modelica.Units.SI.Height roughness=2.5e-5
    "Average height of surface asperities (default: smooth steel pipe)"
    annotation (Dialog(group="Pipe material"));
  parameter Modelica.Units.SI.SpecificHeatCapacity cPip=2300
    "Specific heat of pipe wall material. 2300 for PE, 500 for steel"
    annotation (Dialog(group="Pipe material"));
  parameter Modelica.Units.SI.Density rhoPip(
    displayUnit="kg/m3")=930
    "Density of pipe wall material. 930 for PE, 8000 for steel"
    annotation (Dialog(group="Pipe material"));
  Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a heatPortGro[nCon+1]
    "Heat transfer to or from surroundings (positive if pipe is colder than surrounding)"
    annotation (Placement(transformation(extent={{-10,-110},{10,-90}})));
equation
  connect(con.heatPort,heatPortGro[1:nCon])
    annotation (Line(points={{-10,0},{-20,0},{-20,-86},{0,-86},{0,-100}},color={191,0,0}));
  connect(pipEnd.heatPort,heatPortGro[nCon+1])
    annotation (Line(points={{50,10},{32,10},{32,-86},{0,-86},{0,-100}},color={191,0,0}));
  annotation (
    Documentation(
      info="<html>
<p>
This model represents a one-pipe distribution network with built-in computation
of the pipe diameter based on the pressure drop per pipe length
at nominal flow rate.
</p>
<h4>Modeling considerations</h4>
<p>
Note that <code>dhDis</code> needs to be vectorized, even if the same value
is computed for each array element in case of a one-pipe network.
This is because the pipe diameter is computed at initialization by the model
<a href=\"modelica://Buildings.DHC.Networks.Combined.BaseClasses.ConnectionSeriesAutosize\">
Buildings.DHC.Networks.Combined.BaseClasses.ConnectionSeriesAutosize</a>
which is instantiated for each connection.
So the initialization system of equations would be overdetermined if using
a parameter binding with a scalar variable.
</p>
</html>",
      revisions="<html>
<ul>
<li>
February 23, 2021, by Antoine Gautier:<br/>
First implementation.
</li>
</ul>
</html>"));
end UnidirectionalSeries;