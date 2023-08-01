within teaser_single.Districts;
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
  parameter Integer numberofchillers = 2;

  // Models

  //
  // Begin Model Instance for TeaserLoad_a7367f54
  // Source template: /model_connectors/load_connectors/templates/Teaser_Instance.mopt
  //
  teaser_single.Loads.B5a6b99ec37f4de7f94020090.building TeaserLoad_a7367f54(
    nPorts_aHeaWat=1,
    nPorts_bHeaWat=1,
    nPorts_aChiWat=1,
    nPorts_bChiWat=1)
    "Building with thermal loads as TEASER zones"
    annotation (Placement(transformation(extent={{50.0,30.0},{70.0,50.0}})));
  //
  // End Model Instance for TeaserLoad_a7367f54
  //


  
  //
  // Begin Model Instance for etsHotWatStub_291011a6
  // Source template: /model_connectors/energy_transfer_systems/templates/EtsHotWaterStub_Instance.mopt
  //
  // TODO: move these components into a single component
  Buildings.Fluid.Sources.Boundary_pT supHeaWat_etsHotWatStub_291011a6(
    redeclare package Medium=MediumW,
    use_T_in=true,
    nPorts=1)
    "Heating water supply"
    annotation (Placement(transformation(extent={{10.0,-10.0},{30.0,10.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinHeaWat_etsHotWatStub_291011a6(
    redeclare package Medium=MediumW,
    nPorts=1)
    "Heating water sink"
    annotation (Placement(transformation(extent={{50.0,-10.0},{70.0,10.0}})));
  //
  // End Model Instance for etsHotWatStub_291011a6
  //


  
  //
  // Begin Model Instance for etsColWatStub_1ceedc83
  // Source template: /model_connectors/energy_transfer_systems/templates/EtsColdWaterStub_Instance.mopt
  //
  // TODO: move these components into a single component
  Buildings.Fluid.Sources.Boundary_pT supChiWat_etsColWatStub_1ceedc83(
    redeclare package Medium=MediumW,
    use_T_in=true,
    nPorts=1)
    "Chilled water supply"
    annotation (Placement(transformation(extent={{-70.0,-50.0},{-50.0,-30.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinChiWat_etsColWatStub_1ceedc83(
    redeclare package Medium=MediumW,
    nPorts=1)
    "Chilled water sink"
    annotation (Placement(transformation(extent={{-30.0,-50.0},{-10.0,-30.0}})));
  //
  // End Model Instance for etsColWatStub_1ceedc83
  //


  

  // Model dependencies

  //
  // Begin Component Definitions for e06d041c
  // Source template: /model_connectors/couplings/templates/Teaser_EtsHotWaterStub/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression THeaWatSup_e06d041c(
    y=max(
      TeaserLoad_a7367f54.terUni.T_aHeaWat_nominal))
    "Heating water supply temperature"
    annotation (Placement(transformation(extent={{-70.0,-10.0},{-50.0,10.0}})));

  //
  // End Component Definitions for e06d041c
  //



  //
  // Begin Component Definitions for def91e8a
  // Source template: /model_connectors/couplings/templates/Teaser_EtsColdWaterStub/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression TChiWatSup_def91e8a(
    y=min(
      TeaserLoad_a7367f54.terUni.T_aChiWat_nominal))
    "Chilled water supply temperature"
    annotation (Placement(transformation(extent={{-30.0,-10.0},{-10.0,10.0}})));

  //
  // End Component Definitions for def91e8a
  //



equation
  // Connections

  //
  // Begin Connect Statements for e06d041c
  // Source template: /model_connectors/couplings/templates/Teaser_EtsHotWaterStub/ConnectStatements.mopt
  //

  // teaser, ets hot water stub connections
  connect(supHeaWat_etsHotWatStub_291011a6.T_in,THeaWatSup_e06d041c.y)
    annotation (Line(points={{16.51412905202521,15.730644727024732},{-3.4858709479747887,15.730644727024732},{-23.48587094797479,15.730644727024732},{-43.485870947974796,15.730644727024732},{-43.485870947974796,-4.269355272975261},{-63.485870947974796,-4.269355272975261}},color={0,0,127}));
  connect(supHeaWat_etsHotWatStub_291011a6.ports[1],TeaserLoad_a7367f54.ports_aHeaWat[1])
    annotation (Line(points={{12.103112659417889,18.148046452394176},{12.103112659417889,38.148046452394176},{32.10311265941789,38.148046452394176},{52.10311265941789,38.148046452394176}},color={0,0,127}));
  connect(sinHeaWat_etsHotWatStub_291011a6.ports[1],TeaserLoad_a7367f54.ports_bHeaWat[1])
    annotation (Line(points={{63.97587616538382,26.84309943566091},{63.97587616538382,46.84309943566091}},color={0,0,127}));

  //
  // End Connect Statements for e06d041c
  //



  //
  // Begin Connect Statements for def91e8a
  // Source template: /model_connectors/couplings/templates/Teaser_EtsColdWaterStub/ConnectStatements.mopt
  //

  // teaser, ets cold water stub connections
  connect(TChiWatSup_def91e8a.y,supChiWat_etsColWatStub_1ceedc83.T_in)
    annotation (Line(points={{-25.320019163473077,-24.41706534698993},{-45.32001916347308,-24.41706534698993},{-45.32001916347308,-44.41706534698993},{-65.32001916347308,-44.41706534698993}},color={0,0,127}));
  connect(supChiWat_etsColWatStub_1ceedc83.ports[1],TeaserLoad_a7367f54.ports_aChiWat[1])
    annotation (Line(points={{-61.001451444205685,-21.345053399689107},{-41.001451444205685,-21.345053399689107},{-41.001451444205685,-1.3450533996891068},{-41.001451444205685,18.654946600310893},{-41.001451444205685,38.65494660031089},{-21.001451444205685,38.65494660031089},{-1.001451444205685,38.65494660031089},{18.998548555794315,38.65494660031089},{38.998548555794315,38.65494660031089},{58.998548555794315,38.65494660031089}},color={0,0,127}));
  connect(sinChiWat_etsColWatStub_1ceedc83.ports[1],TeaserLoad_a7367f54.ports_bChiWat[1])
    annotation (Line(points={{-19.736642173317506,-10.599042736154587},{0.2633578266824941,-10.599042736154587},{0.2633578266824941,9.40095726384542},{0.2633578266824941,29.40095726384542},{0.2633578266824941,49.40095726384542},{20.263357826682494,49.40095726384542},{40.263357826682494,49.40095726384542},{60.263357826682494,49.40095726384542}},color={0,0,127}));

  //
  // End Connect Statements for def91e8a
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