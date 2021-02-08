"""
****************************************************************************************************
:copyright (c) 2019-2021 URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.

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

import json

import click
import requests

files_to_download = [
    "building_properties.json",
    "district_system_properties.json",
    "electrical_connector_properties.json",
    "electrical_junction_properties.json",
    "region_properties.json",
    "site_properties.json",
    "thermal_connector_properties.json",
    "thermal_junction_properties.json",
]

baseurl = "https://raw.githubusercontent.com/urbanopt/urbanopt-geojson-gem/develop/lib/urbanopt/geojson/schema/"  # noqa


@click.command()
@click.argument('schema', required=False)
def update_schemas(schema):
    for f in files_to_download:
        click.echo(f"Downloading schema: {f}")
        response = requests.get(f"{baseurl}/{f}")
        save_path = f"geojson_modelica_translator/geojson/data/schemas/{f}"
        with open(save_path, "w") as outf:
            json.dump(response.json(), outf, indent=2)
