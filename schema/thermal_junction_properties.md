# URBANopt Thermal Junction

*Schema for an URBANopt Thermal Junction object*

## Properties

- <a id="properties/id"></a>**`id`** *(string)*: Unique id used to refer to this feature within this dataset.
- <a id="properties/project_id"></a>**`project_id`** *(string)*: Project which this feature belongs to.
- <a id="properties/type"></a>**`type`** *(string, required)*: Type of feature. Must be one of: "ThermalJunction".
- <a id="properties/source_name"></a>**`source_name`** *(string)*: Name of the original data source.
- <a id="properties/source_id"></a>**`source_id`** *(string)*: Id of the feature in original data source.
- <a id="properties/name"></a>**`name`** *(string)*: Feature name.
- <a id="properties/connector_type"></a>**`connector_type`** *(required)*: Refer to *[#/definitions/ThermalJunctionType](#definitions/ThermalJunctionType)*.
- <a id="properties/building_id"></a>**`building_id`** *(string)*: Id of building if this junction is inside a building.
- <a id="properties/district_system_id"></a>**`district_system_id`** *(string)*: Id of district system if this junction is inside a district system.
- <a id="properties/pump_presence"></a>**`pump_presence`** *(boolean)*: Presence of pump: true if present, false if absent.
- <a id="properties/connection_type"></a>**`connection_type`** *(required)*: Characterize the connection as series or parallel. Refer to *[#/definitions/ThermalJunctionConnectionType](#definitions/ThermalJunctionConnectionType)*.
- <a id="properties/user_data"></a>**`user_data`**: Arbitrary user data.
## Definitions

- <a id="definitions/ThermalJunctionType"></a>**`ThermalJunctionType`** *(string)*: Type of thermal junction. Must be one of: "DES", "ETS", or "Valve".
- <a id="definitions/ThermalJunctionConnectionType"></a>**`ThermalJunctionConnectionType`** *(string)*: Type of connection for connectors meeting at this junction. Must be one of: "Series" or "Parallel".
