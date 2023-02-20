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
  // Begin Model Instance for disNet_1e8cfb72
  // Source template: /model_connectors/networks/templates/Network2Pipe_Instance.mopt
  //
parameter Integer nBui_disNet_1e8cfb72=1;
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_disNet_1e8cfb72=sum({
    heaInd_de5f7708.mDis_flow_nominal})
    "Nominal mass flow rate of the distribution pump";
  parameter Modelica.Units.SI.MassFlowRate mCon_flow_nominal_disNet_1e8cfb72[nBui_disNet_1e8cfb72]={
    heaInd_de5f7708.mDis_flow_nominal}
    "Nominal mass flow rate in each connection line";
  parameter Modelica.Units.SI.PressureDifference dpDis_nominal_disNet_1e8cfb72[nBui_disNet_1e8cfb72](
    each min=0,
    each displayUnit="Pa")=1/2 .* cat(
    1,
    {dp_nominal_disNet_1e8cfb72*0.1},
    fill(
      dp_nominal_disNet_1e8cfb72*0.9/(nBui_disNet_1e8cfb72-1),
      nBui_disNet_1e8cfb72-1))
    "Pressure drop between each connected building at nominal conditions (supply line)";
  parameter Modelica.Units.SI.PressureDifference dp_nominal_disNet_1e8cfb72=dpSetPoi_disNet_1e8cfb72+nBui_disNet_1e8cfb72*7000
    "District network pressure drop";
  // NOTE: this differential pressure setpoint is currently utilized by plants elsewhere
  parameter Modelica.Units.SI.Pressure dpSetPoi_disNet_1e8cfb72=50000
    "Differential pressure setpoint";

  Buildings.Experimental.DHC.Networks.Distribution2Pipe disNet_1e8cfb72(
    redeclare final package Medium=MediumW,
    final nCon=nBui_disNet_1e8cfb72,
    iConDpSen=nBui_disNet_1e8cfb72,
    final mDis_flow_nominal=mDis_flow_nominal_disNet_1e8cfb72,
    final mCon_flow_nominal=mCon_flow_nominal_disNet_1e8cfb72,
    final allowFlowReversal=true,
    dpDis_nominal=dpDis_nominal_disNet_1e8cfb72)
    "Distribution network."
    annotation (Placement(transformation(extent={{-30.0,40.0},{-10.0,50.0}})));
  //
  // End Model Instance for disNet_1e8cfb72
  //


  
  //
  // Begin Model Instance for heaPlac7d62edc
  // Source template: /model_connectors/plants/templates/HeatingPlant_Instance.mopt
  //
  // heating plant instance
  parameter Modelica.Units.SI.MassFlowRate mHW_flow_nominal_heaPlac7d62edc=mBoi_flow_nominal_heaPlac7d62edc*heaPlac7d62edc.numBoi
    "Nominal heating water mass flow rate";
  parameter Modelica.Units.SI.MassFlowRate mBoi_flow_nominal_heaPlac7d62edc=QBoi_nominal_heaPlac7d62edc/(4200*heaPlac7d62edc.delT_nominal)
    "Nominal heating water mass flow rate";
  parameter Modelica.Units.SI.Power QBoi_nominal_heaPlac7d62edc=Q_flow_nominal_heaPlac7d62edc/heaPlac7d62edc.numBoi
    "Nominal heating capaciaty";
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_heaPlac7d62edc=1000000*2
    "Heating load";
  parameter Modelica.Units.SI.MassFlowRate mMin_flow_heaPlac7d62edc=0.2*mBoi_flow_nominal_heaPlac7d62edc
    "Minimum mass flow rate of single boiler";
  // controls
  parameter Modelica.Units.SI.Pressure pumDP=(heaPlac7d62edc.dpBoi_nominal+dpSetPoi_disNet_1e8cfb72+50000)
    "Heating water pump pressure drop";
  parameter Modelica.Units.SI.Time tWai_heaPlac7d62edc=30
    "Waiting time";
  parameter Buildings.Fluid.Movers.Data.Generic perHWPum_heaPlac7d62edc(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=mBoi_flow_nominal_heaPlac7d62edc/1000*{0.1,1.1},
      dp=pumDP*{1.1,0.1}))
    "Performance data for heating water pumps";

  spawn_district_heating.Plants.CentralHeatingPlant heaPlac7d62edc(
    perHWPum=perHWPum_heaPlac7d62edc,
    mHW_flow_nominal=mHW_flow_nominal_heaPlac7d62edc,
    QBoi_flow_nominal=QBoi_nominal_heaPlac7d62edc,
    mMin_flow=mMin_flow_heaPlac7d62edc,
    mBoi_flow_nominal=mBoi_flow_nominal_heaPlac7d62edc,
    dpBoi_nominal=10000,
    delT_nominal(
      displayUnit="degC")=15,
    tWai=tWai_heaPlac7d62edc,
    // TODO: we're currently grabbing dpSetPoi from the Network instance -- need feedback to determine if that's the proper "home" for it
    dpSetPoi=dpSetPoi_disNet_1e8cfb72
    )
    "District heating plant."
    annotation (Placement(transformation(extent={{-70.0,30.0},{-50.0,50.0}})));
  //
  // End Model Instance for heaPlac7d62edc
  //


  
  //
  // Begin Model Instance for SpawnLoad_b8198b05
  // Source template: /model_connectors/load_connectors/templates/Spawn_Instance.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mLoaCoo_flow_nominal_SpawnLoad_b8198b05[SpawnLoad_b8198b05.nZon]={(-1*SpawnLoad_b8198b05.QCoo_flow_nominal[i]*(0.06)/1000) for i in 1:SpawnLoad_b8198b05.nZon};
  parameter Modelica.Units.SI.MassFlowRate mLoaHea_flow_nominal_SpawnLoad_b8198b05[SpawnLoad_b8198b05.nZon]={(SpawnLoad_b8198b05.QHea_flow_nominal[i]*(0.05)/1000) for i in 1:SpawnLoad_b8198b05.nZon};
  spawn_district_heating.Loads.B5a6b99ec37f4de7f94020090.building SpawnLoad_b8198b05(
    allowFlowReversal=true,
    mLoaCoo_flow_nominal=mLoaCoo_flow_nominal_SpawnLoad_b8198b05,
    mLoaHea_flow_nominal=mLoaHea_flow_nominal_SpawnLoad_b8198b05,
    nPorts_aHeaWat=1,
    nPorts_bHeaWat=1,
    nPorts_aChiWat=1,
    nPorts_bChiWat=1,
    have_pum=true)
    "Building spawn model"
    annotation (Placement(transformation(extent={{50.0,30.0},{70.0,50.0}})));
  //
  // End Model Instance for SpawnLoad_b8198b05
  //


  
  //
  // Begin Model Instance for heaInd_de5f7708
  // Source template: /model_connectors/energy_transfer_systems/templates/HeatingIndirect_Instance.mopt
  //
  // heating indirect instance
  spawn_district_heating.Substations.HeatingIndirect_5a6b99ec37f4de7f94020090 heaInd_de5f7708(
    allowFlowReversal1=true,
    allowFlowReversal2=true,
    show_T=true,
    redeclare package Medium=MediumW,
    mDis_flow_nominal=mDis_flow_nominal_0815b81f,
    mBui_flow_nominal=mBui_flow_nominal_0815b81f,
    dpValve_nominal=6000,
    dp1_nominal=500,
    dp2_nominal=500,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_0815b81f,
    T_a1_nominal=55+273.15,
    T_a2_nominal=35+273.15,
    k=0.1,
    Ti=60,
    reverseActing=true)
    annotation (Placement(transformation(extent={{10.0,30.0},{30.0,50.0}})));
  //
  // End Model Instance for heaInd_de5f7708
  //


  
  //
  // Begin Model Instance for etsColWatStub_ff41590e
  // Source template: /model_connectors/energy_transfer_systems/templates/EtsColdWaterStub_Instance.mopt
  //
  // TODO: move these components into a single component
  Buildings.Fluid.Sources.Boundary_pT supChiWat_etsColWatStub_ff41590e(
    redeclare package Medium=MediumW,
    use_T_in=true,
    nPorts=1)
    "Chilled water supply"
    annotation (Placement(transformation(extent={{-30.0,-50.0},{-10.0,-30.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinChiWat_etsColWatStub_ff41590e(
    redeclare package Medium=MediumW,
    p = 50000,
    nPorts=1)
    "Chilled water sink"
    annotation (Placement(transformation(extent={{10.0,-50.0},{30.0,-30.0}})));
  //
  // End Model Instance for etsColWatStub_ff41590e
  //


  

  // Model dependencies

  //
  // Begin Component Definitions for 5536dfd8
  // Source template: /model_connectors/couplings/templates/Network2Pipe_HeatingPlant/ComponentDefinitions.mopt
  //
  // TODO: This should not be here, it is entirely plant specific and should be moved elsewhere
  // but since it requires a connect statement we must put it here for now...
  Modelica.Blocks.Sources.BooleanConstant mPum_flow_5536dfd8(
    k=true)
    "Total heating water pump mass flow rate"
    annotation (Placement(transformation(extent={{-70.0,-10.0},{-50.0,10.0}})));
  // TODO: This should not be here, it is entirely plant specific and should be moved elsewhere
  // but since it requires a connect statement we must put it here for now...
  Modelica.Blocks.Sources.RealExpression TDisSetHeaWat_5536dfd8(
    each y=273.15+54)
    "District side heating water supply temperature set point."
    annotation (Placement(transformation(extent={{-30.0,-10.0},{-10.0,10.0}})));

  //
  // End Component Definitions for 5536dfd8
  //



  //
  // Begin Component Definitions for 0815b81f
  // Source template: /model_connectors/couplings/templates/Spawn_HeatingIndirect/ComponentDefinitions.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_0815b81f=SpawnLoad_b8198b05.disFloHea.m_flow_nominal*delHeaWatTemBui/delHeaWatTemDis
    "Nominal mass flow rate of primary (district) district heating side"; // TODO: Verify this is ok!
  parameter Modelica.Units.SI.MassFlowRate mBui_flow_nominal_0815b81f=SpawnLoad_b8198b05.terUni[1].mHeaWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district heating side"; // TODO: Verify this is ok!
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_0815b81f=SpawnLoad_b8198b05.QHea_flow_nominal[1]; // TODO: Verify this is ok!
  Modelica.Fluid.Sources.FixedBoundary pressure_source_0815b81f(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{10.0,-10.0},{30.0,10.0}})));
  // TODO: move THeaWatSet (and its connection) into a HeatingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression THeaWatSet_0815b81f(
    // y=40+273.15)
    y=273.15+40 )
    "Secondary loop (Building side) heating water setpoint temperature."
    //Dehardcode
    annotation (Placement(transformation(extent={{50.0,-10.0},{70.0,10.0}})));

  //
  // End Component Definitions for 0815b81f
  //



  //
  // Begin Component Definitions for c0a2ac14
  // Source template: /model_connectors/couplings/templates/Spawn_EtsColdWaterStub/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression TChiWatSup_c0a2ac14(
    y=
    //y=min(
      //SpawnLoad_b8198b05.terUni.T_aChiWat_nominal))
      280)
    "Chilled water supply temperature"
    annotation (Placement(transformation(extent={{-70.0,-50.0},{-50.0,-30.0}})));

  //
  // End Component Definitions for c0a2ac14
  //



  //
  // Begin Component Definitions for 1ce23fdf
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for heating indirect and network 2 pipe

  //
  // End Component Definitions for 1ce23fdf
  //



equation
  // Connections

  //
  // Begin Connect Statements for 5536dfd8
  // Source template: /model_connectors/couplings/templates/Network2Pipe_HeatingPlant/ConnectStatements.mopt
  //

  connect(heaPlac7d62edc.port_a,disNet_1e8cfb72.port_bDisRet)
    annotation (Line(points={{-35.15073941343428,38.5665369934935},{-15.15073941343428,38.5665369934935}},color={0,0,127}));
  connect(disNet_1e8cfb72.dp,heaPlac7d62edc.dpMea)
    annotation (Line(points={{-31.24597220614848,36.76472164473463},{-51.24597220614848,36.76472164473463}},color={0,0,127}));
  connect(heaPlac7d62edc.port_b,disNet_1e8cfb72.port_aDisSup)
    annotation (Line(points={{-43.758000083910225,42.210874722228276},{-23.758000083910233,42.210874722228276}},color={0,0,127}));
  connect(mPum_flow_5536dfd8.y,heaPlac7d62edc.on)
    annotation (Line(points={{-62.43016202652637,19.232830342482657},{-62.43016202652637,39.23283034248266}},color={0,0,127}));
  connect(TDisSetHeaWat_5536dfd8.y,heaPlac7d62edc.THeaSet)
    annotation (Line(points={{-24.578083869251827,29.184289273175956},{-44.57808386925183,29.184289273175956},{-44.57808386925183,49.184289273175956},{-64.57808386925183,49.184289273175956}},color={0,0,127}));

  //
  // End Connect Statements for 5536dfd8
  //



  //
  // Begin Connect Statements for 0815b81f
  // Source template: /model_connectors/couplings/templates/Spawn_HeatingIndirect/ConnectStatements.mopt
  //

  connect(SpawnLoad_b8198b05.ports_bHeaWat[1], heaInd_de5f7708.port_a2)
    annotation (Line(points={{42.08781086802111,32.64867523445355},{22.08781086802111,32.64867523445355}},color={0,0,127}));
  connect(heaInd_de5f7708.port_b2,SpawnLoad_b8198b05.ports_aHeaWat[1])
    annotation (Line(points={{45.81871372340356,34.99929519699094},{65.81871372340356,34.99929519699094}},color={0,0,127}));
  connect(pressure_source_0815b81f.ports[1], heaInd_de5f7708.port_b2)
    annotation (Line(points={{27.85821408958958,22.686638844101452},{27.85821408958958,42.68663884410145}},color={0,0,127}));
  connect(THeaWatSet_0815b81f.y,heaInd_de5f7708.TSetBuiSup)
    annotation (Line(points={{54.08458023649905,16.642748602247195},{34.08458023649905,16.642748602247195},{34.08458023649905,36.642748602247195},{14.08458023649905,36.642748602247195}},color={0,0,127}));

  //
  // End Connect Statements for 0815b81f
  //



  //
  // Begin Connect Statements for c0a2ac14
  // Source template: /model_connectors/couplings/templates/Spawn_EtsColdWaterStub/ConnectStatements.mopt
  //

  // spawn, ets cold water stub connections
  connect(TChiWatSup_c0a2ac14.y,supChiWat_etsColWatStub_ff41590e.T_in)
    annotation (Line(points={{-48.27973467545484,-43.601243343927536},{-28.27973467545484,-43.601243343927536}},color={0,0,127}));
  connect(SpawnLoad_b8198b05.ports_bChiWat[1],sinChiWat_etsColWatStub_ff41590e.ports[1])
    annotation (Line(points={{62.5073924134858,27.304105310307023},{42.5073924134858,27.304105310307023},{42.5073924134858,7.304105310307023},{42.5073924134858,-12.695894689692977},{42.5073924134858,-32.69589468969298},{22.507392413485803,-32.69589468969298}},color={0,0,127}));
  connect(supChiWat_etsColWatStub_ff41590e.ports[1],SpawnLoad_b8198b05.ports_aChiWat[1])
    annotation (Line(points={{-16.618731093422895,-14.759162537351912},{3.3812689065771053,-14.759162537351912},{3.3812689065771053,5.240837462648088},{3.3812689065771053,25.240837462648088},{23.381268906577105,25.240837462648088},{43.381268906577105,25.240837462648088},{43.381268906577105,45.24083746264809},{63.381268906577105,45.24083746264809}},color={0,0,127}));

  //
  // End Connect Statements for c0a2ac14
  //



  //
  // Begin Connect Statements for 1ce23fdf
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // heating indirect and network 2 pipe
  
  connect(disNet_1e8cfb72.ports_bCon[1],heaInd_de5f7708.port_a1)
    annotation (Line(points={{-1.0466225309130834,41.66604331475949},{18.953377469086917,41.66604331475949}},color={0,0,127}));
  connect(disNet_1e8cfb72.ports_aCon[1],heaInd_de5f7708.port_b1)
    annotation (Line(points={{-2.231784104944012,39.34825997556622},{17.768215895055988,39.34825997556622}},color={0,0,127}));

  //
  // End Connect Statements for 1ce23fdf
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