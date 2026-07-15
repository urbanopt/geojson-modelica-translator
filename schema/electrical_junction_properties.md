# URBANopt Electrical Junction

*Schema for an URBANopt Electrical Junction object*

## Properties

- <a id="properties/id"></a>**`id`** *(string, required)*: Unique id used to refer to this feature within this dataset.
- <a id="properties/project_id"></a>**`project_id`** *(string)*: Project which this feature belongs to.
- <a id="properties/type"></a>**`type`** *(string, required)*: Type of feature. Must be one of: "ElectricalJunction".
- <a id="properties/source_name"></a>**`source_name`** *(string)*: Name of the original data source.
- <a id="properties/source_id"></a>**`source_id`** *(string)*: Id of the feature in original data source.
- <a id="properties/name"></a>**`name`** *(string)*: Feature name.
- <a id="properties/connector_type"></a>**`connector_type`**: Refer to *[#/definitions/ElectricalJunctionType](#definitions/ElectricalJunctionType)*.
- <a id="properties/buildingId"></a>**`buildingId`** *(string)*: Id of building if this junction is inside a building.
- <a id="properties/DSId"></a>**`DSId`** *(string)*: Id of district system if this junction is inside a district system.
- <a id="properties/user_data"></a>**`user_data`**: Arbitrary user data.
## Definitions

- <a id="definitions/ElectricalJunctionType"></a>**`ElectricalJunctionType`** *(string)*: Type of electrical junction. Must be one of: "ElectricalJunction".
