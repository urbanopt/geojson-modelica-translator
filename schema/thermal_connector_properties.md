# URBANopt Thermal Connector

*Schema for an URBANopt Thermal Connector object*

## Properties

- <a id="properties/id"></a>**`id`** *(string)*: Unique id used to refer to this feature within this dataset.
- <a id="properties/project_id"></a>**`project_id`** *(string)*: Project which this feature belongs to.
- <a id="properties/type"></a>**`type`** *(string, required)*: Type of feature. Must be one of: "ThermalConnector".
- <a id="properties/source_name"></a>**`source_name`** *(string)*: Name of the original data source.
- <a id="properties/source_id"></a>**`source_id`** *(string)*: Id of the feature in original data source.
- <a id="properties/name"></a>**`name`** *(string)*: Feature name.
- <a id="properties/connector_type"></a>**`connector_type`** *(required)*: Refer to *[#/definitions/ThermalConnectorType](#definitions/ThermalConnectorType)*.
- <a id="properties/lengths"></a>**`lengths`** *(array)*: Length of each segment in meters, generated on export.
  - <a id="properties/lengths/items"></a>**Items** *(number)*
- <a id="properties/total_length"></a>**`total_length`** *(number)*: Total length of the connector in meters, generated on export.
- <a id="properties/start_junction_id"></a>**`start_junction_id`** *(string, required)*: Id of the junction that this connector starts at.
- <a id="properties/end_junction_id"></a>**`end_junction_id`** *(string, required)*: Id of the junction that this connector ends at.
- <a id="properties/fluid_temperature_type"></a>**`fluid_temperature_type`** *(required)*: Classification of temperature range of fluid in this connector. Refer to *[#/definitions/TemperatureType](#definitions/TemperatureType)*.
- <a id="properties/flow_direction"></a>**`flow_direction`** *(required)*: Charcterization of connector, relative to the central plant. Refer to *[#/definitions/FlowDirection](#definitions/FlowDirection)*.
- <a id="properties/user_data"></a>**`user_data`**: Arbitrary user data.
## Definitions

- <a id="definitions/ThermalConnectorType"></a>**`ThermalConnectorType`** *(string)*: Type of thermal connector. Must be one of: "OnePipe", "TwoPipe", "ThreePipe", or "FourPipe".
- <a id="definitions/TemperatureType"></a>**`TemperatureType`** *(string)*: Temperature of fluid flowing in connector. Must be one of: "Hot", "Cold", or "Ambient".
- <a id="definitions/FlowDirection"></a>**`FlowDirection`** *(string)*: Direction of flow from start junction to end junction. Must be one of: "Supply", "Return", or "Unspecified".
