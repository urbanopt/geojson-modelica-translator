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

  // Models

  //
  // Begin Model Instance for disNet_c8ba1673
  // Source template: /model_connectors/networks/templates/Network2Pipe_Instance.mopt
  //
parameter Integer nBui_disNet_c8ba1673=1;
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_disNet_c8ba1673=sum({
    cooInd_4d682cda.mDis_flow_nominal})
    "Nominal mass flow rate of the distribution pump";
  parameter Modelica.Units.SI.MassFlowRate mCon_flow_nominal_disNet_c8ba1673[nBui_disNet_c8ba1673]={
    cooInd_4d682cda.mDis_flow_nominal}
    "Nominal mass flow rate in each connection line";
  parameter Modelica.Units.SI.PressureDifference dpDis_nominal_disNet_c8ba1673[nBui_disNet_c8ba1673](
    each min=0,
    each displayUnit="Pa")=1/2 .* cat(
    1,
    {dp_nominal_disNet_c8ba1673*0.1},
    fill(
      dp_nominal_disNet_c8ba1673*0.9/(nBui_disNet_c8ba1673-1),
      nBui_disNet_c8ba1673-1))
    "Pressure drop between each connected building at nominal conditions (supply line)";
  parameter Modelica.Units.SI.PressureDifference dp_nominal_disNet_c8ba1673=dpSetPoi_disNet_c8ba1673+nBui_disNet_c8ba1673*7000
    "District network pressure drop";
  // NOTE: this differential pressure setpoint is currently utilized by plants elsewhere
  parameter Modelica.Units.SI.Pressure dpSetPoi_disNet_c8ba1673=50000
    "Differential pressure setpoint";

  Buildings.Experimental.DHC.Networks.Distribution2Pipe disNet_c8ba1673(
    redeclare final package Medium=MediumW,
    final nCon=nBui_disNet_c8ba1673,
    iConDpSen=nBui_disNet_c8ba1673,
    final mDis_flow_nominal=mDis_flow_nominal_disNet_c8ba1673,
    final mCon_flow_nominal=mCon_flow_nominal_disNet_c8ba1673,
    final allowFlowReversal=false,
    dpDis_nominal=dpDis_nominal_disNet_c8ba1673)
    "Distribution network."
    annotation (Placement(transformation(extent={{-30.0,60.0},{-10.0,70.0}})));
  //
  // End Model Instance for disNet_c8ba1673
  //


  
  //
  // Begin Model Instance for cooPla_f1477eff
  // Source template: /model_connectors/plants/templates/CoolingPlant_Instance.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mCHW_flow_nominal_cooPla_f1477eff=cooPla_f1477eff.numChi*(cooPla_f1477eff.perChi.mEva_flow_nominal)
    "Nominal chilled water mass flow rate";
  parameter Modelica.Units.SI.MassFlowRate mCW_flow_nominal_cooPla_f1477eff=cooPla_f1477eff.perChi.mCon_flow_nominal
    "Nominal condenser water mass flow rate";
  parameter Modelica.Units.SI.PressureDifference dpCHW_nominal_cooPla_f1477eff=44.8*1000
    "Nominal chilled water side pressure";
  parameter Modelica.Units.SI.PressureDifference dpCW_nominal_cooPla_f1477eff=46.2*1000
    "Nominal condenser water side pressure";
  parameter Modelica.Units.SI.Power QEva_nominal_cooPla_f1477eff=mCHW_flow_nominal_cooPla_f1477eff*4200*(5-14)
    "Nominal cooling capaciaty (Negative means cooling)";
  parameter Modelica.Units.SI.MassFlowRate mMin_flow_cooPla_f1477eff=0.2*mCHW_flow_nominal_cooPla_f1477eff/cooPla_f1477eff.numChi
    "Minimum mass flow rate of single chiller";
  // control settings
  parameter Modelica.Units.SI.Pressure dpSetPoi_cooPla_f1477eff=70000
    "Differential pressure setpoint";
  parameter Modelica.Units.SI.Pressure pumDP_cooPla_f1477eff=dpCHW_nominal_cooPla_f1477eff+dpSetPoi_cooPla_f1477eff+200000;
  parameter Modelica.Units.SI.Time tWai_cooPla_f1477eff=30
    "Waiting time";
  // pumps
  parameter Buildings.Fluid.Movers.Data.Generic perCHWPum_cooPla_f1477eff(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=((mCHW_flow_nominal_cooPla_f1477eff/cooPla_f1477eff.numChi)/1000)*{0.1,1,1.2},
      dp=pumDP_cooPla_f1477eff*{1.2,1,0.1}))
    "Performance data for chilled water pumps";
  parameter Buildings.Fluid.Movers.Data.Generic perCWPum_cooPla_f1477eff(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=mCW_flow_nominal_cooPla_f1477eff/1000*{0.2,0.6,1.0,1.2},
      dp=(dpCW_nominal_cooPla_f1477eff+60000+6000)*{1.2,1.1,1.0,0.6}))
    "Performance data for condenser water pumps";


  Modelica.Blocks.Sources.RealExpression TSetChiWatDis_cooPla_f1477eff(
    y=5+273.15)
    "Chilled water supply temperature set point on district level."
    annotation (Placement(transformation(extent={{10.0,-70.0},{30.0,-50.0}})));
  Modelica.Blocks.Sources.BooleanConstant on_cooPla_f1477eff
    "On signal of the plant"
    annotation (Placement(transformation(extent={{50.0,-70.0},{70.0,-50.0}})));

  spawn_district_heating_and_cooling_systems.Plants.CentralCoolingPlant cooPla_f1477eff(
    redeclare Buildings.Fluid.Chillers.Data.ElectricEIR.ElectricEIRChiller_Carrier_19EX_5208kW_6_88COP_Vanes perChi,
    perCHWPum=perCHWPum_cooPla_f1477eff,
    perCWPum=perCWPum_cooPla_f1477eff,
    mCHW_flow_nominal=mCHW_flow_nominal_cooPla_f1477eff,
    dpCHW_nominal=dpCHW_nominal_cooPla_f1477eff,
    QEva_nominal=QEva_nominal_cooPla_f1477eff,
    mMin_flow=mMin_flow_cooPla_f1477eff,
    mCW_flow_nominal=mCW_flow_nominal_cooPla_f1477eff,
    dpCW_nominal=dpCW_nominal_cooPla_f1477eff,
    TAirInWB_nominal=298.7,
    TCW_nominal=308.15,
    TMin=288.15,
    tWai=tWai_cooPla_f1477eff,
    dpSetPoi=dpSetPoi_cooPla_f1477eff
    )
    "District cooling plant."
    annotation (Placement(transformation(extent={{-70.0,50.0},{-50.0,70.0}})));
  //
  // End Model Instance for cooPla_f1477eff
  //


  
  //
  // Begin Model Instance for disNet_87ea6b5d
  // Source template: /model_connectors/networks/templates/Network2Pipe_Instance.mopt
  //
parameter Integer nBui_disNet_87ea6b5d=1;
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_disNet_87ea6b5d=sum({
    heaInd_6a5974be.mDis_flow_nominal})
    "Nominal mass flow rate of the distribution pump";
  parameter Modelica.Units.SI.MassFlowRate mCon_flow_nominal_disNet_87ea6b5d[nBui_disNet_87ea6b5d]={
    heaInd_6a5974be.mDis_flow_nominal}
    "Nominal mass flow rate in each connection line";
  parameter Modelica.Units.SI.PressureDifference dpDis_nominal_disNet_87ea6b5d[nBui_disNet_87ea6b5d](
    each min=0,
    each displayUnit="Pa")=1/2 .* cat(
    1,
    {dp_nominal_disNet_87ea6b5d*0.1},
    fill(
      dp_nominal_disNet_87ea6b5d*0.9/(nBui_disNet_87ea6b5d-1),
      nBui_disNet_87ea6b5d-1))
    "Pressure drop between each connected building at nominal conditions (supply line)";
  parameter Modelica.Units.SI.PressureDifference dp_nominal_disNet_87ea6b5d=dpSetPoi_disNet_87ea6b5d+nBui_disNet_87ea6b5d*7000
    "District network pressure drop";
  // NOTE: this differential pressure setpoint is currently utilized by plants elsewhere
  parameter Modelica.Units.SI.Pressure dpSetPoi_disNet_87ea6b5d=50000
    "Differential pressure setpoint";

  Buildings.Experimental.DHC.Networks.Distribution2Pipe disNet_87ea6b5d(
    redeclare final package Medium=MediumW,
    final nCon=nBui_disNet_87ea6b5d,
    iConDpSen=nBui_disNet_87ea6b5d,
    final mDis_flow_nominal=mDis_flow_nominal_disNet_87ea6b5d,
    final mCon_flow_nominal=mCon_flow_nominal_disNet_87ea6b5d,
    final allowFlowReversal=false,
    dpDis_nominal=dpDis_nominal_disNet_87ea6b5d)
    "Distribution network."
    annotation (Placement(transformation(extent={{-30.0,20.0},{-10.0,30.0}})));
  //
  // End Model Instance for disNet_87ea6b5d
  //


  
  //
  // Begin Model Instance for heaPla436da72a
  // Source template: /model_connectors/plants/templates/HeatingPlant_Instance.mopt
  //
  // heating plant instance
  parameter Modelica.Units.SI.MassFlowRate mHW_flow_nominal_heaPla436da72a=mBoi_flow_nominal_heaPla436da72a*heaPla436da72a.numBoi
    "Nominal heating water mass flow rate";
  parameter Modelica.Units.SI.MassFlowRate mBoi_flow_nominal_heaPla436da72a=QBoi_nominal_heaPla436da72a/(4200*heaPla436da72a.delT_nominal)
    "Nominal heating water mass flow rate";
  parameter Modelica.Units.SI.Power QBoi_nominal_heaPla436da72a=Q_flow_nominal_heaPla436da72a/heaPla436da72a.numBoi
    "Nominal heating capaciaty";
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_heaPla436da72a=1000000*2
    "Heating load";
  parameter Modelica.Units.SI.MassFlowRate mMin_flow_heaPla436da72a=0.2*mBoi_flow_nominal_heaPla436da72a
    "Minimum mass flow rate of single boiler";
  // controls
  parameter Modelica.Units.SI.Pressure pumDP=(heaPla436da72a.dpBoi_nominal+dpSetPoi_disNet_87ea6b5d+50000)
    "Heating water pump pressure drop";
  parameter Modelica.Units.SI.Time tWai_heaPla436da72a=30
    "Waiting time";
  parameter Buildings.Fluid.Movers.Data.Generic perHWPum_heaPla436da72a(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=mBoi_flow_nominal_heaPla436da72a/1000*{0.1,1.1},
      dp=pumDP*{1.1,0.1}))
    "Performance data for heating water pumps";

  spawn_district_heating_and_cooling_systems.Plants.CentralHeatingPlant heaPla436da72a(
    perHWPum=perHWPum_heaPla436da72a,
    mHW_flow_nominal=mHW_flow_nominal_heaPla436da72a,
    QBoi_flow_nominal=QBoi_nominal_heaPla436da72a,
    mMin_flow=mMin_flow_heaPla436da72a,
    mBoi_flow_nominal=mBoi_flow_nominal_heaPla436da72a,
    dpBoi_nominal=10000,
    delT_nominal(
      displayUnit="degC")=15,
    tWai=tWai_heaPla436da72a,
    // TODO: we're currently grabbing dpSetPoi from the Network instance -- need feedback to determine if that's the proper "home" for it
    dpSetPoi=dpSetPoi_disNet_87ea6b5d
    )
    "District heating plant."
    annotation (Placement(transformation(extent={{-70.0,10.0},{-50.0,30.0}})));
  //
  // End Model Instance for heaPla436da72a
  //


  
  //
  // Begin Model Instance for SpawnLoad_a951c97a
  // Source template: /model_connectors/load_connectors/templates/Spawn_Instance.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mLoaCoo_flow_nominal_SpawnLoad_a951c97a[SpawnLoad_a951c97a.nZon]={(-1*SpawnLoad_a951c97a.QCoo_flow_nominal[i]*(0.06)/1000) for i in 1:SpawnLoad_a951c97a.nZon};
  parameter Modelica.Units.SI.MassFlowRate mLoaHea_flow_nominal_SpawnLoad_a951c97a[SpawnLoad_a951c97a.nZon]={(SpawnLoad_a951c97a.QHea_flow_nominal[i]*(0.05)/1000) for i in 1:SpawnLoad_a951c97a.nZon};
  spawn_district_heating_and_cooling_systems.Loads.B5a6b99ec37f4de7f94020090.building SpawnLoad_a951c97a(
    mLoaCoo_flow_nominal=mLoaCoo_flow_nominal_SpawnLoad_a951c97a,
    mLoaHea_flow_nominal=mLoaHea_flow_nominal_SpawnLoad_a951c97a,
    nPorts_aHeaWat=1,
    nPorts_bHeaWat=1,
    nPorts_aChiWat=1,
    nPorts_bChiWat=1,
    have_pum=true)
    "Building spawn model"
    annotation (Placement(transformation(extent={{50.0,50.0},{70.0,70.0}})));
  //
  // End Model Instance for SpawnLoad_a951c97a
  //


  
  //
  // Begin Model Instance for cooInd_4d682cda
  // Source template: /model_connectors/energy_transfer_systems/templates/CoolingIndirect_Instance.mopt
  //
  // cooling indirect instance
  spawn_district_heating_and_cooling_systems.Substations.CoolingIndirect_5a6b99ec37f4de7f94020090 cooInd_4d682cda(
    redeclare package Medium=MediumW,
    allowFlowReversal1=true,
    allowFlowReversal2=true,
    mDis_flow_nominal=mDis_flow_nominal_baad8f13,
    mBui_flow_nominal=mBui_flow_nominal_baad8f13,
    dp1_nominal=500,
    dp2_nominal=500,
    dpValve_nominal=7000,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_baad8f13,
    // TODO: dehardcode the nominal temperatures?
    T_a1_nominal=273.15+5,
    T_a2_nominal=273.15+13)
    "Indirect cooling energy transfer station ETS."
    annotation (Placement(transformation(extent={{10.0,50.0},{30.0,70.0}})));
  //
  // End Model Instance for cooInd_4d682cda
  //


  
  //
  // Begin Model Instance for heaInd_6a5974be
  // Source template: /model_connectors/energy_transfer_systems/templates/HeatingIndirect_Instance.mopt
  //
  // heating indirect instance
  spawn_district_heating_and_cooling_systems.Substations.HeatingIndirect_5a6b99ec37f4de7f94020090 heaInd_6a5974be(
    allowFlowReversal1=true,
    allowFlowReversal2=true,
    show_T=true,
    redeclare package Medium=MediumW,
    mDis_flow_nominal=mDis_flow_nominal_83187da1,
    mBui_flow_nominal=mBui_flow_nominal_83187da1,
    dpValve_nominal=6000,
    dp1_nominal=500,
    dp2_nominal=500,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_83187da1,
    T_a1_nominal=55+273.15,
    T_a2_nominal=35+273.15,
    k=0.1,
    Ti=60,
    reverseActing=true)
    annotation (Placement(transformation(extent={{10.0,10.0},{30.0,30.0}})));
  //
  // End Model Instance for heaInd_6a5974be
  //


  

  // Model dependencies

  //
  // Begin Component Definitions for 84b15b23
  // Source template: /model_connectors/couplings/templates/Network2Pipe_CoolingPlant/ComponentDefinitions.mopt
  //
  // No components for pipe and cooling plant

  //
  // End Component Definitions for 84b15b23
  //



  //
  // Begin Component Definitions for 4d3052bd
  // Source template: /model_connectors/couplings/templates/Network2Pipe_HeatingPlant/ComponentDefinitions.mopt
  //
  // TODO: This should not be here, it is entirely plant specific and should be moved elsewhere
  // but since it requires a connect statement we must put it here for now...
  Modelica.Blocks.Sources.BooleanConstant mPum_flow_4d3052bd(
    k=true)
    "Total heating water pump mass flow rate"
    annotation (Placement(transformation(extent={{-70.0,-30.0},{-50.0,-10.0}})));
  // TODO: This should not be here, it is entirely plant specific and should be moved elsewhere
  // but since it requires a connect statement we must put it here for now...
  Modelica.Blocks.Sources.RealExpression TDisSetHeaWat_4d3052bd(
    each y=273.15+54)
    "District side heating water supply temperature set point."
    annotation (Placement(transformation(extent={{-30.0,-30.0},{-10.0,-10.0}})));

  //
  // End Component Definitions for 4d3052bd
  //



  //
  // Begin Component Definitions for baad8f13
  // Source template: /model_connectors/couplings/templates/Spawn_CoolingIndirect/ComponentDefinitions.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_baad8f13=SpawnLoad_a951c97a.disFloCoo.m_flow_nominal*delChiWatTemBui/delChiWatTemDis
    "Nominal mass flow rate of primary (district) district cooling side"; // TODO: verify this is ok!
  parameter Modelica.Units.SI.MassFlowRate mBui_flow_nominal_baad8f13=SpawnLoad_a951c97a.terUni[1].mChiWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district cooling side"; // TODO: verify this is ok!
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_baad8f13=-1*SpawnLoad_a951c97a.QHea_flow_nominal[1]; // TODO: verify this is ok!
  Modelica.Fluid.Sources.FixedBoundary pressure_source_baad8f13(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{10.0,-30.0},{30.0,-10.0}})));
  // TODO: move TChiWatSet (and its connection) into a CoolingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression TChiWatSet_baad8f13(
    y=7+273.15)
    //Dehardcode
    "Primary loop (district side) chilled water setpoint temperature."
    annotation (Placement(transformation(extent={{50.0,-30.0},{70.0,-10.0}})));

  //
  // End Component Definitions for baad8f13
  //



  //
  // Begin Component Definitions for 0d64611e
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for cooling indirect and network 2 pipe

  //
  // End Component Definitions for 0d64611e
  //



  //
  // Begin Component Definitions for 83187da1
  // Source template: /model_connectors/couplings/templates/Spawn_HeatingIndirect/ComponentDefinitions.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_83187da1=SpawnLoad_a951c97a.disFloHea.m_flow_nominal*delHeaWatTemBui/delHeaWatTemDis
    "Nominal mass flow rate of primary (district) district heating side"; // TODO: Verify this is ok!
  parameter Modelica.Units.SI.MassFlowRate mBui_flow_nominal_83187da1=SpawnLoad_a951c97a.terUni[1].mHeaWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district heating side"; // TODO: Verify this is ok!
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_83187da1=SpawnLoad_a951c97a.QHea_flow_nominal[1]; // TODO: Verify this is ok!
  Modelica.Fluid.Sources.FixedBoundary pressure_source_83187da1(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{-70.0,-70.0},{-50.0,-50.0}})));
  // TODO: move THeaWatSet (and its connection) into a HeatingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression THeaWatSet_83187da1(
    // y=40+273.15)
    y=273.15+40 )
    "Secondary loop (Building side) heating water setpoint temperature."
    //Dehardcode
    annotation (Placement(transformation(extent={{-30.0,-70.0},{-10.0,-50.0}})));

  //
  // End Component Definitions for 83187da1
  //



  //
  // Begin Component Definitions for 173a87f8
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for heating indirect and network 2 pipe

  //
  // End Component Definitions for 173a87f8
  //



equation
  // Connections

  //
  // Begin Connect Statements for 84b15b23
  // Source template: /model_connectors/couplings/templates/Network2Pipe_CoolingPlant/ConnectStatements.mopt
  //

  // TODO: these connect statements shouldn't be here, they are plant specific
  // but since we can't currently make connect statements for single systems, this is what we've got
  connect(on_cooPla_f1477eff.y,cooPla_f1477eff.on)
    annotation (Line(points={{50.166701517916295,-44.64683827779368},{30.166701517916295,-44.64683827779368},{30.166701517916295,-24.646838277793677},{30.166701517916295,-4.646838277793677},{30.166701517916295,15.353161722206323},{30.166701517916295,35.35316172220632},{10.166701517916295,35.35316172220632},{-9.833298482083705,35.35316172220632},{-29.833298482083705,35.35316172220632},{-49.833298482083705,35.35316172220632},{-49.833298482083705,55.35316172220632},{-69.8332984820837,55.35316172220632}},color={0,0,127}));
  connect(TSetChiWatDis_cooPla_f1477eff.y,cooPla_f1477eff.TCHWSupSet)
    annotation (Line(points={{23.935449276096364,-45.15302912343407},{3.9354492760963637,-45.15302912343407},{3.9354492760963637,-25.153029123434067},{3.9354492760963637,-5.153029123434067},{3.9354492760963637,14.846970876565933},{3.9354492760963637,34.84697087656593},{-16.064550723903636,34.84697087656593},{-36.06455072390364,34.84697087656593},{-36.06455072390364,54.84697087656593},{-56.06455072390364,54.84697087656593}},color={0,0,127}));

  connect(disNet_c8ba1673.port_bDisRet,cooPla_f1477eff.port_a)
    annotation (Line(points={{-38.82267462135053,61.74617225168657},{-58.82267462135053,61.74617225168657}},color={0,0,127}));
  connect(cooPla_f1477eff.port_b,disNet_c8ba1673.port_aDisSup)
    annotation (Line(points={{-37.04020330164088,69.09808902873408},{-17.040203301640872,69.09808902873408}},color={0,0,127}));
  connect(disNet_c8ba1673.dp,cooPla_f1477eff.dpMea)
    annotation (Line(points={{-44.69513666194535,65.30499789474091},{-64.69513666194536,65.30499789474091}},color={0,0,127}));

  //
  // End Connect Statements for 84b15b23
  //



  //
  // Begin Connect Statements for 4d3052bd
  // Source template: /model_connectors/couplings/templates/Network2Pipe_HeatingPlant/ConnectStatements.mopt
  //

  connect(heaPla436da72a.port_a,disNet_87ea6b5d.port_bDisRet)
    annotation (Line(points={{-44.52643475586253,15.810933087287054},{-24.52643475586254,15.810933087287054}},color={0,0,127}));
  connect(disNet_87ea6b5d.dp,heaPla436da72a.dpMea)
    annotation (Line(points={{-43.396061989404956,14.133304401277826},{-63.396061989404956,14.133304401277826}},color={0,0,127}));
  connect(heaPla436da72a.port_b,disNet_87ea6b5d.port_aDisSup)
    annotation (Line(points={{-46.881222548709964,26.399197673658847},{-26.881222548709964,26.399197673658847}},color={0,0,127}));
  connect(mPum_flow_4d3052bd.y,heaPla436da72a.on)
    annotation (Line(points={{-57.376751153822966,-6.322677356347555},{-57.376751153822966,13.677322643652445}},color={0,0,127}));
  connect(TDisSetHeaWat_4d3052bd.y,heaPla436da72a.THeaSet)
    annotation (Line(points={{-27.582847019580647,-2.6201003644747374},{-47.58284701958065,-2.6201003644747374},{-47.58284701958065,17.379899635525263},{-67.58284701958064,17.379899635525263}},color={0,0,127}));

  //
  // End Connect Statements for 4d3052bd
  //



  //
  // Begin Connect Statements for baad8f13
  // Source template: /model_connectors/couplings/templates/Spawn_CoolingIndirect/ConnectStatements.mopt
  //

  connect(SpawnLoad_a951c97a.ports_bChiWat[1], cooInd_4d682cda.port_a2)
    annotation (Line(points={{37.26641361846528,59.461312810024616},{17.26641361846528,59.461312810024616}},color={0,0,127}));
  connect(cooInd_4d682cda.port_b2,SpawnLoad_a951c97a.ports_aChiWat[1])
    annotation (Line(points={{38.28348716110008,69.09958051007065},{58.28348716110008,69.09958051007065}},color={0,0,127}));
  connect(pressure_source_baad8f13.ports[1], cooInd_4d682cda.port_b2)
    annotation (Line(points={{18.491110599552627,7.080569278328767},{-1.508889400447373,7.080569278328767},{-1.508889400447373,27.08056927832876},{-1.508889400447373,47.08056927832876},{-1.508889400447373,67.08056927832877},{18.491110599552627,67.08056927832877}},color={0,0,127}));
  connect(TChiWatSet_baad8f13.y,cooInd_4d682cda.TSetBuiSup)
    annotation (Line(points={{63.55413995158486,-3.461154192415279},{63.55413995158486,16.53884580758472},{63.55413995158486,36.53884580758473},{63.55413995158486,56.53884580758473}},color={0,0,127}));

  //
  // End Connect Statements for baad8f13
  //



  //
  // Begin Connect Statements for 0d64611e
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // cooling indirect and network 2 pipe
  
  connect(disNet_c8ba1673.ports_bCon[1],cooInd_4d682cda.port_a1)
    annotation (Line(points={{1.4738424002183592,69.89689479839637},{21.47384240021836,69.89689479839637}},color={0,0,127}));
  connect(disNet_c8ba1673.ports_aCon[1],cooInd_4d682cda.port_b1)
    annotation (Line(points={{2.0370502834616815,61.07685904813155},{22.03705028346168,61.07685904813155}},color={0,0,127}));

  //
  // End Connect Statements for 0d64611e
  //



  //
  // Begin Connect Statements for 83187da1
  // Source template: /model_connectors/couplings/templates/Spawn_HeatingIndirect/ConnectStatements.mopt
  //

  connect(SpawnLoad_a951c97a.ports_bHeaWat[1], heaInd_6a5974be.port_a2)
    annotation (Line(points={{52.24268702926514,33.90880376543802},{52.24268702926514,13.908803765438023},{32.24268702926513,13.908803765438023},{12.242687029265127,13.908803765438023}},color={0,0,127}));
  connect(heaInd_6a5974be.port_b2,SpawnLoad_a951c97a.ports_aHeaWat[1])
    annotation (Line(points={{28.897919596661467,31.80215058534175},{48.89791959666147,31.80215058534175},{48.89791959666147,51.80215058534175},{68.89791959666147,51.80215058534175}},color={0,0,127}));
  connect(pressure_source_83187da1.ports[1], heaInd_6a5974be.port_b2)
    annotation (Line(points={{-67.02798530762956,-40.66562863631273},{-47.02798530762957,-40.66562863631273},{-47.02798530762957,-20.665628636312718},{-47.02798530762957,-0.665628636312718},{-27.02798530762957,-0.665628636312718},{-7.027985307629578,-0.665628636312718},{-7.027985307629578,19.334371363687282},{12.972014692370422,19.334371363687282}},color={0,0,127}));
  connect(THeaWatSet_83187da1.y,heaInd_6a5974be.TSetBuiSup)
    annotation (Line(points={{-22.193455989990497,-38.008361571654774},{-2.193455989990497,-38.008361571654774},{-2.193455989990497,-18.00836157165479},{-2.193455989990497,1.9916384283452118},{-2.193455989990497,21.99163842834521},{17.806544010009503,21.99163842834521}},color={0,0,127}));

  //
  // End Connect Statements for 83187da1
  //



  //
  // Begin Connect Statements for 173a87f8
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // heating indirect and network 2 pipe
  
  connect(disNet_87ea6b5d.ports_bCon[1],heaInd_6a5974be.port_a1)
    annotation (Line(points={{8.90300150620277,14.688100745958423},{28.90300150620277,14.688100745958423}},color={0,0,127}));
  connect(disNet_87ea6b5d.ports_aCon[1],heaInd_6a5974be.port_b1)
    annotation (Line(points={{5.815785268919697,14.471842460325135},{25.815785268919697,14.471842460325135}},color={0,0,127}));

  //
  // End Connect Statements for 173a87f8
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