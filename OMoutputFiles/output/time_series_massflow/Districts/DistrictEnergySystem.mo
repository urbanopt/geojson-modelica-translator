within time_series_massflow.Districts;
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
  // Begin Model Instance for TimeSerMFTLoa_1e8c0844
  // Source template: /model_connectors/load_connectors/templates/TimeSeriesMFT_Instance.mopt
  //
  time_series_massflow.Loads.B5a6b99ec37f4de7f94020090.building TimeSerMFTLoa_1e8c0844
  annotation (Placement(transformation(extent={{50.0,50.0},{70.0,70.0}})));
  //
  // End Model Instance for TimeSerMFTLoa_1e8c0844
  //



  //
  // Begin Model Instance for heaInd_dd88c6b9
  // Source template: /model_connectors/energy_transfer_systems/templates/HeatingIndirect_Instance.mopt
  //
  // heating indirect instance
  time_series_massflow.Substations.HeatingIndirect_5a6b99ec37f4de7f94020090 heaInd_dd88c6b9(
    allowFlowReversal1=true,
    allowFlowReversal2=true,
    show_T=true,
    redeclare package Medium=MediumW,
    mDis_flow_nominal=mDis_flow_nominal_b4aca81d,
    mBui_flow_nominal=mBui_flow_nominal_b4aca81d,
    dpValve_nominal=6000,
    dp1_nominal=500,
    dp2_nominal=500,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_b4aca81d,
    T_a1_nominal=55+273.15,
    T_a2_nominal=35+273.15,
    k=0.1,
    Ti=60,
    reverseActing=true)
    annotation (Placement(transformation(extent={{10.0,10.0},{30.0,30.0}})));
  //
  // End Model Instance for heaInd_dd88c6b9
  //



  //
  // Begin Model Instance for cooInd_793c5f8e
  // Source template: /model_connectors/energy_transfer_systems/templates/CoolingIndirect_Instance.mopt
  //
  // cooling indirect instance
  time_series_massflow.Substations.CoolingIndirect_5a6b99ec37f4de7f94020090 cooInd_793c5f8e(
    redeclare package Medium=MediumW,
    allowFlowReversal1=true,
    allowFlowReversal2=true,
    mDis_flow_nominal=mDis_flow_nominal_e923fac1,
    mBui_flow_nominal=mBui_flow_nominal_e923fac1,
    dp1_nominal=500,
    dp2_nominal=500,
    dpValve_nominal=7000,
    use_Q_flow_nominal=true,
    Q_flow_nominal=Q_flow_nominal_e923fac1,
    // TODO: dehardcode the nominal temperatures?
    T_a1_nominal=273.15+5,
    T_a2_nominal=273.15+13)
    "Indirect cooling energy transfer station ETS."
    annotation (Placement(transformation(extent={{10.0,50.0},{30.0,70.0}})));
  //
  // End Model Instance for cooInd_793c5f8e
  //



  //
  // Begin Model Instance for MyNetworkHeatedWaterStub
  // Source template: /model_connectors/networks/templates/NetworkHeatedWaterStub_Instance.mopt
  //
  // heated water stub
  // TODO: move these components into a single component
  Buildings.Fluid.Sources.MassFlowSource_T supHeaWat(
    redeclare package Medium=MediumW,
    use_m_flow_in=true,
    use_T_in=false,
    T=54+273.15,
    nPorts=1)
    "Heating water supply temperature (district side)."
    annotation (Placement(transformation(extent={{-70.0,-70.0},{-50.0,-50.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinHeaWat(
    redeclare package Medium=MediumW,
    nPorts=1)
    "Heating water sink (district side)"
    annotation (Placement(transformation(extent={{-30.0,-70.0},{-10.0,-50.0}})));

  // NOTE: this differential pressure setpoint is currently utilized by plants elsewhere
  parameter Modelica.Units.SI.Pressure dpSetPoi_MyNetworkHeatedWaterStub=50000
    "Differential pressure setpoint";
  //
  // End Model Instance for MyNetworkHeatedWaterStub
  //



  //
  // Begin Model Instance for MyNetworkChilledWaterStub
  // Source template: /model_connectors/networks/templates/NetworkChilledWaterStub_Instance.mopt
  //
  // chilled water stub
  // TODO: move these components into a single component
  Buildings.Fluid.Sources.MassFlowSource_T supChiWat(
    redeclare package Medium=MediumW,
    use_m_flow_in=true,
    use_T_in=false,
    T=6+273.15,
    nPorts=1)
    "Chilled water supply (district side)."
    annotation (Placement(transformation(extent={{10.0,-70.0},{30.0,-50.0}})));
  Buildings.Fluid.Sources.Boundary_pT sinChiWat1(
    redeclare package Medium=MediumW,
    nPorts=1)
    "Chilled water sink (district side)"
    annotation (Placement(transformation(extent={{50.0,-70.0},{70.0,-50.0}})));
  //
  // End Model Instance for MyNetworkChilledWaterStub
  //




  // Model dependencies

  //
  // Begin Component Definitions for b4aca81d
  // Source template: /model_connectors/couplings/templates/TimeSeriesMFT_HeatingIndirect/ComponentDefinitions.mopt
  //
  Buildings.Controls.OBC.UnitConversions.From_degC THWSET_b4aca81d
    annotation (Placement(transformation(extent={{-70.0,-30.0},{-50.0,-10.0}})));
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_b4aca81d=TimeSerMFTLoa_1e8c0844.mHW_flow_nominal*delHeaWatTemBui/delHeaWatTemDis;
  parameter Modelica.Units.SI.MassFlowRate mBui_flow_nominal_b4aca81d=TimeSerMFTLoa_1e8c0844.mHW_flow_nominal;
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_b4aca81d=TimeSerMFTLoa_1e8c0844.mHW_flow_nominal*4187*delHeaWatTemBui;

  //
  // End Component Definitions for b4aca81d
  //



  //
  // Begin Component Definitions for e923fac1
  // Source template: /model_connectors/couplings/templates/TimeSeriesMFT_CoolingIndirect/ComponentDefinitions.mopt
  //
  Buildings.Controls.OBC.UnitConversions.From_degC TChWSET_e923fac1
    annotation (Placement(transformation(extent={{-30.0,-30.0},{-10.0,-10.0}})));
  parameter Modelica.Units.SI.MassFlowRate mDis_flow_nominal_e923fac1 = TimeSerMFTLoa_1e8c0844.mChW_flow_nominal;
  parameter Modelica.Units.SI.MassFlowRate mBui_flow_nominal_e923fac1 = TimeSerMFTLoa_1e8c0844.mChW_flow_nominal;
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal_e923fac1 = TimeSerMFTLoa_1e8c0844.mChW_flow_nominal*4187*delChiWatTemBui;

  //
  // End Component Definitions for e923fac1
  //



  //
  // Begin Component Definitions for 246d8fed
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_NetworkHeatedWaterStub/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression secMasFloRat_246d8fed(
    // TODO: avoid reaching into other coupling!
    // Warning: the value here is multiplied by 5/7.5 for unknown (undocumented) reasons and needs to be reevaluated in the future.
    y=mDis_flow_nominal_b4aca81d*5/7.5)
    "Secondary loop heated water flow rate."
    annotation (Placement(transformation(extent={{10.0,-30.0},{30.0,-10.0}})));

  //
  // End Component Definitions for 246d8fed
  //



  //
  // Begin Component Definitions for 1381cf21
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_NetworkChilledWaterStub/ComponentDefinitions.mopt
  //
  Modelica.Blocks.Sources.RealExpression secMasFloRat_1381cf21(
    // TODO: avoid reaching into other coupling!
    // TODO: explain the 5/7.5
    y=mDis_flow_nominal_e923fac1*5/7.5)
    "Secondary loop chilled water flow rate."
    annotation (Placement(transformation(extent={{50.0,-30.0},{70.0,-10.0}})));

  //
  // End Component Definitions for 1381cf21
  //



equation
  // Connections

  //
  // Begin Connect Statements for b4aca81d
  // Source template: /model_connectors/couplings/templates/TimeSeriesMFT_HeatingIndirect/ConnectStatements.mopt
  //

  connect(THWSET_b4aca81d.y,heaInd_dd88c6b9.TSetBuiSup)
    annotation (Line(points={{-57.69567254505052,-7.472159991063251},{-57.69567254505052,12.52784000893675},{-37.69567254505052,12.52784000893675},{-17.695672545050513,12.52784000893675},{2.3043274549494868,12.52784000893675},{22.304327454949487,12.52784000893675}},color={0,0,127}));
  connect(TimeSerMFTLoa_1e8c0844.buiMasTem.y[2],THWSET_b4aca81d.u);
  connect(TimeSerMFTLoa_1e8c0844.ports_aHeaWat[1],heaInd_dd88c6b9.port_b2)
    annotation (Line(points={{68.26352005232204,41.34793720465652},{68.26352005232204,21.347937204656517},{48.263520052322036,21.347937204656517},{28.263520052322036,21.347937204656517}},color={0,0,127}));
  connect(TimeSerMFTLoa_1e8c0844.ports_bHeaWat[1],heaInd_dd88c6b9.port_a2)
    annotation (Line(points={{62.45552257025395,34.87554500284238},{62.45552257025395,14.875545002842387},{42.45552257025395,14.875545002842387},{22.455522570253947,14.875545002842387}},color={0,0,127}));

  //
  // End Connect Statements for b4aca81d
  //



  //
  // Begin Connect Statements for e923fac1
  // Source template: /model_connectors/couplings/templates/TimeSeriesMFT_CoolingIndirect/ConnectStatements.mopt
  //

  connect(TChWSET_e923fac1.y,cooInd_793c5f8e.TSetBuiSup)
    annotation (Line(points={{-21.711728486226363,-9.577712109796067},{-21.711728486226363,10.422287890203933},{-21.711728486226363,30.422287890203926},{-21.711728486226363,50.422287890203926},{-1.711728486226363,50.422287890203926},{18.288271513773637,50.422287890203926}},color={0,0,127}));
  connect(TimeSerMFTLoa_1e8c0844.buiMasTem.y[4],TChWSET_e923fac1.u);
  connect(TimeSerMFTLoa_1e8c0844.ports_aChiWat[1],cooInd_793c5f8e.port_b2)
    annotation (Line(points={{37.43200629381073,55.904112258811},{17.43200629381073,55.904112258811}},color={0,0,127}));
  connect(cooInd_793c5f8e.port_a2,TimeSerMFTLoa_1e8c0844.ports_bChiWat[1])
    annotation (Line(points={{45.729073780893,59.33522734627659},{65.729073780893,59.33522734627659}},color={0,0,127}));

  //
  // End Connect Statements for e923fac1
  //



  //
  // Begin Connect Statements for 246d8fed
  // Source template: /model_connectors/couplings/templates/HeatingIndirect_NetworkHeatedWaterStub/ConnectStatements.mopt
  //

  // Heating indirect, Heated water stub connections
  connect(secMasFloRat_246d8fed.y, supHeaWat.m_flow_in)
    annotation (Line(points={{13.905790716877803,-35.18905169149838},{-6.094209283122197,-35.18905169149838},{-26.09420928312219,-35.18905169149838},{-46.09420928312219,-35.18905169149838},{-46.09420928312219,-55.18905169149838},{-66.09420928312218,-55.18905169149838}},color={0,0,127}));
  connect(heaInd_dd88c6b9.port_a1,supHeaWat.ports[1])
    annotation (Line(points={{11.97800188575485,0.2644928509559463},{-8.02199811424515,0.2644928509559463},{-8.02199811424515,-19.735507149044054},{-8.02199811424515,-39.735507149044054},{-28.02199811424515,-39.735507149044054},{-48.02199811424515,-39.735507149044054},{-48.02199811424515,-59.735507149044054},{-68.02199811424515,-59.735507149044054}},color={0,0,127}));
  connect(sinHeaWat.ports[1],heaInd_dd88c6b9.port_b1)
    annotation (Line(points={{-23.309475379108463,-33.07030369051125},{-3.309475379108463,-33.07030369051125},{-3.309475379108463,-13.070303690511253},{-3.309475379108463,6.929696309488747},{-3.309475379108463,26.929696309488747},{16.690524620891537,26.929696309488747}},color={0,0,127}));

  //
  // End Connect Statements for 246d8fed
  //



  //
  // Begin Connect Statements for 1381cf21
  // Source template: /model_connectors/couplings/templates/CoolingIndirect_NetworkChilledWaterStub/ConnectStatements.mopt
  //

  // Cooling indirect, Chilled water stub connections
  connect(secMasFloRat_1381cf21.y, supChiWat.m_flow_in)
    annotation (Line(points={{60.64487488274929,-46.93064471332639},{40.64487488274929,-46.93064471332639},{40.64487488274929,-66.93064471332639},{20.644874882749292,-66.93064471332639}},color={0,0,127}));
  connect(cooInd_793c5f8e.port_a1,supChiWat.ports[1])
    annotation (Line(points={{28.818791842553154,43.87908306843401},{8.818791842553154,43.87908306843401},{8.818791842553154,23.879083068434},{8.818791842553154,3.8790830684339994},{8.818791842553154,-16.120916931566},{8.818791842553154,-36.120916931566},{8.818791842553154,-56.120916931566},{28.818791842553154,-56.120916931566}},color={0,0,127}));
  connect(sinChiWat1.ports[1],cooInd_793c5f8e.port_b1)
    annotation (Line(points={{69.50706402746465,-40.402326380017115},{49.50706402746465,-40.402326380017115},{49.50706402746465,-20.402326380017115},{49.50706402746465,-0.40232638001711507},{49.50706402746465,19.597673619982885},{49.50706402746465,39.597673619982885},{49.50706402746465,59.597673619982885},{29.50706402746465,59.597673619982885}},color={0,0,127}));

  //
  // End Connect Statements for 1381cf21
  //




annotation(
  experiment(
    StopTime=86400,
    Interval=3600,
    Tolerance=1e-06),
  Diagram(
    coordinateSystem(
      preserveAspectRatio=false,
      extent={{-90.0,-90.0},{90.0,90.0}})),
  Documentation(
    revisions="<html>
 <li>
 May 10, 2020: Hagar Elarga<br/>
Updated implementation to handle template needed for GeoJSON to Modelica.
</li>
</html>"));
end DistrictEnergySystem;
