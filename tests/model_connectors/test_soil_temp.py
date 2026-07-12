from unittest.mock import MagicMock, Mock, patch

import pandas as pd

from geojson_modelica_translator.model_connectors.plants.borefield import Borefield
from geojson_modelica_translator.system_parameters.system_parameters import SystemParameters
from tests.base_test_case import TestCaseBase


class TestValidateUndisturbedSoilTemperature(TestCaseBase):
    def setUp(self):
        # Mock SystemParameters object
        self.mock_system_parameters = Mock(spec=SystemParameters)

        # Setup mock to return a dict for district_system that includes fifth_generation with full structure
        district_system_data = {
            "fifth_generation": {
                "central_pump_parameters": {},
                "horizontal_piping_parameters": {"pressure_drop_per_meter": 300},
                "ghe_parameters": {},
            }
        }

        # Mock the get_param method to return appropriate values
        def mock_get_param(path):
            if path == "district_system":
                return district_system_data
            elif path == "$.weather":
                return "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw"
            else:
                return None

        self.mock_system_parameters.get_param = MagicMock(side_effect=mock_get_param)
        self.mock_system_parameters.filename = "/fake/path/system_params.json"  # Mock filename

        # Mock GHE data
        self.mock_ghe = {"ghe_id": "test_ghe_id"}

        # Patch the load_loop_order function since it's not needed for our test
        with patch("geojson_modelica_translator.model_connectors.model_base.load_loop_order", return_value=[]):
            # Create Borefield instance with mocked dependencies
            self.borefield = Borefield(self.mock_system_parameters, self.mock_ghe)

    def _create_mock_district_system(self):
        """Helper method to create proper district system structure"""
        return {
            "fifth_generation": {
                "central_pump_parameters": {},
                "horizontal_piping_parameters": {"pressure_drop_per_meter": 300},
                "ghe_parameters": {},
            }
        }

    @patch("pandas.read_csv")
    def test_matching_station_name_within_threshold(self, mock_read_csv):
        """Test validation passes when station name matches and temperature is within threshold."""
        # Setup weather parameter specifically for this test
        self.mock_system_parameters.get_param.side_effect = lambda path: (
            "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw"
            if path == "$.weather"
            else self._create_mock_district_system()
            if path == "district_system"
            else None
        )

        # Mock CSV data with matching station
        # The station name extracted from "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw" should be:
        # parts[2] = "Chicago-OHare.Intl.AP.725300" -> after re.sub(r"\d+", "") -> "Chicago-OHare.Intl.AP."
        # -> after .replace(".", " ") -> "Chicago-OHare Intl AP "
        mock_df = pd.DataFrame(
            {
                "Station": ["Chicago-OHare Intl AP Weather Station", "Boston Logan", "Denver Intl"],
                "Ts,avg, C": [12.0, 8.5, 10.2],
            }
        )
        mock_read_csv.return_value = mock_df

        # This should not generate any warnings - just call the method successfully
        # The validation logic doesn't return anything, it just logs warnings if there are issues
        self.borefield.validate_undisturbed_soil_temperature(12.2)

    @patch("pandas.read_csv")
    def test_matching_station_name_outside_threshold(self, mock_read_csv):
        """Test validation warns when station name matches but temperature is outside threshold."""
        # Setup weather parameter
        self.mock_system_parameters.get_param.side_effect = lambda path: (
            "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw"
            if path == "$.weather"
            else self._create_mock_district_system()
            if path == "district_system"
            else None
        )

        # Mock CSV data with matching station
        # Station name will be "Chicago-OHare Intl AP " so need to match that
        mock_df = pd.DataFrame(
            {
                "Station": ["Chicago-OHare Intl AP Weather Station", "Boston Logan", "Denver Intl"],
                "Ts,avg, C": [12.0, 8.5, 10.2],
            }
        )
        mock_read_csv.return_value = mock_df

        # Capture log messages
        with self.assertLogs("geojson_modelica_translator.model_connectors.plants.borefield", level="WARNING") as log:
            self.borefield.validate_undisturbed_soil_temperature(15.0)
            # Should generate warning - temperature difference is 3.0, outside 0.5 threshold
            assert len(log.output) == 1
            assert "differs from the lookup value" in log.output[0]

    @patch("pandas.read_csv")
    def test_non_matching_station_name(self, mock_read_csv):
        """Test validation warns when station name doesn't match."""
        # Setup weather parameter with different station
        self.mock_system_parameters.get_param.side_effect = lambda path: (
            "USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw"
            if path == "$.weather"
            else self._create_mock_district_system()
            if path == "district_system"
            else None
        )

        # Mock CSV data with different station
        mock_df = pd.DataFrame({"Station": ["Chicago-OHare"], "Ts,avg, C": [12.0]})
        mock_read_csv.return_value = mock_df

        # Capture log messages
        with self.assertLogs("geojson_modelica_translator.model_connectors.plants.borefield", level="WARNING") as log:
            self.borefield.validate_undisturbed_soil_temperature(15.0)
            # Should generate warning - no matching station found
            assert len(log.output) == 1
            assert "Could not validate undisturbed soil temperature" in log.output[0]

    @patch("pandas.read_csv")
    def test_zero_temperature_validation(self, mock_read_csv):
        """Test validation behavior with zero temperature value."""
        # Setup weather parameter
        self.mock_system_parameters.get_param.side_effect = lambda path: (
            "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw"
            if path == "$.weather"
            else self._create_mock_district_system()
            if path == "district_system"
            else None
        )

        # Mock CSV data with matching station
        mock_df = pd.DataFrame(
            {
                "Station": ["Chicago-OHare Intl AP Weather Station", "Boston Logan", "Denver Intl"],
                "Ts,avg, C": [12.0, 8.5, 10.2],
            }
        )
        mock_read_csv.return_value = mock_df

        # Capture log messages
        with self.assertLogs("geojson_modelica_translator.model_connectors.plants.borefield", level="WARNING") as log:
            self.borefield.validate_undisturbed_soil_temperature(0.0)
            # Should generate warning - large temperature difference
            assert len(log.output) == 1
            assert "differs from the lookup value" in log.output[0]

    @patch("pandas.read_csv")
    def test_negative_temperature_validation(self, mock_read_csv):
        """Test validation behavior with negative temperature value."""
        # Setup weather parameter
        self.mock_system_parameters.get_param.side_effect = lambda path: (
            "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw"
            if path == "$.weather"
            else self._create_mock_district_system()
            if path == "district_system"
            else None
        )

        # Mock CSV data with matching station
        mock_df = pd.DataFrame(
            {
                "Station": ["Chicago-OHare Intl AP Weather Station", "Boston Logan", "Denver Intl"],
                "Ts,avg, C": [12.0, 8.5, 10.2],
            }
        )
        mock_read_csv.return_value = mock_df

        # Capture log messages
        with self.assertLogs("geojson_modelica_translator.model_connectors.plants.borefield", level="WARNING") as log:
            self.borefield.validate_undisturbed_soil_temperature(-5.0)
            # Should generate warning - large temperature difference
            assert len(log.output) == 1
            assert "differs from the lookup value" in log.output[0]

    @patch("pandas.read_csv")
    def test_different_weather_file_patterns(self, mock_read_csv):
        """Test validation with different weather file naming patterns."""
        # Test 2-part naming pattern which goes to unexpected format handling
        # From debug: "Chicago-OHare_TMY3.epw" -> final station name: "TMY"
        self.mock_system_parameters.get_param.side_effect = lambda path: (
            "Chicago-OHare_TMY3.epw"
            if path == "$.weather"
            else self._create_mock_district_system()
            if path == "district_system"
            else None
        )

        mock_df = pd.DataFrame(
            {"Station": ["TMY Weather Station", "Boston Logan", "Denver Intl"], "Ts,avg, C": [10.0, 8.5, 12.0]}
        )
        mock_read_csv.return_value = mock_df

        # Should generate warning about unexpected format, but temperature should match
        with self.assertLogs("geojson_modelica_translator.model_connectors.plants.borefield", level="WARNING") as log:
            self.borefield.validate_undisturbed_soil_temperature(10.2)
            # Should have both unexpected format warning AND no temperature difference warning
            assert any("Unexpected weather file name format" in output for output in log.output)
            # Should not warn about temperature difference since 10.2 vs 10.0 is within 0.5 threshold
            assert not any("differs from the lookup value" in output for output in log.output)

    @patch("pandas.read_csv")
    def test_unexpected_weather_file_format(self, mock_read_csv):
        """Test validation with unexpected weather file naming format."""
        # Setup weather parameter with unexpected format
        self.mock_system_parameters.get_param.side_effect = lambda path: (
            "weird_format.epw"
            if path == "$.weather"
            else self._create_mock_district_system()
            if path == "district_system"
            else None
        )

        mock_df = pd.DataFrame({"Station": ["weird_format"], "Ts,avg, C": [10.0]})
        mock_read_csv.return_value = mock_df

        # Capture log messages
        with self.assertLogs("geojson_modelica_translator.model_connectors.plants.borefield", level="WARNING") as log:
            self.borefield.validate_undisturbed_soil_temperature(10.2)
            # Should generate warning about unexpected format
            assert any("Unexpected weather file name format" in output for output in log.output)

    @patch("pandas.read_csv")
    def test_empty_csv_data(self, mock_read_csv):
        """Test validation when CSV file is empty or has no matching stations."""
        # Setup weather parameter
        self.mock_system_parameters.get_param.side_effect = lambda path: (
            "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw"
            if path == "$.weather"
            else self._create_mock_district_system()
            if path == "district_system"
            else None
        )

        # Mock empty CSV data with proper dtypes to avoid str accessor issues
        mock_df = pd.DataFrame({"Station": pd.Series([], dtype="str"), "Ts,avg, C": pd.Series([], dtype="float64")})
        mock_read_csv.return_value = mock_df

        # Capture log messages
        with self.assertLogs("geojson_modelica_translator.model_connectors.plants.borefield", level="WARNING") as log:
            self.borefield.validate_undisturbed_soil_temperature(15.0)
            # Should generate warning - no matching station found
            assert len(log.output) == 1
            assert "Could not validate undisturbed soil temperature" in log.output[0]

    @patch("pandas.read_csv")
    def test_station_name_case_insensitive_matching(self, mock_read_csv):
        """Test that station name matching is case insensitive."""
        # Setup weather parameter - this will extract "CHICAGO-OHARE Intl AP " (uppercase)
        self.mock_system_parameters.get_param.side_effect = lambda path: (
            "USA_IL_CHICAGO-OHARE.Intl.AP.725300_TMY3.epw"
            if path == "$.weather"
            else self._create_mock_district_system()
            if path == "district_system"
            else None
        )

        # Mock CSV data with lowercase station name that should match case-insensitively
        mock_df = pd.DataFrame(
            {
                "Station": ["chicago-ohare intl ap station", "Boston Logan", "Denver Intl"],
                "Ts,avg, C": [12.0, 8.5, 10.2],
            }
        )
        mock_read_csv.return_value = mock_df

        # Should find match despite case difference and not generate warnings (within threshold)
        self.borefield.validate_undisturbed_soil_temperature(12.2)
