within time_series_heating_indirect.Districts;
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
  // Begin Model Instance for TimeSerLoa_65361aa9
  // Source template: /model_connectors/load_connectors/templates/TimeSeries_Instance.mopt
  //
  // time series load
  time_series_heating_indirect.Loads.B5a6b99ec37f4de7f94020090.TimeSeriesBuilding TimeSerLoa_65361aa9(

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
  // End Model Instance for TimeSerLoa_65361aa9
  //



  //
  // Begin Model Instance for heaInd_19a82808
  // Source template: /model_connectors/energy_transfer_systems/templates/HeatingIndirect_Instance.mopt
  //
  // heating indirect instance
  time_series_heating_indirect.Substations.HeatingIndirect_5a6b99ec37f4de7f94020090 heaInd_19a82808(
    allowFlowReversal1=true,
    allowFlowReversal2=true,
    show_T=true,
    redeclare package Medium=MediumW,
    mDis_flow_nominal=mDis_flow_nominal_7ae4953a,
    mBui_flow_nominal=mBui_flow_nominal_7ae4953a,
    dpValve_nominal=6000,
    dp1_nominal=500,
    dp2_nominal=500,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_7ae4953a,
    T_a1_nominal=55+273.15,
    T_a2_nominal=35+273.15,
    k=0.1,
    Ti=60,
    reverseActing=true)
    annotation (Placement(transformation(extent={{10.0,30.0},{30.0,50.0}})));
  //
  // End Model Instance for heaInd_19a82808
  //



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
  // Begin Model Instance for etsColWatStub_6ec5ff91
  // Source template: /model_connectors/energy_transfer_systems/templates/EtsColdWaterStub_Instance.mopt
  //
  // TODO: move these components into a single component
  Buildings.Fluid.Sources.Boundary_pT supChiWat_etsColWatStub_6ec5ff91(
    redeclare package Medium=MediumW,
    use_T_in=true,
    nPorts=1)
    "Chilled water supply"
    annotation (Placement(transformation(extent={{10.0,-50.0},{30.0,-30.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinChiWat_etsColWatStub_6ec5ff91(
    redeclare package Medium=MediumW,
    nPorts=1)
    "Chilled water sink"
    annotation (Placement(transformation(extent={{50.0,-50.0},{70.0,-30.0}})));
  //
  // End Model Instance for etsColWatStub_6ec5ff91
  //




  // Model dependencies

  //
  // Begin Component Definitions for 7ae4953a
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ComponentDefinitions.mopt
  //
  // TimeSeries + HeatingIndirect Component Definitions
  // TODO: the components below need to be fixed!
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_7ae4953a=TimeSerLoa_65361aa9.mHeaWat_flow_nominal*delHeaWatTemBui/delHeaWatTemDis
    "Nominal mass flow rate of primary (district) district heating side";
  parameter Modelica.Units.SI.MassFlowRate mBui_flow_nominal_7ae4953a=TimeSerLoa_65361aa9.mHeaWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district heating side";
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_7ae4953a=(TimeSerLoa_65361aa9.QHea_flow_nominal);
  Modelica.Fluid.Sources.FixedBoundary pressure_source_7ae4953a(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{-70.0,-10.0},{-50.0,10.0}})));
  // TODO: move THeaWatSet (and its connection) into a HeatingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression THeaWatSet_7ae4953a(
    // y=40+273.15)
    y=273.15+40 )
    "Secondary loop (Building side) heating water setpoint temperature."
    //Dehardcode
    annotation (Placement(transformation(extent={{-30.0,-10.0},{-10.0,10.0}})));

  //
  // End Component Definitions for 7ae4953a
  //



  //
  // Begin Component Definitions for 2fbf8108
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_NetworkHeatedWaterStub/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression secMasFloRat_2fbf8108(
    // TODO: avoid reaching into other coupling!
    // Warning: the value here is multiplied by 5/7.5 for unknown (undocumented) reasons and needs to be reevaluated in the future.
    y=mDis_flow_nominal_7ae4953a*5/7.5)
    "Secondary loop heated water flow rate."
    annotation (Placement(transformation(extent={{10.0,-10.0},{30.0,10.0}})));

  //
  // End Component Definitions for 2fbf8108
  //



  //
  // Begin Component Definitions for faf83a95
  // Source template: /model_connectors/couplings/templates/TimeSeries_EtsColdWaterStub/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression TChiWatSup_faf83a95(
    y=TimeSerLoa_65361aa9.T_aChiWat_nominal)
    "Chilled water supply temperature"
    annotation (Placement(transformation(extent={{50.0,-10.0},{70.0,10.0}})));

  //
  // End Component Definitions for faf83a95
  //



equation
  // Connections

  //
  // Begin Connect Statements for 7ae4953a
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ConnectStatements.mopt
  //

  // heating indirect, timeseries coupling connections
  connect(TimeSerLoa_65361aa9.ports_bHeaWat[1], heaInd_19a82808.port_a2)
    annotation (Line(points={{48.77176077129084,48.21770539428516},{28.771760771290843,48.21770539428516}},color={0,0,127}));
  connect(heaInd_19a82808.port_b2,TimeSerLoa_65361aa9.ports_aHeaWat[1])
    annotation (Line(points={{45.99847191904169,34.8957499243863},{65.99847191904169,34.8957499243863}},color={0,0,127}));
  connect(pressure_source_7ae4953a.ports[1], heaInd_19a82808.port_b2)
    annotation (Line(points={{-57.047741566186986,26.902537996451407},{-57.047741566186986,46.90253799645141},{-37.047741566186986,46.90253799645141},{-17.047741566186986,46.90253799645141},{2.9522584338130144,46.90253799645141},{22.952258433813014,46.90253799645141}},color={0,0,127}));
  connect(THeaWatSet_7ae4953a.y,heaInd_19a82808.TSetBuiSup)
    annotation (Line(points={{-21.62499117072882,26.336810556090178},{-21.62499117072882,46.33681055609017},{-1.6249911707288192,46.33681055609017},{18.37500882927118,46.33681055609017}},color={0,0,127}));

  //
  // End Connect Statements for 7ae4953a
  //



  //
  // Begin Connect Statements for 2fbf8108
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_NetworkHeatedWaterStub/ConnectStatements.mopt
  //

  // Heating indirect, Heated water stub connections
  connect(secMasFloRat_2fbf8108.y, supHeaWat.m_flow_in)
    annotation (Line(points={{29.22857546334687,-20.036721225739058},{9.228575463346871,-20.036721225739058},{-10.771424536653129,-20.036721225739058},{-30.77142453665313,-20.036721225739058},{-30.77142453665313,-40.03672122573906},{-50.77142453665313,-40.03672122573906}},color={0,0,127}));
  connect(heaInd_19a82808.port_a1,supHeaWat.ports[1])
    annotation (Line(points={{25.869830846581394,22.445545839717},{5.869830846581394,22.445545839717},{5.869830846581394,2.445545839716999},{5.869830846581394,-17.554454160283},{-14.130169153418606,-17.554454160283},{-34.130169153418606,-17.554454160283},{-34.130169153418606,-37.554454160283},{-54.130169153418606,-37.554454160283}},color={0,0,127}));
  connect(sinHeaWat.ports[1],heaInd_19a82808.port_b1)
    annotation (Line(points={{-27.995749588640976,-23.146939958297438},{-7.995749588640976,-23.146939958297438},{-7.995749588640976,-3.1469399582974376},{-7.995749588640976,16.85306004170257},{-7.995749588640976,36.85306004170257},{12.004250411359024,36.85306004170257}},color={0,0,127}));

  //
  // End Connect Statements for 2fbf8108
  //



  //
  // Begin Connect Statements for faf83a95
  // Source template: /model_connectors/couplings/templates/TimeSeries_EtsColdWaterStub/ConnectStatements.mopt
  //

  // time series, ets cold water stub connections
  connect(TChiWatSup_faf83a95.y,supChiWat_etsColWatStub_6ec5ff91.T_in)
    annotation (Line(points={{66.7431727193661,-28.34467604073633},{46.7431727193661,-28.34467604073633},{46.7431727193661,-48.34467604073633},{26.743172719366115,-48.34467604073633}},color={0,0,127}));
  connect(TimeSerLoa_65361aa9.ports_bChiWat[1],sinChiWat_etsColWatStub_6ec5ff91.ports[1])
    annotation (Line(points={{66.605515143671,12.07331281612872},{46.605515143671,12.07331281612872},{46.605515143671,-7.92668718387128},{46.605515143671,-27.92668718387128},{46.605515143671,-47.92668718387128},{66.605515143671,-47.92668718387128}},color={0,0,127}));
  connect(supChiWat_etsColWatStub_6ec5ff91.ports[1],TimeSerLoa_65361aa9.ports_aChiWat[1])
    annotation (Line(points={{27.701838685941738,-28.995271942826705},{47.70183868594174,-28.995271942826705},{47.70183868594174,-8.995271942826705},{47.70183868594174,11.004728057173295},{47.70183868594174,31.004728057173295},{67.70183868594174,31.004728057173295}},color={0,0,127}));

  //
  // End Connect Statements for faf83a95
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
