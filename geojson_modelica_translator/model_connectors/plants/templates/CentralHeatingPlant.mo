within geojson_modelica_translator.model_connectors.templates;
model CentralHeatingPlant
  "Central heating plant."
  package Medium=Buildings.Media.Water
    "MediumW model";
  parameter Integer numBoi=2
    "Number of boilers, maximum is 2";
  parameter Boolean show_T=true
    "= true, if actual temperature at port is computed"
    annotation (Dialog(tab="Advanced",group="Diagnostics"));
  // boiler parameters
  parameter Modelica.Units.SI.MassFlowRate mHW_flow_nominal
    "Nominal heating water mass flow rate"
    annotation (Dialog(group="Boiler"));
  parameter Modelica.Units.SI.Power QBoi_flow_nominal
    "Nominal heating capacity of single boiler"
    annotation (Dialog(group="Boiler"));
  parameter Modelica.Units.SI.MassFlowRate mMin_flow
    "Minimum mass flow rate of single boiler"
    annotation (Dialog(group="Boiler"));
  parameter Modelica.Units.SI.MassFlowRate mBoi_flow_nominal
    "Nominal mass flow rate of single boiler"
    annotation (Dialog(group="Boiler"));
  parameter Modelica.Units.SI.Pressure dpBoi_nominal
    "Pressure difference at the boiler water side"
    annotation (Dialog(group="Boiler"));
  parameter Modelica.Units.SI.TemperatureDifference delT_nominal
    "Design heating water temperature Difference";
  // pump parameters
  replaceable parameter Buildings.Fluid.Movers.Data.Generic perHWPum
    constrainedby Buildings.Fluid.Movers.Data.Generic
    "Performance data of heating water pump"
    annotation (Dialog(group="Pump"),choicesAllMatching=true,Placement(transformation(extent={{138,82},{152,96}})));
  // control settings
  parameter Modelica.Units.SI.Time tWai
    "Waiting time"
    annotation (Dialog(group="Control Settings"));
  parameter Modelica.Units.SI.PressureDifference dpSetPoi(
    displayUnit="Pa")
    "Demand side pressure difference setpoint"
    annotation (Dialog(group="Control Settings"));
  // diagnostics
  Medium.ThermodynamicState sta_a=Medium.setState_phX(
    port_a.p,
    noEvent(
      actualStream(
        port_a.h_outflow)),
    noEvent(
      actualStream(
        port_a.Xi_outflow))) if show_T
    "MediumW properties in port_a";
  Medium.ThermodynamicState sta_b=Medium.setState_phX(
    port_b.p,
    noEvent(
      actualStream(
        port_b.h_outflow)),
    noEvent(
      actualStream(
        port_b.Xi_outflow))) if show_T
    "MediumW properties in port_b";
  Modelica.Fluid.Interfaces.FluidPort_a port_a(
    redeclare package Medium=Medium)
    "Fluid connector a (positive design flow direction is from port_a to port_b)"
    annotation (Placement(transformation(extent={{150,40},{170,60}}),iconTransformation(extent={{90,40},{110,60}})));
  Modelica.Fluid.Interfaces.FluidPort_b port_b(
    redeclare package Medium=Medium)
    "Fluid connector b (positive design flow direction is from port_a to port_b)"
    annotation (Placement(transformation(extent={{150,-60},{170,-40}}),iconTransformation(extent={{90,-60},{110,-40}})));
  Modelica.Blocks.Interfaces.BooleanInput on
    "On signal of the plant"
    annotation (Placement(transformation(extent={{-160,58},{-140,78}}),iconTransformation(extent={{-140,60},{-100,100}})));
  Modelica.Blocks.Interfaces.RealInput dpMea(
    final unit="Pa")
    "Measured pressure difference"
    annotation (Placement(transformation(extent={{-160,-40},{-140,-20}}),iconTransformation(extent={{-140,-50},{-100,-10}})));
  Boiler_TParallel boiHotWat(
    redeclare package Medium=Medium,
    m_flow_nominal=mBoi_flow_nominal,
    Q_flow_nominal=QBoi_flow_nominal,
    dp_nominal=dpBoi_nominal,
    numBoi=numBoi)
    "Parallel boilers."
    annotation (Placement(transformation(extent={{10,-60},{30,-40}})));
  Buildings.Fluid.Sensors.TemperatureTwoPort THWSup(
    redeclare package Medium=Medium,
    m_flow_nominal=mHW_flow_nominal)
    "Heating water supply temperature"
    annotation (Placement(transformation(extent={{-10,-10},{10,10}},rotation=0,origin={132,-50})));
  HeatingWaterPumpSpeed heaWatPumCon(
    tWai=0,
    m_flow_nominal=mBoi_flow_nominal,
    dpSetPoi=dpSetPoi,
    controllerType=Modelica.Blocks.Types.SimpleController.PI,
    Ti=30,
    k=0.1)
    "Heating water pump controller."
    annotation (Placement(transformation(extent={{-120,-40},{-100,-20}})));
  BoilerStage boiStaCon(
    tWai=tWai,
    QBoi_nominal=QBoi_flow_nominal,
    criPoiLoa=0.55*QBoi_flow_nominal,
    dQ=0.25*QBoi_flow_nominal,
    numBoi=numBoi)
    "Boiler staging controller."
    annotation (Placement(transformation(extent={{-120,58},{-100,78}})));
  Modelica.Blocks.Sources.RealExpression mPum_flow(
    y=pumHW.port_a.m_flow)
    "Total heating water pump mass flow rate"
    annotation (Placement(transformation(extent={{-100,30},{-120,50}})));
  Buildings.Fluid.Sensors.TemperatureTwoPort THWRet(
    redeclare package Medium=Medium,
    m_flow_nominal=mHW_flow_nominal)
    "Heating water return temperature"
    annotation (Placement(transformation(extent={{10,-10},{-10,10}},rotation=0,origin={104,50})));
  Buildings.Applications.BaseClasses.Equipment.FlowMachine_y pumHW(
    per=fill(
      perHWPum,
      numBoi),
    redeclare package Medium=Medium,
    m_flow_nominal=mBoi_flow_nominal,
    dpValve_nominal=7000,
    num=numBoi,
    l=0.001)
    "Parallel heating water pumps."
    annotation (Placement(transformation(extent={{0,40},{-20,60}})));
  Buildings.Fluid.Actuators.Valves.TwoWayEqualPercentage valByp(
    redeclare package Medium=Medium,
    allowFlowReversal=true,
    m_flow_nominal=mHW_flow_nominal*0.05,
    dpValve_nominal=7000,
    l=0.001)
    "Heating water bypass valve"
    annotation (Placement(transformation(extent={{-10,10},{10,-10}},rotation=90,origin={54,0})));
  Buildings.Fluid.Sensors.MassFlowRate senMasFlo(
    redeclare package Medium=Medium)
    "Heating water return mass flow"
    annotation (Placement(transformation(extent={{42,40},{22,60}})));
  Buildings.Fluid.Sensors.MassFlowRate senMasFloByp(
    redeclare package Medium=Medium)
    "Heating water bypass valve mass flow meter"
    annotation (Placement(transformation(extent={{10,10},{-10,-10}},rotation=-90,origin={54,-30})));
  final parameter Medium.ThermodynamicState sta_default=Medium.setState_pTX(
    T=Medium.T_default,
    p=Medium.p_default,
    X=Medium.X_default)
    "Medium state at default properties";
  final parameter Modelica.Units.SI.SpecificHeatCapacity cp_default=Medium.specificHeatCapacityCp(
    sta_default)
    "Specific heat capacity of the fluid";
  Buildings.Fluid.Sources.Boundary_pT expTanHW(
    redeclare package Medium=Medium,
    nPorts=1)
    "Heating water expansion tank"
    annotation (Placement(transformation(extent={{-8,6},{12,26}})));
  Modelica.Blocks.Interfaces.RealInput THeaSet(
    final unit="K",
    displayUnit="degC")
    "Heating water setpoint."
    annotation (Placement(transformation(extent={{-160,-60},{-140,-40}}),iconTransformation(extent={{-140,-104},{-100,-64}})));
  Modelica.Blocks.Math.Product pumOn[numBoi]
    "Output pump speed"
    annotation (Placement(transformation(extent={{-80,0},{-60,20}})));
equation
  connect(THeaSet,boiHotWat.THeaWatSet)
    annotation (Line(points={{-150,-50},{-72,-50},{-72,-56},{9,-56}},color={0,0,127}));
  connect(on,boiStaCon.on)
    annotation (Line(points={{-150,68},{-121,68}},color={255,0,255}));
  connect(dpMea,heaWatPumCon.dpMea)
    annotation (Line(points={{-150,-30},{-138,-30},{-138,-35},{-121,-35}},color={0,0,127}));
  connect(valByp.port_a,senMasFloByp.port_b)
    annotation (Line(points={{54,-10},{54,-20}},color={0,127,255}));
  connect(senMasFloByp.m_flow,heaWatPumCon.meaFloByPas)
    annotation (Line(points={{43,-30},{40,-30},{40,-74},{-130,-74},{-130,-38.8},{-121,-38.8}},color={0,0,127}));
  connect(port_a,THWRet.port_a)
    annotation (Line(points={{160,50},{114,50}},color={0,127,255}));
  connect(pumHW.port_b,boiHotWat.port_a)
    annotation (Line(points={{-20,50},{-36,50},{-36,-50},{10,-50}},color={0,127,255}));
  connect(boiHotWat.port_b,THWSup.port_a)
    annotation (Line(points={{30,-50},{122,-50}},color={0,127,255}));
  connect(THWSup.port_b,port_b)
    annotation (Line(points={{142,-50},{160,-50}},color={0,127,255}));
  connect(pumHW.port_a,senMasFlo.port_b)
    annotation (Line(points={{0,50},{22,50}},color={0,127,255}));
  connect(senMasFlo.port_a,THWRet.port_b)
    annotation (Line(points={{42,50},{94,50}},color={0,127,255}));
  connect(heaWatPumCon.deCouVal,valByp.y)
    annotation (Line(points={{-99,-35},{-94,-35},{-94,-70},{80,-70},{80,0},{74,0},{74,-6},{66,-6}},color={0,0,127}));
  connect(valByp.port_b,senMasFlo.port_a)
    annotation (Line(points={{54,10},{54,50},{42,50}},color={0,127,255}));
  connect(boiHotWat.port_b,senMasFloByp.port_a)
    annotation (Line(points={{30,-50},{54,-50},{54,-40}},color={0,127,255}));
  connect(expTanHW.ports[1],senMasFlo.port_a)
    annotation (Line(points={{12,16},{42,16},{42,50}},color={0,127,255}));
  connect(boiStaCon.y_On,boiHotWat.on)
    annotation (Line(points={{-99,70.6},{-72,70.6},{-72,-45},{9,-45}},color={255,0,255}));
  connect(THWSup.T,boiStaCon.TDisSup)
    annotation (Line(points={{132,-39},{132,96},{-134,96},{-134,70.6},{-121,70.6}},color={0,0,127}));
  connect(THWRet.T,boiStaCon.TDisRet)
    annotation (Line(points={{104,61},{104,88},{-130,88},{-130,73.4},{-121,73.4}},color={0,0,127}));
  connect(senMasFlo.m_flow,boiStaCon.mHeaDis)
    annotation (Line(points={{32,61},{32,86},{-126,86},{-126,76.6},{-121,76.6}},color={0,0,127}));
  connect(boiStaCon.y,pumOn.u1)
    annotation (Line(points={{-99,66},{-92,66},{-92,16},{-82,16}},color={0,0,127}));
  connect(heaWatPumCon.y,pumOn.u2)
    annotation (Line(points={{-99,-30},{-94,-30},{-94,4},{-82,4}},color={0,0,127}));
  connect(pumOn.y,pumHW.u)
    annotation (Line(points={{-59,10},{-46,10},{-46,72},{12,72},{12,54},{2,54}},color={0,0,127}));
  connect(boiStaCon.y_On,heaWatPumCon.ON)
    annotation (Line(points={{-99,70.6},{-88,70.6},{-88,24},{-128,24},{-128,-23.4},{-121,-23.4}},color={255,0,255}));
  connect(mPum_flow.y,heaWatPumCon.masFloPum)
    annotation (Line(points={{-121,40},{-134,40},{-134,-25.6},{-121,-25.6}},color={0,0,127}));
  annotation (
    Diagram(
      coordinateSystem(
        preserveAspectRatio=false,
        extent={{-140,-80},{120,100}})),
    Icon(
      graphics={
        Rectangle(
          extent={{-100,-100},{100,100}},
          lineColor={0,0,127},
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid),
        Polygon(
          points={{-62,-14},{-62,-14}},
          lineColor={238,46,47},
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid),
        Polygon(
          points={{80,-60},{-80,-60},{-80,60},{-60,60},{-60,0},{-40,0},{-40,20},{0,0},{0,20},{40,0},{40,20},{80,0},{80,-60}},
          lineColor={95,95,95},
          fillColor={238,46,47},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{46,-38},{58,-26}},
          lineColor={255,255,255},
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{62,-38},{74,-26}},
          lineColor={255,255,255},
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{62,-54},{74,-42}},
          lineColor={255,255,255},
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{46,-54},{58,-42}},
          lineColor={255,255,255},
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{22,-54},{34,-42}},
          lineColor={255,255,255},
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{6,-54},{18,-42}},
          lineColor={255,255,255},
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{6,-38},{18,-26}},
          lineColor={255,255,255},
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{22,-38},{34,-26}},
          lineColor={255,255,255},
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{-18,-54},{-6,-42}},
          lineColor={255,255,255},
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{-34,-54},{-22,-42}},
          lineColor={255,255,255},
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{-34,-38},{-22,-26}},
          lineColor={255,255,255},
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{-18,-38},{-6,-26}},
          lineColor={255,255,255},
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid),
        Text(
          extent={{-149,-114},{151,-154}},
          lineColor={0,0,255},
          textString="%name")}),
    Documentation(
      info="<html>
   <p>
   This model presents a heating water central plant for the distrcit systems application.
   </p>
   </html>",
      revisions="<html>
   <ul>
   <li>
   June 30, 2020, by Hagar Elarga:<br/>
   First implementation.
   </li>
   </ul>
   </html>"));
end CentralHeatingPlant;
