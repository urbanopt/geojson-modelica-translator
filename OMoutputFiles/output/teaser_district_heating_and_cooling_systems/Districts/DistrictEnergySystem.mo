within teaser_district_heating_and_cooling_systems.Districts;
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
  // Begin Model Instance for disNet_b19be277
  // Source template: /model_connectors/networks/templates/Network2Pipe_Instance.mopt
  //
parameter Integer nBui_disNet_b19be277=2;
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_disNet_b19be277=sum({
    cooInd_66ab1bcf.mDis_flow_nominal,
  cooInd_e0ceb13d.mDis_flow_nominal})
    "Nominal mass flow rate of the distribution pump";
  parameter Modelica.Units.SI.MassFlowRate mCon_flow_nominal_disNet_b19be277[nBui_disNet_b19be277]={
    cooInd_66ab1bcf.mDis_flow_nominal,
  cooInd_e0ceb13d.mDis_flow_nominal}
    "Nominal mass flow rate in each connection line";
  parameter Modelica.Units.SI.PressureDifference dpDis_nominal_disNet_b19be277[nBui_disNet_b19be277](
    each min=0,
    each displayUnit="Pa")=1/2 .* cat(
    1,
    {dp_nominal_disNet_b19be277*0.1},
    fill(
      dp_nominal_disNet_b19be277*0.9/(nBui_disNet_b19be277-1),
      nBui_disNet_b19be277-1))
    "Pressure drop between each connected building at nominal conditions (supply line)";
  parameter Modelica.Units.SI.PressureDifference dp_nominal_disNet_b19be277=dpSetPoi_disNet_b19be277+nBui_disNet_b19be277*7000
    "District network pressure drop";
  // NOTE: this differential pressure setpoint is currently utilized by plants elsewhere
  parameter Modelica.Units.SI.Pressure dpSetPoi_disNet_b19be277=50000
    "Differential pressure setpoint";

  Buildings.Experimental.DHC.Networks.Distribution2Pipe disNet_b19be277(
    redeclare final package Medium=MediumW,
    final nCon=nBui_disNet_b19be277,
    iConDpSen=nBui_disNet_b19be277,
    final mDis_flow_nominal=mDis_flow_nominal_disNet_b19be277,
    final mCon_flow_nominal=mCon_flow_nominal_disNet_b19be277,
    final allowFlowReversal=false,
    dpDis_nominal=dpDis_nominal_disNet_b19be277)
    "Distribution network."
    annotation (Placement(transformation(extent={{-30.0,120.0},{-10.0,130.0}})));
  //
  // End Model Instance for disNet_b19be277
  //



  //
  // Begin Model Instance for cooPla_16803a71
  // Source template: /model_connectors/plants/templates/CoolingPlant_Instance.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mCHW_flow_nominal_cooPla_16803a71=cooPla_16803a71.numChi*(cooPla_16803a71.perChi.mEva_flow_nominal)
    "Nominal chilled water mass flow rate";
  parameter Modelica.Units.SI.MassFlowRate mCW_flow_nominal_cooPla_16803a71=cooPla_16803a71.perChi.mCon_flow_nominal
    "Nominal condenser water mass flow rate";
  parameter Modelica.Units.SI.PressureDifference dpCHW_nominal_cooPla_16803a71=44.8*1000
    "Nominal chilled water side pressure";
  parameter Modelica.Units.SI.PressureDifference dpCW_nominal_cooPla_16803a71=46.2*1000
    "Nominal condenser water side pressure";
  parameter Modelica.Units.SI.Power QEva_nominal_cooPla_16803a71=mCHW_flow_nominal_cooPla_16803a71*4200*(5-14)
    "Nominal cooling capaciaty (Negative means cooling)";
  parameter Modelica.Units.SI.MassFlowRate mMin_flow_cooPla_16803a71=0.2*mCHW_flow_nominal_cooPla_16803a71/cooPla_16803a71.numChi
    "Minimum mass flow rate of single chiller";
  // control settings
  parameter Modelica.Units.SI.Pressure dpSetPoi_cooPla_16803a71=70000
    "Differential pressure setpoint";
  parameter Modelica.Units.SI.Pressure pumDP_cooPla_16803a71=dpCHW_nominal_cooPla_16803a71+dpSetPoi_cooPla_16803a71+200000;
  parameter Modelica.Units.SI.Time tWai_cooPla_16803a71=30
    "Waiting time";
  // pumps
  parameter Buildings.Fluid.Movers.Data.Generic perCHWPum_cooPla_16803a71(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=((mCHW_flow_nominal_cooPla_16803a71/cooPla_16803a71.numChi)/1000)*{0.1,1,1.2},
      dp=pumDP_cooPla_16803a71*{1.2,1,0.1}))
    "Performance data for chilled water pumps";
  parameter Buildings.Fluid.Movers.Data.Generic perCWPum_cooPla_16803a71(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=mCW_flow_nominal_cooPla_16803a71/1000*{0.2,0.6,1.0,1.2},
      dp=(dpCW_nominal_cooPla_16803a71+60000+6000)*{1.2,1.1,1.0,0.6}))
    "Performance data for condenser water pumps";


  Modelica.Blocks.Sources.RealExpression TSetChiWatDis_cooPla_16803a71(
    y=5+273.15)
    "Chilled water supply temperature set point on district level."
    annotation (Placement(transformation(extent={{10.0,-130.0},{30.0,-110.0}})));
  Modelica.Blocks.Sources.BooleanConstant on_cooPla_16803a71
    "On signal of the plant"
    annotation (Placement(transformation(extent={{50.0,-130.0},{70.0,-110.0}})));

  teaser_district_heating_and_cooling_systems.Plants.CentralCoolingPlant cooPla_16803a71(
    redeclare Buildings.Fluid.Chillers.Data.ElectricEIR.ElectricEIRChiller_Carrier_19EX_5208kW_6_88COP_Vanes perChi,
    perCHWPum=perCHWPum_cooPla_16803a71,
    perCWPum=perCWPum_cooPla_16803a71,
    mCHW_flow_nominal=mCHW_flow_nominal_cooPla_16803a71,
    dpCHW_nominal=dpCHW_nominal_cooPla_16803a71,
    QEva_nominal=QEva_nominal_cooPla_16803a71,
    mMin_flow=mMin_flow_cooPla_16803a71,
    mCW_flow_nominal=mCW_flow_nominal_cooPla_16803a71,
    dpCW_nominal=dpCW_nominal_cooPla_16803a71,
    TAirInWB_nominal=298.7,
    TCW_nominal=308.15,
    TMin=288.15,
    tWai=tWai_cooPla_16803a71,
    dpSetPoi=dpSetPoi_cooPla_16803a71
    )
    "District cooling plant."
    annotation (Placement(transformation(extent={{-70.0,110.0},{-50.0,130.0}})));
  //
  // End Model Instance for cooPla_16803a71
  //



  //
  // Begin Model Instance for disNet_77c66200
  // Source template: /model_connectors/networks/templates/Network2Pipe_Instance.mopt
  //
parameter Integer nBui_disNet_77c66200=2;
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_disNet_77c66200=sum({
    heaInd_01742131.mDis_flow_nominal,
  heaInd_6a617e11.mDis_flow_nominal})
    "Nominal mass flow rate of the distribution pump";
  parameter Modelica.Units.SI.MassFlowRate mCon_flow_nominal_disNet_77c66200[nBui_disNet_77c66200]={
    heaInd_01742131.mDis_flow_nominal,
  heaInd_6a617e11.mDis_flow_nominal}
    "Nominal mass flow rate in each connection line";
  parameter Modelica.Units.SI.PressureDifference dpDis_nominal_disNet_77c66200[nBui_disNet_77c66200](
    each min=0,
    each displayUnit="Pa")=1/2 .* cat(
    1,
    {dp_nominal_disNet_77c66200*0.1},
    fill(
      dp_nominal_disNet_77c66200*0.9/(nBui_disNet_77c66200-1),
      nBui_disNet_77c66200-1))
    "Pressure drop between each connected building at nominal conditions (supply line)";
  parameter Modelica.Units.SI.PressureDifference dp_nominal_disNet_77c66200=dpSetPoi_disNet_77c66200+nBui_disNet_77c66200*7000
    "District network pressure drop";
  // NOTE: this differential pressure setpoint is currently utilized by plants elsewhere
  parameter Modelica.Units.SI.Pressure dpSetPoi_disNet_77c66200=50000
    "Differential pressure setpoint";

  Buildings.Experimental.DHC.Networks.Distribution2Pipe disNet_77c66200(
    redeclare final package Medium=MediumW,
    final nCon=nBui_disNet_77c66200,
    iConDpSen=nBui_disNet_77c66200,
    final mDis_flow_nominal=mDis_flow_nominal_disNet_77c66200,
    final mCon_flow_nominal=mCon_flow_nominal_disNet_77c66200,
    final allowFlowReversal=false,
    dpDis_nominal=dpDis_nominal_disNet_77c66200)
    "Distribution network."
    annotation (Placement(transformation(extent={{-30.0,80.0},{-10.0,90.0}})));
  //
  // End Model Instance for disNet_77c66200
  //



  //
  // Begin Model Instance for heaPla2c906da4
  // Source template: /model_connectors/plants/templates/HeatingPlant_Instance.mopt
  //
  // heating plant instance
  parameter Modelica.Units.SI.MassFlowRate mHW_flow_nominal_heaPla2c906da4=mBoi_flow_nominal_heaPla2c906da4*heaPla2c906da4.numBoi
    "Nominal heating water mass flow rate";
  parameter Modelica.Units.SI.MassFlowRate mBoi_flow_nominal_heaPla2c906da4=QBoi_nominal_heaPla2c906da4/(4200*heaPla2c906da4.delT_nominal)
    "Nominal heating water mass flow rate";
  parameter Modelica.Units.SI.Power QBoi_nominal_heaPla2c906da4=Q_flow_nominal_heaPla2c906da4/heaPla2c906da4.numBoi
    "Nominal heating capaciaty";
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_heaPla2c906da4=1000000*2
    "Heating load";
  parameter Modelica.Units.SI.MassFlowRate mMin_flow_heaPla2c906da4=0.2*mBoi_flow_nominal_heaPla2c906da4
    "Minimum mass flow rate of single boiler";
  // controls
  parameter Modelica.Units.SI.Pressure pumDP=(heaPla2c906da4.dpBoi_nominal+dpSetPoi_disNet_77c66200+50000)
    "Heating water pump pressure drop";
  parameter Modelica.Units.SI.Time tWai_heaPla2c906da4=30
    "Waiting time";
  parameter Buildings.Fluid.Movers.Data.Generic perHWPum_heaPla2c906da4(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=mBoi_flow_nominal_heaPla2c906da4/1000*{0.1,1.1},
      dp=pumDP*{1.1,0.1}))
    "Performance data for heating water pumps";

  teaser_district_heating_and_cooling_systems.Plants.CentralHeatingPlant heaPla2c906da4(
    perHWPum=perHWPum_heaPla2c906da4,
    mHW_flow_nominal=mHW_flow_nominal_heaPla2c906da4,
    QBoi_flow_nominal=QBoi_nominal_heaPla2c906da4,
    mMin_flow=mMin_flow_heaPla2c906da4,
    mBoi_flow_nominal=mBoi_flow_nominal_heaPla2c906da4,
    dpBoi_nominal=10000,
    delT_nominal(
      displayUnit="degC")=15,
    tWai=tWai_heaPla2c906da4,
    // TODO: we're currently grabbing dpSetPoi from the Network instance -- need feedback to determine if that's the proper "home" for it
    dpSetPoi=dpSetPoi_disNet_77c66200
    )
    "District heating plant."
    annotation (Placement(transformation(extent={{-70.0,70.0},{-50.0,90.0}})));
  //
  // End Model Instance for heaPla2c906da4
  //



  //
  // Begin Model Instance for TeaserLoad_2a880683
  // Source template: /model_connectors/load_connectors/templates/Teaser_Instance.mopt
  //
  teaser_district_heating_and_cooling_systems.Loads.B5a6b99ec37f4de7f94020090.building TeaserLoad_2a880683(
    nPorts_aHeaWat=1,
    nPorts_bHeaWat=1,
    nPorts_aChiWat=1,
    nPorts_bChiWat=1)
    "Building with thermal loads as TEASER zones"
    annotation (Placement(transformation(extent={{50.0,110.0},{70.0,130.0}})));
  //
  // End Model Instance for TeaserLoad_2a880683
  //



  //
  // Begin Model Instance for cooInd_66ab1bcf
  // Source template: /model_connectors/energy_transfer_systems/templates/CoolingIndirect_Instance.mopt
  //
  // cooling indirect instance
  teaser_district_heating_and_cooling_systems.Substations.CoolingIndirect_5a6b99ec37f4de7f94020090 cooInd_66ab1bcf(
    redeclare package Medium=MediumW,
    allowFlowReversal1=true,
    allowFlowReversal2=true,
    mDis_flow_nominal=mDis_flow_nominal_c5e8ff3d,
    mBui_flow_nominal=mBui_flow_nominal_c5e8ff3d,
    dp1_nominal=500,
    dp2_nominal=500,
    dpValve_nominal=7000,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_c5e8ff3d,
    // TODO: dehardcode the nominal temperatures?
    T_a1_nominal=273.15+5,
    T_a2_nominal=273.15+13)
    "Indirect cooling energy transfer station ETS."
    annotation (Placement(transformation(extent={{10.0,70.0},{30.0,90.0}})));
  //
  // End Model Instance for cooInd_66ab1bcf
  //



  //
  // Begin Model Instance for heaInd_01742131
  // Source template: /model_connectors/energy_transfer_systems/templates/HeatingIndirect_Instance.mopt
  //
  // heating indirect instance
  teaser_district_heating_and_cooling_systems.Substations.HeatingIndirect_5a6b99ec37f4de7f94020090 heaInd_01742131(
    allowFlowReversal1=true,
    allowFlowReversal2=true,
    show_T=true,
    redeclare package Medium=MediumW,
    mDis_flow_nominal=mDis_flow_nominal_18a0df15,
    mBui_flow_nominal=mBui_flow_nominal_18a0df15,
    dpValve_nominal=6000,
    dp1_nominal=500,
    dp2_nominal=500,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_18a0df15,
    T_a1_nominal=55+273.15,
    T_a2_nominal=35+273.15,
    k=0.1,
    Ti=60,
    reverseActing=true)
    annotation (Placement(transformation(extent={{10.0,110.0},{30.0,130.0}})));
  //
  // End Model Instance for heaInd_01742131
  //



  //
  // Begin Model Instance for TeaserLoad_fc0ac7c8
  // Source template: /model_connectors/load_connectors/templates/Teaser_Instance.mopt
  //
  teaser_district_heating_and_cooling_systems.Loads.B5a72287837f4de77124f946a.building TeaserLoad_fc0ac7c8(
    nPorts_aHeaWat=1,
    nPorts_bHeaWat=1,
    nPorts_aChiWat=1,
    nPorts_bChiWat=1)
    "Building with thermal loads as TEASER zones"
    annotation (Placement(transformation(extent={{50.0,30.0},{70.0,50.0}})));
  //
  // End Model Instance for TeaserLoad_fc0ac7c8
  //



  //
  // Begin Model Instance for cooInd_e0ceb13d
  // Source template: /model_connectors/energy_transfer_systems/templates/CoolingIndirect_Instance.mopt
  //
  // cooling indirect instance
  teaser_district_heating_and_cooling_systems.Substations.CoolingIndirect_5a72287837f4de77124f946a cooInd_e0ceb13d(
    redeclare package Medium=MediumW,
    allowFlowReversal1=true,
    allowFlowReversal2=true,
    mDis_flow_nominal=mDis_flow_nominal_19964dfa,
    mBui_flow_nominal=mBui_flow_nominal_19964dfa,
    dp1_nominal=500,
    dp2_nominal=500,
    dpValve_nominal=7000,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_19964dfa,
    // TODO: dehardcode the nominal temperatures?
    T_a1_nominal=273.15+5,
    T_a2_nominal=273.15+13)
    "Indirect cooling energy transfer station ETS."
    annotation (Placement(transformation(extent={{10.0,30.0},{30.0,50.0}})));
  //
  // End Model Instance for cooInd_e0ceb13d
  //



  //
  // Begin Model Instance for heaInd_6a617e11
  // Source template: /model_connectors/energy_transfer_systems/templates/HeatingIndirect_Instance.mopt
  //
  // heating indirect instance
  teaser_district_heating_and_cooling_systems.Substations.HeatingIndirect_5a72287837f4de77124f946a heaInd_6a617e11(
    allowFlowReversal1=true,
    allowFlowReversal2=true,
    show_T=true,
    redeclare package Medium=MediumW,
    mDis_flow_nominal=mDis_flow_nominal_b7fca81e,
    mBui_flow_nominal=mBui_flow_nominal_b7fca81e,
    dpValve_nominal=6000,
    dp1_nominal=500,
    dp2_nominal=500,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_b7fca81e,
    T_a1_nominal=55+273.15,
    T_a2_nominal=35+273.15,
    k=0.1,
    Ti=60,
    reverseActing=true)
    annotation (Placement(transformation(extent={{10.0,-10.0},{30.0,10.0}})));
  //
  // End Model Instance for heaInd_6a617e11
  //




  // Model dependencies

  //
  // Begin Component Definitions for f74e497b
  // Source template: /model_connectors/couplings/templates/Network2Pipe_CoolingPlant/ComponentDefinitions.mopt
  //
  // No components for pipe and cooling plant

  //
  // End Component Definitions for f74e497b
  //



  //
  // Begin Component Definitions for fc810e6f
  // Source template: /model_connectors/couplings/templates/Network2Pipe_HeatingPlant/ComponentDefinitions.mopt
  //
  // TODO: This should not be here, it is entirely plant specific and should be moved elsewhere
  // but since it requires a connect statement we must put it here for now...
  Modelica.Blocks.Sources.BooleanConstant mPum_flow_fc810e6f(
    k=true)
    "Total heating water pump mass flow rate"
    annotation (Placement(transformation(extent={{-70.0,-50.0},{-50.0,-30.0}})));
  // TODO: This should not be here, it is entirely plant specific and should be moved elsewhere
  // but since it requires a connect statement we must put it here for now...
  Modelica.Blocks.Sources.RealExpression TDisSetHeaWat_fc810e6f(
    each y=273.15+54)
    "District side heating water supply temperature set point."
    annotation (Placement(transformation(extent={{-30.0,-50.0},{-10.0,-30.0}})));

  //
  // End Component Definitions for fc810e6f
  //



  //
  // Begin Component Definitions for c5e8ff3d
  // Source template: /model_connectors/couplings/templates/Teaser_CoolingIndirect/ComponentDefinitions.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_c5e8ff3d=TeaserLoad_2a880683.disFloCoo.m_flow_nominal*delChiWatTemBui/delChiWatTemDis
    "Nominal mass flow rate of primary (district) district cooling side"; // TODO: verify this is ok!
  parameter Modelica.Units.SI.MassFlowRate mBui_flow_nominal_c5e8ff3d=TeaserLoad_2a880683.terUni[1].mChiWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district cooling side"; // TODO: verify this is ok!
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_c5e8ff3d=-1*TeaserLoad_2a880683.terUni[1].QHea_flow_nominal; // TODO: verify this is ok!
  Modelica.Fluid.Sources.FixedBoundary pressure_source_c5e8ff3d(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{10.0,-50.0},{30.0,-30.0}})));
  // TODO: move TChiWatSet (and its connection) into a CoolingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression TChiWatSet_c5e8ff3d(
    y=7+273.15)
    //Dehardcode
    "Primary loop (district side) chilled water setpoint temperature."
    annotation (Placement(transformation(extent={{50.0,-50.0},{70.0,-30.0}})));

  //
  // End Component Definitions for c5e8ff3d
  //



  //
  // Begin Component Definitions for ccff210c
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for cooling indirect and network 2 pipe

  //
  // End Component Definitions for ccff210c
  //



  //
  // Begin Component Definitions for 18a0df15
  // Source template: /model_connectors/couplings/templates/Teaser_HeatingIndirect/ComponentDefinitions.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_18a0df15=TeaserLoad_2a880683.disFloHea.m_flow_nominal*delHeaWatTemBui/delHeaWatTemDis
    "Nominal mass flow rate of primary (district) district heating side"; // TODO: Verify this is ok!
  parameter Modelica.Units.SI.MassFlowRate mBui_flow_nominal_18a0df15=TeaserLoad_2a880683.terUni[1].mHeaWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district heating side"; // TODO: Verify this is ok!
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_18a0df15=TeaserLoad_2a880683.terUni[1].QHea_flow_nominal; // TODO: Verify this is ok!
  Modelica.Fluid.Sources.FixedBoundary pressure_source_18a0df15(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{-70.0,-90.0},{-50.0,-70.0}})));
  // TODO: move THeaWatSet (and its connection) into a HeatingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression THeaWatSet_18a0df15(
    // y=40+273.15)
    y=273.15+40)
    "Secondary loop (Building side) heating water setpoint temperature."
    //Dehardcode
    annotation (Placement(transformation(extent={{-30.0,-90.0},{-10.0,-70.0}})));

  //
  // End Component Definitions for 18a0df15
  //



  //
  // Begin Component Definitions for d774ad50
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for heating indirect and network 2 pipe

  //
  // End Component Definitions for d774ad50
  //



  //
  // Begin Component Definitions for 19964dfa
  // Source template: /model_connectors/couplings/templates/Teaser_CoolingIndirect/ComponentDefinitions.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_19964dfa=TeaserLoad_fc0ac7c8.disFloCoo.m_flow_nominal*delChiWatTemBui/delChiWatTemDis
    "Nominal mass flow rate of primary (district) district cooling side"; // TODO: verify this is ok!
  parameter Modelica.Units.SI.MassFlowRate mBui_flow_nominal_19964dfa=TeaserLoad_fc0ac7c8.terUni[1].mChiWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district cooling side"; // TODO: verify this is ok!
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_19964dfa=-1*TeaserLoad_fc0ac7c8.terUni[1].QHea_flow_nominal; // TODO: verify this is ok!
  Modelica.Fluid.Sources.FixedBoundary pressure_source_19964dfa(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{10.0,-90.0},{30.0,-70.0}})));
  // TODO: move TChiWatSet (and its connection) into a CoolingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression TChiWatSet_19964dfa(
    y=7+273.15)
    //Dehardcode
    "Primary loop (district side) chilled water setpoint temperature."
    annotation (Placement(transformation(extent={{50.0,-90.0},{70.0,-70.0}})));

  //
  // End Component Definitions for 19964dfa
  //



  //
  // Begin Component Definitions for 641285b1
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for cooling indirect and network 2 pipe

  //
  // End Component Definitions for 641285b1
  //



  //
  // Begin Component Definitions for b7fca81e
  // Source template: /model_connectors/couplings/templates/Teaser_HeatingIndirect/ComponentDefinitions.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_b7fca81e=TeaserLoad_fc0ac7c8.disFloHea.m_flow_nominal*delHeaWatTemBui/delHeaWatTemDis
    "Nominal mass flow rate of primary (district) district heating side"; // TODO: Verify this is ok!
  parameter Modelica.Units.SI.MassFlowRate mBui_flow_nominal_b7fca81e=TeaserLoad_fc0ac7c8.terUni[1].mHeaWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district heating side"; // TODO: Verify this is ok!
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_b7fca81e=TeaserLoad_fc0ac7c8.terUni[1].QHea_flow_nominal; // TODO: Verify this is ok!
  Modelica.Fluid.Sources.FixedBoundary pressure_source_b7fca81e(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{-70.0,-130.0},{-50.0,-110.0}})));
  // TODO: move THeaWatSet (and its connection) into a HeatingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression THeaWatSet_b7fca81e(
    // y=40+273.15)
    y=273.15+40)
    "Secondary loop (Building side) heating water setpoint temperature."
    //Dehardcode
    annotation (Placement(transformation(extent={{-30.0,-130.0},{-10.0,-110.0}})));

  //
  // End Component Definitions for b7fca81e
  //



  //
  // Begin Component Definitions for 2c2ba738
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for heating indirect and network 2 pipe

  //
  // End Component Definitions for 2c2ba738
  //



equation
  // Connections

  //
  // Begin Connect Statements for f74e497b
  // Source template: /model_connectors/couplings/templates/Network2Pipe_CoolingPlant/ConnectStatements.mopt
  //

  // TODO: these connect statements shouldn't be here, they are plant specific
  // but since we can't currently make connect statements for single systems, this is what we've got
  connect(on_cooPla_16803a71.y,cooPla_16803a71.on)
    annotation (Line(points={{61.533894834170326,-91.68303829731272},{41.533894834170326,-91.68303829731272},{41.533894834170326,-71.68303829731272},{41.533894834170326,-51.68303829731272},{41.533894834170326,-31.68303829731272},{41.533894834170326,-11.68303829731272},{41.533894834170326,8.31696170268728},{41.533894834170326,28.31696170268728},{41.533894834170326,48.31696170268728},{41.533894834170326,68.31696170268728},{41.533894834170326,88.31696170268728},{41.533894834170326,108.31696170268728},{21.53389483417031,108.31696170268728},{1.5338948341703116,108.31696170268728},{-18.46610516582969,108.31696170268728},{-38.46610516582969,108.31696170268728},{-38.46610516582969,128.31696170268728},{-58.46610516582969,128.31696170268728}},color={0,0,127}));
  connect(TSetChiWatDis_cooPla_16803a71.y,cooPla_16803a71.TCHWSupSet)
    annotation (Line(points={{13.734715769761635,-96.35018557006569},{-6.265284230238365,-96.35018557006569},{-6.265284230238365,-76.35018557006569},{-6.265284230238365,-56.35018557006569},{-6.265284230238365,-36.35018557006569},{-6.265284230238365,-16.35018557006569},{-6.265284230238365,3.6498144299343096},{-6.265284230238365,23.649814429934295},{-6.265284230238365,43.649814429934295},{-6.265284230238365,63.649814429934295},{-6.265284230238365,83.6498144299343},{-6.265284230238365,103.6498144299343},{-26.265284230238365,103.6498144299343},{-46.265284230238365,103.6498144299343},{-46.265284230238365,123.6498144299343},{-66.26528423023836,123.6498144299343}},color={0,0,127}));

  connect(disNet_b19be277.port_bDisRet,cooPla_16803a71.port_a)
    annotation (Line(points={{-45.684000714742524,112.86984968472055},{-65.68400071474252,112.86984968472055}},color={0,0,127}));
  connect(cooPla_16803a71.port_b,disNet_b19be277.port_aDisSup)
    annotation (Line(points={{-43.50026652214913,129.93676741547694},{-23.500266522149133,129.93676741547694}},color={0,0,127}));
  connect(disNet_b19be277.dp,cooPla_16803a71.dpMea)
    annotation (Line(points={{-47.36720469408871,121.91636948425516},{-67.36720469408871,121.91636948425516}},color={0,0,127}));

  //
  // End Connect Statements for f74e497b
  //



  //
  // Begin Connect Statements for fc810e6f
  // Source template: /model_connectors/couplings/templates/Network2Pipe_HeatingPlant/ConnectStatements.mopt
  //

  connect(heaPla2c906da4.port_a,disNet_77c66200.port_bDisRet)
    annotation (Line(points={{-48.16058373797143,79.67538040312887},{-28.16058373797143,79.67538040312887}},color={0,0,127}));
  connect(disNet_77c66200.dp,heaPla2c906da4.dpMea)
    annotation (Line(points={{-48.989878131351176,76.56245058474484},{-68.98987813135118,76.56245058474484}},color={0,0,127}));
  connect(heaPla2c906da4.port_b,disNet_77c66200.port_aDisSup)
    annotation (Line(points={{-44.40759387076699,84.0414303657432},{-24.407593870766988,84.0414303657432}},color={0,0,127}));
  connect(mPum_flow_fc810e6f.y,heaPla2c906da4.on)
    annotation (Line(points={{-50.386829708279635,-26.81929011264083},{-50.386829708279635,-6.819290112640829},{-50.386829708279635,13.180709887359171},{-50.386829708279635,33.18070988735917},{-50.386829708279635,53.18070988735917},{-50.386829708279635,73.18070988735917}},color={0,0,127}));
  connect(TDisSetHeaWat_fc810e6f.y,heaPla2c906da4.THeaSet)
    annotation (Line(points={{-20.268051456180018,-24.16395396611597},{-20.268051456180018,-4.163953966115969},{-20.268051456180018,15.836046033884031},{-20.268051456180018,35.83604603388403},{-20.268051456180018,55.83604603388403},{-40.268051456180025,55.83604603388403},{-40.268051456180025,75.83604603388403},{-60.268051456180025,75.83604603388403}},color={0,0,127}));

  //
  // End Connect Statements for fc810e6f
  //



  //
  // Begin Connect Statements for c5e8ff3d
  // Source template: /model_connectors/couplings/templates/Teaser_CoolingIndirect/ConnectStatements.mopt
  //

  connect(TeaserLoad_2a880683.ports_bChiWat[1], cooInd_66ab1bcf.port_a2)
    annotation (Line(points={{53.1945286954321,104.27470814954056},{53.1945286954321,84.27470814954056},{33.1945286954321,84.27470814954056},{13.194528695432098,84.27470814954056}},color={0,0,127}));
  connect(cooInd_66ab1bcf.port_b2,TeaserLoad_2a880683.ports_aChiWat[1])
    annotation (Line(points={{29.938754534196903,92.14294306947792},{49.9387545341969,92.14294306947792},{49.9387545341969,112.14294306947792},{69.9387545341969,112.14294306947792}},color={0,0,127}));
  connect(pressure_source_c5e8ff3d.ports[1], cooInd_66ab1bcf.port_b2)
    annotation (Line(points={{24.097839412951103,-19.09036123000942},{4.097839412951103,-19.09036123000942},{4.097839412951103,0.909638769990579},{4.097839412951103,20.90963876999058},{4.097839412951103,40.90963876999059},{4.097839412951103,60.90963876999059},{4.097839412951103,80.9096387699906},{24.097839412951103,80.9096387699906}},color={0,0,127}));
  connect(TChiWatSet_c5e8ff3d.y,cooInd_66ab1bcf.TSetBuiSup)
    annotation (Line(points={{52.506748558905315,-15.5760656610299},{52.506748558905315,4.423934338970099},{52.506748558905315,24.423934338970113},{32.506748558905315,24.423934338970113},{32.506748558905315,44.42393433897011},{32.506748558905315,64.42393433897011},{32.506748558905315,84.42393433897011},{32.506748558905315,104.42393433897011},{32.506748558905315,124.42393433897011},{52.506748558905315,124.42393433897011}},color={0,0,127}));

  //
  // End Connect Statements for c5e8ff3d
  //



  //
  // Begin Connect Statements for ccff210c
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // cooling indirect and network 2 pipe

  connect(disNet_b19be277.ports_bCon[1],cooInd_66ab1bcf.port_a1)
    annotation (Line(points={{-20.43943700912699,99.10187573416509},{-0.4394370091269906,99.10187573416509},{-0.4394370091269906,79.10187573416509},{19.56056299087301,79.10187573416509}},color={0,0,127}));
  connect(disNet_b19be277.ports_aCon[1],cooInd_66ab1bcf.port_b1)
    annotation (Line(points={{-11.456029496453908,99.53224128391443},{8.543970503546092,99.53224128391443},{8.543970503546092,79.53224128391443},{28.543970503546092,79.53224128391443}},color={0,0,127}));

  //
  // End Connect Statements for ccff210c
  //



  //
  // Begin Connect Statements for 18a0df15
  // Source template: /model_connectors/couplings/templates/Teaser_HeatingIndirect/ConnectStatements.mopt
  //

  connect(TeaserLoad_2a880683.ports_bHeaWat[1], heaInd_01742131.port_a2)
    annotation (Line(points={{40.56293336078818,114.04295285390606},{20.562933360788165,114.04295285390606}},color={0,0,127}));
  connect(heaInd_01742131.port_b2,TeaserLoad_2a880683.ports_aHeaWat[1])
    annotation (Line(points={{49.38811418360123,113.67791730504172},{69.38811418360123,113.67791730504172}},color={0,0,127}));
  connect(pressure_source_18a0df15.ports[1], heaInd_01742131.port_b2)
    annotation (Line(points={{-52.15977367000808,-51.6895789186637},{-32.15977367000808,-51.6895789186637},{-32.15977367000808,-31.6895789186637},{-32.15977367000808,-11.689578918663699},{-32.15977367000808,8.310421081336301},{-32.15977367000808,28.3104210813363},{-32.15977367000808,48.3104210813363},{-32.15977367000808,68.3104210813363},{-32.15977367000808,88.3104210813363},{-32.15977367000808,108.3104210813363},{-12.159773670008079,108.3104210813363},{7.840226329991921,108.3104210813363},{7.840226329991921,128.3104210813363},{27.84022632999192,128.3104210813363}},color={0,0,127}));
  connect(THeaWatSet_18a0df15.y,heaInd_01742131.TSetBuiSup)
    annotation (Line(points={{-24.540662639060287,-59.44190596782363},{-4.540662639060287,-59.44190596782363},{-4.540662639060287,-39.44190596782363},{-4.540662639060287,-19.44190596782363},{-4.540662639060287,0.5580940321763705},{-4.540662639060287,20.55809403217637},{-4.540662639060287,40.55809403217637},{-4.540662639060287,60.55809403217637},{-4.540662639060287,80.55809403217637},{-4.540662639060287,100.55809403217637},{-4.540662639060287,120.55809403217637},{15.459337360939713,120.55809403217637}},color={0,0,127}));

  //
  // End Connect Statements for 18a0df15
  //



  //
  // Begin Connect Statements for d774ad50
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // heating indirect and network 2 pipe

  connect(disNet_77c66200.ports_bCon[1],heaInd_01742131.port_a1)
    annotation (Line(points={{-10.14695938853464,105.39822178072276},{9.85304061146536,105.39822178072276},{9.85304061146536,125.39822178072276},{29.85304061146536,125.39822178072276}},color={0,0,127}));
  connect(disNet_77c66200.ports_aCon[1],heaInd_01742131.port_b1)
    annotation (Line(points={{-28.50863875985513,109.56307533362208},{-8.508638759855131,109.56307533362208},{-8.508638759855131,129.56307533362207},{11.491361240144869,129.56307533362207}},color={0,0,127}));

  //
  // End Connect Statements for d774ad50
  //



  //
  // Begin Connect Statements for 19964dfa
  // Source template: /model_connectors/couplings/templates/Teaser_CoolingIndirect/ConnectStatements.mopt
  //

  connect(TeaserLoad_fc0ac7c8.ports_bChiWat[1], cooInd_e0ceb13d.port_a2)
    annotation (Line(points={{41.397099563745826,42.12607855774071},{21.39709956374584,42.12607855774071}},color={0,0,127}));
  connect(cooInd_e0ceb13d.port_b2,TeaserLoad_fc0ac7c8.ports_aChiWat[1])
    annotation (Line(points={{40.04081334458232,48.95859578367947},{60.04081334458232,48.95859578367947}},color={0,0,127}));
  connect(pressure_source_19964dfa.ports[1], cooInd_e0ceb13d.port_b2)
    annotation (Line(points={{22.074858476795555,-65.17050598715858},{2.074858476795555,-65.17050598715858},{2.074858476795555,-45.17050598715858},{2.074858476795555,-25.170505987158577},{2.074858476795555,-5.1705059871585775},{2.074858476795555,14.829494012841423},{2.074858476795555,34.82949401284141},{22.074858476795555,34.82949401284141}},color={0,0,127}));
  connect(TChiWatSet_19964dfa.y,cooInd_e0ceb13d.TSetBuiSup)
    annotation (Line(points={{68.32464551700741,-58.95902609039848},{48.32464551700741,-58.95902609039848},{48.32464551700741,-38.95902609039848},{48.32464551700741,-18.95902609039848},{48.32464551700741,1.0409739096015187},{48.32464551700741,21.04097390960152},{48.32464551700741,41.04097390960153},{68.32464551700741,41.04097390960153}},color={0,0,127}));

  //
  // End Connect Statements for 19964dfa
  //



  //
  // Begin Connect Statements for 641285b1
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // cooling indirect and network 2 pipe

  connect(disNet_b19be277.ports_bCon[2],cooInd_e0ceb13d.port_a1)
    annotation (Line(points={{-16.621661984496654,99.33190223842034},{3.3783380155033456,99.33190223842034},{3.3783380155033456,79.33190223842034},{3.3783380155033456,59.33190223842034},{3.3783380155033456,39.33190223842034},{23.378338015503346,39.33190223842034}},color={0,0,127}));
  connect(disNet_b19be277.ports_aCon[2],cooInd_e0ceb13d.port_b1)
    annotation (Line(points={{-18.334563923009227,93.32503796899097},{1.6654360769907726,93.32503796899097},{1.6654360769907726,73.32503796899097},{1.6654360769907726,53.32503796899097},{1.6654360769907726,33.32503796899097},{21.665436076990773,33.32503796899097}},color={0,0,127}));

  //
  // End Connect Statements for 641285b1
  //



  //
  // Begin Connect Statements for b7fca81e
  // Source template: /model_connectors/couplings/templates/Teaser_HeatingIndirect/ConnectStatements.mopt
  //

  connect(TeaserLoad_fc0ac7c8.ports_bHeaWat[1], heaInd_6a617e11.port_a2)
    annotation (Line(points={{65.3780119608297,22.40194816310678},{65.3780119608297,2.4019481631067663},{45.378011960829696,2.4019481631067663},{25.37801196082971,2.4019481631067663}},color={0,0,127}));
  connect(heaInd_6a617e11.port_b2,TeaserLoad_fc0ac7c8.ports_aHeaWat[1])
    annotation (Line(points={{16.476229200157718,18.317367476697825},{36.47622920015772,18.317367476697825},{36.47622920015772,38.31736747669781},{56.47622920015772,38.31736747669781}},color={0,0,127}));
  connect(pressure_source_b7fca81e.ports[1], heaInd_6a617e11.port_b2)
    annotation (Line(points={{-66.51902191431947,-99.02596825553073},{-46.51902191431947,-99.02596825553073},{-46.51902191431947,-79.02596825553073},{-46.51902191431947,-59.02596825553073},{-46.51902191431947,-39.02596825553073},{-46.51902191431947,-19.025968255530728},{-46.51902191431947,0.9740317444692721},{-26.519021914319467,0.9740317444692721},{-6.519021914319467,0.9740317444692721},{13.480978085680533,0.9740317444692721}},color={0,0,127}));
  connect(THeaWatSet_b7fca81e.y,heaInd_6a617e11.TSetBuiSup)
    annotation (Line(points={{-28.77459671782202,-100.45189340085452},{-8.774596717822021,-100.45189340085452},{-8.774596717822021,-80.45189340085452},{-8.774596717822021,-60.451893400854516},{-8.774596717822021,-40.451893400854516},{-8.774596717822021,-20.451893400854516},{-8.774596717822021,-0.4518934008545159},{11.225403282177979,-0.4518934008545159}},color={0,0,127}));

  //
  // End Connect Statements for b7fca81e
  //



  //
  // Begin Connect Statements for 2c2ba738
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // heating indirect and network 2 pipe

  connect(disNet_77c66200.ports_bCon[2],heaInd_6a617e11.port_a1)
    annotation (Line(points={{-16.465126121653398,68.0345168074926},{-16.465126121653398,48.034516807492594},{-16.465126121653398,28.034516807492594},{-16.465126121653398,8.034516807492594},{3.534873878346602,8.034516807492594},{23.534873878346602,8.034516807492594}},color={0,0,127}));
  connect(disNet_77c66200.ports_aCon[2],heaInd_6a617e11.port_b1)
    annotation (Line(points={{-17.5164725445904,55.5324002878681},{-17.5164725445904,35.5324002878681},{-17.5164725445904,15.532400287868114},{-17.5164725445904,-4.467599712131886},{2.4835274554096003,-4.467599712131886},{22.4835274554096,-4.467599712131886}},color={0,0,127}));

  //
  // End Connect Statements for 2c2ba738
  //




annotation(
  experiment(
    StopTime=86400,
    Interval=3600,
    Tolerance=1e-06),
  Diagram(
    coordinateSystem(
      preserveAspectRatio=false,
      extent={{-90.0,-150.0},{90.0,150.0}})),
  Documentation(
    revisions="<html>
 <li>
 May 10, 2020: Hagar Elarga<br/>
Updated implementation to handle template needed for GeoJSON to Modelica.
</li>
</html>"));
end DistrictEnergySystem;
