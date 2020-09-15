within geojson_modelica_translator.model_connectors.templates;
model BuildingSpawnZ6WithCoolingIndirectETS
  package MediumW=Buildings.Media.Water;
  extends PartialBuildingWithCoolingIndirectETS(
    final m1_flow_nominal=mBuiHea_flow_nominal,
    final m2_flow_nominal=mBuiCoo_flow_nominal,
    redeclare final package Medium1=MediumW,
    redeclare final package Medium2=MediumW,
    redeclare DHC.Loads.Examples.BaseClasses.BuildingSpawnZ6 bui(
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
;
