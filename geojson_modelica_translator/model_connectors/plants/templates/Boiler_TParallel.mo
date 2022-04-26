within geojson_modelica_translator.model_connectors.templates;
model Boiler_TParallel
  "Multiple identical boiler"
  extends PartialPlantParallel(
    num=numBoi,
    redeclare Buildings.Fluid.Boilers.BoilerPolynomial boi(
      each Q_flow_nominal=Q_flow_nominal,
      each m_flow_nominal=m_flow_nominal,
      each dp_nominal=dp_nominal,
      each effCur=Buildings.Fluid.Types.EfficiencyCurves.Constant,
      each a={0.9},
      each fue=Buildings.Fluid.Data.Fuels.NaturalGasHigherHeatingValue()));
  parameter Modelica.Units.SI.MassFlowRate m_flow_nominal;
  parameter Modelica.Units.SI.PressureDifference dp_nominal;
  parameter Modelica.Units.SI.HeatFlowRate Q_flow_nominal;
  parameter Integer numBoi;
  Modelica.Blocks.Interfaces.RealOutput TBoiLvg[num](
    unit="K",
    displayUnit="degC")
    "Boiler leaving water temperature."
    annotation (Placement(transformation(extent={{100,30},{120,50}}),iconTransformation(extent={{100,30},{120,50}})));
  Modelica.Blocks.Math.BooleanToReal booToRea[num](
    each final realTrue=1,
    each final realFalse=0)
    "Boolean to real (if true then 1 else 0)"
    annotation (Placement(transformation(extent={{-92,40},{-72,60}})));
  Modelica.Blocks.Interfaces.BooleanInput on[num]
    "On signal of the plant"
    annotation (Placement(transformation(extent={{-120,40},{-100,60}}),iconTransformation(extent={{-120,80},{-100,100}})));
  Buildings.Controls.Continuous.LimPID PI_TBoiLvg(
    u_s(
      unit="K",
      displayUnit="degC"),
    u_m(
      unit="K",
      displayUnit="degC"),
    controllerType=Modelica.Blocks.Types.SimpleController.PI,
    k=1,
    Ti=60,
    reverseActing=true,
    reset=Buildings.Types.Reset.Disabled,
    y_reset=0)
    "Boiler leaving water temperature controller"
    annotation (Placement(transformation(extent={{-72,-40},{-52,-20}})));
  Modelica.Blocks.Math.Product pro[numBoi]
    "Product of PLR and On boiler signal"
    annotation (Placement(transformation(extent={{-36,18},{-16,38}})));
  Buildings.Fluid.Sensors.TemperatureTwoPort senTDisSup(
    redeclare final package Medium=Medium,
    final m_flow_nominal=m_flow_nominal)
    "District-side (primary) supply temperature sensor"
    annotation (Placement(transformation(extent={{-10,-10},{10,10}},rotation=0,origin={76,0})));
  Modelica.Blocks.Interfaces.RealInput THeaWatSet
    "Heating water set point."
    annotation (Placement(transformation(extent={{-10,-10},{10,10}},rotation=0,origin={-110,-60}),iconTransformation(extent={{-10,-10},{10,10}},rotation=0,origin={-110,-60})));
equation
  for i in 1:numBoi loop
    connect(port_a,boi[i].port_a)
      annotation (Line(points={{-100,0},{-2,0}},color={0,127,255}));
    connect(val[i].port_b,senTDisSup.port_a)
      annotation (Line(points={{56,0},{66,0}},color={0,127,255}));
  end for;
  connect(on,booToRea.u)
    annotation (Line(points={{-110,50},{-94,50}},color={255,0,255}));
  connect(boi.port_b,val.port_a)
    annotation (Line(points={{18,0},{36,0}},color={0,127,255}));
  connect(boi.T,TBoiLvg)
    annotation (Line(points={{19,8},{20,8},{20,40},{110,40}},color={0,0,127}));
  connect(booToRea.y,filter.u)
    annotation (Line(points={{-71,50},{-60,50},{-60,84},{-55.2,84}},color={0,0,127}));
  connect(booToRea.y,pro.u1)
    annotation (Line(points={{-71,50},{-60,50},{-60,34},{-38,34}},color={0,0,127}));
  connect(pro.y,boi.y)
    annotation (Line(points={{-15,28},{-12,28},{-12,8},{-4,8}},color={0,0,127}));
  connect(PI_TBoiLvg.y,pro[1].u2)
    annotation (Line(points={{-51,-30},{-44,-30},{-44,22},{-38,22}},color={0,0,127}));
  connect(PI_TBoiLvg.y,pro[2].u2)
    annotation (Line(points={{-51,-30},{-44,-30},{-44,22},{-38,22}},color={0,0,127}));
  connect(port_b,senTDisSup.port_b)
    annotation (Line(points={{100,0},{86,0}},color={0,127,255}));
  connect(senTDisSup.T,PI_TBoiLvg.u_m)
    annotation (Line(points={{76,11},{76,18},{62,18},{62,-74},{-62,-74},{-62,-42}},color={0,0,127}));
  connect(THeaWatSet,PI_TBoiLvg.u_s)
    annotation (Line(points={{-110,-60},{-92,-60},{-92,-30},{-74,-30}},color={0,0,127}));
  annotation (
    Documentation(
      info="<html>
  <p>
  This model implements a heating water parallel boilers. For the boiler model please see
  <a href=\"modelica://Buildings.Fluid.Boilers.BoilerPolynomial\">Buildings.Fluid.Boilers.BoilerPolynomial</a>.
  </p>
  </html>",
      revisions="<html>
  <ul>
  <li>
  June 30, 2020, by Hagar Elarga:<br/>
  First implementation.
  </li>
  </ul>
  </html>"),
    Icon(
      graphics={
        Line(
          points={{-92,0},{0,0}},
          color={28,108,200},
          thickness=1),
        Line(
          points={{0,0},{92,0}},
          color={238,46,47},
          thickness=1),
        Rectangle(
          extent={{-54,54},{54,-54}},
          lineColor={102,44,145})}));
end Boiler_TParallel;
