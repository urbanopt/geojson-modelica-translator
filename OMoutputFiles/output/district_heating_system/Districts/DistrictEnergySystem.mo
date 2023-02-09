within district_heating_system.Districts;
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
  // Begin Model Instance for disNet_01b8c046
  // Source template: /model_connectors/networks/templates/Network2Pipe_Instance.mopt
  //
parameter Integer nBui_disNet_01b8c046=2;
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_disNet_01b8c046=sum({
    heaInd_cd9802f7.mDis_flow_nominal,
  heaInd_9099a4e7.mDis_flow_nominal})
    "Nominal mass flow rate of the distribution pump";
  parameter Modelica.Units.SI.MassFlowRate mCon_flow_nominal_disNet_01b8c046[nBui_disNet_01b8c046]={
    heaInd_cd9802f7.mDis_flow_nominal,
  heaInd_9099a4e7.mDis_flow_nominal}
    "Nominal mass flow rate in each connection line";
  parameter Modelica.Units.SI.PressureDifference dpDis_nominal_disNet_01b8c046[nBui_disNet_01b8c046](
    each min=0,
    each displayUnit="Pa")=1/2 .* cat(
    1,
    {dp_nominal_disNet_01b8c046*0.1},
    fill(
      dp_nominal_disNet_01b8c046*0.9/(nBui_disNet_01b8c046-1),
      nBui_disNet_01b8c046-1))
    "Pressure drop between each connected building at nominal conditions (supply line)";
  parameter Modelica.Units.SI.PressureDifference dp_nominal_disNet_01b8c046=dpSetPoi_disNet_01b8c046+nBui_disNet_01b8c046*7000
    "District network pressure drop";
  // NOTE: this differential pressure setpoint is currently utilized by plants elsewhere
  parameter Modelica.Units.SI.Pressure dpSetPoi_disNet_01b8c046=50000
    "Differential pressure setpoint";

  Buildings.Experimental.DHC.Networks.Distribution2Pipe disNet_01b8c046(
    redeclare final package Medium=MediumW,
    final nCon=nBui_disNet_01b8c046,
    iConDpSen=nBui_disNet_01b8c046,
    final mDis_flow_nominal=mDis_flow_nominal_disNet_01b8c046,
    final mCon_flow_nominal=mCon_flow_nominal_disNet_01b8c046,
    final allowFlowReversal=true,
    dpDis_nominal=dpDis_nominal_disNet_01b8c046)
    "Distribution network."
    annotation (Placement(transformation(extent={{-30.0,80.0},{-10.0,90.0}})));
  //
  // End Model Instance for disNet_01b8c046
  //


  
  //
  // Begin Model Instance for heaPlad55e8068
  // Source template: /model_connectors/plants/templates/HeatingPlant_Instance.mopt
  //
  // heating plant instance
  parameter Modelica.Units.SI.MassFlowRate mHW_flow_nominal_heaPlad55e8068=mBoi_flow_nominal_heaPlad55e8068*heaPlad55e8068.numBoi
    "Nominal heating water mass flow rate";
  parameter Modelica.Units.SI.MassFlowRate mBoi_flow_nominal_heaPlad55e8068=QBoi_nominal_heaPlad55e8068/(4200*heaPlad55e8068.delT_nominal)
    "Nominal heating water mass flow rate";
  parameter Modelica.Units.SI.Power QBoi_nominal_heaPlad55e8068=Q_flow_nominal_heaPlad55e8068/heaPlad55e8068.numBoi
    "Nominal heating capaciaty";
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_heaPlad55e8068=1000000*2
    "Heating load";
  parameter Modelica.Units.SI.MassFlowRate mMin_flow_heaPlad55e8068=0.2*mBoi_flow_nominal_heaPlad55e8068
    "Minimum mass flow rate of single boiler";
  // controls
  parameter Modelica.Units.SI.Pressure pumDP=(heaPlad55e8068.dpBoi_nominal+dpSetPoi_disNet_01b8c046+50000)
    "Heating water pump pressure drop";
  parameter Modelica.Units.SI.Time tWai_heaPlad55e8068=30
    "Waiting time";
  parameter Buildings.Fluid.Movers.Data.Generic perHWPum_heaPlad55e8068(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=mBoi_flow_nominal_heaPlad55e8068/1000*{0.1,1.1},
      dp=pumDP*{1.1,0.1}))
    "Performance data for heating water pumps";

  district_heating_system.Plants.CentralHeatingPlant heaPlad55e8068(
    perHWPum=perHWPum_heaPlad55e8068,
    mHW_flow_nominal=mHW_flow_nominal_heaPlad55e8068,
    QBoi_flow_nominal=QBoi_nominal_heaPlad55e8068,
    mMin_flow=mMin_flow_heaPlad55e8068,
    mBoi_flow_nominal=mBoi_flow_nominal_heaPlad55e8068,
    dpBoi_nominal=10000,
    delT_nominal(
      displayUnit="degC")=15,
    tWai=tWai_heaPlad55e8068,
    // TODO: we're currently grabbing dpSetPoi from the Network instance -- need feedback to determine if that's the proper "home" for it
    dpSetPoi=dpSetPoi_disNet_01b8c046
    )
    "District heating plant."
    annotation (Placement(transformation(extent={{-70.0,70.0},{-50.0,90.0}})));
  //
  // End Model Instance for heaPlad55e8068
  //


  
  //
  // Begin Model Instance for TimeSerLoa_a0ae3e74
  // Source template: /model_connectors/load_connectors/templates/TimeSeries_Instance.mopt
  //
  // time series load
  district_heating_system.Loads.B5a6b99ec37f4de7f94020090.TimeSeriesBuilding TimeSerLoa_a0ae3e74(
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
    annotation (Placement(transformation(extent={{50.0,70.0},{70.0,90.0}})));
  //
  // End Model Instance for TimeSerLoa_a0ae3e74
  //


  
  //
  // Begin Model Instance for heaInd_cd9802f7
  // Source template: /model_connectors/energy_transfer_systems/templates/HeatingIndirect_Instance.mopt
  //
  // heating indirect instance
  district_heating_system.Substations.HeatingIndirect_5a6b99ec37f4de7f94020090 heaInd_cd9802f7(
    allowFlowReversal1=true,
    allowFlowReversal2=true,
    show_T=true,
    redeclare package Medium=MediumW,
    mDis_flow_nominal=mDis_flow_nominal_6df20f47,
    mBui_flow_nominal=mBui_flow_nominal_6df20f47,
    dpValve_nominal=6000,
    dp1_nominal=500,
    dp2_nominal=500,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_6df20f47,
    T_a1_nominal=55+273.15,
    T_a2_nominal=35+273.15,
    k=0.1,
    Ti=60,
    reverseActing=true)
    annotation (Placement(transformation(extent={{10.0,70.0},{30.0,90.0}})));
  //
  // End Model Instance for heaInd_cd9802f7
  //


  
  //
  // Begin Model Instance for etsColWatStub_b650d6b2
  // Source template: /model_connectors/energy_transfer_systems/templates/EtsColdWaterStub_Instance.mopt
  //
  // TODO: move these components into a single component
  Buildings.Fluid.Sources.Boundary_pT supChiWat_etsColWatStub_b650d6b2(
    redeclare package Medium=MediumW,
    use_T_in=true,
    nPorts=1)
    "Chilled water supply"
    annotation (Placement(transformation(extent={{-70.0,-90.0},{-50.0,-70.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinChiWat_etsColWatStub_b650d6b2(
    redeclare package Medium=MediumW,
    nPorts=1)
    "Chilled water sink"
    annotation (Placement(transformation(extent={{-30.0,-90.0},{-10.0,-70.0}})));
  //
  // End Model Instance for etsColWatStub_b650d6b2
  //


  
  //
  // Begin Model Instance for TimeSerLoa_fad64cd4
  // Source template: /model_connectors/load_connectors/templates/TimeSeries_Instance.mopt
  //
  // time series load
  district_heating_system.Loads.abcdefghijklmnopqrstuvwx.TimeSeriesBuilding TimeSerLoa_fad64cd4(
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
  // End Model Instance for TimeSerLoa_fad64cd4
  //


  
  //
  // Begin Model Instance for heaInd_9099a4e7
  // Source template: /model_connectors/energy_transfer_systems/templates/HeatingIndirect_Instance.mopt
  //
  // heating indirect instance
  district_heating_system.Substations.HeatingIndirect_abcdefghijklmnopqrstuvwx heaInd_9099a4e7(
    allowFlowReversal1=true,
    allowFlowReversal2=true,
    show_T=true,
    redeclare package Medium=MediumW,
    mDis_flow_nominal=mDis_flow_nominal_2a7d0c4a,
    mBui_flow_nominal=mBui_flow_nominal_2a7d0c4a,
    dpValve_nominal=6000,
    dp1_nominal=500,
    dp2_nominal=500,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_2a7d0c4a,
    T_a1_nominal=55+273.15,
    T_a2_nominal=35+273.15,
    k=0.1,
    Ti=60,
    reverseActing=true)
    annotation (Placement(transformation(extent={{10.0,30.0},{30.0,50.0}})));
  //
  // End Model Instance for heaInd_9099a4e7
  //


  
  //
  // Begin Model Instance for etsColWatStub_db12c57f
  // Source template: /model_connectors/energy_transfer_systems/templates/EtsColdWaterStub_Instance.mopt
  //
  // TODO: move these components into a single component
  Buildings.Fluid.Sources.Boundary_pT supChiWat_etsColWatStub_db12c57f(
    redeclare package Medium=MediumW,
    use_T_in=true,
    nPorts=1)
    "Chilled water supply"
    annotation (Placement(transformation(extent={{10.0,-90.0},{30.0,-70.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinChiWat_etsColWatStub_db12c57f(
    redeclare package Medium=MediumW,
    nPorts=1)
    "Chilled water sink"
    annotation (Placement(transformation(extent={{50.0,-90.0},{70.0,-70.0}})));
  //
  // End Model Instance for etsColWatStub_db12c57f
  //


  

  // Model dependencies

  //
  // Begin Component Definitions for 86c7e579
  // Source template: /model_connectors/couplings/templates/Network2Pipe_HeatingPlant/ComponentDefinitions.mopt
  //
  // TODO: This should not be here, it is entirely plant specific and should be moved elsewhere
  // but since it requires a connect statement we must put it here for now...
  Modelica.Blocks.Sources.BooleanConstant mPum_flow_86c7e579(
    k=true)
    "Total heating water pump mass flow rate"
    annotation (Placement(transformation(extent={{-70.0,-10.0},{-50.0,10.0}})));
  // TODO: This should not be here, it is entirely plant specific and should be moved elsewhere
  // but since it requires a connect statement we must put it here for now...
  Modelica.Blocks.Sources.RealExpression TDisSetHeaWat_86c7e579(
    each y=273.15+68)
    "District side heating water supply temperature set point."
    annotation (Placement(transformation(extent={{-30.0,-10.0},{-10.0,10.0}})));

  //
  // End Component Definitions for 86c7e579
  //



  //
  // Begin Component Definitions for 6df20f47
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ComponentDefinitions.mopt
  //
  // TimeSeries + HeatingIndirect Component Definitions
  // TODO: the components below need to be fixed!
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_6df20f47=TimeSerLoa_a0ae3e74.mHeaWat_flow_nominal*delHeaWatTemBui/delHeaWatTemDis
    "Nominal mass flow rate of primary (district) district heating side";
  parameter Modelica.Units.SI.MassFlowRate mBui_flow_nominal_6df20f47=TimeSerLoa_a0ae3e74.mHeaWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district heating side";
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_6df20f47=(TimeSerLoa_a0ae3e74.QHea_flow_nominal);
  Modelica.Fluid.Sources.FixedBoundary pressure_source_6df20f47(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{10.0,-10.0},{30.0,10.0}})));
  // TODO: move THeaWatSet (and its connection) into a HeatingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression THeaWatSet_6df20f47(
    // y=40+273.15)
    y=273.15+40 )
    "Secondary loop (Building side) heating water setpoint temperature."
    //Dehardcode
    annotation (Placement(transformation(extent={{50.0,-10.0},{70.0,10.0}})));

  //
  // End Component Definitions for 6df20f47
  //



  //
  // Begin Component Definitions for ef02dd6a
  // Source template: /model_connectors/couplings/templates/TimeSeries_EtsColdWaterStub/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression TChiWatSup_ef02dd6a(
    y=TimeSerLoa_a0ae3e74.T_aChiWat_nominal)
    "Chilled water supply temperature"
    annotation (Placement(transformation(extent={{-70.0,-50.0},{-50.0,-30.0}})));

  //
  // End Component Definitions for ef02dd6a
  //



  //
  // Begin Component Definitions for 0fa958f9
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for heating indirect and network 2 pipe

  //
  // End Component Definitions for 0fa958f9
  //



  //
  // Begin Component Definitions for 2a7d0c4a
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ComponentDefinitions.mopt
  //
  // TimeSeries + HeatingIndirect Component Definitions
  // TODO: the components below need to be fixed!
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_2a7d0c4a=TimeSerLoa_fad64cd4.mHeaWat_flow_nominal*delHeaWatTemBui/delHeaWatTemDis
    "Nominal mass flow rate of primary (district) district heating side";
  parameter Modelica.Units.SI.MassFlowRate mBui_flow_nominal_2a7d0c4a=TimeSerLoa_fad64cd4.mHeaWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district heating side";
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_2a7d0c4a=(TimeSerLoa_fad64cd4.QHea_flow_nominal);
  Modelica.Fluid.Sources.FixedBoundary pressure_source_2a7d0c4a(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{-30.0,-50.0},{-10.0,-30.0}})));
  // TODO: move THeaWatSet (and its connection) into a HeatingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression THeaWatSet_2a7d0c4a(
    // y=40+273.15)
    y=273.15+40 )
    "Secondary loop (Building side) heating water setpoint temperature."
    //Dehardcode
    annotation (Placement(transformation(extent={{10.0,-50.0},{30.0,-30.0}})));

  //
  // End Component Definitions for 2a7d0c4a
  //



  //
  // Begin Component Definitions for a28b0ad3
  // Source template: /model_connectors/couplings/templates/TimeSeries_EtsColdWaterStub/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression TChiWatSup_a28b0ad3(
    y=TimeSerLoa_fad64cd4.T_aChiWat_nominal)
    "Chilled water supply temperature"
    annotation (Placement(transformation(extent={{50.0,-50.0},{70.0,-30.0}})));

  //
  // End Component Definitions for a28b0ad3
  //



  //
  // Begin Component Definitions for 196a7c69
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for heating indirect and network 2 pipe

  //
  // End Component Definitions for 196a7c69
  //



equation
  // Connections

  //
  // Begin Connect Statements for 86c7e579
  // Source template: /model_connectors/couplings/templates/Network2Pipe_HeatingPlant/ConnectStatements.mopt
  //

  connect(heaPlad55e8068.port_a,disNet_01b8c046.port_bDisRet)
    annotation (Line(points={{-37.059236950300885,78.10370412549929},{-17.059236950300885,78.10370412549929}},color={0,0,127}));
  connect(disNet_01b8c046.dp,heaPlad55e8068.dpMea)
    annotation (Line(points={{-31.816593537557104,79.12234925376447},{-51.816593537557104,79.12234925376447}},color={0,0,127}));
  connect(heaPlad55e8068.port_b,disNet_01b8c046.port_aDisSup)
    annotation (Line(points={{-45.940971992398154,83.33581763431796},{-25.940971992398147,83.33581763431796}},color={0,0,127}));
  connect(mPum_flow_86c7e579.y,heaPlad55e8068.on)
    annotation (Line(points={{-68.95868202834694,14.031474063505797},{-68.95868202834694,34.0314740635058},{-68.95868202834694,54.031474063505804},{-68.95868202834694,74.03147406350581}},color={0,0,127}));
  connect(TDisSetHeaWat_86c7e579.y,heaPlad55e8068.THeaSet)
    annotation (Line(points={{-11.027871240824467,17.498033092097955},{-11.027871240824467,37.498033092097955},{-11.027871240824467,57.498033092097955},{-31.027871240824467,57.498033092097955},{-31.027871240824467,77.49803309209796},{-51.02787124082447,77.49803309209796}},color={0,0,127}));

  //
  // End Connect Statements for 86c7e579
  //



  //
  // Begin Connect Statements for 6df20f47
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ConnectStatements.mopt
  //

  // heating indirect, timeseries coupling connections
  connect(TimeSerLoa_a0ae3e74.ports_bHeaWat[1], heaInd_cd9802f7.port_a2)
    annotation (Line(points={{34.08699305999116,78.23382454271028},{14.086993059991158,78.23382454271028}},color={0,0,127}));
  connect(heaInd_cd9802f7.port_b2,TimeSerLoa_a0ae3e74.ports_aHeaWat[1])
    annotation (Line(points={{38.5584749161406,79.89545942284425},{58.5584749161406,79.89545942284425}},color={0,0,127}));
  connect(pressure_source_6df20f47.ports[1], heaInd_cd9802f7.port_b2)
    annotation (Line(points={{22.453874335938522,29.523757468871864},{2.453874335938522,29.523757468871864},{2.453874335938522,49.52375746887187},{2.453874335938522,69.52375746887188},{2.453874335938522,89.52375746887188},{22.453874335938522,89.52375746887188}},color={0,0,127}));
  connect(THeaWatSet_6df20f47.y,heaInd_cd9802f7.TSetBuiSup)
    annotation (Line(points={{65.7829997942597,20.42060281468342},{45.782999794259695,20.42060281468342},{45.782999794259695,40.42060281468342},{45.782999794259695,60.42060281468342},{45.782999794259695,80.42060281468342},{25.78299979425971,80.42060281468342}},color={0,0,127}));

  //
  // End Connect Statements for 6df20f47
  //



  //
  // Begin Connect Statements for ef02dd6a
  // Source template: /model_connectors/couplings/templates/TimeSeries_EtsColdWaterStub/ConnectStatements.mopt
  //

  // time series, ets cold water stub connections
  connect(TChiWatSup_ef02dd6a.y,supChiWat_etsColWatStub_b650d6b2.T_in)
    annotation (Line(points={{-51.37141650405521,-69.50964297397857},{-51.37141650405521,-89.50964297397857}},color={0,0,127}));
  connect(TimeSerLoa_a0ae3e74.ports_bChiWat[1],sinChiWat_etsColWatStub_b650d6b2.ports[1])
    annotation (Line(points={{60.40835929693415,65.97931558371306},{40.40835929693415,65.97931558371306},{40.40835929693415,45.97931558371306},{40.40835929693415,25.97931558371306},{40.40835929693415,5.97931558371306},{40.40835929693415,-14.02068441628694},{40.40835929693415,-34.02068441628694},{40.40835929693415,-54.02068441628694},{20.40835929693415,-54.02068441628694},{0.40835929693415096,-54.02068441628694},{0.40835929693415096,-74.02068441628694},{-19.59164070306585,-74.02068441628694}},color={0,0,127}));
  connect(supChiWat_etsColWatStub_b650d6b2.ports[1],TimeSerLoa_a0ae3e74.ports_aChiWat[1])
    annotation (Line(points={{-60.93581359678389,-64.7933557597986},{-40.93581359678389,-64.7933557597986},{-40.93581359678389,-44.7933557597986},{-40.93581359678389,-24.7933557597986},{-40.93581359678389,-4.793355759798601},{-40.93581359678389,15.206644240201399},{-40.93581359678389,35.2066442402014},{-40.93581359678389,55.2066442402014},{-20.935813596783888,55.2066442402014},{-0.9358135967838876,55.2066442402014},{19.064186403216112,55.2066442402014},{39.06418640321613,55.2066442402014},{39.06418640321613,75.2066442402014},{59.06418640321613,75.2066442402014}},color={0,0,127}));

  //
  // End Connect Statements for ef02dd6a
  //



  //
  // Begin Connect Statements for 0fa958f9
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // heating indirect and network 2 pipe
  
  connect(disNet_01b8c046.ports_bCon[1],heaInd_cd9802f7.port_a1)
    annotation (Line(points={{-2.128309045907855,79.1200280952537},{17.871690954092145,79.1200280952537}},color={0,0,127}));
  connect(disNet_01b8c046.ports_aCon[1],heaInd_cd9802f7.port_b1)
    annotation (Line(points={{0.33622666964599546,73.49776889734467},{20.336226669645995,73.49776889734467}},color={0,0,127}));

  //
  // End Connect Statements for 0fa958f9
  //



  //
  // Begin Connect Statements for 2a7d0c4a
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ConnectStatements.mopt
  //

  // heating indirect, timeseries coupling connections
  connect(TimeSerLoa_fad64cd4.ports_bHeaWat[1], heaInd_9099a4e7.port_a2)
    annotation (Line(points={{44.98716034442273,43.73017988157636},{24.987160344422747,43.73017988157636}},color={0,0,127}));
  connect(heaInd_9099a4e7.port_b2,TimeSerLoa_fad64cd4.ports_aHeaWat[1])
    annotation (Line(points={{38.753875396932386,47.930269013806246},{58.753875396932386,47.930269013806246}},color={0,0,127}));
  connect(pressure_source_2a7d0c4a.ports[1], heaInd_9099a4e7.port_b2)
    annotation (Line(points={{-23.065011448856197,-20.135195740058236},{-3.065011448856197,-20.135195740058236},{-3.065011448856197,-0.13519574005823642},{-3.065011448856197,19.864804259941764},{-3.065011448856197,39.864804259941764},{16.934988551143803,39.864804259941764}},color={0,0,127}));
  connect(THeaWatSet_2a7d0c4a.y,heaInd_9099a4e7.TSetBuiSup)
    annotation (Line(points={{28.876714408446915,-21.182732234240945},{8.876714408446915,-21.182732234240945},{8.876714408446915,-1.1827322342409445},{8.876714408446915,18.817267765759055},{8.876714408446915,38.817267765759055},{28.876714408446915,38.817267765759055}},color={0,0,127}));

  //
  // End Connect Statements for 2a7d0c4a
  //



  //
  // Begin Connect Statements for a28b0ad3
  // Source template: /model_connectors/couplings/templates/TimeSeries_EtsColdWaterStub/ConnectStatements.mopt
  //

  // time series, ets cold water stub connections
  connect(TChiWatSup_a28b0ad3.y,supChiWat_etsColWatStub_db12c57f.T_in)
    annotation (Line(points={{50.756196056495355,-60.06402582354539},{30.75619605649534,-60.06402582354539},{30.75619605649534,-80.06402582354539},{10.756196056495341,-80.06402582354539}},color={0,0,127}));
  connect(TimeSerLoa_fad64cd4.ports_bChiWat[1],sinChiWat_etsColWatStub_db12c57f.ports[1])
    annotation (Line(points={{51.557835292066954,20.500256734799564},{31.55783529206697,20.500256734799564},{31.55783529206697,0.5002567347995637},{31.55783529206697,-19.499743265200436},{31.55783529206697,-39.499743265200436},{31.55783529206697,-59.499743265200436},{31.55783529206697,-79.49974326520044},{51.557835292066954,-79.49974326520044}},color={0,0,127}));
  connect(supChiWat_etsColWatStub_db12c57f.ports[1],TimeSerLoa_fad64cd4.ports_aChiWat[1])
    annotation (Line(points={{13.34145035299953,-63.121539388021375},{33.34145035299953,-63.121539388021375},{33.34145035299953,-43.121539388021375},{33.34145035299953,-23.121539388021375},{33.34145035299953,-3.1215393880213753},{33.34145035299953,16.878460611978625},{33.34145035299953,36.878460611978625},{53.341450352999516,36.878460611978625}},color={0,0,127}));

  //
  // End Connect Statements for a28b0ad3
  //



  //
  // Begin Connect Statements for 196a7c69
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // heating indirect and network 2 pipe
  
  connect(disNet_01b8c046.ports_bCon[2],heaInd_9099a4e7.port_a1)
    annotation (Line(points={{-14.412031081497304,69.03194941964773},{-14.412031081497304,49.03194941964774},{5.587968918502696,49.03194941964774},{25.587968918502696,49.03194941964774}},color={0,0,127}));
  connect(disNet_01b8c046.ports_aCon[2],heaInd_9099a4e7.port_b1)
    annotation (Line(points={{-18.694209133759387,64.3642416685768},{-18.694209133759387,44.36424166857678},{1.3057908662406135,44.36424166857678},{21.305790866240613,44.36424166857678}},color={0,0,127}));

  //
  // End Connect Statements for 196a7c69
  //




annotation(
  experiment(
    StopTime=86400,
    Interval=3600,
    Tolerance=1e-06),
  Diagram(
    coordinateSystem(
      preserveAspectRatio=false,
      extent={{-90.0,-110.0},{90.0,110.0}})),
  Documentation(
    revisions="<html>
 <li>
 May 10, 2020: Hagar Elarga<br/>
Updated implementation to handle template needed for GeoJSON to Modelica.
</li>
</html>"));
end DistrictEnergySystem;