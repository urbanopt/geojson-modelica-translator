within spawn_single.Districts;
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
  // Begin Model Instance for SpawnLoad_416f556c
  // Source template: /model_connectors/load_connectors/templates/Spawn_Instance.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mLoaCoo_flow_nominal_SpawnLoad_416f556c[SpawnLoad_416f556c.nZon]={(-1*SpawnLoad_416f556c.QCoo_flow_nominal[i]*(0.06)/1000) for i in 1:SpawnLoad_416f556c.nZon};
  parameter Modelica.Units.SI.MassFlowRate mLoaHea_flow_nominal_SpawnLoad_416f556c[SpawnLoad_416f556c.nZon]={(SpawnLoad_416f556c.QHea_flow_nominal[i]*(0.05)/1000) for i in 1:SpawnLoad_416f556c.nZon};
  spawn_single.Loads.B5a6b99ec37f4de7f94020090.building SpawnLoad_416f556c(
    allowFlowReversal = true,
    mLoaCoo_flow_nominal=mLoaCoo_flow_nominal_SpawnLoad_416f556c,
    mLoaHea_flow_nominal=mLoaHea_flow_nominal_SpawnLoad_416f556c,
    nPorts_aHeaWat=1,
    nPorts_bHeaWat=1,
    nPorts_aChiWat=1,
    nPorts_bChiWat=1,
    have_pum=true)
    "Building spawn model"
    annotation (Placement(transformation(extent={{50.0,30.0},{70.0,50.0}})));
  //
  // End Model Instance for SpawnLoad_416f556c
  //


  
  //
  // Begin Model Instance for etsHotWatStub_bce3ec86
  // Source template: /model_connectors/energy_transfer_systems/templates/EtsHotWaterStub_Instance.mopt
  //
  // TODO: move these components into a single component
  Buildings.Fluid.Sources.Boundary_pT supHeaWat_etsHotWatStub_bce3ec86(
    redeclare package Medium=MediumW,
    use_T_in=true,
    nPorts=1)
    "Heating water supply"
    annotation (Placement(transformation(extent={{10.0,-10.0},{30.0,10.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinHeaWat_etsHotWatStub_bce3ec86(
    redeclare package Medium=MediumW,
    nPorts=1)
    "Heating water sink"
    annotation (Placement(transformation(extent={{50.0,-10.0},{70.0,10.0}})));
  //
  // End Model Instance for etsHotWatStub_bce3ec86
  //


  
  //
  // Begin Model Instance for etsColWatStub_1e23eac0
  // Source template: /model_connectors/energy_transfer_systems/templates/EtsColdWaterStub_Instance.mopt
  //
  // TODO: move these components into a single component
  Buildings.Fluid.Sources.Boundary_pT supChiWat_etsColWatStub_1e23eac0(
    redeclare package Medium=MediumW,
    use_T_in=true,
    nPorts=1)
    "Chilled water supply"
    annotation (Placement(transformation(extent={{-70.0,-50.0},{-50.0,-30.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinChiWat_etsColWatStub_1e23eac0(
    redeclare package Medium=MediumW,
    nPorts=1)
    "Chilled water sink"
    annotation (Placement(transformation(extent={{-30.0,-50.0},{-10.0,-30.0}})));
  //
  // End Model Instance for etsColWatStub_1e23eac0
  //


  

  // Model dependencies

  //
  // Begin Component Definitions for 7a1153a1
  // Source template: /model_connectors/couplings/templates/Spawn_EtsHotWaterStub/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression THeaWatSup_7a1153a1(
    y=max(
      SpawnLoad_416f556c.terUni.T_aHeaWat_nominal))
    "Heating water supply temperature"
    annotation (Placement(transformation(extent={{-70.0,-10.0},{-50.0,10.0}})));

  //
  // End Component Definitions for 7a1153a1
  //



  //
  // Begin Component Definitions for d7cce571
  // Source template: /model_connectors/couplings/templates/Spawn_EtsColdWaterStub/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression TChiWatSup_d7cce571(
    y=min(
      SpawnLoad_416f556c.terUni.T_aChiWat_nominal))
    "Chilled water supply temperature"
    annotation (Placement(transformation(extent={{-30.0,-10.0},{-10.0,10.0}})));

  //
  // End Component Definitions for d7cce571
  //



equation
  // Connections

  //
  // Begin Connect Statements for 7a1153a1
  // Source template: /model_connectors/couplings/templates/Spawn_EtsHotWaterStub/ConnectStatements.mopt
  //

  // spawn, ets hot water stub connections
  connect(supHeaWat_etsHotWatStub_bce3ec86.T_in,THeaWatSup_7a1153a1.y)
    annotation (Line(points={{16.01379381964557,25.791504430785523},{-3.9862061803544293,25.791504430785523},{-23.98620618035443,25.791504430785523},{-43.98620618035442,25.791504430785523},{-43.98620618035442,5.791504430785523},{-63.98620618035442,5.791504430785523}},color={0,0,127}));
  connect(supHeaWat_etsHotWatStub_bce3ec86.ports[1],SpawnLoad_416f556c.ports_aHeaWat[1])
    annotation (Line(points={{19.593891870204047,19.52300284157201},{19.593891870204047,39.52300284157201},{39.59389187020403,39.52300284157201},{59.59389187020403,39.52300284157201}},color={0,0,127}));
  connect(sinHeaWat_etsHotWatStub_bce3ec86.ports[1],SpawnLoad_416f556c.ports_bHeaWat[1])
    annotation (Line(points={{58.30627202952704,21.473734341471285},{58.30627202952704,41.473734341471285}},color={0,0,127}));

  //
  // End Connect Statements for 7a1153a1
  //



  //
  // Begin Connect Statements for d7cce571
  // Source template: /model_connectors/couplings/templates/Spawn_EtsColdWaterStub/ConnectStatements.mopt
  //

  // spawn, ets cold water stub connections
  connect(TChiWatSup_d7cce571.y,supChiWat_etsColWatStub_1e23eac0.T_in)
    annotation (Line(points={{-17.21513376276343,-11.22233027666212},{-37.21513376276342,-11.22233027666212},{-37.21513376276342,-31.22233027666212},{-57.21513376276342,-31.22233027666212}},color={0,0,127}));
  connect(SpawnLoad_416f556c.ports_bChiWat[1],sinChiWat_etsColWatStub_1e23eac0.ports[1])
    annotation (Line(points={{69.18934208003924,27.217235843105158},{49.18934208003924,27.217235843105158},{49.18934208003924,7.217235843105158},{49.18934208003924,-12.782764156894842},{49.18934208003924,-32.78276415689484},{29.18934208003924,-32.78276415689484},{9.18934208003924,-32.78276415689484},{-10.81065791996076,-32.78276415689484}},color={0,0,127}));
  connect(supChiWat_etsColWatStub_1e23eac0.ports[1],SpawnLoad_416f556c.ports_aChiWat[1])
    annotation (Line(points={{-55.43187738516657,-19.421961021917298},{-35.43187738516657,-19.421961021917298},{-35.43187738516657,0.5780389780827022},{-35.43187738516657,20.57803897808271},{-35.43187738516657,40.57803897808271},{-15.431877385166572,40.57803897808271},{4.5681226148334275,40.57803897808271},{24.568122614833428,40.57803897808271},{44.56812261483341,40.57803897808271},{64.56812261483341,40.57803897808271}},color={0,0,127}));

  //
  // End Connect Statements for d7cce571
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