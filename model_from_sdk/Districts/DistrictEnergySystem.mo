within model_from_sdk.Districts;
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
  // Begin Model Instance for disNet_0659f6eb
  // Source template: /model_connectors/networks/templates/Network2Pipe_Instance.mopt
  //
parameter Integer nBui_disNet_0659f6eb=4;
  parameter Modelica.SIunits.MassFlowRate mDis_flow_nominal_disNet_0659f6eb=sum({
    cooInd_a11d97ad.mDis_flow_nominal,
  cooInd_5e057248.mDis_flow_nominal,
  cooInd_a58fc75a.mDis_flow_nominal,
  cooInd_d0c8c34f.mDis_flow_nominal})
    "Nominal mass flow rate of the distribution pump";
  parameter Modelica.SIunits.MassFlowRate mCon_flow_nominal_disNet_0659f6eb[nBui_disNet_0659f6eb]={
    cooInd_a11d97ad.mDis_flow_nominal,
  cooInd_5e057248.mDis_flow_nominal,
  cooInd_a58fc75a.mDis_flow_nominal,
  cooInd_d0c8c34f.mDis_flow_nominal}
    "Nominal mass flow rate in each connection line";
  parameter Modelica.SIunits.PressureDifference dpDis_nominal_disNet_0659f6eb[nBui_disNet_0659f6eb](
    each min=0,
    each displayUnit="Pa")=1/2 .* cat(
    1,
    {dp_nominal_disNet_0659f6eb*0.1},
    fill(
      dp_nominal_disNet_0659f6eb*0.9/(nBui_disNet_0659f6eb-1),
      nBui_disNet_0659f6eb-1))
    "Pressure drop between each connected building at nominal conditions (supply line)";
  parameter Modelica.SIunits.PressureDifference dp_nominal_disNet_0659f6eb=dpSetPoi_disNet_0659f6eb+nBui_disNet_0659f6eb*7000
    "District network pressure drop";
  // NOTE: this differential pressure setpoint is currently utilized by plants elsewhere
  parameter Modelica.SIunits.Pressure dpSetPoi_disNet_0659f6eb=50000
    "Differential pressure setpoint";

  Buildings.Experimental.DHC.Loads.Validation.BaseClasses.Distribution2Pipe disNet_0659f6eb(
    redeclare final package Medium=MediumW,
    final nCon=nBui_disNet_0659f6eb,
    iConDpSen=nBui_disNet_0659f6eb,
    final mDis_flow_nominal=mDis_flow_nominal_disNet_0659f6eb,
    final mCon_flow_nominal=mCon_flow_nominal_disNet_0659f6eb,
    final allowFlowReversal=false,
    dpDis_nominal=dpDis_nominal_disNet_0659f6eb)
    "Distribution network."
    annotation (Placement(transformation(extent={{-30.0,240.0},{-10.0,250.0}})));
  //
  // End Model Instance for disNet_0659f6eb
  //



  //
  // Begin Model Instance for cooPla_7a98179f
  // Source template: /model_connectors/plants/templates/CoolingPlant_Instance.mopt
  //
  parameter Modelica.SIunits.MassFlowRate mCHW_flow_nominal_cooPla_7a98179f=cooPla_7a98179f.numChi*(cooPla_7a98179f.perChi.mEva_flow_nominal)
    "Nominal chilled water mass flow rate";
  parameter Modelica.SIunits.MassFlowRate mCW_flow_nominal_cooPla_7a98179f=cooPla_7a98179f.perChi.mCon_flow_nominal
    "Nominal condenser water mass flow rate";
  parameter Modelica.SIunits.PressureDifference dpCHW_nominal_cooPla_7a98179f=44.8*1000
    "Nominal chilled water side pressure";
  parameter Modelica.SIunits.PressureDifference dpCW_nominal_cooPla_7a98179f=46.2*1000
    "Nominal condenser water side pressure";
  parameter Modelica.SIunits.Power QEva_nominal_cooPla_7a98179f=mCHW_flow_nominal_cooPla_7a98179f*4200*(5-14)
    "Nominal cooling capaciaty (Negative means cooling)";
  parameter Modelica.SIunits.MassFlowRate mMin_flow_cooPla_7a98179f=0.2*mCHW_flow_nominal_cooPla_7a98179f/cooPla_7a98179f.numChi
    "Minimum mass flow rate of single chiller";
  // control settings
  parameter Modelica.SIunits.Pressure dpSetPoi_cooPla_7a98179f=70000
    "Differential pressure setpoint";
  parameter Modelica.SIunits.Pressure pumDP_cooPla_7a98179f=dpCHW_nominal_cooPla_7a98179f+dpSetPoi_cooPla_7a98179f+200000;
  parameter Modelica.SIunits.Time tWai_cooPla_7a98179f=30
    "Waiting time";
  // pumps
  parameter Buildings.Fluid.Movers.Data.Generic perCHWPum_cooPla_7a98179f(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=((mCHW_flow_nominal_cooPla_7a98179f/cooPla_7a98179f.numChi)/1000)*{0.1,1,1.2},
      dp=pumDP_cooPla_7a98179f*{1.2,1,0.1}))
    "Performance data for chilled water pumps";
  parameter Buildings.Fluid.Movers.Data.Generic perCWPum_cooPla_7a98179f(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=mCW_flow_nominal_cooPla_7a98179f/1000*{0.2,0.6,1.0,1.2},
      dp=(dpCW_nominal_cooPla_7a98179f+60000+6000)*{1.2,1.1,1.0,0.6}))
    "Performance data for condenser water pumps";


  Modelica.Blocks.Sources.RealExpression TSetChiWatDis_cooPla_7a98179f(
    y=5+273.15)
    "Chilled water supply temperature set point on district level."
    annotation (Placement(transformation(extent={{10.0,-250.0},{30.0,-230.0}})));
  Modelica.Blocks.Sources.BooleanConstant on_cooPla_7a98179f
    "On signal of the plant"
    annotation (Placement(transformation(extent={{50.0,-250.0},{70.0,-230.0}})));

  model_from_sdk.Plants.CentralCoolingPlant cooPla_7a98179f(
    redeclare Buildings.Fluid.Chillers.Data.ElectricEIR.ElectricEIRChiller_Carrier_19EX_5208kW_6_88COP_Vanes perChi,
    perCHWPum=perCHWPum_cooPla_7a98179f,
    perCWPum=perCWPum_cooPla_7a98179f,
    mCHW_flow_nominal=mCHW_flow_nominal_cooPla_7a98179f,
    dpCHW_nominal=dpCHW_nominal_cooPla_7a98179f,
    QEva_nominal=QEva_nominal_cooPla_7a98179f,
    mMin_flow=mMin_flow_cooPla_7a98179f,
    mCW_flow_nominal=mCW_flow_nominal_cooPla_7a98179f,
    dpCW_nominal=dpCW_nominal_cooPla_7a98179f,
    TAirInWB_nominal=298.7,
    TCW_nominal=308.15,
    TMin=288.15,
    tWai=tWai_cooPla_7a98179f,
    dpSetPoi=dpSetPoi_cooPla_7a98179f,
    energyDynamics=Modelica.Fluid.Types.Dynamics.FixedInitial)
    "District cooling plant."
    annotation (Placement(transformation(extent={{-70.0,230.0},{-50.0,250.0}})));
  //
  // End Model Instance for cooPla_7a98179f
  //



  //
  // Begin Model Instance for disNet_eed2e036
  // Source template: /model_connectors/networks/templates/Network2Pipe_Instance.mopt
  //
parameter Integer nBui_disNet_eed2e036=4;
  parameter Modelica.SIunits.MassFlowRate mDis_flow_nominal_disNet_eed2e036=sum({
    heaInd_16e95443.mDis_flow_nominal,
  heaInd_a5bcccb6.mDis_flow_nominal,
  heaInd_9b2854d7.mDis_flow_nominal,
  heaInd_dda3250a.mDis_flow_nominal})
    "Nominal mass flow rate of the distribution pump";
  parameter Modelica.SIunits.MassFlowRate mCon_flow_nominal_disNet_eed2e036[nBui_disNet_eed2e036]={
    heaInd_16e95443.mDis_flow_nominal,
  heaInd_a5bcccb6.mDis_flow_nominal,
  heaInd_9b2854d7.mDis_flow_nominal,
  heaInd_dda3250a.mDis_flow_nominal}
    "Nominal mass flow rate in each connection line";
  parameter Modelica.SIunits.PressureDifference dpDis_nominal_disNet_eed2e036[nBui_disNet_eed2e036](
    each min=0,
    each displayUnit="Pa")=1/2 .* cat(
    1,
    {dp_nominal_disNet_eed2e036*0.1},
    fill(
      dp_nominal_disNet_eed2e036*0.9/(nBui_disNet_eed2e036-1),
      nBui_disNet_eed2e036-1))
    "Pressure drop between each connected building at nominal conditions (supply line)";
  parameter Modelica.SIunits.PressureDifference dp_nominal_disNet_eed2e036=dpSetPoi_disNet_eed2e036+nBui_disNet_eed2e036*7000
    "District network pressure drop";
  // NOTE: this differential pressure setpoint is currently utilized by plants elsewhere
  parameter Modelica.SIunits.Pressure dpSetPoi_disNet_eed2e036=50000
    "Differential pressure setpoint";

  Buildings.Experimental.DHC.Loads.Validation.BaseClasses.Distribution2Pipe disNet_eed2e036(
    redeclare final package Medium=MediumW,
    final nCon=nBui_disNet_eed2e036,
    iConDpSen=nBui_disNet_eed2e036,
    final mDis_flow_nominal=mDis_flow_nominal_disNet_eed2e036,
    final mCon_flow_nominal=mCon_flow_nominal_disNet_eed2e036,
    final allowFlowReversal=false,
    dpDis_nominal=dpDis_nominal_disNet_eed2e036)
    "Distribution network."
    annotation (Placement(transformation(extent={{-30.0,200.0},{-10.0,210.0}})));
  //
  // End Model Instance for disNet_eed2e036
  //



  //
  // Begin Model Instance for heaPlabddcd2c8
  // Source template: /model_connectors/plants/templates/HeatingPlant_Instance.mopt
  //
  // heating plant instance
  parameter Modelica.SIunits.MassFlowRate mHW_flow_nominal_heaPlabddcd2c8=mBoi_flow_nominal_heaPlabddcd2c8*heaPlabddcd2c8.numBoi
    "Nominal heating water mass flow rate";
  parameter Modelica.SIunits.MassFlowRate mBoi_flow_nominal_heaPlabddcd2c8=QBoi_nominal_heaPlabddcd2c8/(4200*heaPlabddcd2c8.delT_nominal)
    "Nominal heating water mass flow rate";
  parameter Modelica.SIunits.Power QBoi_nominal_heaPlabddcd2c8=Q_flow_nominal_heaPlabddcd2c8/heaPlabddcd2c8.numBoi
    "Nominal heating capaciaty";
  parameter Modelica.SIunits.HeatFlowRate Q_flow_nominal_heaPlabddcd2c8=1000000*2
    "Heating load";
  parameter Modelica.SIunits.MassFlowRate mMin_flow_heaPlabddcd2c8=0.2*mBoi_flow_nominal_heaPlabddcd2c8
    "Minimum mass flow rate of single boiler";
  // controls
  parameter Modelica.SIunits.Pressure pumDP=(heaPlabddcd2c8.dpBoi_nominal+dpSetPoi_disNet_eed2e036+50000)
    "Heating water pump pressure drop";
  parameter Modelica.SIunits.Time tWai_heaPlabddcd2c8=30
    "Waiting time";
  parameter Buildings.Fluid.Movers.Data.Generic perHWPum_heaPlabddcd2c8(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=mBoi_flow_nominal_heaPlabddcd2c8/1000*{0.1,1.1},
      dp=pumDP*{1.1,0.1}))
    "Performance data for heating water pumps";

  model_from_sdk.Plants.CentralHeatingPlant heaPlabddcd2c8(
    perHWPum=perHWPum_heaPlabddcd2c8,
    mHW_flow_nominal=mHW_flow_nominal_heaPlabddcd2c8,
    QBoi_flow_nominal=QBoi_nominal_heaPlabddcd2c8,
    mMin_flow=mMin_flow_heaPlabddcd2c8,
    mBoi_flow_nominal=mBoi_flow_nominal_heaPlabddcd2c8,
    dpBoi_nominal=10000,
    delT_nominal(
      displayUnit="degC")=15,
    tWai=tWai_heaPlabddcd2c8,
    // TODO: we're currently grabbing dpSetPoi from the Network instance -- need feedback to determine if that's the proper "home" for it
    dpSetPoi=dpSetPoi_disNet_eed2e036,
    energyDynamics=Modelica.Fluid.Types.Dynamics.FixedInitial)
    "District heating plant."
    annotation (Placement(transformation(extent={{-70.0,190.0},{-50.0,210.0}})));
  //
  // End Model Instance for heaPlabddcd2c8
  //



  //
  // Begin Model Instance for TimeSerLoa_4ff1b7e3
  // Source template: /model_connectors/load_connectors/templates/TimeSeries_Instance.mopt
  //
  // time series load
  model_from_sdk.Loads.B2.building TimeSerLoa_4ff1b7e3(
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
    annotation (Placement(transformation(extent={{50.0,230.0},{70.0,250.0}})));
  //
  // End Model Instance for TimeSerLoa_4ff1b7e3
  //



  //
  // Begin Model Instance for cooInd_a11d97ad
  // Source template: /model_connectors/energy_transfer_systems/templates/CoolingIndirect_Instance.mopt
  //
  // cooling indirect instance
  model_from_sdk.Substations.CoolingIndirect_2 cooInd_a11d97ad(
    redeclare package Medium=MediumW,
    allowFlowReversal1=false,
    allowFlowReversal2=false,
    mDis_flow_nominal=mDis_flow_nominal_476b9595,
    mBui_flow_nominal=mBui_flow_nominal_476b9595,
    dp1_nominal=500,
    dp2_nominal=500,
    dpValve_nominal=7000,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_476b9595,
    // TODO: dehardcode the nominal temperatures?
    T_a1_nominal=273.15+5,
    T_a2_nominal=273.15+13)
    "Indirect cooling energy transfer station ETS."
    annotation (Placement(transformation(extent={{10.0,190.0},{30.0,210.0}})));
  //
  // End Model Instance for cooInd_a11d97ad
  //



  //
  // Begin Model Instance for heaInd_16e95443
  // Source template: /model_connectors/energy_transfer_systems/templates/HeatingIndirect_Instance.mopt
  //
  // heating indirect instance
  model_from_sdk.Substations.HeatingIndirect_2 heaInd_16e95443(
    allowFlowReversal1=false,
    allowFlowReversal2=false,
    show_T=true,
    redeclare package Medium=MediumW,
    mDis_flow_nominal=mDis_flow_nominal_b3337893,
    mBui_flow_nominal=mBui_flow_nominal_b3337893,
    dpValve_nominal=6000,
    dp1_nominal=500,
    dp2_nominal=500,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_b3337893,
    T_a1_nominal=55+273.15,
    T_a2_nominal=35+273.15,
    k=0.1,
    Ti=60,
    reverseActing=true)
    annotation (Placement(transformation(extent={{10.0,230.0},{30.0,250.0}})));
  //
  // End Model Instance for heaInd_16e95443
  //



  //
  // Begin Model Instance for TimeSerLoa_76c14bd6
  // Source template: /model_connectors/load_connectors/templates/TimeSeries_Instance.mopt
  //
  // time series load
  model_from_sdk.Loads.B4.building TimeSerLoa_76c14bd6(
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
    annotation (Placement(transformation(extent={{50.0,150.0},{70.0,170.0}})));
  //
  // End Model Instance for TimeSerLoa_76c14bd6
  //



  //
  // Begin Model Instance for cooInd_5e057248
  // Source template: /model_connectors/energy_transfer_systems/templates/CoolingIndirect_Instance.mopt
  //
  // cooling indirect instance
  model_from_sdk.Substations.CoolingIndirect_4 cooInd_5e057248(
    redeclare package Medium=MediumW,
    allowFlowReversal1=false,
    allowFlowReversal2=false,
    mDis_flow_nominal=mDis_flow_nominal_1a74b9df,
    mBui_flow_nominal=mBui_flow_nominal_1a74b9df,
    dp1_nominal=500,
    dp2_nominal=500,
    dpValve_nominal=7000,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_1a74b9df,
    // TODO: dehardcode the nominal temperatures?
    T_a1_nominal=273.15+5,
    T_a2_nominal=273.15+13)
    "Indirect cooling energy transfer station ETS."
    annotation (Placement(transformation(extent={{10.0,110.0},{30.0,130.0}})));
  //
  // End Model Instance for cooInd_5e057248
  //



  //
  // Begin Model Instance for heaInd_a5bcccb6
  // Source template: /model_connectors/energy_transfer_systems/templates/HeatingIndirect_Instance.mopt
  //
  // heating indirect instance
  model_from_sdk.Substations.HeatingIndirect_4 heaInd_a5bcccb6(
    allowFlowReversal1=false,
    allowFlowReversal2=false,
    show_T=true,
    redeclare package Medium=MediumW,
    mDis_flow_nominal=mDis_flow_nominal_a1ec1627,
    mBui_flow_nominal=mBui_flow_nominal_a1ec1627,
    dpValve_nominal=6000,
    dp1_nominal=500,
    dp2_nominal=500,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_a1ec1627,
    T_a1_nominal=55+273.15,
    T_a2_nominal=35+273.15,
    k=0.1,
    Ti=60,
    reverseActing=true)
    annotation (Placement(transformation(extent={{10.0,150.0},{30.0,170.0}})));
  //
  // End Model Instance for heaInd_a5bcccb6
  //



  //
  // Begin Model Instance for TimeSerLoa_baaf0022
  // Source template: /model_connectors/load_connectors/templates/TimeSeries_Instance.mopt
  //
  // time series load
  model_from_sdk.Loads.B5.building TimeSerLoa_baaf0022(
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
  // End Model Instance for TimeSerLoa_baaf0022
  //



  //
  // Begin Model Instance for cooInd_a58fc75a
  // Source template: /model_connectors/energy_transfer_systems/templates/CoolingIndirect_Instance.mopt
  //
  // cooling indirect instance
  model_from_sdk.Substations.CoolingIndirect_5 cooInd_a58fc75a(
    redeclare package Medium=MediumW,
    allowFlowReversal1=false,
    allowFlowReversal2=false,
    mDis_flow_nominal=mDis_flow_nominal_0071de0f,
    mBui_flow_nominal=mBui_flow_nominal_0071de0f,
    dp1_nominal=500,
    dp2_nominal=500,
    dpValve_nominal=7000,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_0071de0f,
    // TODO: dehardcode the nominal temperatures?
    T_a1_nominal=273.15+5,
    T_a2_nominal=273.15+13)
    "Indirect cooling energy transfer station ETS."
    annotation (Placement(transformation(extent={{10.0,30.0},{30.0,50.0}})));
  //
  // End Model Instance for cooInd_a58fc75a
  //



  //
  // Begin Model Instance for heaInd_9b2854d7
  // Source template: /model_connectors/energy_transfer_systems/templates/HeatingIndirect_Instance.mopt
  //
  // heating indirect instance
  model_from_sdk.Substations.HeatingIndirect_5 heaInd_9b2854d7(
    allowFlowReversal1=false,
    allowFlowReversal2=false,
    show_T=true,
    redeclare package Medium=MediumW,
    mDis_flow_nominal=mDis_flow_nominal_f8c646c1,
    mBui_flow_nominal=mBui_flow_nominal_f8c646c1,
    dpValve_nominal=6000,
    dp1_nominal=500,
    dp2_nominal=500,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_f8c646c1,
    T_a1_nominal=55+273.15,
    T_a2_nominal=35+273.15,
    k=0.1,
    Ti=60,
    reverseActing=true)
    annotation (Placement(transformation(extent={{10.0,70.0},{30.0,90.0}})));
  //
  // End Model Instance for heaInd_9b2854d7
  //



  //
  // Begin Model Instance for TimeSerLoa_78820bfd
  // Source template: /model_connectors/load_connectors/templates/TimeSeries_Instance.mopt
  //
  // time series load
  model_from_sdk.Loads.B6.building TimeSerLoa_78820bfd(
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
    annotation (Placement(transformation(extent={{50.0,-10.0},{70.0,10.0}})));
  //
  // End Model Instance for TimeSerLoa_78820bfd
  //



  //
  // Begin Model Instance for cooInd_d0c8c34f
  // Source template: /model_connectors/energy_transfer_systems/templates/CoolingIndirect_Instance.mopt
  //
  // cooling indirect instance
  model_from_sdk.Substations.CoolingIndirect_6 cooInd_d0c8c34f(
    redeclare package Medium=MediumW,
    allowFlowReversal1=false,
    allowFlowReversal2=false,
    mDis_flow_nominal=mDis_flow_nominal_18c3f8dd,
    mBui_flow_nominal=mBui_flow_nominal_18c3f8dd,
    dp1_nominal=500,
    dp2_nominal=500,
    dpValve_nominal=7000,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_18c3f8dd,
    // TODO: dehardcode the nominal temperatures?
    T_a1_nominal=273.15+5,
    T_a2_nominal=273.15+13)
    "Indirect cooling energy transfer station ETS."
    annotation (Placement(transformation(extent={{10.0,-50.0},{30.0,-30.0}})));
  //
  // End Model Instance for cooInd_d0c8c34f
  //



  //
  // Begin Model Instance for heaInd_dda3250a
  // Source template: /model_connectors/energy_transfer_systems/templates/HeatingIndirect_Instance.mopt
  //
  // heating indirect instance
  model_from_sdk.Substations.HeatingIndirect_6 heaInd_dda3250a(
    allowFlowReversal1=false,
    allowFlowReversal2=false,
    show_T=true,
    redeclare package Medium=MediumW,
    mDis_flow_nominal=mDis_flow_nominal_99235804,
    mBui_flow_nominal=mBui_flow_nominal_99235804,
    dpValve_nominal=6000,
    dp1_nominal=500,
    dp2_nominal=500,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_99235804,
    T_a1_nominal=55+273.15,
    T_a2_nominal=35+273.15,
    k=0.1,
    Ti=60,
    reverseActing=true)
    annotation (Placement(transformation(extent={{10.0,-10.0},{30.0,10.0}})));
  //
  // End Model Instance for heaInd_dda3250a
  //




  // Model dependencies

  //
  // Begin Component Definitions for 6a500d63
  // Source template: /model_connectors/couplings/templates/Network2Pipe_CoolingPlant/ComponentDefinitions.mopt
  //
  // No components for pipe and cooling plant

  //
  // End Component Definitions for 6a500d63
  //



  //
  // Begin Component Definitions for 3ac546a8
  // Source template: /model_connectors/couplings/templates/Network2Pipe_HeatingPlant/ComponentDefinitions.mopt
  //
  // TODO: This should not be here, it is entirely plant specific and should be moved elsewhere
  // but since it requires a connect statement we must put it here for now...
  Modelica.Blocks.Sources.BooleanConstant mPum_flow_3ac546a8(
    k=true)
    "Total heating water pump mass flow rate"
    annotation (Placement(transformation(extent={{-70.0,-90.0},{-50.0,-70.0}})));
  // TODO: This should not be here, it is entirely plant specific and should be moved elsewhere
  // but since it requires a connect statement we must put it here for now...
  Modelica.Blocks.Sources.RealExpression TDisSetHeaWat_3ac546a8(
    each y=273.15+54)
    "District side heating water supply temperature set point."
    annotation (Placement(transformation(extent={{-30.0,-90.0},{-10.0,-70.0}})));

  //
  // End Component Definitions for 3ac546a8
  //



  //
  // Begin Component Definitions for 476b9595
  // Source template: /model_connectors/couplings/templates/TimeSeries_CoolingIndirect/ComponentDefinitions.mopt
  //
  // TimeSeries + CoolingIndirect Component Definitions
  parameter Modelica.SIunits.MassFlowRate mDis_flow_nominal_476b9595=TimeSerLoa_4ff1b7e3.mChiWat_flow_nominal*delChiWatTemBui/delChiWatTemDis
    "Nominal mass flow rate of primary (district) district cooling side";
  parameter Modelica.SIunits.MassFlowRate mBui_flow_nominal_476b9595=TimeSerLoa_4ff1b7e3.mChiWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district cooling side";
  parameter Modelica.SIunits.HeatFlowRate Q_flow_nominal_476b9595=-1*(TimeSerLoa_4ff1b7e3.QCoo_flow_nominal);
  Modelica.Fluid.Sources.FixedBoundary pressure_source_476b9595(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{10.0,-90.0},{30.0,-70.0}})));
  // TODO: move TChiWatSet (and its connection) into a CoolingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression TChiWatSet_476b9595(
    y=7+273.15)
    //Dehardcode
    "Primary loop (district side) chilled water setpoint temperature."
    annotation (Placement(transformation(extent={{50.0,-90.0},{70.0,-70.0}})));

  //
  // End Component Definitions for 476b9595
  //



  //
  // Begin Component Definitions for 96d64aae
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for cooling indirect and network 2 pipe

  //
  // End Component Definitions for 96d64aae
  //



  //
  // Begin Component Definitions for b3337893
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ComponentDefinitions.mopt
  //
  // TimeSeries + HeatingIndirect Component Definitions
  // TODO: the components below need to be fixed!
  parameter Modelica.SIunits.MassFlowRate mDis_flow_nominal_b3337893=TimeSerLoa_4ff1b7e3.mHeaWat_flow_nominal*delHeaWatTemBui/delHeaWatTemDis
    "Nominal mass flow rate of primary (district) district heating side";
  parameter Modelica.SIunits.MassFlowRate mBui_flow_nominal_b3337893=TimeSerLoa_4ff1b7e3.mHeaWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district heating side";
  parameter Modelica.SIunits.HeatFlowRate Q_flow_nominal_b3337893=(TimeSerLoa_4ff1b7e3.QHea_flow_nominal);
  Modelica.Fluid.Sources.FixedBoundary pressure_source_b3337893(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{-70.0,-130.0},{-50.0,-110.0}})));
  // TODO: move THeaWatSet (and its connection) into a HeatingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression THeaWatSet_b3337893(
    // y=40+273.15)
    y=273.15+40 )
    "Secondary loop (Building side) heating water setpoint temperature."
    //Dehardcode
    annotation (Placement(transformation(extent={{-30.0,-130.0},{-10.0,-110.0}})));

  //
  // End Component Definitions for b3337893
  //



  //
  // Begin Component Definitions for 2f68639d
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for heating indirect and network 2 pipe

  //
  // End Component Definitions for 2f68639d
  //



  //
  // Begin Component Definitions for 1a74b9df
  // Source template: /model_connectors/couplings/templates/TimeSeries_CoolingIndirect/ComponentDefinitions.mopt
  //
  // TimeSeries + CoolingIndirect Component Definitions
  parameter Modelica.SIunits.MassFlowRate mDis_flow_nominal_1a74b9df=TimeSerLoa_76c14bd6.mChiWat_flow_nominal*delChiWatTemBui/delChiWatTemDis
    "Nominal mass flow rate of primary (district) district cooling side";
  parameter Modelica.SIunits.MassFlowRate mBui_flow_nominal_1a74b9df=TimeSerLoa_76c14bd6.mChiWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district cooling side";
  parameter Modelica.SIunits.HeatFlowRate Q_flow_nominal_1a74b9df=-1*(TimeSerLoa_76c14bd6.QCoo_flow_nominal);
  Modelica.Fluid.Sources.FixedBoundary pressure_source_1a74b9df(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{10.0,-130.0},{30.0,-110.0}})));
  // TODO: move TChiWatSet (and its connection) into a CoolingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression TChiWatSet_1a74b9df(
    y=7+273.15)
    //Dehardcode
    "Primary loop (district side) chilled water setpoint temperature."
    annotation (Placement(transformation(extent={{50.0,-130.0},{70.0,-110.0}})));

  //
  // End Component Definitions for 1a74b9df
  //



  //
  // Begin Component Definitions for 67792418
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for cooling indirect and network 2 pipe

  //
  // End Component Definitions for 67792418
  //



  //
  // Begin Component Definitions for a1ec1627
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ComponentDefinitions.mopt
  //
  // TimeSeries + HeatingIndirect Component Definitions
  // TODO: the components below need to be fixed!
  parameter Modelica.SIunits.MassFlowRate mDis_flow_nominal_a1ec1627=TimeSerLoa_76c14bd6.mHeaWat_flow_nominal*delHeaWatTemBui/delHeaWatTemDis
    "Nominal mass flow rate of primary (district) district heating side";
  parameter Modelica.SIunits.MassFlowRate mBui_flow_nominal_a1ec1627=TimeSerLoa_76c14bd6.mHeaWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district heating side";
  parameter Modelica.SIunits.HeatFlowRate Q_flow_nominal_a1ec1627=(TimeSerLoa_76c14bd6.QHea_flow_nominal);
  Modelica.Fluid.Sources.FixedBoundary pressure_source_a1ec1627(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{-70.0,-170.0},{-50.0,-150.0}})));
  // TODO: move THeaWatSet (and its connection) into a HeatingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression THeaWatSet_a1ec1627(
    // y=40+273.15)
    y=273.15+40 )
    "Secondary loop (Building side) heating water setpoint temperature."
    //Dehardcode
    annotation (Placement(transformation(extent={{-30.0,-170.0},{-10.0,-150.0}})));

  //
  // End Component Definitions for a1ec1627
  //



  //
  // Begin Component Definitions for 4019d966
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for heating indirect and network 2 pipe

  //
  // End Component Definitions for 4019d966
  //



  //
  // Begin Component Definitions for 0071de0f
  // Source template: /model_connectors/couplings/templates/TimeSeries_CoolingIndirect/ComponentDefinitions.mopt
  //
  // TimeSeries + CoolingIndirect Component Definitions
  parameter Modelica.SIunits.MassFlowRate mDis_flow_nominal_0071de0f=TimeSerLoa_baaf0022.mChiWat_flow_nominal*delChiWatTemBui/delChiWatTemDis
    "Nominal mass flow rate of primary (district) district cooling side";
  parameter Modelica.SIunits.MassFlowRate mBui_flow_nominal_0071de0f=TimeSerLoa_baaf0022.mChiWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district cooling side";
  parameter Modelica.SIunits.HeatFlowRate Q_flow_nominal_0071de0f=-1*(TimeSerLoa_baaf0022.QCoo_flow_nominal);
  Modelica.Fluid.Sources.FixedBoundary pressure_source_0071de0f(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{10.0,-170.0},{30.0,-150.0}})));
  // TODO: move TChiWatSet (and its connection) into a CoolingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression TChiWatSet_0071de0f(
    y=7+273.15)
    //Dehardcode
    "Primary loop (district side) chilled water setpoint temperature."
    annotation (Placement(transformation(extent={{50.0,-170.0},{70.0,-150.0}})));

  //
  // End Component Definitions for 0071de0f
  //



  //
  // Begin Component Definitions for 45305f18
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for cooling indirect and network 2 pipe

  //
  // End Component Definitions for 45305f18
  //



  //
  // Begin Component Definitions for f8c646c1
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ComponentDefinitions.mopt
  //
  // TimeSeries + HeatingIndirect Component Definitions
  // TODO: the components below need to be fixed!
  parameter Modelica.SIunits.MassFlowRate mDis_flow_nominal_f8c646c1=TimeSerLoa_baaf0022.mHeaWat_flow_nominal*delHeaWatTemBui/delHeaWatTemDis
    "Nominal mass flow rate of primary (district) district heating side";
  parameter Modelica.SIunits.MassFlowRate mBui_flow_nominal_f8c646c1=TimeSerLoa_baaf0022.mHeaWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district heating side";
  parameter Modelica.SIunits.HeatFlowRate Q_flow_nominal_f8c646c1=(TimeSerLoa_baaf0022.QHea_flow_nominal);
  Modelica.Fluid.Sources.FixedBoundary pressure_source_f8c646c1(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{-70.0,-210.0},{-50.0,-190.0}})));
  // TODO: move THeaWatSet (and its connection) into a HeatingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression THeaWatSet_f8c646c1(
    // y=40+273.15)
    y=273.15+40 )
    "Secondary loop (Building side) heating water setpoint temperature."
    //Dehardcode
    annotation (Placement(transformation(extent={{-30.0,-210.0},{-10.0,-190.0}})));

  //
  // End Component Definitions for f8c646c1
  //



  //
  // Begin Component Definitions for 9b13e991
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for heating indirect and network 2 pipe

  //
  // End Component Definitions for 9b13e991
  //



  //
  // Begin Component Definitions for 18c3f8dd
  // Source template: /model_connectors/couplings/templates/TimeSeries_CoolingIndirect/ComponentDefinitions.mopt
  //
  // TimeSeries + CoolingIndirect Component Definitions
  parameter Modelica.SIunits.MassFlowRate mDis_flow_nominal_18c3f8dd=TimeSerLoa_78820bfd.mChiWat_flow_nominal*delChiWatTemBui/delChiWatTemDis
    "Nominal mass flow rate of primary (district) district cooling side";
  parameter Modelica.SIunits.MassFlowRate mBui_flow_nominal_18c3f8dd=TimeSerLoa_78820bfd.mChiWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district cooling side";
  parameter Modelica.SIunits.HeatFlowRate Q_flow_nominal_18c3f8dd=-1*(TimeSerLoa_78820bfd.QCoo_flow_nominal);
  Modelica.Fluid.Sources.FixedBoundary pressure_source_18c3f8dd(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{10.0,-210.0},{30.0,-190.0}})));
  // TODO: move TChiWatSet (and its connection) into a CoolingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression TChiWatSet_18c3f8dd(
    y=7+273.15)
    //Dehardcode
    "Primary loop (district side) chilled water setpoint temperature."
    annotation (Placement(transformation(extent={{50.0,-210.0},{70.0,-190.0}})));

  //
  // End Component Definitions for 18c3f8dd
  //



  //
  // Begin Component Definitions for 67703b4b
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for cooling indirect and network 2 pipe

  //
  // End Component Definitions for 67703b4b
  //



  //
  // Begin Component Definitions for 99235804
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ComponentDefinitions.mopt
  //
  // TimeSeries + HeatingIndirect Component Definitions
  // TODO: the components below need to be fixed!
  parameter Modelica.SIunits.MassFlowRate mDis_flow_nominal_99235804=TimeSerLoa_78820bfd.mHeaWat_flow_nominal*delHeaWatTemBui/delHeaWatTemDis
    "Nominal mass flow rate of primary (district) district heating side";
  parameter Modelica.SIunits.MassFlowRate mBui_flow_nominal_99235804=TimeSerLoa_78820bfd.mHeaWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district heating side";
  parameter Modelica.SIunits.HeatFlowRate Q_flow_nominal_99235804=(TimeSerLoa_78820bfd.QHea_flow_nominal);
  Modelica.Fluid.Sources.FixedBoundary pressure_source_99235804(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{-70.0,-250.0},{-50.0,-230.0}})));
  // TODO: move THeaWatSet (and its connection) into a HeatingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression THeaWatSet_99235804(
    // y=40+273.15)
    y=273.15+40 )
    "Secondary loop (Building side) heating water setpoint temperature."
    //Dehardcode
    annotation (Placement(transformation(extent={{-30.0,-250.0},{-10.0,-230.0}})));

  //
  // End Component Definitions for 99235804
  //



  //
  // Begin Component Definitions for 7b5c02ea
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for heating indirect and network 2 pipe

  //
  // End Component Definitions for 7b5c02ea
  //



equation
  // Connections

  //
  // Begin Connect Statements for 6a500d63
  // Source template: /model_connectors/couplings/templates/Network2Pipe_CoolingPlant/ConnectStatements.mopt
  //

  // TODO: these connect statements shouldn't be here, they are plant specific
  // but since we can't currently make connect statements for single systems, this is what we've got
  connect(on_cooPla_7a98179f.y,cooPla_7a98179f.on)
    annotation (Line(points={{52.06678702052497,-221.9302652086601},{32.06678702052497,-221.9302652086601},{32.06678702052497,-201.9302652086601},{32.06678702052497,-181.9302652086601},{32.06678702052497,-161.9302652086601},{32.06678702052497,-141.9302652086601},{32.06678702052497,-121.9302652086601},{32.06678702052497,-101.9302652086601},{32.06678702052497,-81.9302652086601},{32.06678702052497,-61.9302652086601},{32.06678702052497,-41.9302652086601},{32.06678702052497,-21.930265208660103},{32.06678702052497,-1.9302652086601029},{32.06678702052497,18.069734791339897},{32.06678702052497,38.0697347913399},{32.06678702052497,58.0697347913399},{32.06678702052497,78.0697347913399},{32.06678702052497,98.0697347913399},{32.06678702052497,118.0697347913399},{32.06678702052497,138.0697347913399},{32.06678702052497,158.0697347913399},{32.06678702052497,178.0697347913399},{32.06678702052497,198.0697347913399},{32.06678702052497,218.0697347913399},{12.06678702052497,218.0697347913399},{-7.93321297947503,218.0697347913399},{-27.933212979475037,218.0697347913399},{-47.93321297947504,218.0697347913399},{-47.93321297947504,238.0697347913399},{-67.93321297947503,238.0697347913399}},color={0,0,127}));
  connect(TSetChiWatDis_cooPla_7a98179f.y,cooPla_7a98179f.TCHWSupSet)
    annotation (Line(points={{16.261652928637034,-212.02882021149446},{-3.7383470713629663,-212.02882021149446},{-3.7383470713629663,-192.02882021149446},{-3.7383470713629663,-172.02882021149446},{-3.7383470713629663,-152.02882021149446},{-3.7383470713629663,-132.02882021149446},{-3.7383470713629663,-112.02882021149446},{-3.7383470713629663,-92.02882021149446},{-3.7383470713629663,-72.02882021149446},{-3.7383470713629663,-52.02882021149446},{-3.7383470713629663,-32.02882021149446},{-3.7383470713629663,-12.028820211494462},{-3.7383470713629663,7.9711797885055375},{-3.7383470713629663,27.97117978850551},{-3.7383470713629663,47.97117978850551},{-3.7383470713629663,67.97117978850551},{-3.7383470713629663,87.97117978850551},{-3.7383470713629663,107.97117978850551},{-3.7383470713629663,127.97117978850551},{-3.7383470713629663,147.97117978850554},{-3.7383470713629663,167.97117978850554},{-3.7383470713629663,187.97117978850554},{-3.7383470713629663,207.9711797885055},{-3.7383470713629663,227.9711797885055},{-23.738347071362966,227.9711797885055},{-43.73834707136297,227.9711797885055},{-43.73834707136297,247.9711797885055},{-63.73834707136297,247.9711797885055}},color={0,0,127}));

  connect(disNet_0659f6eb.port_bDisRet,cooPla_7a98179f.port_a)
    annotation (Line(points={{-42.779288465112764,238.06319800413195},{-62.779288465112764,238.06319800413195}},color={0,0,127}));
  connect(cooPla_7a98179f.port_b,disNet_0659f6eb.port_aDisSup)
    annotation (Line(points={{-44.87398560022313,243.79746839916587},{-24.873985600223122,243.79746839916587}},color={0,0,127}));
  connect(disNet_0659f6eb.dp,cooPla_7a98179f.dpMea)
    annotation (Line(points={{-39.47465296030265,234.92020003195626},{-59.47465296030265,234.92020003195626}},color={0,0,127}));

  //
  // End Connect Statements for 6a500d63
  //



  //
  // Begin Connect Statements for 3ac546a8
  // Source template: /model_connectors/couplings/templates/Network2Pipe_HeatingPlant/ConnectStatements.mopt
  //

  connect(heaPlabddcd2c8.port_a,disNet_eed2e036.port_bDisRet)
    annotation (Line(points={{-30.78401517101303,194.79225967234424},{-10.784015171013039,194.79225967234424}},color={0,0,127}));
  connect(disNet_eed2e036.dp,heaPlabddcd2c8.dpMea)
    annotation (Line(points={{-38.44554702354218,209.82730851169663},{-58.44554702354218,209.82730851169663}},color={0,0,127}));
  connect(heaPlabddcd2c8.port_b,disNet_eed2e036.port_aDisSup)
    annotation (Line(points={{-30.48339098970083,199.36684164154667},{-10.483390989700837,199.36684164154667}},color={0,0,127}));
  connect(mPum_flow_3ac546a8.y,heaPlabddcd2c8.on)
    annotation (Line(points={{-63.18405341008749,-59.76580787711015},{-63.18405341008749,-39.76580787711015},{-63.18405341008749,-19.76580787711015},{-63.18405341008749,0.23419212288985136},{-63.18405341008749,20.23419212288988},{-63.18405341008749,40.23419212288988},{-63.18405341008749,60.23419212288988},{-63.18405341008749,80.23419212288988},{-63.18405341008749,100.23419212288988},{-63.18405341008749,120.23419212288988},{-63.18405341008749,140.23419212288988},{-63.18405341008749,160.23419212288985},{-63.18405341008749,180.23419212288985},{-63.18405341008749,200.23419212288985}},color={0,0,127}));
  connect(TDisSetHeaWat_3ac546a8.y,heaPlabddcd2c8.THeaSet)
    annotation (Line(points={{-17.24692758080785,-54.391540496809114},{-17.24692758080785,-34.391540496809114},{-17.24692758080785,-14.391540496809114},{-17.24692758080785,5.608459503190886},{-17.24692758080785,25.608459503190915},{-17.24692758080785,45.608459503190915},{-17.24692758080785,65.60845950319091},{-17.24692758080785,85.60845950319091},{-17.24692758080785,105.60845950319091},{-17.24692758080785,125.60845950319091},{-17.24692758080785,145.6084595031909},{-17.24692758080785,165.6084595031909},{-17.24692758080785,185.6084595031909},{-37.24692758080785,185.6084595031909},{-37.24692758080785,205.6084595031909},{-57.24692758080785,205.6084595031909}},color={0,0,127}));

  //
  // End Connect Statements for 3ac546a8
  //



  //
  // Begin Connect Statements for 476b9595
  // Source template: /model_connectors/couplings/templates/TimeSeries_CoolingIndirect/ConnectStatements.mopt
  //

  // cooling indirect, timeseries coupling connections
  connect(TimeSerLoa_4ff1b7e3.ports_bChiWat[1], cooInd_a11d97ad.port_a2)
    annotation (Line(points={{58.24029642393049,214.75076402368148},{58.24029642393049,194.75076402368148},{38.24029642393049,194.75076402368148},{18.240296423930488,194.75076402368148}},color={0,0,127}));
  connect(cooInd_a11d97ad.port_b2,TimeSerLoa_4ff1b7e3.ports_aChiWat[1])
    annotation (Line(points={{15.748390917406297,227.5660879996758},{35.7483909174063,227.5660879996758},{35.7483909174063,247.5660879996758},{55.74839091740628,247.5660879996758}},color={0,0,127}));
  connect(pressure_source_476b9595.ports[1], cooInd_a11d97ad.port_b2)
    annotation (Line(points={{11.762934760821736,-59.6897399716637},{-8.237065239178264,-59.6897399716637},{-8.237065239178264,-39.6897399716637},{-8.237065239178264,-19.6897399716637},{-8.237065239178264,0.31026002833630173},{-8.237065239178264,20.31026002833633},{-8.237065239178264,40.31026002833633},{-8.237065239178264,60.31026002833633},{-8.237065239178264,80.31026002833633},{-8.237065239178264,100.31026002833633},{-8.237065239178264,120.31026002833633},{-8.237065239178264,140.31026002833633},{-8.237065239178264,160.31026002833633},{-8.237065239178264,180.31026002833633},{-8.237065239178264,200.31026002833633},{11.762934760821736,200.31026002833633}},color={0,0,127}));
  connect(TChiWatSet_476b9595.y,cooInd_a11d97ad.TSetBuiSup)
    annotation (Line(points={{54.1660308539673,-59.40335494087742},{54.1660308539673,-39.40335494087742},{54.1660308539673,-19.40335494087742},{34.1660308539673,-19.40335494087742},{34.1660308539673,0.5966450591225794},{34.1660308539673,20.59664505912258},{34.1660308539673,40.59664505912258},{34.1660308539673,60.59664505912258},{34.1660308539673,80.59664505912258},{34.1660308539673,100.59664505912258},{34.1660308539673,120.59664505912258},{34.1660308539673,140.59664505912258},{34.1660308539673,160.59664505912258},{34.1660308539673,180.59664505912258},{34.1660308539673,200.59664505912258},{34.1660308539673,220.59664505912258},{34.1660308539673,240.59664505912258},{54.1660308539673,240.59664505912258}},color={0,0,127}));

  //
  // End Connect Statements for 476b9595
  //



  //
  // Begin Connect Statements for 96d64aae
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // cooling indirect and network 2 pipe

  connect(disNet_0659f6eb.ports_bCon[1],cooInd_a11d97ad.port_a1)
    annotation (Line(points={{-25.546921112227167,227.81591762683644},{-5.546921112227167,227.81591762683644},{-5.546921112227167,207.81591762683644},{14.453078887772833,207.81591762683644}},color={0,0,127}));
  connect(disNet_0659f6eb.ports_aCon[1],cooInd_a11d97ad.port_b1)
    annotation (Line(points={{-17.075438468637444,212.2492006479863},{2.9245615313625564,212.2492006479863},{2.9245615313625564,192.2492006479863},{22.924561531362556,192.2492006479863}},color={0,0,127}));

  //
  // End Connect Statements for 96d64aae
  //



  //
  // Begin Connect Statements for b3337893
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ConnectStatements.mopt
  //

  // cooling indirect, timeseries coupling connections
  connect(TimeSerLoa_4ff1b7e3.ports_bHeaWat[1], heaInd_16e95443.port_a2)
    annotation (Line(points={{48.721917918223596,232.8423344584702},{28.721917918223596,232.8423344584702}},color={0,0,127}));
  connect(heaInd_16e95443.port_b2,TimeSerLoa_4ff1b7e3.ports_aHeaWat[1])
    annotation (Line(points={{37.85686231180284,232.77098270491837},{57.85686231180284,232.77098270491837}},color={0,0,127}));
  connect(pressure_source_b3337893.ports[1], heaInd_16e95443.port_b2)
    annotation (Line(points={{-56.482442888053846,-98.71245965933406},{-36.482442888053846,-98.71245965933406},{-36.482442888053846,-78.71245965933406},{-36.482442888053846,-58.71245965933406},{-36.482442888053846,-38.71245965933406},{-36.482442888053846,-18.71245965933406},{-36.482442888053846,1.2875403406659416},{-36.482442888053846,21.28754034066594},{-36.482442888053846,41.28754034066594},{-36.482442888053846,61.28754034066594},{-36.482442888053846,81.28754034066594},{-36.482442888053846,101.28754034066594},{-36.482442888053846,121.28754034066594},{-36.482442888053846,141.28754034066594},{-36.482442888053846,161.28754034066594},{-36.482442888053846,181.28754034066594},{-36.482442888053846,201.28754034066594},{-36.482442888053846,221.28754034066594},{-16.482442888053853,221.28754034066594},{3.5175571119461466,221.28754034066594},{3.5175571119461466,241.28754034066594},{23.517557111946147,241.28754034066594}},color={0,0,127}));
  connect(THeaWatSet_b3337893.y,heaInd_16e95443.TSetBuiSup)
    annotation (Line(points={{-27.6236789670561,-107.50395020506778},{-7.623678967056108,-107.50395020506778},{-7.623678967056108,-87.50395020506778},{-7.623678967056108,-67.50395020506778},{-7.623678967056108,-47.50395020506778},{-7.623678967056108,-27.50395020506778},{-7.623678967056108,-7.503950205067781},{-7.623678967056108,12.496049794932219},{-7.623678967056108,32.49604979493222},{-7.623678967056108,52.49604979493222},{-7.623678967056108,72.49604979493222},{-7.623678967056108,92.49604979493222},{-7.623678967056108,112.49604979493222},{-7.623678967056108,132.49604979493222},{-7.623678967056108,152.49604979493222},{-7.623678967056108,172.49604979493222},{-7.623678967056108,192.49604979493222},{-7.623678967056108,212.49604979493222},{-7.623678967056108,232.49604979493222},{12.376321032943892,232.49604979493222}},color={0,0,127}));

  //
  // End Connect Statements for b3337893
  //



  //
  // Begin Connect Statements for 2f68639d
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // heating indirect and network 2 pipe

  connect(disNet_eed2e036.ports_bCon[1],heaInd_16e95443.port_a1)
    annotation (Line(points={{-22.4036834949747,223.95760848958176},{-2.4036834949747004,223.95760848958176},{-2.4036834949747004,243.95760848958176},{17.5963165050253,243.95760848958176}},color={0,0,127}));
  connect(disNet_eed2e036.ports_aCon[1],heaInd_16e95443.port_b1)
    annotation (Line(points={{-13.284948538692447,224.93381437292675},{6.715051461307553,224.93381437292675},{6.715051461307553,244.93381437292675},{26.715051461307553,244.93381437292675}},color={0,0,127}));

  //
  // End Connect Statements for 2f68639d
  //



  //
  // Begin Connect Statements for 1a74b9df
  // Source template: /model_connectors/couplings/templates/TimeSeries_CoolingIndirect/ConnectStatements.mopt
  //

  // cooling indirect, timeseries coupling connections
  connect(TimeSerLoa_76c14bd6.ports_bChiWat[1], cooInd_5e057248.port_a2)
    annotation (Line(points={{58.78641673999434,144.0002466206602},{58.78641673999434,124.00024662066019},{38.78641673999434,124.00024662066019},{18.78641673999435,124.00024662066019}},color={0,0,127}));
  connect(cooInd_5e057248.port_b2,TimeSerLoa_76c14bd6.ports_aChiWat[1])
    annotation (Line(points={{15.740392048872124,133.16421487791587},{35.740392048872124,133.16421487791587},{35.740392048872124,153.16421487791587},{55.74039204887211,153.16421487791587}},color={0,0,127}));
  connect(pressure_source_1a74b9df.ports[1], cooInd_5e057248.port_b2)
    annotation (Line(points={{14.508463686491439,-95.31390851562361},{-5.491536313508561,-95.31390851562361},{-5.491536313508561,-75.31390851562361},{-5.491536313508561,-55.31390851562361},{-5.491536313508561,-35.31390851562361},{-5.491536313508561,-15.31390851562361},{-5.491536313508561,4.686091484376391},{-5.491536313508561,24.686091484376362},{-5.491536313508561,44.68609148437636},{-5.491536313508561,64.68609148437636},{-5.491536313508561,84.68609148437636},{-5.491536313508561,104.68609148437636},{-5.491536313508561,124.68609148437636},{14.508463686491439,124.68609148437636}},color={0,0,127}));
  connect(TChiWatSet_1a74b9df.y,cooInd_5e057248.TSetBuiSup)
    annotation (Line(points={{56.91327100838123,-101.65663850467382},{36.91327100838123,-101.65663850467382},{36.91327100838123,-81.65663850467382},{36.91327100838123,-61.65663850467382},{36.91327100838123,-41.65663850467382},{36.91327100838123,-21.656638504673822},{36.91327100838123,-1.656638504673822},{36.91327100838123,18.34336149532615},{36.91327100838123,38.34336149532615},{36.91327100838123,58.34336149532615},{36.91327100838123,78.34336149532615},{36.91327100838123,98.34336149532615},{36.91327100838123,118.34336149532615},{36.91327100838123,138.34336149532615},{36.91327100838123,158.34336149532615},{56.91327100838123,158.34336149532615}},color={0,0,127}));

  //
  // End Connect Statements for 1a74b9df
  //



  //
  // Begin Connect Statements for 67792418
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // cooling indirect and network 2 pipe

  connect(disNet_0659f6eb.ports_bCon[2],cooInd_5e057248.port_a1)
    annotation (Line(points={{-27.203943117501076,219.76165765850496},{-7.203943117501069,219.76165765850496},{-7.203943117501069,199.76165765850496},{-7.203943117501069,179.76165765850496},{-7.203943117501069,159.76165765850496},{-7.203943117501069,139.76165765850496},{-7.203943117501069,119.76165765850496},{12.796056882498931,119.76165765850496}},color={0,0,127}));
  connect(disNet_0659f6eb.ports_aCon[2],cooInd_5e057248.port_b1)
    annotation (Line(points={{-24.244725656454193,224.35534247452654},{-4.244725656454193,224.35534247452654},{-4.244725656454193,204.35534247452654},{-4.244725656454193,184.35534247452654},{-4.244725656454193,164.35534247452654},{-4.244725656454193,144.35534247452654},{-4.244725656454193,124.35534247452654},{15.755274343545807,124.35534247452654}},color={0,0,127}));

  //
  // End Connect Statements for 67792418
  //



  //
  // Begin Connect Statements for a1ec1627
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ConnectStatements.mopt
  //

  // cooling indirect, timeseries coupling connections
  connect(TimeSerLoa_76c14bd6.ports_bHeaWat[1], heaInd_a5bcccb6.port_a2)
    annotation (Line(points={{38.29268956108868,168.52923814412313},{18.29268956108868,168.52923814412313}},color={0,0,127}));
  connect(heaInd_a5bcccb6.port_b2,TimeSerLoa_76c14bd6.ports_aHeaWat[1])
    annotation (Line(points={{37.44528703115846,152.54626623800704},{57.44528703115844,152.54626623800704}},color={0,0,127}));
  connect(pressure_source_a1ec1627.ports[1], heaInd_a5bcccb6.port_b2)
    annotation (Line(points={{-59.16843478002659,-148.64940954675728},{-39.16843478002659,-148.64940954675728},{-39.16843478002659,-128.64940954675728},{-39.16843478002659,-108.64940954675728},{-39.16843478002659,-88.64940954675728},{-39.16843478002659,-68.64940954675728},{-39.16843478002659,-48.64940954675728},{-39.16843478002659,-28.649409546757283},{-39.16843478002659,-8.649409546757283},{-39.16843478002659,11.350590453242717},{-39.16843478002659,31.350590453242717},{-39.16843478002659,51.35059045324272},{-39.16843478002659,71.35059045324272},{-39.16843478002659,91.35059045324272},{-39.16843478002659,111.35059045324272},{-39.16843478002659,131.35059045324272},{-39.16843478002659,151.35059045324272},{-19.168434780026587,151.35059045324272},{0.8315652199734132,151.35059045324272},{20.831565219973413,151.35059045324272}},color={0,0,127}));
  connect(THeaWatSet_a1ec1627.y,heaInd_a5bcccb6.TSetBuiSup)
    annotation (Line(points={{-12.508305105031752,-147.63895556301674},{7.491694894968248,-147.63895556301674},{7.491694894968248,-127.63895556301674},{7.491694894968248,-107.63895556301674},{7.491694894968248,-87.63895556301674},{7.491694894968248,-67.63895556301674},{7.491694894968248,-47.63895556301674},{7.491694894968248,-27.638955563016737},{7.491694894968248,-7.6389555630167365},{7.491694894968248,12.361044436983263},{7.491694894968248,32.36104443698326},{7.491694894968248,52.36104443698326},{7.491694894968248,72.36104443698326},{7.491694894968248,92.36104443698326},{7.491694894968248,112.36104443698326},{7.491694894968248,132.36104443698326},{7.491694894968248,152.36104443698326},{27.491694894968248,152.36104443698326}},color={0,0,127}));

  //
  // End Connect Statements for a1ec1627
  //



  //
  // Begin Connect Statements for 4019d966
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // heating indirect and network 2 pipe

  connect(disNet_eed2e036.ports_bCon[2],heaInd_a5bcccb6.port_a1)
    annotation (Line(points={{-11.407840388933607,177.08157859835458},{-11.407840388933607,157.08157859835458},{8.592159611066393,157.08157859835458},{28.592159611066393,157.08157859835458}},color={0,0,127}));
  connect(disNet_eed2e036.ports_aCon[2],heaInd_a5bcccb6.port_b1)
    annotation (Line(points={{-13.010001683924443,177.13097269174307},{-13.010001683924443,157.13097269174307},{6.989998316075557,157.13097269174307},{26.989998316075557,157.13097269174307}},color={0,0,127}));

  //
  // End Connect Statements for 4019d966
  //



  //
  // Begin Connect Statements for 0071de0f
  // Source template: /model_connectors/couplings/templates/TimeSeries_CoolingIndirect/ConnectStatements.mopt
  //

  // cooling indirect, timeseries coupling connections
  connect(TimeSerLoa_baaf0022.ports_bChiWat[1], cooInd_a58fc75a.port_a2)
    annotation (Line(points={{61.72282629293943,69.29415211143123},{61.72282629293943,49.29415211143123},{41.72282629293943,49.29415211143123},{21.722826292939445,49.29415211143123}},color={0,0,127}));
  connect(cooInd_a58fc75a.port_b2,TimeSerLoa_baaf0022.ports_aChiWat[1])
    annotation (Line(points={{28.27999556036437,52.6170350624526},{48.27999556036437,52.6170350624526},{48.27999556036437,72.6170350624526},{68.27999556036437,72.6170350624526}},color={0,0,127}));
  connect(pressure_source_0071de0f.ports[1], cooInd_a58fc75a.port_b2)
    annotation (Line(points={{23.110859508806755,-137.24212469032227},{3.1108595088067545,-137.24212469032227},{3.1108595088067545,-117.24212469032227},{3.1108595088067545,-97.24212469032227},{3.1108595088067545,-77.24212469032227},{3.1108595088067545,-57.24212469032227},{3.1108595088067545,-37.24212469032227},{3.1108595088067545,-17.24212469032227},{3.1108595088067545,2.757875309677729},{3.1108595088067545,22.757875309677758},{3.1108595088067545,42.75787530967776},{23.110859508806755,42.75787530967776}},color={0,0,127}));
  connect(TChiWatSet_0071de0f.y,cooInd_a58fc75a.TSetBuiSup)
    annotation (Line(points={{63.81628658904751,-134.52016177549348},{43.81628658904751,-134.52016177549348},{43.81628658904751,-114.52016177549348},{43.81628658904751,-94.52016177549348},{43.81628658904751,-74.52016177549348},{43.81628658904751,-54.52016177549348},{43.81628658904751,-34.52016177549348},{43.81628658904751,-14.520161775493477},{43.81628658904751,5.479838224506523},{43.81628658904751,25.479838224506494},{43.81628658904751,45.479838224506494},{43.81628658904751,65.4798382245065},{43.81628658904751,85.4798382245065},{63.81628658904751,85.4798382245065}},color={0,0,127}));

  //
  // End Connect Statements for 0071de0f
  //



  //
  // Begin Connect Statements for 45305f18
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // cooling indirect and network 2 pipe

  connect(disNet_0659f6eb.ports_bCon[3],cooInd_a58fc75a.port_a1)
    annotation (Line(points={{-15.39597663404956,228.17217712101382},{4.6040233659504395,228.17217712101382},{4.6040233659504395,208.17217712101382},{4.6040233659504395,188.17217712101382},{4.6040233659504395,168.17217712101382},{4.6040233659504395,148.17217712101382},{4.6040233659504395,128.17217712101382},{4.6040233659504395,108.17217712101382},{4.6040233659504395,88.17217712101382},{4.6040233659504395,68.17217712101382},{4.6040233659504395,48.17217712101382},{24.60402336595044,48.17217712101382}},color={0,0,127}));
  connect(disNet_0659f6eb.ports_aCon[3],cooInd_a58fc75a.port_b1)
    annotation (Line(points={{-28.23260531663712,210.4582663171451},{-8.23260531663712,210.4582663171451},{-8.23260531663712,190.4582663171451},{-8.23260531663712,170.4582663171451},{-8.23260531663712,150.4582663171451},{-8.23260531663712,130.45826631714513},{-8.23260531663712,110.45826631714513},{-8.23260531663712,90.45826631714513},{-8.23260531663712,70.45826631714513},{-8.23260531663712,50.45826631714513},{-8.23260531663712,30.45826631714513},{11.76739468336288,30.45826631714513}},color={0,0,127}));

  //
  // End Connect Statements for 45305f18
  //



  //
  // Begin Connect Statements for f8c646c1
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ConnectStatements.mopt
  //

  // cooling indirect, timeseries coupling connections
  connect(TimeSerLoa_baaf0022.ports_bHeaWat[1], heaInd_9b2854d7.port_a2)
    annotation (Line(points={{31.35154258338983,74.14319109571531},{11.35154258338983,74.14319109571531}},color={0,0,127}));
  connect(heaInd_9b2854d7.port_b2,TimeSerLoa_baaf0022.ports_aHeaWat[1])
    annotation (Line(points={{31.467773552063733,87.34827822385273},{51.46777355206373,87.34827822385273}},color={0,0,127}));
  connect(pressure_source_f8c646c1.ports[1], heaInd_9b2854d7.port_b2)
    annotation (Line(points={{-53.976478018689704,-185.46912476410512},{-33.976478018689704,-185.46912476410512},{-33.976478018689704,-165.46912476410512},{-33.976478018689704,-145.46912476410512},{-33.976478018689704,-125.46912476410512},{-33.976478018689704,-105.46912476410512},{-33.976478018689704,-85.46912476410512},{-33.976478018689704,-65.46912476410512},{-33.976478018689704,-45.46912476410512},{-33.976478018689704,-25.469124764105118},{-33.976478018689704,-5.469124764105118},{-33.976478018689704,14.530875235894854},{-33.976478018689704,34.530875235894854},{-33.976478018689704,54.530875235894854},{-33.976478018689704,74.53087523589485},{-13.976478018689704,74.53087523589485},{6.023521981310296,74.53087523589485},{26.023521981310296,74.53087523589485}},color={0,0,127}));
  connect(THeaWatSet_f8c646c1.y,heaInd_9b2854d7.TSetBuiSup)
    annotation (Line(points={{-16.23920484318596,-183.2486065407216},{3.7607951568140408,-183.2486065407216},{3.7607951568140408,-163.2486065407216},{3.7607951568140408,-143.2486065407216},{3.7607951568140408,-123.2486065407216},{3.7607951568140408,-103.2486065407216},{3.7607951568140408,-83.2486065407216},{3.7607951568140408,-63.248606540721596},{3.7607951568140408,-43.248606540721596},{3.7607951568140408,-23.248606540721596},{3.7607951568140408,-3.248606540721596},{3.7607951568140408,16.751393459278404},{3.7607951568140408,36.751393459278404},{3.7607951568140408,56.751393459278404},{3.7607951568140408,76.7513934592784},{23.76079515681404,76.7513934592784}},color={0,0,127}));

  //
  // End Connect Statements for f8c646c1
  //



  //
  // Begin Connect Statements for 9b13e991
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // heating indirect and network 2 pipe

  connect(disNet_eed2e036.ports_bCon[3],heaInd_9b2854d7.port_a1)
    annotation (Line(points={{-20.18780361472227,175.51863907507695},{-20.18780361472227,155.51863907507695},{-20.18780361472227,135.51863907507695},{-20.18780361472227,115.51863907507695},{-20.18780361472227,95.51863907507695},{-20.18780361472227,75.51863907507695},{-0.18780361472227014,75.51863907507695},{19.81219638527773,75.51863907507695}},color={0,0,127}));
  connect(disNet_eed2e036.ports_aCon[3],heaInd_9b2854d7.port_b1)
    annotation (Line(points={{-27.049108742834953,188.4896329737347},{-27.049108742834953,168.4896329737347},{-27.049108742834953,148.4896329737347},{-27.049108742834953,128.4896329737347},{-27.049108742834953,108.4896329737347},{-27.049108742834953,88.4896329737347},{-7.04910874283496,88.4896329737347},{12.95089125716504,88.4896329737347}},color={0,0,127}));

  //
  // End Connect Statements for 9b13e991
  //



  //
  // Begin Connect Statements for 18c3f8dd
  // Source template: /model_connectors/couplings/templates/TimeSeries_CoolingIndirect/ConnectStatements.mopt
  //

  // cooling indirect, timeseries coupling connections
  connect(TimeSerLoa_78820bfd.ports_bChiWat[1], cooInd_d0c8c34f.port_a2)
    annotation (Line(points={{52.17107296182303,-14.528108131108638},{52.17107296182303,-34.52810813110864},{32.17107296182304,-34.52810813110864},{12.171072961823043,-34.52810813110864}},color={0,0,127}));
  connect(cooInd_d0c8c34f.port_b2,TimeSerLoa_78820bfd.ports_aChiWat[1])
    annotation (Line(points={{24.370663617124876,-23.721463550609087},{44.370663617124876,-23.721463550609087},{44.370663617124876,-3.721463550609087},{64.37066361712488,-3.721463550609087}},color={0,0,127}));
  connect(pressure_source_18c3f8dd.ports[1], cooInd_d0c8c34f.port_b2)
    annotation (Line(points={{14.712329191067482,-179.873657352625},{-5.287670808932518,-179.873657352625},{-5.287670808932518,-159.873657352625},{-5.287670808932518,-139.873657352625},{-5.287670808932518,-119.873657352625},{-5.287670808932518,-99.873657352625},{-5.287670808932518,-79.873657352625},{-5.287670808932518,-59.873657352625},{-5.287670808932518,-39.873657352625},{14.712329191067482,-39.873657352625}},color={0,0,127}));
  connect(TChiWatSet_18c3f8dd.y,cooInd_d0c8c34f.TSetBuiSup)
    annotation (Line(points={{60.463229124196005,-178.2395030119107},{40.463229124196005,-178.2395030119107},{40.463229124196005,-158.2395030119107},{40.463229124196005,-138.2395030119107},{40.463229124196005,-118.2395030119107},{40.463229124196005,-98.2395030119107},{40.463229124196005,-78.2395030119107},{40.463229124196005,-58.2395030119107},{40.463229124196005,-38.2395030119107},{40.463229124196005,-18.2395030119107},{40.463229124196005,1.7604969880893009},{60.463229124196005,1.7604969880893009}},color={0,0,127}));

  //
  // End Connect Statements for 18c3f8dd
  //



  //
  // Begin Connect Statements for 67703b4b
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // cooling indirect and network 2 pipe

  connect(disNet_0659f6eb.ports_bCon[4],cooInd_d0c8c34f.port_a1)
    annotation (Line(points={{-19.807299931417205,215.15648257984026},{0.19270006858279487,215.15648257984026},{0.19270006858279487,195.15648257984026},{0.19270006858279487,175.15648257984026},{0.19270006858279487,155.15648257984026},{0.19270006858279487,135.15648257984026},{0.19270006858279487,115.15648257984026},{0.19270006858279487,95.15648257984026},{0.19270006858279487,75.15648257984026},{0.19270006858279487,55.15648257984026},{0.19270006858279487,35.15648257984026},{0.19270006858279487,15.156482579840258},{0.19270006858279487,-4.843517420159742},{0.19270006858279487,-24.843517420159742},{0.19270006858279487,-44.84351742015974},{20.192700068582795,-44.84351742015974}},color={0,0,127}));
  connect(disNet_0659f6eb.ports_aCon[4],cooInd_d0c8c34f.port_b1)
    annotation (Line(points={{-12.575838677028997,211.18854500695255},{7.424161322971003,211.18854500695255},{7.424161322971003,191.18854500695255},{7.424161322971003,171.18854500695255},{7.424161322971003,151.18854500695255},{7.424161322971003,131.18854500695255},{7.424161322971003,111.18854500695255},{7.424161322971003,91.18854500695255},{7.424161322971003,71.18854500695255},{7.424161322971003,51.18854500695255},{7.424161322971003,31.188545006952552},{7.424161322971003,11.188545006952552},{7.424161322971003,-8.811454993047448},{7.424161322971003,-28.811454993047448},{7.424161322971003,-48.81145499304745},{27.424161322971003,-48.81145499304745}},color={0,0,127}));

  //
  // End Connect Statements for 67703b4b
  //



  //
  // Begin Connect Statements for 99235804
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ConnectStatements.mopt
  //

  // cooling indirect, timeseries coupling connections
  connect(TimeSerLoa_78820bfd.ports_bHeaWat[1], heaInd_dda3250a.port_a2)
    annotation (Line(points={{40.92134050377339,2.0549601395265427},{20.921340503773393,2.0549601395265427}},color={0,0,127}));
  connect(heaInd_dda3250a.port_b2,TimeSerLoa_78820bfd.ports_aHeaWat[1])
    annotation (Line(points={{37.991301236146796,0.1530719694015943},{57.991301236146796,0.1530719694015943}},color={0,0,127}));
  connect(pressure_source_99235804.ports[1], heaInd_dda3250a.port_b2)
    annotation (Line(points={{-52.17682159194053,-219.84724075460014},{-32.17682159194053,-219.84724075460014},{-32.17682159194053,-199.84724075460014},{-32.17682159194053,-179.84724075460014},{-32.17682159194053,-159.84724075460014},{-32.17682159194053,-139.84724075460014},{-32.17682159194053,-119.84724075460014},{-32.17682159194053,-99.84724075460014},{-32.17682159194053,-79.84724075460014},{-32.17682159194053,-59.847240754600136},{-32.17682159194053,-39.847240754600136},{-32.17682159194053,-19.847240754600136},{-32.17682159194053,0.15275924539986363},{-12.176821591940524,0.15275924539986363},{7.823178408059476,0.15275924539986363},{27.823178408059476,0.15275924539986363}},color={0,0,127}));
  connect(THeaWatSet_99235804.y,heaInd_dda3250a.TSetBuiSup)
    annotation (Line(points={{-20.851050605290084,-212.3810174295187},{-0.8510506052900837,-212.3810174295187},{-0.8510506052900837,-192.3810174295187},{-0.8510506052900837,-172.3810174295187},{-0.8510506052900837,-152.3810174295187},{-0.8510506052900837,-132.3810174295187},{-0.8510506052900837,-112.38101742951869},{-0.8510506052900837,-92.38101742951869},{-0.8510506052900837,-72.38101742951869},{-0.8510506052900837,-52.38101742951869},{-0.8510506052900837,-32.38101742951869},{-0.8510506052900837,-12.381017429518693},{-0.8510506052900837,7.6189825704813074},{19.148949394709916,7.6189825704813074}},color={0,0,127}));

  //
  // End Connect Statements for 99235804
  //



  //
  // Begin Connect Statements for 7b5c02ea
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // heating indirect and network 2 pipe

  connect(disNet_eed2e036.ports_bCon[4],heaInd_dda3250a.port_a1)
    annotation (Line(points={{-10.955968529152187,175.37737041395906},{-10.955968529152187,155.37737041395906},{-10.955968529152187,135.37737041395906},{-10.955968529152187,115.37737041395906},{-10.955968529152187,95.37737041395906},{-10.955968529152187,75.37737041395906},{-10.955968529152187,55.377370413959056},{-10.955968529152187,35.377370413959056},{-10.955968529152187,15.377370413959056},{-10.955968529152187,-4.622629586040944},{9.044031470847813,-4.622629586040944},{29.044031470847813,-4.622629586040944}},color={0,0,127}));
  connect(disNet_eed2e036.ports_aCon[4],heaInd_dda3250a.port_b1)
    annotation (Line(points={{-20.029721996267767,189.7158408205746},{-20.029721996267767,169.7158408205746},{-20.029721996267767,149.7158408205746},{-20.029721996267767,129.7158408205746},{-20.029721996267767,109.71584082057461},{-20.029721996267767,89.71584082057461},{-20.029721996267767,69.71584082057461},{-20.029721996267767,49.71584082057461},{-20.029721996267767,29.715840820574613},{-20.029721996267767,9.715840820574613},{-0.02972199626776728,9.715840820574613},{19.970278003732233,9.715840820574613}},color={0,0,127}));

  //
  // End Connect Statements for 7b5c02ea
  //




annotation(
  experiment(
    StopTime=86400,
    Interval=3600,
    Tolerance=1e-06),
  Diagram(
    coordinateSystem(
      preserveAspectRatio=false,
      extent={{-90.0,-270.0},{90.0,270.0}})),
  Documentation(
    revisions="<html>
 <li>
 May 10, 2020: Hagar Elarga<br/>
Updated implementation to handle template needed for GeoJSON to Modelica.
</li>
</html>"));
end DistrictEnergySystem;
