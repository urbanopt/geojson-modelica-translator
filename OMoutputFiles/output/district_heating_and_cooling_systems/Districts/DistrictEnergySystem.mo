within district_heating_and_cooling_systems.Districts;
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
  // Begin Model Instance for disNet_fbbfd6aa
  // Source template: /model_connectors/networks/templates/Network2Pipe_Instance.mopt
  //
parameter Integer nBui_disNet_fbbfd6aa=2;
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_disNet_fbbfd6aa=sum({
    cooInd_64f9e9cf.mDis_flow_nominal,
  cooInd_17448693.mDis_flow_nominal})
    "Nominal mass flow rate of the distribution pump";
  parameter Modelica.Units.SI.MassFlowRate mCon_flow_nominal_disNet_fbbfd6aa[nBui_disNet_fbbfd6aa]={
    cooInd_64f9e9cf.mDis_flow_nominal,
  cooInd_17448693.mDis_flow_nominal}
    "Nominal mass flow rate in each connection line";
  parameter Modelica.Units.SI.PressureDifference dpDis_nominal_disNet_fbbfd6aa[nBui_disNet_fbbfd6aa](
    each min=0,
    each displayUnit="Pa")=1/2 .* cat(
    1,
    {dp_nominal_disNet_fbbfd6aa*0.1},
    fill(
      dp_nominal_disNet_fbbfd6aa*0.9/(nBui_disNet_fbbfd6aa-1),
      nBui_disNet_fbbfd6aa-1))
    "Pressure drop between each connected building at nominal conditions (supply line)";
  parameter Modelica.Units.SI.PressureDifference dp_nominal_disNet_fbbfd6aa=dpSetPoi_disNet_fbbfd6aa+nBui_disNet_fbbfd6aa*7000
    "District network pressure drop";
  // NOTE: this differential pressure setpoint is currently utilized by plants elsewhere
  parameter Modelica.Units.SI.Pressure dpSetPoi_disNet_fbbfd6aa=50000
    "Differential pressure setpoint";

  Buildings.Experimental.DHC.Networks.Distribution2Pipe disNet_fbbfd6aa(
    redeclare final package Medium=MediumW,
    final nCon=nBui_disNet_fbbfd6aa,
    iConDpSen=nBui_disNet_fbbfd6aa,
    final mDis_flow_nominal=mDis_flow_nominal_disNet_fbbfd6aa,
    final mCon_flow_nominal=mCon_flow_nominal_disNet_fbbfd6aa,
    final allowFlowReversal=true,
    dpDis_nominal=dpDis_nominal_disNet_fbbfd6aa)
    "Distribution network."
    annotation (Placement(transformation(extent={{-30.0,120.0},{-10.0,130.0}})));
  //
  // End Model Instance for disNet_fbbfd6aa
  //


  
  //
  // Begin Model Instance for cooPla_b9d0bc6b
  // Source template: /model_connectors/plants/templates/CoolingPlant_Instance.mopt
  //
 // parameter Modelica.Units.SI.MassFlowRate mCHW_flow_nominal_cooPla_b9d0bc6b=cooPla_b9d0bc6b.numChi*(cooPla_b9d0bc6b.perChi.mEva_flow_nominal)
   parameter Modelica.Units.SI.MassFlowRate mCHW_flow_nominal_cooPla_b9d0bc6b=2*(180)
    "Nominal chilled water mass flow rate";
  parameter Modelica.Units.SI.MassFlowRate mCW_flow_nominal_cooPla_b9d0bc6b=cooPla_b9d0bc6b.perChi.mCon_flow_nominal
    "Nominal condenser water mass flow rate";
  parameter Modelica.Units.SI.PressureDifference dpCHW_nominal_cooPla_b9d0bc6b=44.8*1000
    "Nominal chilled water side pressure";
  parameter Modelica.Units.SI.PressureDifference dpCW_nominal_cooPla_b9d0bc6b=46.2*1000
    "Nominal condenser water side pressure";
  parameter Modelica.Units.SI.Power QEva_nominal_cooPla_b9d0bc6b=mCHW_flow_nominal_cooPla_b9d0bc6b*4200*(5-14)
    "Nominal cooling capaciaty (Negative means cooling)";
  parameter Modelica.Units.SI.MassFlowRate mMin_flow_cooPla_b9d0bc6b=0.2*mCHW_flow_nominal_cooPla_b9d0bc6b/cooPla_b9d0bc6b.numChi
    "Minimum mass flow rate of single chiller";
  // control settings
  parameter Modelica.Units.SI.Pressure dpSetPoi_cooPla_b9d0bc6b=70000
    "Differential pressure setpoint";
  parameter Modelica.Units.SI.Pressure pumDP_cooPla_b9d0bc6b=dpCHW_nominal_cooPla_b9d0bc6b+dpSetPoi_cooPla_b9d0bc6b+200000;
  parameter Modelica.Units.SI.Time tWai_cooPla_b9d0bc6b=30
    "Waiting time";
  // pumps
  parameter Buildings.Fluid.Movers.Data.Generic perCHWPum_cooPla_b9d0bc6b(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
     // V_flow=((mCHW_flow_nominal_cooPla_b9d0bc6b/cooPla_b9d0bc6b.numChi)/1000)*{0.1,1,1.2},
       V_flow=((mCHW_flow_nominal_cooPla_b9d0bc6b/2)/1000)*{0.1,1,1.2},
      dp=pumDP_cooPla_b9d0bc6b*{1.2,1,0.1}))
    "Performance data for chilled water pumps";
  parameter Buildings.Fluid.Movers.Data.Generic perCWPum_cooPla_b9d0bc6b(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=mCW_flow_nominal_cooPla_b9d0bc6b/1000*{0.2,0.6,1.0,1.2},
      dp=(dpCW_nominal_cooPla_b9d0bc6b+60000+6000)*{1.2,1.1,1.0,0.6}))
    "Performance data for condenser water pumps";


  Modelica.Blocks.Sources.RealExpression TSetChiWatDis_cooPla_b9d0bc6b(
    y=5+273.15)
    "Chilled water supply temperature set point on district level."
    annotation (Placement(transformation(extent={{10.0,-130.0},{30.0,-110.0}})));
  Modelica.Blocks.Sources.BooleanConstant on_cooPla_b9d0bc6b
    "On signal of the plant"
    annotation (Placement(transformation(extent={{50.0,-130.0},{70.0,-110.0}})));

  district_heating_and_cooling_systems.Plants.CentralCoolingPlant cooPla_b9d0bc6b(
    redeclare Buildings.Fluid.Chillers.Data.ElectricEIR.ElectricEIRChiller_Carrier_19EX_5208kW_6_88COP_Vanes perChi,
    perCHWPum=perCHWPum_cooPla_b9d0bc6b,
    perCWPum=perCWPum_cooPla_b9d0bc6b,
    mCHW_flow_nominal=mCHW_flow_nominal_cooPla_b9d0bc6b,
    dpCHW_nominal=dpCHW_nominal_cooPla_b9d0bc6b,
    QEva_nominal=QEva_nominal_cooPla_b9d0bc6b,
    mMin_flow=mMin_flow_cooPla_b9d0bc6b,
    mCW_flow_nominal=mCW_flow_nominal_cooPla_b9d0bc6b,
    dpCW_nominal=dpCW_nominal_cooPla_b9d0bc6b,
    TAirInWB_nominal=298.7,
    TCW_nominal=308.15,
    TMin=288.15,
    tWai=tWai_cooPla_b9d0bc6b,
    dpSetPoi=dpSetPoi_cooPla_b9d0bc6b
    )
    "District cooling plant."
    annotation (Placement(transformation(extent={{-70.0,110.0},{-50.0,130.0}})));
  //
  // End Model Instance for cooPla_b9d0bc6b
  //


  
  //
  // Begin Model Instance for disNet_16bb913e
  // Source template: /model_connectors/networks/templates/Network2Pipe_Instance.mopt
  //
parameter Integer nBui_disNet_16bb913e=2;
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_disNet_16bb913e=sum({
    heaInd_9e07b389.mDis_flow_nominal,
  heaInd_9562514f.mDis_flow_nominal})
    "Nominal mass flow rate of the distribution pump";
  parameter Modelica.Units.SI.MassFlowRate mCon_flow_nominal_disNet_16bb913e[nBui_disNet_16bb913e]={
    heaInd_9e07b389.mDis_flow_nominal,
  heaInd_9562514f.mDis_flow_nominal}
    "Nominal mass flow rate in each connection line";
  parameter Modelica.Units.SI.PressureDifference dpDis_nominal_disNet_16bb913e[nBui_disNet_16bb913e](
    each min=0,
    each displayUnit="Pa")=1/2 .* cat(
    1,
    {dp_nominal_disNet_16bb913e*0.1},
    fill(
      dp_nominal_disNet_16bb913e*0.9/(nBui_disNet_16bb913e-1),
      nBui_disNet_16bb913e-1))
    "Pressure drop between each connected building at nominal conditions (supply line)";
  parameter Modelica.Units.SI.PressureDifference dp_nominal_disNet_16bb913e=dpSetPoi_disNet_16bb913e+nBui_disNet_16bb913e*7000
    "District network pressure drop";
  // NOTE: this differential pressure setpoint is currently utilized by plants elsewhere
  parameter Modelica.Units.SI.Pressure dpSetPoi_disNet_16bb913e=50000
    "Differential pressure setpoint";

  Buildings.Experimental.DHC.Networks.Distribution2Pipe disNet_16bb913e(
    redeclare final package Medium=MediumW,
    final nCon=nBui_disNet_16bb913e,
    iConDpSen=nBui_disNet_16bb913e,
    final mDis_flow_nominal=mDis_flow_nominal_disNet_16bb913e,
    final mCon_flow_nominal=mCon_flow_nominal_disNet_16bb913e,
    final allowFlowReversal=true,
    dpDis_nominal=dpDis_nominal_disNet_16bb913e)
    "Distribution network."
    annotation (Placement(transformation(extent={{-30.0,80.0},{-10.0,90.0}})));
  //
  // End Model Instance for disNet_16bb913e
  //


  
  //
  // Begin Model Instance for heaPlab5a32a5d
  // Source template: /model_connectors/plants/templates/HeatingPlant_Instance.mopt
  //
  // heating plant instance
  parameter Modelica.Units.SI.MassFlowRate mHW_flow_nominal_heaPlab5a32a5d=mBoi_flow_nominal_heaPlab5a32a5d*heaPlab5a32a5d.numBoi
    "Nominal heating water mass flow rate";
  parameter Modelica.Units.SI.MassFlowRate mBoi_flow_nominal_heaPlab5a32a5d=QBoi_nominal_heaPlab5a32a5d/(4200*heaPlab5a32a5d.delT_nominal)
    "Nominal heating water mass flow rate";
  parameter Modelica.Units.SI.Power QBoi_nominal_heaPlab5a32a5d=Q_flow_nominal_heaPlab5a32a5d/heaPlab5a32a5d.numBoi
    "Nominal heating capaciaty";
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_heaPlab5a32a5d=1000000*2
    "Heating load";
  parameter Modelica.Units.SI.MassFlowRate mMin_flow_heaPlab5a32a5d=0.2*mBoi_flow_nominal_heaPlab5a32a5d
    "Minimum mass flow rate of single boiler";
  // controls
  parameter Modelica.Units.SI.Pressure pumDP=(heaPlab5a32a5d.dpBoi_nominal+dpSetPoi_disNet_16bb913e+50000)
    "Heating water pump pressure drop";
  parameter Modelica.Units.SI.Time tWai_heaPlab5a32a5d=30
    "Waiting time";
  parameter Buildings.Fluid.Movers.Data.Generic perHWPum_heaPlab5a32a5d(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=mBoi_flow_nominal_heaPlab5a32a5d/1000*{0.1,1.1},
      dp=pumDP*{1.1,0.1}))
    "Performance data for heating water pumps";

  district_heating_and_cooling_systems.Plants.CentralHeatingPlant heaPlab5a32a5d(
    perHWPum=perHWPum_heaPlab5a32a5d,
    mHW_flow_nominal=mHW_flow_nominal_heaPlab5a32a5d,
    QBoi_flow_nominal=QBoi_nominal_heaPlab5a32a5d,
    mMin_flow=mMin_flow_heaPlab5a32a5d,
    mBoi_flow_nominal=mBoi_flow_nominal_heaPlab5a32a5d,
    dpBoi_nominal=10000,
    delT_nominal(
      displayUnit="degC")=15,
    tWai=tWai_heaPlab5a32a5d,
    // TODO: we're currently grabbing dpSetPoi from the Network instance -- need feedback to determine if that's the proper "home" for it
    dpSetPoi=dpSetPoi_disNet_16bb913e
    )
    "District heating plant."
    annotation (Placement(transformation(extent={{-70.0,70.0},{-50.0,90.0}})));
  //
  // End Model Instance for heaPlab5a32a5d
  //


  
  //
  // Begin Model Instance for TimeSerLoa_dc1e9bbe
  // Source template: /model_connectors/load_connectors/templates/TimeSeries_Instance.mopt
  //
  // time series load
  district_heating_and_cooling_systems.Loads.B5a6b99ec37f4de7f94020090.TimeSeriesBuilding TimeSerLoa_dc1e9bbe(
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
    annotation (Placement(transformation(extent={{50.0,110.0},{70.0,130.0}})));
  //
  // End Model Instance for TimeSerLoa_dc1e9bbe
  //


  
  //
  // Begin Model Instance for cooInd_64f9e9cf
  // Source template: /model_connectors/energy_transfer_systems/templates/CoolingIndirect_Instance.mopt
  //
  // cooling indirect instance
  district_heating_and_cooling_systems.Substations.CoolingIndirect_5a6b99ec37f4de7f94020090 cooInd_64f9e9cf(
    redeclare package Medium=MediumW,
    allowFlowReversal1=true,
    allowFlowReversal2=true,
    mDis_flow_nominal=mDis_flow_nominal_9dc82118,
    mBui_flow_nominal=mBui_flow_nominal_9dc82118,
    dp1_nominal=500,
    dp2_nominal=500,
    dpValve_nominal=7000,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_9dc82118,
    // TODO: dehardcode the nominal temperatures?
    T_a1_nominal=273.15+5,
    T_a2_nominal=273.15+13)
    "Indirect cooling energy transfer station ETS."
    annotation (Placement(transformation(extent={{10.0,110.0},{30.0,130.0}})));
  //
  // End Model Instance for cooInd_64f9e9cf
  //


  
  //
  // Begin Model Instance for heaInd_9e07b389
  // Source template: /model_connectors/energy_transfer_systems/templates/HeatingIndirect_Instance.mopt
  //
  // heating indirect instance
  district_heating_and_cooling_systems.Substations.HeatingIndirect_5a6b99ec37f4de7f94020090 heaInd_9e07b389(
    allowFlowReversal1=true,
    allowFlowReversal2=true,
    show_T=true,
    redeclare package Medium=MediumW,
    mDis_flow_nominal=mDis_flow_nominal_34388ba6,
    mBui_flow_nominal=mBui_flow_nominal_34388ba6,
    dpValve_nominal=6000,
    dp1_nominal=500,
    dp2_nominal=500,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_34388ba6,
    T_a1_nominal=55+273.15,
    T_a2_nominal=35+273.15,
    k=0.1,
    Ti=60,
    reverseActing=true)
    annotation (Placement(transformation(extent={{10.0,70.0},{30.0,90.0}})));
  //
  // End Model Instance for heaInd_9e07b389
  //


  
  //
  // Begin Model Instance for TimeSerLoa_b0f547d0
  // Source template: /model_connectors/load_connectors/templates/TimeSeries_Instance.mopt
  //
  // time series load
  district_heating_and_cooling_systems.Loads.abcdefghijklmnopqrstuvwx.TimeSeriesBuilding TimeSerLoa_b0f547d0(
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
  // End Model Instance for TimeSerLoa_b0f547d0
  //


  
  //
  // Begin Model Instance for cooInd_17448693
  // Source template: /model_connectors/energy_transfer_systems/templates/CoolingIndirect_Instance.mopt
  //
  // cooling indirect instance
  district_heating_and_cooling_systems.Substations.CoolingIndirect_abcdefghijklmnopqrstuvwx cooInd_17448693(
    redeclare package Medium=MediumW,
    allowFlowReversal1=true,
    allowFlowReversal2=true,
    mDis_flow_nominal=mDis_flow_nominal_eb8b9dfb,
    mBui_flow_nominal=mBui_flow_nominal_eb8b9dfb,
    dp1_nominal=500,
    dp2_nominal=500,
    dpValve_nominal=7000,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_eb8b9dfb,
    // TODO: dehardcode the nominal temperatures?
    T_a1_nominal=273.15+5,
    T_a2_nominal=273.15+13)
    "Indirect cooling energy transfer station ETS."
    annotation (Placement(transformation(extent={{10.0,-10.0},{30.0,10.0}})));
  //
  // End Model Instance for cooInd_17448693
  //


  
  //
  // Begin Model Instance for heaInd_9562514f
  // Source template: /model_connectors/energy_transfer_systems/templates/HeatingIndirect_Instance.mopt
  //
  // heating indirect instance
  district_heating_and_cooling_systems.Substations.HeatingIndirect_abcdefghijklmnopqrstuvwx heaInd_9562514f(
    allowFlowReversal1=true,
    allowFlowReversal2=true,
    show_T=true,
    redeclare package Medium=MediumW,
    mDis_flow_nominal=mDis_flow_nominal_5127a512,
    mBui_flow_nominal=mBui_flow_nominal_5127a512,
    dpValve_nominal=6000,
    dp1_nominal=500,
    dp2_nominal=500,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_5127a512,
    T_a1_nominal=55+273.15,
    T_a2_nominal=35+273.15,
    k=0.1,
    Ti=60,
    reverseActing=true)
    annotation (Placement(transformation(extent={{10.0,30.0},{30.0,50.0}})));
  //
  // End Model Instance for heaInd_9562514f
  //


  

  // Model dependencies

  //
  // Begin Component Definitions for b182b7fa
  // Source template: /model_connectors/couplings/templates/Network2Pipe_CoolingPlant/ComponentDefinitions.mopt
  //
  // No components for pipe and cooling plant

  //
  // End Component Definitions for b182b7fa
  //



  //
  // Begin Component Definitions for a4881284
  // Source template: /model_connectors/couplings/templates/Network2Pipe_HeatingPlant/ComponentDefinitions.mopt
  //
  // TODO: This should not be here, it is entirely plant specific and should be moved elsewhere
  // but since it requires a connect statement we must put it here for now...
  Modelica.Blocks.Sources.BooleanConstant mPum_flow_a4881284(
    k=true)
    "Total heating water pump mass flow rate"
    annotation (Placement(transformation(extent={{-70.0,-50.0},{-50.0,-30.0}})));
  // TODO: This should not be here, it is entirely plant specific and should be moved elsewhere
  // but since it requires a connect statement we must put it here for now...
  Modelica.Blocks.Sources.RealExpression TDisSetHeaWat_a4881284(
    each y=273.15+68)
    "District side heating water supply temperature set point."
    annotation (Placement(transformation(extent={{-30.0,-50.0},{-10.0,-30.0}})));

  //
  // End Component Definitions for a4881284
  //



  //
  // Begin Component Definitions for 9dc82118
  // Source template: /model_connectors/couplings/templates/TimeSeries_CoolingIndirect/ComponentDefinitions.mopt
  //
  // TimeSeries + CoolingIndirect Component Definitions
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_9dc82118=TimeSerLoa_dc1e9bbe.mChiWat_flow_nominal*delChiWatTemBui/delChiWatTemDis
    "Nominal mass flow rate of primary (district) district cooling side";
  parameter Modelica.Units.SI.MassFlowRate mBui_flow_nominal_9dc82118=TimeSerLoa_dc1e9bbe.mChiWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district cooling side";
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_9dc82118=-1*(TimeSerLoa_dc1e9bbe.QCoo_flow_nominal);
  Modelica.Fluid.Sources.FixedBoundary pressure_source_9dc82118(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{10.0,-50.0},{30.0,-30.0}})));
  // TODO: move TChiWatSet (and its connection) into a CoolingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression TChiWatSet_9dc82118(
    y=7+273.15)
    //Dehardcode
    "Primary loop (district side) chilled water setpoint temperature."
    annotation (Placement(transformation(extent={{50.0,-50.0},{70.0,-30.0}})));

  //
  // End Component Definitions for 9dc82118
  //



  //
  // Begin Component Definitions for 6a76a04c
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for cooling indirect and network 2 pipe

  //
  // End Component Definitions for 6a76a04c
  //



  //
  // Begin Component Definitions for 34388ba6
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ComponentDefinitions.mopt
  //
  // TimeSeries + HeatingIndirect Component Definitions
  // TODO: the components below need to be fixed!
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_34388ba6=TimeSerLoa_dc1e9bbe.mHeaWat_flow_nominal*delHeaWatTemBui/delHeaWatTemDis
    "Nominal mass flow rate of primary (district) district heating side";
  parameter Modelica.Units.SI.MassFlowRate mBui_flow_nominal_34388ba6=TimeSerLoa_dc1e9bbe.mHeaWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district heating side";
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_34388ba6=(TimeSerLoa_dc1e9bbe.QHea_flow_nominal);
  Modelica.Fluid.Sources.FixedBoundary pressure_source_34388ba6(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{-70.0,-90.0},{-50.0,-70.0}})));
  // TODO: move THeaWatSet (and its connection) into a HeatingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression THeaWatSet_34388ba6(
    // y=40+273.15)
    y=273.15+40 )
    "Secondary loop (Building side) heating water setpoint temperature."
    //Dehardcode
    annotation (Placement(transformation(extent={{-30.0,-90.0},{-10.0,-70.0}})));

  //
  // End Component Definitions for 34388ba6
  //



  //
  // Begin Component Definitions for cd0ff70c
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for heating indirect and network 2 pipe

  //
  // End Component Definitions for cd0ff70c
  //



  //
  // Begin Component Definitions for eb8b9dfb
  // Source template: /model_connectors/couplings/templates/TimeSeries_CoolingIndirect/ComponentDefinitions.mopt
  //
  // TimeSeries + CoolingIndirect Component Definitions
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_eb8b9dfb=TimeSerLoa_b0f547d0.mChiWat_flow_nominal*delChiWatTemBui/delChiWatTemDis
    "Nominal mass flow rate of primary (district) district cooling side";
  parameter Modelica.Units.SI.MassFlowRate mBui_flow_nominal_eb8b9dfb=TimeSerLoa_b0f547d0.mChiWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district cooling side";
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_eb8b9dfb=-1*(TimeSerLoa_b0f547d0.QCoo_flow_nominal);
  Modelica.Fluid.Sources.FixedBoundary pressure_source_eb8b9dfb(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{10.0,-90.0},{30.0,-70.0}})));
  // TODO: move TChiWatSet (and its connection) into a CoolingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression TChiWatSet_eb8b9dfb(
    y=7+273.15)
    //Dehardcode
    "Primary loop (district side) chilled water setpoint temperature."
    annotation (Placement(transformation(extent={{50.0,-90.0},{70.0,-70.0}})));

  //
  // End Component Definitions for eb8b9dfb
  //



  //
  // Begin Component Definitions for 796a7284
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for cooling indirect and network 2 pipe

  //
  // End Component Definitions for 796a7284
  //



  //
  // Begin Component Definitions for 5127a512
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ComponentDefinitions.mopt
  //
  // TimeSeries + HeatingIndirect Component Definitions
  // TODO: the components below need to be fixed!
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_5127a512=TimeSerLoa_b0f547d0.mHeaWat_flow_nominal*delHeaWatTemBui/delHeaWatTemDis
    "Nominal mass flow rate of primary (district) district heating side";
  parameter Modelica.Units.SI.MassFlowRate mBui_flow_nominal_5127a512=TimeSerLoa_b0f547d0.mHeaWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district heating side";
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_5127a512=(TimeSerLoa_b0f547d0.QHea_flow_nominal);
  Modelica.Fluid.Sources.FixedBoundary pressure_source_5127a512(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{-70.0,-130.0},{-50.0,-110.0}})));
  // TODO: move THeaWatSet (and its connection) into a HeatingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression THeaWatSet_5127a512(
    // y=40+273.15)
    y=273.15+40 )
    "Secondary loop (Building side) heating water setpoint temperature."
    //Dehardcode
    annotation (Placement(transformation(extent={{-30.0,-130.0},{-10.0,-110.0}})));

  //
  // End Component Definitions for 5127a512
  //



  //
  // Begin Component Definitions for 5396de39
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for heating indirect and network 2 pipe

  //
  // End Component Definitions for 5396de39
  //



equation
  // Connections

  //
  // Begin Connect Statements for b182b7fa
  // Source template: /model_connectors/couplings/templates/Network2Pipe_CoolingPlant/ConnectStatements.mopt
  //

  // TODO: these connect statements shouldn't be here, they are plant specific
  // but since we can't currently make connect statements for single systems, this is what we've got
  connect(on_cooPla_b9d0bc6b.y,cooPla_b9d0bc6b.on)
    annotation (Line(points={{61.98528340335304,-92.87227506370309},{41.98528340335304,-92.87227506370309},{41.98528340335304,-72.87227506370309},{41.98528340335304,-52.872275063703086},{41.98528340335304,-32.872275063703086},{41.98528340335304,-12.872275063703086},{41.98528340335304,7.127724936296914},{41.98528340335304,27.127724936296914},{41.98528340335304,47.127724936296914},{41.98528340335304,67.12772493629691},{41.98528340335304,87.12772493629691},{41.98528340335304,107.12772493629691},{21.985283403353037,107.12772493629691},{1.985283403353037,107.12772493629691},{-18.014716596646963,107.12772493629691},{-38.014716596646956,107.12772493629691},{-38.014716596646956,127.12772493629691},{-58.014716596646956,127.12772493629691}},color={0,0,127}));
  connect(TSetChiWatDis_cooPla_b9d0bc6b.y,cooPla_b9d0bc6b.TCHWSupSet)
    annotation (Line(points={{15.586290035510416,-92.85268467250083},{-4.413709964489584,-92.85268467250083},{-4.413709964489584,-72.85268467250083},{-4.413709964489584,-52.85268467250083},{-4.413709964489584,-32.85268467250083},{-4.413709964489584,-12.852684672500828},{-4.413709964489584,7.147315327499172},{-4.413709964489584,27.14731532749917},{-4.413709964489584,47.14731532749917},{-4.413709964489584,67.14731532749917},{-4.413709964489584,87.14731532749917},{-4.413709964489584,107.14731532749917},{-24.413709964489584,107.14731532749917},{-44.413709964489584,107.14731532749917},{-44.413709964489584,127.14731532749917},{-64.41370996448958,127.14731532749917}},color={0,0,127}));

  connect(disNet_fbbfd6aa.port_bDisRet,cooPla_b9d0bc6b.port_a)
    annotation (Line(points={{-40.999926020580745,126.80024295641756},{-60.999926020580745,126.80024295641756}},color={0,0,127}));
  connect(cooPla_b9d0bc6b.port_b,disNet_fbbfd6aa.port_aDisSup)
    annotation (Line(points={{-38.86283796961099,123.59145086890575},{-18.862837969610993,123.59145086890575}},color={0,0,127}));
  connect(disNet_fbbfd6aa.dp,cooPla_b9d0bc6b.dpMea)
    annotation (Line(points={{-34.945966305991874,123.97263134444749},{-54.945966305991874,123.97263134444749}},color={0,0,127}));

  //
  // End Connect Statements for b182b7fa
  //



  //
  // Begin Connect Statements for a4881284
  // Source template: /model_connectors/couplings/templates/Network2Pipe_HeatingPlant/ConnectStatements.mopt
  //

  connect(heaPlab5a32a5d.port_a,disNet_16bb913e.port_bDisRet)
    annotation (Line(points={{-39.46592994692146,73.26750923751601},{-19.465929946921463,73.26750923751601}},color={0,0,127}));
  connect(disNet_16bb913e.dp,heaPlab5a32a5d.dpMea)
    annotation (Line(points={{-49.11852413681822,72.37079291515894},{-69.11852413681822,72.37079291515894}},color={0,0,127}));
  connect(heaPlab5a32a5d.port_b,disNet_16bb913e.port_aDisSup)
    annotation (Line(points={{-41.23655808319434,71.70259161945359},{-21.23655808319434,71.70259161945359}},color={0,0,127}));
  connect(mPum_flow_a4881284.y,heaPlab5a32a5d.on)
    annotation (Line(points={{-68.6279202568422,-15.682408500313159},{-68.6279202568422,4.317591499686841},{-68.6279202568422,24.31759149968684},{-68.6279202568422,44.31759149968684},{-68.6279202568422,64.31759149968684},{-68.6279202568422,84.31759149968684}},color={0,0,127}));
  connect(TDisSetHeaWat_a4881284.y,heaPlab5a32a5d.THeaSet)
    annotation (Line(points={{-27.122930528719777,-24.22312121221134},{-27.122930528719777,-4.223121212211339},{-27.122930528719777,15.776878787788661},{-27.122930528719777,35.77687878778865},{-27.122930528719777,55.77687878778865},{-47.12293052871978,55.77687878778865},{-47.12293052871978,75.77687878778865},{-67.12293052871978,75.77687878778865}},color={0,0,127}));

  //
  // End Connect Statements for a4881284
  //



  //
  // Begin Connect Statements for 9dc82118
  // Source template: /model_connectors/couplings/templates/TimeSeries_CoolingIndirect/ConnectStatements.mopt
  //

  // cooling indirect, timeseries coupling connections
  connect(TimeSerLoa_dc1e9bbe.ports_bChiWat[1], cooInd_64f9e9cf.port_a2)
    annotation (Line(points={{44.65253564266956,125.76394114239199},{24.652535642669562,125.76394114239199}},color={0,0,127}));
  connect(cooInd_64f9e9cf.port_b2,TimeSerLoa_dc1e9bbe.ports_aChiWat[1])
    annotation (Line(points={{35.2460943311861,116.18599807770367},{55.2460943311861,116.18599807770367}},color={0,0,127}));
  connect(pressure_source_9dc82118.ports[1], cooInd_64f9e9cf.port_b2)
    annotation (Line(points={{14.140559490167576,-24.589716719788072},{-5.8594405098324245,-24.589716719788072},{-5.8594405098324245,-4.589716719788072},{-5.8594405098324245,15.410283280211928},{-5.8594405098324245,35.41028328021193},{-5.8594405098324245,55.41028328021193},{-5.8594405098324245,75.41028328021193},{-5.8594405098324245,95.41028328021193},{-5.8594405098324245,115.41028328021193},{14.140559490167576,115.41028328021193}},color={0,0,127}));
  connect(TChiWatSet_9dc82118.y,cooInd_64f9e9cf.TSetBuiSup)
    annotation (Line(points={{56.1686256450449,-14.405919991222333},{56.1686256450449,5.5940800087776665},{56.1686256450449,25.594080008777667},{36.1686256450449,25.594080008777667},{36.1686256450449,45.59408000877767},{36.1686256450449,65.59408000877767},{36.1686256450449,85.59408000877767},{36.1686256450449,105.59408000877767},{36.1686256450449,125.59408000877767},{56.1686256450449,125.59408000877767}},color={0,0,127}));

  //
  // End Connect Statements for 9dc82118
  //



  //
  // Begin Connect Statements for 6a76a04c
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // cooling indirect and network 2 pipe
  
  connect(disNet_fbbfd6aa.ports_bCon[1],cooInd_64f9e9cf.port_a1)
    annotation (Line(points={{7.4185747562136015,120.21953850489571},{27.4185747562136,120.21953850489571}},color={0,0,127}));
  connect(disNet_fbbfd6aa.ports_aCon[1],cooInd_64f9e9cf.port_b1)
    annotation (Line(points={{-3.4404139959337954,113.61453443541257},{16.559586004066205,113.61453443541257}},color={0,0,127}));

  //
  // End Connect Statements for 6a76a04c
  //



  //
  // Begin Connect Statements for 34388ba6
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ConnectStatements.mopt
  //

  // heating indirect, timeseries coupling connections
  connect(TimeSerLoa_dc1e9bbe.ports_bHeaWat[1], heaInd_9e07b389.port_a2)
    annotation (Line(points={{53.942221711563406,103.2003495784007},{53.942221711563406,83.2003495784007},{33.94222171156339,83.2003495784007},{13.942221711563391,83.2003495784007}},color={0,0,127}));
  connect(heaInd_9e07b389.port_b2,TimeSerLoa_dc1e9bbe.ports_aHeaWat[1])
    annotation (Line(points={{17.759176605021864,94.6174851811741},{37.759176605021864,94.6174851811741},{37.759176605021864,114.6174851811741},{57.75917660502188,114.6174851811741}},color={0,0,127}));
  connect(pressure_source_34388ba6.ports[1], heaInd_9e07b389.port_b2)
    annotation (Line(points={{-64.06646423983993,-58.923134896445475},{-44.06646423983993,-58.923134896445475},{-44.06646423983993,-38.923134896445475},{-44.06646423983993,-18.923134896445475},{-44.06646423983993,1.0768651035545247},{-44.06646423983993,21.076865103554525},{-44.06646423983993,41.076865103554525},{-44.06646423983993,61.076865103554525},{-24.06646423983993,61.076865103554525},{-4.066464239839931,61.076865103554525},{-4.066464239839931,81.07686510355452},{15.93353576016007,81.07686510355452}},color={0,0,127}));
  connect(THeaWatSet_34388ba6.y,heaInd_9e07b389.TSetBuiSup)
    annotation (Line(points={{-15.56611859779072,-62.94104667520298},{4.4338814022092805,-62.94104667520298},{4.4338814022092805,-42.94104667520298},{4.4338814022092805,-22.941046675202983},{4.4338814022092805,-2.9410466752029834},{4.4338814022092805,17.058953324797017},{4.4338814022092805,37.05895332479703},{4.4338814022092805,57.05895332479703},{4.4338814022092805,77.05895332479703},{24.43388140220928,77.05895332479703}},color={0,0,127}));

  //
  // End Connect Statements for 34388ba6
  //



  //
  // Begin Connect Statements for cd0ff70c
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // heating indirect and network 2 pipe
  
  connect(disNet_16bb913e.ports_bCon[1],heaInd_9e07b389.port_a1)
    annotation (Line(points={{3.38557096037421,79.13058280144048},{23.38557096037421,79.13058280144048}},color={0,0,127}));
  connect(disNet_16bb913e.ports_aCon[1],heaInd_9e07b389.port_b1)
    annotation (Line(points={{4.5207426130711355,70.96595080440736},{24.520742613071135,70.96595080440736}},color={0,0,127}));

  //
  // End Connect Statements for cd0ff70c
  //



  //
  // Begin Connect Statements for eb8b9dfb
  // Source template: /model_connectors/couplings/templates/TimeSeries_CoolingIndirect/ConnectStatements.mopt
  //

  // cooling indirect, timeseries coupling connections
  connect(TimeSerLoa_b0f547d0.ports_bChiWat[1], cooInd_17448693.port_a2)
    annotation (Line(points={{63.54388052545144,29.969527392375383},{63.54388052545144,9.969527392375397},{43.54388052545144,9.969527392375397},{23.543880525451442,9.969527392375397}},color={0,0,127}));
  connect(cooInd_17448693.port_b2,TimeSerLoa_b0f547d0.ports_aChiWat[1])
    annotation (Line(points={{15.221589297525753,26.57720393516999},{35.22158929752575,26.57720393516999},{35.22158929752575,46.57720393516999},{55.22158929752575,46.57720393516999}},color={0,0,127}));
  connect(pressure_source_eb8b9dfb.ports[1], cooInd_17448693.port_b2)
    annotation (Line(points={{26.384149139070473,-57.87260460583036},{6.384149139070473,-57.87260460583036},{6.384149139070473,-37.87260460583036},{6.384149139070473,-17.87260460583036},{6.384149139070473,2.127395394169639},{26.384149139070473,2.127395394169639}},color={0,0,127}));
  connect(TChiWatSet_eb8b9dfb.y,cooInd_17448693.TSetBuiSup)
    annotation (Line(points={{59.3508454618366,-64.07489069629958},{39.3508454618366,-64.07489069629958},{39.3508454618366,-44.074890696299576},{39.3508454618366,-24.074890696299576},{39.3508454618366,-4.074890696299576},{39.3508454618366,15.925109303700424},{39.3508454618366,35.925109303700424},{59.3508454618366,35.925109303700424}},color={0,0,127}));

  //
  // End Connect Statements for eb8b9dfb
  //



  //
  // Begin Connect Statements for 796a7284
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // cooling indirect and network 2 pipe
  
  connect(disNet_fbbfd6aa.ports_bCon[2],cooInd_17448693.port_a1)
    annotation (Line(points={{-28.363310075607068,106.05826882114084},{-8.363310075607075,106.05826882114084},{-8.363310075607075,86.05826882114084},{-8.363310075607075,66.05826882114084},{-8.363310075607075,46.05826882114084},{-8.363310075607075,26.058268821140842},{-8.363310075607075,6.058268821140842},{11.636689924392925,6.058268821140842}},color={0,0,127}));
  connect(disNet_fbbfd6aa.ports_aCon[2],cooInd_17448693.port_b1)
    annotation (Line(points={{-22.58289076047106,103.39524105176336},{-2.5828907604710594,103.39524105176336},{-2.5828907604710594,83.39524105176336},{-2.5828907604710594,63.395241051763364},{-2.5828907604710594,43.395241051763364},{-2.5828907604710594,23.395241051763364},{-2.5828907604710594,3.3952410517633496},{17.41710923952894,3.3952410517633496}},color={0,0,127}));

  //
  // End Connect Statements for 796a7284
  //



  //
  // Begin Connect Statements for 5127a512
  // Source template: /model_connectors/couplings/templates/TimeSeries_HeatingIndirect/ConnectStatements.mopt
  //

  // heating indirect, timeseries coupling connections
  connect(TimeSerLoa_b0f547d0.ports_bHeaWat[1], heaInd_9562514f.port_a2)
    annotation (Line(points={{38.90577495984459,30.209932594421133},{18.905774959844592,30.209932594421133}},color={0,0,127}));
  connect(heaInd_9562514f.port_b2,TimeSerLoa_b0f547d0.ports_aHeaWat[1])
    annotation (Line(points={{49.319376265127545,35.528591015281364},{69.31937626512754,35.528591015281364}},color={0,0,127}));
  connect(pressure_source_5127a512.ports[1], heaInd_9562514f.port_b2)
    annotation (Line(points={{-69.07802146882929,-107.14424468030944},{-49.07802146882929,-107.14424468030944},{-49.07802146882929,-87.14424468030944},{-49.07802146882929,-67.14424468030944},{-49.07802146882929,-47.14424468030944},{-49.07802146882929,-27.14424468030944},{-49.07802146882929,-7.144244680309441},{-49.07802146882929,12.855755319690559},{-49.07802146882929,32.85575531969056},{-29.07802146882929,32.85575531969056},{-9.078021468829292,32.85575531969056},{10.921978531170708,32.85575531969056}},color={0,0,127}));
  connect(THeaWatSet_5127a512.y,heaInd_9562514f.TSetBuiSup)
    annotation (Line(points={{-10.62240338126712,-102.17129064597631},{9.37759661873288,-102.17129064597631},{9.37759661873288,-82.17129064597631},{9.37759661873288,-62.17129064597631},{9.37759661873288,-42.17129064597631},{9.37759661873288,-22.171290645976313},{9.37759661873288,-2.1712906459763133},{9.37759661873288,17.828709354023687},{9.37759661873288,37.82870935402369},{29.37759661873288,37.82870935402369}},color={0,0,127}));

  //
  // End Connect Statements for 5127a512
  //



  //
  // Begin Connect Statements for 5396de39
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // heating indirect and network 2 pipe
  
  connect(disNet_16bb913e.ports_bCon[2],heaInd_9562514f.port_a1)
    annotation (Line(points={{-18.109988262797884,63.73005129228129},{-18.109988262797884,43.73005129228129},{1.8900117372021157,43.73005129228129},{21.890011737202116,43.73005129228129}},color={0,0,127}));
  connect(disNet_16bb913e.ports_aCon[2],heaInd_9562514f.port_b1)
    annotation (Line(points={{-10.651465671440036,58.15097336263176},{-10.651465671440036,38.15097336263176},{9.348534328559964,38.15097336263176},{29.348534328559964,38.15097336263176}},color={0,0,127}));

  //
  // End Connect Statements for 5396de39
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