within district_system.Districts;
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
  // Begin Model Instance for TimeSerLoa_73fdcbf0
  // Source template: /model_connectors/load_connectors/templates/TimeSeries_Instance.mopt
  //
  // time series load
  district_system.Loads.B5a6b99ec37f4de7f94020090.TimeSeriesBuilding TimeSerLoa_73fdcbf0(
     allowFlowReversal=true,
    T_aHeaWat_nominal(displayUnit="K")=318.15,
    T_aChiWat_nominal(displayUnit="K")=280.15,
    delTAirCoo(displayUnit="degC")=10,
    delTAirHea(displayUnit="degC")=20,
    k=0.1,
    Ti=120,
    nPorts_aHeaWat=1,
    nPorts_bHeaWat=1,
    nPorts_aChiWat=1,
    nPorts_bChiWat=1
    
    )
    "Building model integrating multiple time series thermal zones."
    annotation (Placement(transformation(extent={{50.0,30.0},{70.0,50.0}})));
  //
  // End Model Instance for TimeSerLoa_73fdcbf0
  //


  
  //
  // Begin Model Instance for cooInd_3ea744ee
  // Source template: /model_connectors/energy_transfer_systems/templates/CoolingIndirect_Instance.mopt
  //
  // cooling indirect instance
  district_system.Substations.CoolingIndirect_5a6b99ec37f4de7f94020090 cooInd_3ea744ee(
    redeclare package Medium=MediumW,
    allowFlowReversal1=true,
    allowFlowReversal2=true,
    mDis_flow_nominal=mDis_flow_nominal_5009fa3c,
    mBui_flow_nominal=mBui_flow_nominal_5009fa3c,
    dp1_nominal=500,
    dp2_nominal=500,
    dpValve_nominal=7000,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_5009fa3c,
    // TODO: dehardcode the nominal temperatures?
    T_a1_nominal=273.15+5,
    T_a2_nominal=273.15+13)
    "Indirect cooling energy transfer station ETS."
    annotation (Placement(transformation(extent={{10.0,30.0},{30.0,50.0}})));
  //
  // End Model Instance for cooInd_3ea744ee
  //


  
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
    annotation (Placement(transformation(extent={{-70.0,-50.0},{-50.0,-30.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinChiWat1(
    redeclare package Medium=MediumW,
    nPorts=1)
    "Chilled water sink (district side)"
    annotation (Placement(transformation(extent={{-30.0,-50.0},{-10.0,-30.0}})));
  //
  // End Model Instance for MyNetworkChilledWaterStub
  //


  
  //
  // Begin Model Instance for etsHotWatStub_031959d2
  // Source template: /model_connectors/energy_transfer_systems/templates/EtsHotWaterStub_Instance.mopt
  //
  // TODO: move these components into a single component
  Buildings.Fluid.Sources.Boundary_pT supHeaWat_etsHotWatStub_031959d2(
    redeclare package Medium=MediumW,
    use_T_in=true,
    nPorts=1)
    "Heating water supply"
    annotation (Placement(transformation(extent={{10.0,-50.0},{30.0,-30.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinHeaWat_etsHotWatStub_031959d2(
    redeclare package Medium=MediumW,
    nPorts=1)
    "Heating water sink"
    annotation (Placement(transformation(extent={{50.0,-50.0},{70.0,-30.0}})));
  //
  // End Model Instance for etsHotWatStub_031959d2
  //


  

  // Model dependencies

  //
  // Begin Component Definitions for 5009fa3c
  // Source template: /model_connectors/couplings/templates/TimeSeries_CoolingIndirect/ComponentDefinitions.mopt
  //
  // TimeSeries + CoolingIndirect Component Definitions
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_5009fa3c=TimeSerLoa_73fdcbf0.mChiWat_flow_nominal*delChiWatTemBui/delChiWatTemDis
    "Nominal mass flow rate of primary (district) district cooling side";
  parameter Modelica.Units.SI.MassFlowRate mBui_flow_nominal_5009fa3c=TimeSerLoa_73fdcbf0.mChiWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district cooling side";
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_5009fa3c=-1*(TimeSerLoa_73fdcbf0.QCoo_flow_nominal);
  Modelica.Fluid.Sources.FixedBoundary pressure_source_5009fa3c(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{-70.0,-10.0},{-50.0,10.0}})));
  // TODO: move TChiWatSet (and its connection) into a CoolingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression TChiWatSet_5009fa3c(
    y=7+273.15)
    //Dehardcode
    "Primary loop (district side) chilled water setpoint temperature."
    annotation (Placement(transformation(extent={{-30.0,-10.0},{-10.0,10.0}})));

  //
  // End Component Definitions for 5009fa3c
  //



  //
  // Begin Component Definitions for 0eaf10a6
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_NetworkChilledWaterStub/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression secMasFloRat_0eaf10a6(
    // TODO: avoid reaching into other coupling!
    // TODO: explain the 5/7.5
    y=mDis_flow_nominal_5009fa3c*5/7.5)
    "Secondary loop chilled water flow rate."
    annotation (Placement(transformation(extent={{10.0,-10.0},{30.0,10.0}})));

  //
  // End Component Definitions for 0eaf10a6
  //



  //
  // Begin Component Definitions for bcced681
  // Source template: /model_connectors/couplings/templates/TimeSeries_EtsHotWaterStub/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression THeaWatSup_bcced681(
    y=TimeSerLoa_73fdcbf0.T_aHeaWat_nominal)
    //Dehardcode where this is originally set
    "Heating water supply temperature"
    annotation (Placement(transformation(extent={{50.0,-10.0},{70.0,10.0}})));

  //
  // End Component Definitions for bcced681
  //



equation
  // Connections

  //
  // Begin Connect Statements for 5009fa3c
  // Source template: /model_connectors/couplings/templates/TimeSeries_CoolingIndirect/ConnectStatements.mopt
  //

  // cooling indirect, timeseries coupling connections
  connect(TimeSerLoa_73fdcbf0.ports_bChiWat[1], cooInd_3ea744ee.port_a2)
    annotation (Line(points={{40.94526490842031,48.727229417039524},{20.945264908420327,48.727229417039524}},color={0,0,127}));
  connect(cooInd_3ea744ee.port_b2,TimeSerLoa_73fdcbf0.ports_aChiWat[1])
    annotation (Line(points={{31.612748645168764,37.790915841156995},{51.61274864516878,37.790915841156995}},color={0,0,127}));
  connect(pressure_source_5009fa3c.ports[1], cooInd_3ea744ee.port_b2)
    annotation (Line(points={{-60.29483346568392,19.315291377211167},{-60.29483346568392,39.31529137721117},{-40.29483346568392,39.31529137721117},{-20.294833465683922,39.31529137721117},{-0.2948334656839222,39.31529137721117},{19.705166534316078,39.31529137721117}},color={0,0,127}));
  connect(TChiWatSet_5009fa3c.y,cooInd_3ea744ee.TSetBuiSup)
    annotation (Line(points={{-21.350159492595083,23.393848164030743},{-1.3501594925950826,23.393848164030743},{18.649840507404917,23.393848164030743},{38.64984050740492,23.393848164030743},{38.64984050740492,43.39384816403074},{58.64984050740492,43.39384816403074}},color={0,0,127}));

  //
  // End Connect Statements for 5009fa3c
  //



  //
  // Begin Connect Statements for 0eaf10a6
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_NetworkChilledWaterStub/ConnectStatements.mopt
  //

  // Cooling indirect, Chilled water stub connections
  connect(secMasFloRat_0eaf10a6.y, supChiWat.m_flow_in)
    annotation (Line(points={{15.799918173163832,-13.234905711259316},{-4.200081826836168,-13.234905711259316},{-24.20008182683617,-13.234905711259316},{-44.200081826836175,-13.234905711259316},{-44.200081826836175,-33.234905711259316},{-64.20008182683617,-33.234905711259316}},color={0,0,127}));
  connect(cooInd_3ea744ee.port_a1,supChiWat.ports[1])
    annotation (Line(points={{16.14730774165058,29.584730539133766},{-3.852692258349421,29.584730539133766},{-3.852692258349421,9.584730539133766},{-3.852692258349421,-10.415269460866227},{-23.85269225834942,-10.415269460866227},{-43.85269225834942,-10.415269460866227},{-43.85269225834942,-30.415269460866227},{-63.85269225834942,-30.415269460866227}},color={0,0,127}));
  connect(sinChiWat1.ports[1],cooInd_3ea744ee.port_b1)
    annotation (Line(points={{-20.360235906504954,-29.114358311057543},{-0.3602359065049541,-29.114358311057543},{-0.3602359065049541,-9.114358311057543},{-0.3602359065049541,10.885641688942457},{-0.3602359065049541,30.885641688942457},{19.639764093495046,30.885641688942457}},color={0,0,127}));

  //
  // End Connect Statements for 0eaf10a6
  //



  //
  // Begin Connect Statements for bcced681
  // Source template: /model_connectors/couplings/templates/TimeSeries_EtsHotWaterStub/ConnectStatements.mopt
  //

  // time series, ets hot water stub connections
  connect(supHeaWat_etsHotWatStub_031959d2.T_in,THeaWatSup_bcced681.y)
    annotation (Line(points={{16.704649301084558,-28.849729126071836},{36.70464930108456,-28.849729126071836},{36.70464930108456,-8.849729126071836},{56.704649301084544,-8.849729126071836}},color={0,0,127}));
  connect(supHeaWat_etsHotWatStub_031959d2.ports[1],TimeSerLoa_73fdcbf0.ports_aHeaWat[1])
    annotation (Line(points={{27.64216698537885,-18.520103145198604},{47.64216698537885,-18.520103145198604},{47.64216698537885,1.479896854801396},{47.64216698537885,21.479896854801396},{47.64216698537885,41.479896854801396},{67.64216698537885,41.479896854801396}},color={0,0,127}));
  connect(sinHeaWat_etsHotWatStub_031959d2.ports[1],TimeSerLoa_73fdcbf0.ports_bHeaWat[1])
    annotation (Line(points={{64.04711431128646,-17.195912416771506},{44.047114311286464,-17.195912416771506},{44.047114311286464,2.804087583228494},{44.047114311286464,22.804087583228487},{44.047114311286464,42.80408758322849},{64.04711431128646,42.80408758322849}},color={0,0,127}));

  //
  // End Connect Statements for bcced681
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