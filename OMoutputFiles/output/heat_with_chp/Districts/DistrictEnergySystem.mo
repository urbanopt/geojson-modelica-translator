within heat_with_chp.Districts;
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
  // Begin Model Instance for disNet_b3d86b1a
  // Source template: /model_connectors/networks/templates/Network2Pipe_Instance.mopt
  //
parameter Integer nBui_disNet_b3d86b1a=2;
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_disNet_b3d86b1a=sum({
    heaInd_0f7bb650.mDis_flow_nominal,
  heaInd_b40e7a31.mDis_flow_nominal})
    "Nominal mass flow rate of the distribution pump";
  parameter Modelica.Units.SI.MassFlowRate mCon_flow_nominal_disNet_b3d86b1a[nBui_disNet_b3d86b1a]={
    heaInd_0f7bb650.mDis_flow_nominal,
  heaInd_b40e7a31.mDis_flow_nominal}
    "Nominal mass flow rate in each connection line";
  parameter Modelica.Units.SI.PressureDifference dpDis_nominal_disNet_b3d86b1a[nBui_disNet_b3d86b1a](
    each min=0,
    each displayUnit="Pa")=1/2 .* cat(
    1,
    {dp_nominal_disNet_b3d86b1a*0.1},
    fill(
      dp_nominal_disNet_b3d86b1a*0.9/(nBui_disNet_b3d86b1a-1),
      nBui_disNet_b3d86b1a-1))
    "Pressure drop between each connected building at nominal conditions (supply line)";
  parameter Modelica.Units.SI.PressureDifference dp_nominal_disNet_b3d86b1a=dpSetPoi_disNet_b3d86b1a+nBui_disNet_b3d86b1a*7000
    "District network pressure drop";
  // NOTE: this differential pressure setpoint is currently utilized by plants elsewhere
  parameter Modelica.Units.SI.Pressure dpSetPoi_disNet_b3d86b1a=50000
    "Differential pressure setpoint";

  Buildings.Experimental.DHC.Networks.Distribution2Pipe disNet_b3d86b1a(
    redeclare final package Medium=MediumW,
    final nCon=nBui_disNet_b3d86b1a,
    iConDpSen=nBui_disNet_b3d86b1a,
    final mDis_flow_nominal=mDis_flow_nominal_disNet_b3d86b1a,
    final mCon_flow_nominal=mCon_flow_nominal_disNet_b3d86b1a,
    final allowFlowReversal=false,
    dpDis_nominal=dpDis_nominal_disNet_b3d86b1a)
    "Distribution network."
    annotation (Placement(transformation(extent={{-30.0,80.0},{-10.0,90.0}})));
  //
  // End Model Instance for disNet_b3d86b1a
  //


  
  //
  // Begin Model Instance for chpPla_0ae5a21c
  // Source template: /model_connectors/plants/templates/HeatingPlant_Instance.mopt
  //
  // heating plant instance
  parameter Modelica.Units.SI.MassFlowRate mHW_flow_nominal_chpPla_0ae5a21c=mBoi_flow_nominal_chpPla_0ae5a21c*chpPla_0ae5a21c.numBoi
    "Nominal heating water mass flow rate";
  parameter Modelica.Units.SI.MassFlowRate mBoi_flow_nominal_chpPla_0ae5a21c=QBoi_nominal_chpPla_0ae5a21c/(4200*chpPla_0ae5a21c.delT_nominal)
    "Nominal heating water mass flow rate";
  parameter Modelica.Units.SI.Power QBoi_nominal_chpPla_0ae5a21c=Q_flow_nominal_chpPla_0ae5a21c/chpPla_0ae5a21c.numBoi
    "Nominal heating capaciaty";
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_chpPla_0ae5a21c=1000000*2
    "Heating load";
  parameter Modelica.Units.SI.MassFlowRate mMin_flow_chpPla_0ae5a21c=0.2*mBoi_flow_nominal_chpPla_0ae5a21c
    "Minimum mass flow rate of single boiler";
  // controls
  parameter Modelica.Units.SI.Pressure pumDP=(chpPla_0ae5a21c.dpBoi_nominal+dpSetPoi_disNet_b3d86b1a+50000)
    "Heating water pump pressure drop";
  parameter Modelica.Units.SI.Time tWai_chpPla_0ae5a21c=30
    "Waiting time";
  parameter Buildings.Fluid.Movers.Data.Generic perHWPum_chpPla_0ae5a21c(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=mBoi_flow_nominal_chpPla_0ae5a21c/1000*{0.1,1.1},
      dp=pumDP*{1.1,0.1}))
    "Performance data for heating water pumps";

  heat_with_chp.Plants.CentralHeatingPlant chpPla_0ae5a21c(
    perHWPum=perHWPum_chpPla_0ae5a21c,
    mHW_flow_nominal=mHW_flow_nominal_chpPla_0ae5a21c,
    QBoi_flow_nominal=QBoi_nominal_chpPla_0ae5a21c,
    mMin_flow=mMin_flow_chpPla_0ae5a21c,
    mBoi_flow_nominal=mBoi_flow_nominal_chpPla_0ae5a21c,
    dpBoi_nominal=10000,
    delT_nominal(
      displayUnit="degC")=15,
    tWai=tWai_chpPla_0ae5a21c,
    // TODO: we're currently grabbing dpSetPoi from the Network instance -- need feedback to determine if that's the proper "home" for it
    dpSetPoi=dpSetPoi_disNet_b3d86b1a
    )
    "District heating plant."
    annotation (Placement(transformation(extent={{-70.0,70.0},{-50.0,90.0}})));
  //
  // End Model Instance for chpPla_0ae5a21c
  //


  
  //
  // Begin Model Instance for TimeSerLoa_9024af11
  // Source template: /model_connectors/load_connectors/templates/TimeSeries_Instance.mopt
  //
  // time series load
  heat_with_chp.Loads.B5a6b99ec37f4de7f94020090.TimeSeriesBuilding TimeSerLoa_9024af11(
    
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
  // End Model Instance for TimeSerLoa_9024af11
  //


  
  //
  // Begin Model Instance for heaInd_0f7bb650
  // Source template: /model_connectors/energy_transfer_systems/templates/HeatingIndirect_Instance.mopt
  //
  // heating indirect instance
  heat_with_chp.Substations.HeatingIndirect_5a6b99ec37f4de7f94020090 heaInd_0f7bb650(
    allowFlowReversal1=true,
    allowFlowReversal2=true,
    show_T=true,
    redeclare package Medium=MediumW,
    mDis_flow_nominal=mDis_flow_nominal_6be694df,
    mBui_flow_nominal=mBui_flow_nominal_6be694df,
    dpValve_nominal=6000,
    dp1_nominal=500,
    dp2_nominal=500,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_6be694df,
    T_a1_nominal=55+273.15,
    T_a2_nominal=35+273.15,
    k=0.1,
    Ti=60,
    reverseActing=true)
    annotation (Placement(transformation(extent={{10.0,70.0},{30.0,90.0}})));
  //
  // End Model Instance for heaInd_0f7bb650
  //


  
  //
  // Begin Model Instance for etsColWatStub_89ee5ba9
  // Source template: /model_connectors/energy_transfer_systems/templates/EtsColdWaterStub_Instance.mopt
  //
  // TODO: move these components into a single component
  Buildings.Fluid.Sources.Boundary_pT supChiWat_etsColWatStub_89ee5ba9(
    redeclare package Medium=MediumW,
    use_T_in=true,
    nPorts=1)
    "Chilled water supply"
    annotation (Placement(transformation(extent={{-70.0,-90.0},{-50.0,-70.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinChiWat_etsColWatStub_89ee5ba9(
    redeclare package Medium=MediumW,
    nPorts=1)
    "Chilled water sink"
    annotation (Placement(transformation(extent={{-30.0,-90.0},{-10.0,-70.0}})));
  //
  // End Model Instance for etsColWatStub_89ee5ba9
  //


  
  //
  // Begin Model Instance for TimeSerLoa_a93a5f30
  // Source template: /model_connectors/load_connectors/templates/TimeSeries_Instance.mopt
  //
  // time series load
  heat_with_chp.Loads.abcdefghijklmnopqrstuvwx.TimeSeriesBuilding TimeSerLoa_a93a5f30(
    
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
  // End Model Instance for TimeSerLoa_a93a5f30
  //


  
  //
  // Begin Model Instance for heaInd_b40e7a31
  // Source template: /model_connectors/energy_transfer_systems/templates/HeatingIndirect_Instance.mopt
  //
  // heating indirect instance
  heat_with_chp.Substations.HeatingIndirect_abcdefghijklmnopqrstuvwx heaInd_b40e7a31(
    allowFlowReversal1=true,
    allowFlowReversal2=true,
    show_T=true,
    redeclare package Medium=MediumW,
    mDis_flow_nominal=mDis_flow_nominal_18924604,
    mBui_flow_nominal=mBui_flow_nominal_18924604,
    dpValve_nominal=6000,
    dp1_nominal=500,
    dp2_nominal=500,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_18924604,
    T_a1_nominal=55+273.15,
    T_a2_nominal=35+273.15,
    k=0.1,
    Ti=60,
    reverseActing=true)
    annotation (Placement(transformation(extent={{10.0,30.0},{30.0,50.0}})));
  //
  // End Model Instance for heaInd_b40e7a31
  //


  
  //
  // Begin Model Instance for etsColWatStub_dfc050f9
  // Source template: /model_connectors/energy_transfer_systems/templates/EtsColdWaterStub_Instance.mopt
  //
  // TODO: move these components into a single component
  Buildings.Fluid.Sources.Boundary_pT supChiWat_etsColWatStub_dfc050f9(
    redeclare package Medium=MediumW,
    use_T_in=true,
    nPorts=1)
    "Chilled water supply"
    annotation (Placement(transformation(extent={{10.0,-90.0},{30.0,-70.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinChiWat_etsColWatStub_dfc050f9(
    redeclare package Medium=MediumW,
    nPorts=1)
    "Chilled water sink"
    annotation (Placement(transformation(extent={{50.0,-90.0},{70.0,-70.0}})));
  //
  // End Model Instance for etsColWatStub_dfc050f9
  //


  

  // Model dependencies

  //
  // Begin Component Definitions for 1fd2498e
  // Source template: /model_connectors/couplings/templates/Network2Pipe_HeatingPlant/ComponentDefinitions.mopt
  //
  // TODO: This should not be here, it is entirely plant specific and should be moved elsewhere
  // but since it requires a connect statement we must put it here for now...
  Modelica.Blocks.Sources.BooleanConstant mPum_flow_1fd2498e(
    k=true)
    "Total heating water pump mass flow rate"
    annotation (Placement(transformation(extent={{-70.0,-10.0},{-50.0,10.0}})));
  // TODO: This should not be here, it is entirely plant specific and should be moved elsewhere
  // but since it requires a connect statement we must put it here for now...
  Modelica.Blocks.Sources.RealExpression TDisSetHeaWat_1fd2498e(
    each y=273.15+68)
    "District side heating water supply temperature set point."
    annotation (Placement(transformation(extent={{-30.0,-10.0},{-10.0,10.0}})));

  //
  // End Component Definitions for 1fd2498e
  //



  //
  // Begin Component Definitions for 6be694df
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ComponentDefinitions.mopt
  //
  // TimeSeries + HeatingIndirect Component Definitions
  // TODO: the components below need to be fixed!
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_6be694df=TimeSerLoa_9024af11.mHeaWat_flow_nominal*delHeaWatTemBui/delHeaWatTemDis
    "Nominal mass flow rate of primary (district) district heating side";
  parameter Modelica.Units.SI.MassFlowRate mBui_flow_nominal_6be694df=TimeSerLoa_9024af11.mHeaWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district heating side";
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_6be694df=(TimeSerLoa_9024af11.QHea_flow_nominal);
  Modelica.Fluid.Sources.FixedBoundary pressure_source_6be694df(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{10.0,-10.0},{30.0,10.0}})));
  // TODO: move THeaWatSet (and its connection) into a HeatingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression THeaWatSet_6be694df(
    // y=40+273.15)
    y=273.15+40 )
    "Secondary loop (Building side) heating water setpoint temperature."
    //Dehardcode
    annotation (Placement(transformation(extent={{50.0,-10.0},{70.0,10.0}})));

  //
  // End Component Definitions for 6be694df
  //



  //
  // Begin Component Definitions for 74bbfd17
  // Source template: /model_connectors/couplings/templates/TimeSeries_EtsColdWaterStub/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression TChiWatSup_74bbfd17(
    y=TimeSerLoa_9024af11.T_aChiWat_nominal)
    "Chilled water supply temperature"
    annotation (Placement(transformation(extent={{-70.0,-50.0},{-50.0,-30.0}})));

  //
  // End Component Definitions for 74bbfd17
  //



  //
  // Begin Component Definitions for 76b7586b
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for heating indirect and network 2 pipe

  //
  // End Component Definitions for 76b7586b
  //



  //
  // Begin Component Definitions for 18924604
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ComponentDefinitions.mopt
  //
  // TimeSeries + HeatingIndirect Component Definitions
  // TODO: the components below need to be fixed!
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_18924604=TimeSerLoa_a93a5f30.mHeaWat_flow_nominal*delHeaWatTemBui/delHeaWatTemDis
    "Nominal mass flow rate of primary (district) district heating side";
  parameter Modelica.Units.SI.MassFlowRate mBui_flow_nominal_18924604=TimeSerLoa_a93a5f30.mHeaWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district heating side";
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_18924604=(TimeSerLoa_a93a5f30.QHea_flow_nominal);
  Modelica.Fluid.Sources.FixedBoundary pressure_source_18924604(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{-30.0,-50.0},{-10.0,-30.0}})));
  // TODO: move THeaWatSet (and its connection) into a HeatingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression THeaWatSet_18924604(
    // y=40+273.15)
    y=273.15+40 )
    "Secondary loop (Building side) heating water setpoint temperature."
    //Dehardcode
    annotation (Placement(transformation(extent={{10.0,-50.0},{30.0,-30.0}})));

  //
  // End Component Definitions for 18924604
  //



  //
  // Begin Component Definitions for 65d5b540
  // Source template: /model_connectors/couplings/templates/TimeSeries_EtsColdWaterStub/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression TChiWatSup_65d5b540(
    y=TimeSerLoa_a93a5f30.T_aChiWat_nominal)
    "Chilled water supply temperature"
    annotation (Placement(transformation(extent={{50.0,-50.0},{70.0,-30.0}})));

  //
  // End Component Definitions for 65d5b540
  //



  //
  // Begin Component Definitions for aa80b052
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for heating indirect and network 2 pipe

  //
  // End Component Definitions for aa80b052
  //



equation
  // Connections

  //
  // Begin Connect Statements for 1fd2498e
  // Source template: /model_connectors/couplings/templates/Network2Pipe_HeatingPlant/ConnectStatements.mopt
  //

  connect(chpPla_0ae5a21c.port_a,disNet_b3d86b1a.port_bDisRet)
    annotation (Line(points={{-30.262668513897594,85.98900322685623},{-10.262668513897594,85.98900322685623}},color={0,0,127}));
  connect(disNet_b3d86b1a.dp,chpPla_0ae5a21c.dpMea)
    annotation (Line(points={{-46.59070874874158,80.44681511591389},{-66.59070874874158,80.44681511591389}},color={0,0,127}));
  connect(chpPla_0ae5a21c.port_b,disNet_b3d86b1a.port_aDisSup)
    annotation (Line(points={{-39.10601714867294,85.69074546061847},{-19.106017148672947,85.69074546061847}},color={0,0,127}));
  connect(mPum_flow_1fd2498e.y,chpPla_0ae5a21c.on)
    annotation (Line(points={{-62.194550690500364,11.22825805122379},{-62.194550690500364,31.22825805122379},{-62.194550690500364,51.22825805122379},{-62.194550690500364,71.22825805122379}},color={0,0,127}));
  connect(TDisSetHeaWat_1fd2498e.y,chpPla_0ae5a21c.THeaSet)
    annotation (Line(points={{-11.84569208360682,17.312643873686625},{-11.84569208360682,37.312643873686625},{-11.84569208360682,57.312643873686625},{-31.84569208360682,57.312643873686625},{-31.84569208360682,77.31264387368662},{-51.84569208360682,77.31264387368662}},color={0,0,127}));

  //
  // End Connect Statements for 1fd2498e
  //



  //
  // Begin Connect Statements for 6be694df
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ConnectStatements.mopt
  //

  // heating indirect, timeseries coupling connections
  connect(TimeSerLoa_9024af11.ports_bHeaWat[1], heaInd_0f7bb650.port_a2)
    annotation (Line(points={{39.85153231428572,77.10168072273918},{19.85153231428572,77.10168072273918}},color={0,0,127}));
  connect(heaInd_0f7bb650.port_b2,TimeSerLoa_9024af11.ports_aHeaWat[1])
    annotation (Line(points={{48.52982797783676,78.99243774804975},{68.52982797783676,78.99243774804975}},color={0,0,127}));
  connect(pressure_source_6be694df.ports[1], heaInd_0f7bb650.port_b2)
    annotation (Line(points={{14.993255783928518,20.583121847307723},{-5.006744216071482,20.583121847307723},{-5.006744216071482,40.58312184730772},{-5.006744216071482,60.58312184730772},{-5.006744216071482,80.58312184730772},{14.993255783928518,80.58312184730772}},color={0,0,127}));
  connect(THeaWatSet_6be694df.y,heaInd_0f7bb650.TSetBuiSup)
    annotation (Line(points={{59.83914272660755,13.037276918771525},{39.83914272660755,13.037276918771525},{39.83914272660755,33.037276918771525},{39.83914272660755,53.037276918771525},{39.83914272660755,73.03727691877152},{19.839142726607548,73.03727691877152}},color={0,0,127}));

  //
  // End Connect Statements for 6be694df
  //



  //
  // Begin Connect Statements for 74bbfd17
  // Source template: /model_connectors/couplings/templates/TimeSeries_EtsColdWaterStub/ConnectStatements.mopt
  //

  // time series, ets cold water stub connections
  connect(TChiWatSup_74bbfd17.y,supChiWat_etsColWatStub_89ee5ba9.T_in)
    annotation (Line(points={{-58.11383130976702,-58.43376008311034},{-58.11383130976702,-78.43376008311034}},color={0,0,127}));
  connect(TimeSerLoa_9024af11.ports_bChiWat[1],sinChiWat_etsColWatStub_89ee5ba9.ports[1])
    annotation (Line(points={{54.45232955738953,65.41084095413467},{34.45232955738955,65.41084095413467},{34.45232955738955,45.410840954134684},{34.45232955738955,25.410840954134684},{34.45232955738955,5.4108409541346845},{34.45232955738955,-14.589159045865316},{34.45232955738955,-34.58915904586533},{34.45232955738955,-54.58915904586533},{14.452329557389547,-54.58915904586533},{-5.547670442610453,-54.58915904586533},{-5.547670442610453,-74.58915904586533},{-25.547670442610453,-74.58915904586533}},color={0,0,127}));
  connect(supChiWat_etsColWatStub_89ee5ba9.ports[1],TimeSerLoa_9024af11.ports_aChiWat[1])
    annotation (Line(points={{-67.16018175705042,-50.23236779896985},{-47.160181757050424,-50.23236779896985},{-47.160181757050424,-30.232367798969847},{-47.160181757050424,-10.232367798969847},{-47.160181757050424,9.767632201030153},{-47.160181757050424,29.767632201030153},{-47.160181757050424,49.76763220103016},{-47.160181757050424,69.76763220103015},{-27.160181757050424,69.76763220103015},{-7.160181757050424,69.76763220103015},{12.839818242949576,69.76763220103015},{32.839818242949576,69.76763220103015},{32.839818242949576,89.76763220103015},{52.839818242949576,89.76763220103015}},color={0,0,127}));

  //
  // End Connect Statements for 74bbfd17
  //



  //
  // Begin Connect Statements for 76b7586b
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // heating indirect and network 2 pipe
  
  connect(disNet_b3d86b1a.ports_bCon[1],heaInd_0f7bb650.port_a1)
    annotation (Line(points={{2.1417570179701357,77.65854358336676},{22.141757017970136,77.65854358336676}},color={0,0,127}));
  connect(disNet_b3d86b1a.ports_aCon[1],heaInd_0f7bb650.port_b1)
    annotation (Line(points={{-9.179096703355953,70.36395188972415},{10.820903296644047,70.36395188972415}},color={0,0,127}));

  //
  // End Connect Statements for 76b7586b
  //



  //
  // Begin Connect Statements for 18924604
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ConnectStatements.mopt
  //

  // heating indirect, timeseries coupling connections
  connect(TimeSerLoa_a93a5f30.ports_bHeaWat[1], heaInd_b40e7a31.port_a2)
    annotation (Line(points={{32.18323934683694,37.37958247748348},{12.183239346836942,37.37958247748348}},color={0,0,127}));
  connect(heaInd_b40e7a31.port_b2,TimeSerLoa_a93a5f30.ports_aHeaWat[1])
    annotation (Line(points={{31.149534753283703,32.750713229014806},{51.14953475328369,32.750713229014806}},color={0,0,127}));
  connect(pressure_source_18924604.ports[1], heaInd_b40e7a31.port_b2)
    annotation (Line(points={{-13.821368461976064,-14.12804598781689},{6.178631538023936,-14.12804598781689},{6.178631538023936,5.87195401218311},{6.178631538023936,25.87195401218311},{6.178631538023936,45.87195401218311},{26.178631538023936,45.87195401218311}},color={0,0,127}));
  connect(THeaWatSet_18924604.y,heaInd_b40e7a31.TSetBuiSup)
    annotation (Line(points={{13.999973035029583,-13.193038555395248},{-6.0000269649704165,-13.193038555395248},{-6.0000269649704165,6.806961444604752},{-6.0000269649704165,26.806961444604752},{-6.0000269649704165,46.80696144460475},{13.999973035029583,46.80696144460475}},color={0,0,127}));

  //
  // End Connect Statements for 18924604
  //



  //
  // Begin Connect Statements for 65d5b540
  // Source template: /model_connectors/couplings/templates/TimeSeries_EtsColdWaterStub/ConnectStatements.mopt
  //

  // time series, ets cold water stub connections
  connect(TChiWatSup_65d5b540.y,supChiWat_etsColWatStub_dfc050f9.T_in)
    annotation (Line(points={{54.86331630183193,-60.295236690745355},{34.863316301831915,-60.295236690745355},{34.863316301831915,-80.29523669074536},{14.863316301831915,-80.29523669074536}},color={0,0,127}));
  connect(TimeSerLoa_a93a5f30.ports_bChiWat[1],sinChiWat_etsColWatStub_dfc050f9.ports[1])
    annotation (Line(points={{69.77068463801896,27.780800842875863},{49.77068463801896,27.780800842875863},{49.77068463801896,7.780800842875863},{49.77068463801896,-12.219199157124137},{49.77068463801896,-32.21919915712414},{49.77068463801896,-52.21919915712414},{49.77068463801896,-72.21919915712414},{69.77068463801896,-72.21919915712414}},color={0,0,127}));
  connect(supChiWat_etsColWatStub_dfc050f9.ports[1],TimeSerLoa_a93a5f30.ports_aChiWat[1])
    annotation (Line(points={{15.538806143682152,-51.345383598999774},{35.53880614368215,-51.345383598999774},{35.53880614368215,-31.345383598999774},{35.53880614368215,-11.345383598999774},{35.53880614368215,8.654616401000226},{35.53880614368215,28.654616401000226},{35.53880614368215,48.654616401000226},{55.53880614368214,48.654616401000226}},color={0,0,127}));

  //
  // End Connect Statements for 65d5b540
  //



  //
  // Begin Connect Statements for aa80b052
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // heating indirect and network 2 pipe
  
  connect(disNet_b3d86b1a.ports_bCon[2],heaInd_b40e7a31.port_a1)
    annotation (Line(points={{-12.374268558036064,55.550016175272035},{-12.374268558036064,35.550016175272035},{7.625731441963936,35.550016175272035},{27.625731441963936,35.550016175272035}},color={0,0,127}));
  connect(disNet_b3d86b1a.ports_aCon[2],heaInd_b40e7a31.port_b1)
    annotation (Line(points={{-22.074232051343827,54.14292099397545},{-22.074232051343827,34.14292099397545},{-2.0742320513438273,34.14292099397545},{17.925767948656173,34.14292099397545}},color={0,0,127}));

  //
  // End Connect Statements for aa80b052
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