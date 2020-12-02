//within geojson_modelica_translator.model_connectors.templates
partial model PartialBuildingWithIndirectETS
  "Partial model of a building with an energy transfer station"
  replaceable package Medium=Modelica.Media.Interfaces.PartialMedium
    "Source medium (heating or chilled water)";
  extends Buildings.Fluid.Interfaces.PartialFourPortInterface(
    final m1_flow_small=1E-4*m1_flow_nominal,
    final m2_flow_small=1E-4*m2_flow_nominal,
    final allowFlowReversal1=allowFlowReversalDis,
    final allowFlowReversal2=allowFlowReversalBui);
  parameter Boolean allowFlowReversalBui=false
    "Set to true to allow flow reversal on the building side"
    annotation (Dialog(tab="Assumptions"),Evaluate=true);
  parameter Boolean allowFlowReversalDis=false
    "Set to true to allow flow reversal on the district side"
    annotation (Dialog(tab="Assumptions"),Evaluate=true);
  // IO CONNECTORS
  Modelica.Blocks.Interfaces.RealInput TSetWat
    "Chilled/Heating water set point."
    annotation (Placement(transformation(extent={{-20,-20},{20,20}},rotation=0,origin={-120,20}),iconTransformation(extent={{-10,-10},{10,10}},rotation=0,origin={-110,30})));
  // COMPONENTS
  replaceable Buildings.Experimental.DHC.Loads.BaseClasses.PartialBuilding bui(
    final allowFlowReversal=allowFlowReversalBui)
    "Building model "
    annotation (Placement(transformation(extent={{-30,8},{30,68}})));
  replaceable HeatingIndirect ets(
    redeclare package Medium=Medium,
    allowFlowReversal1=false,
    allowFlowReversal2=false)
    "Energy transfer station model"
    annotation (Placement(transformation(extent={{-28,-84},{32,-24}})));
  Modelica.Fluid.Sources.FixedBoundary preSou(
    redeclare package Medium=Medium,
    nPorts=1)
    annotation (Placement(transformation(extent={{-80,-98},{-60,-78}})));
  annotation (
    Dialog(
      group="ETS model parameters"),
    DefaultComponentName="bui",
    Icon(
      coordinateSystem(
        preserveAspectRatio=false,
        extent={{-100,-100},{100,100}}),
      graphics={
        Rectangle(
          extent={{-60,-34},{0,-28}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={255,0,0},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{-60,-34},{0,-40}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={0,0,255},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{0,-40},{60,-34}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={255,0,0},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{0,-28},{60,-34}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={0,0,255},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{60,6},{100,0}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={0,0,255},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{-100,0},{-60,-6}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={0,0,255},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{-100,0},{-60,6}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={255,0,0},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{60,-6},{100,0}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={255,0,0},
          fillPattern=FillPattern.Solid),
        Polygon(
          points={{0,80},{-40,60},{40,60},{0,80}},
          lineColor={95,95,95},
          smooth=Smooth.None,
          fillPattern=FillPattern.Solid,
          fillColor={95,95,95}),
        Rectangle(
          extent={{-40,60},{40,-40}},
          lineColor={150,150,150},
          fillPattern=FillPattern.Sphere,
          fillColor={255,255,255}),
        Rectangle(
          extent={{-30,30},{-10,50}},
          lineColor={255,255,255},
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{10,30},{30,50}},
          lineColor={255,255,255},
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{-30,-10},{-10,10}},
          lineColor={255,255,255},
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{10,-10},{30,10}},
          lineColor={255,255,255},
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{-100,100},{100,-100}},
          lineColor={0,0,0}),
        Rectangle(
          extent={{-20,-3},{20,3}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={255,0,0},
          fillPattern=FillPattern.Solid,
          origin={63,-20},
          rotation=90),
        Rectangle(
          extent={{-19,3},{19,-3}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={0,0,255},
          fillPattern=FillPattern.Solid,
          origin={-63,-21},
          rotation=90),
        Rectangle(
          extent={{-19,-3},{19,3}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={255,0,0},
          fillPattern=FillPattern.Solid,
          origin={-57,-13},
          rotation=90),
        Rectangle(
          extent={{-19,3},{19,-3}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={0,0,255},
          fillPattern=FillPattern.Solid,
          origin={57,-13},
          rotation=90)}),
    Diagram(
      coordinateSystem(
        preserveAspectRatio=false)));
end PartialBuildingWithIndirectETS;
