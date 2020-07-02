//within geojson_modelica_translator.model_connectors.templates;
record DesignDataParallel4GDC
  "Record with design data for parallel network"
  extends Modelica.Icons.Record;
  parameter Integer nBui=3
    "Number of served buildings"
    annotation (Evaluate=true);
  parameter Modelica.SIunits.MassFlowRate mDis_flow_nominal
    "Nominal mass flow rate of the distribution pump";
  parameter Modelica.SIunits.MassFlowRate mCon_flow_nominal[nBui]
    "Nominal mass flow rate in each connection line";
  parameter Modelica.SIunits.Length lDis[nBui]=fill(
    100,
    nBui)
    "Length of distribution pipe (only counting warm or cold line, but not sum)";
  parameter Modelica.SIunits.Length lCon[nBui]=fill(
    10,
    nBui)
    "Length of connection pipe (only counting warm or cold line, but not sum)";
  parameter Modelica.SIunits.Length lEnd=10
    "Length of the end of the distribution line (supply only, not counting return line)";
  parameter Modelica.SIunits.Length dhDis[nBui]={0.15, 0.1, 0.05}
    "Hydraulic diameter of the distribution pipe before each connection";
  parameter Modelica.SIunits.Length dhCon[nBui]=fill(
    0.05,
    nBui)
    "Hydraulic diameter of each connection pipe";
  parameter Modelica.SIunits.Length dhEnd=dhDis[nBui]
    "Hydraulic diameter of the end of the distribution line";
  annotation (defaultComponentPrefix="datDes", defaultComponentPrefixes="inner");
end DesignDataParallel4GDC;
