# compile and simulate the model here, called separately by the measure
# make sure this approach works with the measure ! it shouldn't need to pass any files=>should just be persisted in the directory
#  need to adjust path so that it can find modules

from pyfmi import load_fmu
from pymodelica import compile_fmu

name = 'Districts.DistrictEnergySystem'

compile_options = {'runtime_log_to_file': True, 'generate_html_diagnostics': True, 'log_level': 6}

fmu = compile_fmu(name, compiler_options=compile_options, compiler_log_level='d', jvm_args='-Xmx10g', target='cs')
fmu_sim = load_fmu(fmu)
fmu_sim.simulate(start_time=0, final_time=5)  # could assign to res later
