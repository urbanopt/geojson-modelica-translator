within spawn_district_heating_and_cooling_systems.Districts;
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
  // Begin Model Instance for disNet_3350e94e
  // Source template: /model_connectors/networks/templates/Network2Pipe_Instance.mopt
  //
parameter Integer nBui_disNet_3350e94e=1;
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_disNet_3350e94e=sum({
    cooInd_a42a34c4.mDis_flow_nominal})
    "Nominal mass flow rate of the distribution pump";
  parameter Modelica.Units.SI.MassFlowRate mCon_flow_nominal_disNet_3350e94e[nBui_disNet_3350e94e]={
    cooInd_a42a34c4.mDis_flow_nominal}
    "Nominal mass flow rate in each connection line";
  parameter Modelica.Units.SI.PressureDifference dpDis_nominal_disNet_3350e94e[nBui_disNet_3350e94e](
    each min=0,
    each displayUnit="Pa")=1/2 .* cat(
    1,
    {dp_nominal_disNet_3350e94e*0.1},
    fill(
      dp_nominal_disNet_3350e94e*0.9/(nBui_disNet_3350e94e-1),
      nBui_disNet_3350e94e-1))
    "Pressure drop between each connected building at nominal conditions (supply line)";
  parameter Modelica.Units.SI.PressureDifference dp_nominal_disNet_3350e94e=dpSetPoi_disNet_3350e94e+nBui_disNet_3350e94e*7000
    "District network pressure drop";
  // NOTE: this differential pressure setpoint is currently utilized by plants elsewhere
  parameter Modelica.Units.SI.Pressure dpSetPoi_disNet_3350e94e=50000
    "Differential pressure setpoint";

  Buildings.Experimental.DHC.Networks.Distribution2Pipe disNet_3350e94e(
    redeclare final package Medium=MediumW,
    final nCon=nBui_disNet_3350e94e,
    iConDpSen=nBui_disNet_3350e94e,
    final mDis_flow_nominal=mDis_flow_nominal_disNet_3350e94e,
    final mCon_flow_nominal=mCon_flow_nominal_disNet_3350e94e,
    final allowFlowReversal=true,
    dpDis_nominal=dpDis_nominal_disNet_3350e94e)
    "Distribution network."
    annotation (Placement(transformation(extent={{-30.0,60.0},{-10.0,70.0}})));
  //
  // End Model Instance for disNet_3350e94e
  //


  
  //
  // Begin Model Instance for cooPla_ba42f06c
  // Source template: /model_connectors/plants/templates/CoolingPlant_Instance.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mCHW_flow_nominal_cooPla_ba42f06c=cooPla_ba42f06c.numChi*(cooPla_ba42f06c.perChi.mEva_flow_nominal)
    "Nominal chilled water mass flow rate";
  parameter Modelica.Units.SI.MassFlowRate mCW_flow_nominal_cooPla_ba42f06c=cooPla_ba42f06c.perChi.mCon_flow_nominal
    "Nominal condenser water mass flow rate";
  parameter Modelica.Units.SI.PressureDifference dpCHW_nominal_cooPla_ba42f06c=44.8*1000
    "Nominal chilled water side pressure";
  parameter Modelica.Units.SI.PressureDifference dpCW_nominal_cooPla_ba42f06c=46.2*1000
    "Nominal condenser water side pressure";
  parameter Modelica.Units.SI.Power QEva_nominal_cooPla_ba42f06c=mCHW_flow_nominal_cooPla_ba42f06c*4200*(5-14)
    "Nominal cooling capaciaty (Negative means cooling)";
  parameter Modelica.Units.SI.MassFlowRate mMin_flow_cooPla_ba42f06c=0.2*mCHW_flow_nominal_cooPla_ba42f06c/cooPla_ba42f06c.numChi
    "Minimum mass flow rate of single chiller";
  // control settings
  parameter Modelica.Units.SI.Pressure dpSetPoi_cooPla_ba42f06c=70000
    "Differential pressure setpoint";
  parameter Modelica.Units.SI.Pressure pumDP_cooPla_ba42f06c=dpCHW_nominal_cooPla_ba42f06c+dpSetPoi_cooPla_ba42f06c+200000;
  parameter Modelica.Units.SI.Time tWai_cooPla_ba42f06c=30
    "Waiting time";
  // pumps
  parameter Buildings.Fluid.Movers.Data.Generic perCHWPum_cooPla_ba42f06c(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=((mCHW_flow_nominal_cooPla_ba42f06c/numberofchillers)/1000)*{0.1,1,1.2},
      dp=pumDP_cooPla_ba42f06c*{1.2,1,0.1}))
    "Performance data for chilled water pumps";
  parameter Buildings.Fluid.Movers.Data.Generic perCWPum_cooPla_ba42f06c(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=mCW_flow_nominal_cooPla_ba42f06c/1000*{0.2,0.6,1.0,1.2},
      dp=(dpCW_nominal_cooPla_ba42f06c+60000+6000)*{1.2,1.1,1.0,0.6}))
    "Performance data for condenser water pumps";


  Modelica.Blocks.Sources.RealExpression TSetChiWatDis_cooPla_ba42f06c(
    y=5+273.15)
    "Chilled water supply temperature set point on district level."
    annotation (Placement(transformation(extent={{10.0,-70.0},{30.0,-50.0}})));
  Modelica.Blocks.Sources.BooleanConstant on_cooPla_ba42f06c
    "On signal of the plant"
    annotation (Placement(transformation(extent={{50.0,-70.0},{70.0,-50.0}})));

  spawn_district_heating_and_cooling_systems.Plants.CentralCoolingPlant cooPla_ba42f06c(
    numChi = numberofchillers,
    redeclare Buildings.Fluid.Chillers.Data.ElectricEIR.ElectricEIRChiller_Carrier_19EX_5208kW_6_88COP_Vanes perChi,
    perCHWPum=perCHWPum_cooPla_ba42f06c,
    perCWPum=perCWPum_cooPla_ba42f06c,
    mCHW_flow_nominal=mCHW_flow_nominal_cooPla_ba42f06c,
    dpCHW_nominal=dpCHW_nominal_cooPla_ba42f06c,
    QEva_nominal=QEva_nominal_cooPla_ba42f06c,
    mMin_flow=mMin_flow_cooPla_ba42f06c,
    mCW_flow_nominal=mCW_flow_nominal_cooPla_ba42f06c,
    dpCW_nominal=dpCW_nominal_cooPla_ba42f06c,
    TAirInWB_nominal=298.7,
    TCW_nominal=308.15,
    TMin=288.15,
    tWai=tWai_cooPla_ba42f06c,
    dpSetPoi=dpSetPoi_cooPla_ba42f06c
    )
    "District cooling plant."
    annotation (Placement(transformation(extent={{-70.0,50.0},{-50.0,70.0}})));
  //
  // End Model Instance for cooPla_ba42f06c
  //


  
  //
  // Begin Model Instance for disNet_979594dc
  // Source template: /model_connectors/networks/templates/Network2Pipe_Instance.mopt
  //
parameter Integer nBui_disNet_979594dc=1;
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_disNet_979594dc=sum({
    heaInd_d49f98b9.mDis_flow_nominal})
    "Nominal mass flow rate of the distribution pump";
  parameter Modelica.Units.SI.MassFlowRate mCon_flow_nominal_disNet_979594dc[nBui_disNet_979594dc]={
    heaInd_d49f98b9.mDis_flow_nominal}
    "Nominal mass flow rate in each connection line";
  parameter Modelica.Units.SI.PressureDifference dpDis_nominal_disNet_979594dc[nBui_disNet_979594dc](
    each min=0,
    each displayUnit="Pa")=1/2 .* cat(
    1,
    {dp_nominal_disNet_979594dc*0.1},
    fill(
      dp_nominal_disNet_979594dc*0.9/(nBui_disNet_979594dc-1),
      nBui_disNet_979594dc-1))
    "Pressure drop between each connected building at nominal conditions (supply line)";
  parameter Modelica.Units.SI.PressureDifference dp_nominal_disNet_979594dc=dpSetPoi_disNet_979594dc+nBui_disNet_979594dc*7000
    "District network pressure drop";
  // NOTE: this differential pressure setpoint is currently utilized by plants elsewhere
  parameter Modelica.Units.SI.Pressure dpSetPoi_disNet_979594dc=50000
    "Differential pressure setpoint";

  Buildings.Experimental.DHC.Networks.Distribution2Pipe disNet_979594dc(
    redeclare final package Medium=MediumW,
    final nCon=nBui_disNet_979594dc,
    iConDpSen=nBui_disNet_979594dc,
    final mDis_flow_nominal=mDis_flow_nominal_disNet_979594dc,
    final mCon_flow_nominal=mCon_flow_nominal_disNet_979594dc,
    final allowFlowReversal=true,
    dpDis_nominal=dpDis_nominal_disNet_979594dc)
    "Distribution network."
    annotation (Placement(transformation(extent={{-30.0,20.0},{-10.0,30.0}})));
  //
  // End Model Instance for disNet_979594dc
  //


  
  //
  // Begin Model Instance for heaPla5df27525
  // Source template: /model_connectors/plants/templates/HeatingPlant_Instance.mopt
  //
  // heating plant instance
  parameter Modelica.Units.SI.MassFlowRate mHW_flow_nominal_heaPla5df27525=mBoi_flow_nominal_heaPla5df27525*heaPla5df27525.numBoi
    "Nominal heating water mass flow rate";
  parameter Modelica.Units.SI.MassFlowRate mBoi_flow_nominal_heaPla5df27525=QBoi_nominal_heaPla5df27525/(4200*heaPla5df27525.delT_nominal)
    "Nominal heating water mass flow rate";
  parameter Modelica.Units.SI.Power QBoi_nominal_heaPla5df27525=Q_flow_nominal_heaPla5df27525/heaPla5df27525.numBoi
    "Nominal heating capaciaty";
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_heaPla5df27525=1000000*2
    "Heating load";
  parameter Modelica.Units.SI.MassFlowRate mMin_flow_heaPla5df27525=0.2*mBoi_flow_nominal_heaPla5df27525
    "Minimum mass flow rate of single boiler";
  // controls
  parameter Modelica.Units.SI.Pressure pumDP=(heaPla5df27525.dpBoi_nominal+dpSetPoi_disNet_979594dc+50000)
    "Heating water pump pressure drop";
  parameter Modelica.Units.SI.Time tWai_heaPla5df27525=30
    "Waiting time";
  parameter Buildings.Fluid.Movers.Data.Generic perHWPum_heaPla5df27525(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=mBoi_flow_nominal_heaPla5df27525/1000*{0.1,1.1},
      dp=pumDP*{1.1,0.1}))
    "Performance data for heating water pumps";

  spawn_district_heating_and_cooling_systems.Plants.CentralHeatingPlant heaPla5df27525(
    perHWPum=perHWPum_heaPla5df27525,
    mHW_flow_nominal=mHW_flow_nominal_heaPla5df27525,
    QBoi_flow_nominal=QBoi_nominal_heaPla5df27525,
    mMin_flow=mMin_flow_heaPla5df27525,
    mBoi_flow_nominal=mBoi_flow_nominal_heaPla5df27525,
    dpBoi_nominal=10000,
    delT_nominal(
      displayUnit="degC")=15,
    tWai=tWai_heaPla5df27525,
    // TODO: we're currently grabbing dpSetPoi from the Network instance -- need feedback to determine if that's the proper "home" for it
    dpSetPoi=dpSetPoi_disNet_979594dc
    )
    "District heating plant."
    annotation (Placement(transformation(extent={{-70.0,10.0},{-50.0,30.0}})));
  //
  // End Model Instance for heaPla5df27525
  //


  
  //
  // Begin Model Instance for SpawnLoad_b76aa4b6
  // Source template: /model_connectors/load_connectors/templates/Spawn_Instance.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mLoaCoo_flow_nominal_SpawnLoad_b76aa4b6[SpawnLoad_b76aa4b6.nZon]={(-1*SpawnLoad_b76aa4b6.QCoo_flow_nominal[i]*(0.06)/1000) for i in 1:SpawnLoad_b76aa4b6.nZon};
  parameter Modelica.Units.SI.MassFlowRate mLoaHea_flow_nominal_SpawnLoad_b76aa4b6[SpawnLoad_b76aa4b6.nZon]={(SpawnLoad_b76aa4b6.QHea_flow_nominal[i]*(0.05)/1000) for i in 1:SpawnLoad_b76aa4b6.nZon};
  spawn_district_heating_and_cooling_systems.Loads.B5a6b99ec37f4de7f94020090.building SpawnLoad_b76aa4b6(
    allowFlowReversal = true,
    mLoaCoo_flow_nominal=mLoaCoo_flow_nominal_SpawnLoad_b76aa4b6,
    mLoaHea_flow_nominal=mLoaHea_flow_nominal_SpawnLoad_b76aa4b6,
    nPorts_aHeaWat=1,
    nPorts_bHeaWat=1,
    nPorts_aChiWat=1,
    nPorts_bChiWat=1,
    have_pum=true)
    "Building spawn model"
    annotation (Placement(transformation(extent={{50.0,50.0},{70.0,70.0}})));
  //
  // End Model Instance for SpawnLoad_b76aa4b6
  //


  
  //
  // Begin Model Instance for cooInd_a42a34c4
  // Source template: /model_connectors/energy_transfer_systems/templates/CoolingIndirect_Instance.mopt
  //
  // cooling indirect instance
  spawn_district_heating_and_cooling_systems.Substations.CoolingIndirect_5a6b99ec37f4de7f94020090 cooInd_a42a34c4(
    redeclare package Medium=MediumW,
    allowFlowReversal1=true,
    allowFlowReversal2=true,
    mDis_flow_nominal=mDis_flow_nominal_fdb45b31,
    mBui_flow_nominal=mBui_flow_nominal_fdb45b31,
    dp1_nominal=500,
    dp2_nominal=500,
    dpValve_nominal=7000,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_fdb45b31,
    // TODO: dehardcode the nominal temperatures?
    T_a1_nominal=273.15+5,
    T_a2_nominal=273.15+13)
    "Indirect cooling energy transfer station ETS."
    annotation (Placement(transformation(extent={{10.0,10.0},{30.0,30.0}})));
  //
  // End Model Instance for cooInd_a42a34c4
  //


  
  //
  // Begin Model Instance for heaInd_d49f98b9
  // Source template: /model_connectors/energy_transfer_systems/templates/HeatingIndirect_Instance.mopt
  //
  // heating indirect instance
  spawn_district_heating_and_cooling_systems.Substations.HeatingIndirect_5a6b99ec37f4de7f94020090 heaInd_d49f98b9(
    allowFlowReversal1=true,
    allowFlowReversal2=true,
    show_T=true,
    redeclare package Medium=MediumW,
    mDis_flow_nominal=mDis_flow_nominal_a15aae99,
    mBui_flow_nominal=mBui_flow_nominal_a15aae99,
    dpValve_nominal=6000,
    dp1_nominal=500,
    dp2_nominal=500,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_a15aae99,
    T_a1_nominal=55+273.15,
    T_a2_nominal=35+273.15,
    k=0.1,
    Ti=60,
    reverseActing=true)
    annotation (Placement(transformation(extent={{10.0,50.0},{30.0,70.0}})));
  //
  // End Model Instance for heaInd_d49f98b9
  //


  

  // Model dependencies

  //
  // Begin Component Definitions for eecc546c
  // Source template: /model_connectors/couplings/templates/Network2Pipe_CoolingPlant/ComponentDefinitions.mopt
  //
  // No components for pipe and cooling plant

  //
  // End Component Definitions for eecc546c
  //



  //
  // Begin Component Definitions for 44d98a6a
  // Source template: /model_connectors/couplings/templates/Network2Pipe_HeatingPlant/ComponentDefinitions.mopt
  //
  // TODO: This should not be here, it is entirely plant specific and should be moved elsewhere
  // but since it requires a connect statement we must put it here for now...
  Modelica.Blocks.Sources.BooleanConstant mPum_flow_44d98a6a(
    k=true)
    "Total heating water pump mass flow rate"
    annotation (Placement(transformation(extent={{-70.0,-30.0},{-50.0,-10.0}})));
  // TODO: This should not be here, it is entirely plant specific and should be moved elsewhere
  // but since it requires a connect statement we must put it here for now...
  Modelica.Blocks.Sources.RealExpression TDisSetHeaWat_44d98a6a(
    each y=273.15+54)
    "District side heating water supply temperature set point."
    annotation (Placement(transformation(extent={{-30.0,-30.0},{-10.0,-10.0}})));

  //
  // End Component Definitions for 44d98a6a
  //



  //
  // Begin Component Definitions for fdb45b31
  // Source template: /model_connectors/couplings/templates/Spawn_CoolingIndirect/ComponentDefinitions.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_fdb45b31=SpawnLoad_b76aa4b6.disFloCoo.m_flow_nominal*delChiWatTemBui/delChiWatTemDis
    "Nominal mass flow rate of primary (district) district cooling side"; // TODO: verify this is ok!
  parameter Modelica.Units.SI.MassFlowRate mBui_flow_nominal_fdb45b31=SpawnLoad_b76aa4b6.terUni[1].mChiWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district cooling side"; // TODO: verify this is ok!
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_fdb45b31=-1*SpawnLoad_b76aa4b6.QHea_flow_nominal[1]; // TODO: verify this is ok!
  Modelica.Fluid.Sources.FixedBoundary pressure_source_fdb45b31(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{10.0,-30.0},{30.0,-10.0}})));
  // TODO: move TChiWatSet (and its connection) into a CoolingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression TChiWatSet_fdb45b31(
    y=7+273.15)
    //Dehardcode
    "Primary loop (district side) chilled water setpoint temperature."
    annotation (Placement(transformation(extent={{50.0,-30.0},{70.0,-10.0}})));

  //
  // End Component Definitions for fdb45b31
  //



  //
  // Begin Component Definitions for a217ff20
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for cooling indirect and network 2 pipe

  //
  // End Component Definitions for a217ff20
  //



  //
  // Begin Component Definitions for a15aae99
  // Source template: /model_connectors/couplings/templates/Spawn_HeatingIndirect/ComponentDefinitions.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_a15aae99=SpawnLoad_b76aa4b6.disFloHea.m_flow_nominal*delHeaWatTemBui/delHeaWatTemDis
    "Nominal mass flow rate of primary (district) district heating side"; // TODO: Verify this is ok!
  parameter Modelica.Units.SI.MassFlowRate mBui_flow_nominal_a15aae99=SpawnLoad_b76aa4b6.terUni[1].mHeaWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district heating side"; // TODO: Verify this is ok!
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_a15aae99=SpawnLoad_b76aa4b6.QHea_flow_nominal[1]; // TODO: Verify this is ok!
  Modelica.Fluid.Sources.FixedBoundary pressure_source_a15aae99(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{-70.0,-70.0},{-50.0,-50.0}})));
  // TODO: move THeaWatSet (and its connection) into a HeatingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression THeaWatSet_a15aae99(
    // y=40+273.15)
    y=273.15+40 )
    "Secondary loop (Building side) heating water setpoint temperature."
    //Dehardcode
    annotation (Placement(transformation(extent={{-30.0,-70.0},{-10.0,-50.0}})));

  //
  // End Component Definitions for a15aae99
  //



  //
  // Begin Component Definitions for a4a31743
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for heating indirect and network 2 pipe

  //
  // End Component Definitions for a4a31743
  //



equation
  // Connections

  //
  // Begin Connect Statements for eecc546c
  // Source template: /model_connectors/couplings/templates/Network2Pipe_CoolingPlant/ConnectStatements.mopt
  //

  // TODO: these connect statements shouldn't be here, they are plant specific
  // but since we can't currently make connect statements for single systems, this is what we've got
  connect(on_cooPla_ba42f06c.y,cooPla_ba42f06c.on)
    annotation (Line(points={{59.67712471074154,-30.09780714114916},{39.67712471074154,-30.09780714114916},{39.67712471074154,-10.097807141149161},{39.67712471074154,9.902192858850839},{39.67712471074154,29.90219285885084},{39.67712471074154,49.90219285885084},{19.677124710741523,49.90219285885084},{-0.3228752892584765,49.90219285885084},{-20.322875289258477,49.90219285885084},{-40.32287528925847,49.90219285885084},{-40.32287528925847,69.90219285885084},{-60.32287528925847,69.90219285885084}},color={0,0,127}));
  connect(TSetChiWatDis_cooPla_ba42f06c.y,cooPla_ba42f06c.TCHWSupSet)
    annotation (Line(points={{26.736253145009158,-35.175972152544944},{6.736253145009158,-35.175972152544944},{6.736253145009158,-15.175972152544944},{6.736253145009158,4.824027847455056},{6.736253145009158,24.824027847455056},{6.736253145009158,44.82402784745506},{-13.263746854990842,44.82402784745506},{-33.26374685499084,44.82402784745506},{-33.26374685499084,64.82402784745506},{-53.26374685499084,64.82402784745506}},color={0,0,127}));

  connect(disNet_3350e94e.port_bDisRet,cooPla_ba42f06c.port_a)
    annotation (Line(points={{-39.88593151501985,50.93850799483132},{-59.88593151501985,50.93850799483132}},color={0,0,127}));
  connect(cooPla_ba42f06c.port_b,disNet_3350e94e.port_aDisSup)
    annotation (Line(points={{-34.8067622012223,69.8626935950658},{-14.806762201222298,69.8626935950658}},color={0,0,127}));
  connect(disNet_3350e94e.dp,cooPla_ba42f06c.dpMea)
    annotation (Line(points={{-33.70643359618465,68.29150944935301},{-53.70643359618465,68.29150944935301}},color={0,0,127}));

  //
  // End Connect Statements for eecc546c
  //



  //
  // Begin Connect Statements for 44d98a6a
  // Source template: /model_connectors/couplings/templates/Network2Pipe_HeatingPlant/ConnectStatements.mopt
  //

  connect(heaPla5df27525.port_a,disNet_979594dc.port_bDisRet)
    annotation (Line(points={{-48.69232416680849,24.918602036014235},{-28.69232416680849,24.918602036014235}},color={0,0,127}));
  connect(disNet_979594dc.dp,heaPla5df27525.dpMea)
    annotation (Line(points={{-46.44338616496596,24.95450172431181},{-66.44338616496596,24.95450172431181}},color={0,0,127}));
  connect(heaPla5df27525.port_b,disNet_979594dc.port_aDisSup)
    annotation (Line(points={{-45.238033923858474,19.320762203433105},{-25.238033923858467,19.320762203433105}},color={0,0,127}));
  connect(mPum_flow_44d98a6a.y,heaPla5df27525.on)
    annotation (Line(points={{-65.29066438145401,5.126674956805758},{-65.29066438145401,25.126674956805758}},color={0,0,127}));
  connect(TDisSetHeaWat_44d98a6a.y,heaPla5df27525.THeaSet)
    annotation (Line(points={{-17.182827448678793,-3.8014641302819854},{-37.18282744867879,-3.8014641302819854},{-37.18282744867879,16.198535869718015},{-57.18282744867879,16.198535869718015}},color={0,0,127}));

  //
  // End Connect Statements for 44d98a6a
  //



  //
  // Begin Connect Statements for fdb45b31
  // Source template: /model_connectors/couplings/templates/Spawn_CoolingIndirect/ConnectStatements.mopt
  //

  connect(SpawnLoad_b76aa4b6.ports_bChiWat[1], cooInd_a42a34c4.port_a2)
    annotation (Line(points={{68.26786201792814,38.52207306864858},{68.26786201792814,18.52207306864858},{48.26786201792814,18.52207306864858},{28.267862017928138,18.52207306864858}},color={0,0,127}));
  connect(cooInd_a42a34c4.port_b2,SpawnLoad_b76aa4b6.ports_aChiWat[1])
    annotation (Line(points={{15.857834857736464,38.67907154406314},{35.857834857736464,38.67907154406314},{35.857834857736464,58.67907154406314},{55.857834857736464,58.67907154406314}},color={0,0,127}));
  connect(pressure_source_fdb45b31.ports[1], cooInd_a42a34c4.port_b2)
    annotation (Line(points={{14.25636571877179,-8.457767785545869},{14.25636571877179,11.542232214454131}},color={0,0,127}));
  connect(TChiWatSet_fdb45b31.y,cooInd_a42a34c4.TSetBuiSup)
    annotation (Line(points={{52.972907818749576,-5.358839460159672},{52.972907818749576,14.641160539840328},{52.972907818749576,34.64116053984033},{52.972907818749576,54.64116053984033}},color={0,0,127}));

  //
  // End Connect Statements for fdb45b31
  //



  //
  // Begin Connect Statements for a217ff20
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // cooling indirect and network 2 pipe
  
  connect(disNet_3350e94e.ports_bCon[1],cooInd_a42a34c4.port_a1)
    annotation (Line(points={{-23.31877925762018,44.81984952976077},{-3.3187792576201787,44.81984952976077},{-3.3187792576201787,24.819849529760774},{16.68122074237982,24.819849529760774}},color={0,0,127}));
  connect(disNet_3350e94e.ports_aCon[1],cooInd_a42a34c4.port_b1)
    annotation (Line(points={{-24.693853954893115,39.14503719098693},{-4.693853954893115,39.14503719098693},{-4.693853954893115,19.14503719098694},{15.306146045106885,19.14503719098694}},color={0,0,127}));

  //
  // End Connect Statements for a217ff20
  //



  //
  // Begin Connect Statements for a15aae99
  // Source template: /model_connectors/couplings/templates/Spawn_HeatingIndirect/ConnectStatements.mopt
  //

  connect(SpawnLoad_b76aa4b6.ports_bHeaWat[1], heaInd_d49f98b9.port_a2)
    annotation (Line(points={{46.10387329745515,55.84417954456802},{26.103873297455166,55.84417954456802}},color={0,0,127}));
  connect(heaInd_d49f98b9.port_b2,SpawnLoad_b76aa4b6.ports_aHeaWat[1])
    annotation (Line(points={{49.012537765515674,69.5366822002747},{69.01253776551567,69.5366822002747}},color={0,0,127}));
  connect(pressure_source_a15aae99.ports[1], heaInd_d49f98b9.port_b2)
    annotation (Line(points={{-63.71589967533494,-35.964980551634014},{-43.71589967533494,-35.964980551634014},{-43.71589967533494,-15.964980551634014},{-43.71589967533494,4.035019448365986},{-43.71589967533494,24.035019448365986},{-43.71589967533494,44.03501944836598},{-23.71589967533494,44.03501944836598},{-3.7158996753349385,44.03501944836598},{-3.7158996753349385,64.03501944836599},{16.28410032466506,64.03501944836599}},color={0,0,127}));
  connect(THeaWatSet_a15aae99.y,heaInd_d49f98b9.TSetBuiSup)
    annotation (Line(points={{-13.305272646829636,-31.596811315919993},{6.694727353170364,-31.596811315919993},{6.694727353170364,-11.596811315919993},{6.694727353170364,8.403188684080007},{6.694727353170364,28.403188684080007},{6.694727353170364,48.40318868408001},{6.694727353170364,68.40318868408},{26.694727353170364,68.40318868408}},color={0,0,127}));

  //
  // End Connect Statements for a15aae99
  //



  //
  // Begin Connect Statements for a4a31743
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // heating indirect and network 2 pipe
  
  connect(disNet_979594dc.ports_bCon[1],heaInd_d49f98b9.port_a1)
    annotation (Line(points={{-24.246241199665164,43.0275842788144},{-4.246241199665164,43.0275842788144},{-4.246241199665164,63.0275842788144},{15.753758800334836,63.0275842788144}},color={0,0,127}));
  connect(disNet_979594dc.ports_aCon[1],heaInd_d49f98b9.port_b1)
    annotation (Line(points={{-20.377834768128395,33.96745793599857},{-0.37783476812839467,33.96745793599857},{-0.37783476812839467,53.96745793599857},{19.622165231871605,53.96745793599857}},color={0,0,127}));

  //
  // End Connect Statements for a4a31743
  //




annotation(
  experiment(
    StopTime=86400,
    Interval=3600,
    Tolerance=1e-06),
  Diagram(
    coordinateSystem(
      preserveAspectRatio=false,
      extent={{-90.0,-90.0},{90.0,90.0}})),
  Documentation(
    revisions="<html>
 <li>
 May 10, 2020: Hagar Elarga<br/>
Updated implementation to handle template needed for GeoJSON to Modelica.
</li>
</html>"));
end DistrictEnergySystem;