# URBANopt Thermal Junction

*Schema for an URBANopt Thermal Junction object*

## Properties

- **`id`** *(string)*: Unique id used to refer to this feature within this dataset.
- **`project_id`** *(string)*: Project which this feature belongs to.
- **`type`** *(string, required)*: Type of feature. Must be one of: `["ThermalJunction"]`.
- **`source_name`** *(string)*: Name of the original data source.
- **`source_id`** *(string)*: Id of the feature in original data source.
- **`name`** *(string)*: Feature name.
- **`connector_type`**: Refer to *[#/definitions/ThermalJunctionType](#definitions/ThermalJunctionType)*.
- **`building_id`** *(string)*: Id of building if this junction is inside a building.
- **`district_system_id`** *(string)*: Id of district system if this junction is inside a district system.
- **`pump_presence`** *(boolean)*: Presence of pump: true if present, false if absent.
- **`connection_type`**: Characterize the connection as series or parallel. Refer to *[#/definitions/ThermalJunctionConnectionType](#definitions/ThermalJunctionConnectionType)*.
- **`user_data`**: Arbitrary user data.
## Definitions

- <a id="definitions/ThermalJunctionType"></a>**`ThermalJunctionType`** *(string)*: Type of thermal junction. Must be one of: `["DES", "ETS", "Valve"]`.
- <a id="definitions/ThermalJunctionConnectionType"></a>**`ThermalJunctionConnectionType`** *(string)*: Type of connection for connectors meeting at this junction. Must be one of: `["Series", "Parallel"]`.
