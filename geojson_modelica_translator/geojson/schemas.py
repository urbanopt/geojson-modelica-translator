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

import json
import os

from jsonschema.validators import _LATEST_VERSION as LatestValidator


class Schemas(object):
    """
    Class to hold the various schemas
    """

    def __init__(self):
        """Load in the schemas"""
        self.schemas = {
            "building": None,
            "district_system": None,
            "electrical_connector": None,
            "electrical_junction": None,
            "region": None,
            "site": None,
            "thermal_connector": None,
            "thermal_junction": None,
        }

        for s in self.schemas.keys():
            path = os.path.join(
                os.path.dirname(__file__), "data/schemas/%s_properties.json" % s
            )
            with open(path, "r") as f:
                self.schemas[s] = json.load(f)

    def retrieve(self, name):
        """name of the schema to retrieve"""
        if self.schemas.get(name):
            return self.schemas[name]
        else:
            raise Exception("Schema for %s does not exist" % name)

    def validate(self, name, instance):
        """
        Validate an instance against a loaded schema

        :param name: str, name of the schema to validate against
        :param instance: dict, instance to validate
        :return:
        """
        results = []
        s = self.retrieve(name)
        v = LatestValidator(s)
        for error in sorted(v.iter_errors(instance), key=str):
            results.append(error.message)

        return results
