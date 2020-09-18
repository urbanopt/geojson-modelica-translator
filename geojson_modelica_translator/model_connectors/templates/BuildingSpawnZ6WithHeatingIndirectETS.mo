within geojson_modelica_translator.model_connectors.templates;
model BuildingSpawnZ6WithCoolingIndirectETS
  package MediumW=Buildings.Media.Water;
  extends PartialBuildingWithCoolingIndirectETS(
    final m1_flow_nominal=mBuiHea_flow_nominal,
    final m2_flow_nominal=mBuiCoo_flow_nominal,
    redeclare final package Medium1=MediumW,
    redeclare final package Medium2=MediumW,
    redeclare building bui(
      final have_pum=true,
      final idfName=idfName,
      final weaName=weaName,
      T_aChiWat_nominal=280.15,
      T_bChiWat_nominal=285.15,
      T_aHeaWat_nominal=323.15,
      T_bHeaWat_nominal=315.15,
      nPorts_aChiWat=1,
      nPorts_bChiWat=1,
      nPorts_bHeaWat=1,
      nPorts_aHeaWat=1),
    redeclare HeatingIndirect ets(
      redeclare package Medium=MediumW,
      final mDis_flow_nominal=mDisHea_flow_nominal,
      final mBui_flow_nominal=mBuiHea_flow_nominal,
      yMax=yMax,
      yMin=yMin,
      dp1_nominal=500,
      dp2_nominal=500,
      use_Q_flow_nominal=true,
      Q_flow_nominal=(sum(
        bui.terUni.QHea_flow_nominal)),
      T_a1_nominal=328.15,
      T_a2_nominal=323.15,
      eta=0.8,
      xi_start=0),
    preSou(
      redeclare package Medium=MediumW));
  parameter String idfName="modelica://Buildings/Resources/Data/ThermalZones/EnergyPlus/Validation/RefBldgSmallOffice/RefBldgSmallOfficeNew2004_Chicago.idf"
    "Name of the IDF file"
    annotation (Dialog(group="Building model parameters"));
  parameter String weaName="modelica://Buildings/Resources/weatherdata/USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.mos"
    "Name of the weather file"
    annotation (Dialog(group="Building model parameters"));
  parameter Modelica.SIunits.MassFlowRate mDisHea_flow_nominal=bui.disFloHea.m_flow_nominal*(bui.delTBuiHea/bui.delTDisHea)
    "Nominal mass flow rate of primary (district) district heating side";
  parameter Modelica.SIunits.MassFlowRate mDisCoo_flow_nominal=bui.disFloCoo.m_flow_nominal*(bui.delTBuiCoo/bui.delTDisCoo)
    "Nominal mass flow rate of primary (district) district cooling side";
  parameter Modelica.SIunits.MassFlowRate mBuiHea_flow_nominal=bui.disFloHea.m_flow_nominal
    "Nominal mass flow rate of secondary (building) district heating side";
  parameter Modelica.SIunits.MassFlowRate mBuiCoo_flow_nominal=bui.disFloCoo.m_flow_nominal
    "Nominal mass flow rate of secondary (building) district cooling side";
  parameter Real yMax(
    start=1)=1
    "Upper limit of output";
  parameter Real yMin=0
    "Lower limit of output";
equation
  connect(TSetWat,ets.TSetBuiSup)
    annotation (Line(points={{-120,20},{-88,20},{-88,-54},{-34,-54}},color={0,0,127}));
  connect(port_a2,bui.ports_aChiWat[1])
    annotation (Line(points={{100,-60},{60,-60},{60,80},{-60,80},{-60,20},{-30,20}},color={0,127,255}));
  connect(bui.ports_bChiWat[1],port_b2)
    annotation (Line(points={{30,20},{50,20},{50,-6},{-80,-6},{-80,-60},{-100,-60}},color={0,127,255}));
  connect(bui.ports_bHeaWat[1],ets.port_a2)
    annotation (Line(points={{30,32},{54,32},{54,-72},{32,-72}},color={0,127,255}));
  connect(ets.port_b2,bui.ports_aHeaWat[1])
    annotation (Line(points={{-28,-72},{-54,-72},{-54,32},{-30,32}},color={0,127,255}));
  connect(ets.port_b1,port_b1)
    annotation (Line(points={{32,-36},{80,-36},{80,60},{100,60}},color={0,127,255}));
  connect(preSou.ports[1],ets.port_b2)
    annotation (Line(points={{-60,-88},{-28,-88},{-28,-72}},color={0,127,255}));
  connect(port_a1,ets.port_a1)
    annotation (Line(points={{-100,60},{-72,60},{-72,-36},{-28,-36}},color={0,127,255}));
  annotation (
    Icon(
      graphics={
        Bitmap(
          extent={{-72,-62},{62,74}},
          fileName="modelica://Buildings/Resources/Images/ThermalZones/EnergyPlus/EnergyPlusLogo.png")}),
    Diagram(
      coordinateSystem(
        extent={{-100,-100},{100,100}})));
end BuildingSpawnZ6WithHeatingIndirectETS;
