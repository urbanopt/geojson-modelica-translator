within district_heating_and_cooling_systems.Districts;
model DistrictEnergySystemCHP
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
  // Begin Model Instance for disNet_0a531ebc
  // Source template: /model_connectors/networks/templates/Network2Pipe_Instance.mopt
  //
parameter Integer nBui_disNet_0a531ebc=2;
  parameter Modelica.SIunits.MassFlowRate mDis_flow_nominal_disNet_0a531ebc=sum({
    cooInd_10ef8496.mDis_flow_nominal,
  cooInd_8c585717.mDis_flow_nominal})
    "Nominal mass flow rate of the distribution pump";
  parameter Modelica.SIunits.MassFlowRate mCon_flow_nominal_disNet_0a531ebc[nBui_disNet_0a531ebc]={
    cooInd_10ef8496.mDis_flow_nominal,
  cooInd_8c585717.mDis_flow_nominal}
    "Nominal mass flow rate in each connection line";
  parameter Modelica.SIunits.PressureDifference dpDis_nominal_disNet_0a531ebc[nBui_disNet_0a531ebc](
    each min=0,
    each displayUnit="Pa")=1/2 .* cat(
    1,
    {dp_nominal_disNet_0a531ebc*0.1},
    fill(
      dp_nominal_disNet_0a531ebc*0.9/(nBui_disNet_0a531ebc-1),
      nBui_disNet_0a531ebc-1))
    "Pressure drop between each connected building at nominal conditions (supply line)";
  parameter Modelica.SIunits.PressureDifference dp_nominal_disNet_0a531ebc=dpSetPoi_disNet_0a531ebc+nBui_disNet_0a531ebc*7000
    "District network pressure drop";
  // NOTE: this differential pressure setpoint is currently utilized by plants elsewhere
  parameter Modelica.SIunits.Pressure dpSetPoi_disNet_0a531ebc=50000
    "Differential pressure setpoint";

  Buildings.Experimental.DHC.Loads.Validation.BaseClasses.Distribution2Pipe disNet_0a531ebc(
    redeclare final package Medium=MediumW,
    final nCon=nBui_disNet_0a531ebc,
    iConDpSen=nBui_disNet_0a531ebc,
    final mDis_flow_nominal=mDis_flow_nominal_disNet_0a531ebc,
    final mCon_flow_nominal=mCon_flow_nominal_disNet_0a531ebc,
    final allowFlowReversal=false,
    dpDis_nominal=dpDis_nominal_disNet_0a531ebc)
    "Distribution network."
    annotation (Placement(transformation(extent={{-30.0,120.0},{-10.0,130.0}})));
  //
  // End Model Instance for disNet_0a531ebc
  //

  //
  // Begin Model Instance for cooPla_c16c5feb
  // Source template: /model_connectors/plants/templates/CoolingPlant_Instance.mopt
  //
  parameter Modelica.SIunits.MassFlowRate mCHW_flow_nominal_cooPla_c16c5feb=cooPla_c16c5feb.numChi*(cooPla_c16c5feb.perChi.mEva_flow_nominal)
    "Nominal chilled water mass flow rate";
  parameter Modelica.SIunits.MassFlowRate mCW_flow_nominal_cooPla_c16c5feb=cooPla_c16c5feb.perChi.mCon_flow_nominal
    "Nominal condenser water mass flow rate";
  parameter Modelica.SIunits.PressureDifference dpCHW_nominal_cooPla_c16c5feb=44.8*1000
    "Nominal chilled water side pressure";
  parameter Modelica.SIunits.PressureDifference dpCW_nominal_cooPla_c16c5feb=46.2*1000
    "Nominal condenser water side pressure";
  parameter Modelica.SIunits.Power QEva_nominal_cooPla_c16c5feb=mCHW_flow_nominal_cooPla_c16c5feb*4200*(5-14)
    "Nominal cooling capaciaty (Negative means cooling)";
  parameter Modelica.SIunits.MassFlowRate mMin_flow_cooPla_c16c5feb=0.2*mCHW_flow_nominal_cooPla_c16c5feb/cooPla_c16c5feb.numChi
    "Minimum mass flow rate of single chiller";
  // control settings
  parameter Modelica.SIunits.Pressure dpSetPoi_cooPla_c16c5feb=70000
    "Differential pressure setpoint";
  parameter Modelica.SIunits.Pressure pumDP_cooPla_c16c5feb=dpCHW_nominal_cooPla_c16c5feb+dpSetPoi_cooPla_c16c5feb+200000;
  parameter Modelica.SIunits.Time tWai_cooPla_c16c5feb=30
    "Waiting time";
  // pumps
  parameter Buildings.Fluid.Movers.Data.Generic perCHWPum_cooPla_c16c5feb(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=((mCHW_flow_nominal_cooPla_c16c5feb/cooPla_c16c5feb.numChi)/1000)*{0.1,1,1.2},
      dp=pumDP_cooPla_c16c5feb*{1.2,1,0.1}))
    "Performance data for chilled water pumps";
  parameter Buildings.Fluid.Movers.Data.Generic perCWPum_cooPla_c16c5feb(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=mCW_flow_nominal_cooPla_c16c5feb/1000*{0.2,0.6,1.0,1.2},
      dp=(dpCW_nominal_cooPla_c16c5feb+60000+6000)*{1.2,1.1,1.0,0.6}))
    "Performance data for condenser water pumps";

  Modelica.Blocks.Sources.RealExpression TSetChiWatDis_cooPla_c16c5feb(
    y=5+273.15)
    "Chilled water supply temperature set point on district level."
    annotation (Placement(transformation(extent={{10.0,-130.0},{30.0,-110.0}})));
  Modelica.Blocks.Sources.BooleanConstant on_cooPla_c16c5feb
    "On signal of the plant"
    annotation (Placement(transformation(extent={{50.0,-130.0},{70.0,-110.0}})));

  district_heating_and_cooling_systems.Plants.CentralCoolingPlant cooPla_c16c5feb(
    redeclare Buildings.Fluid.Chillers.Data.ElectricEIR.ElectricEIRChiller_Carrier_19EX_5208kW_6_88COP_Vanes perChi,
    perCHWPum=perCHWPum_cooPla_c16c5feb,
    perCWPum=perCWPum_cooPla_c16c5feb,
    mCHW_flow_nominal=mCHW_flow_nominal_cooPla_c16c5feb,
    dpCHW_nominal=dpCHW_nominal_cooPla_c16c5feb,
    QEva_nominal=QEva_nominal_cooPla_c16c5feb,
    mMin_flow=mMin_flow_cooPla_c16c5feb,
    mCW_flow_nominal=mCW_flow_nominal_cooPla_c16c5feb,
    dpCW_nominal=dpCW_nominal_cooPla_c16c5feb,
    TAirInWB_nominal=298.7,
    TCW_nominal=308.15,
    TMin=288.15,
    tWai=tWai_cooPla_c16c5feb,
    dpSetPoi=dpSetPoi_cooPla_c16c5feb,
    energyDynamics=Modelica.Fluid.Types.Dynamics.FixedInitial)
    "District cooling plant."
    annotation (Placement(transformation(extent={{-80,108},{-60,128}})));
  //
  // End Model Instance for cooPla_c16c5feb
  //

  //
  // Begin Model Instance for disNet_aaccda4a
  // Source template: /model_connectors/networks/templates/Network2Pipe_Instance.mopt
  //
parameter Integer nBui_disNet_aaccda4a=2;
  parameter Modelica.SIunits.MassFlowRate mDis_flow_nominal_disNet_aaccda4a=sum({
    heaInd_5e1a06ae.mDis_flow_nominal,
  heaInd_06ab776a.mDis_flow_nominal})
    "Nominal mass flow rate of the distribution pump";
  parameter Modelica.SIunits.MassFlowRate mCon_flow_nominal_disNet_aaccda4a[nBui_disNet_aaccda4a]={
    heaInd_5e1a06ae.mDis_flow_nominal,
  heaInd_06ab776a.mDis_flow_nominal}
    "Nominal mass flow rate in each connection line";
  parameter Modelica.SIunits.PressureDifference dpDis_nominal_disNet_aaccda4a[nBui_disNet_aaccda4a](
    each min=0,
    each displayUnit="Pa")=1/2 .* cat(
    1,
    {dp_nominal_disNet_aaccda4a*0.1},
    fill(
      dp_nominal_disNet_aaccda4a*0.9/(nBui_disNet_aaccda4a-1),
      nBui_disNet_aaccda4a-1))
    "Pressure drop between each connected building at nominal conditions (supply line)";
  parameter Modelica.SIunits.PressureDifference dp_nominal_disNet_aaccda4a=dpSetPoi_disNet_aaccda4a+nBui_disNet_aaccda4a*7000
    "District network pressure drop";
  // NOTE: this differential pressure setpoint is currently utilized by plants elsewhere
  parameter Modelica.SIunits.Pressure dpSetPoi_disNet_aaccda4a=50000
    "Differential pressure setpoint";

  Buildings.Experimental.DHC.Loads.Validation.BaseClasses.Distribution2Pipe disNet_aaccda4a(
    redeclare final package Medium=MediumW,
    final nCon=nBui_disNet_aaccda4a,
    iConDpSen=nBui_disNet_aaccda4a,
    final mDis_flow_nominal=mDis_flow_nominal_disNet_aaccda4a,
    final mCon_flow_nominal=mCon_flow_nominal_disNet_aaccda4a,
    final allowFlowReversal=false,
    dpDis_nominal=dpDis_nominal_disNet_aaccda4a)
    "Distribution network."
    annotation (Placement(transformation(extent={{-30.0,80.0},{-10.0,90.0}})));
  //
  // End Model Instance for disNet_aaccda4a
  //

  //
  // Begin Model Instance for heaPla_ad69f8b1
  // Source template: /model_connectors/plants/templates/HeatingPlant_Instance.mopt
  //
  // heating plant instance
  parameter Modelica.SIunits.MassFlowRate mHW_flow_nominal_heaPla_ad69f8b1=mBoi_flow_nominal_heaPla_ad69f8b1*heaPla_ad69f8b1.numBoi
    "Nominal heating water mass flow rate";
  parameter Modelica.SIunits.MassFlowRate mBoi_flow_nominal_heaPla_ad69f8b1=QBoi_nominal_heaPla_ad69f8b1/(4200*heaPla_ad69f8b1.delT_nominal)
    "Nominal heating water mass flow rate";
  parameter Modelica.SIunits.Power QBoi_nominal_heaPla_ad69f8b1=Q_flow_nominal_heaPla_ad69f8b1/heaPla_ad69f8b1.numBoi
    "Nominal heating capaciaty";
  parameter Modelica.SIunits.HeatFlowRate Q_flow_nominal_heaPla_ad69f8b1=1000000*2
    "Heating load";
  parameter Modelica.SIunits.MassFlowRate mMin_flow_heaPla_ad69f8b1=0.2*mBoi_flow_nominal_heaPla_ad69f8b1
    "Minimum mass flow rate of single boiler";
  // controls
  parameter Modelica.SIunits.Pressure pumDP=(heaPla_ad69f8b1.dpBoi_nominal+dpSetPoi_disNet_aaccda4a+50000)
    "Heating water pump pressure drop";
  parameter Modelica.SIunits.Time tWai_heaPla_ad69f8b1=30
    "Waiting time";
  parameter Buildings.Fluid.Movers.Data.Generic perHWPum_heaPla_ad69f8b1(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=mBoi_flow_nominal_heaPla_ad69f8b1/1000*{0.1,1.1},
      dp=pumDP*{1.1,0.1}))
    "Performance data for heating water pumps";

  district_heating_and_cooling_systems.Plants.CentralHeatingPlant heaPla_ad69f8b1(
    perHWPum=perHWPum_heaPla_ad69f8b1,
    mHW_flow_nominal=mHW_flow_nominal_heaPla_ad69f8b1,
    QBoi_flow_nominal=QBoi_nominal_heaPla_ad69f8b1,
    mMin_flow=mMin_flow_heaPla_ad69f8b1,
    mBoi_flow_nominal=mBoi_flow_nominal_heaPla_ad69f8b1,
    dpBoi_nominal=10000,
    delT_nominal(
      displayUnit="degC")=15,
    tWai=tWai_heaPla_ad69f8b1,
    dpSetPoi=dpSetPoi_disNet_aaccda4a,
    energyDynamics=Modelica.Fluid.Types.Dynamics.FixedInitial)
    "District heating plant."
    annotation (Placement(transformation(extent={{-80,70},{-60,90}})));
    // TODO: we're currently grabbing dpSetPoi from the Network instance -- need feedback to determine if that's the proper "home" for it
  //
  // End Model Instance for heaPla_ad69f8b1
  //

  //
  // Begin Model Instance for TimeSerLoa_22cdb8e4
  // Source template: /model_connectors/load_connectors/templates/TimeSeries_Instance.mopt
  //
  // time series load
  district_heating_and_cooling_systems.Loads.B5a6b99ec37f4de7f94020090.building TimeSerLoa_22cdb8e4(
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
    annotation (Placement(transformation(extent={{50.0,110.0},{70.0,130.0}})));
  //
  // End Model Instance for TimeSerLoa_22cdb8e4
  //

  //
  // Begin Model Instance for cooInd_10ef8496
  // Source template: /model_connectors/energy_transfer_systems/templates/CoolingIndirect_Instance.mopt
  //
  // cooling indirect instance
  district_heating_and_cooling_systems.Substations.CoolingIndirect_5a6b99ec37f4de7f94020090 cooInd_10ef8496(
    redeclare package Medium=MediumW,
    allowFlowReversal1=false,
    allowFlowReversal2=false,
    mDis_flow_nominal=mDis_flow_nominal_6f479c16,
    mBui_flow_nominal=mBui_flow_nominal_6f479c16,
    dp1_nominal=500,
    dp2_nominal=500,
    dpValve_nominal=7000,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_6f479c16,
    T_a1_nominal=273.15+5,
    T_a2_nominal=273.15+13)
    "Indirect cooling energy transfer station ETS."
    annotation (Placement(transformation(extent={{10.0,110.0},{30.0,130.0}})));
    // TODO: dehardcode the nominal temperatures?
  //
  // End Model Instance for cooInd_10ef8496
  //

  //
  // Begin Model Instance for heaInd_5e1a06ae
  // Source template: /model_connectors/energy_transfer_systems/templates/HeatingIndirect_Instance.mopt
  //
  // heating indirect instance
  district_heating_and_cooling_systems.Substations.HeatingIndirect_5a6b99ec37f4de7f94020090 heaInd_5e1a06ae(
    allowFlowReversal1=false,
    allowFlowReversal2=false,
    show_T=true,
    redeclare package Medium=MediumW,
    mDis_flow_nominal=mDis_flow_nominal_9d87c5b1,
    mBui_flow_nominal=mBui_flow_nominal_9d87c5b1,
    dpValve_nominal=6000,
    dp1_nominal=500,
    dp2_nominal=500,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_9d87c5b1,
    T_a1_nominal=55+273.15,
    T_a2_nominal=35+273.15,
    k=0.1,
    Ti=60,
    reverseActing=true)
    annotation (Placement(transformation(extent={{10.0,70.0},{30.0,90.0}})));
  //
  // End Model Instance for heaInd_5e1a06ae
  //

  //
  // Begin Model Instance for TimeSerLoa_40b5db32
  // Source template: /model_connectors/load_connectors/templates/TimeSeries_Instance.mopt
  //
  // time series load
  district_heating_and_cooling_systems.Loads.Babcdefghijklmnopqrstuvwx.building TimeSerLoa_40b5db32(
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
  // End Model Instance for TimeSerLoa_40b5db32
  //

  //
  // Begin Model Instance for cooInd_8c585717
  // Source template: /model_connectors/energy_transfer_systems/templates/CoolingIndirect_Instance.mopt
  //
  // cooling indirect instance
  district_heating_and_cooling_systems.Substations.CoolingIndirect_abcdefghijklmnopqrstuvwx cooInd_8c585717(
    redeclare package Medium=MediumW,
    allowFlowReversal1=false,
    allowFlowReversal2=false,
    mDis_flow_nominal=mDis_flow_nominal_da8eb9ea,
    mBui_flow_nominal=mBui_flow_nominal_da8eb9ea,
    dp1_nominal=500,
    dp2_nominal=500,
    dpValve_nominal=7000,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_da8eb9ea,
    T_a1_nominal=273.15+5,
    T_a2_nominal=273.15+13)
    "Indirect cooling energy transfer station ETS."
    annotation (Placement(transformation(extent={{10.0,30.0},{30.0,50.0}})));
    // TODO: dehardcode the nominal temperatures?
  //
  // End Model Instance for cooInd_8c585717
  //

  //
  // Begin Model Instance for heaInd_06ab776a
  // Source template: /model_connectors/energy_transfer_systems/templates/HeatingIndirect_Instance.mopt
  //
  // heating indirect instance
  district_heating_and_cooling_systems.Substations.HeatingIndirect_abcdefghijklmnopqrstuvwx heaInd_06ab776a(
    allowFlowReversal1=false,
    allowFlowReversal2=false,
    show_T=true,
    redeclare package Medium=MediumW,
    mDis_flow_nominal=mDis_flow_nominal_72f54e3c,
    mBui_flow_nominal=mBui_flow_nominal_72f54e3c,
    dpValve_nominal=6000,
    dp1_nominal=500,
    dp2_nominal=500,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_72f54e3c,
    T_a1_nominal=55+273.15,
    T_a2_nominal=35+273.15,
    k=0.1,
    Ti=60,
    reverseActing=true)
    annotation (Placement(transformation(extent={{10.0,-10.0},{30.0,10.0}})));
  //
  // End Model Instance for heaInd_06ab776a
  //

  // Model dependencies

  //
  // Begin Component Definitions for 1b771627
  // Source template: /model_connectors/couplings/templates/Network2Pipe_CoolingPlant/ComponentDefinitions.mopt
  //
  // No components for pipe and cooling plant

  //
  // End Component Definitions for 1b771627
  //

  //
  // Begin Component Definitions for 1544cf6b
  // Source template: /model_connectors/couplings/templates/Network2Pipe_HeatingPlant/ComponentDefinitions.mopt
  //
  // TODO: This should not be here, it is entirely plant specific and should be moved elsewhere
  // but since it requires a connect statement we must put it here for now...
  Modelica.Blocks.Sources.BooleanConstant mPum_flow_1544cf6b(
    k=true)
    "Total heating water pump mass flow rate"
    annotation (Placement(transformation(extent={{-70.0,-50.0},{-50.0,-30.0}})));
  // TODO: This should not be here, it is entirely plant specific and should be moved elsewhere
  // but since it requires a connect statement we must put it here for now...
  Modelica.Blocks.Sources.RealExpression TDisSetHeaWat_1544cf6b(
    each y=55+273.15)
    "Distrcit side heating water supply temperature set point."
    annotation (Placement(transformation(extent={{-30.0,-50.0},{-10.0,-30.0}})));

  //
  // End Component Definitions for 1544cf6b
  //

  //
  // Begin Component Definitions for 6f479c16
  // Source template: /model_connectors/couplings/templates/TimeSeries_CoolingIndirect/ComponentDefinitions.mopt
  //
  // TimeSeries + CoolingIndirect Component Definitions
  parameter Modelica.SIunits.MassFlowRate mDis_flow_nominal_6f479c16=TimeSerLoa_22cdb8e4.mChiWat_flow_nominal*delChiWatTemBui/delChiWatTemDis
    "Nominal mass flow rate of primary (district) district cooling side";
  parameter Modelica.SIunits.MassFlowRate mBui_flow_nominal_6f479c16=TimeSerLoa_22cdb8e4.mChiWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district cooling side";
  parameter Modelica.SIunits.HeatFlowRate Q_flow_nominal_6f479c16=-1*(TimeSerLoa_22cdb8e4.QCoo_flow_nominal);
  Modelica.Fluid.Sources.FixedBoundary pressure_source_6f479c16(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{10.0,-50.0},{30.0,-30.0}})));
  // TODO: move TChiWatSet (and its connection) into a CoolingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression TChiWatSet_6f479c16(
    y=7+273.15)
    "Primary loop (district side) chilled water setpoint temperature."
    annotation (Placement(transformation(extent={{50.0,-50.0},{70.0,-30.0}})));
    //Dehardcode

  //
  // End Component Definitions for 6f479c16
  //

  //
  // Begin Component Definitions for 76b40133
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for cooling indirect and network 2 pipe

  //
  // End Component Definitions for 76b40133
  //

  //
  // Begin Component Definitions for 9d87c5b1
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ComponentDefinitions.mopt
  //
  // TimeSeries + HeatingIndirect Component Definitions
  // TODO: the components below need to be fixed!
  parameter Modelica.SIunits.MassFlowRate mDis_flow_nominal_9d87c5b1=TimeSerLoa_22cdb8e4.mHeaWat_flow_nominal*delHeaWatTemBui/delHeaWatTemDis
    "Nominal mass flow rate of primary (district) district heating side";
  parameter Modelica.SIunits.MassFlowRate mBui_flow_nominal_9d87c5b1=TimeSerLoa_22cdb8e4.mHeaWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district heating side";
  parameter Modelica.SIunits.HeatFlowRate Q_flow_nominal_9d87c5b1=(TimeSerLoa_22cdb8e4.QHea_flow_nominal);
  Modelica.Fluid.Sources.FixedBoundary pressure_source_9d87c5b1(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{-70.0,-90.0},{-50.0,-70.0}})));
  // TODO: move THeaWatSet (and its connection) into a HeatingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression THeaWatSet_9d87c5b1(
    y=40+273.15)
    "Secondary loop (Building side) heating water setpoint temperature."
    annotation (Placement(transformation(extent={{-30.0,-90.0},{-10.0,-70.0}})));
    //Dehardcode

  //
  // End Component Definitions for 9d87c5b1
  //

  //
  // Begin Component Definitions for 4ac88e64
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for heating indirect and network 2 pipe

  //
  // End Component Definitions for 4ac88e64
  //

  //
  // Begin Component Definitions for da8eb9ea
  // Source template: /model_connectors/couplings/templates/TimeSeries_CoolingIndirect/ComponentDefinitions.mopt
  //
  // TimeSeries + CoolingIndirect Component Definitions
  parameter Modelica.SIunits.MassFlowRate mDis_flow_nominal_da8eb9ea=TimeSerLoa_40b5db32.mChiWat_flow_nominal*delChiWatTemBui/delChiWatTemDis
    "Nominal mass flow rate of primary (district) district cooling side";
  parameter Modelica.SIunits.MassFlowRate mBui_flow_nominal_da8eb9ea=TimeSerLoa_40b5db32.mChiWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district cooling side";
  parameter Modelica.SIunits.HeatFlowRate Q_flow_nominal_da8eb9ea=-1*(TimeSerLoa_40b5db32.QCoo_flow_nominal);
  Modelica.Fluid.Sources.FixedBoundary pressure_source_da8eb9ea(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{10.0,-90.0},{30.0,-70.0}})));
  // TODO: move TChiWatSet (and its connection) into a CoolingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression TChiWatSet_da8eb9ea(
    y=7+273.15)
    "Primary loop (district side) chilled water setpoint temperature."
    annotation (Placement(transformation(extent={{50.0,-90.0},{70.0,-70.0}})));
    //Dehardcode

  //
  // End Component Definitions for da8eb9ea
  //

  //
  // Begin Component Definitions for 9d460edc
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for cooling indirect and network 2 pipe

  //
  // End Component Definitions for 9d460edc
  //

  //
  // Begin Component Definitions for 72f54e3c
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ComponentDefinitions.mopt
  //
  // TimeSeries + HeatingIndirect Component Definitions
  // TODO: the components below need to be fixed!
  parameter Modelica.SIunits.MassFlowRate mDis_flow_nominal_72f54e3c=TimeSerLoa_40b5db32.mHeaWat_flow_nominal*delHeaWatTemBui/delHeaWatTemDis
    "Nominal mass flow rate of primary (district) district heating side";
  parameter Modelica.SIunits.MassFlowRate mBui_flow_nominal_72f54e3c=TimeSerLoa_40b5db32.mHeaWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district heating side";
  parameter Modelica.SIunits.HeatFlowRate Q_flow_nominal_72f54e3c=(TimeSerLoa_40b5db32.QHea_flow_nominal);
  Modelica.Fluid.Sources.FixedBoundary pressure_source_72f54e3c(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{-70.0,-130.0},{-50.0,-110.0}})));
  // TODO: move THeaWatSet (and its connection) into a HeatingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression THeaWatSet_72f54e3c(
    y=40+273.15)
    "Secondary loop (Building side) heating water setpoint temperature."
    annotation (Placement(transformation(extent={{-30.0,-130.0},{-10.0,-110.0}})));
    //Dehardcode

  //
  // End Component Definitions for 72f54e3c
  //

  //
  // Begin Component Definitions for afcd41bc
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for heating indirect and network 2 pipe

  //
  // End Component Definitions for afcd41bc
  //

  Buildings.Fluid.CHPs.ThermalElectricalFollowing eleFol(redeclare package
      Medium =                                                                      MediumW,
    m_flow_nominal=0.4,
    energyDynamics=Modelica.Fluid.Types.Dynamics.SteadyState,
    redeclare Buildings.Fluid.CHPs.Data.Senertech5_5kW per,
    TEngIni=273.15 + 69.55,
    waitTime=0)
    annotation (Placement(transformation(extent={{-80,28},{-60,48}})));
  Modelica.Blocks.Sources.BooleanTable avaSig(startValue=true, table={172800})
    "Plant availability signal"
    annotation (Placement(transformation(extent={{-160,80},{-140,100}})));
  Modelica.Blocks.Sources.Constant ElePowDem(k=5500)
    annotation (Placement(transformation(extent={{-120,82},{-100,102}})));
  Modelica.Blocks.Sources.Constant TWatOutSet(k=60)
    annotation (Placement(transformation(extent={{-120,52},{-100,72}})));
protected
  Modelica.Blocks.Sources.BooleanExpression theFolSig(final y=true)
    "Signal for thermal following, set to false if electrical following"
    annotation (Placement(transformation(extent={{-160,50},{-140,66}})));
equation
  // Connections

  //
  // Begin Connect Statements for 1b771627
  // Source template: /model_connectors/couplings/templates/Network2Pipe_CoolingPlant/ConnectStatements.mopt
  //

  // TODO: these connect statements shouldn't be here, they are plant specific
  // but since we can't currently make connect statements for single systems, this is what we've got
  connect(on_cooPla_c16c5feb.y,cooPla_c16c5feb.on)
    annotation (Line(points={{71,-120},{36.2605,-120},{36.2605,101.979},{-43.7395,101.979},{-43.7395,126},{-82,126}},                                                                                                                                                                                                        color={0,0,127}));
  connect(TSetChiWatDis_cooPla_c16c5feb.y,cooPla_c16c5feb.TCHWSupSet)
    annotation (Line(points={{31,-120},{-0.711768,-120},{-0.711768,106.637},{-40.7118,106.637},{-40.7118,121},{-82,121}},                                                                                                                                                                                      color={0,0,127}));

  connect(disNet_0a531ebc.port_bDisRet,cooPla_c16c5feb.port_a)
    annotation (Line(points={{-30,122},{-32,122},{-32,122.183},{-35.9431,122.183},{-35.9431,123},{-60,123}},color={0,0,127}));
  connect(cooPla_c16c5feb.port_b,disNet_0a531ebc.port_aDisSup)
    annotation (Line(points={{-60,113},{-46,113},{-46,116},{-43.3667,116},{-43.3667,125},{-30,125}},          color={0,0,127}));
  connect(disNet_0a531ebc.dp,cooPla_c16c5feb.dpMea)
    annotation (Line(points={{-9.5,126.5},{-30,126.5},{-30,126},{-49.2319,126},{-49.2319,115},{-82,115}},     color={0,0,127}));

  //
  // End Connect Statements for 1b771627
  //

  //
  // Begin Connect Statements for 1544cf6b
  // Source template: /model_connectors/couplings/templates/Network2Pipe_HeatingPlant/ConnectStatements.mopt
  //

  connect(heaPla_ad69f8b1.port_a,disNet_aaccda4a.port_bDisRet)
    annotation (Line(points={{-60,85},{-60,86},{-50,86},{-50,82},{-30,82}},                                   color={0,0,127}));
  connect(disNet_aaccda4a.dp,heaPla_ad69f8b1.dpMea)
    annotation (Line(points={{-9.5,86.5},{-28,86.5},{-28,86},{-47.3677,86},{-47.3677,77},{-82,77}},       color={0,0,127}));
  connect(heaPla_ad69f8b1.port_b,disNet_aaccda4a.port_aDisSup)
    annotation (Line(points={{-60,75},{-60,76},{-48.2889,76},{-48.2889,85},{-30,85}},                     color={0,0,127}));
  connect(mPum_flow_1544cf6b.y,heaPla_ad69f8b1.on)
    annotation (Line(points={{-49,-40},{-49,88},{-82,88}},                                                                                                                                                                                                        color={0,0,127}));
  connect(TDisSetHeaWat_1544cf6b.y,heaPla_ad69f8b1.THeaSet)
    annotation (Line(points={{-9,-40},{-9,53.7307},{-32.4375,53.7307},{-32.4375,71.6},{-82,71.6}},                                                                                                                                  color={0,0,127}));

  //
  // End Connect Statements for 1544cf6b
  //

  //
  // Begin Connect Statements for 6f479c16
  // Source template: /model_connectors/couplings/templates/TimeSeries_CoolingIndirect/ConnectStatements.mopt
  //

  // cooling indirect, timeseries coupling connections
  connect(TimeSerLoa_22cdb8e4.ports_bChiWat[1], cooInd_10ef8496.port_a2)
    annotation (Line(points={{70,114},{64,114},{64,108.912},{57.8691,108.912},{57.8691,114},{30,114}},       color={0,0,127}));
  connect(cooInd_10ef8496.port_b2,TimeSerLoa_22cdb8e4.ports_aChiWat[1])
    annotation (Line(points={{10,114},{20,114},{20,109.033},{29.4063,109.033},{29.4063,114},{50,114}},       color={0,0,127}));
  connect(pressure_source_6f479c16.ports[1], cooInd_10ef8496.port_b2)
    annotation (Line(points={{30,-40},{6.33823,-40},{6.33823,-0.110143},{6.33823,19.8899},{6.33823,39.8899},{6.33823,
          59.8899},{6.33823,79.8899},{6.33823,99.8899},{6.33823,114},{10,114}},                                                                                                                                                                                                        color={0,0,127}));
  connect(TChiWatSet_6f479c16.y,cooInd_10ef8496.TSetBuiSup)
    annotation (Line(points={{71,-40},{71,-0.0493932},{71,19.9506},{39.4863,19.9506},{39.4863,39.9506},{39.4863,59.9506},
          {39.4863,79.9506},{39.4863,99.9506},{39.4863,120},{8,120}},                                                                                                                                                                                                        color={0,0,127}));

  //
  // End Connect Statements for 6f479c16
  //

  //
  // Begin Connect Statements for 76b40133
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // cooling indirect and network 2 pipe

  connect(disNet_0a531ebc.ports_bCon[1],cooInd_10ef8496.port_a1)
    annotation (Line(points={{-24,130},{-16,130},{-16,132.016},{-8.10396,132.016},{-8.10396,126},{10,126}},   color={0,0,127}));
  connect(disNet_0a531ebc.ports_aCon[1],cooInd_10ef8496.port_b1)
    annotation (Line(points={{-12,130},{0,130},{0,127.313},{13.5096,127.313},{13.5096,126},{30,126}},        color={0,0,127}));

  //
  // End Connect Statements for 76b40133
  //

  //
  // Begin Connect Statements for 9d87c5b1
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ConnectStatements.mopt
  //

  // cooling indirect, timeseries coupling connections
  connect(TimeSerLoa_22cdb8e4.ports_bHeaWat[1], heaInd_5e1a06ae.port_a2)
    annotation (Line(points={{70,118},{70,71.5942},{30,71.5942},{30,74}},                                                                                                                color={0,0,127}));
  connect(heaInd_5e1a06ae.port_b2,TimeSerLoa_22cdb8e4.ports_aHeaWat[1])
    annotation (Line(points={{10,74},{35.7678,74},{35.7678,118},{50,118}},                                                                                                                  color={0,0,127}));
  connect(pressure_source_9d87c5b1.ports[1], heaInd_5e1a06ae.port_b2)
    annotation (Line(points={{-50,-80},{-33.793,-80},{-33.793,-48.1869},{-33.793,-28.1869},{-33.793,-8.18688},{-33.793,
          11.8131},{-33.793,31.8131},{-33.793,51.8131},{-13.793,51.8131},{6.20704,51.8131},{6.20704,74},{10,74}},                                                                                                                                                                                                        color={0,0,127}));
  connect(THeaWatSet_9d87c5b1.y,heaInd_5e1a06ae.TSetBuiSup)
    annotation (Line(points={{-9,-80},{4.52138,-80},{4.52138,-44.3119},{4.52138,-24.3119},{4.52138,-4.31188},{4.52138,
          15.6881},{4.52138,35.6881},{4.52138,55.6881},{4.52138,80},{8,80}},                                                                                                                                                                                                        color={0,0,127}));

  //
  // End Connect Statements for 9d87c5b1
  //

  //
  // Begin Connect Statements for 4ac88e64
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // heating indirect and network 2 pipe

  connect(disNet_aaccda4a.ports_bCon[1],heaInd_5e1a06ae.port_a1)
    annotation (Line(points={{-24,90},{-18,90},{-18,94.4899},{-10.7086,94.4899},{-10.7086,86},{10,86}},     color={0,0,127}));
  connect(disNet_aaccda4a.ports_aCon[1],heaInd_5e1a06ae.port_b1)
    annotation (Line(points={{-12,90},{2,90},{2,86.8723},{14.8745,86.8723},{14.8745,86},{30,86}},            color={0,0,127}));

  //
  // End Connect Statements for 4ac88e64
  //

  //
  // Begin Connect Statements for da8eb9ea
  // Source template: /model_connectors/couplings/templates/TimeSeries_CoolingIndirect/ConnectStatements.mopt
  //

  // cooling indirect, timeseries coupling connections
  connect(TimeSerLoa_40b5db32.ports_bChiWat[1], cooInd_8c585717.port_a2)
    annotation (Line(points={{70,34},{62,34},{62,36.8405},{53.2545,36.8405},{53.2545,34},{30,34}},          color={0,0,127}));
  connect(cooInd_8c585717.port_b2,TimeSerLoa_40b5db32.ports_aChiWat[1])
    annotation (Line(points={{10,34},{16,34},{16,30.9994},{20.8822,30.9994},{20.8822,34},{50,34}},        color={0,0,127}));
  connect(pressure_source_da8eb9ea.ports[1], cooInd_8c585717.port_b2)
    annotation (Line(points={{30,-80},{-9.96929,-80},{-9.96929,-42.1175},{-9.96929,-22.1175},{-9.96929,-2.11748},{-9.96929,
          17.8825},{-9.96929,34},{9.99999,34}},                                                                                                                                                                                                        color={0,0,127}));
  connect(TChiWatSet_da8eb9ea.y,cooInd_8c585717.TSetBuiSup)
    annotation (Line(points={{71,-80},{36.8018,-80},{36.8018,-42.5986},{36.8018,-22.5986},{36.8018,-2.59863},{36.8018,
          17.4014},{36.8018,40},{8,40}},                                                                                                                                                                                                        color={0,0,127}));

  //
  // End Connect Statements for da8eb9ea
  //

  //
  // Begin Connect Statements for 9d460edc
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // cooling indirect and network 2 pipe

  connect(disNet_0a531ebc.ports_bCon[2],cooInd_8c585717.port_a1)
    annotation (Line(points={{-28,130},{3.32411,130},{3.32411,79.9493},{3.32411,59.9493},{3.32411,46},{9.99999,46}},                                                                                                                                                 color={0,0,127}));
  connect(disNet_0a531ebc.ports_aCon[2],cooInd_8c585717.port_b1)
    annotation (Line(points={{-16,130},{-0.823374,130},{-0.823374,74.1347},{-0.823374,54.1347},{-0.823374,46},{30,46}},                                                                                                                                                      color={0,0,127}));

  //
  // End Connect Statements for 9d460edc
  //

  //
  // Begin Connect Statements for 72f54e3c
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ConnectStatements.mopt
  //

  // cooling indirect, timeseries coupling connections
  connect(TimeSerLoa_40b5db32.ports_bHeaWat[1], heaInd_06ab776a.port_a2)
    annotation (Line(points={{70,38},{70,-9.54597},{30,-9.54597},{30,-6}},                                                                                                            color={0,0,127}));
  connect(heaInd_06ab776a.port_b2,TimeSerLoa_40b5db32.ports_aHeaWat[1])
    annotation (Line(points={{10,-6},{34.2237,-6},{34.2237,38},{50,38}},                                                                                                                   color={0,0,127}));
  connect(pressure_source_72f54e3c.ports[1], heaInd_06ab776a.port_b2)
    annotation (Line(points={{-50,-120},{-48.9154,-120},{-48.9154,-84.42},{-48.9154,-64.42},{-48.9154,-44.42},{-48.9154,
          -24.42},{-48.9154,-4.42002},{-28.9154,-4.42002},{10,-4.42002},{10,-6}},                                                                                                                                                                                                        color={0,0,127}));
  connect(THeaWatSet_72f54e3c.y,heaInd_06ab776a.TSetBuiSup)
    annotation (Line(points={{-9,-120},{3.84222,-120},{3.84222,-74.14},{3.84222,-54.14},{3.84222,-34.14},{3.84222,-14.14},
          {3.84222,2.7376e-06},{8,2.7376e-06}},                                                                                                                                                                                                        color={0,0,127}));

  //
  // End Connect Statements for 72f54e3c
  //

  //
  // Begin Connect Statements for afcd41bc
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // heating indirect and network 2 pipe

  connect(disNet_aaccda4a.ports_bCon[2],heaInd_06ab776a.port_a1)
    annotation (Line(points={{-28,90},{-28,34.4862},{-28,14.4862},{-28,-5.51381},{10,-5.51381},{10,6}},                                                                                                                                                                          color={0,0,127}));
  connect(disNet_aaccda4a.ports_aCon[2],heaInd_06ab776a.port_b1)
    annotation (Line(points={{-16,90},{-16,30.4018},{-16,10.4018},{-16,-9.59815},{30,-9.59815},{30,6}},                                                                                                                                                                        color={0,0,127}));

  //
  // End Connect Statements for afcd41bc
  //

  connect(avaSig.y, eleFol.avaSig)
    annotation (Line(points={{-139,90},{-128,90},{-128,47},{-82,47}},  color={255,0,255}));
  connect(theFolSig.y, eleFol.theFol)
    annotation (Line(points={{-139,58},{-136,58},{-136,45},{-82,45}}, color={255,0,255}));
  connect(TWatOutSet.y, eleFol.TWatOutSet)
    annotation (Line(points={{-99,62},{-92,62},{-92,43},{-82,43}}, color={0,0,127}));
  connect(ElePowDem.y, eleFol.PEleDem)
    annotation (Line(points={{-99,92},{-92,92},{-92,41},{-82,41}}, color={0,0,127}));
  connect(eleFol.port_b, disNet_aaccda4a.port_aDisSup)
    annotation (Line(points={{-60,38},{-42,38},{-42,85},{-30,85}}, color={0,127,255}));
  connect(eleFol.port_a, disNet_aaccda4a.port_bDisRet)
    annotation (Line(points={{-80,38},{-88,38},{-88,8},{-36,8},{-36,82},{-30,82}}, color={0,127,255}));
annotation (
  experiment(
    StopTime=86400,
    Interval=3600,
    Tolerance=1e-06),
  Diagram(
    coordinateSystem(
      preserveAspectRatio=false,
      extent={{-180,-150},{90,150}})),
  Documentation(
    revisions="<html>
 <li>
 May 10, 2020: Hagar Elarga<br/>
Updated implementation to handle template needed for GeoJSON to Modelica.
</li>
</html>"),
    Icon(coordinateSystem(extent={{-180,-150},{90,150}})));
end DistrictEnergySystemCHP;