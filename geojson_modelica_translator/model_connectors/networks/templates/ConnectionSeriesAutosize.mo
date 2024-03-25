within district_single_ghe.Networks;
model ConnectionSeriesAutosize
  "Model for connecting an agent to the DHC system"
  extends
    Buildings.Experimental.DHC.Networks.Combined.BaseClasses.ConnectionSeriesStandard(
    tau=5*60,
    redeclare replaceable model Model_pipDis =
        Buildings.Fluid.FixedResistances.PlugFlowPipe (
        roughness=7e-6,
        fac=1.5,
        final dIns=dIns,
        final kIns=kIns,
        final thickness=thickness,
        final length=lDis,
        final dh(fixed=true) = dhDis),
    redeclare replaceable model Model_pipCon =
        Buildings.Experimental.DHC.Networks.Combined.BaseClasses.PipeAutosize (
        roughness=2.5e-5,
        fac=2,
        final length=2*lCon,
        final dh(fixed=true) = dhCon,
        final dp_length_nominal=dp_length_nominal));
  parameter Real dp_length_nominal(unit="Pa/m")=250
    "Pressure drop per pipe length at nominal flow rate";
  parameter Modelica.Units.SI.Length dIns
    "Thickness of pipe insulation, used to compute R";
  parameter Modelica.Units.SI.ThermalConductivity kIns
    "Heat conductivity of pipe insulation, used to compute R";
  parameter Modelica.Units.SI.Length thickness=0.0035 "Pipe wall thickness";
  Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a heatPort
    "Heat transfer to or from surroundings (positive if pipe is colder than surrounding)"
    annotation (Placement(transformation(extent={{-110,-10},{-90,10}})));
equation
  connect(heatPort, pipDis.heatPort)
    annotation (Line(points={{-100,0},{-70,0},{-70,-30}}, color={191,0,0}));
  annotation (Documentation(revisions="<html>
<ul>
<li>
February 23, 2021, by Antoine Gautier:<br/>
First implementation.
</li>
</ul>
</html>", info="<html>
<p>
This model represents the supply and return lines to connect an
agent (e.g., an energy transfer station) to a one-pipe main distribution
system.
The instances of the pipe model are autosized based on the pressure drop per pipe length 
at nominal flow rate.
</p>
</html>"));
end ConnectionSeriesAutosize;
