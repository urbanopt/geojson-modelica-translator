within geojson_modelica_translator.model_connectors.templates;
model BuildingSpawnZ6WithCoolingIndirectETS
  package MediumW=Buildings.Media.Water;
  extends PartialBuildingWithCoolingIndirectETS(
    final m1_flow_nominal=mBuiHea_flow_nominal,
    final m2_flow_nominal=mDis_flow_nominal,
    redeclare final package Medium1=MediumW,
    redeclare final package Medium2=MediumW,
    preSou(
      redeclare package Medium=MediumW),
    val(
      redeclare package Medium=MediumW,
      m_flow_nominal=mDis_flow_nominal,
      dpValve_nominal=7000),
    redeclare building bui(
      final idfName=idfName,
      final weaName=weaName,
      T_aChiWat_nominal=280.15,
      T_bChiWat_nominal=285.15,
      nPorts_aHeaWat=1,
      nPorts_bHeaWat=1,
      nPorts_bChiWat=1,
      nPorts_aChiWat=1),
    redeclare CoolingIndirect ets(
      redeclare package Medium=MediumW,
      final mDis_flow_nominal=mDis_flow_nominal,
      final mBui_flow_nominal=mBui_flow_nominal,
      dp1_nominal=500,
      dp2_nominal=500,
      use_Q_flow_nominal=true,
      Q_flow_nominal=-1*(sum(
        bui.terUni.QCoo_flow_nominal)),
      T_a1_nominal=273.15+5,
      T_a2_nominal=273.15+12,
      eta=0.8)
      "Spawn building connected to the indirect cooling ETS model");
  parameter String idfName="modelica://Buildings/Resources/Data/ThermalZones/EnergyPlus/Validation/RefBldgSmallOffice/RefBldgSmallOfficeNew2004_Chicago.idf"
    "Name of the IDF file"
    annotation (Dialog(group="Building model parameters"));
  parameter String weaName="modelica://{{project_name}}/Loads/{{data['load_resources_path']}}/{{data['mos_weather']['filename']}}"
    "Name of the weather file"
    annotation (Dialog(group="Building model parameters"));
  parameter Modelica.SIunits.MassFlowRate mDis_flow_nominal=bui.disFloCoo.m_flow_nominal*(bui.delTBuiCoo/bui.delTDisCoo)
    "Nominal mass flow rate of primary (district) district cooling side";
  parameter Modelica.SIunits.MassFlowRate mBuiHea_flow_nominal=bui.disFloHea.m_flow_nominal
    "Nominal mass flow rate of secondary (building) district heating side";
  parameter Modelica.SIunits.MassFlowRate mBui_flow_nominal=bui.disFloCoo.m_flow_nominal
    "Nominal mass flow rate of secondary (building) district cooling side";
  Buildings.Controls.Continuous.LimPID con(
    final controllerType=Modelica.Blocks.Types.SimpleController.PI,
    final k=1,
    final yMax=1,
    final yMin=0.1,
    final Ti=300,
    final initType=Modelica.Blocks.Types.InitPID.InitialOutput,
    final y_start=1,
    final reverseActing=true)
    "Controller"
    annotation (Placement(transformation(extent={{-12,-124},{8,-104}})));
  Modelica.Blocks.Sources.RealExpression mDis_flowSet(
    y=0.6)
    annotation (Placement(transformation(extent={{-44,-124},{-24,-104}})));
  Modelica.Blocks.Sources.RealExpression mDis_mea(
    y=port_a2.m_flow)
    annotation (Placement(transformation(extent={{-44,-144},{-24,-124}})));
equation
  connect(con.y,val.y)
    annotation (Line(points={{9,-114},{50,-114},{50,-108}},color={0,0,127}));
  connect(con.u_s,mDis_flowSet.y)
    annotation (Line(points={{-14,-114},{-23,-114}},color={0,0,127}));
  connect(mDis_mea.y,con.u_m)
    annotation (Line(points={{-23,-134},{-2,-134},{-2,-126}},color={0,0,127}));
  annotation (
    Icon(
      graphics={
        Bitmap(
          extent={{-72,-62},{62,74}},
          fileName="modelica://Buildings/Resources/Images/ThermalZones/EnergyPlus/EnergyPlusLogo.png")}),
    Diagram(
      coordinateSystem(
        extent={{-100,-140},{100,100}})));
end BuildingSpawnZ6WithCoolingIndirectETS;
