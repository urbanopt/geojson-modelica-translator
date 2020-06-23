//within Buildings.Applications.DHC.Examples.Combined.Generation5.Unidirectional.Networks;
model ConnectionParallel "Model for connecting an agent to the DHC system"
  extends PartialConnection2Pipe(
    redeclare model Model_pipDis = PipeDistribution (
      final dh=dhDis, final length=lDis, final fac= fac),
    redeclare model Model_pipCon = PipeConnection (
      final fac= fac,
      final length=2*lCon,
      final dh=dhCon));

  parameter Real fac
    "Factor to take into account resistance of bends etc., fac=dp_nominal/dpStraightPipe_nominal";
  parameter Modelica.SIunits.Length lDis
    "Length of the distribution pipe before the connection";
  parameter Modelica.SIunits.Length lCon
    "Length of the connection pipe (supply only, not counting return line)";
  parameter Modelica.SIunits.Length dhDis
    "Hydraulic diameter of the distribution pipe";
  parameter Modelica.SIunits.Length dhCon
    "Hydraulic diameter of the connection pipe";
end ConnectionParallel;
