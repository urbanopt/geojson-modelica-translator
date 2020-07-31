//within geojson_modelica_translator.model_connectors.templates
partial model PartialBuildingWithCoolingIndirectETS
  "Partial model of a building with an energy transfer station"
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
  Modelica.Blocks.Interfaces.RealInput TSetChiWat
    "Chilled water set point"
    annotation (Placement(transformation(extent={{-20,-20},{20,20}},rotation=0,origin={-120,20}),iconTransformation(extent={{-10,-10},{10,10}},rotation=0,origin={-110,30})));
  // COMPONENTS
  replaceable PartialBuilding bui(
    final allowFlowReversal=allowFlowReversalBui)
    "Building model "
    annotation (Placement(transformation(extent={{-30,8},{30,68}})));
  replaceable CoolingIndirect ets
    annotation (Placement(transformation(extent={{-30,-82},{30,-22}})));
  Buildings.Fluid.Actuators.Valves.TwoWayLinear val(
    use_inputFilter=false,
    final linearized=false)
    "Two way modulating valve"
    annotation (Placement(transformation(extent={{10,10},{-10,-10}},origin={60,-86})));
  Modelica.Fluid.Sources.FixedBoundary preSou(
    nPorts=1)
    annotation (Placement(transformation(extent={{-100,-98},{-80,-78}})));
equation
  connect(TSetChiWat,ets.TSetBuiSup)
    annotation (Line(points={{-120,20},{-74,20},{-74,-52},{-36,-52}},color={0,0,127}));
  connect(port_b1,bui.ports_bHeaWat[1])
    annotation (Line(points={{100,60},{60,60},{60,32},{30,32}},color={0,127,255}));
  connect(port_a1,bui.ports_aHeaWat[1])
    annotation (Line(points={{-100,60},{-60,60},{-60,32},{-30,32}},color={0,127,255}));
  connect(val.port_b,ets.port_a1)
    annotation (Line(points={{50,-86},{-54,-86},{-54,-34},{-30,-34}},color={0,127,255}));
  connect(port_a2,val.port_a)
    annotation (Line(points={{100,-60},{76,-60},{76,-86},{70,-86}},color={0,127,255}));
  connect(ets.port_b1,port_b2)
    annotation (Line(points={{30,-34},{46,-34},{46,0},{-80,0},{-80,-60},{-100,-60}},color={0,127,255}));
  connect(ets.port_a2,bui.ports_bChiWat[1])
    annotation (Line(points={{30,-70},{60,-70},{60,20},{30,20}},color={0,127,255}));
  connect(ets.port_b2,preSou.ports[1])
    annotation (Line(points={{-30,-70},{-62,-70},{-62,-88},{-80,-88}},color={0,127,255}));
  connect(ets.port_b2,bui.ports_aChiWat[1])
    annotation (Line(points={{-30,-70},{-62,-70},{-62,20},{-30,20}},color={0,127,255}));
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
end PartialBuildingWithCoolingIndirectETS;
