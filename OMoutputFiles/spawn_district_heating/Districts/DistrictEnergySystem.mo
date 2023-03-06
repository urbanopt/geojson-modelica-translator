within spawn_district_heating.Districts;
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
  // Begin Model Instance for disNet_97fa5a54
  // Source template: /model_connectors/networks/templates/Network2Pipe_Instance.mopt
  //
parameter Integer nBui_disNet_97fa5a54=1;
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_disNet_97fa5a54=sum({
    heaInd_92c83b84.mDis_flow_nominal})
    "Nominal mass flow rate of the distribution pump";
  parameter Modelica.Units.SI.MassFlowRate mCon_flow_nominal_disNet_97fa5a54[nBui_disNet_97fa5a54]={
    heaInd_92c83b84.mDis_flow_nominal}
    "Nominal mass flow rate in each connection line";
  parameter Modelica.Units.SI.PressureDifference dpDis_nominal_disNet_97fa5a54[nBui_disNet_97fa5a54](
    each min=0,
    each displayUnit="Pa")=1/2 .* cat(
    1,
    {dp_nominal_disNet_97fa5a54*0.1},
    fill(
      dp_nominal_disNet_97fa5a54*0.9/(nBui_disNet_97fa5a54-1),
      nBui_disNet_97fa5a54-1))
    "Pressure drop between each connected building at nominal conditions (supply line)";
  parameter Modelica.Units.SI.PressureDifference dp_nominal_disNet_97fa5a54=dpSetPoi_disNet_97fa5a54+nBui_disNet_97fa5a54*7000
    "District network pressure drop";
  // NOTE: this differential pressure setpoint is currently utilized by plants elsewhere
  parameter Modelica.Units.SI.Pressure dpSetPoi_disNet_97fa5a54=50000
    "Differential pressure setpoint";

  Buildings.Experimental.DHC.Networks.Distribution2Pipe disNet_97fa5a54(
    redeclare final package Medium=MediumW,
    final nCon=nBui_disNet_97fa5a54,
    iConDpSen=nBui_disNet_97fa5a54,
    final mDis_flow_nominal=mDis_flow_nominal_disNet_97fa5a54,
    final mCon_flow_nominal=mCon_flow_nominal_disNet_97fa5a54,
    final allowFlowReversal=true,
    dpDis_nominal=dpDis_nominal_disNet_97fa5a54)
    "Distribution network."
    annotation (Placement(transformation(extent={{-30.0,40.0},{-10.0,50.0}})));
  //
  // End Model Instance for disNet_97fa5a54
  //


  
  //
  // Begin Model Instance for heaPla899b43a2
  // Source template: /model_connectors/plants/templates/HeatingPlant_Instance.mopt
  //
  // heating plant instance
  parameter Modelica.Units.SI.MassFlowRate mHW_flow_nominal_heaPla899b43a2=mBoi_flow_nominal_heaPla899b43a2*heaPla899b43a2.numBoi
    "Nominal heating water mass flow rate";
  parameter Modelica.Units.SI.MassFlowRate mBoi_flow_nominal_heaPla899b43a2=QBoi_nominal_heaPla899b43a2/(4200*heaPla899b43a2.delT_nominal)
    "Nominal heating water mass flow rate";
  parameter Modelica.Units.SI.Power QBoi_nominal_heaPla899b43a2=Q_flow_nominal_heaPla899b43a2/heaPla899b43a2.numBoi
    "Nominal heating capaciaty";
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_heaPla899b43a2=1000000*2
    "Heating load";
  parameter Modelica.Units.SI.MassFlowRate mMin_flow_heaPla899b43a2=0.2*mBoi_flow_nominal_heaPla899b43a2
    "Minimum mass flow rate of single boiler";
  // controls
  parameter Modelica.Units.SI.Pressure pumDP=(heaPla899b43a2.dpBoi_nominal+dpSetPoi_disNet_97fa5a54+50000)
    "Heating water pump pressure drop";
  parameter Modelica.Units.SI.Time tWai_heaPla899b43a2=30
    "Waiting time";
  parameter Buildings.Fluid.Movers.Data.Generic perHWPum_heaPla899b43a2(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=mBoi_flow_nominal_heaPla899b43a2/1000*{0.1,1.1},
      dp=pumDP*{1.1,0.1}))
    "Performance data for heating water pumps";

  spawn_district_heating.Plants.CentralHeatingPlant heaPla899b43a2(
    perHWPum=perHWPum_heaPla899b43a2,
    mHW_flow_nominal=mHW_flow_nominal_heaPla899b43a2,
    QBoi_flow_nominal=QBoi_nominal_heaPla899b43a2,
    mMin_flow=mMin_flow_heaPla899b43a2,
    mBoi_flow_nominal=mBoi_flow_nominal_heaPla899b43a2,
    dpBoi_nominal=10000,
    delT_nominal(
      displayUnit="degC")=15,
    tWai=tWai_heaPla899b43a2,
    // TODO: we're currently grabbing dpSetPoi from the Network instance -- need feedback to determine if that's the proper "home" for it
    dpSetPoi=dpSetPoi_disNet_97fa5a54
    )
    "District heating plant."
    annotation (Placement(transformation(extent={{-70.0,30.0},{-50.0,50.0}})));
  //
  // End Model Instance for heaPla899b43a2
  //


  
  //
  // Begin Model Instance for SpawnLoad_b8f8936d
  // Source template: /model_connectors/load_connectors/templates/Spawn_Instance.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mLoaCoo_flow_nominal_SpawnLoad_b8f8936d[SpawnLoad_b8f8936d.nZon]={(-1*SpawnLoad_b8f8936d.QCoo_flow_nominal[i]*(0.06)/1000) for i in 1:SpawnLoad_b8f8936d.nZon};
  parameter Modelica.Units.SI.MassFlowRate mLoaHea_flow_nominal_SpawnLoad_b8f8936d[SpawnLoad_b8f8936d.nZon]={(SpawnLoad_b8f8936d.QHea_flow_nominal[i]*(0.05)/1000) for i in 1:SpawnLoad_b8f8936d.nZon};
  spawn_district_heating.Loads.B5a6b99ec37f4de7f94020090.building SpawnLoad_b8f8936d(
    allowFlowReversal = true, 
    mLoaCoo_flow_nominal=mLoaCoo_flow_nominal_SpawnLoad_b8f8936d,
    mLoaHea_flow_nominal=mLoaHea_flow_nominal_SpawnLoad_b8f8936d,
    nPorts_aHeaWat=1,
    nPorts_bHeaWat=1,
    nPorts_aChiWat=1,
    nPorts_bChiWat=1,
    have_pum=true)
    "Building spawn model"
    annotation (Placement(transformation(extent={{50.0,30.0},{70.0,50.0}})));
  //
  // End Model Instance for SpawnLoad_b8f8936d
  //


  
  //
  // Begin Model Instance for heaInd_92c83b84
  // Source template: /model_connectors/energy_transfer_systems/templates/HeatingIndirect_Instance.mopt
  //
  // heating indirect instance
  spawn_district_heating.Substations.HeatingIndirect_5a6b99ec37f4de7f94020090 heaInd_92c83b84(
    allowFlowReversal1=true,
    allowFlowReversal2=true,
    show_T=true,
    redeclare package Medium=MediumW,
    mDis_flow_nominal=mDis_flow_nominal_5c425775,
    mBui_flow_nominal=mBui_flow_nominal_5c425775,
    dpValve_nominal=6000,
    dp1_nominal=500,
    dp2_nominal=500,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_5c425775,
    T_a1_nominal=55+273.15,
    T_a2_nominal=35+273.15,
    k=0.1,
    Ti=60,
    reverseActing=true)
    annotation (Placement(transformation(extent={{10.0,30.0},{30.0,50.0}})));
  //
  // End Model Instance for heaInd_92c83b84
  //


  
  //
  // Begin Model Instance for etsColWatStub_f93069c2
  // Source template: /model_connectors/energy_transfer_systems/templates/EtsColdWaterStub_Instance.mopt
  //
  // TODO: move these components into a single component
  Buildings.Fluid.Sources.Boundary_pT supChiWat_etsColWatStub_f93069c2(
    redeclare package Medium=MediumW,
    use_T_in=true,
    nPorts=1)
    "Chilled water supply"
    annotation (Placement(transformation(extent={{-30.0,-50.0},{-10.0,-30.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinChiWat_etsColWatStub_f93069c2(
    redeclare package Medium=MediumW,
    nPorts=1)
    "Chilled water sink"
    annotation (Placement(transformation(extent={{10.0,-50.0},{30.0,-30.0}})));
  //
  // End Model Instance for etsColWatStub_f93069c2
  //


  

  // Model dependencies

  //
  // Begin Component Definitions for cc234d07
  // Source template: /model_connectors/couplings/templates/Network2Pipe_HeatingPlant/ComponentDefinitions.mopt
  //
  // TODO: This should not be here, it is entirely plant specific and should be moved elsewhere
  // but since it requires a connect statement we must put it here for now...
  Modelica.Blocks.Sources.BooleanConstant mPum_flow_cc234d07(
    k=true)
    "Total heating water pump mass flow rate"
    annotation (Placement(transformation(extent={{-70.0,-10.0},{-50.0,10.0}})));
  // TODO: This should not be here, it is entirely plant specific and should be moved elsewhere
  // but since it requires a connect statement we must put it here for now...
  Modelica.Blocks.Sources.RealExpression TDisSetHeaWat_cc234d07(
    each y=273.15+54)
    "District side heating water supply temperature set point."
    annotation (Placement(transformation(extent={{-30.0,-10.0},{-10.0,10.0}})));

  //
  // End Component Definitions for cc234d07
  //



  //
  // Begin Component Definitions for 5c425775
  // Source template: /model_connectors/couplings/templates/Spawn_HeatingIndirect/ComponentDefinitions.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_5c425775=SpawnLoad_b8f8936d.disFloHea.m_flow_nominal*delHeaWatTemBui/delHeaWatTemDis
    "Nominal mass flow rate of primary (district) district heating side"; // TODO: Verify this is ok!
  parameter Modelica.Units.SI.MassFlowRate mBui_flow_nominal_5c425775=SpawnLoad_b8f8936d.terUni[1].mHeaWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district heating side"; // TODO: Verify this is ok!
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_5c425775=SpawnLoad_b8f8936d.QHea_flow_nominal[1]; // TODO: Verify this is ok!
  Modelica.Fluid.Sources.FixedBoundary pressure_source_5c425775(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{10.0,-10.0},{30.0,10.0}})));
  // TODO: move THeaWatSet (and its connection) into a HeatingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression THeaWatSet_5c425775(
    // y=40+273.15)
    y=273.15+40 )
    "Secondary loop (Building side) heating water setpoint temperature."
    //Dehardcode
    annotation (Placement(transformation(extent={{50.0,-10.0},{70.0,10.0}})));

  //
  // End Component Definitions for 5c425775
  //



  //
  // Begin Component Definitions for 85363771
  // Source template: /model_connectors/couplings/templates/Spawn_EtsColdWaterStub/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression TChiWatSup_85363771(
    y=min(
      SpawnLoad_b8f8936d.terUni.T_aChiWat_nominal))
    "Chilled water supply temperature"
    annotation (Placement(transformation(extent={{-70.0,-50.0},{-50.0,-30.0}})));

  //
  // End Component Definitions for 85363771
  //



  //
  // Begin Component Definitions for d518bdb0
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for heating indirect and network 2 pipe

  //
  // End Component Definitions for d518bdb0
  //



equation
  // Connections

  //
  // Begin Connect Statements for cc234d07
  // Source template: /model_connectors/couplings/templates/Network2Pipe_HeatingPlant/ConnectStatements.mopt
  //

  connect(heaPla899b43a2.port_a,disNet_97fa5a54.port_bDisRet)
    annotation (Line(points={{-33.98724000360221,43.559585355691084},{-13.98724000360221,43.559585355691084}},color={0,0,127}));
  connect(disNet_97fa5a54.dp,heaPla899b43a2.dpMea)
    annotation (Line(points={{-49.575754355909424,34.12586499337297},{-69.57575435590942,34.12586499337297}},color={0,0,127}));
  connect(heaPla899b43a2.port_b,disNet_97fa5a54.port_aDisSup)
    annotation (Line(points={{-33.403655364696945,44.64519381467333},{-13.403655364696945,44.64519381467333}},color={0,0,127}));
  connect(mPum_flow_cc234d07.y,heaPla899b43a2.on)
    annotation (Line(points={{-50.994582770726126,15.972207702750495},{-50.994582770726126,35.972207702750495}},color={0,0,127}));
  connect(TDisSetHeaWat_cc234d07.y,heaPla899b43a2.THeaSet)
    annotation (Line(points={{-23.495177644738945,15.471544190209165},{-43.49517764473894,15.471544190209165},{-43.49517764473894,35.471544190209165},{-63.495177644738945,35.471544190209165}},color={0,0,127}));

  //
  // End Connect Statements for cc234d07
  //



  //
  // Begin Connect Statements for 5c425775
  // Source template: /model_connectors/couplings/templates/Spawn_HeatingIndirect/ConnectStatements.mopt
  //

  connect(SpawnLoad_b8f8936d.ports_bHeaWat[1], heaInd_92c83b84.port_a2)
    annotation (Line(points={{32.92116307849487,49.138232218176526},{12.921163078494871,49.138232218176526}},color={0,0,127}));
  connect(heaInd_92c83b84.port_b2,SpawnLoad_b8f8936d.ports_aHeaWat[1])
    annotation (Line(points={{33.67333089020913,38.484036783337714},{53.673330890209115,38.484036783337714}},color={0,0,127}));
  connect(pressure_source_5c425775.ports[1], heaInd_92c83b84.port_b2)
    annotation (Line(points={{17.595816597927367,18.393711355433005},{17.595816597927367,38.393711355433005}},color={0,0,127}));
  connect(THeaWatSet_5c425775.y,heaInd_92c83b84.TSetBuiSup)
    annotation (Line(points={{59.13324086213575,26.268663590824616},{39.13324086213575,26.268663590824616},{39.13324086213575,46.268663590824616},{19.133240862135764,46.268663590824616}},color={0,0,127}));

  //
  // End Connect Statements for 5c425775
  //



  //
  // Begin Connect Statements for 85363771
  // Source template: /model_connectors/couplings/templates/Spawn_EtsColdWaterStub/ConnectStatements.mopt
  //

  // spawn, ets cold water stub connections
  connect(TChiWatSup_85363771.y,supChiWat_etsColWatStub_f93069c2.T_in)
    annotation (Line(points={{-33.45161994936271,-43.779332543319555},{-13.451619949362708,-43.779332543319555}},color={0,0,127}));
  connect(SpawnLoad_b8f8936d.ports_bChiWat[1],sinChiWat_etsColWatStub_f93069c2.ports[1])
    annotation (Line(points={{62.548513602261835,26.32374758702511},{42.548513602261835,26.32374758702511},{42.548513602261835,6.32374758702511},{42.548513602261835,-13.67625241297489},{42.548513602261835,-33.67625241297489},{22.548513602261835,-33.67625241297489}},color={0,0,127}));
  connect(supChiWat_etsColWatStub_f93069c2.ports[1],SpawnLoad_b8f8936d.ports_aChiWat[1])
    annotation (Line(points={{-29.482092834702925,-28.079060915084938},{-9.482092834702925,-28.079060915084938},{-9.482092834702925,-8.079060915084938},{-9.482092834702925,11.920939084915062},{10.517907165297075,11.920939084915062},{30.517907165297075,11.920939084915062},{30.517907165297075,31.920939084915062},{50.51790716529706,31.920939084915062}},color={0,0,127}));

  //
  // End Connect Statements for 85363771
  //



  //
  // Begin Connect Statements for d518bdb0
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // heating indirect and network 2 pipe
  
  connect(disNet_97fa5a54.ports_bCon[1],heaInd_92c83b84.port_a1)
    annotation (Line(points={{-5.788607091647194,32.82104079930156},{14.211392908352806,32.82104079930156}},color={0,0,127}));
  connect(disNet_97fa5a54.ports_aCon[1],heaInd_92c83b84.port_b1)
    annotation (Line(points={{-3.522850494745583,34.375063922616},{16.477149505254417,34.375063922616}},color={0,0,127}));

  //
  // End Connect Statements for d518bdb0
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