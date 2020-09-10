within Buildings.Applications.DHC.Loads;
model TimeSeriesMassFlow_Temp
  "Heating and Cooling Water massflowrates and temperatures from building on EP."
 extends Modelica.Icons.Example;

  package MediumW = Buildings.Media.Water;

  parameter String filNam= "modelica://Buildings/Resources/Data/Applications/DHC/Examples/FourthGeneration/modelica.csv";

  parameter Modelica.SIunits.MassFlowRate mChW_flow_nominal=
    Buildings.Experimental.DistrictHeatingCooling.SubStations.VaporCompression.BaseClasses.getPeakMassFlowRate(
    string="#Nominal chilled water mass flow rate",
    filNam=Modelica.Utilities.Files.loadResource(filNam))
    "Nominal cooling water flow rate"
    annotation (Dialog(group="Design parameter"));
  parameter Modelica.SIunits.MassFlowRate mHW_flow_nominal=
    Buildings.Experimental.DistrictHeatingCooling.SubStations.VaporCompression.BaseClasses.getPeakMassFlowRate(
    string="#Nominal heating water mass flow rate",
    filNam=Modelica.Utilities.Files.loadResource(filNam))
    "Nominal heating water flow rate"
    annotation (Dialog(group="Design parameter"));
  parameter Modelica.SIunits.TemperatureDifference delTBuiChW(displayUnit="degC")=7
    "Nominal chilled water temperature differnce(building side)";
  parameter Modelica.SIunits.TemperatureDifference delTBuiHW(displayUnit="degC")=15
    "Nominal heating water temperature difference(building side) ";
  parameter Modelica.SIunits.TemperatureDifference delTDisChW(displayUnit="degC")=9
    "Nominal chilled water temperature differnce(district side)";
  parameter Modelica.SIunits.TemperatureDifference delTDisHW(displayUnit="degC")=20
    "Nominal heating water temperature difference(district side) ";

  Modelica.Blocks.Sources.CombiTimeTable buiMasTem(
    tableOnFile=true,
    tableName="modelica",
    fileName=Modelica.Utilities.Files.loadResource(filNam),
    extrapolation=Modelica.Blocks.Types.Extrapolation.Periodic,
    columns=2:7,
    smoothness=Modelica.Blocks.Types.Smoothness.LinearSegments)
    annotation (Placement(transformation(extent={{114,0},{94,20}})));
  Buildings.Fluid.Sources.MassFlowSource_T supChiWat(
    redeclare package Medium = MediumW,
    use_m_flow_in=true,
    use_T_in=true,
    nPorts=1) "Chilled water supply" annotation (Placement(transformation(
      extent={{10,-10},{-10,10}},
      rotation=0,
      origin={24,22})));
  Buildings.Fluid.Sources.Boundary_pT disCooSin(
    redeclare package Medium = MediumW,
    use_T_in=false,
    T=288.15,
    nPorts=1) "District cooling sink." annotation (Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=0,
        origin={26,60})));
  EnergyTransferStations.CoolingIndirect cooETS(
    allowFlowReversal1=false,
    allowFlowReversal2=false,
    redeclare package Medium = MediumW,
    mBui_flow_nominal=mChW_flow_nominal,
    mDis_flow_nominal=mChW_flow_nominal,
    dpValve_nominal=6000,
    dp1_nominal=500,
    dp2_nominal=500,
    use_Q_flow_nominal=true,
    Q_flow_nominal=mChW_flow_nominal*4187*delTBuiChW,
    T_a1_nominal(displayUnit="degC") = 278.15,
    T_a2_nominal(displayUnit="degC") = 289.15)
    annotation (Placement(transformation(extent={{-22,18},{-2,38}})));
  Buildings.Fluid.Sources.Boundary_pT buiCooSin(
    redeclare package Medium = MediumW,
    use_T_in=false,
    nPorts=1) "Building cooling sink." annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={-66,20})));
  EnergyTransferStations.Heating.HeatingIndirect heaETS(
    allowFlowReversal1=false,
    allowFlowReversal2=false,
    redeclare package Medium = MediumW,
    mBui_flow_nominal=mHW_flow_nominal,
    mDis_flow_nominal=mHW_flow_nominal*delTBuiHW/delTDisHW,
    dpValve_nominal=6000,
    dp1_nominal=500,
    dp2_nominal=500,
    use_Q_flow_nominal=true,
    Q_flow_nominal=mHW_flow_nominal*4187*delTBuiHW,
    T_a1_nominal=65 + 273.15,
    T_a2_nominal=42 + 273.15,
    reverseActing=true)
    annotation (Placement(transformation(extent={{-22,-48},{-2,-28}})));
  Buildings.Fluid.Sources.MassFlowSource_T supHeaWat(
    redeclare package Medium = MediumW,
    use_m_flow_in=true,
    use_T_in=true,
    nPorts=1) "Heating water supply" annotation (Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=0,
        origin={26,-60})));
  Buildings.Fluid.Sources.Boundary_pT buiHeaSin(
    redeclare package Medium = MediumW,
    use_T_in=false,
    nPorts=1) "Building heating sink." annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={-66,-70})));
  Buildings.Fluid.Sources.Boundary_pT disHeaSou(
    redeclare package Medium = MediumW,
    use_T_in=false,
    T=313.15,
    nPorts=1) "Heating water supply" annotation (Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=0,
        origin={26,-20})));
  Buildings.Controls.OBC.UnitConversions.From_degC TChWR
    annotation (Placement(transformation(extent={{76,30},{56,50}})));
  Buildings.Controls.OBC.UnitConversions.From_degC THWR
    "Heating water temperature."
    annotation (Placement(transformation(extent={{82,-60},{62,-40}})));
  Buildings.Controls.OBC.UnitConversions.From_degC TChWSET
    annotation (Placement(transformation(extent={{4,70},{-16,90}})));
  Buildings.Controls.OBC.UnitConversions.From_degC THWSET
    annotation (Placement(transformation(extent={{4,-96},{-16,-76}})));
  Buildings.Fluid.Sources.MassFlowSource_T supDisChWat(
    redeclare package Medium = MediumW,
    use_m_flow_in=true,
    use_T_in=false,
    T=278.15,
    nPorts=1) "Chilled water supply district side." annotation (Placement(
        transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={-66,50})));
  Modelica.Blocks.Sources.RealExpression mDisChW(y=buiMasTem.y[6]*(delTBuiChW/
        delTDisChW))
    annotation (Placement(transformation(extent={{-36,70},{-56,90}})));
  Modelica.Blocks.Sources.RealExpression mDisHW(y=buiMasTem.y[5]*delTDisHW/
        delTBuiHW)
    annotation (Placement(transformation(extent={{-36,-10},{-56,10}})));
  Modelica.Blocks.Sources.RealExpression mBuiHW(y=buiMasTem.y[5])
    annotation (Placement(transformation(extent={{80,-34},{60,-14}})));
  Buildings.Fluid.Sources.MassFlowSource_T      disHeaSin(
    redeclare package Medium = MediumW,
    use_m_flow_in=true,
    use_T_in=false,
    T=330.15,
    nPorts=1) "District heating sink." annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={-66,-30})));
  Modelica.Blocks.Sources.RealExpression mBuiChW(y=buiMasTem.y[6])
    annotation (Placement(transformation(extent={{78,52},{58,72}})));
equation
  connect(cooETS.port_a2, supChiWat.ports[1]) annotation (Line(points={{-2,22},{
          14,22}},               color={0,127,255}));
  connect(cooETS.port_b1, disCooSin.ports[1]) annotation (Line(points={{-2,34},{
          4,34},{4,60},{16,60}},  color={0,127,255}));
  connect(buiCooSin.ports[1], cooETS.port_b2) annotation (Line(points={{-56,20},
          {-36,20},{-36,22},{-22,22}},
                                     color={0,127,255}));
  connect(THWSET.y, heaETS.TSetBuiSup) annotation (Line(points={{-18,-86},{-36,-86},
          {-36,-38},{-24,-38}}, color={0,0,127}));
  connect(TChWSET.y, cooETS.TSetBuiSup) annotation (Line(points={{-18,80},{-28,80},
          {-28,28},{-24,28}}, color={0,0,127}));
  connect(TChWR.y, supChiWat.T_in) annotation (Line(points={{54,40},{46,40},{46,
          26},{36,26}}, color={0,0,127}));
  connect(THWR.y, supHeaWat.T_in) annotation (Line(points={{60,-50},{58,-50},{58,
          -56},{38,-56}},
                        color={0,0,127}));
  connect(supDisChWat.ports[1], cooETS.port_a1) annotation (Line(points={{-56,50},
          {-36,50},{-36,34},{-22,34}}, color={0,127,255}));
  connect(mDisChW.y, supDisChWat.m_flow_in) annotation (Line(points={{-57,80},{-84,
          80},{-84,58},{-78,58}}, color={0,0,127}));
  connect(buiHeaSin.ports[1], heaETS.port_b2) annotation (Line(points={{-56,-70},
          {-44,-70},{-44,-44},{-22,-44}}, color={0,127,255}));
  connect(supHeaWat.ports[1], heaETS.port_a2) annotation (Line(points={{16,-60},
          {4,-60},{4,-44},{-2,-44}},  color={0,127,255}));
  connect(disHeaSou.ports[1], heaETS.port_b1) annotation (Line(points={{16,-20},
          {4,-20},{4,-32},{-2,-32}},  color={0,127,255}));
  connect(mBuiHW.y, supHeaWat.m_flow_in) annotation (Line(points={{59,-24},{50,-24},
          {50,-52},{38,-52}}, color={0,0,127}));
  connect(disHeaSin.ports[1], heaETS.port_a1) annotation (Line(points={{-56,-30},
          {-38,-30},{-38,-32},{-22,-32}}, color={0,127,255}));
  connect(mDisHW.y, disHeaSin.m_flow_in) annotation (Line(points={{-57,0},{-84,0},
          {-84,-22},{-78,-22}},    color={0,0,127}));
  connect(buiMasTem.y[1], THWR.u) annotation (Line(points={{93,10},{90,10},{90,-50},
          {84,-50}}, color={0,0,127}));
  connect(buiMasTem.y[2], THWSET.u) annotation (Line(points={{93,10},{90,10},{90,
          -86},{6,-86}}, color={0,0,127}));
  connect(buiMasTem.y[3], TChWR.u) annotation (Line(points={{93,10},{90,10},{90,
          40},{78,40}}, color={0,0,127}));
  connect(buiMasTem.y[4], TChWSET.u) annotation (Line(points={{93,10},{90,10},{90,
          80},{6,80}}, color={0,0,127}));
  connect(mBuiChW.y, supChiWat.m_flow_in) annotation (Line(points={{57,62},{42,62},
          {42,30},{36,30}}, color={0,0,127}));
  annotation (Diagram(coordinateSystem(extent={{-100,-100},{120,100}})), Icon(
        coordinateSystem(extent={{-100,-100},{120,100}})),
    experiment(StopTime=31534200, __Dymola_Algorithm="Dassl"));
end TimeSeriesMassFlow_Temp;
