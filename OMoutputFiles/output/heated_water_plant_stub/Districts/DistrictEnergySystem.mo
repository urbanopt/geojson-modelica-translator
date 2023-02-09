within heated_water_plant_stub.Districts;
model DistrictEnergySystem
  extends Modelica.Icons.Example;
  // District Parameters
  package MediumW=Buildings.Media.Water
    "Source side medium";
  package MediumA=Buildings.Media.Air
    "Load side medium";

  // TODO: dehardcode these
  parameter Modelica.Units.SI.TemperatureDifference delChiWatTemDis(displayUnit="degC")=7;
  parameter Modelica.Units.SI.TemperatureDifference delChiWatTemBui(displayUnit="degC")=5;
  parameter Modelica.Units.SI.TemperatureDifference delHeaWatTemDis(displayUnit="degC")=12;
  parameter Modelica.Units.SI.TemperatureDifference delHeaWatTemBui(displayUnit="degC")=5;

  // Models

  //
  // Begin Model Instance for MyNetworkHeatedWaterStub
  // Source template: /model_connectors/networks/templates/NetworkHeatedWaterStub_Instance.mopt
  //
  // heated water stub
  // TODO: move these components into a single component
  Buildings.Fluid.Sources.MassFlowSource_T supHeaWat(
    redeclare package Medium=MediumW,
    use_m_flow_in=true,
    use_T_in=false,
    T=68+273.15,
    nPorts=1)
    "Heating water supply temperature (district side)."
    annotation (Placement(transformation(extent={{-70.0,-50.0},{-50.0,-30.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinHeaWat(
    redeclare package Medium=MediumW,
    nPorts=1)
    "Heating water sink (district side)"
    annotation (Placement(transformation(extent={{-30.0,-50.0},{-10.0,-30.0}})));

  // NOTE: this differential pressure setpoint is currently utilized by plants elsewhere
  parameter Modelica.Units.SI.Pressure dpSetPoi_MyNetworkHeatedWaterStub=50000
    "Differential pressure setpoint";
  //
  // End Model Instance for MyNetworkHeatedWaterStub
  //


  
  //
  // Begin Model Instance for heaPla5ad49efc
  // Source template: /model_connectors/plants/templates/HeatingPlant_Instance.mopt
  //
  // heating plant instance
  parameter Modelica.Units.SI.MassFlowRate mHW_flow_nominal_heaPla5ad49efc=mBoi_flow_nominal_heaPla5ad49efc*heaPla5ad49efc.numBoi
    "Nominal heating water mass flow rate";
  parameter Modelica.Units.SI.MassFlowRate mBoi_flow_nominal_heaPla5ad49efc=QBoi_nominal_heaPla5ad49efc/(4200*heaPla5ad49efc.delT_nominal)
    "Nominal heating water mass flow rate";
  parameter Modelica.Units.SI.Power QBoi_nominal_heaPla5ad49efc=Q_flow_nominal_heaPla5ad49efc/heaPla5ad49efc.numBoi
    "Nominal heating capaciaty";
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_heaPla5ad49efc=1000000*2
    "Heating load";
  parameter Modelica.Units.SI.MassFlowRate mMin_flow_heaPla5ad49efc=0.2*mBoi_flow_nominal_heaPla5ad49efc
    "Minimum mass flow rate of single boiler";
  // controls
  parameter Modelica.Units.SI.Pressure pumDP=(heaPla5ad49efc.dpBoi_nominal+dpSetPoi_MyNetworkHeatedWaterStub+50000)
    "Heating water pump pressure drop";
  parameter Modelica.Units.SI.Time tWai_heaPla5ad49efc=30
    "Waiting time";
  parameter Buildings.Fluid.Movers.Data.Generic perHWPum_heaPla5ad49efc(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=mBoi_flow_nominal_heaPla5ad49efc/1000*{0.1,1.1},
      dp=pumDP*{1.1,0.1}))
    "Performance data for heating water pumps";

  heated_water_plant_stub.Plants.CentralHeatingPlant heaPla5ad49efc(
    perHWPum=perHWPum_heaPla5ad49efc,
    mHW_flow_nominal=mHW_flow_nominal_heaPla5ad49efc,
    QBoi_flow_nominal=QBoi_nominal_heaPla5ad49efc,
    mMin_flow=mMin_flow_heaPla5ad49efc,
    mBoi_flow_nominal=mBoi_flow_nominal_heaPla5ad49efc,
    dpBoi_nominal=10000,
    delT_nominal(
      displayUnit="degC")=15,
    tWai=tWai_heaPla5ad49efc,
    // TODO: we're currently grabbing dpSetPoi from the Network instance -- need feedback to determine if that's the proper "home" for it
    dpSetPoi=dpSetPoi_MyNetworkHeatedWaterStub
    )
    "District heating plant."
    annotation (Placement(transformation(extent={{-70.0,30.0},{-50.0,50.0}})));
  //
  // End Model Instance for heaPla5ad49efc
  //


  

  // Model dependencies

  //
  // Begin Component Definitions for 519a97e0
  // Source template: /model_connectors/couplings/templates/NetworkHeatedWaterStub_HeatingPlant/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression TSetDP_519a97e0(y=0.70)
    "Heated water supply temperature set point on district level."
    annotation (Placement(transformation(extent={{-70.0,-10.0},{-50.0,10.0}})));
  Modelica.Blocks.Sources.RealExpression secMasFloRat_519a97e0(y=32)
    "Secondary loop heated water flow rate."
    annotation (Placement(transformation(extent={{-30.0,-10.0},{-10.0,10.0}})));
  Modelica.Blocks.Sources.RealExpression TDisSetHeaWat_519a97e0(
    each y=273.15+68)
    "District side heating water supply temperature set point."
    annotation (Placement(transformation(extent={{10.0,-10.0},{30.0,10.0}})));
  Modelica.Blocks.Sources.BooleanConstant mPum_flow_519a97e0(
    k=true)
    "Total heating water pump mass flow rate"
    annotation (Placement(transformation(extent={{50.0,-10.0},{70.0,10.0}})));

  //
  // End Component Definitions for 519a97e0
  //



equation
  // Connections

  //
  // Begin Connect Statements for 519a97e0
  // Source template: /model_connectors/couplings/templates/NetworkHeatedWaterStub_HeatingPlant/ConnectStatements.mopt
  //

  // TODO: these connect statements shouldn't be here, they are plant specific
  // but since we can't currently make connect statements for single systems, this is what we've got
  connect(mPum_flow_519a97e0.y, heaPla5ad49efc.on)
    annotation (Line(points={{65.52360364225558,15.15664811254716},{65.52360364225558,35.15664811254716},{45.52360364225558,35.15664811254716},{25.523603642255566,35.15664811254716},{5.523603642255566,35.15664811254716},{-14.476396357744434,35.15664811254716},{-34.476396357744434,35.15664811254716},{-54.476396357744434,35.15664811254716}},color={0,0,127}));
  connect(TDisSetHeaWat_519a97e0.y, heaPla5ad49efc.THeaSet)
    annotation (Line(points={{28.787082973528953,10.742856963015655},{28.787082973528953,30.742856963015655},{8.787082973528953,30.742856963015655},{-11.212917026471047,30.742856963015655},{-31.212917026471054,30.742856963015655},{-51.212917026471054,30.742856963015655}},color={0,0,127}));

  // connect plant to sink and source
  connect(heaPla5ad49efc.port_a, supHeaWat.ports[1])
    annotation (Line(points={{-66.24302544740405,-10.298312088954503},{-86.24302544740405,-10.298312088954503},{-86.24302544740405,9.701687911045497},{-86.24302544740405,29.701687911045497},{-86.24302544740405,49.7016879110455},{-66.24302544740405,49.7016879110455}},color={0,0,127}));
  connect(heaPla5ad49efc.port_b, sinHeaWat.ports[1])
    annotation (Line(points={{-17.39104895028011,-17.987356719081745},{-37.39104895028011,-17.987356719081745},{-37.39104895028011,2.0126432809182546},{-37.39104895028011,22.012643280918255},{-37.39104895028011,42.012643280918255},{-57.39104895028011,42.012643280918255}},color={0,0,127}));

  // connect additional inputs for plant and the water source
  connect(TSetDP_519a97e0.y, heaPla5ad49efc.dpMea)
    annotation (Line(points={{-53.171167947149385,13.792805905950814},{-53.171167947149385,33.792805905950814}},color={0,0,127}));
  connect(secMasFloRat_519a97e0.y, supHeaWat.m_flow_in)
    annotation (Line(points={{-23.158779666562012,-11.144408143356515},{-43.158779666562005,-11.144408143356515},{-43.158779666562005,-31.144408143356515},{-63.158779666562005,-31.144408143356515}},color={0,0,127}));

  //
  // End Connect Statements for 519a97e0
  //




annotation(
  experiment(
    StopTime=86400,
    Interval=3600,
    Tolerance=1e-06),
  Diagram(
    coordinateSystem(
      preserveAspectRatio=false,
      extent={{-90.0,-70.0},{90.0,70.0}})),
  Documentation(
    revisions="<html>
 <li>
 May 10, 2020: Hagar Elarga<br/>
Updated implementation to handle template needed for GeoJSON to Modelica.
</li>
</html>"));
end DistrictEnergySystem;