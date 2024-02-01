# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

from pathlib import Path

import pytest
from buildingspy.io.outputfile import Reader

from geojson_modelica_translator.geojson.urbanopt_geojson import UrbanOptGeoJson
from geojson_modelica_translator.model_connectors.couplings import Coupling, CouplingGraph
from geojson_modelica_translator.model_connectors.districts import District
from geojson_modelica_translator.model_connectors.energy_transfer_systems import CoolingIndirect, HeatingIndirect
from geojson_modelica_translator.model_connectors.load_connectors import Teaser
from geojson_modelica_translator.model_connectors.networks import Network2Pipe
from geojson_modelica_translator.model_connectors.plants import CoolingPlant
from geojson_modelica_translator.model_connectors.plants.chp import HeatingPlantWithOptionalCHP
from geojson_modelica_translator.system_parameters.system_parameters import SystemParameters
from tests.base_test_case import TestCaseBase


class TestTeaserDistrictHeatingAndCoolingSystems(TestCaseBase):
    def setUp(self):
        super().setUp()

        self.project_name = "teaser_district_heating_and_cooling_systems"
        self.data_dir, self.output_dir = self.set_up(Path(__file__).parent, self.project_name)

        filename = Path(self.data_dir) / "teaser_geojson_two_loads.json"
        self.gj = UrbanOptGeoJson(filename)

        # load system parameter data
        filename = Path(self.data_dir) / "teaser_system_params_two_loads.json"
        self.sys_params = SystemParameters(filename)

        # create cooling network and plant
        cooling_network = Network2Pipe(self.sys_params)
        cooling_plant = CoolingPlant(self.sys_params)

        # create heating network and plant
        heating_network = Network2Pipe(self.sys_params)
        heating_plant = HeatingPlantWithOptionalCHP(self.sys_params)

        # create our load/ets/stubs
        # store all couplings to construct the District system
        all_couplings = [
            Coupling(cooling_network, cooling_plant),
            Coupling(heating_network, heating_plant),
        ]

        # keep track of separate loads and etses for testing purposes
        self.loads = []
        heat_etses = []
        cool_etses = []
        for geojson_load in self.gj.buildings:
            teaser_load = Teaser(self.sys_params, geojson_load)
            self.loads.append(teaser_load)
            geojson_load_id = geojson_load.feature.properties["id"]

            cooling_indirect = CoolingIndirect(self.sys_params, geojson_load_id)
            cool_etses.append(cooling_indirect)
            all_couplings.append(Coupling(teaser_load, cooling_indirect))
            all_couplings.append(Coupling(cooling_indirect, cooling_network))

            heating_indirect = HeatingIndirect(self.sys_params, geojson_load_id)
            heat_etses.append(heating_indirect)
            all_couplings.append(Coupling(teaser_load, heating_indirect))
            all_couplings.append(Coupling(heating_indirect, heating_network))

        # create the couplings and graph
        graph = CouplingGraph(all_couplings)

        self.district = District(
            root_dir=self.output_dir,
            project_name=self.project_name,
            system_parameters=self.sys_params,
            coupling_graph=graph,
        )
        self.district.to_modelica()

    def test_build_teaser_district_heating_and_cooling_systems(self):
        root_path = Path(self.district._scaffold.districts_path.files_dir).resolve()
        assert (root_path / "DistrictEnergySystem.mo").exists()

    @pytest.mark.simulation()
    @pytest.mark.skip(reason="Takes forever to run. Teaser is a problem for another day.")
    def test_teaser_district_heating_and_cooling_systems(self):
        self.run_and_assert_in_docker(
            f"{self.district._scaffold.project_name}.Districts.DistrictEnergySystem",
            file_to_load=self.district._scaffold.package_path,
            run_path=self.district._scaffold.project_path,
            start_time=17280000,  # Day 200 (in seconds) (Run in summer to keep chiller happy)
            stop_time=17366400,  # For 1 day duration (in seconds)
            step_size=3600,  # At 1 hour intervals (in seconds)
        )

        #
        # Validate model outputs
        #
        results_dir = (
            f"{self.district._scaffold.project_path}/{self.project_name}.Districts.DistrictEnergySystem_results"
        )

        mat_file = f"{results_dir}/{self.project_name}.Districts.DistrictEnergySystem_res.mat"
        mat_results = Reader(mat_file, "dymola")

        # check the mass flow rates of the first load are in the expected range
        load = self.loads[0]
        (_, heat_m_flow) = mat_results.values(f"{load.id}.ports_aHeaWat[1].m_flow")
        (_, cool_m_flow) = mat_results.values(f"{load.id}.ports_aChiWat[1].m_flow")
        assert (heat_m_flow >= 0).all(), "Heating mass flow rate must be greater than or equal to zero"
        assert (cool_m_flow >= 0).all(), "Cooling mass flow rate must be greater than or equal to zero"

        # this tolerance determines how much we allow the actual mass flow rate to exceed the nominal value
        m_flow_nominal_tolerance = 0.01
        (_, heat_m_flow_nominal) = mat_results.values(f"{load.id}.terUni[1].mLoaHea_flow_nominal")
        heat_m_flow_nominal = heat_m_flow_nominal[0]
        (_, cool_m_flow_nominal) = mat_results.values(f"{load.id}.terUni[1].mLoaCoo_flow_nominal")
        cool_m_flow_nominal = cool_m_flow_nominal[0]

        assert (
            heat_m_flow <= pytest.approx(heat_m_flow_nominal, rel=m_flow_nominal_tolerance).all()
        ), f"Heating mass flow rate must be less than nominal mass flow rate ({heat_m_flow_nominal}) plus a tolerance ({m_flow_nominal_tolerance * 100}%)"  # noqa: E501
        assert (
            cool_m_flow <= pytest.approx(cool_m_flow_nominal, rel=m_flow_nominal_tolerance).all()
        ), f"Cooling mass flow rate must be less than nominal mass flow rate ({cool_m_flow_nominal}) plus a tolerance ({m_flow_nominal_tolerance * 100}%)"  # noqa: E501
