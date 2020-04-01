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

import distutils.cmd
import distutils.log
import json

import requests


class UpdateSchemas(distutils.cmd.Command):
    """Custom comand for updating the GeoJSON schemas on which this project depends."""

    description = "download updated GeoJSON schemas"

    user_options = [("baseurl=", "u", "base URL from which to download the schemas")]

    def initialize_options(self):
        self.files_to_download = [
            "building_properties.json",
            "district_system_properties.json",
            "electrical_connector_properties.json",
            "electrical_junction_properties.json",
            "region_properties.json",
            "site_properties.json",
            "thermal_connector_properties.json",
            "thermal_junction_properties.json",
        ]
        # For now the branch is 'schema' but will need to be moved to develop after it is merged.
        self.baseurl = "https://raw.githubusercontent.com/urbanopt/urbanopt-geojson-gem/schema/lib/urbanopt/geojson/schema/"  # noqa

    def finalize_options(self):
        if self.baseurl is None:
            print("Downloading the schemas from the default url: %s" % self.baseurl)

    def run(self):
        for f in self.files_to_download:
            self.announce("Downloading schema: %s" % str(f), level=distutils.log.INFO)
            response = requests.get("%s/%s" % (self.baseurl, f))
            save_path = "geojson_modelica_translator/geojson/data/schemas/%s" % f
            # if os.path.exists(save_path):
            #     os.remove(save_path)
            with open(save_path, "w") as outf:
                json.dump(response.json(), outf, indent=2)
