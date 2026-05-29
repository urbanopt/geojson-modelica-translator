# URBANopt Region

*Schema for an URBANopt Region object*

## Properties

- <a id="properties/id"></a>**`id`** *(string)*: Unique id used to refer to this feature within this dataset.
- <a id="properties/project_id"></a>**`project_id`** *(string)*: Project which this feature belongs to.
- <a id="properties/type"></a>**`type`** *(string, required)*: Type of feature. Must be one of: "Region".
- <a id="properties/region_type"></a>**`region_type`** *(string, required)*: Type of region. Must be one of: "Taxlot", "Park", "Road", "Lake", or "Obstacle".
- <a id="properties/source_name"></a>**`source_name`** *(string)*: Name of the original data source.
- <a id="properties/source_id"></a>**`source_id`** *(string)*: Id of the feature in original data source.
- <a id="properties/name"></a>**`name`** *(string)*: Feature name.
- <a id="properties/legal_name"></a>**`legal_name`** *(string)*: Legal name used to identify this feature.
- <a id="properties/address"></a>**`address`** *(string)*: Street address.
- <a id="properties/footprint_area"></a>**`footprint_area`** *(number)*: Area of the footprint (ft^2).  Calculated on export.
- <a id="properties/footprint_perimeter"></a>**`footprint_perimeter`** *(number)*: Perimeter of the footprint (ft). Calculated on export.
- <a id="properties/exterior_lighting_zone"></a>**`exterior_lighting_zone`** *(string)*: Choice of exterior lighting zone. Must be one of: "0 - Undeveloped Areas Parks", "1 - Developed Areas Parks", "2 - Neighborhood", "3 - All Other Areas", or "4 - High Activity".
- <a id="properties/taxlot_zoning"></a>**`taxlot_zoning`** *(string)*: Type of zoning if this feature is a taxlot. Must be one of: "Vacant", "Mixed", "Residential", "Commercial", or "OpenSpace".
- <a id="properties/user_data"></a>**`user_data`**: Arbitrary user data.
