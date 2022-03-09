"""
****************************************************************************************************
:copyright (c) 2019-2022, Alliance for Sustainable Energy, LLC, and other contributors.

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

Redistribution of this software, without modification, must refer to the software by the same
designation. Redistribution of a modified version of this software (i) may not refer to the
modified version by the same designation, or by any confusingly similar designation, and
(ii) must refer to the underlying software originally provided by Alliance as “URBANopt”. Except
to comply with the foregoing, the term “URBANopt”, or any confusingly similar designation may
not be used to refer to any modified version of this software or any modified version of the
underlying software originally provided by Alliance without the prior written consent of Alliance.

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

from pathlib import Path

import pytest
from geojson_modelica_translator.geojson_modelica_translator import (
    GeoJsonModelicaTranslator
)

from ..base_test_case import TestCaseBase

ROOT_DIR = Path(__file__).parent


class GeoJSONTranslatorTest(TestCaseBase):
    geojson_file = TestCaseBase.SHARED_DATA_DIR / 'geojson_district' / 'geojson.json'
    sys_params_file = TestCaseBase.SHARED_DATA_DIR / 'geojson_district' / 'system_params.json'

    def test_to_modelica_is_successful_when_inputs_are_valid(self):
        # -- Setup, Act
        project_name = 'generate_package'
        _, output_dir = self.set_up(ROOT_DIR, project_name)
        gmt = GeoJsonModelicaTranslator(
            self.geojson_file,
            self.sys_params_file,
            output_dir,
            project_name,
        )

        gmt.to_modelica()

        # -- Assert
        self.assertTrue((output_dir / project_name / 'package.mo').exists())

    @pytest.mark.simulation
    def test_successfully_creates_and_simulates_when_inputs_are_valid(self):
        # -- Setup
        project_name = 'simulate_package'
        _, output_dir = self.set_up(ROOT_DIR, project_name)

        gmt = GeoJsonModelicaTranslator(
            self.geojson_file,
            self.sys_params_file,
            output_dir,
            project_name,
        )

        package = gmt.to_modelica()

        # -- Act
        success, results_dir = package.simulate()

        # -- Assert
        self.assertTrue(success, 'simulation did not complete successfully')
        self.assertTrue((results_dir / 'stdout.log').exists())
