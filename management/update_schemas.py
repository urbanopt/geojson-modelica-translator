import distutils.cmd
import distutils.log
import json

import requests


class UpdateSchemas(distutils.cmd.Command):
    """Custom comand for updating the GeoJSON schemas on which this project depends."""

    description = 'download updated GeoJSON schemas'

    user_options = [
        ('baseurl=', 'u', 'base URL from which to download the schemas'),
    ]

    def initialize_options(self):
        self.files_to_download = [
            'building_properties.json',
            'district_system_properties.json',
            'electrical_connector_properties.json',
            'electrical_junction_properties.json',
            'region_properties.json',
            'site_properties.json',
            'thermal_connector_properties.json',
            'thermal_junction_properties.json',

        ]
        # For now the branch is 'schema' but will need to be moved to develop after it is merged.
        self.baseurl = 'https://raw.githubusercontent.com/urbanopt/urbanopt-geojson-gem/schema/lib/urbanopt/geojson/schema/'

    def finalize_options(self):
        if self.baseurl is None:
            print("Downloading the schemas from the default url: %s" % self.baseurl)

    def run(self):
        for f in self.files_to_download:
            self.announce('Downloading schema: %s' % str(f), level=distutils.log.INFO)
            response = requests.get('%s/%s' % (self.baseurl, f))
            save_path = 'geojson_modelica_translator/geojson/data/schemas/%s' % f
            # if os.path.exists(save_path):
            #     os.remove(save_path)
            with open(save_path, 'w') as outf:
                json.dump(response.json(), outf, indent=2)
