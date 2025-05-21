within geojson_modelica_translator.model_connectors.templates;
block WasteHeatController
  "Controller for waste heat loop"
  replaceable package MediumSer=Buildings.Media.Water
    constrainedby Modelica.Media.Interfaces.PartialMedium
    "District side medium";
  parameter Modelica.Units.SI.TemperatureDifference hexAppTem=2
    "Waste heat HX approach temperature";
  Buildings.Controls.OBC.CDL.Reals.Sources.Constant hexAppTem_S(
    y(
      unit="K",
      displayUnit="degC",
      quantity="ThermodynamicTemperature"),
    k=hexAppTem)
    "Waste heat HX approach temperature"
    annotation (Placement(transformation(extent={{-200,-130},{-180,-110}})));
  Buildings.Controls.OBC.CDL.Interfaces.RealInput QWasHea(
    unit="W",
    displayUnit="W",
    quantity="HeatFlowRate")
    "Heat flow rate from/to the waste heat source/sink"
    annotation (Placement(transformation(extent={{-340,-210},{-300,-170}}),iconTransformation(extent={{-380,-250},{-300,-170}})));
  Buildings.Controls.OBC.CDL.Interfaces.RealInput TWasHeaWat(
    unit="K",
    displayUnit="degC",
    quantity="ThermodynamicTemperature")
    "Waste heat fluid temperature"
    annotation (Placement(transformation(extent={{-340,60},{-300,100}}),iconTransformation(extent={{-380,-120},{-300,-40}})));
  Buildings.Controls.OBC.CDL.Interfaces.RealInput T_disRet(
    unit="K",
    displayUnit="degC",
    quantity="ThermodynamicTemperature")
    "District fluid return temperature"
    annotation (Placement(transformation(extent={{-340,120},{-300,160}}),iconTransformation(extent={{-380,280},{-300,200}})));
  Buildings.Controls.OBC.CDL.Interfaces.RealInput m_flow_pumDis(
    unit="kg/s",
    displayUnit="kg/s",
    quantity="MassFlowRate")
    "Mass flow rate of district pump [kg/s]"
    annotation (Placement(transformation(extent={{-340,210},{-300,250}}),iconTransformation(extent={{-380,-40},{-300,40}})));
  Buildings.Controls.OBC.CDL.Interfaces.RealInput yPumDis(
    unit="1")
    "Control signal for district pump"
    annotation (Placement(transformation(extent={{-340,170},{-300,210}}),iconTransformation(extent={{-380,-200},{-300,-120}})));
  Buildings.Controls.OBC.CDL.Interfaces.RealOutput m_flow_pumPla(
    unit="kg/s",
    displayUnit="kg/s",
    quantity="MassFlowRate")
    "Mass flow rate of plant pump [kg/s]"
    annotation (Placement(transformation(extent={{300,150},{340,190}}),iconTransformation(extent={{300,280},{380,200}})));
  Buildings.Controls.OBC.CDL.Interfaces.RealOutput Q_flow_wasHea_out(
    unit="W",
    displayUnit="W",
    quantity="HeatFlowRate")
    "Heat flow rate from/to the waste heat source/sink"
    annotation (Placement(transformation(extent={{300,-250},{340,-210}}),iconTransformation(extent={{300,200},{380,120}})));
  Buildings.Controls.OBC.CDL.Interfaces.BooleanOutput uWasHeaSou
    "Waste heat source enable signal"
    annotation (Placement(transformation(extent={{300,110},{340,150}}),iconTransformation(extent={{300,-150},{420,-30}})));
  Buildings.Controls.OBC.CDL.Interfaces.BooleanOutput uWasHeaSin
    "Waste heat sink enable signal"
    annotation (Placement(transformation(extent={{300,70},{340,110}}),iconTransformation(extent={{300,-210},{420,-90}})));
  parameter MediumSer.ThermodynamicState sta_defaultSer=MediumSer.setState_pTX(
    T=MediumSer.T_default,
    p=MediumSer.p_default,
    X=MediumSer.X_default);
  parameter Modelica.Units.SI.SpecificHeatCapacity cp_defaultSer=MediumSer.specificHeatCapacityCp(
    sta_defaultSer)
    "Specific heat capacity of waste heat side medium at default medium state [J/kg-K]";
  Modelica.Blocks.Sources.RealExpression cp_defaultSer_s(
    y(
      unit="J/(kg.K)",
      displayUnit="J/(kg.K)",
      quantity="SpecificHeatCapacity")=cp_defaultSer)
    "Specific heat capacity of waste heat side medium at default medium state [J/kg-K]"
    annotation (Placement(transformation(extent={{-160,-280},{-140,-260}})));
  Buildings.Controls.OBC.CDL.Reals.GreaterThreshold enaWasHea_pumDis(
    t=1e-4)
    "Threshold comparison to check if district pump is on (condition to enable waste heat)"
    annotation (Placement(transformation(extent={{-260,180},{-240,200}})));
  Buildings.Controls.OBC.CDL.Reals.Subtract TOutMax_wasHeaSou(
    y(
      unit="K",
      displayUnit="degC",
      quantity="ThermodynamicTemperature"))
    "Maximum temperature leaving the HX when waste heat is source (plant side)"
    annotation (Placement(transformation(extent={{-160,-100},{-140,-80}})));
  Buildings.Controls.OBC.CDL.Reals.Add TOutMin_wasHeaSin(
    y(
      unit="K",
      displayUnit="degC",
      quantity="ThermodynamicTemperature"))
    "Minimum temperature leaving the HX when waste heat is sink (plant side)"
    annotation (Placement(transformation(extent={{-160,-160},{-140,-140}})));
  Buildings.Controls.OBC.CDL.Reals.Subtract dT_wasHeaIsSou(
    y(
      unit="K",
      displayUnit="K",
      quantity="TemperatureDifference"))
    "Temperature difference between district fluid and waste heat (when waste heat is source)"
    annotation (Placement(transformation(extent={{-260,100},{-240,120}})));
  Buildings.Controls.OBC.CDL.Reals.MultiplyByParameter gai_dT_wasHeaIsSin(
    y(
      unit="K",
      displayUnit="K",
      quantity="TemperatureDifference"),
    k=-1)
    "Temperature difference between waste heat and district fluid (when waste heat is sink)"
    annotation (Placement(transformation(extent={{-220,80},{-200,100}})));
  Buildings.Controls.OBC.CDL.Reals.Multiply pro_mPumPla(
    y(
      unit="kg/s",
      displayUnit="kg/s",
      quantity="MassFlowRate"))
    "Waste heat plant pump mass flow rate (turns plant pump off when conditions not satisfied for waste heat source/sink)"
    annotation (Placement(transformation(extent={{260,160},{280,180}})));
  Buildings.Controls.OBC.CDL.Reals.Min min_QWasHeaIsSou(
    y(
      unit="W",
      displayUnit="W",
      quantity="HeatFlowRate"))
    "Minimum heat flow rate when waste heat is source (Q has positive value)"
    annotation (Placement(transformation(extent={{160,-100},{180,-80}})));
  Buildings.Controls.OBC.CDL.Reals.Max max_QWasHeaIsSin(
    y(
      unit="W",
      displayUnit="W",
      quantity="HeatFlowRate"))
    "Maximum heat flow rate when waste heat is sink (Q has negative value)"
    annotation (Placement(transformation(extent={{160,-160},{180,-140}})));
  parameter Modelica.Units.SI.TemperatureDifference dT_hysLow_souSin=-0.3
    "Hysteresis limit cutoff (deltaT between waste heat source and district return temperature)";
  Buildings.Controls.OBC.CDL.Reals.Hysteresis hys_dT_wasHea_souSin[2](
    each uLow=-hexAppTem+dT_hysLow_souSin,
    each uHigh=-hexAppTem)
    "deltaT hysteresis (opposite of waste heat signal) (source: [1], sink: [2])"
    annotation (Placement(transformation(extent={{-30,100},{-10,120}})));
  Buildings.Controls.OBC.CDL.Logical.Not not_wasHea_souSin[2]
    "Condition to enable waste heat (source: true if T_disRet < TWasHeaWat, sink: true if T_disRet > TWasHeaWat) (source: [1], sink: [2])"
    annotation (Placement(transformation(extent={{0,100},{20,120}})));
  Buildings.Controls.OBC.CDL.Reals.Multiply pro_maxQWasHea_souSin[2](
    each y(
      unit="W",
      displayUnit="W",
      quantity="HeatFlowRate"))
    "Maximum waste heat flow rate (source: [1], sink: [2])"
    annotation (Placement(transformation(extent={{100,-240},{120,-220}})));
  Buildings.Controls.OBC.CDL.Reals.Multiply ProWasHea_cp_dT[2](
    each y(
      unit="J/kg",
      displayUnit="J/kg",
      quantity="SpecificEnergy"))
    "Product of c_p and deltaT (source: [1], sink: [2])"
    annotation (Placement(transformation(extent={{-80,-260},{-60,-240}})));
  Buildings.Controls.OBC.CDL.Routing.RealScalarReplicator reaRep(
    each y(
      each unit="J/(kg.K)",
      each displayUnit="J/(kg.K)",
      each quantity="SpecificHeatCapacity"),
    final nout=2)
    "Replicate real number"
    annotation (Placement(transformation(extent={{-120,-280},{-100,-260}})));
  Buildings.Controls.OBC.CDL.Reals.Subtract dTHexMax_souSin[2](
    each y(
      unit="K",
      displayUnit="K",
      quantity="TemperatureDifference"))
    "Maximum temperature difference between inlet and outlet of HX (source: positive, sink: negative) (source: [1], sink: [2])"
    annotation (Placement(transformation(extent={{-120,-240},{-100,-220}})));
  Buildings.Controls.OBC.CDL.Reals.Multiply pro_QWasHea_souSin[2](
    each y(
      unit="W",
      displayUnit="W",
      quantity="HeatFlowRate"))
    "Waste heat flow rate to/from district (source: [1], sink: [2])"
    annotation (Placement(transformation(extent={{220,-240},{240,-220}})));
  Buildings.Controls.OBC.CDL.Reals.Add add_Q_flow_wasHea_out(
    y(
      unit="W",
      displayUnit="W",
      quantity="HeatFlowRate"))
    "Addition of heat flow rate when waste heat is source and sink (they will not occur simultaneously)"
    annotation (Placement(transformation(extent={{260,-240},{280,-220}})));
  Buildings.Controls.OBC.CDL.Logical.MultiAnd mulAnd_wasHeaIsSou(
    nin=3)
    "True if wate heat source, district pump on, and district return temp lower than waste heat temp"
    annotation (Placement(transformation(extent={{80,120},{100,140}})));
  Buildings.Controls.OBC.CDL.Logical.MultiAnd mulAnd_wasHeaIsSin(
    nin=3)
    "True if wate heat sink, district pump on, and district return temp higher than waste heat temp"
    annotation (Placement(transformation(extent={{80,80},{100,100}})));
  parameter String filNam_QWasHea
    "Waste heat rate as time series (source positive, sink negative) (user input, also must provide both peaks source and sink)";
  parameter Modelica.Units.SI.HeatFlowRate QWasHeaSou_flow_max(
    min=0)=Buildings.DHC.Loads.BaseClasses.getPeakLoad(
    string="#Peak heat flow rate from the waste heat source",
    filNam=Modelica.Utilities.Files.loadResource(filNam_QWasHea))
    "Peak heat flow rate from the waste heat source (>=0)"
    annotation (Dialog(group="Nominal condition"));
  parameter Modelica.Units.SI.HeatFlowRate QWasHeaSin_flow_max(
    max=0)=Buildings.DHC.Loads.BaseClasses.getPeakLoad(
    string="#Peak heat flow rate to the waste heat sink",
    filNam=Modelica.Utilities.Files.loadResource(filNam_QWasHea))
    "Peak heat flow rate to the waste heat sink (<=0)"
    annotation (Dialog(group="Nominal condition"));
  Buildings.Controls.OBC.CDL.Reals.Limiter limSou_wasHea(
    y(
      unit="W",
      displayUnit="W",
      quantity="HeatFlowRate"),
    uMin=0,
    uMax=Modelica.Constants.inf)
    "Positive heat flow rate from the waste heat source"
    annotation (Placement(transformation(extent={{-220,0},{-200,20}})));
  Buildings.Controls.OBC.CDL.Reals.Limiter limSin_wasHea(
    y(
      unit="W",
      displayUnit="W",
      quantity="HeatFlowRate"),
    uMin=-Modelica.Constants.inf,
    uMax=0)
    "Negative heat flow rate to the waste heat sink"
    annotation (Placement(transformation(extent={{-220,-40},{-200,-20}})));
  Buildings.Controls.OBC.CDL.Reals.MultiplyByParameter QWasHeaSou_nor(
    k=1/QWasHeaSou_flow_max)
    "Normalized heat flow rate from the waste heat source"
    annotation (Placement(transformation(extent={{-180,0},{-160,20}})));
  Buildings.Controls.OBC.CDL.Reals.MultiplyByParameter QWasHeaSin_nor(
    k=1/QWasHeaSin_flow_max)
    "Normalized heat flow rate to the waste heat sink"
    annotation (Placement(transformation(extent={{-180,-40},{-160,-20}})));
  Buildings.Controls.OBC.CDL.Reals.GreaterThreshold enaWasHea_souSin[2](
    each t=1e-4)
    "Threshold comparison to check if heat flow rate is source or sink (condition to enable waste heat) (source: [1], sink: [2])"
    annotation (Placement(transformation(extent={{-140,-20},{-120,0}})));
  parameter Modelica.Units.SI.Time QWasHeaTime_souSin=(15)*60
    "Minimum time that waste heat (source or sink) is on/off before changing to other state [s].";
  Buildings.Controls.OBC.CDL.Logical.TrueFalseHold enaWasHeaSou(
    trueHoldDuration=QWasHeaTime_souSin)
    "Enable waste heat source"
    annotation (Placement(transformation(extent={{-80,-60},{-60,-40}})));
  Buildings.Controls.OBC.CDL.Logical.TrueFalseHold enaWasHeaSin(
    trueHoldDuration=QWasHeaTime_souSin)
    "Enable waste heat sink"
    annotation (Placement(transformation(extent={{-80,-100},{-60,-80}})));
  Buildings.Controls.OBC.CDL.Logical.Switch swi_uWasHeaSin
    "Switch to reset uWasHeaSin to false when uWasHeaSou switch to true"
    annotation (Placement(transformation(extent={{-40,-60},{-20,-40}})));
  Buildings.Controls.OBC.CDL.Logical.Sources.Constant uWasHeaSin_reset(
    k=false)
    "Constant false"
    annotation (Placement(transformation(extent={{-80,-20},{-60,0}})));
  Buildings.Controls.OBC.CDL.Conversions.BooleanToReal booToRea_uWasHeaIsSou(
    final realTrue=1,
    final realFalse=0)
    "Waste heat is source"
    annotation (Placement(transformation(extent={{120,140},{140,160}})));
  Buildings.Controls.OBC.CDL.Conversions.BooleanToReal booToRea_uWasHeaIsSin(
    final realTrue=1,
    final realFalse=0)
    "Waste heat is sink"
    annotation (Placement(transformation(extent={{120,60},{140,80}})));
  Buildings.Controls.OBC.CDL.Conversions.BooleanToReal booToRea_uWasHeaIsSouSin(
    final realTrue=1,
    final realFalse=0)
    "Waste heat is source or sink"
    annotation (Placement(transformation(extent={{220,140},{240,160}})));
  Buildings.Controls.OBC.CDL.Logical.MultiOr or_wasHeaIsSouSin(
    nin=2)
    "True if waste heat is source or sink"
    annotation (Placement(transformation(extent={{180,140},{200,160}})));
  Buildings.Controls.OBC.CDL.Routing.RealScalarReplicator reaRep1(
    each y(
      each unit="kg/s",
      each displayUnit="kg/s",
      each quantity="MassFlowRate"),
    final nout=2)
    "Replicate real number"
    annotation (Placement(transformation(extent={{60,-234},{80,-214}})));
  Buildings.Controls.OBC.CDL.Routing.RealScalarReplicator reaRep2(
    each y(
      each unit="K",
      each displayUnit="degC",
      each quantity="ThermodynamicTemperature"),
    final nout=2)
    "Replicate real number"
    annotation (Placement(transformation(extent={{-160,-246},{-140,-226}})));
equation
  connect(T_disRet,dT_wasHeaIsSou.u1)
    annotation (Line(points={{-320,140},{-280,140},{-280,116},{-262,116}},color={0,0,127}));
  connect(TWasHeaWat,dT_wasHeaIsSou.u2)
    annotation (Line(points={{-320,80},{-268,80},{-268,104},{-262,104}},color={0,0,127}));
  connect(dT_wasHeaIsSou.y,hys_dT_wasHea_souSin[1].u)
    annotation (Line(points={{-238,110},{-32,110}},color={0,0,127}));
  connect(hys_dT_wasHea_souSin.y,not_wasHea_souSin.u)
    annotation (Line(points={{-8,110},{-2,110}},color={255,0,255}));
  connect(pro_mPumPla.y,m_flow_pumPla)
    annotation (Line(points={{282,170},{320,170}},color={0,0,127}));
  connect(pro_maxQWasHea_souSin[1].y,min_QWasHeaIsSou.u2)
    annotation (Line(points={{122,-230},{130,-230},{130,-96},{158,-96}},color={0,0,127}));
  connect(QWasHea,min_QWasHeaIsSou.u1)
    annotation (Line(points={{-320,-190},{120,-190},{120,-84},{158,-84}},color={0,0,127}));
  connect(ProWasHea_cp_dT.y,pro_maxQWasHea_souSin.u2)
    annotation (Line(points={{-58,-250},{90,-250},{90,-236},{98,-236}},color={0,0,127}));
  connect(dTHexMax_souSin.y,ProWasHea_cp_dT.u1)
    annotation (Line(points={{-98,-230},{-90,-230},{-90,-244},{-82,-244}},color={0,0,127}));
  connect(T_disRet,reaRep2.u)
    annotation (Line(points={{-320,140},{-280,140},{-280,-236},{-162,-236}},color={0,0,127}));
  connect(m_flow_pumDis,reaRep1.u)
    annotation (Line(points={{-320,230},{50,230},{50,-224},{58,-224}},color={0,0,127}));
  connect(yPumDis,enaWasHea_pumDis.u)
    annotation (Line(points={{-320,190},{-262,190}},color={0,0,127}));
  connect(not_wasHea_souSin[1].y,mulAnd_wasHeaIsSou.u[1])
    annotation (Line(points={{22,110},{38,110},{38,128},{78,128},{78,127.667}},color={255,0,255}));
  connect(enaWasHea_pumDis.y,mulAnd_wasHeaIsSou.u[2])
    annotation (Line(points={{-238,190},{26,190},{26,130},{78,130}},color={255,0,255}));
  connect(enaWasHeaSou.y,mulAnd_wasHeaIsSou.u[3])
    annotation (Line(points={{-58,-50},{-52,-50},{-52,0},{-20,0},{-20,96},{40,96},{40,132.333},{78,132.333}},color={255,0,255}));
  connect(mulAnd_wasHeaIsSou.y,booToRea_uWasHeaIsSou.u)
    annotation (Line(points={{102,130},{110,130},{110,150},{118,150}},color={255,0,255}));
  connect(not_wasHea_souSin[2].y,mulAnd_wasHeaIsSin.u[1])
    annotation (Line(points={{22,110},{38,110},{38,86},{78,86},{78,87.6667}},color={255,0,255}));
  connect(enaWasHea_pumDis.y,mulAnd_wasHeaIsSin.u[2])
    annotation (Line(points={{-238,190},{26,190},{26,90},{78,90}},color={255,0,255}));
  connect(swi_uWasHeaSin.y,mulAnd_wasHeaIsSin.u[3])
    annotation (Line(points={{-18,-50},{-10,-50},{-10,92.3333},{78,92.3333}},color={255,0,255}));
  connect(mulAnd_wasHeaIsSin.y,booToRea_uWasHeaIsSin.u)
    annotation (Line(points={{102,90},{110,90},{110,70},{118,70}},color={255,0,255}));
  connect(hexAppTem_S.y,TOutMax_wasHeaSou.u2)
    annotation (Line(points={{-178,-120},{-170,-120},{-170,-96},{-162,-96}},color={0,0,127}));
  connect(TWasHeaWat,TOutMax_wasHeaSou.u1)
    annotation (Line(points={{-320,80},{-268,80},{-268,-84},{-162,-84}},color={0,0,127}));
  connect(TOutMax_wasHeaSou.y,dTHexMax_souSin[1].u1)
    annotation (Line(points={{-138,-90},{-130,-90},{-130,-224},{-122,-224}},color={0,0,127}));
  connect(TOutMin_wasHeaSin.y,dTHexMax_souSin[2].u1)
    annotation (Line(points={{-138,-150},{-130,-150},{-130,-224},{-122,-224}},color={0,0,127}));
  connect(m_flow_pumDis,pro_mPumPla.u1)
    annotation (Line(points={{-320,230},{252,230},{252,176},{258,176}},color={0,0,127}));
  connect(QWasHea,limSou_wasHea.u)
    annotation (Line(points={{-320,-190},{-274,-190},{-274,10},{-222,10}},color={0,0,127}));
  connect(QWasHea,limSin_wasHea.u)
    annotation (Line(points={{-320,-190},{-274,-190},{-274,-30},{-222,-30}},color={0,0,127}));
  connect(limSou_wasHea.y,QWasHeaSou_nor.u)
    annotation (Line(points={{-198,10},{-182,10}},color={0,0,127}));
  connect(limSin_wasHea.y,QWasHeaSin_nor.u)
    annotation (Line(points={{-198,-30},{-182,-30}},color={0,0,127}));
  connect(QWasHeaSou_nor.y,enaWasHea_souSin[1].u)
    annotation (Line(points={{-158,10},{-150,10},{-150,-10},{-142,-10}},color={0,0,127}));
  connect(QWasHeaSin_nor.y,enaWasHea_souSin[2].u)
    annotation (Line(points={{-158,-30},{-150,-30},{-150,-10},{-142,-10}},color={0,0,127}));
  connect(enaWasHeaSin.y,swi_uWasHeaSin.u3)
    annotation (Line(points={{-58,-90},{-48,-90},{-48,-58},{-42,-58}},color={255,0,255}));
  connect(uWasHeaSin_reset.y,swi_uWasHeaSin.u1)
    annotation (Line(points={{-58,-10},{-48,-10},{-48,-42},{-42,-42}},color={255,0,255}));
  connect(enaWasHea_souSin[1].y,enaWasHeaSou.u)
    annotation (Line(points={{-118,-10},{-108,-10},{-108,-50},{-82,-50}},color={255,0,255}));
  connect(enaWasHea_souSin[2].y,enaWasHeaSin.u)
    annotation (Line(points={{-118,-10},{-108,-10},{-108,-90},{-82,-90}},color={255,0,255}));
  connect(enaWasHeaSou.y,swi_uWasHeaSin.u2)
    annotation (Line(points={{-58,-50},{-42,-50}},color={255,0,255}));
  connect(min_QWasHeaIsSou.y,pro_QWasHea_souSin[1].u1)
    annotation (Line(points={{182,-90},{212,-90},{212,-224},{218,-224}},color={0,0,127}));
  connect(booToRea_uWasHeaIsSou.y,pro_QWasHea_souSin[1].u2)
    annotation (Line(points={{142,150},{150,150},{150,76},{200,76},{200,-236},{218,-236}},color={0,0,127}));
  connect(max_QWasHeaIsSin.y,pro_QWasHea_souSin[2].u1)
    annotation (Line(points={{182,-150},{206,-150},{206,-224},{218,-224}},color={0,0,127}));
  connect(booToRea_uWasHeaIsSin.y,pro_QWasHea_souSin[2].u2)
    annotation (Line(points={{142,70},{194,70},{194,-236},{218,-236}},color={0,0,127}));
  connect(dT_wasHeaIsSou.y,gai_dT_wasHeaIsSin.u)
    annotation (Line(points={{-238,110},{-230,110},{-230,90},{-222,90}},color={0,0,127}));
  connect(gai_dT_wasHeaIsSin.y,hys_dT_wasHea_souSin[2].u)
    annotation (Line(points={{-198,90},{-190,90},{-190,110},{-32,110}},color={0,0,127}));
  connect(mulAnd_wasHeaIsSou.y,or_wasHeaIsSouSin.u[1])
    annotation (Line(points={{102,130},{172,130},{172,148.25},{178,148.25}},color={255,0,255}));
  connect(mulAnd_wasHeaIsSin.y,or_wasHeaIsSouSin.u[2])
    annotation (Line(points={{102,90},{168,90},{168,151.75},{178,151.75}},color={255,0,255}));
  connect(or_wasHeaIsSouSin.y,booToRea_uWasHeaIsSouSin.u)
    annotation (Line(points={{202,150},{218,150}},color={255,0,255}));
  connect(booToRea_uWasHeaIsSouSin.y,pro_mPumPla.u2)
    annotation (Line(points={{242,150},{250,150},{250,164},{258,164}},color={0,0,127}));
  connect(mulAnd_wasHeaIsSou.y,uWasHeaSou)
    annotation (Line(points={{102,130},{320,130}},color={255,0,255}));
  connect(mulAnd_wasHeaIsSin.y,uWasHeaSin)
    annotation (Line(points={{102,90},{320,90}},color={255,0,255}));
  connect(TWasHeaWat,TOutMin_wasHeaSin.u1)
    annotation (Line(points={{-320,80},{-268,80},{-268,-144},{-162,-144}},color={0,0,127}));
  connect(hexAppTem_S.y,TOutMin_wasHeaSin.u2)
    annotation (Line(points={{-178,-120},{-170,-120},{-170,-156},{-162,-156}},color={0,0,127}));
  connect(cp_defaultSer_s.y,reaRep.u)
    annotation (Line(points={{-139,-270},{-122,-270}},color={0,0,127}));
  connect(reaRep.y,ProWasHea_cp_dT.u2)
    annotation (Line(points={{-98,-270},{-90,-270},{-90,-256},{-82,-256}},color={0,0,127}));
  connect(reaRep1.y,pro_maxQWasHea_souSin.u1)
    annotation (Line(points={{82,-224},{98,-224}},color={0,0,127}));
  connect(QWasHea,max_QWasHeaIsSin.u1)
    annotation (Line(points={{-320,-190},{120,-190},{120,-144},{158,-144}},color={0,0,127}));
  connect(pro_maxQWasHea_souSin[2].y,max_QWasHeaIsSin.u2)
    annotation (Line(points={{122,-230},{140,-230},{140,-156},{158,-156}},color={0,0,127}));
  connect(pro_QWasHea_souSin[1].y,add_Q_flow_wasHea_out.u1)
    annotation (Line(points={{242,-230},{250,-230},{250,-224},{258,-224}},color={0,0,127}));
  connect(pro_QWasHea_souSin[2].y,add_Q_flow_wasHea_out.u2)
    annotation (Line(points={{242,-230},{250,-230},{250,-236},{258,-236}},color={0,0,127}));
  connect(add_Q_flow_wasHea_out.y,Q_flow_wasHea_out)
    annotation (Line(points={{282,-230},{320,-230}},color={0,0,127}));
  connect(reaRep2.y,dTHexMax_souSin.u2)
    annotation (Line(points={{-138,-236},{-122,-236}},color={0,0,127}));
  annotation (
    Icon(
      coordinateSystem(
        preserveAspectRatio=false,
        extent={{-300,-300},{300,300}}),
      graphics={
        Rectangle(
          extent={{-300,-300},{300,300}},
          lineColor={0,0,0},
          fillColor={255,255,255},
          fillPattern=FillPattern.Solid),
        Text(
          extent={{-148,-326},{152,-366}},
          textColor={0,0,255},
          textString="%name")}),
    Diagram(
      coordinateSystem(
        preserveAspectRatio=false,
        extent={{-300,-300},{300,300}})));
end WasteHeatController;
