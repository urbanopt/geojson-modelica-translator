# test_output_processing.py

import matplotlib.pyplot as plt
from buildingspy.io.outputfile import Reader

mat = Reader("tests/model_connectors/output/manual_case_2_results/manual_case_2_Districts_DistrictEnergySystem_result.mat", "dymola")

# List off all the variables
for var in mat.varNames():
    print(var)
(time1, zn_1_temp) = mat.values("TimeSerLoa_820cbdd6.terUniCoo.fan.vol.T")
# (time1, zn_1_temp) = mat.values("TimeSerLoa_f893f58f.terUniCoo.fan.vol.T")
# (_time1, zn_4_temp) = mat.values("bui.znPerimeter_ZN_4.TAir")
plt.style.use('seaborn-whitegrid')
fig = plt.figure(figsize=(16, 8))
ax = fig.add_subplot(211)
ax.plot(time1 / 3600, zn_1_temp - 273.15, 'r', label='$T_1$')
# ax.plot(time1 / 3600, zn_4_temp - 273.15, 'b', label='$T_4$')
ax.set_xlabel('time [h]')
ax.set_ylabel(r'temperature [$^\circ$C]')
# Simulation is only for 168 hours?
ax.set_xlim([0, 168])
ax.legend()
ax.grid(True)
fig.savefig('indoor_temp_example.png')
