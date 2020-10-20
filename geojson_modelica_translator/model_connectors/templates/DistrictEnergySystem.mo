within somePackage;
model DistrictEnergySystem
  extends Modelica.Icons.Example;
equation
  annotation (
    experiment(
      StopTime=86400,
      Interval=3600,
      Tolerance=1e-06));
end DistrictEnergySystem;
