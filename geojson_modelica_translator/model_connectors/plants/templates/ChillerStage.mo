within geojson_modelica_translator.model_connectors.templates;
model ChillerStage
  "Stage controller for chillers"
  parameter Modelica.Units.SI.Time tWai
    "Waiting time";
  parameter Modelica.Units.SI.Power QEva_nominal
    "Nominal cooling capaciaty (negative means cooling)";
  parameter Modelica.Units.SI.Power criPoiLoa=0.55*QEva_nominal
    "Critical point of cooling load for switching one chiller on or off";
  parameter Modelica.Units.SI.Power dQ=0.25*QEva_nominal
    "Deadband for critical point of cooling load";
  Modelica.Blocks.Interfaces.RealInput QLoa(
    unit="W")
    "Total cooling load, negative"
    annotation (Placement(transformation(extent={{-140,-60},{-100,-20}})));
  Modelica.Blocks.Interfaces.BooleanInput on
    "On signal of the chillers"
    annotation (Placement(transformation(extent={{-140,20},{-100,60}})));
  Modelica.Blocks.Interfaces.RealOutput y[2]
    "On/off signal for the chillers - 0: off; 1: on"
    annotation (Placement(transformation(extent={{100,-10},{120,10}})));
  Modelica.StateGraph.InitialStep off(
    nIn=1,
    nOut=1)
    "No cooling is demanded"
    annotation (Placement(transformation(extent={{-10,10},{10,-10}},rotation=-90,origin={-50,70})));
  Modelica.StateGraph.StepWithSignal oneOn(
    nOut=2,
    nIn=2)
    "One chiller is on"
    annotation (Placement(transformation(extent={{10,-10},{-10,10}},rotation=90,origin={-50,0})));
  Modelica.StateGraph.StepWithSignal twoOn(
    nIn=1,
    nOut=1)
    "Two chillers are on"
    annotation (Placement(transformation(extent={{10,-10},{-10,10}},rotation=90,origin={-50,-70})));
  Modelica.StateGraph.Transition offToOne(
    condition=on == true,
    enableTimer=true,
    waitTime=tWai)
    "Condition of transition from off to one chiller on"
    annotation (Placement(transformation(extent={{10,10},{-10,-10}},rotation=90,origin={-50,40})));
  Modelica.StateGraph.Transition oneToTwo(
    enableTimer=true,
    waitTime=tWai,
    condition=-QLoa >=-(criPoiLoa+dQ))
    "Condition of transition from one chiller to two chillers"
    annotation (Placement(transformation(extent={{10,10},{-10,-10}},rotation=90,origin={-50,-40})));
  Modelica.StateGraph.Transition twoToOne(
    enableTimer=true,
    waitTime=tWai,
    condition=-QLoa <-(criPoiLoa-dQ))
    "Condition of transion from two chillers to one chiller"
    annotation (Placement(transformation(extent={{-10,10},{10,-10}},rotation=90,origin={0,-40})));
  Modelica.StateGraph.Transition oneToOff(
    condition=on == false,
    enableTimer=true,
    waitTime=tWai)
    "Transition from one chiller to off"
    annotation (Placement(transformation(extent={{-10,10},{10,-10}},rotation=90,origin={-20,40})));
  inner Modelica.StateGraph.StateGraphRoot stateGraphRoot
    annotation (Placement(transformation(extent={{60,60},{80,80}})));
  Modelica.Blocks.Tables.CombiTable1Ds combiTable1Ds(
    table=[
      0,0,0;
      1,1,0;
      2,1,1])
    annotation (Placement(transformation(extent={{70,-10},{90,10}})));
  Buildings.Controls.OBC.CDL.Conversions.BooleanToInteger booToInt(
    final integerTrue=1,
    final integerFalse=0)
    annotation (Placement(transformation(extent={{30,-40},{50,-20}})));
  Buildings.Controls.OBC.CDL.Conversions.BooleanToInteger booToInt1(
    final integerFalse=0,
    final integerTrue=2)
    annotation (Placement(transformation(extent={{30,-80},{50,-60}})));
  Buildings.Controls.OBC.CDL.Integers.Add addInt
    annotation (Placement(transformation(extent={{70,-60},{90,-40}})));
  Buildings.Controls.OBC.CDL.Conversions.IntegerToReal intToRea
    annotation (Placement(transformation(extent={{40,-10},{60,10}})));
equation
  connect(off.outPort[1],offToOne.inPort)
    annotation (Line(points={{-50,59.5},{-50,44}},color={0,0,0}));
  connect(oneToOff.outPort,off.inPort[1])
    annotation (Line(points={{-20,41.5},{-20,88},{-50,88},{-50,81}},color={0,0,0}));
  connect(oneToTwo.outPort,twoOn.inPort[1])
    annotation (Line(points={{-50,-41.5},{-50,-59}},color={0,0,0}));
  connect(twoOn.outPort[1],twoToOne.inPort)
    annotation (Line(points={{-50,-80.5},{-50,-88},{-2.22045e-16,-88},{-2.22045e-16,-44}},color={0,0,0}));
  connect(twoToOne.outPort,oneOn.inPort[2])
    annotation (Line(points={{0,-38.5},{0,16},{-49.5,16},{-49.5,11}},color={0,0,0}));
  connect(offToOne.outPort,oneOn.inPort[1])
    annotation (Line(points={{-50,38.5},{-50,24},{-50,11},{-50.5,11}},color={0,0,0}));
  connect(oneOn.outPort[2],oneToOff.inPort)
    annotation (Line(points={{-49.75,-10.5},{-49.75,-18},{-20,-18},{-20,36}},color={0,0,0}));
  connect(oneOn.outPort[1],oneToTwo.inPort)
    annotation (Line(points={{-50.25,-10.5},{-50.25,-18},{-50,-18},{-50,-36}},color={0,0,0}));
  connect(combiTable1Ds.y,y)
    annotation (Line(points={{91,0},{110,0}},color={0,0,127}));
  connect(combiTable1Ds.u,intToRea.y)
    annotation (Line(points={{68,0},{62,0}},color={0,0,127}));
  connect(addInt.u2,booToInt1.y)
    annotation (Line(points={{68,-56},{60,-56},{60,-70},{52,-70}},color={255,127,0}));
  connect(oneOn.active,booToInt.u)
    annotation (Line(points={{-39,0},{20,0},{20,-30},{28,-30}},color={255,0,255}));
  connect(twoOn.active,booToInt1.u)
    annotation (Line(points={{-39,-70},{28,-70}},color={255,0,255}));
  connect(booToInt.y,addInt.u1)
    annotation (Line(points={{52,-30},{60,-30},{60,-44},{68,-44}},color={255,127,0}));
  connect(addInt.y,intToRea.u)
    annotation (Line(points={{92,-50},{94,-50},{94,-14},{34,-14},{34,0},{38,0}},color={255,127,0}));
  annotation (
    Diagram(
      coordinateSystem(
        preserveAspectRatio=false,
        extent={{-100,-100},{100,100}})),
    Icon(
      coordinateSystem(
        preserveAspectRatio=false,
        extent={{-100,-100},{100,100}}),
      graphics={
        Rectangle(
          extent={{-100,-100},{100,100}},
          lineColor={0,0,127},
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid),
        Text(
          extent={{-150,150},{150,110}},
          textString="%name",
          lineColor={0,0,255})}),
    Documentation(
      revisions="<html>
<ul>
<li>
March 19, 2014 by Sen Huang:<br/>
First implementation.
</li>
</ul>
</html>"));
end ChillerStage;
