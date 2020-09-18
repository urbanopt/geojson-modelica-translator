within geojson_modelica_translator.model_connectors.templates;
model Boiler_TParallel
  "Multiple identical boiler"
  extends PartialPlantParallel(
    redeclare Heater_T boi(
      each energyDynamics=Modelica.Fluid.Types.Dynamics.FixedInitial,
      each QMax_flow=QMax_flow,
      each m_flow_nominal=m_flow_nominal,
      each dp_nominal=dp_nominal));
  parameter Modelica.SIunits.MassFlowRate m_flow_nominal;
  parameter Modelica.SIunits.PressureDifference dp_nominal;
  parameter Modelica.SIunits.HeatFlowRate QMax_flow;
  parameter Integer numBoi=2;
  Modelica.Blocks.Math.BooleanToReal booToRea[numBoi](
    each final realTrue=1,
    each final realFalse=0)
    "Boolean to real (if true then 1 else 0)"
    annotation (Placement(transformation(extent={{-80,40},{-60,60}})));
  Modelica.Blocks.Interfaces.BooleanInput on[numBoi]
    "On signal of the plant"
    annotation (Placement(transformation(extent={{-120,40},{-100,60}}),iconTransformation(extent={{-120,40},{-100,60}})));
  Modelica.Blocks.Interfaces.RealInput TSet[num]
    "Heating water setpoint temperature[K]."
    annotation (Placement(transformation(extent={{-120,-42},{-100,-22}}),iconTransformation(extent={{-120,-50},{-100,-30}})));
  Modelica.Blocks.Interfaces.RealOutput Q_Boi[numBoi]
    "Boiler heat flow rate."
    annotation (Placement(transformation(extent={{100,40},{120,60}}),iconTransformation(extent={{100,40},{120,60}})));
equation
  for i in 1:numBoi loop
    connect(val[i].port_b,port_b)
      annotation (Line(points={{56,0},{100,0}},color={0,127,255}));
    connect(port_a,boi[i].port_a)
      annotation (Line(points={{-100,0},{-20,0}},color={0,127,255}));
  end for;
  connect(filter.u,booToRea.y)
    annotation (Line(points={{-55.2,84},{-58,84},{-58,50},{-59,50}},color={0,0,127}));
  connect(on,booToRea.u)
    annotation (Line(points={{-110,50},{-82,50}},color={255,0,255}));
  connect(val.port_a,boi.port_b)
    annotation (Line(points={{36,0},{0,0}},color={0,127,255}));
  connect(boi.Q_flow,Q_Boi)
    annotation (Line(points={{1,8},{18,8},{18,50},{110,50}},color={0,0,127}));
  connect(TSet,boi.TSet)
    annotation (Line(points={{-110,-32},{-68,-32},{-68,8},{-22,8}},color={0,0,127}));
  connect(on,boi.on)
    annotation (Line(points={{-110,50},{-88,50},{-88,-4},{-22,-4}},color={255,0,255}));
  annotation (
    Documentation(
      info="<html>
<p>
This model connects two identical boilers in parallel, each boiler is isolated
with an on/off two-way valve.
</p>
</html>",
      revisions="<html>
<ul>
<li>
August 25, 2020, by Hagar Elarga:<br/>
First implementation.
</li>
</ul>
</html>"),
    Icon(
      graphics={
        Line(
          points={{-92,0},{0,0}},
          color={28,108,200},
          thickness=1),
        Line(
          points={{0,0},{92,0}},
          color={238,46,47},
          thickness=1),
        Rectangle(
          extent={{-54,54},{54,-54}},
          lineColor={102,44,145})}));
end Boiler_TParaller;
