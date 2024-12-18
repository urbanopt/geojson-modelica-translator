# URBANopt Electrical Junction

*Schema for an URBANopt Electrical Junction object*

## Properties

- **`id`** *(string, required)*: Unique id used to refer to this feature within this dataset.
- **`project_id`** *(string)*: Project which this feature belongs to.
- **`type`** *(string, required)*: Type of feature. Must be one of: `["ElectricalJunction"]`.
- **`source_name`** *(string)*: Name of the original data source.
- **`source_id`** *(string)*: Id of the feature in original data source.
- **`name`** *(string)*: Feature name.
- **`connector_type`**: Refer to *[#/definitions/ElectricalJunctionType](#definitions/ElectricalJunctionType)*.
- **`buildingId`** *(string)*: Id of building if this junction is inside a building.
- **`DSId`** *(string)*: Id of district system if this junction is inside a district system.
- **`user_data`**: Arbitrary user data.
## Definitions

- <a id="definitions/ElectricalJunctionType"></a>**`ElectricalJunctionType`** *(string)*: Type of electrical junction. Must be one of: `["ElectricalJunction"]`.
