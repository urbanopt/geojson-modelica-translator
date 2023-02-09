within chilled_water_plant_stub.Districts;
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
  // Begin Model Instance for MyNetworkChilledWaterStub
  // Source template: /model_connectors/networks/templates/NetworkChilledWaterStub_Instance.mopt
  //
  // chilled water stub
  // TODO: move these components into a single component
  Buildings.Fluid.Sources.MassFlowSource_T supChiWat(
    redeclare package Medium=MediumW,
    use_m_flow_in=true,
    use_T_in=false,
    T=6+273.15,
    nPorts=1)
    "Chilled water supply (district side)."
    annotation (Placement(transformation(extent={{10.0,-10.0},{30.0,10.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinChiWat1(
    redeclare package Medium=MediumW,
    nPorts=1)
    "Chilled water sink (district side)"
    annotation (Placement(transformation(extent={{50.0,-10.0},{70.0,10.0}})));
  //
  // End Model Instance for MyNetworkChilledWaterStub
  //


  
  //
  // Begin Model Instance for cooPla_8def2263
  // Source template: /model_connectors/plants/templates/CoolingPlant_Instance.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mCHW_flow_nominal_cooPla_8def2263=cooPla_8def2263.numChi*(cooPla_8def2263.perChi.mEva_flow_nominal)
    "Nominal chilled water mass flow rate";
  parameter Modelica.Units.SI.MassFlowRate mCW_flow_nominal_cooPla_8def2263=cooPla_8def2263.perChi.mCon_flow_nominal
    "Nominal condenser water mass flow rate";
  parameter Modelica.Units.SI.PressureDifference dpCHW_nominal_cooPla_8def2263=44.8*1000
    "Nominal chilled water side pressure";
  parameter Modelica.Units.SI.PressureDifference dpCW_nominal_cooPla_8def2263=46.2*1000
    "Nominal condenser water side pressure";
  parameter Modelica.Units.SI.Power QEva_nominal_cooPla_8def2263=mCHW_flow_nominal_cooPla_8def2263*4200*(5-14)
    "Nominal cooling capaciaty (Negative means cooling)";
  parameter Modelica.Units.SI.MassFlowRate mMin_flow_cooPla_8def2263=0.2*mCHW_flow_nominal_cooPla_8def2263/cooPla_8def2263.numChi
    "Minimum mass flow rate of single chiller";
  // control settings
  parameter Modelica.Units.SI.Pressure dpSetPoi_cooPla_8def2263=70000
    "Differential pressure setpoint";
  parameter Modelica.Units.SI.Pressure pumDP_cooPla_8def2263=dpCHW_nominal_cooPla_8def2263+dpSetPoi_cooPla_8def2263+200000;
  parameter Modelica.Units.SI.Time tWai_cooPla_8def2263=30
    "Waiting time";
  // pumps
  parameter Buildings.Fluid.Movers.Data.Generic perCHWPum_cooPla_8def2263(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=((mCHW_flow_nominal_cooPla_8def2263/cooPla_8def2263.numChi)/1000)*{0.1,1,1.2},
      dp=pumDP_cooPla_8def2263*{1.2,1,0.1}))
    "Performance data for chilled water pumps";
  parameter Buildings.Fluid.Movers.Data.Generic perCWPum_cooPla_8def2263(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=mCW_flow_nominal_cooPla_8def2263/1000*{0.2,0.6,1.0,1.2},
      dp=(dpCW_nominal_cooPla_8def2263+60000+6000)*{1.2,1.1,1.0,0.6}))
    "Performance data for condenser water pumps";


  Modelica.Blocks.Sources.RealExpression TSetChiWatDis_cooPla_8def2263(
    y=5+273.15)
    "Chilled water supply temperature set point on district level."
    annotation (Placement(transformation(extent={{-70.0,-50.0},{-50.0,-30.0}})));
  Modelica.Blocks.Sources.BooleanConstant on_cooPla_8def2263
    "On signal of the plant"
    annotation (Placement(transformation(extent={{-30.0,-50.0},{-10.0,-30.0}})));

  chilled_water_plant_stub.Plants.CentralCoolingPlant cooPla_8def2263(
    redeclare Buildings.Fluid.Chillers.Data.ElectricEIR.ElectricEIRChiller_Carrier_19EX_5208kW_6_88COP_Vanes perChi,
    perCHWPum=perCHWPum_cooPla_8def2263,
    perCWPum=perCWPum_cooPla_8def2263,
    mCHW_flow_nominal=mCHW_flow_nominal_cooPla_8def2263,
    dpCHW_nominal=dpCHW_nominal_cooPla_8def2263,
    QEva_nominal=QEva_nominal_cooPla_8def2263,
    mMin_flow=mMin_flow_cooPla_8def2263,
    mCW_flow_nominal=mCW_flow_nominal_cooPla_8def2263,
    dpCW_nominal=dpCW_nominal_cooPla_8def2263,
    TAirInWB_nominal=298.7,
    TCW_nominal=308.15,
    TMin=288.15,
    tWai=tWai_cooPla_8def2263,
    dpSetPoi=dpSetPoi_cooPla_8def2263
    )
    "District cooling plant."
    annotation (Placement(transformation(extent={{-70.0,30.0},{-50.0,50.0}})));
  //
  // End Model Instance for cooPla_8def2263
  //


  

  // Model dependencies

  //
  // Begin Component Definitions for 2c993886
  // Source template: /model_connectors/couplings/templates/NetworkChilledWaterStub_CoolingPlant/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression TSetDP_2c993886(y=0.70)
    "Chilled water supply temperature set point on district level."
    annotation (Placement(transformation(extent={{-70.0,-10.0},{-50.0,10.0}})));
  Modelica.Blocks.Sources.RealExpression secMasFloRat_2c993886(y=32)
    "Secondary loop chilled water flow rate."
    annotation (Placement(transformation(extent={{-30.0,-10.0},{-10.0,10.0}})));

  //
  // End Component Definitions for 2c993886
  //



equation
  // Connections

  //
  // Begin Connect Statements for 2c993886
  // Source template: /model_connectors/couplings/templates/NetworkChilledWaterStub_CoolingPlant/ConnectStatements.mopt
  //

  // TODO: these connect statements shouldn't be here, they are plant specific
  // but since we can't currently make connect statements for single systems, this is what we've got
  connect(on_cooPla_8def2263.y,cooPla_8def2263.on)
    annotation (Line(points={{-16.781743696344392,-29.156305456117224},{-36.78174369634439,-29.156305456117224},{-36.78174369634439,-9.156305456117224},{-36.78174369634439,10.843694543882776},{-36.78174369634439,30.843694543882776},{-56.78174369634439,30.843694543882776}},color={0,0,127}));
  connect(TSetChiWatDis_cooPla_8def2263.y,cooPla_8def2263.TCHWSupSet)
    annotation (Line(points={{-62.329375702429374,-15.113331954035104},{-82.32937570242937,-15.113331954035104},{-82.32937570242937,4.886668045964896},{-82.32937570242937,24.886668045964896},{-82.32937570242937,44.886668045964896},{-62.329375702429374,44.886668045964896}},color={0,0,127}));

  // connect plant to sink and source
  connect(supChiWat.ports[1], cooPla_8def2263.port_a)
    annotation (Placement(Line(points={{23.999475791230566,20.76697456375595},{23.999475791230566,40.76697456375595},{3.999475791230566,40.76697456375595},{-16.000524208769434,40.76697456375595},{-36.000524208769434,40.76697456375595},{-56.000524208769434,40.76697456375595}},color={0,0,127})));
  connect(sinChiWat1.ports[1], cooPla_8def2263.port_b)
    annotation (Placement(Line(points={{51.71140147423566,17.91035748564446},{51.71140147423566,37.91035748564446},{31.711401474235657,37.91035748564446},{11.711401474235657,37.91035748564446},{-8.288598525764343,37.91035748564446},{-28.288598525764343,37.91035748564446},{-48.28859852576434,37.91035748564446},{-68.28859852576434,37.91035748564446}},color={0,0,127})));

  // connect additional inputs for plant and the water source
  connect(TSetDP_2c993886.y, cooPla_8def2263.dpMea)
    annotation (Placement(Line(points={{-65.07949703596456,17.254004966968367},{-65.07949703596456,37.25400496696837}},color={0,0,127})));
  connect(secMasFloRat_2c993886.y, supChiWat.m_flow_in)
    annotation (Placement(Line(points={{1.1017178200213351,5.948215188305838},{21.101717820021335,5.948215188305838}},color={0,0,127})));

  //
  // End Connect Statements for 2c993886
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