# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

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

        print("Note that the [unused] fields will have been overwritten by this operation. It is recommended to "
              "open the previous version and new version in a diff tool to copy over the [unused] tags.")
