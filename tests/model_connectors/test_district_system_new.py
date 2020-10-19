"""
****************************************************************************************************
:copyright (c) 2019-2020 URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted
provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions
and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this list of conditions
and the following disclaimer in the documentation and/or other materials provided with the
distribution.

Neither the name of the copyright holder nor the names of its contributors may be used to endorse
or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
****************************************************************************************************
"""

import os

from geojson_modelica_translator.geojson_modelica_translator import GeoJsonModelicaTranslator
from geojson_modelica_translator.model_connectors.district import District
from geojson_modelica_translator.model_connectors.energy_transfer_connectors.cooling_indirect import (
    CoolingIndirectConnector
)
from geojson_modelica_translator.model_connectors.load_connectors.time_series_new import (
    TimeSeriesConnector
)
from geojson_modelica_translator.system_parameters.system_parameters import (
    SystemParameters
)

from ..base_test_case import TestCaseBase


class DistrictSystemTest(TestCaseBase):
    def test_district_system(self):
        project_name = "district_system_new"
        self.data_dir, self.output_dir = self.set_up(os.path.dirname(__file__), project_name)

        # load in the example geojson with a single office building
        filename = os.path.join(self.data_dir, "time_series_ex1.json")
        self.gj = GeoJsonModelicaTranslator.from_geojson(filename)
        # use the GeoJson translator to scaffold out the directory
        # self.gj.scaffold_directory(self.output_dir, project_name)

        # load system parameter data
        filename = os.path.join(self.data_dir, "time_series_system_params_ets.json")
        sys_params = SystemParameters(filename)

        # Create the time series load
        time_series_load = TimeSeriesConnector(sys_params)
        for b in self.gj.json_loads:
            # will only add a single building
            time_series_load.add_building(b)

        # create the energy transfer system
        cooling_indirect_system = CoolingIndirectConnector(sys_params)

        ts_load_id = 'timSerLoa'
        cooling_id = 'cooIndSys'
        district = District(
            root_dir=self.output_dir,
            project_name=project_name,
            system_parameters=sys_params,
            components=[
                time_series_load.as_component(ts_load_id),
                cooling_indirect_system.as_component(cooling_id)
            ],
            connections=[
                (ts_load_id + ".ports_bChiWat", cooling_id + ".port_b1"),
            ])

        district.to_modelica()
