within spawn_district_cooling.Districts;
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
  // Begin Model Instance for disNet_ab4120b7
  // Source template: /model_connectors/networks/templates/Network2Pipe_Instance.mopt
  //
parameter Integer nBui_disNet_ab4120b7=1;
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_disNet_ab4120b7=sum({
    cooInd_4e81dd87.mDis_flow_nominal})
    "Nominal mass flow rate of the distribution pump";
  parameter Modelica.Units.SI.MassFlowRate mCon_flow_nominal_disNet_ab4120b7[nBui_disNet_ab4120b7]={
    cooInd_4e81dd87.mDis_flow_nominal}
    "Nominal mass flow rate in each connection line";
  parameter Modelica.Units.SI.PressureDifference dpDis_nominal_disNet_ab4120b7[nBui_disNet_ab4120b7](
    each min=0,
    each displayUnit="Pa")=1/2 .* cat(
    1,
    {dp_nominal_disNet_ab4120b7*0.1},
    fill(
      dp_nominal_disNet_ab4120b7*0.9/(nBui_disNet_ab4120b7-1),
      nBui_disNet_ab4120b7-1))
    "Pressure drop between each connected building at nominal conditions (supply line)";
  parameter Modelica.Units.SI.PressureDifference dp_nominal_disNet_ab4120b7=dpSetPoi_disNet_ab4120b7+nBui_disNet_ab4120b7*7000
    "District network pressure drop";
  // NOTE: this differential pressure setpoint is currently utilized by plants elsewhere
  parameter Modelica.Units.SI.Pressure dpSetPoi_disNet_ab4120b7=50000
    "Differential pressure setpoint";

  Buildings.Experimental.DHC.Networks.Distribution2Pipe disNet_ab4120b7(

    redeclare final package Medium=MediumW,
    final nCon=nBui_disNet_ab4120b7,
    iConDpSen=nBui_disNet_ab4120b7,
    final mDis_flow_nominal=mDis_flow_nominal_disNet_ab4120b7,
    final mCon_flow_nominal=mCon_flow_nominal_disNet_ab4120b7,
    final allowFlowReversal=true,
    dpDis_nominal=dpDis_nominal_disNet_ab4120b7)
    "Distribution network."
    annotation (Placement(transformation(extent={{-30.0,40.0},{-10.0,50.0}})));
  //
  // End Model Instance for disNet_ab4120b7
  //



  //
  // Begin Model Instance for cooPla_eb62225f
  // Source template: /model_connectors/plants/templates/CoolingPlant_Instance.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mCHW_flow_nominal_cooPla_eb62225f=cooPla_eb62225f.numChi*(cooPla_eb62225f.perChi.mEva_flow_nominal)
    "Nominal chilled water mass flow rate";
  parameter Modelica.Units.SI.MassFlowRate mCW_flow_nominal_cooPla_eb62225f=cooPla_eb62225f.perChi.mCon_flow_nominal
    "Nominal condenser water mass flow rate";
  parameter Modelica.Units.SI.PressureDifference dpCHW_nominal_cooPla_eb62225f=44.8*1000
    "Nominal chilled water side pressure";
  parameter Modelica.Units.SI.PressureDifference dpCW_nominal_cooPla_eb62225f=46.2*1000
    "Nominal condenser water side pressure";
  parameter Modelica.Units.SI.Power QEva_nominal_cooPla_eb62225f=mCHW_flow_nominal_cooPla_eb62225f*4200*(5-14)
    "Nominal cooling capaciaty (Negative means cooling)";
  parameter Modelica.Units.SI.MassFlowRate mMin_flow_cooPla_eb62225f=0.2*mCHW_flow_nominal_cooPla_eb62225f/cooPla_eb62225f.numChi
    "Minimum mass flow rate of single chiller";
  // control settings
  parameter Modelica.Units.SI.Pressure dpSetPoi_cooPla_eb62225f=70000
    "Differential pressure setpoint";
  parameter Modelica.Units.SI.Pressure pumDP_cooPla_eb62225f=dpCHW_nominal_cooPla_eb62225f+dpSetPoi_cooPla_eb62225f+200000;
  parameter Modelica.Units.SI.Time tWai_cooPla_eb62225f=30
    "Waiting time";
  // pumps
  parameter Buildings.Fluid.Movers.Data.Generic perCHWPum_cooPla_eb62225f(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      //V_flow=((mCHW_flow_nominal_cooPla_eb62225f/cooPla_eb62225f.numChi)/1000)*{0.1,1,1.2},
       V_flow=((mCHW_flow_nominal_cooPla_eb62225f/2)/1000)*{0.1,1,1.2},
      dp=pumDP_cooPla_eb62225f*{1.2,1,0.1}))
    "Performance data for chilled water pumps";
  parameter Buildings.Fluid.Movers.Data.Generic perCWPum_cooPla_eb62225f(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=mCW_flow_nominal_cooPla_eb62225f/1000*{0.2,0.6,1.0,1.2},
      dp=(dpCW_nominal_cooPla_eb62225f+60000+6000)*{1.2,1.1,1.0,0.6}))
    "Performance data for condenser water pumps";


  Modelica.Blocks.Sources.RealExpression TSetChiWatDis_cooPla_eb62225f(
    y=5+273.15)
    "Chilled water supply temperature set point on district level."
    annotation (Placement(transformation(extent={{50.0,-10.0},{70.0,10.0}})));
  Modelica.Blocks.Sources.BooleanConstant on_cooPla_eb62225f
    "On signal of the plant"
    annotation (Placement(transformation(extent={{-70.0,-50.0},{-50.0,-30.0}})));

  spawn_district_cooling.Plants.CentralCoolingPlant cooPla_eb62225f(
    redeclare Buildings.Fluid.Chillers.Data.ElectricEIR.ElectricEIRChiller_Carrier_19EX_5208kW_6_88COP_Vanes perChi,
    perCHWPum=perCHWPum_cooPla_eb62225f,
    perCWPum=perCWPum_cooPla_eb62225f,
    mCHW_flow_nominal=mCHW_flow_nominal_cooPla_eb62225f,
    dpCHW_nominal=dpCHW_nominal_cooPla_eb62225f,
    QEva_nominal=QEva_nominal_cooPla_eb62225f,
    mMin_flow=mMin_flow_cooPla_eb62225f,
    mCW_flow_nominal=mCW_flow_nominal_cooPla_eb62225f,
    dpCW_nominal=dpCW_nominal_cooPla_eb62225f,
    TAirInWB_nominal=298.7,
    TCW_nominal=308.15,
    TMin=288.15,
    tWai=tWai_cooPla_eb62225f,
    dpSetPoi=dpSetPoi_cooPla_eb62225f
    )
    "District cooling plant."
    annotation (Placement(transformation(extent={{-70.0,30.0},{-50.0,50.0}})));
  //
  // End Model Instance for cooPla_eb62225f
  //



  //
  // Begin Model Instance for SpawnLoad_909d187e
  // Source template: /model_connectors/load_connectors/templates/Spawn_Instance.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mLoaCoo_flow_nominal_SpawnLoad_909d187e[SpawnLoad_909d187e.nZon]={(-1*SpawnLoad_909d187e.QCoo_flow_nominal[i]*(0.06)/1000) for i in 1:SpawnLoad_909d187e.nZon};
  parameter Modelica.Units.SI.MassFlowRate mLoaHea_flow_nominal_SpawnLoad_909d187e[SpawnLoad_909d187e.nZon]={(SpawnLoad_909d187e.QHea_flow_nominal[i]*(0.05)/1000) for i in 1:SpawnLoad_909d187e.nZon};
  spawn_district_cooling.Loads.B5a6b99ec37f4de7f94020090.building SpawnLoad_909d187e(
  allowFlowReversal = true,
    mLoaCoo_flow_nominal=mLoaCoo_flow_nominal_SpawnLoad_909d187e,
    mLoaHea_flow_nominal=mLoaHea_flow_nominal_SpawnLoad_909d187e,
    nPorts_aHeaWat=1,
    nPorts_bHeaWat=1,
    nPorts_aChiWat=1,
    nPorts_bChiWat=1,
    have_pum=true)
    "Building spawn model"
    annotation (Placement(transformation(extent={{50.0,30.0},{70.0,50.0}})));
  //
  // End Model Instance for SpawnLoad_909d187e
  //



  //
  // Begin Model Instance for cooInd_4e81dd87
  // Source template: /model_connectors/energy_transfer_systems/templates/CoolingIndirect_Instance.mopt
  //
  // cooling indirect instance
  spawn_district_cooling.Substations.CoolingIndirect_5a6b99ec37f4de7f94020090 cooInd_4e81dd87(
    redeclare package Medium=MediumW,
    allowFlowReversal1=true,
    allowFlowReversal2=true,
    mDis_flow_nominal=mDis_flow_nominal_c92be705,
    mBui_flow_nominal=mBui_flow_nominal_c92be705,
    dp1_nominal=500,
    dp2_nominal=500,
    dpValve_nominal=7000,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_c92be705,
    // TODO: dehardcode the nominal temperatures?
    T_a1_nominal=273.15+5,
    T_a2_nominal=273.15+13)
    "Indirect cooling energy transfer station ETS."
    annotation (Placement(transformation(extent={{10.0,30.0},{30.0,50.0}})));
  //
  // End Model Instance for cooInd_4e81dd87
  //



  //
  // Begin Model Instance for etsHotWatStub_3d70d616
  // Source template: /model_connectors/energy_transfer_systems/templates/EtsHotWaterStub_Instance.mopt
  //
  // TODO: move these components into a single component
  Buildings.Fluid.Sources.Boundary_pT supHeaWat_etsHotWatStub_3d70d616(
    redeclare package Medium=MediumW,
    use_T_in=true,
    nPorts=1)
    "Heating water supply"
    annotation (Placement(transformation(extent={{-30.0,-50.0},{-10.0,-30.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinHeaWat_etsHotWatStub_3d70d616(
    redeclare package Medium=MediumW,
    nPorts=1)
    "Heating water sink"
    annotation (Placement(transformation(extent={{10.0,-50.0},{30.0,-30.0}})));
  //
  // End Model Instance for etsHotWatStub_3d70d616
  //




  // Model dependencies

  //
  // Begin Component Definitions for f06692cf
  // Source template: /model_connectors/couplings/templates/Network2Pipe_CoolingPlant/ComponentDefinitions.mopt
  //
  // No components for pipe and cooling plant

  //
  // End Component Definitions for f06692cf
  //



  //
  // Begin Component Definitions for c92be705
  // Source template: /model_connectors/couplings/templates/Spawn_CoolingIndirect/ComponentDefinitions.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_c92be705=SpawnLoad_909d187e.disFloCoo.m_flow_nominal*delChiWatTemBui/delChiWatTemDis
    "Nominal mass flow rate of primary (district) district cooling side"; // TODO: verify this is ok!
  parameter Modelica.Units.SI.MassFlowRate mBui_flow_nominal_c92be705=SpawnLoad_909d187e.terUni[1].mChiWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district cooling side"; // TODO: verify this is ok!
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_c92be705=-1*SpawnLoad_909d187e.QHea_flow_nominal[1]; // TODO: verify this is ok!
  Modelica.Fluid.Sources.FixedBoundary pressure_source_c92be705(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{-70.0,-10.0},{-50.0,10.0}})));
  // TODO: move TChiWatSet (and its connection) into a CoolingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression TChiWatSet_c92be705(
    y=7+273.15)
    //Dehardcode
    "Primary loop (district side) chilled water setpoint temperature."
    annotation (Placement(transformation(extent={{-30.0,-10.0},{-10.0,10.0}})));

  //
  // End Component Definitions for c92be705
  //



  //
  // Begin Component Definitions for 727eab20
  // Source template: /model_connectors/couplings/templates/Spawn_EtsHotWaterStub/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression THeaWatSup_727eab20(
    y=max(
      SpawnLoad_909d187e.terUni.T_aHeaWat_nominal))
    "Heating water supply temperature"
    annotation (Placement(transformation(extent={{10.0,-10.0},{30.0,10.0}})));

  //
  // End Component Definitions for 727eab20
  //



  //
  // Begin Component Definitions for b281bcee
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for cooling indirect and network 2 pipe

  //
  // End Component Definitions for b281bcee
  //



equation
  // Connections

  //
  // Begin Connect Statements for f06692cf
  // Source template: /model_connectors/couplings/templates/Network2Pipe_CoolingPlant/ConnectStatements.mopt
  //

  // TODO: these connect statements shouldn't be here, they are plant specific
  // but since we can't currently make connect statements for single systems, this is what we've got
  connect(on_cooPla_eb62225f.y,cooPla_eb62225f.on)
    annotation (Line(points={{-61.38890897390914,-16.631731269802827},{-81.38890897390914,-16.631731269802827},{-81.38890897390914,3.3682687301971725},{-81.38890897390914,23.368268730197173},{-81.38890897390914,43.36826873019717},{-61.38890897390914,43.36826873019717}},color={0,0,127}));
  connect(TSetChiWatDis_cooPla_eb62225f.y,cooPla_eb62225f.TCHWSupSet)
    annotation (Line(points={{54.47320078981019,18.637874429709207},{34.47320078981019,18.637874429709207},{14.473200789810193,18.637874429709207},{-5.526799210189807,18.637874429709207},{-25.526799210189807,18.637874429709207},{-45.52679921018981,18.637874429709207},{-45.52679921018981,38.63787442970921},{-65.52679921018981,38.63787442970921}},color={0,0,127}));

  connect(disNet_ab4120b7.port_bDisRet,cooPla_eb62225f.port_a)
    annotation (Line(points={{-32.896280503560334,41.35642563391536},{-52.896280503560334,41.35642563391536}},color={0,0,127}));
  connect(cooPla_eb62225f.port_b,disNet_ab4120b7.port_aDisSup)
    annotation (Line(points={{-42.96965989659943,46.096866957163925},{-22.969659896599424,46.096866957163925}},color={0,0,127}));
  connect(disNet_ab4120b7.dp,cooPla_eb62225f.dpMea)
    annotation (Line(points={{-31.701691915207874,41.54593608506316},{-51.701691915207874,41.54593608506316}},color={0,0,127}));

  //
  // End Connect Statements for f06692cf
  //



  //
  // Begin Connect Statements for c92be705
  // Source template: /model_connectors/couplings/templates/Spawn_CoolingIndirect/ConnectStatements.mopt
  //

  connect(SpawnLoad_909d187e.ports_bChiWat[1], cooInd_4e81dd87.port_a2)
    annotation (Line(points={{43.62292511705735,33.38430174240645},{23.622925117057363,33.38430174240645}},color={0,0,127}));
  connect(cooInd_4e81dd87.port_b2,SpawnLoad_909d187e.ports_aChiWat[1])
    annotation (Line(points={{41.042184648773,36.23414846455864},{61.042184648773,36.23414846455864}},color={0,0,127}));
  connect(pressure_source_c92be705.ports[1], cooInd_4e81dd87.port_b2)
    annotation (Line(points={{-61.90544360663698,21.584396435523388},{-41.90544360663698,21.584396435523388},{-21.90544360663698,21.584396435523388},{-1.9054436066369789,21.584396435523388},{-1.9054436066369789,41.58439643552339},{18.09455639336302,41.58439643552339}},color={0,0,127}));
  connect(TChiWatSet_c92be705.y,cooInd_4e81dd87.TSetBuiSup)
    annotation (Line(points={{-25.05782298456012,21.944538380782532},{-5.057822984560119,21.944538380782532},{14.942177015439881,21.944538380782532},{34.94217701543988,21.944538380782532},{34.94217701543988,41.94453838078253},{54.94217701543988,41.94453838078253}},color={0,0,127}));

  //
  // End Connect Statements for c92be705
  //



  //
  // Begin Connect Statements for 727eab20
  // Source template: /model_connectors/couplings/templates/Spawn_EtsHotWaterStub/ConnectStatements.mopt
  //

  // spawn, ets hot water stub connections
  connect(supHeaWat_etsHotWatStub_3d70d616.T_in,THeaWatSup_727eab20.y)
    annotation (Line(points={{-18.033876380648806,-29.39465423986306},{1.966123619351194,-29.39465423986306},{1.966123619351194,-9.394654239863058},{21.966123619351194,-9.394654239863058}},color={0,0,127}));
  connect(supHeaWat_etsHotWatStub_3d70d616.ports[1],SpawnLoad_909d187e.ports_aHeaWat[1])
    annotation (Line(points={{-19.485281557674426,-27.69089619677038},{0.5147184423255737,-27.69089619677038},{0.5147184423255737,-7.690896196770382},{0.5147184423255737,12.309103803229625},{20.514718442325574,12.309103803229625},{40.514718442325574,12.309103803229625},{40.514718442325574,32.309103803229625},{60.514718442325574,32.309103803229625}},color={0,0,127}));
  connect(sinHeaWat_etsHotWatStub_3d70d616.ports[1],SpawnLoad_909d187e.ports_bHeaWat[1])
    annotation (Line(points={{26.738046951592622,-26.110468920800315},{46.73804695159262,-26.110468920800315},{46.73804695159262,-6.110468920800315},{46.73804695159262,13.889531079199678},{46.73804695159262,33.88953107919968},{66.73804695159262,33.88953107919968}},color={0,0,127}));

  //
  // End Connect Statements for 727eab20
  //



  //
  // Begin Connect Statements for b281bcee
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // cooling indirect and network 2 pipe

  connect(disNet_ab4120b7.ports_bCon[1],cooInd_4e81dd87.port_a1)
    annotation (Line(points={{0.35862565150237913,31.243765761584207},{20.35862565150238,31.243765761584207}},color={0,0,127}));
  connect(disNet_ab4120b7.ports_aCon[1],cooInd_4e81dd87.port_b1)
    annotation (Line(points={{7.308819582002698,41.127585031260516},{27.308819582002698,41.127585031260516}},color={0,0,127}));

  //
  // End Connect Statements for b281bcee
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
