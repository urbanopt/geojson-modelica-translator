within district_single_ghe.Networks;
model UnidirectionalSeries
  "Hydronic network for unidirectional series DHC system"
  extends
    Buildings.Experimental.DHC.Networks.BaseClasses.PartialDistribution1Pipe(
    tau=5*60,
    redeclare district_single_ghe.Networks.ConnectionSeriesAutosize con[nCon](
      each final dp_length_nominal=dp_length_nominal,
      final lDis=lDis,
      final lCon=lCon,
      final dhDis=dhDis,
      final dhCon=dhCon,
      final dIns=dIns,
      final thickness=thickness),
    redeclare model Model_pipDis =
        Buildings.Fluid.FixedResistances.PlugFlowPipe (
      roughness=7e-6,
      fac=1.5,
      final dIns=dIns,
      final thickness=thickness,
      final dh(fixed=true)=dhEnd,
      final length=lEnd));
  parameter Real dp_length_nominal(final unit="Pa/m") = 250
    "Pressure drop per pipe length at nominal flow rate";
  parameter Modelica.Units.SI.Length lDis[nCon]
    "Length of the distribution pipe before each connection";
  parameter Modelica.Units.SI.Length lCon[nCon]
    "Length of each connection pipe (supply only, not counting return line)";
  parameter Modelica.Units.SI.Length lEnd
    "Length of the end of the distribution line (after last connection)";
  parameter Modelica.Units.SI.Length dhDis[nCon](
    each fixed=false,
    each start=0.05,
    each min=0.01)
    "Hydraulic diameter of the distribution pipe before each connection";
  parameter Modelica.Units.SI.Length dhCon[nCon](
    each fixed=false,
    each start=0.05,
    each min=0.01) "Hydraulic diameter of each connection pipe";
  parameter Modelica.Units.SI.Length dhEnd(
    fixed=false,
    start=0.05,
    min=0.01)
    "Hydraulic diameter of of the end of the distribution line (after last connection)";
  parameter Modelica.Units.SI.Length dIns
    "Thickness of pipe insulation, used to compute R";
  parameter Modelica.Units.SI.Length thickness=0.0035 "Pipe wall thickness";
  Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a heatPortRet
    "Heat transfer to or from surroundings (positive if pipe is colder than surrounding)"
    annotation (Placement(transformation(extent={{60,-110},{80,-90}})));
  Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a heatPortSup[nCon]
    "Heat transfer to or from surroundings (positive if pipe is colder than surrounding)"
    annotation (Placement(transformation(extent={{-80,-110},{-60,-90}})));
equation
  connect(pipEnd.heatPort, heatPortRet) annotation (Line(points={{50,10},{50,12},
          {36,12},{36,-86},{70,-86},{70,-100}}, color={191,0,0}));
  connect(con.heatPort, heatPortSup) annotation (Line(points={{-10,0},{-10,-86},
          {-70,-86},{-70,-100}}, color={191,0,0}));
  annotation (Documentation(info="<html>
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
<a href=\"modelica://Buildings.Experimental.DHC.Networks.Combined.BaseClasses.ConnectionSeriesAutosize\">
Buildings.Experimental.DHC.Networks.Combined.BaseClasses.ConnectionSeriesAutosize</a>
which is instantiated for each connection.
So the initialization system of equations would be overdetermined if using
a parameter binding with a scalar variable.
</p>
</html>", revisions="<html>
<ul>
<li>
February 23, 2021, by Antoine Gautier:<br/>
First implementation.
</li>
</ul>
</html>"));
end UnidirectionalSeries;
