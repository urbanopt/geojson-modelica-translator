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
  parameter Integer numberofchiller = 2;
  // Models

  //
  // Begin Model Instance for disNet_90e09dae
  // Source template: /model_connectors/networks/templates/Network2Pipe_Instance.mopt
  //
parameter Integer nBui_disNet_90e09dae=1;
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_disNet_90e09dae=sum({
    cooInd_78fb87ae.mDis_flow_nominal})
    "Nominal mass flow rate of the distribution pump";
  parameter Modelica.Units.SI.MassFlowRate mCon_flow_nominal_disNet_90e09dae[nBui_disNet_90e09dae]={
    cooInd_78fb87ae.mDis_flow_nominal}
    "Nominal mass flow rate in each connection line";
  parameter Modelica.Units.SI.PressureDifference dpDis_nominal_disNet_90e09dae[nBui_disNet_90e09dae](
    each min=0,
    each displayUnit="Pa")=1/2 .* cat(
    1,
    {dp_nominal_disNet_90e09dae*0.1},
    fill(
      dp_nominal_disNet_90e09dae*0.9/(nBui_disNet_90e09dae-1),
      nBui_disNet_90e09dae-1))
    "Pressure drop between each connected building at nominal conditions (supply line)";
  parameter Modelica.Units.SI.PressureDifference dp_nominal_disNet_90e09dae=dpSetPoi_disNet_90e09dae+nBui_disNet_90e09dae*7000
    "District network pressure drop";
  // NOTE: this differential pressure setpoint is currently utilized by plants elsewhere
  parameter Modelica.Units.SI.Pressure dpSetPoi_disNet_90e09dae=50000
    "Differential pressure setpoint";

  Buildings.Experimental.DHC.Networks.Distribution2Pipe disNet_90e09dae(
    redeclare final package Medium=MediumW,
    final nCon=nBui_disNet_90e09dae,
    iConDpSen=nBui_disNet_90e09dae,
    final mDis_flow_nominal=mDis_flow_nominal_disNet_90e09dae,
    final mCon_flow_nominal=mCon_flow_nominal_disNet_90e09dae,
    final allowFlowReversal=true,
    dpDis_nominal=dpDis_nominal_disNet_90e09dae)
    "Distribution network."
    annotation (Placement(transformation(extent={{-30.0,40.0},{-10.0,50.0}})));
  //
  // End Model Instance for disNet_90e09dae
  //


  
  //
  // Begin Model Instance for cooPla_64b500d1
  // Source template: /model_connectors/plants/templates/CoolingPlant_Instance.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mCHW_flow_nominal_cooPla_64b500d1=cooPla_64b500d1.numChi*(cooPla_64b500d1.perChi.mEva_flow_nominal)
    "Nominal chilled water mass flow rate";
  parameter Modelica.Units.SI.MassFlowRate mCW_flow_nominal_cooPla_64b500d1=cooPla_64b500d1.perChi.mCon_flow_nominal
    "Nominal condenser water mass flow rate";
  parameter Modelica.Units.SI.PressureDifference dpCHW_nominal_cooPla_64b500d1=44.8*1000
    "Nominal chilled water side pressure";
  parameter Modelica.Units.SI.PressureDifference dpCW_nominal_cooPla_64b500d1=46.2*1000
    "Nominal condenser water side pressure";
  parameter Modelica.Units.SI.Power QEva_nominal_cooPla_64b500d1=mCHW_flow_nominal_cooPla_64b500d1*4200*(5-14)
    "Nominal cooling capaciaty (Negative means cooling)";
  parameter Modelica.Units.SI.MassFlowRate mMin_flow_cooPla_64b500d1=0.2*mCHW_flow_nominal_cooPla_64b500d1/cooPla_64b500d1.numChi
    "Minimum mass flow rate of single chiller";
  // control settings
  parameter Modelica.Units.SI.Pressure dpSetPoi_cooPla_64b500d1=70000
    "Differential pressure setpoint";
  parameter Modelica.Units.SI.Pressure pumDP_cooPla_64b500d1=dpCHW_nominal_cooPla_64b500d1+dpSetPoi_cooPla_64b500d1+200000;
  parameter Modelica.Units.SI.Time tWai_cooPla_64b500d1=30
    "Waiting time";
  // pumps
  parameter Buildings.Fluid.Movers.Data.Generic perCHWPum_cooPla_64b500d1(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=((mCHW_flow_nominal_cooPla_64b500d1/numberofchiller)/1000)*{0.1,1,1.2},
      dp=pumDP_cooPla_64b500d1*{1.2,1,0.1}))
    "Performance data for chilled water pumps";
  parameter Buildings.Fluid.Movers.Data.Generic perCWPum_cooPla_64b500d1(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=mCW_flow_nominal_cooPla_64b500d1/1000*{0.2,0.6,1.0,1.2},
      dp=(dpCW_nominal_cooPla_64b500d1+60000+6000)*{1.2,1.1,1.0,0.6}))
    "Performance data for condenser water pumps";


  Modelica.Blocks.Sources.RealExpression TSetChiWatDis_cooPla_64b500d1(
    y=5+273.15)
    "Chilled water supply temperature set point on district level."
    annotation (Placement(transformation(extent={{50.0,-10.0},{70.0,10.0}})));
  Modelica.Blocks.Sources.BooleanConstant on_cooPla_64b500d1
    "On signal of the plant"
    annotation (Placement(transformation(extent={{-70.0,-50.0},{-50.0,-30.0}})));

  spawn_district_cooling.Plants.CentralCoolingPlant cooPla_64b500d1(
     numChi = numberofchiller,
    redeclare Buildings.Fluid.Chillers.Data.ElectricEIR.ElectricEIRChiller_Carrier_19EX_5208kW_6_88COP_Vanes perChi,
    perCHWPum=perCHWPum_cooPla_64b500d1,
    perCWPum=perCWPum_cooPla_64b500d1,
    mCHW_flow_nominal=mCHW_flow_nominal_cooPla_64b500d1,
    dpCHW_nominal=dpCHW_nominal_cooPla_64b500d1,
    QEva_nominal=QEva_nominal_cooPla_64b500d1,
    mMin_flow=mMin_flow_cooPla_64b500d1,
    mCW_flow_nominal=mCW_flow_nominal_cooPla_64b500d1,
    dpCW_nominal=dpCW_nominal_cooPla_64b500d1,
    TAirInWB_nominal=298.7,
    TCW_nominal=308.15,
    TMin=288.15,
    tWai=tWai_cooPla_64b500d1,
    dpSetPoi=dpSetPoi_cooPla_64b500d1
    )
    "District cooling plant."
    annotation (Placement(transformation(extent={{-70.0,30.0},{-50.0,50.0}})));
  //
  // End Model Instance for cooPla_64b500d1
  //


  
  //
  // Begin Model Instance for SpawnLoad_aed2da14
  // Source template: /model_connectors/load_connectors/templates/Spawn_Instance.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mLoaCoo_flow_nominal_SpawnLoad_aed2da14[SpawnLoad_aed2da14.nZon]={(-1*SpawnLoad_aed2da14.QCoo_flow_nominal[i]*(0.06)/1000) for i in 1:SpawnLoad_aed2da14.nZon};
  parameter Modelica.Units.SI.MassFlowRate mLoaHea_flow_nominal_SpawnLoad_aed2da14[SpawnLoad_aed2da14.nZon]={(SpawnLoad_aed2da14.QHea_flow_nominal[i]*(0.05)/1000) for i in 1:SpawnLoad_aed2da14.nZon};
  spawn_district_cooling.Loads.B5a6b99ec37f4de7f94020090.building SpawnLoad_aed2da14(
  allowFlowReversal = true,
    mLoaCoo_flow_nominal=mLoaCoo_flow_nominal_SpawnLoad_aed2da14,
    mLoaHea_flow_nominal=mLoaHea_flow_nominal_SpawnLoad_aed2da14,
    nPorts_aHeaWat=1,
    nPorts_bHeaWat=1,
    nPorts_aChiWat=1,
    nPorts_bChiWat=1,
    have_pum=true)
    "Building spawn model"
    annotation (Placement(transformation(extent={{50.0,30.0},{70.0,50.0}})));
  //
  // End Model Instance for SpawnLoad_aed2da14
  //


  
  //
  // Begin Model Instance for cooInd_78fb87ae
  // Source template: /model_connectors/energy_transfer_systems/templates/CoolingIndirect_Instance.mopt
  //
  // cooling indirect instance
  spawn_district_cooling.Substations.CoolingIndirect_5a6b99ec37f4de7f94020090 cooInd_78fb87ae(
    redeclare package Medium=MediumW,
    allowFlowReversal1=true,
    allowFlowReversal2=true,
    mDis_flow_nominal=mDis_flow_nominal_e88c4e32,
    mBui_flow_nominal=mBui_flow_nominal_e88c4e32,
    dp1_nominal=500,
    dp2_nominal=500,
    dpValve_nominal=7000,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_e88c4e32,
    // TODO: dehardcode the nominal temperatures?
    T_a1_nominal=273.15+5,
    T_a2_nominal=273.15+13)
    "Indirect cooling energy transfer station ETS."
    annotation (Placement(transformation(extent={{10.0,30.0},{30.0,50.0}})));
  //
  // End Model Instance for cooInd_78fb87ae
  //


  
  //
  // Begin Model Instance for etsHotWatStub_a784c189
  // Source template: /model_connectors/energy_transfer_systems/templates/EtsHotWaterStub_Instance.mopt
  //
  // TODO: move these components into a single component
  Buildings.Fluid.Sources.Boundary_pT supHeaWat_etsHotWatStub_a784c189(
    redeclare package Medium=MediumW,
    use_T_in=true,
    nPorts=1)
    "Heating water supply"
    annotation (Placement(transformation(extent={{-30.0,-50.0},{-10.0,-30.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinHeaWat_etsHotWatStub_a784c189(
    redeclare package Medium=MediumW,
    nPorts=1)
    "Heating water sink"
    annotation (Placement(transformation(extent={{10.0,-50.0},{30.0,-30.0}})));
  //
  // End Model Instance for etsHotWatStub_a784c189
  //


  

  // Model dependencies

  //
  // Begin Component Definitions for dd421fc7
  // Source template: /model_connectors/couplings/templates/Network2Pipe_CoolingPlant/ComponentDefinitions.mopt
  //
  // No components for pipe and cooling plant

  //
  // End Component Definitions for dd421fc7
  //



  //
  // Begin Component Definitions for e88c4e32
  // Source template: /model_connectors/couplings/templates/Spawn_CoolingIndirect/ComponentDefinitions.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_e88c4e32=SpawnLoad_aed2da14.disFloCoo.m_flow_nominal*delChiWatTemBui/delChiWatTemDis
    "Nominal mass flow rate of primary (district) district cooling side"; // TODO: verify this is ok!
  parameter Modelica.Units.SI.MassFlowRate mBui_flow_nominal_e88c4e32=SpawnLoad_aed2da14.terUni[1].mChiWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district cooling side"; // TODO: verify this is ok!
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_e88c4e32=-1*SpawnLoad_aed2da14.QHea_flow_nominal[1]; // TODO: verify this is ok!
  Modelica.Fluid.Sources.FixedBoundary pressure_source_e88c4e32(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{-70.0,-10.0},{-50.0,10.0}})));
  // TODO: move TChiWatSet (and its connection) into a CoolingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression TChiWatSet_e88c4e32(
    y=7+273.15)
    //Dehardcode
    "Primary loop (district side) chilled water setpoint temperature."
    annotation (Placement(transformation(extent={{-30.0,-10.0},{-10.0,10.0}})));

  //
  // End Component Definitions for e88c4e32
  //



  //
  // Begin Component Definitions for 50d0c3d9
  // Source template: /model_connectors/couplings/templates/Spawn_EtsHotWaterStub/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression THeaWatSup_50d0c3d9(
    y=max(
      SpawnLoad_aed2da14.terUni.T_aHeaWat_nominal))
    "Heating water supply temperature"
    annotation (Placement(transformation(extent={{10.0,-10.0},{30.0,10.0}})));

  //
  // End Component Definitions for 50d0c3d9
  //



  //
  // Begin Component Definitions for 71947c52
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for cooling indirect and network 2 pipe

  //
  // End Component Definitions for 71947c52
  //



equation
  // Connections

  //
  // Begin Connect Statements for dd421fc7
  // Source template: /model_connectors/couplings/templates/Network2Pipe_CoolingPlant/ConnectStatements.mopt
  //

  // TODO: these connect statements shouldn't be here, they are plant specific
  // but since we can't currently make connect statements for single systems, this is what we've got
  connect(on_cooPla_64b500d1.y,cooPla_64b500d1.on)
    annotation (Line(points={{-53.1701001877164,-26.1457773285681},{-73.1701001877164,-26.1457773285681},{-73.1701001877164,-6.145777328568101},{-73.1701001877164,13.854222671431891},{-73.1701001877164,33.85422267143189},{-53.1701001877164,33.85422267143189}},color={0,0,127}));
  connect(TSetChiWatDis_cooPla_64b500d1.y,cooPla_64b500d1.TCHWSupSet)
    annotation (Line(points={{58.969794527516,23.81420727575246},{38.969794527516,23.81420727575246},{18.969794527516,23.81420727575246},{-1.030205472483999,23.81420727575246},{-21.030205472484,23.81420727575246},{-41.030205472484,23.81420727575246},{-41.030205472484,43.81420727575246},{-61.030205472484,43.81420727575246}},color={0,0,127}));

  connect(disNet_90e09dae.port_bDisRet,cooPla_64b500d1.port_a)
    annotation (Line(points={{-31.117069623558606,44.18759198093028},{-51.117069623558606,44.18759198093028}},color={0,0,127}));
  connect(cooPla_64b500d1.port_b,disNet_90e09dae.port_aDisSup)
    annotation (Line(points={{-31.18211965130456,41.62024185278039},{-11.18211965130456,41.62024185278039}},color={0,0,127}));
  connect(disNet_90e09dae.dp,cooPla_64b500d1.dpMea)
    annotation (Line(points={{-46.74789231454109,42.58394820796661},{-66.74789231454109,42.58394820796661}},color={0,0,127}));

  //
  // End Connect Statements for dd421fc7
  //



  //
  // Begin Connect Statements for e88c4e32
  // Source template: /model_connectors/couplings/templates/Spawn_CoolingIndirect/ConnectStatements.mopt
  //

  connect(SpawnLoad_aed2da14.ports_bChiWat[1], cooInd_78fb87ae.port_a2)
    annotation (Line(points={{45.33829458931211,33.2583655105604},{25.338294589312113,33.2583655105604}},color={0,0,127}));
  connect(cooInd_78fb87ae.port_b2,SpawnLoad_aed2da14.ports_aChiWat[1])
    annotation (Line(points={{33.20326386984544,47.72810343080687},{53.20326386984544,47.72810343080687}},color={0,0,127}));
  connect(pressure_source_e88c4e32.ports[1], cooInd_78fb87ae.port_b2)
    annotation (Line(points={{-67.52175932183289,22.486338925472474},{-47.52175932183289,22.486338925472474},{-27.52175932183289,22.486338925472474},{-7.521759321832889,22.486338925472474},{-7.521759321832889,42.48633892547247},{12.478240678167111,42.48633892547247}},color={0,0,127}));
  connect(TChiWatSet_e88c4e32.y,cooInd_78fb87ae.TSetBuiSup)
    annotation (Line(points={{-14.194443376762138,27.997787268775504},{5.805556623237862,27.997787268775504},{25.805556623237862,27.997787268775504},{45.80555662323786,27.997787268775504},{45.80555662323786,47.997787268775504},{65.80555662323786,47.997787268775504}},color={0,0,127}));

  //
  // End Connect Statements for e88c4e32
  //



  //
  // Begin Connect Statements for 50d0c3d9
  // Source template: /model_connectors/couplings/templates/Spawn_EtsHotWaterStub/ConnectStatements.mopt
  //

  // spawn, ets hot water stub connections
  connect(supHeaWat_etsHotWatStub_a784c189.T_in,THeaWatSup_50d0c3d9.y)
    annotation (Line(points={{-11.2616164351426,-12.445981960318989},{8.7383835648574,-12.445981960318989},{8.7383835648574,7.5540180396810115},{28.7383835648574,7.5540180396810115}},color={0,0,127}));
  connect(supHeaWat_etsHotWatStub_a784c189.ports[1],SpawnLoad_aed2da14.ports_aHeaWat[1])
    annotation (Line(points={{-10.14303740851257,-16.926573247152106},{9.85696259148743,-16.926573247152106},{9.85696259148743,3.073426752847894},{9.85696259148743,23.0734267528479},{29.85696259148743,23.0734267528479},{49.856962591487445,23.0734267528479},{49.856962591487445,43.0734267528479},{69.85696259148745,43.0734267528479}},color={0,0,127}));
  connect(sinHeaWat_etsHotWatStub_a784c189.ports[1],SpawnLoad_aed2da14.ports_bHeaWat[1])
    annotation (Line(points={{13.836640763604777,-22.457497095858685},{33.83664076360478,-22.457497095858685},{33.83664076360478,-2.4574970958586846},{33.83664076360478,17.542502904141323},{33.83664076360478,37.54250290414132},{53.83664076360478,37.54250290414132}},color={0,0,127}));

  //
  // End Connect Statements for 50d0c3d9
  //



  //
  // Begin Connect Statements for 71947c52
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // cooling indirect and network 2 pipe
  
  connect(disNet_90e09dae.ports_bCon[1],cooInd_78fb87ae.port_a1)
    annotation (Line(points={{-4.138882684674996,33.15234051313274},{15.861117315325004,33.15234051313274}},color={0,0,127}));
  connect(disNet_90e09dae.ports_aCon[1],cooInd_78fb87ae.port_b1)
    annotation (Line(points={{7.481588148612886,44.85311971991753},{27.481588148612886,44.85311971991753}},color={0,0,127}));

  //
  // End Connect Statements for 71947c52
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