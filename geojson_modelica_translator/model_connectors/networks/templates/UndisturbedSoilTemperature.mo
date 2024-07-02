within geojson_modelica_translator.model_connectors.templates;
model UndisturbedSoilTemperature
  "Undisturbed soil temperature"
  parameter Modelica.Units.SI.Length dep
    "Soil depth";
  replaceable parameter Buildings.Fluid.Geothermal.Borefields.Data.Soil.SandStone soiDat
    "Soil thermal properties";
  parameter Modelica.Units.SI.Temperature TSurMea(
    displayUnit="degC")
    "Mean annual surface temperature";
  parameter Modelica.Units.SI.TemperatureDifference TSurAmp1
    "First-order surface temperature amplitude";
  parameter Modelica.Units.SI.TemperatureDifference TSurAmp2
    "Second-order surface temperature amplitude";
  parameter Modelica.Units.SI.Duration cosPha1(
    displayUnit="d")
    "First phase lag of soil surface temperature, in days";
  parameter Modelica.Units.SI.Duration cosPha2(
    displayUnit="d")
    "Second phase lag of soil surface temperature, in days";
  Modelica.Units.SI.Temperature T
    "Undisturbed soil temperature at depth dep";
protected
  constant Modelica.Units.SI.Angle pi=Modelica.Constants.pi;
  constant Modelica.Units.SI.Duration Year=365
    "Annual period length, in days";
  parameter Modelica.Units.SI.ThermalDiffusivity soiDif=soiDat.kSoi/soiDat.cSoi/soiDat.dSoi*60*60*24
    "Soil diffusivity";
  parameter Real pha1=-dep*(pi/soiDif/Year)^0.5
    "First phase angle of ground temperature sinusoid";
  parameter Real pha2=-dep*(2*pi/soiDif/Year)^0.5
    "Second phase angle of ground temperature sinusoid";
equation
  T=TSurMea-TSurAmp1*exp(
    pha1)*cos(
    2*pi*(time/60/60/24-cosPha1)/Year+pha1)-TSurAmp2*exp(
    pha2)*cos(
    4*pi*(time/60/60/24-cosPha2)/Year+pha2);
  annotation (
    Placement(
      transformation(
        extent={{-6,-104},{6,-92}}),
      iconTransformation(
        extent={{-6,-104},{6,-92}})),
    Icon(
      coordinateSystem(
        preserveAspectRatio=false),
      graphics={
        Text(
          textColor={0,0,255},
          extent={{-150,110},{150,150}},
          textString="%name"),
        Rectangle(
          extent={{-100,20},{100,-100}},
          lineColor={0,0,0},
          fillColor={211,168,137},
          fillPattern=FillPattern.Backward),
        Rectangle(
          extent={{-100,20},{100,26}},
          lineColor={0,0,0},
          fillColor={0,255,128},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{-100,26},{100,100}},
          lineColor={0,0,0},
          fillColor={85,170,255},
          fillPattern=FillPattern.Solid),
        Line(
          points={{0,38},{0,-60}},
          color={191,0,0},
          thickness=1),
        Polygon(
          points={{16,-60},{-16,-60},{0,-92},{16,-60}},
          lineColor={191,0,0},
          fillColor={191,0,0},
          fillPattern=FillPattern.Solid),
        Text(
          extent={{-38,-38},{-100,-100}},
          textColor={0,0,0},
          textString="K")}),
    Diagram(
      coordinateSystem(
        preserveAspectRatio=false)),
    Documentation(
      info="<html>
<p>
This model provides a prescribed temperature boundary condition for buried objects,
where the temperature is computed per the ASCE (1996) equation:
</p>
<p>
<img alt=\"image\" src=\"modelica://Buildings/Resources/Images/BoundaryConditions/GroundTemperature/UndisturbedSoilTemperature.svg\" />
</p>
<p>
where: <br>
<i>T<sub>s,z</sub></i> = ground temperature at depth <i>z</i>,<br>
<i>&tau;</i> = annual period length (constant 365.25 days),<br>
<i>&alpha;</i> = soil thermal diffusivity (assumed constant throughout the year), <br>
<i>t</i> = time, <br>
<i>T<sub>ms</sub></i> = mean annual surface temperature, <br>
<i>A<sub>s</sub></i> = temperature amplitude throughout the year (max - min), <br>
<i>t<sub>lag</sub></i> = phase lag of the surface temperature sinusoid
</p>

<h4>Corrections</h4>

<p>
Without correction, this model assumes that the surface temperature (depth = 0) is
equal to the air temperature, which is acceptable for most design calculations.<br>
For more accurate calculation, this model provides methods to compensate for
the convective thermal resistance and the impact of surface cover.
</p>
<p>
The convective thermal resistance can be modeled as a virtual equivalent soil layer
by setting the flag <i>useCon</i> to <code>true</code> and specifying the
heat transfer coefficient <i>hSur</i>.<br/>
This correction would result in a larger delay and dampening of the
resulting sinusoid.
</p>
<p>
The impact of surface cover on soil temperature can be modeled using
<i>n</i>-factors by setting the flag <i>useNFac</i> to <code>true</code> and
specifying the thawing and freezing <i>n</i>-factors at the surface. <br>

More information about <i>n</i>-factors correction can be found in the documentation
for <a href=\"modelica://Buildings.BoundaryConditions.GroundTemperature.BaseClasses.surfaceTemperature\">
Buildings.BoundaryConditions.GroundTemperature.BaseClasses.surfaceTemperature</a>.
</p>
<p>
Since <i>n</i>-factors incorporate the effect of surface convection,
both corrections would typically not be applied simultaneously. <br>
</p>

<h4>References</h4>
<p>
ASCE (1996). <i>Cold Regions Utilities Monograph</i>. D.W. Smith, Technical Editor.
</p>

</html>",
      revisions="<html>
<ul>
<li>
March 17, 2021, by Baptiste Ravache:<br/>
First implementation.
</li>
</ul>
</html>"));
end UndisturbedSoilTemperature;
