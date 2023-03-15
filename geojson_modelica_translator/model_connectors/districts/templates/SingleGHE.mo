within GHP.System;
model SingleGHE "One-pipe system model with only one GHE component."

  extends Modelica.Icons.Example;
  replaceable package Medium = Buildings.Media.Water constrainedby
    Modelica.Media.Interfaces.PartialMedium
    "Medium in the component"
      annotation (choices(
        choice(redeclare package Medium = Buildings.Media.Water "Water"),
        choice(redeclare package Medium =
            Buildings.Media.Antifreeze.PropyleneGlycolWater (
              property_T=293.15,
              X_a=0.40)
              "Propylene glycol water, 40% mass fraction")));
  // borefiled parameters
  parameter Modelica.Units.SI.Time tLoaAgg(displayUnit="min")=3600
    "Time resolution of load aggregation";
  parameter Integer nCel(min=1)=5 "Number of cells per aggregation level";
  parameter Integer nSeg(min=1)=10
    "Number of segments to use in vertical discretization of the boreholes";
  parameter Modelica.Units.SI.Temperature TGro=283.15 "Initial ground temperature";
  parameter String gFunFilNam = "modelica://GHP/Resources/Data/System/SampleGFunction.mat"
    "Library path of the g-function file in MAT format";
  parameter Integer nRowGFun = 76
    "Total length of g-function vector";
  // building parameters
  parameter Integer nBui = datDes.nBui
    "Number of buildings connected to DHC system"
    annotation (Evaluate=true);
  parameter String filNam[nBui]={
    "modelica://Buildings/Resources/Data/Experimental/DHC/Loads/Examples/SwissOffice_20190916.mos",
    "modelica://Buildings/Resources/Data/Experimental/DHC/Loads/Examples/SwissResidential_20190916.mos",
    "modelica://Buildings/Resources/Data/Experimental/DHC/Loads/Examples/SwissHospital_20190916.mos"}
    "Library paths of the files with thermal loads as time series";
  constant Real facMul = 10
    "Building loads multiplier factor";
  parameter Boolean allowFlowReversalSer = true
    "Set to true to allow flow reversal in the service lines"
    annotation(Dialog(tab="Assumptions"), Evaluate=true);
  parameter Boolean allowFlowReversalBui = false
    "Set to true to allow flow reversal for in-building systems"
    annotation(Dialog(tab="Assumptions"), Evaluate=true);

  Buildings.Fluid.Geothermal.Borefields.OneUTube borFieUTub(
    redeclare package Medium = Medium,
    nCel=nCel,
    nSeg=nSeg,
    forceGFunCalc=true,
    tLoaAgg=tLoaAgg,
    gFunFilNam=Modelica.Utilities.Files.loadResource(gFunFilNam),
    nTimTot=nRowGFun,
    dynFil=false,
    energyDynamics=Modelica.Fluid.Types.Dynamics.FixedInitial,
    TExt0_start=TGro,
    borFieDat=borFieDat)
    "Borefield with a U-tube borehole configuration"
    annotation (Placement(transformation(extent={{0,0},{20,20}})));
    //gFunFilNam=Modelica.Utilities.Files.loadResource(gFunFilNam),
  Buildings.Fluid.Sensors.TemperatureTwoPort TUTubIn(
    redeclare package Medium = Medium,
    m_flow_nominal=borFieDat.conDat.mBorFie_flow_nominal,
    tau=0)
    "Inlet temperature of the borefield with UTube configuration"
    annotation (Placement(transformation(extent={{-40,0},{-20,20}})));
  Buildings.Fluid.Sensors.TemperatureTwoPort TUTubOut(
    redeclare package Medium = Medium,
    m_flow_nominal=borFieDat.conDat.mBorFie_flow_nominal,
    tau=0)
    "Inlet temperature of the borefield with UTube configuration"
    annotation (Placement(transformation(extent={{40,0},{60,20}})));
  inner parameter
  Buildings.Experimental.DHC.Examples.Combined.BaseClasses.DesignDataSeries
    datDes(
    mPumDis_flow_nominal=95,
    mPipDis_flow_nominal=datDes.mPumDis_flow_nominal,
    dp_length_nominal=250,
    final mCon_flow_nominal=bui.ets.mSerWat_flow_nominal)
    "Design data"
    annotation (Placement(transformation(extent={{-140,80},{-120,100}})));
  Buildings.Controls.OBC.CDL.Continuous.Sources.Constant THeaWatSupMaxSet[nBui](k=bui.THeaWatSup_nominal)
    "Heating water supply temperature set point - Maximum value"
    annotation (Placement(transformation(extent={{-120,20},{-100,40}})));
  Buildings.Controls.OBC.CDL.Continuous.Sources.Constant TChiWatSupSet[nBui](k=bui.TChiWatSup_nominal)
    "Chilled water supply temperature set point"
    annotation (Placement(transformation(extent={{-120,-10},{-100,10}})));
  Buildings.Controls.OBC.CDL.Continuous.Sources.Constant THeaWatSupMinSet[nBui](each k=
        28 + 273.15)
    "Heating water supply temperature set point - Minimum value"
    annotation (Placement(transformation(extent={{-120,50},{-100,70}})));
  Buildings.Controls.OBC.CDL.Continuous.Sources.Constant THotWatSupSet[nBui](k=fill(
        63 + 273.15, nBui))
    "Hot water supply temperature set point"
    annotation (Placement(transformation(extent={{-120,-40},{-100,-20}})));
  Buildings.Controls.OBC.CDL.Continuous.Sources.Constant TColWat[nBui](k=fill(15
         + 273.15, nBui))
    "Cold water temperature"
    annotation (Placement(transformation(extent={{-120,-70},{-100,-50}})));
  Buildings.Experimental.DHC.Networks.Combined.UnidirectionalSeries
    dis(
    redeclare final package Medium = Medium,
    final nCon=nBui,
    show_TOut=true,
    final mDis_flow_nominal=datDes.mPipDis_flow_nominal,
    final mCon_flow_nominal=datDes.mCon_flow_nominal,
    final dp_length_nominal=datDes.dp_length_nominal,
    final lDis=datDes.lDis,
    final lCon=datDes.lCon,
    final lEnd=datDes.lEnd,
    final allowFlowReversal=allowFlowReversalSer) "Distribution network"
    annotation (Placement(transformation(extent={{70,0},{110,20}})));
  Buildings.Experimental.DHC.EnergyTransferStations.BaseClasses.Pump_m_flow pumDis(
      redeclare final package Medium = Medium, m_flow_nominal=datDes.mPumDis_flow_nominal)
    "Distribution pump"
    annotation (Placement(transformation(
      extent={{10,-10},{-10,10}},
      rotation=270,
      origin={-44,-60})));
  Modelica.Blocks.Sources.Constant masFloMaiPum(k=datDes.mPumDis_flow_nominal)
    "Distribution pump mass flow rate"
    annotation (Placement(transformation(extent={{0,-70},{-20,-50}})));
  Buildings.Experimental.DHC.Loads.Combined.BuildingTimeSeriesWithETS bui[nBui](
    final filNam=filNam,
    bui(each final facMul=facMul),
    redeclare each final package MediumBui = Medium,
    redeclare each final package MediumSer = Medium,
    each final allowFlowReversalBui=allowFlowReversalBui,
    each final allowFlowReversalSer=allowFlowReversalSer) "Building and ETS"
    annotation (Placement(transformation(extent={{80,40},{100,60}})));
  parameter Buildings.Fluid.Geothermal.Borefields.Data.Borefield.Template borFieDat(
    final filDat=Buildings.Fluid.Geothermal.Borefields.Data.Filling.Bentonite(
        kFil=2.0,
        cFil=3040,
        dFil=1450),
    final soiDat=Buildings.Fluid.Geothermal.Borefields.Data.Soil.SandStone(
        kSoi=2.5,
        cSoi=769.23,
        dSoi=2600),
    final conDat=
        Buildings.Fluid.Geothermal.Borefields.Data.Configuration.Example(
        borCon=Buildings.Fluid.Geothermal.Borefields.Types.BoreholeConfiguration.SingleUTube,
        dp_nominal=35000,
        hBor=100,
        rBor=0.075,
        dBor=1.524,
        cooBor={{0.3048,0.3048},{5.3048,0.3048},{0.3048,5.3048},{5.3048,5.3048}},
        rTub=0.02,
        kTub=0.5,
        eTub=0.0037,
        xC=0.05))                                                                   "Borefield data"
    annotation (choicesAllMatching=true,Placement(transformation(extent={{-110,80},
            {-90,100}})));
  Buildings.Fluid.Sources.Boundary_pT expVes(redeclare final package Medium =
        Medium,
    T=283.15,   nPorts=2) "Expansion vessel"
    annotation (Placement(transformation(extent={{140,-76},{120,-56}})));
equation
  connect(TUTubIn.port_b,borFieUTub. port_a)
    annotation (Line(points={{-20,10},{0,10}},     color={0,127,255}));
  connect(borFieUTub.port_b,TUTubOut. port_a)
    annotation (Line(points={{20,10},{40,10}},            color={0,127,255}));
  connect(TUTubOut.port_b, dis.port_aDisSup) annotation (Line(points={{60,10},{70,
          10}},                              color={0,127,255}));
  connect(masFloMaiPum.y,pumDis. m_flow_in) annotation (Line(points={{-21,-60},{
          -32,-60}},                 color={0,0,127}));
  connect(pumDis.port_b, TUTubIn.port_a) annotation (Line(points={{-44,-50},{-44,
          10},{-40,10}},          color={0,127,255}));
  connect(dis.ports_bCon, bui.port_aSerAmb) annotation (Line(points={{78,20},{78,
          38},{74,38},{74,50},{80,50}}, color={0,127,255}));
  connect(bui.port_bSerAmb, dis.ports_aCon) annotation (Line(points={{100,50},{106,
          50},{106,38},{102,38},{102,20}}, color={0,127,255}));
  connect(THeaWatSupMinSet.y, bui.THeaWatSupMinSet)
    annotation (Line(points={{-98,60},{78,59}}, color={0,0,127}));
  connect(THeaWatSupMaxSet.y, bui.THeaWatSupMaxSet) annotation (Line(points={{-98,
          30},{-92,30},{-92,57},{78,57}}, color={0,0,127}));
  connect(TChiWatSupSet.y, bui.TChiWatSupSet) annotation (Line(points={{-98,0},{
          -86,0},{-86,55},{78,55}}, color={0,0,127}));
  connect(THotWatSupSet.y, bui.THotWatSupSet) annotation (Line(points={{-98,-30},
          {-80,-30},{-80,53},{78,53}}, color={0,0,127}));
  connect(TColWat.y, bui.TColWat) annotation (Line(points={{-98,-60},{-74,-60},{
          -74,36},{82,36},{82,38}}, color={0,0,127}));
  connect(pumDis.port_a, expVes.ports[1]) annotation (Line(points={{-44,-70},{-44,
          -80},{108,-80},{108,-64},{120,-64}}, color={0,127,255}));
  connect(expVes.ports[2], dis.port_bDisSup) annotation (Line(points={{120,-68},
          {108,-68},{108,-8},{122,-8},{122,10},{110,10}}, color={0,127,255}));
  annotation (Icon(coordinateSystem(preserveAspectRatio=false, extent={{-100,-100},
            {100,100}})),                                        Diagram(
        coordinateSystem(preserveAspectRatio=false, extent={{-140,-100},{140,100}})),
    experiment(StopTime=86400, __Dymola_Algorithm="Cvode"),
    __Dymola_Commands(file="Resources/Scripts/System/SingleGHE.mos"
        "Simulate and Plot"));
end SingleGHE;
