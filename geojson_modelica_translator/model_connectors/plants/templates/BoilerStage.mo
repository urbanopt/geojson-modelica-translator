within geojson_modelica_translator.model_connectors.templates;
model BoilerStage
  "Stage controller for boilers"
  parameter Modelica.Units.SI.Time tWai
    "Waiting time";
  parameter Modelica.Units.SI.Power QBoi_nominal
    "Nominal heating capaciaty";
  parameter Modelica.Units.SI.Power criPoiLoa=0.55*QBoi_nominal
    "Critical point of heating load for switching one boiler on or off";
  parameter Modelica.Units.SI.Power dQ=0.25*QBoi_nominal
    "Deadband for critical point of heating load";
  parameter Integer numBoi
    "Number of boilers";
  Modelica.StateGraph.InitialStep off(
    nIn=1,
    nOut=1)
    "No heating is demanded"
    annotation (Placement(transformation(extent={{-10,10},{10,-10}},rotation=-90,origin={-52,56})));
  Modelica.StateGraph.StepWithSignal oneOn(
    nOut=2,
    nIn=2)
    "One boiler is on"
    annotation (Placement(transformation(extent={{10,-10},{-10,10}},rotation=90,origin={-52,-14})));
  Modelica.StateGraph.StepWithSignal twoOn(
    nIn=1,
    nOut=1)
    "Two boilers are on"
    annotation (Placement(transformation(extent={{10,-10},{-10,10}},rotation=90,origin={-52,-84})));
  Modelica.StateGraph.Transition offToOne(
    condition=on == true,
    enableTimer=true,
    waitTime=tWai)
    "Condition of transition from off to one boiler on"
    annotation (Placement(transformation(extent={{10,10},{-10,-10}},rotation=90,origin={-52,26})));
  Modelica.StateGraph.Transition oneToTwo(
    enableTimer=true,
    waitTime=tWai,
    condition=QLoa >=(criPoiLoa+dQ))
    "Condition of transition from one boiler to two boilers"
    annotation (Placement(transformation(extent={{10,10},{-10,-10}},rotation=90,origin={-52,-54})));
  Modelica.StateGraph.Transition twoToOne(
    enableTimer=true,
    waitTime=tWai,
    condition=QLoa <(criPoiLoa-dQ))
    "Condition of transion from two boilers to one boiler"
    annotation (Placement(transformation(extent={{-10,10},{10,-10}},rotation=90,origin={-2,-54})));
  Modelica.StateGraph.Transition oneToOff(
    condition=on == false,
    enableTimer=true,
    waitTime=tWai)
    "Transition from one boiler to off"
    annotation (Placement(transformation(extent={{-10,10},{10,-10}},rotation=90,origin={-12,26})));
  inner Modelica.StateGraph.StateGraphRoot stateGraphRoot
    annotation (Placement(transformation(extent={{-100,-80},{-80,-60}})));
  Modelica.Blocks.Tables.CombiTable1Ds comTab(
    table=[
      0,0,0;
      1,1,0;
      2,1,1])
    annotation (Placement(transformation(extent={{68,-24},{88,-4}})));
  Buildings.Controls.OBC.CDL.Conversions.BooleanToInteger booToInt(
    final integerTrue=1,
    final integerFalse=0)
    annotation (Placement(transformation(extent={{18,-54},{38,-34}})));
  Buildings.Controls.OBC.CDL.Conversions.BooleanToInteger booToInt1(
    final integerFalse=0,
    final integerTrue=2)
    annotation (Placement(transformation(extent={{18,-94},{38,-74}})));
  Buildings.Controls.OBC.CDL.Integers.Add addInt
    annotation (Placement(transformation(extent={{58,-74},{78,-54}})));
  Buildings.Controls.OBC.CDL.Conversions.IntegerToReal intToRea
    annotation (Placement(transformation(extent={{36,-24},{56,-4}})));
  Modelica.Blocks.Math.RealToBoolean boiOn[numBoi]
    "Real value to boolean value"
    annotation (Placement(transformation(extent={{66,16},{86,36}})));
  Modelica.Blocks.Interfaces.BooleanOutput y_On[numBoi]
    "On signal of the boilers"
    annotation (Placement(transformation(extent={{100,16},{120,36}}),iconTransformation(extent={{100,16},{120,36}})));
  Modelica.Blocks.Math.Add dT(
    final k1=1,
    final k2=-1)
    "Temperature difference"
    annotation (Placement(transformation(extent={{-60,102},{-40,122}})));
  Modelica.Blocks.Math.Product pro
    "Product"
    annotation (Placement(transformation(extent={{0,100},{20,120}})));
  Modelica.Blocks.Math.Gain cp(
    final k=4200)
    "Specific heat multiplier to calculate heat flow rate"
    annotation (Placement(transformation(extent={{40,100},{60,120}})));
  Modelica.Blocks.Interfaces.RealInput TDisSup(
    unit="K",
    displayUnit="degC")
    "Heating water supply temperature( distrcit side)."
    annotation (Placement(transformation(extent={{-120,16},{-100,36}}),iconTransformation(extent={{-120,16},{-100,36}})));
  Modelica.Blocks.Interfaces.RealInput TDisRet(
    unit="K",
    displayUnit="degC")
    "Heating water return temperature( distrcit side)."
    annotation (Placement(transformation(extent={{-120,44},{-100,64}}),iconTransformation(extent={{-120,44},{-100,64}})));
  Modelica.Blocks.Interfaces.RealInput mHeaDis(
    unit="kg/s")
    "Heating water mass flow rate distrcit side)."
    annotation (Placement(transformation(extent={{-120,76},{-100,96}}),iconTransformation(extent={{-120,76},{-100,96}})));
  Modelica.Blocks.Interfaces.BooleanInput on
    "On signal of the boilers"
    annotation (Placement(transformation(extent={{-120,-10},{-100,10}}),iconTransformation(extent={{-120,-10},{-100,10}})));
  Modelica.Blocks.Interfaces.RealOutput y[2]
    "On/off signal for the boilers - 0: off; 1: on"
    annotation (Placement(transformation(extent={{100,-30},{120,-10}}),iconTransformation(extent={{100,-30},{120,-10}})));
  Modelica.Blocks.Interfaces.RealOutput QLoa(
    unit="W")
    "Total heating loads"
    annotation (Placement(transformation(extent={{100,70},{120,90}}),iconTransformation(extent={{100,70},{120,90}})));
equation
  connect(off.outPort[1],offToOne.inPort)
    annotation (Line(points={{-52,45.5},{-52,30}},color={0,0,0}));
  connect(oneToOff.outPort,off.inPort[1])
    annotation (Line(points={{-12,27.5},{-12,74},{-52,74},{-52,67}},color={0,0,0}));
  connect(oneToTwo.outPort,twoOn.inPort[1])
    annotation (Line(points={{-52,-55.5},{-52,-73}},color={0,0,0}));
  connect(twoOn.outPort[1],twoToOne.inPort)
    annotation (Line(points={{-52,-94.5},{-52,-102},{-2,-102},{-2,-58}},color={0,0,0}));
  connect(twoToOne.outPort,oneOn.inPort[2])
    annotation (Line(points={{-2,-52.5},{-2,6},{-51.5,6},{-51.5,-3}},color={0,0,0}));
  connect(offToOne.outPort,oneOn.inPort[1])
    annotation (Line(points={{-52,24.5},{-52,-3},{-52.5,-3}},color={0,0,0}));
  connect(oneOn.outPort[2],oneToOff.inPort)
    annotation (Line(points={{-51.75,-24.5},{-51.75,-34},{-12,-34},{-12,22}},color={0,0,0}));
  connect(oneOn.outPort[1],oneToTwo.inPort)
    annotation (Line(points={{-52.25,-24.5},{-52.25,-32},{-52,-32},{-52,-50}},color={0,0,0}));
  connect(comTab.y,y)
    annotation (Line(points={{89,-14},{100,-14},{100,-20},{110,-20}},color={0,0,127}));
  connect(comTab.u,intToRea.y)
    annotation (Line(points={{66,-14},{58,-14}},color={0,0,127}));
  connect(addInt.u2,booToInt1.y)
    annotation (Line(points={{56,-70},{46,-70},{46,-84},{40,-84}},color={255,127,0}));
  connect(oneOn.active,booToInt.u)
    annotation (Line(points={{-41,-14},{2,-14},{2,-44},{16,-44}},color={255,0,255}));
  connect(twoOn.active,booToInt1.u)
    annotation (Line(points={{-41,-84},{16,-84}},color={255,0,255}));
  connect(booToInt.y,addInt.u1)
    annotation (Line(points={{40,-44},{44,-44},{44,-58},{56,-58}},color={255,127,0}));
  connect(addInt.y,intToRea.u)
    annotation (Line(points={{80,-64},{92,-64},{92,-28},{32,-28},{32,-14},{34,-14}},color={255,127,0}));
  connect(comTab.y,boiOn.u)
    annotation (Line(points={{89,-14},{90,-14},{90,6},{58,6},{58,26},{64,26}},color={0,0,127}));
  connect(boiOn.y,y_On)
    annotation (Line(points={{87,26},{110,26}},color={255,0,255}));
  connect(dT.y,pro.u1)
    annotation (Line(points={{-39,112},{-13,112},{-13,116},{-2,116}},color={0,0,127}));
  connect(pro.y,cp.u)
    annotation (Line(points={{21,110},{38,110}},color={0,0,127}));
  connect(TDisSup,dT.u1)
    annotation (Line(points={{-110,26},{-88,26},{-88,118},{-62,118}},color={0,0,127}));
  connect(TDisRet,dT.u2)
    annotation (Line(points={{-110,54},{-80,54},{-80,106},{-62,106}},color={0,0,127}));
  connect(mHeaDis,pro.u2)
    annotation (Line(points={{-110,86},{-70,86},{-70,88},{-20,88},{-20,104},{-2,104}},color={0,0,127}));
  connect(cp.y,QLoa)
    annotation (Line(points={{61,110},{86,110},{86,80},{110,80}},color={0,0,127}));
  annotation (
    Diagram(
      coordinateSystem(
        preserveAspectRatio=false,
        extent={{-100,-100},{100,140}})),
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
September 01, 2020 by Hagar Elarga:<br/>
First implementation.
</li>
</ul>
</html>"));
end BoilerStage;
