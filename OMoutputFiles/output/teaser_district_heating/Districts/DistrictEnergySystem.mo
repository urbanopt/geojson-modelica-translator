within teaser_district_heating.Districts;
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
  // Begin Model Instance for disNet_86cd77f9
  // Source template: /model_connectors/networks/templates/Network2Pipe_Instance.mopt
  //
parameter Integer nBui_disNet_86cd77f9=2;
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_disNet_86cd77f9=sum({
    heaInd_fa103f20.mDis_flow_nominal,
  heaInd_56d24392.mDis_flow_nominal})
    "Nominal mass flow rate of the distribution pump";
  parameter Modelica.Units.SI.MassFlowRate mCon_flow_nominal_disNet_86cd77f9[nBui_disNet_86cd77f9]={
    heaInd_fa103f20.mDis_flow_nominal,
  heaInd_56d24392.mDis_flow_nominal}
    "Nominal mass flow rate in each connection line";
  parameter Modelica.Units.SI.PressureDifference dpDis_nominal_disNet_86cd77f9[nBui_disNet_86cd77f9](
    each min=0,
    each displayUnit="Pa")=1/2 .* cat(
    1,
    {dp_nominal_disNet_86cd77f9*0.1},
    fill(
      dp_nominal_disNet_86cd77f9*0.9/(nBui_disNet_86cd77f9-1),
      nBui_disNet_86cd77f9-1))
    "Pressure drop between each connected building at nominal conditions (supply line)";
  parameter Modelica.Units.SI.PressureDifference dp_nominal_disNet_86cd77f9=dpSetPoi_disNet_86cd77f9+nBui_disNet_86cd77f9*7000
    "District network pressure drop";
  // NOTE: this differential pressure setpoint is currently utilized by plants elsewhere
  parameter Modelica.Units.SI.Pressure dpSetPoi_disNet_86cd77f9=50000
    "Differential pressure setpoint";

  Buildings.Experimental.DHC.Networks.Distribution2Pipe disNet_86cd77f9(
    redeclare final package Medium=MediumW,
    final nCon=nBui_disNet_86cd77f9,
    iConDpSen=nBui_disNet_86cd77f9,
    final mDis_flow_nominal=mDis_flow_nominal_disNet_86cd77f9,
    final mCon_flow_nominal=mCon_flow_nominal_disNet_86cd77f9,
    final allowFlowReversal=false,
    dpDis_nominal=dpDis_nominal_disNet_86cd77f9)
    "Distribution network."
    annotation (Placement(transformation(extent={{-30.0,80.0},{-10.0,90.0}})));
  //
  // End Model Instance for disNet_86cd77f9
  //


  
  //
  // Begin Model Instance for heaPlaa91d5909
  // Source template: /model_connectors/plants/templates/HeatingPlant_Instance.mopt
  //
  // heating plant instance
  parameter Modelica.Units.SI.MassFlowRate mHW_flow_nominal_heaPlaa91d5909=mBoi_flow_nominal_heaPlaa91d5909*heaPlaa91d5909.numBoi
    "Nominal heating water mass flow rate";
  parameter Modelica.Units.SI.MassFlowRate mBoi_flow_nominal_heaPlaa91d5909=QBoi_nominal_heaPlaa91d5909/(4200*heaPlaa91d5909.delT_nominal)
    "Nominal heating water mass flow rate";
  parameter Modelica.Units.SI.Power QBoi_nominal_heaPlaa91d5909=Q_flow_nominal_heaPlaa91d5909/heaPlaa91d5909.numBoi
    "Nominal heating capaciaty";
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_heaPlaa91d5909=1000000*2
    "Heating load";
  parameter Modelica.Units.SI.MassFlowRate mMin_flow_heaPlaa91d5909=0.2*mBoi_flow_nominal_heaPlaa91d5909
    "Minimum mass flow rate of single boiler";
  // controls
  parameter Modelica.Units.SI.Pressure pumDP=(heaPlaa91d5909.dpBoi_nominal+dpSetPoi_disNet_86cd77f9+50000)
    "Heating water pump pressure drop";
  parameter Modelica.Units.SI.Time tWai_heaPlaa91d5909=30
    "Waiting time";
  parameter Buildings.Fluid.Movers.Data.Generic perHWPum_heaPlaa91d5909(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=mBoi_flow_nominal_heaPlaa91d5909/1000*{0.1,1.1},
      dp=pumDP*{1.1,0.1}))
    "Performance data for heating water pumps";

  teaser_district_heating.Plants.CentralHeatingPlant heaPlaa91d5909(
    perHWPum=perHWPum_heaPlaa91d5909,
    mHW_flow_nominal=mHW_flow_nominal_heaPlaa91d5909,
    QBoi_flow_nominal=QBoi_nominal_heaPlaa91d5909,
    mMin_flow=mMin_flow_heaPlaa91d5909,
    mBoi_flow_nominal=mBoi_flow_nominal_heaPlaa91d5909,
    dpBoi_nominal=10000,
    delT_nominal(
      displayUnit="degC")=15,
    tWai=tWai_heaPlaa91d5909,
    // TODO: we're currently grabbing dpSetPoi from the Network instance -- need feedback to determine if that's the proper "home" for it
    dpSetPoi=dpSetPoi_disNet_86cd77f9
    )
    "District heating plant."
    annotation (Placement(transformation(extent={{-70.0,70.0},{-50.0,90.0}})));
  //
  // End Model Instance for heaPlaa91d5909
  //


  
  //
  // Begin Model Instance for TeaserLoad_39de86a4
  // Source template: /model_connectors/load_connectors/templates/Teaser_Instance.mopt
  //
  teaser_district_heating.Loads.B5a6b99ec37f4de7f94020090.building TeaserLoad_39de86a4(
    nPorts_aHeaWat=1,
    nPorts_bHeaWat=1,
    nPorts_aChiWat=1,
    nPorts_bChiWat=1)
    "Building with thermal loads as TEASER zones"
    annotation (Placement(transformation(extent={{50.0,70.0},{70.0,90.0}})));
  //
  // End Model Instance for TeaserLoad_39de86a4
  //


  
  //
  // Begin Model Instance for heaInd_fa103f20
  // Source template: /model_connectors/energy_transfer_systems/templates/HeatingIndirect_Instance.mopt
  //
  // heating indirect instance
  teaser_district_heating.Substations.HeatingIndirect_5a6b99ec37f4de7f94020090 heaInd_fa103f20(
    allowFlowReversal1=true,
    allowFlowReversal2=true,
    show_T=true,
    redeclare package Medium=MediumW,
    mDis_flow_nominal=mDis_flow_nominal_daa1ab82,
    mBui_flow_nominal=mBui_flow_nominal_daa1ab82,
    dpValve_nominal=6000,
    dp1_nominal=500,
    dp2_nominal=500,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_daa1ab82,
    T_a1_nominal=55+273.15,
    T_a2_nominal=35+273.15,
    k=0.1,
    Ti=60,
    reverseActing=true)
    annotation (Placement(transformation(extent={{10.0,70.0},{30.0,90.0}})));
  //
  // End Model Instance for heaInd_fa103f20
  //


  
  //
  // Begin Model Instance for etsColWatStub_9be4c379
  // Source template: /model_connectors/energy_transfer_systems/templates/EtsColdWaterStub_Instance.mopt
  //
  // TODO: move these components into a single component
  Buildings.Fluid.Sources.Boundary_pT supChiWat_etsColWatStub_9be4c379(
    redeclare package Medium=MediumW,
    use_T_in=true,
    nPorts=1)
    "Chilled water supply"
    annotation (Placement(transformation(extent={{-70.0,-90.0},{-50.0,-70.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinChiWat_etsColWatStub_9be4c379(
    redeclare package Medium=MediumW,
    nPorts=1)
    "Chilled water sink"
    annotation (Placement(transformation(extent={{-30.0,-90.0},{-10.0,-70.0}})));
  //
  // End Model Instance for etsColWatStub_9be4c379
  //


  
  //
  // Begin Model Instance for TeaserLoad_0f0b1663
  // Source template: /model_connectors/load_connectors/templates/Teaser_Instance.mopt
  //
  teaser_district_heating.Loads.B5a72287837f4de77124f946a.building TeaserLoad_0f0b1663(
    nPorts_aHeaWat=1,
    nPorts_bHeaWat=1,
    nPorts_aChiWat=1,
    nPorts_bChiWat=1)
    "Building with thermal loads as TEASER zones"
    annotation (Placement(transformation(extent={{50.0,30.0},{70.0,50.0}})));
  //
  // End Model Instance for TeaserLoad_0f0b1663
  //


  
  //
  // Begin Model Instance for heaInd_56d24392
  // Source template: /model_connectors/energy_transfer_systems/templates/HeatingIndirect_Instance.mopt
  //
  // heating indirect instance
  teaser_district_heating.Substations.HeatingIndirect_5a72287837f4de77124f946a heaInd_56d24392(
    allowFlowReversal1=true,
    allowFlowReversal2=true,
    show_T=true,
    redeclare package Medium=MediumW,
    mDis_flow_nominal=mDis_flow_nominal_859a4b0c,
    mBui_flow_nominal=mBui_flow_nominal_859a4b0c,
    dpValve_nominal=6000,
    dp1_nominal=500,
    dp2_nominal=500,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_859a4b0c,
    T_a1_nominal=55+273.15,
    T_a2_nominal=35+273.15,
    k=0.1,
    Ti=60,
    reverseActing=true)
    annotation (Placement(transformation(extent={{10.0,30.0},{30.0,50.0}})));
  //
  // End Model Instance for heaInd_56d24392
  //


  
  //
  // Begin Model Instance for etsColWatStub_ce6dff20
  // Source template: /model_connectors/energy_transfer_systems/templates/EtsColdWaterStub_Instance.mopt
  //
  // TODO: move these components into a single component
  Buildings.Fluid.Sources.Boundary_pT supChiWat_etsColWatStub_ce6dff20(
    redeclare package Medium=MediumW,
    use_T_in=true,
    nPorts=1)
    "Chilled water supply"
    annotation (Placement(transformation(extent={{10.0,-90.0},{30.0,-70.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinChiWat_etsColWatStub_ce6dff20(
    redeclare package Medium=MediumW,
    nPorts=1)
    "Chilled water sink"
    annotation (Placement(transformation(extent={{50.0,-90.0},{70.0,-70.0}})));
  //
  // End Model Instance for etsColWatStub_ce6dff20
  //


  

  // Model dependencies

  //
  // Begin Component Definitions for 46131fbe
  // Source template: /model_connectors/couplings/templates/Network2Pipe_HeatingPlant/ComponentDefinitions.mopt
  //
  // TODO: This should not be here, it is entirely plant specific and should be moved elsewhere
  // but since it requires a connect statement we must put it here for now...
  Modelica.Blocks.Sources.BooleanConstant mPum_flow_46131fbe(
    k=true)
    "Total heating water pump mass flow rate"
    annotation (Placement(transformation(extent={{-70.0,-10.0},{-50.0,10.0}})));
  // TODO: This should not be here, it is entirely plant specific and should be moved elsewhere
  // but since it requires a connect statement we must put it here for now...
  Modelica.Blocks.Sources.RealExpression TDisSetHeaWat_46131fbe(
    each y=273.15+54)
    "District side heating water supply temperature set point."
    annotation (Placement(transformation(extent={{-30.0,-10.0},{-10.0,10.0}})));

  //
  // End Component Definitions for 46131fbe
  //



  //
  // Begin Component Definitions for daa1ab82
  // Source template: /model_connectors/couplings/templates/Teaser_HeatingIndirect/ComponentDefinitions.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_daa1ab82=TeaserLoad_39de86a4.disFloHea.m_flow_nominal*delHeaWatTemBui/delHeaWatTemDis
    "Nominal mass flow rate of primary (district) district heating side"; // TODO: Verify this is ok!
  parameter Modelica.Units.SI.MassFlowRate mBui_flow_nominal_daa1ab82=TeaserLoad_39de86a4.terUni[1].mHeaWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district heating side"; // TODO: Verify this is ok!
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_daa1ab82=TeaserLoad_39de86a4.terUni[1].QHea_flow_nominal; // TODO: Verify this is ok!
  Modelica.Fluid.Sources.FixedBoundary pressure_source_daa1ab82(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{10.0,-10.0},{30.0,10.0}})));
  // TODO: move THeaWatSet (and its connection) into a HeatingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression THeaWatSet_daa1ab82(
    // y=40+273.15)
    y=273.15+40)
    "Secondary loop (Building side) heating water setpoint temperature."
    //Dehardcode
    annotation (Placement(transformation(extent={{50.0,-10.0},{70.0,10.0}})));

  //
  // End Component Definitions for daa1ab82
  //



  //
  // Begin Component Definitions for a61e8eb1
  // Source template: /model_connectors/couplings/templates/Teaser_EtsColdWaterStub/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression TChiWatSup_a61e8eb1(
    y=min(
      TeaserLoad_39de86a4.terUni.T_aChiWat_nominal))
    "Chilled water supply temperature"
    annotation (Placement(transformation(extent={{-70.0,-50.0},{-50.0,-30.0}})));

  //
  // End Component Definitions for a61e8eb1
  //



  //
  // Begin Component Definitions for 93acb1a1
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for heating indirect and network 2 pipe

  //
  // End Component Definitions for 93acb1a1
  //



  //
  // Begin Component Definitions for 859a4b0c
  // Source template: /model_connectors/couplings/templates/Teaser_HeatingIndirect/ComponentDefinitions.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_859a4b0c=TeaserLoad_0f0b1663.disFloHea.m_flow_nominal*delHeaWatTemBui/delHeaWatTemDis
    "Nominal mass flow rate of primary (district) district heating side"; // TODO: Verify this is ok!
  parameter Modelica.Units.SI.MassFlowRate mBui_flow_nominal_859a4b0c=TeaserLoad_0f0b1663.terUni[1].mHeaWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district heating side"; // TODO: Verify this is ok!
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_859a4b0c=TeaserLoad_0f0b1663.terUni[1].QHea_flow_nominal; // TODO: Verify this is ok!
  Modelica.Fluid.Sources.FixedBoundary pressure_source_859a4b0c(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{-30.0,-50.0},{-10.0,-30.0}})));
  // TODO: move THeaWatSet (and its connection) into a HeatingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression THeaWatSet_859a4b0c(
    // y=40+273.15)
    y=273.15+40)
    "Secondary loop (Building side) heating water setpoint temperature."
    //Dehardcode
    annotation (Placement(transformation(extent={{10.0,-50.0},{30.0,-30.0}})));

  //
  // End Component Definitions for 859a4b0c
  //



  //
  // Begin Component Definitions for b1500b5c
  // Source template: /model_connectors/couplings/templates/Teaser_EtsColdWaterStub/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression TChiWatSup_b1500b5c(
    y=min(
      TeaserLoad_0f0b1663.terUni.T_aChiWat_nominal))
    "Chilled water supply temperature"
    annotation (Placement(transformation(extent={{50.0,-50.0},{70.0,-30.0}})));

  //
  // End Component Definitions for b1500b5c
  //



  //
  // Begin Component Definitions for c314a637
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for heating indirect and network 2 pipe

  //
  // End Component Definitions for c314a637
  //



equation
  // Connections

  //
  // Begin Connect Statements for 46131fbe
  // Source template: /model_connectors/couplings/templates/Network2Pipe_HeatingPlant/ConnectStatements.mopt
  //

  connect(heaPlaa91d5909.port_a,disNet_86cd77f9.port_bDisRet)
    annotation (Line(points={{-49.222366074993985,88.87098359571465},{-29.222366074993985,88.87098359571465}},color={0,0,127}));
  connect(disNet_86cd77f9.dp,heaPlaa91d5909.dpMea)
    annotation (Line(points={{-30.835360154130925,85.01926833146896},{-50.835360154130925,85.01926833146896}},color={0,0,127}));
  connect(heaPlaa91d5909.port_b,disNet_86cd77f9.port_aDisSup)
    annotation (Line(points={{-32.81882279376418,77.68489958422977},{-12.818822793764184,77.68489958422977}},color={0,0,127}));
  connect(mPum_flow_46131fbe.y,heaPlaa91d5909.on)
    annotation (Line(points={{-67.8033105635308,25.453225498279835},{-67.8033105635308,45.453225498279835},{-67.8033105635308,65.45322549827983},{-67.8033105635308,85.45322549827983}},color={0,0,127}));
  connect(TDisSetHeaWat_46131fbe.y,heaPlaa91d5909.THeaSet)
    annotation (Line(points={{-12.30368941396199,24.73343164264635},{-12.30368941396199,44.73343164264635},{-12.30368941396199,64.73343164264635},{-32.303689413962,64.73343164264635},{-32.303689413962,84.73343164264635},{-52.303689413962,84.73343164264635}},color={0,0,127}));

  //
  // End Connect Statements for 46131fbe
  //



  //
  // Begin Connect Statements for daa1ab82
  // Source template: /model_connectors/couplings/templates/Teaser_HeatingIndirect/ConnectStatements.mopt
  //

  connect(TeaserLoad_39de86a4.ports_bHeaWat[1], heaInd_fa103f20.port_a2)
    annotation (Line(points={{42.71788242975606,81.08031276937882},{22.717882429756074,81.08031276937882}},color={0,0,127}));
  connect(heaInd_fa103f20.port_b2,TeaserLoad_39de86a4.ports_aHeaWat[1])
    annotation (Line(points={{48.772342434044134,87.9939022649821},{68.77234243404413,87.9939022649821}},color={0,0,127}));
  connect(pressure_source_daa1ab82.ports[1], heaInd_fa103f20.port_b2)
    annotation (Line(points={{28.07509176136783,18.288628637350868},{8.07509176136783,18.288628637350868},{8.07509176136783,38.28862863735087},{8.07509176136783,58.28862863735086},{8.07509176136783,78.28862863735085},{28.07509176136783,78.28862863735085}},color={0,0,127}));
  connect(THeaWatSet_daa1ab82.y,heaInd_fa103f20.TSetBuiSup)
    annotation (Line(points={{68.02538967164668,21.48464328498784},{48.02538967164668,21.48464328498784},{48.02538967164668,41.48464328498784},{48.02538967164668,61.48464328498784},{48.02538967164668,81.48464328498784},{28.025389671646664,81.48464328498784}},color={0,0,127}));

  //
  // End Connect Statements for daa1ab82
  //



  //
  // Begin Connect Statements for a61e8eb1
  // Source template: /model_connectors/couplings/templates/Teaser_EtsColdWaterStub/ConnectStatements.mopt
  //

  // teaser, ets cold water stub connections
  connect(TChiWatSup_a61e8eb1.y,supChiWat_etsColWatStub_9be4c379.T_in)
    annotation (Line(points={{-66.79604871240036,-64.76810920574874},{-66.79604871240036,-84.76810920574874}},color={0,0,127}));
  connect(supChiWat_etsColWatStub_9be4c379.ports[1],TeaserLoad_39de86a4.ports_aChiWat[1])
    annotation (Line(points={{-51.40199222338295,-65.6091930148593},{-31.401992223382948,-65.6091930148593},{-31.401992223382948,-45.6091930148593},{-31.401992223382948,-25.6091930148593},{-31.401992223382948,-5.609193014859315},{-31.401992223382948,14.390806985140685},{-31.401992223382948,34.390806985140685},{-31.401992223382948,54.390806985140685},{-11.401992223382948,54.390806985140685},{8.598007776617052,54.390806985140685},{28.598007776617052,54.390806985140685},{48.59800777661704,54.390806985140685},{48.59800777661704,74.39080698514069},{68.59800777661704,74.39080698514069}},color={0,0,127}));
  connect(sinChiWat_etsColWatStub_9be4c379.ports[1],TeaserLoad_39de86a4.ports_bChiWat[1])
    annotation (Line(points={{-17.64548297026701,-69.80469465409467},{2.354517029732989,-69.80469465409467},{2.354517029732989,-49.804694654094675},{2.354517029732989,-29.804694654094675},{2.354517029732989,-9.804694654094675},{2.354517029732989,10.195305345905325},{2.354517029732989,30.195305345905325},{2.354517029732989,50.19530534590532},{22.35451702973299,50.19530534590532},{42.35451702973299,50.19530534590532},{42.35451702973299,70.19530534590533},{62.35451702973299,70.19530534590533}},color={0,0,127}));

  //
  // End Connect Statements for a61e8eb1
  //



  //
  // Begin Connect Statements for 93acb1a1
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // heating indirect and network 2 pipe
  
  connect(disNet_86cd77f9.ports_bCon[1],heaInd_fa103f20.port_a1)
    annotation (Line(points={{8.027452827552096,74.88825806533},{28.027452827552096,74.88825806533}},color={0,0,127}));
  connect(disNet_86cd77f9.ports_aCon[1],heaInd_fa103f20.port_b1)
    annotation (Line(points={{4.177180793414948,72.43076997955768},{24.177180793414948,72.43076997955768}},color={0,0,127}));

  //
  // End Connect Statements for 93acb1a1
  //



  //
  // Begin Connect Statements for 859a4b0c
  // Source template: /model_connectors/couplings/templates/Teaser_HeatingIndirect/ConnectStatements.mopt
  //

  connect(TeaserLoad_0f0b1663.ports_bHeaWat[1], heaInd_56d24392.port_a2)
    annotation (Line(points={{38.864893620337085,48.647186743327374},{18.864893620337085,48.647186743327374}},color={0,0,127}));
  connect(heaInd_56d24392.port_b2,TeaserLoad_0f0b1663.ports_aHeaWat[1])
    annotation (Line(points={{35.31298194572405,32.68521195526499},{55.31298194572403,32.68521195526499}},color={0,0,127}));
  connect(pressure_source_859a4b0c.ports[1], heaInd_56d24392.port_b2)
    annotation (Line(points={{-16.04382010550279,-10.409894220636133},{3.956179894497211,-10.409894220636133},{3.956179894497211,9.590105779363867},{3.956179894497211,29.590105779363867},{3.956179894497211,49.59010577936387},{23.95617989449721,49.59010577936387}},color={0,0,127}));
  connect(THeaWatSet_859a4b0c.y,heaInd_56d24392.TSetBuiSup)
    annotation (Line(points={{24.726594306613094,-12.167047069671156},{4.726594306613094,-12.167047069671156},{4.726594306613094,7.832952930328844},{4.726594306613094,27.832952930328844},{4.726594306613094,47.83295293032885},{24.726594306613094,47.83295293032885}},color={0,0,127}));

  //
  // End Connect Statements for 859a4b0c
  //



  //
  // Begin Connect Statements for b1500b5c
  // Source template: /model_connectors/couplings/templates/Teaser_EtsColdWaterStub/ConnectStatements.mopt
  //

  // teaser, ets cold water stub connections
  connect(TChiWatSup_b1500b5c.y,supChiWat_etsColWatStub_ce6dff20.T_in)
    annotation (Line(points={{62.72720589106606,-61.98542835789647},{42.72720589106606,-61.98542835789647},{42.72720589106606,-81.98542835789647},{22.727205891066063,-81.98542835789647}},color={0,0,127}));
  connect(supChiWat_etsColWatStub_ce6dff20.ports[1],TeaserLoad_0f0b1663.ports_aChiWat[1])
    annotation (Line(points={{17.450940135237516,-63.87812934172956},{37.450940135237516,-63.87812934172956},{37.450940135237516,-43.87812934172956},{37.450940135237516,-23.87812934172956},{37.450940135237516,-3.8781293417295473},{37.450940135237516,16.121870658270453},{37.450940135237516,36.12187065827045},{57.450940135237516,36.12187065827045}},color={0,0,127}));
  connect(sinChiWat_etsColWatStub_ce6dff20.ports[1],TeaserLoad_0f0b1663.ports_bChiWat[1])
    annotation (Line(points={{67.695155156595,-54.64733782474019},{47.69515515659501,-54.64733782474019},{47.69515515659501,-34.64733782474019},{47.69515515659501,-14.647337824740191},{47.69515515659501,5.352662175259809},{47.69515515659501,25.35266217525981},{47.69515515659501,45.35266217525981},{67.695155156595,45.35266217525981}},color={0,0,127}));

  //
  // End Connect Statements for b1500b5c
  //



  //
  // Begin Connect Statements for c314a637
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // heating indirect and network 2 pipe
  
  connect(disNet_86cd77f9.ports_bCon[2],heaInd_56d24392.port_a1)
    annotation (Line(points={{-21.71440551073951,60.03530146199461},{-21.71440551073951,40.03530146199461},{-1.7144055107395104,40.03530146199461},{18.28559448926049,40.03530146199461}},color={0,0,127}));
  connect(disNet_86cd77f9.ports_aCon[2],heaInd_56d24392.port_b1)
    annotation (Line(points={{-14.756465424782874,51.09469966316962},{-14.756465424782874,31.09469966316962},{5.243534575217126,31.09469966316962},{25.243534575217126,31.09469966316962}},color={0,0,127}));

  //
  // End Connect Statements for c314a637
  //




annotation(
  experiment(
    StopTime=86400,
    Interval=3600,
    Tolerance=1e-06),
  Diagram(
    coordinateSystem(
      preserveAspectRatio=false,
      extent={{-90.0,-110.0},{90.0,110.0}})),
  Documentation(
    revisions="<html>
 <li>
 May 10, 2020: Hagar Elarga<br/>
Updated implementation to handle template needed for GeoJSON to Modelica.
</li>
</html>"));
end DistrictEnergySystem;