within time_series_5g.Districts;
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
  inner parameter Buildings.Experimental.DHC.Examples.Combined.BaseClasses.DesignDataSeries datDes(
    nBui=1,
    mPumDis_flow_nominal=95,
    mPipDis_flow_nominal=95,
    dp_length_nominal=250,
    epsPla=0.935,
    final mCon_flow_nominal={18})
    "Design data";
  // Models

  //
  // Begin Model Instance for TimeSerLoa_eff53284
  // Source template: /model_connectors/load_connectors/templates/TimeSeries_Instance.mopt
  //
    // time series load
  time_series_5g.Loads.B5a6b99ec37f4de7f94020090.building TimeSerLoa_eff53284(

    allowFlowReversalBui = true,
    allowFlowReversalSer = true,
    bui(T_aHeaWat_nominal(displayUnit="K")=318.15,
    T_aChiWat_nominal(displayUnit="K")=291.15,
    delTAirCoo(displayUnit="degC")=10,
    delTAirHea(displayUnit="degC")=20,
    k=0.1,
    Ti=120
    ), ets(have_hotWat = false)

    )
    "Building model integrating multiple time series thermal zones."
    annotation (Placement(transformation(extent={{50.0,30.0},{70.0,50.0}})));
  //
  // End Model Instance for TimeSerLoa_eff53284
  //

  //
  // Begin Model Instance for MyNetworkAmbientWaterStub
  // Source template: /model_connectors/networks/templates/NetworkAmbientWaterStub_Instance.mopt
  //
    // heated water stub
  // TODO: move these components into a single component
  Buildings.Fluid.Sources.MassFlowSource_T supHeaWat(
    redeclare package Medium=MediumW,
    use_m_flow_in=true,
    use_T_in=false,
    T=7+273.15,
    nPorts=1)
    "Heating water supply temperature (district side)."
    annotation (Placement(transformation(extent={{-70.0,-50.0},{-50.0,-30.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinHeaWat(
    redeclare package Medium=MediumW,
    nPorts=1)
    "Heating water sink (district side)"
    annotation (Placement(transformation(extent={{-30.0,-50.0},{-10.0,-30.0}})));

  // NOTE: this differential pressure setpoint is currently utilized by plants elsewhere
  parameter Modelica.Units.SI.Pressure dpSetPoi_MyNetworkAmbientWaterStub=50000
    "Differential pressure setpoint";
  //
  // End Model Instance for MyNetworkAmbientWaterStub
  //
   // Model dependencies

  //
  // Begin Component Definitions for fba60755
  // Source template: /model_connectors/couplings/5G_templates/TimeSeries_NetworkAmbientWaterStub/ComponentDefinitions.mopt
  //
    // TimeSeries 5G Component Definitions
  // TODO: the components below need to be fixed!
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_fba60755=TimeSerLoa_eff53284.bui.mHeaWat_flow_nominal*delHeaWatTemBui/delHeaWatTemDis
    "Nominal mass flow rate of primary (district) district heating side";
  parameter Modelica.Units.SI.MassFlowRate mBui_flow_nominal_fba60755=TimeSerLoa_eff53284.bui.mHeaWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district heating side";
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_fba60755=(TimeSerLoa_eff53284.bui.QHea_flow_nominal);
  // Modelica.Fluid.Sources.FixedBoundary pressure_source_fba60755(
  //   redeclare package Medium=MediumW,
  //   use_T=false,
  //   nPorts=1)
  //   "Pressure source"
  //   annotation (Placement(transformation(extent={{-70.0,-10.0},{-50.0,10.0}})));
    Modelica.Blocks.Sources.RealExpression secMasFloRat_fba60755(
    // TODO: avoid reaching into other coupling!
    // Removed the unexplained *5/7.5, and added a multiplier of 15, to have a flow rate closer to the datDes nominal value
    y=15*mDis_flow_nominal_fba60755)
    "Secondary loop conditioned water flow rate."
    annotation (Placement(transformation(extent={{-30.0,-10.0},{-10.0,10.0}})));
    // TODO: move THeaWatSet (and its connection) into a specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression THeaWatSet_fba60755(
    y=273.15+25)
    "Secondary loop (Building side) heating setpoint temperature."
    annotation (Placement(transformation(extent={{10.0,-10.0},{30.0,10.0}})));
  Modelica.Blocks.Sources.RealExpression TCooWatSet_fba60755(
    y=273.15+15)
    "Secondary loop (Building side) cooling setpoint temperature."
    annotation (Placement(transformation(extent={{50.0,-10.0},{70.0,10.0}})));
  //
// End Component Definitions for fba60755
//
 equation
// Connections

//
// Begin Connect Statements for fba60755
// Source template: /model_connectors/couplings/5G_templates/TimeSeries_NetworkAmbientWaterStub/ConnectStatements.mopt
//
// 5G ambient, timeseries coupling connections
connect(TimeSerLoa_eff53284.THeaWatSupMinSet, THeaWatSet_fba60755.y)
  annotation (Line(points={{68.45797348187395,16.21616082152643},{48.45797348187395,16.21616082152643},{48.45797348187395,-3.7838391784735705},{28.457973481873964,-3.7838391784735705}},color={0,0,127}));
connect(TimeSerLoa_eff53284.THeaWatSupMaxSet, THeaWatSet_fba60755.y)
  annotation (Line(points={{65.93186015442782,22.77437366174236},{45.931860154427824,22.77437366174236},{45.931860154427824,2.7743736617423593},{25.931860154427838,2.7743736617423593}},color={0,0,127}));
connect(TimeSerLoa_eff53284.THotWatSupSet, THeaWatSet_fba60755.y)
  annotation (Line(points={{57.11416819178936,25.404090374233085},{37.11416819178935,25.404090374233085},{37.11416819178935,5.404090374233093},{17.114168191789346,5.404090374233093}},color={0,0,127}));
connect(TimeSerLoa_eff53284.TChiWatSupSet, THeaWatSet_fba60755.y)
  annotation (Line(points={{63.33698041999918,28.433218031756816},{43.33698041999918,28.433218031756816},{43.33698041999918,8.433218031756816},{23.33698041999918,8.433218031756816}},color={0,0,127}));
connect(TCooWatSet_fba60755.y, TimeSerLoa_eff53284.TColWat)
  annotation (Line(points={{60.07582443870473,18.685889850105845},{60.07582443870473,38.685889850105845}},color={0,0,127}));
connect(secMasFloRat_fba60755.y, supHeaWat.m_flow_in)
  annotation (Line(points={{-24.442516335805934,-16.473154906820398},{-44.442516335805934,-16.473154906820398},{-44.442516335805934,-36.4731549068204},{-64.44251633580593,-36.4731549068204}},color={0,0,127}));
connect(supHeaWat.ports[1], TimeSerLoa_eff53284.port_aSerAmb)
  annotation (Line(points={{-69.39177407903244,-28.464554328979446},{-49.391774079032444,-28.464554328979446},{-49.391774079032444,-8.464554328979446},{-49.391774079032444,11.535445671020554},{-49.391774079032444,31.535445671020554},{-29.391774079032444,31.535445671020554},{-9.391774079032444,31.535445671020554},{10.608225920967556,31.535445671020554},{30.608225920967556,31.535445671020554},{50.608225920967556,31.535445671020554}},color={0,0,127}));
connect(TimeSerLoa_eff53284.port_bSerAmb, sinHeaWat.ports[1])
  annotation (Line(points={{64.85983797978477,16.968090999808624},{44.85983797978477,16.968090999808624},{44.85983797978477,-3.0319090001913764},{44.85983797978477,-23.031909000191376},{44.85983797978477,-43.031909000191376},{24.85983797978477,-43.031909000191376},{4.859837979784771,-43.031909000191376},{-15.140162020215229,-43.031909000191376}},color={0,0,127}));
//
// End Connect Statements for fba60755
//
 annotation (
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
