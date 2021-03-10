within geojson_modelica_translator.model_connectors.templates;
partial model PartialPlantParallel
  "Partial source plant model with associated valves"
  extends PartialPlantParallelInterface;
  extends ValveParameters(
    final deltaM=0.1,
    rhoStd=Medium.density_pTX(
      101325,
      273.15+4,
      Medium.X_default));
  extends Buildings.Applications.DataCenters.ChillerCooled.Equipment.BaseClasses.SignalFilter(
    final numFil=num);
  constant Boolean homotopyInitialization=true
    "= true, use homotopy method"
    annotation (HideResult=true);
  // Isolation valve parameters
  parameter Real l(
    min=1e-10,
    max=1)=0.0001
    "Valve leakage, l=Kv(y=0)/Kv(y=1)"
    annotation (Dialog(group="Two-way valve"));
  parameter Real kFixed(
    unit="",
    min=0)=m_flow_nominal ./ sqrt(
    dp_nominal)
    "Flow coefficient of fixed resistance that may be in series with valve 1, k=m_flow/sqrt(dp), with unit=(kg.m)^(1/2)."
    annotation (Dialog(group="Two-way valve"));
  parameter Integer num=2
    "Number of equipment";
  Buildings.Fluid.Actuators.Valves.TwoWayLinear val[num](
    redeclare each package Medium=Medium,
    each final allowFlowReversal=allowFlowReversal,
    each final m_flow_nominal=m_flow_nominal,
    each final deltaM=deltaM,
    each dpFixed_nominal=dp_nominal,
    each final show_T=show_T,
    each final homotopyInitialization=homotopyInitialization,
    each final use_inputFilter=false,
    each final riseTime=riseTimeValve,
    each final init=initValve,
    final y_start=yValve_start,
    each final l=l,
    each final kFixed=kFixed,
    each final dpValve_nominal=dpValve_nominal,
    each final CvData=Buildings.Fluid.Types.CvTypes.OpPoint,
    each final from_dp=from_dp,
    each final linearized=linearizeFlowResistance,
    each final rhoStd=rhoStd)
    "Isolation valves for on/off use"
    annotation (Placement(transformation(extent={{-10,-10},{10,10}},rotation=0,origin={46,0})));
  replaceable Buildings.Fluid.Boilers.BoilerPolynomial boi[num](
    redeclare each final package Medium=Medium,
    each from_dp=true,
    each T_start=293.15)
    annotation (Placement(transformation(extent={{-20,-10},{0,10}})));
initial equation
  assert(
    homotopyInitialization,
    "In "+getInstanceName()+": The constant homotopyInitialization has been modified from its default value. This constant will be removed in future releases.",
    level=AssertionLevel.warning);
equation
  connect(y_actual,val.y)
    annotation (Line(points={{-20,74},{46,74},{46,12}},color={0,0,127}));
  annotation (
    Documentation(
      info="<html>
<p>
A partial model of parallel connected heating water boilers. Each boiler is isolated
with an on/off two way valve.
</p>
</html>",
      revisions="<html>
<ul>
<li>
August 20, 2020, by Hagar Elarga:<br/>
First implementation.
</li>
</ul>
</html>"));
end PartialPlantParallel;
