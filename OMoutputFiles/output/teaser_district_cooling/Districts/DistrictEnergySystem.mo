within teaser_district_cooling.Districts;
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
  // Begin Model Instance for disNet_9bd50e4a
  // Source template: /model_connectors/networks/templates/Network2Pipe_Instance.mopt
  //
parameter Integer nBui_disNet_9bd50e4a=2;
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_disNet_9bd50e4a=sum({
    cooInd_6e4db825.mDis_flow_nominal,
  cooInd_7f48d218.mDis_flow_nominal})
    "Nominal mass flow rate of the distribution pump";
  parameter Modelica.Units.SI.MassFlowRate mCon_flow_nominal_disNet_9bd50e4a[nBui_disNet_9bd50e4a]={
    cooInd_6e4db825.mDis_flow_nominal,
  cooInd_7f48d218.mDis_flow_nominal}
    "Nominal mass flow rate in each connection line";
  parameter Modelica.Units.SI.PressureDifference dpDis_nominal_disNet_9bd50e4a[nBui_disNet_9bd50e4a](
    each min=0,
    each displayUnit="Pa")=1/2 .* cat(
    1,
    {dp_nominal_disNet_9bd50e4a*0.1},
    fill(
      dp_nominal_disNet_9bd50e4a*0.9/(nBui_disNet_9bd50e4a-1),
      nBui_disNet_9bd50e4a-1))
    "Pressure drop between each connected building at nominal conditions (supply line)";
  parameter Modelica.Units.SI.PressureDifference dp_nominal_disNet_9bd50e4a=dpSetPoi_disNet_9bd50e4a+nBui_disNet_9bd50e4a*7000
    "District network pressure drop";
  // NOTE: this differential pressure setpoint is currently utilized by plants elsewhere
  parameter Modelica.Units.SI.Pressure dpSetPoi_disNet_9bd50e4a=50000
    "Differential pressure setpoint";

  Buildings.Experimental.DHC.Networks.Distribution2Pipe disNet_9bd50e4a(
    redeclare final package Medium=MediumW,
    final nCon=nBui_disNet_9bd50e4a,
    iConDpSen=nBui_disNet_9bd50e4a,
    final mDis_flow_nominal=mDis_flow_nominal_disNet_9bd50e4a,
    final mCon_flow_nominal=mCon_flow_nominal_disNet_9bd50e4a,
    final allowFlowReversal=false,
    dpDis_nominal=dpDis_nominal_disNet_9bd50e4a)
    "Distribution network."
    annotation (Placement(transformation(extent={{-30.0,80.0},{-10.0,90.0}})));
  //
  // End Model Instance for disNet_9bd50e4a
  //


  
  //
  // Begin Model Instance for cooPla_e68f0b80
  // Source template: /model_connectors/plants/templates/CoolingPlant_Instance.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mCHW_flow_nominal_cooPla_e68f0b80=cooPla_e68f0b80.numChi*(cooPla_e68f0b80.perChi.mEva_flow_nominal)
    "Nominal chilled water mass flow rate";
  parameter Modelica.Units.SI.MassFlowRate mCW_flow_nominal_cooPla_e68f0b80=cooPla_e68f0b80.perChi.mCon_flow_nominal
    "Nominal condenser water mass flow rate";
  parameter Modelica.Units.SI.PressureDifference dpCHW_nominal_cooPla_e68f0b80=44.8*1000
    "Nominal chilled water side pressure";
  parameter Modelica.Units.SI.PressureDifference dpCW_nominal_cooPla_e68f0b80=46.2*1000
    "Nominal condenser water side pressure";
  parameter Modelica.Units.SI.Power QEva_nominal_cooPla_e68f0b80=mCHW_flow_nominal_cooPla_e68f0b80*4200*(5-14)
    "Nominal cooling capaciaty (Negative means cooling)";
  parameter Modelica.Units.SI.MassFlowRate mMin_flow_cooPla_e68f0b80=0.2*mCHW_flow_nominal_cooPla_e68f0b80/cooPla_e68f0b80.numChi
    "Minimum mass flow rate of single chiller";
  // control settings
  parameter Modelica.Units.SI.Pressure dpSetPoi_cooPla_e68f0b80=70000
    "Differential pressure setpoint";
  parameter Modelica.Units.SI.Pressure pumDP_cooPla_e68f0b80=dpCHW_nominal_cooPla_e68f0b80+dpSetPoi_cooPla_e68f0b80+200000;
  parameter Modelica.Units.SI.Time tWai_cooPla_e68f0b80=30
    "Waiting time";
  // pumps
  parameter Buildings.Fluid.Movers.Data.Generic perCHWPum_cooPla_e68f0b80(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=((mCHW_flow_nominal_cooPla_e68f0b80/2)/1000)*{0.1,1,1.2},
      dp=pumDP_cooPla_e68f0b80*{1.2,1,0.1}))
    "Performance data for chilled water pumps";
  parameter Buildings.Fluid.Movers.Data.Generic perCWPum_cooPla_e68f0b80(
    pressure=Buildings.Fluid.Movers.BaseClasses.Characteristics.flowParameters(
      V_flow=mCW_flow_nominal_cooPla_e68f0b80/1000*{0.2,0.6,1.0,1.2},
      dp=(dpCW_nominal_cooPla_e68f0b80+60000+6000)*{1.2,1.1,1.0,0.6}))
    "Performance data for condenser water pumps";


  Modelica.Blocks.Sources.RealExpression TSetChiWatDis_cooPla_e68f0b80(
    y=5+273.15)
    "Chilled water supply temperature set point on district level."
    annotation (Placement(transformation(extent={{10.0,-50.0},{30.0,-30.0}})));
  Modelica.Blocks.Sources.BooleanConstant on_cooPla_e68f0b80
    "On signal of the plant"
    annotation (Placement(transformation(extent={{50.0,-50.0},{70.0,-30.0}})));

  teaser_district_cooling.Plants.CentralCoolingPlant cooPla_e68f0b80(
    redeclare Buildings.Fluid.Chillers.Data.ElectricEIR.ElectricEIRChiller_Carrier_19EX_5208kW_6_88COP_Vanes perChi,
    perCHWPum=perCHWPum_cooPla_e68f0b80,
    perCWPum=perCWPum_cooPla_e68f0b80,
    mCHW_flow_nominal=mCHW_flow_nominal_cooPla_e68f0b80,
    dpCHW_nominal=dpCHW_nominal_cooPla_e68f0b80,
    QEva_nominal=QEva_nominal_cooPla_e68f0b80,
    mMin_flow=mMin_flow_cooPla_e68f0b80,
    mCW_flow_nominal=mCW_flow_nominal_cooPla_e68f0b80,
    dpCW_nominal=dpCW_nominal_cooPla_e68f0b80,
    TAirInWB_nominal=298.7,
    TCW_nominal=308.15,
    TMin=288.15,
    tWai=tWai_cooPla_e68f0b80,
    dpSetPoi=dpSetPoi_cooPla_e68f0b80
    )
    "District cooling plant."
    annotation (Placement(transformation(extent={{-70.0,70.0},{-50.0,90.0}})));
  //
  // End Model Instance for cooPla_e68f0b80
  //


  
  //
  // Begin Model Instance for TeaserLoad_67f392ce
  // Source template: /model_connectors/load_connectors/templates/Teaser_Instance.mopt
  //
  teaser_district_cooling.Loads.B5a6b99ec37f4de7f94020090.building TeaserLoad_67f392ce(
    nPorts_aHeaWat=1,
    nPorts_bHeaWat=1,
    nPorts_aChiWat=1,
    nPorts_bChiWat=1)
    "Building with thermal loads as TEASER zones"
    annotation (Placement(transformation(extent={{50.0,70.0},{70.0,90.0}})));
  //
  // End Model Instance for TeaserLoad_67f392ce
  //


  
  //
  // Begin Model Instance for cooInd_6e4db825
  // Source template: /model_connectors/energy_transfer_systems/templates/CoolingIndirect_Instance.mopt
  //
  // cooling indirect instance
  teaser_district_cooling.Substations.CoolingIndirect_5a6b99ec37f4de7f94020090 cooInd_6e4db825(
    redeclare package Medium=MediumW,
    allowFlowReversal1=true,
    allowFlowReversal2=true,
    mDis_flow_nominal=mDis_flow_nominal_5efcb6f3,
    mBui_flow_nominal=mBui_flow_nominal_5efcb6f3,
    dp1_nominal=500,
    dp2_nominal=500,
    dpValve_nominal=7000,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_5efcb6f3,
    // TODO: dehardcode the nominal temperatures?
    T_a1_nominal=273.15+5,
    T_a2_nominal=273.15+13)
    "Indirect cooling energy transfer station ETS."
    annotation (Placement(transformation(extent={{10.0,70.0},{30.0,90.0}})));
  //
  // End Model Instance for cooInd_6e4db825
  //


  
  //
  // Begin Model Instance for etsHotWatStub_7b28baa9
  // Source template: /model_connectors/energy_transfer_systems/templates/EtsHotWaterStub_Instance.mopt
  //
  // TODO: move these components into a single component
  Buildings.Fluid.Sources.Boundary_pT supHeaWat_etsHotWatStub_7b28baa9(
    redeclare package Medium=MediumW,
    use_T_in=true,
    nPorts=1)
    "Heating water supply"
    annotation (Placement(transformation(extent={{-70.0,-90.0},{-50.0,-70.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinHeaWat_etsHotWatStub_7b28baa9(
    redeclare package Medium=MediumW,
    nPorts=1)
    "Heating water sink"
    annotation (Placement(transformation(extent={{-30.0,-90.0},{-10.0,-70.0}})));
  //
  // End Model Instance for etsHotWatStub_7b28baa9
  //


  
  //
  // Begin Model Instance for TeaserLoad_b55dcf3b
  // Source template: /model_connectors/load_connectors/templates/Teaser_Instance.mopt
  //
  teaser_district_cooling.Loads.B5a72287837f4de77124f946a.building TeaserLoad_b55dcf3b(
    nPorts_aHeaWat=1,
    nPorts_bHeaWat=1,
    nPorts_aChiWat=1,
    nPorts_bChiWat=1)
    "Building with thermal loads as TEASER zones"
    annotation (Placement(transformation(extent={{50.0,30.0},{70.0,50.0}})));
  //
  // End Model Instance for TeaserLoad_b55dcf3b
  //


  
  //
  // Begin Model Instance for cooInd_7f48d218
  // Source template: /model_connectors/energy_transfer_systems/templates/CoolingIndirect_Instance.mopt
  //
  // cooling indirect instance
  teaser_district_cooling.Substations.CoolingIndirect_5a72287837f4de77124f946a cooInd_7f48d218(
    redeclare package Medium=MediumW,
    allowFlowReversal1=true,
    allowFlowReversal2=true,
    mDis_flow_nominal=mDis_flow_nominal_4302ba1f,
    mBui_flow_nominal=mBui_flow_nominal_4302ba1f,
    dp1_nominal=500,
    dp2_nominal=500,
    dpValve_nominal=7000,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_4302ba1f,
    // TODO: dehardcode the nominal temperatures?
    T_a1_nominal=273.15+5,
    T_a2_nominal=273.15+13)
    "Indirect cooling energy transfer station ETS."
    annotation (Placement(transformation(extent={{10.0,30.0},{30.0,50.0}})));
  //
  // End Model Instance for cooInd_7f48d218
  //


  
  //
  // Begin Model Instance for etsHotWatStub_414cc5a1
  // Source template: /model_connectors/energy_transfer_systems/templates/EtsHotWaterStub_Instance.mopt
  //
  // TODO: move these components into a single component
  Buildings.Fluid.Sources.Boundary_pT supHeaWat_etsHotWatStub_414cc5a1(
    redeclare package Medium=MediumW,
    use_T_in=true,
    nPorts=1)
    "Heating water supply"
    annotation (Placement(transformation(extent={{10.0,-90.0},{30.0,-70.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinHeaWat_etsHotWatStub_414cc5a1(
    redeclare package Medium=MediumW,
    nPorts=1)
    "Heating water sink"
    annotation (Placement(transformation(extent={{50.0,-90.0},{70.0,-70.0}})));
  //
  // End Model Instance for etsHotWatStub_414cc5a1
  //


  

  // Model dependencies

  //
  // Begin Component Definitions for 2079ab67
  // Source template: /model_connectors/couplings/templates/Network2Pipe_CoolingPlant/ComponentDefinitions.mopt
  //
  // No components for pipe and cooling plant

  //
  // End Component Definitions for 2079ab67
  //



  //
  // Begin Component Definitions for 5efcb6f3
  // Source template: /model_connectors/couplings/templates/Teaser_CoolingIndirect/ComponentDefinitions.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_5efcb6f3=TeaserLoad_67f392ce.disFloCoo.m_flow_nominal*delChiWatTemBui/delChiWatTemDis
    "Nominal mass flow rate of primary (district) district cooling side"; // TODO: verify this is ok!
  parameter Modelica.Units.SI.MassFlowRate mBui_flow_nominal_5efcb6f3=TeaserLoad_67f392ce.terUni[1].mChiWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district cooling side"; // TODO: verify this is ok!
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_5efcb6f3=-1*TeaserLoad_67f392ce.terUni[1].QHea_flow_nominal; // TODO: verify this is ok!
  Modelica.Fluid.Sources.FixedBoundary pressure_source_5efcb6f3(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{-70.0,-10.0},{-50.0,10.0}})));
  // TODO: move TChiWatSet (and its connection) into a CoolingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression TChiWatSet_5efcb6f3(
    y=7+273.15)
    //Dehardcode
    "Primary loop (district side) chilled water setpoint temperature."
    annotation (Placement(transformation(extent={{-30.0,-10.0},{-10.0,10.0}})));

  //
  // End Component Definitions for 5efcb6f3
  //



  //
  // Begin Component Definitions for 14b53aa2
  // Source template: /model_connectors/couplings/templates/Teaser_EtsHotWaterStub/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression THeaWatSup_14b53aa2(
    y=max(
      TeaserLoad_67f392ce.terUni.T_aHeaWat_nominal))
    "Heating water supply temperature"
    annotation (Placement(transformation(extent={{10.0,-10.0},{30.0,10.0}})));

  //
  // End Component Definitions for 14b53aa2
  //



  //
  // Begin Component Definitions for 569b4f20
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for cooling indirect and network 2 pipe

  //
  // End Component Definitions for 569b4f20
  //



  //
  // Begin Component Definitions for 4302ba1f
  // Source template: /model_connectors/couplings/templates/Teaser_CoolingIndirect/ComponentDefinitions.mopt
  //
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_4302ba1f=TeaserLoad_b55dcf3b.disFloCoo.m_flow_nominal*delChiWatTemBui/delChiWatTemDis
    "Nominal mass flow rate of primary (district) district cooling side"; // TODO: verify this is ok!
  parameter Modelica.Units.SI.MassFlowRate mBui_flow_nominal_4302ba1f=TeaserLoad_b55dcf3b.terUni[1].mChiWat_flow_nominal
    "Nominal mass flow rate of secondary (building) district cooling side"; // TODO: verify this is ok!
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_4302ba1f=-1*TeaserLoad_b55dcf3b.terUni[1].QHea_flow_nominal; // TODO: verify this is ok!
  Modelica.Fluid.Sources.FixedBoundary pressure_source_4302ba1f(
    redeclare package Medium=MediumW,
    use_T=false,
    nPorts=1)
    "Pressure source"
    annotation (Placement(transformation(extent={{50.0,-10.0},{70.0,10.0}})));
  // TODO: move TChiWatSet (and its connection) into a CoolingIndirect specific template file (this component does not depend on the coupling)
  Modelica.Blocks.Sources.RealExpression TChiWatSet_4302ba1f(
    y=7+273.15)
    //Dehardcode
    "Primary loop (district side) chilled water setpoint temperature."
    annotation (Placement(transformation(extent={{-70.0,-50.0},{-50.0,-30.0}})));

  //
  // End Component Definitions for 4302ba1f
  //



  //
  // Begin Component Definitions for b6cc52d6
  // Source template: /model_connectors/couplings/templates/Teaser_EtsHotWaterStub/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression THeaWatSup_b6cc52d6(
    y=max(
      TeaserLoad_b55dcf3b.terUni.T_aHeaWat_nominal))
    "Heating water supply temperature"
    annotation (Placement(transformation(extent={{-30.0,-50.0},{-10.0,-30.0}})));

  //
  // End Component Definitions for b6cc52d6
  //



  //
  // Begin Component Definitions for 92f80712
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ComponentDefinitions.mopt
  //
  // no component definitions for cooling indirect and network 2 pipe

  //
  // End Component Definitions for 92f80712
  //



equation
  // Connections

  //
  // Begin Connect Statements for 2079ab67
  // Source template: /model_connectors/couplings/templates/Network2Pipe_CoolingPlant/ConnectStatements.mopt
  //

  // TODO: these connect statements shouldn't be here, they are plant specific
  // but since we can't currently make connect statements for single systems, this is what we've got
  connect(on_cooPla_e68f0b80.y,cooPla_e68f0b80.on)
    annotation (Line(points={{66.31129955639872,-26.757609690292554},{46.31129955639872,-26.757609690292554},{46.31129955639872,-6.75760969029254},{46.31129955639872,13.24239030970746},{46.31129955639872,33.24239030970746},{46.31129955639872,53.24239030970746},{26.31129955639871,53.24239030970746},{6.311299556398708,53.24239030970746},{-13.688700443601292,53.24239030970746},{-33.68870044360129,53.24239030970746},{-33.68870044360129,73.24239030970746},{-53.68870044360129,73.24239030970746}},color={0,0,127}));
  connect(TSetChiWatDis_cooPla_e68f0b80.y,cooPla_e68f0b80.TCHWSupSet)
    annotation (Line(points={{26.860668638506354,-25.83675957332204},{6.860668638506354,-25.83675957332204},{6.860668638506354,-5.836759573322027},{6.860668638506354,14.163240426677973},{6.860668638506354,34.16324042667797},{6.860668638506354,54.16324042667797},{-13.139331361493646,54.16324042667797},{-33.13933136149364,54.16324042667797},{-33.13933136149364,74.16324042667797},{-53.13933136149364,74.16324042667797}},color={0,0,127}));

  connect(disNet_9bd50e4a.port_bDisRet,cooPla_e68f0b80.port_a)
    annotation (Line(points={{-36.204741567286376,74.12158803622845},{-56.204741567286376,74.12158803622845}},color={0,0,127}));
  connect(cooPla_e68f0b80.port_b,disNet_9bd50e4a.port_aDisSup)
    annotation (Line(points={{-41.57048069864589,86.32897406693247},{-21.570480698645895,86.32897406693247}},color={0,0,127}));
  connect(disNet_9bd50e4a.dp,cooPla_e68f0b80.dpMea)
    annotation (Line(points={{-46.35045968257959,70.22459618920121},{-66.35045968257958,70.22459618920121}},color={0,0,127}));

  //
  // End Connect Statements for 2079ab67
  //



  //
  // Begin Connect Statements for 5efcb6f3
  // Source template: /model_connectors/couplings/templates/Teaser_CoolingIndirect/ConnectStatements.mopt
  //

  connect(TeaserLoad_67f392ce.ports_bChiWat[1], cooInd_6e4db825.port_a2)
    annotation (Line(points={{48.491763424817606,88.15716689408967},{28.491763424817606,88.15716689408967}},color={0,0,127}));
  connect(cooInd_6e4db825.port_b2,TeaserLoad_67f392ce.ports_aChiWat[1])
    annotation (Line(points={{44.8501819883065,89.03163739830308},{64.8501819883065,89.03163739830308}},color={0,0,127}));
  connect(pressure_source_5efcb6f3.ports[1], cooInd_6e4db825.port_b2)
    annotation (Line(points={{-63.32346477763966,26.37318629791119},{-63.32346477763966,46.37318629791119},{-63.32346477763966,66.37318629791119},{-43.32346477763966,66.37318629791119},{-23.323464777639657,66.37318629791119},{-3.323464777639657,66.37318629791119},{-3.323464777639657,86.37318629791119},{16.676535222360343,86.37318629791119}},color={0,0,127}));
  connect(TChiWatSet_5efcb6f3.y,cooInd_6e4db825.TSetBuiSup)
    annotation (Line(points={{-10.392730922655517,18.346546627476442},{-10.392730922655517,38.34654662747644},{-10.392730922655517,58.346546627476435},{9.607269077344483,58.346546627476435},{29.607269077344483,58.346546627476435},{49.60726907734448,58.346546627476435},{49.60726907734448,78.34654662747644},{69.60726907734448,78.34654662747644}},color={0,0,127}));

  //
  // End Connect Statements for 5efcb6f3
  //



  //
  // Begin Connect Statements for 14b53aa2
  // Source template: /model_connectors/couplings/templates/Teaser_EtsHotWaterStub/ConnectStatements.mopt
  //

  // teaser, ets hot water stub connections
  connect(supHeaWat_etsHotWatStub_7b28baa9.T_in,THeaWatSup_14b53aa2.y)
    annotation (Line(points={{-62.25379824120648,-65.98720849103819},{-42.25379824120648,-65.98720849103819},{-42.25379824120648,-45.98720849103819},{-42.25379824120648,-25.98720849103819},{-22.253798241206482,-25.98720849103819},{-2.253798241206482,-25.98720849103819},{-2.253798241206482,-5.987208491038189},{17.746201758793518,-5.987208491038189}},color={0,0,127}));
  connect(supHeaWat_etsHotWatStub_7b28baa9.ports[1],TeaserLoad_67f392ce.ports_aHeaWat[1])
    annotation (Line(points={{-67.52303048822418,-60.25155444815425},{-47.52303048822418,-60.25155444815425},{-47.52303048822418,-40.25155444815425},{-47.52303048822418,-20.251554448154252},{-47.52303048822418,-0.2515544481542662},{-47.52303048822418,19.748445551845734},{-47.52303048822418,39.748445551845734},{-47.52303048822418,59.74844555184574},{-27.52303048822418,59.74844555184574},{-7.52303048822418,59.74844555184574},{12.47696951177582,59.74844555184574},{32.47696951177582,59.74844555184574},{32.47696951177582,79.74844555184575},{52.47696951177582,79.74844555184575}},color={0,0,127}));
  connect(sinHeaWat_etsHotWatStub_7b28baa9.ports[1],TeaserLoad_67f392ce.ports_bHeaWat[1])
    annotation (Line(points={{-25.211276303765658,-64.26749282794998},{-5.211276303765658,-64.26749282794998},{-5.211276303765658,-44.26749282794998},{-5.211276303765658,-24.26749282794998},{-5.211276303765658,-4.2674928279499795},{-5.211276303765658,15.73250717205002},{-5.211276303765658,35.73250717205002},{-5.211276303765658,55.73250717205002},{14.788723696234342,55.73250717205002},{34.78872369623434,55.73250717205002},{34.78872369623434,75.73250717205002},{54.78872369623434,75.73250717205002}},color={0,0,127}));

  //
  // End Connect Statements for 14b53aa2
  //



  //
  // Begin Connect Statements for 569b4f20
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // cooling indirect and network 2 pipe
  
  connect(disNet_9bd50e4a.ports_bCon[1],cooInd_6e4db825.port_a1)
    annotation (Line(points={{-4.563034033187435,71.05126463640107},{15.436965966812565,71.05126463640107}},color={0,0,127}));
  connect(disNet_9bd50e4a.ports_aCon[1],cooInd_6e4db825.port_b1)
    annotation (Line(points={{-8.084631352606209,72.42918757848125},{11.915368647393791,72.42918757848125}},color={0,0,127}));

  //
  // End Connect Statements for 569b4f20
  //



  //
  // Begin Connect Statements for 4302ba1f
  // Source template: /model_connectors/couplings/templates/Teaser_CoolingIndirect/ConnectStatements.mopt
  //

  connect(TeaserLoad_b55dcf3b.ports_bChiWat[1], cooInd_7f48d218.port_a2)
    annotation (Line(points={{41.27873001855451,49.2943866704465},{21.278730018554512,49.2943866704465}},color={0,0,127}));
  connect(cooInd_7f48d218.port_b2,TeaserLoad_b55dcf3b.ports_aChiWat[1])
    annotation (Line(points={{31.889579292049874,32.31153440679216},{51.88957929204989,32.31153440679216}},color={0,0,127}));
  connect(pressure_source_4302ba1f.ports[1], cooInd_7f48d218.port_b2)
    annotation (Line(points={{68.64516026257601,12.187136453212673},{48.64516026257601,12.187136453212673},{48.64516026257601,32.18713645321267},{28.645160262576,32.18713645321267}},color={0,0,127}));
  connect(TChiWatSet_4302ba1f.y,cooInd_7f48d218.TSetBuiSup)
    annotation (Line(points={{-54.18860361982523,-13.483905225891846},{-34.18860361982523,-13.483905225891846},{-34.18860361982523,6.516094774108154},{-34.18860361982523,26.516094774108154},{-14.18860361982523,26.516094774108154},{5.81139638017477,26.516094774108154},{25.81139638017477,26.516094774108154},{45.811396380174756,26.516094774108154},{45.811396380174756,46.516094774108154},{65.81139638017476,46.516094774108154}},color={0,0,127}));

  //
  // End Connect Statements for 4302ba1f
  //



  //
  // Begin Connect Statements for b6cc52d6
  // Source template: /model_connectors/couplings/templates/Teaser_EtsHotWaterStub/ConnectStatements.mopt
  //

  // teaser, ets hot water stub connections
  connect(supHeaWat_etsHotWatStub_414cc5a1.T_in,THeaWatSup_b6cc52d6.y)
    annotation (Line(points={{19.967567975954182,-56.19189208353038},{-0.0324320240458178,-56.19189208353038},{-0.0324320240458178,-36.19189208353038},{-20.032432024045818,-36.19189208353038}},color={0,0,127}));
  connect(supHeaWat_etsHotWatStub_414cc5a1.ports[1],TeaserLoad_b55dcf3b.ports_aHeaWat[1])
    annotation (Line(points={{29.995957124558615,-63.0094963763558},{49.99595712455863,-63.0094963763558},{49.99595712455863,-43.0094963763558},{49.99595712455863,-23.0094963763558},{49.99595712455863,-3.0094963763558127},{49.99595712455863,16.990503623644187},{49.99595712455863,36.99050362364419},{69.99595712455863,36.99050362364419}},color={0,0,127}));
  connect(sinHeaWat_etsHotWatStub_414cc5a1.ports[1],TeaserLoad_b55dcf3b.ports_bHeaWat[1])
    annotation (Line(points={{56.4940995902175,-68.14132908121314},{36.494099590217516,-68.14132908121314},{36.494099590217516,-48.141329081213144},{36.494099590217516,-28.141329081213144},{36.494099590217516,-8.141329081213144},{36.494099590217516,11.858670918786856},{36.494099590217516,31.858670918786856},{56.4940995902175,31.858670918786856}},color={0,0,127}));

  //
  // End Connect Statements for b6cc52d6
  //



  //
  // Begin Connect Statements for 92f80712
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_Network2Pipe/ConnectStatements.mopt
  //

  // cooling indirect and network 2 pipe
  
  connect(disNet_9bd50e4a.ports_bCon[2],cooInd_7f48d218.port_a1)
    annotation (Line(points={{-14.577424456112624,69.46440771749565},{-14.577424456112624,49.46440771749565},{5.422575543887376,49.46440771749565},{25.422575543887376,49.46440771749565}},color={0,0,127}));
  connect(disNet_9bd50e4a.ports_aCon[2],cooInd_7f48d218.port_b1)
    annotation (Line(points={{-23.39279914167608,55.96656660912421},{-23.39279914167608,35.966566609124214},{-3.392799141676079,35.966566609124214},{16.60720085832392,35.966566609124214}},color={0,0,127}));

  //
  // End Connect Statements for 92f80712
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