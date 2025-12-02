within DES_5G_Variable_Dymola.Districts;
model district
  "Series connection with variable district water mass flow rate"
  extends PartialSeries(
                  redeclare
      DES_5G_Variable_Dymola.Loads.buildingHPTrio
      bui[nBui](
      TChiWatSup_nominal=280.15,
      final filNam=filNam), datDes(
      nBui=3,
      mPumDis_flow_nominal=19.577,
      mPla_flow_nominal=19.577,
      mSto_flow_nominal=1.9577000000000002,
      dp_length_nominal=250,
      epsPla=0.935,
      lDis = { 0.5, 0.5, 0.5},
      lCon = { 0.5, 0.5, 0.5}));
  parameter String filNam[nBui]={
    "modelica://DES_5G_Variable_Dymola/Resources/Data/Districts/1/B2.mos",
    "modelica://DES_5G_Variable_Dymola/Resources/Data/Districts/7/B6.mos",
    "modelica://DES_5G_Variable_Dymola/Resources/Data/Districts/8/B11.mos"}
    "Library paths of the files with thermal loads as time series";

  Modelica.Blocks.Sources.Constant masFloDisPla(
    k=datDes.mPla_flow_nominal)
    "District water flow rate to plant"
    annotation (Placement(transformation(extent={{-250,10},{-230,30}})));
  Buildings.Controls.OBC.CDL.Reals.Sources.Constant THotWatSupSet[nBui](
    k=fill(63 + 273.15, nBui))
    "Hot water supply temperature set point"
    annotation (Placement(transformation(extent={{-190,170},{-170,190}})));
  Buildings.Controls.OBC.CDL.Reals.Sources.Constant TColWat[nBui](
    k=fill(15 + 273.15, nBui))
    "Cold water temperature"
    annotation (Placement(transformation(extent={{-160,150},{-140,170}})));
  Buildings.DHC.Networks.Controls.MainPump1Pipe conPum(
    nMix=nBui,
    nBui=nBui,
    nSou=2,
    TMin=279.15,
    TMax=290.15) "Main pump controller"
    annotation (Placement(transformation(extent={{-280,-70},{-260,-50}})));
  Buildings.Controls.OBC.CDL.Reals.MultiplyByParameter gaiPumDis(k=datDes.mPumDis_flow_nominal)
    "Scale with nominal mass flow rate for distribution pump"
    annotation (Placement(transformation(extent={{-240,-70},{-220,-50}})));
Buildings.Controls.OBC.CDL.Reals.MultiplyByParameter gaiPumSto(k=datDes.mSto_flow_nominal)
    "Scale with nominal mass flow rate for storage GHX pump"
    annotation (Placement(transformation(extent={{-240,-112},{-220,-92}})));
equation
  connect(masFloDisPla.y, pla.mPum_flow) annotation (Line(points={{-229,20},{
          -184,20},{-184,4.66667},{-161.333,4.66667}},
                                  color={0,0,127}));
  connect(THotWatSupSet.y, bui.THotWatSupSet) annotation (Line(points={{-168,
          180},{-40,180},{-40,183},{-12,183}}, color={0,0,127}));
  connect(TColWat.y, bui.TColWat) annotation (Line(points={{-138,160},{-40,160},
          {-40,164},{-8,164},{-8,168}},
                                color={0,0,127}));
  connect(pumDis.m_flow_in, gaiPumDis.y)
    annotation (Line(points={{68,-60},{-218,-60}}, color={0,0,127}));
  connect(conPum.y, gaiPumDis.u)
    annotation (Line(points={{-258.462,-60},{-242,-60}},
                                                     color={0,0,127}));
  connect(dis.TOut, conPum.TMix) annotation (Line(points={{22,134},{30,134},{30,
          120},{-300,120},{-300,-53},{-281.692,-53}},
                                         color={0,0,127}));
  connect(TDisWatRet.T, conPum.TSouIn[1]) annotation (Line(points={{69,0},{60,0},
          {60,80},{-304,80},{-304,-57.25},{-281.692,-57.25}},
                                            color={0,0,127}));
  connect(TDisWatBorLvg.T, conPum.TSouIn[2]) annotation (Line(points={{-91,-40},
          {-290,-40},{-290,-58},{-281.692,-58},{-281.692,-56.75}},
                                                  color={0,0,127}));
  connect(TDisWatBorLvg.T, conPum.TSouOut[1]) annotation (Line(points={{-91,-40},
          {-290,-40},{-290,-62.25},{-281.692,-62.25}},    color={0,0,127}));
  connect(TDisWatSup.T, conPum.TSouOut[2]) annotation (Line(points={{-91,20},{
          -100,20},{-100,60},{-296,60},{-296,-61.75},{-281.692,-61.75}},
                                                   color={0,0,127}));
  connect(gaiPumSto.u, gaiPumDis.u) annotation (Line(points={{-242,-102},{-248,
          -102},{-248,-60},{-242,-60}}, color={0,0,127}));
  connect(gaiPumSto.y, pumSto.m_flow_in) annotation (Line(points={{-218,-102},{
          -210,-102},{-210,-62},{-180,-62},{-180,-68}}, color={0,0,127}));
  connect(bui.QCoo_flow, conPum.QCoo_flow) annotation (Line(points={{7,168},{6,
          168},{6,156},{-130,156},{-130,130},{-312,130},{-312,-66},{-281.692,
          -66}},                                                               color={0,0,127}));
  annotation (
  Diagram(
  coordinateSystem(preserveAspectRatio=false, extent={{-360,-260},{360,260}})),
  experiment(
      StopTime=86400,
      Interval=299.99988,
      Tolerance=1e-06,
      __Dymola_Algorithm="Dassl"),
    Documentation(info="<html>
<p>
This model is identical to
<a href=\"Buildings.DHC.Examples.Combined.SeriesConstantFlow\">
Buildings.DHC.Examples.Combined.SeriesConstantFlow</a>
except for the pipe diameter and the control of the main circulation pump.
Rather than having a constant mass flow rate, the mass flow rate is varied
based on the mixing temperatures after each agent.
If these mixing temperatures are sufficiently far away from the minimum or maximum
allowed loop temperature, then the mass flow rate is reduced to save pump energy.
</p>
</html>", revisions="<html>
<ul>
<li>
November 17, 2023, by Nicholas Long:<br/>
Break out the mass flow rate gain multiplier for the GHX/Storage.
</li>
<li>
November 1, 2023, by Nicholas Long:<br/>
Templatized for direct use in GMT with n-building connectors.<br/>
Changes include: removing dymola run command tied to MBL path, adding
a constant for borehole field mass flow rate (no longer tied to main
distribution loop).
</li>
<li>
February 23, 2021, by Antoine Gautier:<br/>
Refactored with base classes from the <code>DHC</code> package.<br/>
This is for
<a href=\"https://github.com/lbl-srg/modelica-buildings/issues/1769\">
issue 1769</a>.
</li>
<li>
January 12, 2020, by Michael Wetter:<br/>
Added documentation.
</li>
</ul>
</html>"),
      __Dymola_experimentSetupOutput);
end district;
