within heat_with_chp.Districts;
model DistrictEnergySystem
  extends Modelica.Icons.Example;
  // District Parameters
  package MediumW=Buildings.Media.Water
    "Source side medium";
  package MediumA=Buildings.Media.Air
    "Load side medium";

  // TODO: dehardcode? Also, add display units to the other parameters.
  parameter Modelica.SIunits.TemperatureDifference delChiWatTemDis(displayUnit="degC")=7;
  parameter Modelica.SIunits.TemperatureDifference delChiWatTemBui=5;
  parameter Modelica.SIunits.TemperatureDifference delHeaWatTemDis=12;
  parameter Modelica.SIunits.TemperatureDifference delHeaWatTemBui=5;

  // Models

  //
  // Begin Model Instance for disNet_5bbe332c
  // Source template: /model_connectors/networks/templates/Network2Pipe_Instance.mopt
  //
parameter Integer nBui_disNet_5bbe332c=2;
  parameter Modelica.SIunits.MassFlowRate mDis_flow_nominal_disNet_5bbe332c=sum({
    heaInd_d4b58520.mDis_flow_nominal,
  heaInd_1bf72ed9.mDis_flow_nominal})
    "Nominal mass flow rate of the distribution pump";
  parameter Modelica.SIunits.MassFlowRate mCon_flow_nominal_disNet_5bbe332c[nBui_disNet_5bbe332c]={
    heaInd_d4b58520.mDis_flow_nominal,
  heaInd_1bf72ed9.mDis_flow_nominal}
    "Nominal mass flow rate in each connection line";
  parameter Modelica.SIunits.PressureDifference dpDis_nominal_disNet_5bbe332c[nBui_disNet_5bbe332c](
    each min=0,
    each displayUnit="Pa")=1/2 .* cat(
    1,
    {dp_nominal_disNet_5bbe332c*0.1},
    fill(
      dp_nominal_disNet_5bbe332c*0.9/(nBui_disNet_5bbe332c-1),
      nBui_disNet_5bbe332c-1))
    "Pressure drop between each connected building at nominal conditions (supply line)";
  parameter Modelica.SIunits.PressureDifference dp_nominal_disNet_5bbe332c=dpSetPoi_disNet_5bbe332c+nBui_disNet_5bbe332c*7000
    "District network pressure drop";
  // NOTE: this differential pressure setpoint is currently utilized by plants elsewhere
  parameter Modelica.SIunits.Pressure dpSetPoi_disNet_5bbe332c=50000
    "Differential pressure setpoint";

  Buildings.Experimental.DHC.Loads.Validation.BaseClasses.Distribution2Pipe disNet_5bbe332c(
    redeclare final package Medium=MediumW,
    final nCon=nBui_disNet_5bbe332c,
    iConDpSen=nBui_disNet_5bbe332c,
    final mDis_flow_nominal=mDis_flow_nominal_disNet_5bbe332c,
    final mCon_flow_nominal=mCon_flow_nominal_disNet_5bbe332c,
    final allowFlowReversal=false,
    dpDis_nominal=dpDis_nominal_disNet_5bbe332c)
    "Distribution network."
    annotation (Placement(transformation(extent={{-30.0,80.0},{-10.0,90.0}})));
  //
  // End Model Instance for disNet_5bbe332c
  //


  
  //
  // Begin Model Instance for chpPla_05ef8e4f
  // Source template: /model_connectors/plants/templates/HeatingPlant_Instance.mopt
  //
  // heating plant instance
  parameter Modelica.SIunits.MassFlowRate mHW_flow_nominal_chpPla_05ef8e4f=mBoi_flow_nominal_chpPla_05ef8e4f*chpPla_05ef8e4f.numBoi
    "Nominal heating water mass flow rate";
  parameter Modelica.SIunits.MassFlowRate mBoi_flow_nominal_chpPla_05ef8e4f=QBoi_nominal_chpPla_05ef8e4f/(4200*chpPla_05ef8e4f.delT_nominal)
    "Nominal heating water mass flow rate";
  parameter Modelica.SIunits.Power QBoi_nominal_chpPla_05ef8e4f=Q_flow_nominal_chpPla_05ef8e4f/chpPla_05ef8e4f.numBoi
    "Nominal heating capaciaty";
  parameter Modelica.SIunits.HeatFlowRate Q_flow_nominal_chpPla_05ef8e4f=1000000*2
    "Heating load";
  parameter Modelica.SIunits.MassFlowRate mMin_flow_chpPla_05ef8e4f=0.2*mBoi_flow_nominal_chpPla_05ef8e4f
    "Minimum mass flow rate of single boiler";
  // controls
  parameter Modelica.SIunits.Pressure pumDP=(chpPla_05ef8e4f.dpBoi_nominal+dpSetPoi_disNet_5bbe332c+50000)
    "Heating water pump pressure drop";
  parameter Modelica.SIunits.Time tWai_chpPla_05ef8e4f=30
    "Waiting time";
  parameter Buildings.Fluid.Movers.Data.Generic perHWPum_chpPla_05ef8e4f(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=mBoi_flow_nominal_chpPla_05ef8e4f/1000*{0.1,1.1},
      dp=pumDP*{1.1,0.1}))
    "Performance data for heating water pumps";

  heat_with_chp.Plants.CentralHeatingPlant chpPla_05ef8e4f(
    perHWPum=perHWPum_chpPla_05ef8e4f,
    mHW_flow_nominal=mHW_flow_nominal_chpPla_05ef8e4f,
    QBoi_flow_nominal=QBoi_nominal_chpPla_05ef8e4f,
    mMin_flow=mMin_flow_chpPla_05ef8e4f,
    mBoi_flow_nominal=mBoi_flow_nominal_chpPla_05ef8e4f,
    dpBoi_nominal=10000,
    delT_nominal(
      displayUnit="degC")=15,
    tWai=tWai_chpPla_05ef8e4f,
    // TODO: we're currently grabbing dpSetPoi from the Network instance -- need feedback to determine if that's the proper "home" for it
    dpSetPoi=dpSetPoi_disNet_5bbe332c,
    energyDynamics=Modelica.Fluid.Types.Dynamics.FixedInitial)
    "District heating plant."
    annotation (Placement(transformation(extent={{-70.0,70.0},{-50.0,90.0}})));
  //
  // End Model Instance for chpPla_05ef8e4f
  //


  
  //
  // Begin Model Instance for TimeSerLoa_66524701
  // Source template: /model_connectors/load_connectors/templates/TimeSeries_Instance.mopt
  //
  // time series load
  heat_with_chp.Loads.B5a6b99ec37f4de7f94020090.building TimeSerLoa_66524701(
    T_aHeaWat_nominal=318.15,
    T_aChiWat_nominal=280.15,
    delTAirCoo(displayUnit="degC")=10,
    delTAirHea(displayUnit="degC")=20,
    k=0.1,
    Ti=120,
    nPorts_bChiWat=1,
    nPorts_aChiWat=1,
    nPorts_bHeaWat=1,
    nPorts_aHeaWat=1)
    "Building model integrating multiple time series thermal zones."
    annotation (Placement(transformation(extent={{50.0,70.0},{70.0,90.0}})));
  //
  // End Model Instance for TimeSerLoa_66524701
  //


  
  //
  // Begin Model Instance for heaInd_d4b58520
  // Source template: /model_connectors/energy_transfer_systems/templates/HeatingIndirect_Instance.mopt
  //
  // heating indirect instance
  heat_with_chp.Substations.HeatingIndirect_5a6b99ec37f4de7f94020090 heaInd_d4b58520(
    allowFlowReversal1=false,
    allowFlowReversal2=false,
    show_T=true,
    redeclare package Medium=MediumW,
    mDis_flow_nominal=mDis_flow_nominal_0b539951,
    mBui_flow_nominal=mBui_flow_nominal_0b539951,
    dpValve_nominal=6000,
    dp1_nominal=500,
    dp2_nominal=500,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_0b539951,
    T_a1_nominal=55+273.15,
    T_a2_nominal=35+273.15,
    k=0.1,
    Ti=60,
    reverseActing=true)
    annotation (Placement(transformation(extent={{10.0,70.0},{30.0,90.0}})));
  //
  // End Model Instance for heaInd_d4b58520
  //


  
  //
  // Begin Model Instance for etsColWatStub_96c8e9a6
  // Source template: /model_connectors/energy_transfer_systems/templates/EtsColdWaterStub_Instance.mopt
  //
  // TODO: move these components into a single component
  Buildings.Fluid.Sources.Boundary_pT supChiWat_etsColWatStub_96c8e9a6(
    redeclare package Medium=MediumW,
    use_T_in=true,
    nPorts=1)
    "Chilled water supply"
    annotation (Placement(transformation(extent={{-70.0,-90.0},{-50.0,-70.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinChiWat_etsColWatStub_96c8e9a6(
    redeclare package Medium=MediumW,
    nPorts=1)
    "Chilled water sink"
    annotation (Placement(transformation(extent={{-30.0,-90.0},{-10.0,-70.0}})));
  //
  // End Model Instance for etsColWatStub_96c8e9a6
  //


  
  //
  // Begin Model Instance for TimeSerLoa_b444ff7a
  // Source template: /model_connectors/load_connectors/templates/TimeSeries_Instance.mopt
  //
  // time series load
  heat_with_chp.Loads.abcdefghijklmnopqrstuvwx.building TimeSerLoa_b444ff7a(
    T_aHeaWat_nominal=318.15,
    T_aChiWat_nominal=280.15,
    delTAirCoo(displayUnit="degC")=10,
    delTAirHea(displayUnit="degC")=20,
    k=0.1,
    Ti=120,
    nPorts_bChiWat=1,
    nPorts_aChiWat=1,
    nPorts_bHeaWat=1,
    nPorts_aHeaWat=1)
    "Building model integrating multiple time series thermal zones."
    annotation (Placement(transformation(extent={{50.0,30.0},{70.0,50.0}})));
  //
  // End Model Instance for TimeSerLoa_b444ff7a
  //


  
  //
  // Begin Model Instance for heaInd_1bf72ed9
  // Source template: /model_connectors/energy_transfer_systems/templates/HeatingIndirect_Instance.mopt
  //
  // heating indirect instance
  heat_with_chp.Substations.HeatingIndirect_abcdefghijklmnopqrstuvwx heaInd_1bf72ed9(
    allowFlowReversal1=false,
    allowFlowReversal2=false,
    show_T=true,
    redeclare package Medium=MediumW,
    mDis_flow_nominal=mDis_flow_nominal_1049ec1c,
    mBui_flow_nominal=mBui_flow_nominal_1049ec1c,
    dpValve_nominal=6000,
    dp1_nominal=500,
    dp2_nominal=500,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_1049ec1c,
    T_a1_nominal=55+273.15,
    T_a2_nominal=35+273.15,
    k=0.1,
    Ti=60,
    reverseActing=true)
    annotation (Placement(transformation(extent={{10.0,30.0},{30.0,50.0}})));
  //
  // End Model Instance for heaInd_1bf72ed9
  //


  
  //
  // Begin Model Instance for etsColWatStub_2740267d
  // Source template: /model_connectors/energy_transfer_systems/templates/EtsColdWaterStub_Instance.mopt
  //
  // TODO: move these components into a single component
  Buildings.Fluid.Sources.Boundary_pT supChiWat_etsColWatStub_2740267d(
    redeclare package Medium=MediumW,
    use_T_in=true,
    nPorts=1)
    "Chilled water supply"
    annotation (Placement(transformation(extent={{10.0,-90.0},{30.0,-70.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinChiWat_etsColWatStub_2740267d(
    redeclare package Medium=MediumW,
    nPorts=1)
    "Chilled water sink"
    annotation (Placement(transformation(extent={{50.0,-90.0},{70.0,-70.0}})));
  //
  // End Model Instance for etsColWatStub_2740267d
  //


  

  // Model dependencies

  //
  // Begin Component Definitions for 240edb90
  // Source template: /model_connectors/couplings/templates/Network2Pipe_HeatingPlant/ComponentDefinitions.mopt
  //
  // TODO: This should not be here, it is entirely plant specific and should be moved elsewhere
  // but since it requires a connect statement we must put it here for now...
  Modelica.Blocks.Sources.BooleanConstant mPum_flow_240edb90(
    k=true)
    "Total heating water pump mass flow rate"
    annotation (Placement(transformation(extent={{-70.0,-10.0},{-50.0,10.0}})));
  // TODO: This should not be here, it is entirely plant specific and should be moved elsewhere
  // but since it requires a connect statement we must put it here for now...
  Modelica.Blocks.Sources.RealExpression TDisSetHeaWat_240edb90(
    each y=55+273.15)
    "Distrcit side heating water supply temperature set point."
    annotation (Placement(transformation(extent={{-30.0,-10.0},{-10.0,10.0}})));

  //
  // End Component Definitions for 240edb90
  //



  //
  // Begin Component Definitions for 0b539951
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ComponentDefinitions.mopt
  //
  // TimeSeries + HeatingIndirect Component Definitions
  // TODO: the components below need to be fixed!
  parameter Modelica.SIunits.MassFlowRate mDis_flow_nominal_0b539951=TimeSerLoa_66524701.mHeaWat_flow_nominal*delHeaWatTemBui/delHeaWatTemDis
    "Nominal mass flow rate of primary (district) district heating side";
  parameter Modelica.SIunits.MassFlowRate mBui_flow_nominal_0b539951=TimeSerLoa_66524701.mHeaWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district heating side";
  parameter Modelica.SIunits.HeatFlowRate Q_flow_nominal_0b539951=(TimeSerLoa_66524701.QHea_flow_nominal);
  Modelica.Fluid.Sources.FixedBoundary pressure_source_0b539951(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{10.0,-10.0},{30.0,10.0}})));
  // TODO: move THeaWatSet (and its connection) into a HeatingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression THeaWatSet_0b539951(
    y=40+273.15)
    "Secondary loop (Building side) heating water setpoint temperature."
    //Dehardcode
    annotation (Placement(transformation(extent={{50.0,-10.0},{70.0,10.0}})));

  //
  // End Component Definitions for 0b539951
  //



  //
  // Begin Component Definitions for 1e7a4aae
  // Source template: /model_connectors/couplings/templates/TimeSeries_EtsColdWaterStub/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression TChiWatSup_1e7a4aae(
    y=TimeSerLoa_66524701.T_aChiWat_nominal)
    "Chilled water supply temperature"
    annotation (Placement(transformation(extent={{-70.0,-50.0},{-50.0,-30.0}})));

  //
  // End Component Definitions for 1e7a4aae
  //



  //
  // Begin Component Definitions for 99a3ec39
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for heating indirect and network 2 pipe

  //
  // End Component Definitions for 99a3ec39
  //



  //
  // Begin Component Definitions for 1049ec1c
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ComponentDefinitions.mopt
  //
  // TimeSeries + HeatingIndirect Component Definitions
  // TODO: the components below need to be fixed!
  parameter Modelica.SIunits.MassFlowRate mDis_flow_nominal_1049ec1c=TimeSerLoa_b444ff7a.mHeaWat_flow_nominal*delHeaWatTemBui/delHeaWatTemDis
    "Nominal mass flow rate of primary (district) district heating side";
  parameter Modelica.SIunits.MassFlowRate mBui_flow_nominal_1049ec1c=TimeSerLoa_b444ff7a.mHeaWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district heating side";
  parameter Modelica.SIunits.HeatFlowRate Q_flow_nominal_1049ec1c=(TimeSerLoa_b444ff7a.QHea_flow_nominal);
  Modelica.Fluid.Sources.FixedBoundary pressure_source_1049ec1c(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{-30.0,-50.0},{-10.0,-30.0}})));
  // TODO: move THeaWatSet (and its connection) into a HeatingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression THeaWatSet_1049ec1c(
    y=40+273.15)
    "Secondary loop (Building side) heating water setpoint temperature."
    //Dehardcode
    annotation (Placement(transformation(extent={{10.0,-50.0},{30.0,-30.0}})));

  //
  // End Component Definitions for 1049ec1c
  //



  //
  // Begin Component Definitions for a89eacd7
  // Source template: /model_connectors/couplings/templates/TimeSeries_EtsColdWaterStub/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression TChiWatSup_a89eacd7(
    y=TimeSerLoa_b444ff7a.T_aChiWat_nominal)
    "Chilled water supply temperature"
    annotation (Placement(transformation(extent={{50.0,-50.0},{70.0,-30.0}})));

  //
  // End Component Definitions for a89eacd7
  //



  //
  // Begin Component Definitions for a03177dd
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for heating indirect and network 2 pipe

  //
  // End Component Definitions for a03177dd
  //



equation
  // Connections

  //
  // Begin Connect Statements for 240edb90
  // Source template: /model_connectors/couplings/templates/Network2Pipe_HeatingPlant/ConnectStatements.mopt
  //

  connect(chpPla_05ef8e4f.port_a,disNet_5bbe332c.port_bDisRet)
    annotation (Line(points={{-32.36323306361828,82.49682974819191},{-12.363233063618281,82.49682974819191}},color={0,0,127}));
  connect(disNet_5bbe332c.dp,chpPla_05ef8e4f.dpMea)
    annotation (Line(points={{-31.18631204153577,71.30968877047567},{-51.18631204153577,71.30968877047567}},color={0,0,127}));
  connect(chpPla_05ef8e4f.port_b,disNet_5bbe332c.port_aDisSup)
    annotation (Line(points={{-39.975771183059834,77.97517961059705},{-19.975771183059834,77.97517961059705}},color={0,0,127}));
  connect(mPum_flow_240edb90.y,chpPla_05ef8e4f.on)
    annotation (Line(points={{-56.31535427908298,28.0953363300346},{-56.31535427908298,48.0953363300346},{-56.31535427908298,68.0953363300346},{-56.31535427908298,88.0953363300346}},color={0,0,127}));
  connect(TDisSetHeaWat_240edb90.y,chpPla_05ef8e4f.THeaSet)
    annotation (Line(points={{-17.446761413629943,15.023906605706273},{-17.446761413629943,35.02390660570627},{-17.446761413629943,55.02390660570628},{-37.44676141362994,55.02390660570628},{-37.44676141362994,75.02390660570629},{-57.44676141362994,75.02390660570629}},color={0,0,127}));

  //
  // End Connect Statements for 240edb90
  //



  //
  // Begin Connect Statements for 0b539951
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ConnectStatements.mopt
  //

  // cooling indirect, timeseries coupling connections
  connect(TimeSerLoa_66524701.ports_bHeaWat[1], heaInd_d4b58520.port_a2)
    annotation (Line(points={{44.078064117550184,85.57550412828238},{24.0780641175502,85.57550412828238}},color={0,0,127}));
  connect(heaInd_d4b58520.port_b2,TimeSerLoa_66524701.ports_aHeaWat[1])
    annotation (Line(points={{44.529394469572026,77.94022715683053},{64.52939446957203,77.94022715683053}},color={0,0,127}));
  connect(pressure_source_0b539951.ports[1], heaInd_d4b58520.port_b2)
    annotation (Line(points={{23.611826851018776,22.67795954978868},{3.611826851018776,22.67795954978868},{3.611826851018776,42.67795954978868},{3.611826851018776,62.67795954978868},{3.611826851018776,82.67795954978868},{23.611826851018776,82.67795954978868}},color={0,0,127}));
  connect(THeaWatSet_0b539951.y,heaInd_d4b58520.TSetBuiSup)
    annotation (Line(points={{61.279294663947866,16.048736267755032},{41.279294663947866,16.048736267755032},{41.279294663947866,36.04873626775503},{41.279294663947866,56.04873626775503},{41.279294663947866,76.04873626775503},{21.27929466394785,76.04873626775503}},color={0,0,127}));

  //
  // End Connect Statements for 0b539951
  //



  //
  // Begin Connect Statements for 1e7a4aae
  // Source template: /model_connectors/couplings/templates/TimeSeries_EtsColdWaterStub/ConnectStatements.mopt
  //

  // spawn, ets cold water stub connections
  connect(TChiWatSup_1e7a4aae.y,supChiWat_etsColWatStub_96c8e9a6.T_in)
    annotation (Line(points={{-53.6527650474856,-58.24524749934312},{-53.6527650474856,-78.24524749934312}},color={0,0,127}));
  connect(TimeSerLoa_66524701.ports_bChiWat[1],sinChiWat_etsColWatStub_96c8e9a6.ports[1])
    annotation (Line(points={{53.03936437851556,56.21874981763757},{33.03936437851556,56.21874981763757},{33.03936437851556,36.21874981763757},{33.03936437851556,16.218749817637573},{33.03936437851556,-3.7812501823624274},{33.03936437851556,-23.78125018236244},{33.03936437851556,-43.78125018236244},{33.03936437851556,-63.78125018236244},{13.039364378515558,-63.78125018236244},{-6.9606356214844425,-63.78125018236244},{-6.9606356214844425,-83.78125018236244},{-26.960635621484442,-83.78125018236244}},color={0,0,127}));
  connect(supChiWat_etsColWatStub_96c8e9a6.ports[1],TimeSerLoa_66524701.ports_aChiWat[1])
    annotation (Line(points={{-52.64041448406893,-58.50604801140676},{-32.64041448406893,-58.50604801140676},{-32.64041448406893,-38.50604801140676},{-32.64041448406893,-18.50604801140676},{-32.64041448406893,1.4939519885932384},{-32.64041448406893,21.49395198859324},{-32.64041448406893,41.49395198859324},{-32.64041448406893,61.49395198859324},{-12.640414484068927,61.49395198859324},{7.359585515931073,61.49395198859324},{27.359585515931073,61.49395198859324},{47.35958551593109,61.49395198859324},{47.35958551593109,81.49395198859324},{67.35958551593109,81.49395198859324}},color={0,0,127}));

  //
  // End Connect Statements for 1e7a4aae
  //



  //
  // Begin Connect Statements for 99a3ec39
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // heating indirect and network 2 pipe
  
  connect(disNet_5bbe332c.ports_bCon[1],heaInd_d4b58520.port_a1)
    annotation (Line(points={{-9.765148382120188,77.29995476451087},{10.234851617879812,77.29995476451087}},color={0,0,127}));
  connect(disNet_5bbe332c.ports_aCon[1],heaInd_d4b58520.port_b1)
    annotation (Line(points={{-1.411911407982089,86.091322268804},{18.58808859201791,86.091322268804}},color={0,0,127}));

  //
  // End Connect Statements for 99a3ec39
  //



  //
  // Begin Connect Statements for 1049ec1c
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ConnectStatements.mopt
  //

  // cooling indirect, timeseries coupling connections
  connect(TimeSerLoa_b444ff7a.ports_bHeaWat[1], heaInd_1bf72ed9.port_a2)
    annotation (Line(points={{38.743460734947945,33.94157842224023},{18.74346073494793,33.94157842224023}},color={0,0,127}));
  connect(heaInd_1bf72ed9.port_b2,TimeSerLoa_b444ff7a.ports_aHeaWat[1])
    annotation (Line(points={{35.83520627442179,31.729675748198233},{55.83520627442178,31.729675748198233}},color={0,0,127}));
  connect(pressure_source_1049ec1c.ports[1], heaInd_1bf72ed9.port_b2)
    annotation (Line(points={{-24.865326857471246,-17.32835872942387},{-4.865326857471246,-17.32835872942387},{-4.865326857471246,2.6716412705761314},{-4.865326857471246,22.67164127057613},{-4.865326857471246,42.67164127057613},{15.134673142528754,42.67164127057613}},color={0,0,127}));
  connect(THeaWatSet_1049ec1c.y,heaInd_1bf72ed9.TSetBuiSup)
    annotation (Line(points={{10.038541718019786,-17.978503836155625},{-9.961458281980214,-17.978503836155625},{-9.961458281980214,2.0214961638443754},{-9.961458281980214,22.021496163844375},{-9.961458281980214,42.021496163844375},{10.038541718019786,42.021496163844375}},color={0,0,127}));

  //
  // End Connect Statements for 1049ec1c
  //



  //
  // Begin Connect Statements for a89eacd7
  // Source template: /model_connectors/couplings/templates/TimeSeries_EtsColdWaterStub/ConnectStatements.mopt
  //

  // spawn, ets cold water stub connections
  connect(TChiWatSup_a89eacd7.y,supChiWat_etsColWatStub_2740267d.T_in)
    annotation (Line(points={{67.80217810547794,-58.635227086220596},{47.802178105477935,-58.635227086220596},{47.802178105477935,-78.6352270862206},{27.802178105477935,-78.6352270862206}},color={0,0,127}));
  connect(TimeSerLoa_b444ff7a.ports_bChiWat[1],sinChiWat_etsColWatStub_2740267d.ports[1])
    annotation (Line(points={{51.23068907698226,11.527904425366643},{31.23068907698226,11.527904425366643},{31.23068907698226,-8.472095574633357},{31.23068907698226,-28.472095574633357},{31.23068907698226,-48.47209557463336},{31.23068907698226,-68.47209557463336},{31.23068907698226,-88.47209557463336},{51.23068907698226,-88.47209557463336}},color={0,0,127}));
  connect(supChiWat_etsColWatStub_2740267d.ports[1],TimeSerLoa_b444ff7a.ports_aChiWat[1])
    annotation (Line(points={{25.07913932758298,-61.22214945549595},{45.079139327582965,-61.22214945549595},{45.079139327582965,-41.22214945549595},{45.079139327582965,-21.222149455495952},{45.079139327582965,-1.2221494554959378},{45.079139327582965,18.777850544504062},{45.079139327582965,38.77785054450406},{65.07913932758296,38.77785054450406}},color={0,0,127}));

  //
  // End Connect Statements for a89eacd7
  //



  //
  // Begin Connect Statements for a03177dd
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // heating indirect and network 2 pipe
  
  connect(disNet_5bbe332c.ports_bCon[2],heaInd_1bf72ed9.port_a1)
    annotation (Line(points={{-11.551448774058017,62.9085958245222},{-11.551448774058017,42.908595824522195},{8.448551225941983,42.908595824522195},{28.448551225941983,42.908595824522195}},color={0,0,127}));
  connect(disNet_5bbe332c.ports_aCon[2],heaInd_1bf72ed9.port_b1)
    annotation (Line(points={{-13.42003450010101,66.55516854580408},{-13.42003450010101,46.55516854580408},{6.579965499898989,46.55516854580408},{26.57996549989899,46.55516854580408}},color={0,0,127}));

  //
  // End Connect Statements for a03177dd
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