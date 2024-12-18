# URBANopt Region

*Schema for an URBANopt Region object*

## Properties

- **`id`** *(string)*: Unique id used to refer to this feature within this dataset.
- **`project_id`** *(string)*: Project which this feature belongs to.
- **`type`** *(string, required)*: Type of feature. Must be one of: `["Region"]`.
- **`region_type`** *(string, required)*: Type of region. Must be one of: `["Taxlot", "Park", "Road", "Lake", "Obstacle"]`.
- **`source_name`** *(string)*: Name of the original data source.
- **`source_id`** *(string)*: Id of the feature in original data source.
- **`name`** *(string)*: Feature name.
- **`legal_name`** *(string)*: Legal name used to identify this feature.
- **`address`** *(string)*: Street address.
- **`footprint_area`** *(number)*: Area of the footprint (ft^2).  Calculated on export.
- **`footprint_perimeter`** *(number)*: Perimeter of the footprint (ft). Calculated on export.
- **`exterior_lighting_zone`** *(string)*: Choice of exterior lighting zone. Must be one of: `["0 - Undeveloped Areas Parks", "1 - Developed Areas Parks", "2 - Neighborhood", "3 - All Other Areas", "4 - High Activity"]`.
- **`taxlot_zoning`** *(string)*: Type of zoning if this feature is a taxlot. Must be one of: `["Vacant", "Mixed", "Residential", "Commercial", "OpenSpace"]`.
- **`user_data`**: Arbitrary user data.
