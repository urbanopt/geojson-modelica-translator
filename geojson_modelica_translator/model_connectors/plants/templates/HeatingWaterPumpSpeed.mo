within geojson_modelica_translator.model_connectors.templates;
model HeatingWaterPumpSpeed
  parameter Integer numPum(
    min=1,
    max=2)=2
    "Number of heating water pumps, maximum is 2";
  parameter Modelica.Units.SI.PressureDifference dpSetPoi(
    displayUnit="Pa")
    "Pressure difference setpoint";
  parameter Modelica.Units.SI.Time tWai
    "Waiting time";
  parameter Modelica.Units.SI.MassFlowRate m_flow_nominal
    "Nominal mass flow rate of single heating water pump";
  parameter Modelica.Units.SI.MassFlowRate mMin_flow=0.2*m_flow_nominal
    "Minimum mass flow rate";
  parameter Real minSpe=0.05
    "Minimum speed ratio required by heating water pumps";
  parameter Modelica.Units.SI.Time riseTime=120
    "Rise time till the pump reaches its maximum speed";
  parameter Modelica.Blocks.Types.SimpleController controllerType=Modelica.Blocks.Types.SimpleController.PI
    "Type of pump speed controller";
  parameter Real k
    "Gain of controller";
  parameter Modelica.Units.SI.Time Ti
    "Time constant of Integrator block"
    annotation (Dialog(enable=controllerType == Modelica.Blocks.Types.SimpleController.PI or controllerType == Modelica.Blocks.Types.SimpleController.PID));
  parameter Modelica.Units.SI.Time Td(
    min=0)=0.1
    "Time constant of Derivative block"
    annotation (Dialog(enable=controllerType == Modelica.Blocks.Types.SimpleController.PD or controllerType == Modelica.Blocks.Types.SimpleController.PID));
  Buildings.Controls.OBC.CDL.Interfaces.RealInput meaFloByPas(
    final unit="kg/s")
    "Measured  bypass mass flow."
    annotation (Placement(transformation(extent={{-120,-98},{-100,-78}}),iconTransformation(extent={{-120,-98},{-100,-78}})));
  Buildings.Controls.OBC.CDL.Interfaces.RealOutput deCouVal
    "Decoupler line valve."
    annotation (Placement(transformation(extent={{100,-60},{120,-40}})));
  Buildings.Controls.OBC.CDL.Interfaces.BooleanInput ON[numPum]
    "Boiler on/off signal."
    annotation (Placement(transformation(extent={{-120,76},{-100,96}}),iconTransformation(extent={{-120,56},{-100,76}})));
  Buildings.Controls.OBC.CDL.Interfaces.RealInput masFloPum(
    final unit="kg/s")
    "Total mass flowrate of heating water pumps"
    annotation (Placement(transformation(extent={{-120,34},{-100,54}}),iconTransformation(extent={{-120,34},{-100,54}})));
  Buildings.Controls.OBC.CDL.Interfaces.RealInput dpMea(
    final unit="Pa")
    "Measured pressure difference"
    annotation (Placement(transformation(extent={{-120,-60},{-100,-40}}),iconTransformation(extent={{-120,-60},{-100,-40}})));
  Buildings.Controls.OBC.CDL.Interfaces.RealOutput y[numPum](
    unit="1",
    min=0,
    max=1)
    "Pump speed signal"
    annotation (Placement(transformation(extent={{100,-10},{120,10}})));
  Modelica.Blocks.Math.Product pumSpe[numPum]
    "Output pump speed"
    annotation (Placement(transformation(extent={{34,-10},{54,10}})));
  Buildings.Applications.BaseClasses.Controls.VariableSpeedPumpStage pumStaCon(
    tWai=tWai,
    m_flow_nominal=m_flow_nominal,
    minSpe=minSpe)
    "heating water pump staging control"
    annotation (Placement(transformation(extent={{-10,-10},{10,10}})));
  Buildings.Controls.Continuous.LimPID conPID(
    controllerType=Modelica.Blocks.Types.SimpleController.PI,
    Ti=Ti,
    k=k,
    Td=60,
    yMax=1,
    yMin=0,
    y_start=conPID.yMin,
    reverseActing=true,
    reset=Buildings.Types.Reset.Disabled,
    y_reset=0)
    "PID controller of pump speed"
    annotation (Placement(transformation(extent={{-60,-10},{-40,10}})));
  Modelica.Blocks.Sources.Constant dpSetSca(
    k=1)
    "Scaled differential pressure setpoint"
    annotation (Placement(transformation(extent={{-100,-10},{-80,10}})));
  Modelica.Blocks.Math.Gain gai(
    k=1/dpSetPoi)
    "Multiplier gain for normalizing dp input"
    annotation (Placement(transformation(extent={{-80,-60},{-60,-40}})));
  Buildings.Controls.Continuous.LimPID bypValCon(
    controllerType=Modelica.Blocks.Types.SimpleController.PI,
    k=1,
    Ti=60,
    reverseActing=false,
    reset=Buildings.Types.Reset.Disabled,
    y_reset=0)
    "Heating water bypass valve controller"
    annotation (Placement(transformation(extent={{-10,-60},{10,-40}})));
  Modelica.Blocks.Sources.RealExpression norDecSetMasFlo(
    y=1)
    "Normalized decoupler line mass flow rate."
    annotation (Placement(transformation(extent={{-40,-60},{-20,-40}})));
  Modelica.Blocks.Sources.RealExpression norDecMasFlo(
    y=meaFloByPas/(
      if ON[numPum] then
        numPum*mMin_flow
      else
        mMin_flow))
    "Normalised decoupler line measured mass flow rate."
    annotation (Placement(transformation(extent={{42,-84},{22,-64}})));
equation
  connect(pumStaCon.masFloPum,masFloPum)
    annotation (Line(points={{-12,8},{-22,8},{-22,66},{-110,66}},color={0,0,127}));
  connect(conPID.y,pumStaCon.speSig)
    annotation (Line(points={{-39,0},{-20,0},{-20,4},{-12,4}},color={0,0,127}));
  connect(dpSetSca.y,conPID.u_s)
    annotation (Line(points={{-79,0},{-62,0}},color={0,0,127}));
  connect(dpMea,gai.u)
    annotation (Line(points={{-110,-50},{-82,-50}},color={0,0,127}));
  connect(conPID.u_m,gai.y)
    annotation (Line(points={{-50,-12},{-50,-50},{-59,-50}},color={0,0,127}));
  connect(bypValCon.u_s,norDecSetMasFlo.y)
    annotation (Line(points={{-12,-50},{-19,-50}},color={0,0,127}));
  connect(bypValCon.u_m,norDecMasFlo.y)
    annotation (Line(points={{0,-62},{0,-74},{21,-74}},color={0,0,127}));
  connect(bypValCon.y,deCouVal)
    annotation (Line(points={{11,-50},{110,-50}},color={0,0,127}));
  connect(pumStaCon.y,pumSpe.u1)
    annotation (Line(points={{11,0},{20,0},{20,6},{32,6}},color={0,0,127}));
  connect(conPID.y,pumSpe[1].u2)
    annotation (Line(points={{-39,0},{-20,0},{-20,-26},{26,-26},{26,-6},{32,-6}},color={0,0,127}));
  connect(conPID.y,pumSpe[2].u2)
    annotation (Line(points={{-39,0},{-20,0},{-20,-26},{26,-26},{26,-6},{32,-6}},color={0,0,127}));
  connect(pumSpe.y,y)
    annotation (Line(points={{55,0},{80,0},{80,0},{110,0}},color={0,0,127}));
  annotation (
    Icon(
      coordinateSystem(
        preserveAspectRatio=false),
      graphics={
        Rectangle(
          extent={{-100,100},{100,-100}},
          lineColor={0,0,127},
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid),
        Text(
          extent={{-150,150},{150,110}},
          textString="%name",
          lineColor={0,0,255})}),
    Diagram(
      coordinateSystem(
        preserveAspectRatio=false)),
    Documentation(
      info="<html>
<p>
the model represents variable speed parrallel pumps controller.
</p>
</html>",
      revisions="<html>
<ul>
<li>
May 3, 2020, by Hagar Elarga:<br/>
First implementation.
</li>
</ul>
</html>"));
end HeatingWaterPumpSpeed;
