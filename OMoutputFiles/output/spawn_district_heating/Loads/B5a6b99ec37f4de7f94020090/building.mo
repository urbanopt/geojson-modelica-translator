within spawn_district_heating.Loads.B5a6b99ec37f4de7f94020090;

model building "n-zone EnergyPlus building model based on URBANopt GeoJSON export, with distribution pumps"
  extends Buildings.Experimental.DHC.Loads.BaseClasses.PartialBuilding(redeclare package Medium = Buildings.Media.Water, final have_eleHea = false, final have_eleCoo = false, final have_weaBus = false, final have_heaWat = true, final have_chiWat = true);
  package MediumW = Buildings.Media.Water "Source side medium";
  package MediumA = Buildings.Media.Air "Load side medium";
  parameter Integer nZon = 5 "Number of conditioned thermal zones";
  parameter Integer facMulZon[nZon] = fill(5, nZon) "Scaling factor to be applied to each extensive quantity";
  parameter Modelica.Units.SI.MassFlowRate mLoaCoo_flow_nominal[nZon] "Load side mass flow rate at cooling nominal conditions" annotation(
    Dialog(group = "Nominal condition"));
  parameter Modelica.Units.SI.MassFlowRate mLoaHea_flow_nominal[nZon] "Load side mass flow rate at heating nominal conditions" annotation(
    Dialog(group = "Nominal condition"));
  parameter Modelica.Units.SI.Temperature T_aChiWat_nominal = 280.15 "Supply chilled water nominal temperature";
  parameter Modelica.Units.SI.Temperature T_bChiWat_nominal = 285.15 "Return chilled water nominal temperature";
  parameter Modelica.Units.SI.Temperature T_aHeaWat_nominal = 313.15 "Supply heating water nominal temperature";
  parameter Modelica.Units.SI.Temperature T_bHeaWat_nominal = 308.15 "Return heating water nominal temperature";
  parameter Modelica.Units.SI.HeatFlowRate QHea_flow_nominal[nZon] = {3000, 3000, 3000, 3000, 3000}./facMulZon "Design heating heat flow rate (>=0)" annotation(
    Dialog(group = "Nominal condition"));
  parameter Modelica.Units.SI.HeatFlowRate QCoo_flow_nominal[nZon] = {-8750, -8750, -8750, -8750, -8750}./facMulZon "Design cooling heat flow rate (<=0)" annotation(
    Dialog(group = "Nominal condition"));
  parameter String idfName = "modelica://spawn_district_heating/Loads/Resources/Data/B5a6b99ec37f4de7f94020090/RefBldgSmallOfficeNew2004_v1.4_9.6_5A_USA_IL_CHICAGO-OHARE.idf" "Path of the IDF file";
  parameter String weaName = "modelica://spawn_district_heating/Loads/Resources/Data/B5a6b99ec37f4de7f94020090/USA_CA_San.Francisco.Intl.AP.724940_TMY3.mos" "Path of the mos weather file";
  parameter String epwName = "modelica://spawn_district_heating/Loads/Resources/Data/B5a6b99ec37f4de7f94020090/USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw" "Name of the epw weather file";
  // TODO: Minimum and Maximum TSet: make a function of the outdoor air temperature, type of building,occupancy schedule or woking/idle days?
  // Set these based on cooling and heating setpoints for now based on current parameters in schema.
  Buildings.Controls.OBC.CDL.Continuous.Sources.Constant minTSet[nZon](k = fill(293.15, nZon)) "Minimum temperature setpoint" annotation(
    Placement(transformation(extent = {{-220, 60}, {-200, 80}})));
  Buildings.Controls.OBC.CDL.Continuous.Sources.Constant maxTSet[nZon](k = fill(297.15, nZon)) "Maximum temperature setpoint" annotation(
    Placement(transformation(extent = {{-220, 20}, {-200, 40}})));
  Modelica.Blocks.Sources.Constant qConGai_flow(k = 0) "Convective heat gain" annotation(
    Placement(transformation(extent = {{-66, 128}, {-46, 148}})));
  Modelica.Blocks.Sources.Constant qRadGai_flow(k = 0) "Radiative heat gain" annotation(
    Placement(transformation(extent = {{-66, 168}, {-46, 188}})));
  Modelica.Blocks.Routing.Multiplex3 multiplex3_1 annotation(
    Placement(transformation(extent = {{-20, 128}, {0, 148}})));
  Modelica.Blocks.Sources.Constant qLatGai_flow(k = 0) "Latent heat gain" annotation(
    Placement(transformation(extent = {{-66, 88}, {-46, 108}})));
  // TODO: apply a dynamic layout
  Buildings.ThermalZones.EnergyPlus_9_6_0.ThermalZone znCore_ZN(redeclare package Medium = MediumA, nPorts = 2, zoneName = "Core_ZN") "Thermal zone" annotation(
    Placement(transformation(extent = {{40, -20}, {80, 20}})));
  Buildings.ThermalZones.EnergyPlus_9_6_0.ThermalZone znPerimeter_ZN_1(redeclare package Medium = MediumA, nPorts = 2, zoneName = "Perimeter_ZN_1") "Thermal zone" annotation(
    Placement(transformation(extent = {{40, -20}, {80, 20}})));
  Buildings.ThermalZones.EnergyPlus_9_6_0.ThermalZone znPerimeter_ZN_2(redeclare package Medium = MediumA, nPorts = 2, zoneName = "Perimeter_ZN_2") "Thermal zone" annotation(
    Placement(transformation(extent = {{40, -20}, {80, 20}})));
  Buildings.ThermalZones.EnergyPlus_9_6_0.ThermalZone znPerimeter_ZN_3(redeclare package Medium = MediumA, nPorts = 2, zoneName = "Perimeter_ZN_3") "Thermal zone" annotation(
    Placement(transformation(extent = {{40, -20}, {80, 20}})));
  Buildings.ThermalZones.EnergyPlus_9_6_0.ThermalZone znPerimeter_ZN_4(redeclare package Medium = MediumA, nPorts = 2, zoneName = "Perimeter_ZN_4") "Thermal zone" annotation(
    Placement(transformation(extent = {{40, -20}, {80, 20}})));
  inner Buildings.ThermalZones.EnergyPlus_9_6_0.Building building(idfName = Modelica.Utilities.Files.loadResource(idfName), epwName = Modelica.Utilities.Files.loadResource(epwName), weaName = Modelica.Utilities.Files.loadResource(weaName)) "Building outer component" annotation(
    Placement(transformation(extent = {{40, 60}, {60, 80}})));
  Buildings.Controls.OBC.CDL.Continuous.MultiSum mulSum(nin = nZon) annotation(
    Placement(transformation(extent = {{260, 110}, {280, 130}})));
  Buildings.Controls.OBC.CDL.Continuous.MultiSum mulSum3(nin = 2) if have_pum annotation(
    Placement(transformation(extent = {{260, 70}, {280, 90}})));
  Buildings.Experimental.DHC.Loads.BaseClasses.Examples.BaseClasses.FanCoil4Pipe terUni[nZon](each T_aChiWat_nominal = T_aChiWat_nominal, each T_bChiWat_nominal = T_bChiWat_nominal, redeclare each final package Medium1 = MediumW, redeclare each final package Medium2 = MediumA, each fan(show_T = true), final facMulZon = facMulZon, final QHea_flow_nominal = QHea_flow_nominal, final QCoo_flow_nominal = QCoo_flow_nominal, each T_aLoaHea_nominal = 293.15, each T_aLoaCoo_nominal = 297.15, each T_bHeaWat_nominal = T_bHeaWat_nominal, each T_aHeaWat_nominal = T_aHeaWat_nominal, final mLoaHea_flow_nominal = mLoaHea_flow_nominal, final mLoaCoo_flow_nominal = mLoaCoo_flow_nominal) "Terminal unit" annotation(
    Placement(transformation(extent = {{-140, -2}, {-120, 20}})));
  Buildings.Experimental.DHC.Loads.BaseClasses.FlowDistribution disFloHea(redeclare package Medium = MediumW, allowFlowReversal = true, dp_nominal = 100000, have_pum = have_pum, m_flow_nominal = sum(terUni.mHeaWat_flow_nominal.*terUni.facMulZon), nPorts_a1 = nZon, nPorts_b1 = nZon) "Heating water distribution system" annotation(
    Placement(transformation(extent = {{-236, -188}, {-216, -168}})));
  Buildings.Experimental.DHC.Loads.BaseClasses.FlowDistribution disFloCoo(redeclare package Medium = MediumW, allowFlowReversal = true, dp_nominal = 100000, have_pum = have_pum, m_flow_nominal = sum(terUni.mChiWat_flow_nominal.*terUni.facMulZon), nPorts_a1 = nZon, nPorts_b1 = nZon, typDis = Buildings.Experimental.DHC.Loads.BaseClasses.Types.DistributionType.ChilledWater) "Chilled water distribution system" annotation(
    Placement(transformation(extent = {{-160, -230}, {-140, -210}})));
equation
  connect(qRadGai_flow.y, multiplex3_1.u1[1]) annotation(
    Line(points = {{-45, 178}, {-26, 178}, {-26, 145}, {-22, 145}}, color = {0, 0, 127}, smooth = Smooth.None));
  connect(qConGai_flow.y, multiplex3_1.u2[1]) annotation(
    Line(points = {{-45, 138}, {-22, 138}}, smooth = Smooth.None));
  connect(qLatGai_flow.y, multiplex3_1.u3[1]) annotation(
    Line(points = {{-22, 131}, {-26, 131}, {-26, 98}, {-45, 98}}, color = {0, 0, 127}));
  connect(disFloHea.port_a, ports_aHeaWat[1]) annotation(
    Line(points = {{-300, 0}, {-280, 0}, {-280, -178}, {-236, -178}}, color = {0, 127, 255}));
  connect(disFloHea.port_b, ports_bHeaWat[1]) annotation(
    Line(points = {{-216, -178}, {260, -178}, {260, 0}, {300, 0}}, color = {0, 127, 255}));
  connect(disFloCoo.port_a, ports_aChiWat[1]) annotation(
    Line(points = {{-300, 0}, {-280, 0}, {-280, -220}, {-160, -220}}, color = {0, 127, 255}));
  connect(disFloCoo.port_b, ports_bChiWat[1]) annotation(
    Line(points = {{-140, -220}, {280, -220}, {280, 0}, {300, 0}}, color = {0, 127, 255}));
  connect(mulSum.y, PFan) annotation(
    Line(points = {{282, 120}, {302, 120}, {302, 120}, {320, 120}}, color = {0, 0, 127}));
  if have_pum then
    connect(PPum, mulSum3.y) annotation(
      Line(points = {{320, 80}, {302, 80}, {302, 80}, {282, 80}}, color = {0, 0, 127}));
    connect(disFloHea.PPum, mulSum3.u[1]) annotation(
      Line(points = {{-215, -186}, {220.5, -186}, {220.5, 81}, {258, 81}}, color = {0, 0, 127}));
    connect(disFloCoo.PPum, mulSum3.u[2]) annotation(
      Line(points = {{-139, -228}, {224, -228}, {224, 79}, {258, 79}}, color = {0, 0, 127}));
  end if;
  connect(disFloHea.QActTot_flow, QHea_flow) annotation(
    Line(points = {{-215, -184}, {-2, -184}, {-2, -182}, {212, -182}, {212, 280}, {320, 280}}, color = {0, 0, 127}));
  connect(disFloCoo.QActTot_flow, QCoo_flow) annotation(
    Line(points = {{-139, -226}, {28, -226}, {28, -224}, {216, -224}, {216, 240}, {320, 240}}, color = {0, 0, 127}));
  for i in 1:nZon loop
    connect(terUni[i].PFan, mulSum.u[i]) annotation(
      Line(points = {{-119.167, 9}, {-100, 9}, {-100, 220}, {220, 220}, {220, 118.333}, {258, 118.333}}, color = {0, 0, 127}));
    connect(disFloCoo.ports_a1[i], terUni[i].port_bChiWat) annotation(
      Line(points = {{-140, -214}, {-38, -214}, {-38, 1.66667}, {-120, 1.66667}}, color = {0, 127, 255}));
    connect(disFloCoo.ports_b1[i], terUni[i].port_aChiWat) annotation(
      Line(points = {{-160, -214}, {-260, -214}, {-260, 1.66667}, {-140, 1.66667}}, color = {0, 127, 255}));
    connect(disFloHea.ports_a1[i], terUni[i].port_bHeaWat) annotation(
      Line(points = {{-220, -164}, {-40, -164}, {-40, -0.166667}, {-120, -0.166667}}, color = {0, 127, 255}));
    connect(disFloHea.ports_b1[i], terUni[i].port_aHeaWat) annotation(
      Line(points = {{-240, -164}, {-260, -164}, {-260, -0.166667}, {-140, -0.166667}}, color = {0, 127, 255}));
    connect(terUni[i].mReqChiWat_flow, disFloCoo.mReq_flow[i]) annotation(
      Line(points = {{-119.167, 3.5}, {-104, 3.5}, {-104, -80}, {-180, -80}, {-180, -224}, {-161, -224}}, color = {0, 0, 127}));
    connect(terUni[i].mReqHeaWat_flow, disFloHea.mReq_flow[i]) annotation(
      Line(points = {{-119.167, 5.33333}, {-100, 5.33333}, {-100, -90.5}, {-241, -90.5}, {-241, -174}}, color = {0, 0, 127}));
    connect(terUni[i].TSetHea, minTSet[i].y) annotation(
      Line(points = {{-140.833, 14.5}, {-160, 14.5}, {-160, 70}, {-198, 70}}, color = {0, 0, 127}));
    connect(terUni[i].TSetCoo, maxTSet[i].y) annotation(
      Line(points = {{-140.833, 12.6667}, {-164, 12.6667}, {-164, 30}, {-198, 30}}, color = {0, 0, 127}));
  end for;
//----------------Depending on number of thermal zones-----------------
  connect(multiplex3_1.y, znCore_ZN.qGai_flow) annotation(
    Line(points = {{1, 138}, {20, 138}, {20, 30}, {22, 30}}, color = {0, 0, 127}));
  connect(znCore_ZN.ports[1], terUni[1].port_aLoa) annotation(
    Line(points = {{42, -119.2}, {-8, -119.2}, {-8, 18.1667}, {-120, 18.1667}}, color = {0, 127, 255}));
  connect(znCore_ZN.ports[2], terUni[1].port_bLoa) annotation(
    Line(points = {{-140, 18.1667}, {-20, 18.1667}, {-20, -119.2}, {46, -119.2}}, color = {0, 127, 255}));
  connect(znCore_ZN.TAir, terUni[1].TSen) annotation(
    Line(points = {{81, 13.8}, {80, 13.8}, {80, 160}, {-152, 160}, {-152, 10.8333}, {-140.833, 10.8333}}, color = {0, 0, 127}));
  connect(multiplex3_1.y, znPerimeter_ZN_1.qGai_flow) annotation(
    Line(points = {{1, 138}, {20, 138}, {20, 30}, {22, 30}}, color = {0, 0, 127}));
  connect(znPerimeter_ZN_1.ports[1], terUni[2].port_aLoa) annotation(
    Line(points = {{42, -119.2}, {-8, -119.2}, {-8, 18.1667}, {-120, 18.1667}}, color = {0, 127, 255}));
  connect(znPerimeter_ZN_1.ports[2], terUni[2].port_bLoa) annotation(
    Line(points = {{-140, 18.1667}, {-20, 18.1667}, {-20, -119.2}, {46, -119.2}}, color = {0, 127, 255}));
  connect(znPerimeter_ZN_1.TAir, terUni[2].TSen) annotation(
    Line(points = {{81, 13.8}, {80, 13.8}, {80, 160}, {-152, 160}, {-152, 10.8333}, {-140.833, 10.8333}}, color = {0, 0, 127}));
  connect(multiplex3_1.y, znPerimeter_ZN_2.qGai_flow) annotation(
    Line(points = {{1, 138}, {20, 138}, {20, 30}, {22, 30}}, color = {0, 0, 127}));
  connect(znPerimeter_ZN_2.ports[1], terUni[3].port_aLoa) annotation(
    Line(points = {{42, -119.2}, {-8, -119.2}, {-8, 18.1667}, {-120, 18.1667}}, color = {0, 127, 255}));
  connect(znPerimeter_ZN_2.ports[2], terUni[3].port_bLoa) annotation(
    Line(points = {{-140, 18.1667}, {-20, 18.1667}, {-20, -119.2}, {46, -119.2}}, color = {0, 127, 255}));
  connect(znPerimeter_ZN_2.TAir, terUni[3].TSen) annotation(
    Line(points = {{81, 13.8}, {80, 13.8}, {80, 160}, {-152, 160}, {-152, 10.8333}, {-140.833, 10.8333}}, color = {0, 0, 127}));
  connect(multiplex3_1.y, znPerimeter_ZN_3.qGai_flow) annotation(
    Line(points = {{1, 138}, {20, 138}, {20, 30}, {22, 30}}, color = {0, 0, 127}));
  connect(znPerimeter_ZN_3.ports[1], terUni[4].port_aLoa) annotation(
    Line(points = {{42, -119.2}, {-8, -119.2}, {-8, 18.1667}, {-120, 18.1667}}, color = {0, 127, 255}));
  connect(znPerimeter_ZN_3.ports[2], terUni[4].port_bLoa) annotation(
    Line(points = {{-140, 18.1667}, {-20, 18.1667}, {-20, -119.2}, {46, -119.2}}, color = {0, 127, 255}));
  connect(znPerimeter_ZN_3.TAir, terUni[4].TSen) annotation(
    Line(points = {{81, 13.8}, {80, 13.8}, {80, 160}, {-152, 160}, {-152, 10.8333}, {-140.833, 10.8333}}, color = {0, 0, 127}));
  connect(multiplex3_1.y, znPerimeter_ZN_4.qGai_flow) annotation(
    Line(points = {{1, 138}, {20, 138}, {20, 30}, {22, 30}}, color = {0, 0, 127}));
  connect(znPerimeter_ZN_4.ports[1], terUni[5].port_aLoa) annotation(
    Line(points = {{42, -119.2}, {-8, -119.2}, {-8, 18.1667}, {-120, 18.1667}}, color = {0, 127, 255}));
  connect(znPerimeter_ZN_4.ports[2], terUni[5].port_bLoa) annotation(
    Line(points = {{-140, 18.1667}, {-20, 18.1667}, {-20, -119.2}, {46, -119.2}}, color = {0, 127, 255}));
  connect(znPerimeter_ZN_4.TAir, terUni[5].TSen) annotation(
    Line(points = {{81, 13.8}, {80, 13.8}, {80, 160}, {-152, 160}, {-152, 10.8333}, {-140.833, 10.8333}}, color = {0, 0, 127}));
  annotation(
    Diagram(coordinateSystem(extent = {{-300, -300}, {300, 300}})),
    Icon(coordinateSystem(extent = {{-300, -300}, {300, 300}}), graphics = {Bitmap(extent = {{-72, -88}, {50, 55}}, fileName = "modelica://Buildings/Resources/Images/ThermalZones/EnergyPlus/EnergyPlusLogo.png")}),
    Documentation(info = "<html>
<p>
 This is a simplified building model based on EnergyPlus
 building envelope model.
 It was generated from translating a GeoJSON model specified within URBANopt UI.
 The heating and cooling loads are computed with a four-pipe
 fan coil unit model derived from
 <a href=\"modelica://Buildings.Experimental.DHC.Loads.BaseClasses.PartialTerminalUnit\">
 Buildings.Experimental.DHC.Loads.BaseClasses.PartialTerminalUnit</a>
 and connected to the room model by means of fluid ports.
</p>
</html>", revisions = "<html>
<ul>
<li>
March 12, 2020: Hagar Elarga<br/>
Updated implementation to handle template needed for GeoJSON to Modelica.
</li>
<li>
February 21, 2020, by Antoine Gautier:<br/>
First implementation.
</li>
</ul>
</html>"));
end building;
