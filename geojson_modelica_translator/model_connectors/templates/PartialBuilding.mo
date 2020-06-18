//within geojson_modelica_translator.model_connectors.templates
partial model PartialBuilding
  "Partial class for building model"
  replaceable package Medium=Modelica.Media.Interfaces.PartialMedium
    "Source side medium (heating or chilled water)"
    annotation (choices(choice(redeclare package Medium=Buildings.Media.Water
      "Water"), choice(redeclare package Medium=Buildings.Media.Antifreeze.PropyleneGlycolWater(property_T=293.15, X_a=0.40)
      "Propylene glycol water, 40% mass fraction")));
  parameter Integer nPorts_aHea=0
    "Number of inlet fluid ports on source side"
    annotation (Evaluate=true, Dialog(connectorSizing=true));
  parameter Integer nPorts_bHea=0
    "Number of outlet fluid ports on source side"
    annotation (Evaluate=true, Dialog(connectorSizing=true));
  parameter Integer nPorts_aCoo=0
    "Number of inlet fluid ports on source side"
    annotation (Evaluate=true, Dialog(connectorSizing=true));
  parameter Integer nPorts_bCoo=0
    "Number of outlet fluid ports on source side"
    annotation (Evaluate=true, Dialog(connectorSizing=true));
  parameter Boolean have_heaLoa=true
    "Set to true if the building has heating loads"
    annotation (Evaluate=true);
  parameter Boolean have_cooLoa=true
    "Set to true if the building has cooling loads"
    annotation (Evaluate=true);
  parameter Boolean have_fan=true
    "Set to true if the power drawn by fan motors is computed"
    annotation (Evaluate=true);
  parameter Boolean have_pum=true
    "Set to true if the power drawn by pump motors is computed"
    annotation (Evaluate=true);
  parameter Boolean have_eleHea=true
    "Set to true if the building has decentralized electric heating equipment"
    annotation (Evaluate=true);
  parameter Boolean have_eleCoo=true
    "Set to true if the building has decentralized electric cooling equipment"
    annotation (Evaluate=true);
  parameter Boolean have_weaBus=true
    "Set to true for weather bus"
    annotation (Evaluate=true);
  parameter Boolean allowFlowReversal=false
    "= true to allow flow reversal, false restricts to design direction (port_a -> port_b)"
    annotation (Evaluate=true);
  // IO CONNECTORS
  Buildings.BoundaryConditions.WeatherData.Bus weaBus if have_weaBus
    "Weather data bus"
    annotation (Placement(transformation(extent={{-16, 284}, {18, 316}}), iconTransformation(extent={{-16, 198}, {18, 230}})));
  Modelica.Fluid.Interfaces.FluidPorts_a secHeaSup[nPorts_aHea](redeclare each package Medium=Medium, each m_flow(min=if allowFlowReversal then-Modelica.Constants.inf else 0), each h_outflow(start=Medium.h_default, nominal=Medium.h_default)) if have_heaLoa
    "Source side inlet ports"
    annotation (Placement(transformation(extent={{-310,-8}, {-290, 72}}), iconTransformation(extent={{-310,-220}, {-290,-140}})));
  Modelica.Fluid.Interfaces.FluidPorts_b secHeaRet[nPorts_bHea](redeclare each package Medium=Medium, each m_flow(max=if allowFlowReversal then + Modelica.Constants.inf else 0), each h_outflow(start=Medium.h_default, nominal=Medium.h_default)) if have_heaLoa
    "Source side outlet ports"
    annotation (Placement(transformation(extent={{290,-8}, {310, 72}}), iconTransformation(extent={{290,-220}, {310,-140}})));
  //if have_heaLoa
  Modelica.Fluid.Interfaces.FluidPorts_a secCooSup[nPorts_aCoo](redeclare each package Medium=Medium, each m_flow(min=if allowFlowReversal then-Modelica.Constants.inf else 0), each h_outflow(start=Medium.h_default, nominal=Medium.h_default)) if have_cooLoa
    "Source side inlet ports"
    annotation (Placement(transformation(extent={{-310,-70}, {-290, 10}}), iconTransformation(extent={{-310,-128}, {-290,-48}})));
  Modelica.Fluid.Interfaces.FluidPorts_b secCooRet[nPorts_bCoo](redeclare each package Medium=Medium, each m_flow(max=if allowFlowReversal then + Modelica.Constants.inf else 0), each h_outflow(start=Medium.h_default, nominal=Medium.h_default)) if have_cooLoa
    "Source side outlet ports"
    annotation (Placement(transformation(extent={{290,-70}, {310, 10}}), iconTransformation(extent={{290,-130}, {310,-50}})));
  Modelica.Blocks.Interfaces.RealOutput QHea_flow(final quantity="HeatFlowRate", final unit="W") if have_heaLoa
    "Total heating heat flow rate transferred to the loads (>=0)"
    annotation (Placement(transformation(extent={{300, 260}, {340, 300}}), iconTransformation(extent={{300, 240}, {340, 280}})));
  Modelica.Blocks.Interfaces.RealOutput QCoo_flow(final quantity="HeatFlowRate", final unit="W") if have_cooLoa
    "Total cooling heat flow rate transferred to the loads (<=0)"
    annotation (Placement(transformation(extent={{300, 220}, {340, 260}}), iconTransformation(extent={{300, 200}, {340, 240}})));
  Modelica.Blocks.Interfaces.RealOutput PHea(final quantity="Power", final unit="W") if have_eleHea
    "Power drawn by decentralized heating equipment"
    annotation (Placement(transformation(extent={{300, 180}, {340, 220}}), iconTransformation(extent={{300, 160}, {340, 200}})));
  Modelica.Blocks.Interfaces.RealOutput PCoo(quantity="Power", final unit="W") if have_eleCoo
    "Power drawn by decentralized cooling equipment"
    annotation (Placement(transformation(extent={{300, 140}, {340, 180}}), iconTransformation(extent={{300, 120}, {340, 160}})));
  Modelica.Blocks.Interfaces.RealOutput PFan(final quantity="Power", final unit="W") if have_fan
    "Power drawn by fan motors"
    annotation (Placement(transformation(extent={{300, 100}, {340, 140}}), iconTransformation(extent={{300, 80}, {340, 120}})));
  Modelica.Blocks.Interfaces.RealOutput PPum(final quantity="Power", final unit="W") if have_pum
    "Power drawn by pump motors"
    annotation (Placement(transformation(extent={{300, 60}, {340, 100}}), iconTransformation(extent={{300, 40}, {340, 80}})));
initial equation
  assert(nPorts_aHea == nPorts_bHea, "In " + getInstanceName() + ": The numbers of secondary heating source side inlet ports (" + String(nPorts_aHea) + ") and outlet ports (" + String(nPorts_bHea) + ") must be equal.");
  assert(nPorts_aCoo == nPorts_bCoo, "In " + getInstanceName() + ": The numbers of secondary cooling source side inlet ports (" + String(nPorts_aCoo) + ") and outlet ports (" + String(nPorts_bCoo) + ") must be equal.");
  annotation (defaultComponentName="bui", Documentation(info="<html>
<p>
Partial model to be used for modeling the thermal loads on an energy
transfer station or a dedicated plant.
Models extending this class are typically used in conjunction with
<a href=\"modelica://Buildings.Applications.DHC.Loads.FlowDistribution\">
Buildings.Applications.DHC.Loads.FlowDistribution</a>
and models extending
<a href=\"modelica://Buildings.Applications.DHC.Loads.BaseClasses.PartialTerminalUnit\">
Buildings.Applications.DHC.Loads.BaseClasses.PartialTerminalUnit</a>
as described in the schematics here under.
The fluid ports represent the connection between the production system and
the building distribution system.
</p>
<p>
See various use cases in
<a href=\"modelica://Buildings.Applications.DHC.Loads.Examples\">
Buildings.Applications.DHC.Loads.Examples</a>.
<br>
</p>
<p>
<img alt=\"image\"
src=\"modelica://Buildings/Resources/Images/Applications/DHC/Loads/PartialBuilding.png\"/>
</p>
</html>", revisions="<html>
<ul>
<li>
April 29, 2020, by Amy Allen:<br/>
Seperated the secondary cooling and heating inlets/outlets to two fluid ports.
</li>
<li>
February 21, 2020, by Antoine Gautier:<br/>
First implementation.
</li>
</ul>
</html>"), Icon(coordinateSystem(extent={{-300,-300}, {300, 300}}, preserveAspectRatio=false), graphics={Rectangle(extent={{-300,-300}, {300, 300}}, lineColor={0, 0, 127}, fillColor={255, 255, 255}, fillPattern=FillPattern.Solid), Rectangle(extent={{10,-186}, {290,-202}}, lineColor={0, 0, 255}, pattern=LinePattern.None, fillColor={0, 0, 255}, fillPattern=FillPattern.Solid), Rectangle(extent={{-290,-204}, {-10,-188}}, lineColor={0, 0, 255}, pattern=LinePattern.None, fillColor={255, 0, 0}, fillPattern=FillPattern.Solid), Rectangle(extent={{10,-100}, {290,-84}}, lineColor={0, 0, 255}, pattern=LinePattern.None, fillColor={255, 0, 0}, fillPattern=FillPattern.Solid), Rectangle(extent={{-290,-80}, {-10,-96}}, lineColor={0, 0, 255}, pattern=LinePattern.None, fillColor={0, 0, 255}, fillPattern=FillPattern.Solid), Rectangle(extent={{18,-38}, {46,-10}}, lineColor={255, 255, 255}, fillColor={255, 255, 255}, fillPattern=FillPattern.Solid), Text(extent={{-150,-328}, {150,-368}}, lineColor={0, 0, 255}, textString="%name"), Rectangle(extent={{10,-146}, {290,-162}}, lineColor={0, 0, 255}, pattern=LinePattern.None, fillColor={0, 0, 255}, fillPattern=FillPattern.Solid), Rectangle(extent={{-290,-162}, {-10,-146}}, lineColor={0, 0, 255}, pattern=LinePattern.None, fillColor={255, 0, 0}, fillPattern=FillPattern.Solid), Rectangle(extent={{-180, 180}, {174,-220}}, lineColor={150, 150, 150}, fillPattern=FillPattern.Sphere, fillColor={255, 255, 255}), Rectangle(extent={{36, 42}, {108, 114}}, lineColor={255, 255, 255}, fillColor={255, 255, 255}, fillPattern=FillPattern.Solid), Rectangle(extent={{-124, 42}, {-52, 114}}, lineColor={255, 255, 255}, fillColor={255, 255, 255}, fillPattern=FillPattern.Solid), Rectangle(extent={{-126,-122}, {-54,-50}}, lineColor={255, 255, 255}, fillColor={255, 255, 255}, fillPattern=FillPattern.Solid), Rectangle(extent={{40,-122}, {112,-50}}, lineColor={255, 255, 255}, fillColor={255, 255, 255}, fillPattern=FillPattern.Solid), Polygon(points={{0, 264}, {-218, 164}, {220, 164}, {0, 264}}, lineColor={95, 95, 95}, smooth=Smooth.None, fillPattern=FillPattern.Solid, fillColor={95, 95, 95})}), Diagram(coordinateSystem(preserveAspectRatio=false, extent={{-300,-300}, {300, 300}})));
end PartialBuilding;
