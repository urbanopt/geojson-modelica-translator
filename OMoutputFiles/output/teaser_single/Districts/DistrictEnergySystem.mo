within teaser_single.Districts;

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
  // Begin Model Instance for TeaserLoad_195144c2
  // Source template: /model_connectors/load_connectors/templates/Teaser_Instance.mopt
  //
  teaser_single.Loads.B5a6b99ec37f4de7f94020090.building TeaserLoad_195144c2(allowFlowReversal = true, nPorts_aChiWat = 1, nPorts_aHeaWat = 1, nPorts_bChiWat = 1, nPorts_bHeaWat = 1) "Building with thermal loads as TEASER zones" annotation(
    Placement(transformation(extent = {{50.0, 30.0}, {70.0, 50.0}})));
  //
  // End Model Instance for TeaserLoad_195144c2
  //
  //
  // Begin Model Instance for etsHotWatStub_9c85a049
  // Source template: /model_connectors/energy_transfer_systems/templates/EtsHotWaterStub_Instance.mopt
  //
  // TODO: move these components into a single component
  Buildings.Fluid.Sources.Boundary_pT supHeaWat_etsHotWatStub_9c85a049(redeclare package Medium = MediumW, use_T_in = true, nPorts = 1) "Heating water supply" annotation(
    Placement(transformation(extent = {{10.0, -10.0}, {30.0, 10.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinHeaWat_etsHotWatStub_9c85a049(redeclare package Medium = MediumW, nPorts = 1) "Heating water sink" annotation(
    Placement(transformation(extent = {{50.0, -10.0}, {70.0, 10.0}})));
  //
  // End Model Instance for etsHotWatStub_9c85a049
  //
  //
  // Begin Model Instance for etsColWatStub_9bf053d8
  // Source template: /model_connectors/energy_transfer_systems/templates/EtsColdWaterStub_Instance.mopt
  //
  // TODO: move these components into a single component
  Buildings.Fluid.Sources.Boundary_pT supChiWat_etsColWatStub_9bf053d8(redeclare package Medium = MediumW, use_T_in = true, nPorts = 1) "Chilled water supply" annotation(
    Placement(transformation(extent = {{-70.0, -50.0}, {-50.0, -30.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinChiWat_etsColWatStub_9bf053d8(redeclare package Medium = MediumW, nPorts = 1) "Chilled water sink" annotation(
    Placement(transformation(extent = {{-30.0, -50.0}, {-10.0, -30.0}})));
  //
  // End Model Instance for etsColWatStub_9bf053d8
  //
  // Model dependencies
  //
  // Begin Component Definitions for 13ef57c2
  // Source template: /model_connectors/couplings/templates/Teaser_EtsHotWaterStub/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression THeaWatSup_13ef57c2(y = max(TeaserLoad_195144c2.terUni.T_aHeaWat_nominal)) "Heating water supply temperature" annotation(
    Placement(transformation(extent = {{-70.0, -10.0}, {-50.0, 10.0}})));
  //
  // End Component Definitions for 13ef57c2
  //
  //
  // Begin Component Definitions for 5d22f2a4
  // Source template: /model_connectors/couplings/templates/Teaser_EtsColdWaterStub/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression TChiWatSup_5d22f2a4(y = min(TeaserLoad_195144c2.terUni.T_aChiWat_nominal)) "Chilled water supply temperature" annotation(
    Placement(transformation(extent = {{-30.0, -10.0}, {-10.0, 10.0}})));
  //
  // End Component Definitions for 5d22f2a4
  //
equation
// Connections
//
// Begin Connect Statements for 13ef57c2
// Source template: /model_connectors/couplings/templates/Teaser_EtsHotWaterStub/ConnectStatements.mopt
//
// teaser, ets hot water stub connections
  connect(supHeaWat_etsHotWatStub_9c85a049.T_in, THeaWatSup_13ef57c2.y) annotation(
    Line(points = {{18.24651985543052, 11.736770937126124}, {-1.7534801445694796, 11.736770937126124}, {-21.75348014456948, 11.736770937126124}, {-41.75348014456948, 11.736770937126124}, {-41.75348014456948, -8.263229062873876}, {-61.75348014456948, -8.263229062873876}}, color = {0, 0, 127}));
  connect(supHeaWat_etsHotWatStub_9c85a049.ports[1], TeaserLoad_195144c2.ports_aHeaWat[1]) annotation(
    Line(points = {{10.950070894629562, 16.323049145759214}, {10.950070894629562, 36.323049145759214}, {30.95007089462956, 36.323049145759214}, {50.95007089462956, 36.323049145759214}}, color = {0, 0, 127}));
  connect(sinHeaWat_etsHotWatStub_9c85a049.ports[1], TeaserLoad_195144c2.ports_bHeaWat[1]) annotation(
    Line(points = {{59.86870045787779, 24.469537352721744}, {59.86870045787779, 44.469537352721744}}, color = {0, 0, 127}));
//
// End Connect Statements for 13ef57c2
//
//
// Begin Connect Statements for 5d22f2a4
// Source template: /model_connectors/couplings/templates/Teaser_EtsColdWaterStub/ConnectStatements.mopt
//
// teaser, ets cold water stub connections
  connect(TChiWatSup_5d22f2a4.y, supChiWat_etsColWatStub_9bf053d8.T_in) annotation(
    Line(points = {{-18.212513627736996, -21.74106437158764}, {-38.21251362773699, -21.74106437158764}, {-38.21251362773699, -41.74106437158764}, {-58.21251362773699, -41.74106437158764}}, color = {0, 0, 127}));
  connect(supChiWat_etsColWatStub_9bf053d8.ports[1], TeaserLoad_195144c2.ports_aChiWat[1]) annotation(
    Line(points = {{-62.707122717826664, -17.858548760363036}, {-42.707122717826664, -17.858548760363036}, {-42.707122717826664, 2.1414512396369645}, {-42.707122717826664, 22.141451239636957}, {-42.707122717826664, 42.141451239636964}, {-22.707122717826664, 42.141451239636964}, {-2.707122717826664, 42.141451239636964}, {17.292877282173336, 42.141451239636964}, {37.292877282173336, 42.141451239636964}, {57.29287728217332, 42.141451239636964}}, color = {0, 0, 127}));
  connect(sinChiWat_etsColWatStub_9bf053d8.ports[1], TeaserLoad_195144c2.ports_bChiWat[1]) annotation(
    Line(points = {{-20.676930603789003, -20.055411839467325}, {-0.6769306037890033, -20.055411839467325}, {-0.6769306037890033, -0.05541183946732531}, {-0.6769306037890033, 19.944588160532675}, {-0.6769306037890033, 39.944588160532675}, {19.323069396210997, 39.944588160532675}, {39.323069396211, 39.944588160532675}, {59.323069396211, 39.944588160532675}}, color = {0, 0, 127}));
//
// End Connect Statements for 5d22f2a4
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