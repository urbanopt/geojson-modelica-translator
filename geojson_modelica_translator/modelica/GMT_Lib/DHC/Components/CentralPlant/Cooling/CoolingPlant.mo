within GMT_Lib.DHC.Components.CentralPlant.Cooling;
model CoolingPlant
  "This example is to validate template Central Cooling Plant component model."
    extends Buildings.Experimental.DHC.CentralPlants.Cooling.Examples.Plant(
    redeclare Buildings.Fluid.Chillers.Data.ElectricEIR.ElectricEIRChiller_York_YT_1055kW_5_96COP_Vanes perChi(
      mEva_flow_nominal=mCHW_flow_nominal,
      mCon_flow_nominal=mCW_flow_nominal,
      QEva_flow_nominal=QChi_nominal),
    redeclare Buildings.Experimental.DHC.CentralPlants.Cooling.Plant pla,
    dTApp=3,
    mCHW_flow_nominal=18.3,
    dpCHW_nominal=44.8*1000,
    mMin_flow=0.03,
    mCW_flow_nominal=34.7,
    dpCW_nominal=46.2*1000,
    PFan_nominal=4999,
    TCHWSet=273.15 + 7,
    dpCooTowVal_nominal=5999,
    dpCHWPumVal_nominal=5999,
    dpCWPumVal_nominal=5999);
  annotation (
    Icon(coordinateSystem(preserveAspectRatio=false)),
    Diagram(coordinateSystem(preserveAspectRatio=false)),
    experiment(StopTime=86400, Tolerance=1e-06),
    Documentation(info="<html>
      <p>This model validates the district central cooling plant template model
GMT_Lib.DHC.Components.CentralPlants.Cooling.Cooling.mot</a>.
</p>
</html>", revisions="<html>
<ul>
<li>
October 20, 2021 by Chengnan Shi:<br/>
First implementation.
</li>
</ul>
</html>"),
    __Dymola_Commands(file="CoolingPlant.mos"
                                             "Simulate and Plot"));
end CoolingPlant;
