# URBANopt Thermal Connector

*Schema for an URBANopt Thermal Connector object*

## Properties

- **`id`** *(string)*: Unique id used to refer to this feature within this dataset.
- **`project_id`** *(string)*: Project which this feature belongs to.
- **`type`** *(string, required)*: Type of feature. Must be one of: `["ThermalConnector"]`.
- **`source_name`** *(string)*: Name of the original data source.
- **`source_id`** *(string)*: Id of the feature in original data source.
- **`name`** *(string)*: Feature name.
- **`connector_type`**: Refer to *[#/definitions/ThermalConnectorType](#definitions/ThermalConnectorType)*.
- **`lengths`** *(array)*: Length of each segment in ft, generated on export.
  - **Items** *(number)*
- **`total_length`** *(number)*: Total length of the connector in ft, generated on export.
- **`start_junction_id`** *(string, required)*: Id of the junction that this connector starts at.
- **`end_junction_id`** *(string, required)*: Id of the junction that this connector ends at.
- **`fluid_temperature_type`**: Classification of temperature range of fluid in this connector. Refer to *[#/definitions/TemperatureType](#definitions/TemperatureType)*.
- **`flow_direction`**: Charcterization of connector, relative to the central plant. Refer to *[#/definitions/FlowDirection](#definitions/FlowDirection)*.
- **`user_data`**: Arbitrary user data.
## Definitions

- <a id="definitions/ThermalConnectorType"></a>**`ThermalConnectorType`** *(string)*: Type of thermal connector. Must be one of: `["OnePipe", "TwoPipe", "ThreePipe", "FourPipe"]`.
- <a id="definitions/TemperatureType"></a>**`TemperatureType`** *(string)*: Temperature of fluid flowing in connector. Must be one of: `["Hot", "Cold", "Ambient"]`.
- <a id="definitions/FlowDirection"></a>**`FlowDirection`** *(string)*: Direction of flow from start junction to end junction. Must be one of: `["Supply", "Return", "Unspecified"]`.
