within spawn_single.Districts;

model DistrictEnergySystem
  extends Modelica.Icons.Example;
  // District Parameters
  package MediumW = Buildings.Media.Water "Source side medium";
  package MediumA = Buildings.Media.Air "Load side medium";
  // TODO: dehardcode these
  parameter Modelica.Units.SI.TemperatureDifference delChiWatTemDis(displayUnit = "degC") = 7;
  parameter Modelica.Units.SI.TemperatureDifference delChiWatTemBui(displayUnit = "degC") = 5;
  parameter Modelica.Units.SI.TemperatureDifference delHeaWatTemDis(displayUnit = "degC") = 12;
  parameter Modelica.Units.SI.TemperatureDifference delHeaWatTemBui(displayUnit = "degC") = 5;
  // Models
  //
  // Begin Model Instance for SpawnLoad_18d44581
  // Source template: /model_connectors/load_connectors/templates/Spawn_Instance.mopt
  //
  // parameter Modelica.Units.SI.MassFlowRate mLoaCoo_flow_nominal_SpawnLoad_18d44581[SpawnLoad_18d44581.nZon]={(-1*SpawnLoad_18d44581.QCoo_flow_nominal[i]*(0.06)///1000) for i in 1:SpawnLoad_18d44581.nZon};
  //  parameter Modelica.Units.SI.MassFlowRate mLoaHea_flow_nominal_SpawnLoad_18d44581[SpawnLoad_18d44581.nZon]={(SpawnLoad_18d44581.QHea_flow_nominal[i]*(0.05)/1000) for i in 1:SpawnLoad_18d44581.nZon};
  spawn_single.Loads.B5a6b99ec37f4de7f94020090.building SpawnLoad_18d44581(allowFlowReversal = true, have_pum = true, mLoaCoo_flow_nominal = {1, 1, 1, 1, 1}, mLoaHea_flow_nominal = {1, 1, 1, 1, 1}, nPorts_aChiWat = 1, nPorts_aHeaWat = 1, nPorts_bChiWat = 1, nPorts_bHeaWat = 1) "Building spawn model" annotation(
    Placement(transformation(extent = {{50.0, 30.0}, {70.0, 50.0}})));
  //
  // End Model Instance for SpawnLoad_18d44581
  //
  //
  // Begin Model Instance for etsHotWatStub_24a30990
  // Source template: /model_connectors/energy_transfer_systems/templates/EtsHotWaterStub_Instance.mopt
  //
  // TODO: move these components into a single component
   Buildings.Fluid.Sources.Boundary_pT supHeaWat_etsHotWatStub_24a30990(redeclare package Medium = MediumW, use_T_in = true, nPorts = 1) "Heating water supply" annotation(
    Placement(transformation(extent = {{10.0, -10.0}, {30.0, 10.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinHeaWat_etsHotWatStub_24a30990(redeclare package Medium = MediumW, nPorts = 1) "Heating water sink" annotation(
    Placement(transformation(extent = {{50.0, -10.0}, {70.0, 10.0}})));
  //
  // End Model Instance for etsHotWatStub_24a30990
  //
  //
  // Begin Model Instance for etsColWatStub_7adfa0ec
  // Source template: /model_connectors/energy_transfer_systems/templates/EtsColdWaterStub_Instance.mopt
  //
  // TODO: move these components into a single component
   Buildings.Fluid.Sources.Boundary_pT supChiWat_etsColWatStub_7adfa0ec(redeclare package Medium = MediumW, use_T_in = true, nPorts = 1) "Chilled water supply" annotation(
    Placement(transformation(extent = {{-70.0, -50.0}, {-50.0, -30.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinChiWat_etsColWatStub_7adfa0ec(redeclare package Medium = MediumW, nPorts = 1) "Chilled water sink" annotation(
    Placement(transformation(extent = {{-30.0, -50.0}, {-10.0, -30.0}})));
  //
  // End Model Instance for etsColWatStub_7adfa0ec
  //
  // Model dependencies
  //
  // Begin Component Definitions for 9680e1ee
  // Source template: /model_connectors/couplings/templates/Spawn_EtsHotWaterStub/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression THeaWatSup_9680e1ee( // y=max(
 // SpawnLoad_18d44581.terUni.T_aHeaWat_nominal))
  y = 313) "Heating water supply temperature" annotation(
    Placement(transformation(extent = {{-70.0, -10.0}, {-50.0, 10.0}})));
  //
  // End Component Definitions for 9680e1ee
  //
  //
  // Begin Component Definitions for 583ebf88
  // Source template: /model_connectors/couplings/templates/Spawn_EtsColdWaterStub/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression TChiWatSup_583ebf88( //  y=min(
 //   SpawnLoad_18d44581.terUni.T_aChiWat_nominal))
  y = 280) "Chilled water supply temperature" annotation(
    Placement(transformation(extent = {{-30.0, -10.0}, {-10.0, 10.0}})));
  //
  // End Component Definitions for 583ebf88
  //
equation
// Connections
//
// Begin Connect Statements for 9680e1ee
// Source template: /model_connectors/couplings/templates/Spawn_EtsHotWaterStub/ConnectStatements.mopt
//
// spawn, ets hot water stub connections
  connect(supHeaWat_etsHotWatStub_24a30990.T_in, THeaWatSup_9680e1ee.y) annotation(
    Line(points = {{29.084032655607942, 20.532028345828124}, {9.084032655607942, 20.532028345828124}, {-10.915967344392058, 20.532028345828124}, {-30.915967344392058, 20.532028345828124}, {-30.915967344392058, 0.5320283458281239}, {-50.91596734439206, 0.5320283458281239}}, color = {0, 0, 127}));
  connect(supHeaWat_etsHotWatStub_24a30990.ports[1], SpawnLoad_18d44581.ports_aHeaWat[1]) annotation(
    Line(points = {{13.717555884323602, 21.791816422605102}, {13.717555884323602, 41.7918164226051}, {33.7175558843236, 41.7918164226051}, {53.71755588432359, 41.7918164226051}}, color = {0, 0, 127}));
  connect(sinHeaWat_etsHotWatStub_24a30990.ports[1], SpawnLoad_18d44581.ports_bHeaWat[1]) annotation(
    Line(points = {{63.51713892322243, 20.332083714025096}, {63.51713892322243, 40.332083714025096}}, color = {0, 0, 127}));
//
// End Connect Statements for 9680e1ee
//
//
// Begin Connect Statements for 583ebf88
// Source template: /model_connectors/couplings/templates/Spawn_EtsColdWaterStub/ConnectStatements.mopt
//
// spawn, ets cold water stub connections
  connect(TChiWatSup_583ebf88.y, supChiWat_etsColWatStub_7adfa0ec.T_in) annotation(
    Line(points = {{-16.33733550758234, -13.451812397077646}, {-36.33733550758233, -13.451812397077646}, {-36.33733550758233, -33.451812397077646}, {-56.33733550758233, -33.451812397077646}}, color = {0, 0, 127}));
  connect(SpawnLoad_18d44581.ports_bChiWat[1], sinChiWat_etsColWatStub_7adfa0ec.ports[1]) annotation(
    Line(points = {{52.764367689120235, 15.188793538024598}, {32.764367689120235, 15.188793538024598}, {32.764367689120235, -4.811206461975402}, {32.764367689120235, -24.811206461975402}, {32.764367689120235, -44.8112064619754}, {12.764367689120235, -44.8112064619754}, {-7.235632310879765, -44.8112064619754}, {-27.235632310879765, -44.8112064619754}}, color = {0, 0, 127}));
  connect(supChiWat_etsColWatStub_7adfa0ec.ports[1], SpawnLoad_18d44581.ports_aChiWat[1]) annotation(
    Line(points = {{-60.61378220518616, -19.445260392176138}, {-40.61378220518616, -19.445260392176138}, {-40.61378220518616, 0.554739607823862}, {-40.61378220518616, 20.554739607823862}, {-40.61378220518616, 40.55473960782386}, {-20.61378220518617, 40.55473960782386}, {-0.613782205186169, 40.55473960782386}, {19.38621779481383, 40.55473960782386}, {39.38621779481383, 40.55473960782386}, {59.38621779481383, 40.55473960782386}}, color = {0, 0, 127}));
//
// End Connect Statements for 583ebf88
//
  annotation(
    experiment(StopTime = 86400, Interval = 3600, Tolerance = 1e-06),
    Diagram(coordinateSystem(preserveAspectRatio = false, extent = {{-90.0, -70.0}, {90.0, 70.0}})),
    Documentation(revisions = "<html>
 <li>
 May 10, 2020: Hagar Elarga<br/>
Updated implementation to handle template needed for GeoJSON to Modelica.
</li>
</html>"));
end DistrictEnergySystem;
