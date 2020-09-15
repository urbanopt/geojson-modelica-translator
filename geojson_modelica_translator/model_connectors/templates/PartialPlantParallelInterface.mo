within geojson_modelica_translator.model_connectors.templates;
partial model PartialPlantParallelInterface
  "Partial model that implements the interface for parallel plants"
  extends Buildings.Fluid.Interfaces.PartialTwoPortInterface;
  extends Buildings.Fluid.Interfaces.TwoPortFlowResistanceParameters(
    final computeFlowResistance=true);
  //parameter Integer num "Number of equipment";
  annotation (
    Icon(
      coordinateSystem(
        preserveAspectRatio=false),
      graphics={
        Rectangle(
          extent={{-80,80},{80,-80}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={95,95,95},
          fillPattern=FillPattern.Solid)}),
    Documentation(
      revisions="<html>
<ul>
<li>
August 25, 2020, by Hagar Elarga:<br/>
First implementation.
</li>
</ul>
</html>",
      info="<html>
</html>"));
end PartialPlantParallelInterface;
