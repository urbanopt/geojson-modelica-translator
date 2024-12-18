# URBANopt Electrical Connector

*Schema for an URBANopt Electrical Connector object*

## Properties

- **`id`** *(string, required)*: Unique id used to refer to this feature within this dataset.
- **`project_id`** *(string)*: Project which this feature belongs to.
- **`type`** *(string, required)*: Type of feature. Must be one of: `["ElectricalConnector"]`.
- **`source_name`** *(string)*: Name of the original data source.
- **`source_id`** *(string)*: Id of the feature in original data source.
- **`name`** *(string)*: Feature name.
- **`connector_type`**: Refer to *[#/definitions/ElectricalLineType](#definitions/ElectricalLineType)*.
- **`lengths`** *(array)*: Length (ft) of each segment, generated on export.
  - **Items** *(number)*
- **`total_length`** *(number)*: Total length (ft) of the line, generated on export.
- **`startJunctionId`** *(string, required)*: Id of the junction that this line starts at.
- **`line_properties`** *(object)*: A sub-element containing all the attributes that can be assigned to a line, including wires.
  - **`is_switch`** *(boolean)*: Flag indicating if the line is a switch or not.
  - **`is_fuse`** *(boolean)*: Flag indicating if the line is a fuse or not.
  - **`is_open`** *(boolean)*: Flag indicating if the switch/fuse is a open or not.
- **`wires`** *(array)*: Array of wires that are on the line.
  - **Items** *(string)*: Refer to *[#/definitions/WireType](#definitions/WireType)*.
- **`endJunctionId`** *(string, required)*: Id of the junction that this line ends at.
- **`user_data`**: Arbitrary user data.
## Definitions

- <a id="definitions/ElectricalLineType"></a>**`ElectricalLineType`** *(string)*: Type of electrical line. Must be one of: `["Wire"]`.
- <a id="definitions/WireType"></a>**`WireType`** *(string)*: Type of wire used. Must be one of: `["OH TPLX #4 S1", "OH TPLX #4 S2", "OH TPLX #4 A", "OH TPLX #4 B", "OH TPLX #4 C", "OH TPLX #4 N", "OH TPLX 1/0 S1", "OH TPLX 1/0 S2", "OH TPLX 1/0 A", "OH TPLX 1/0 B", "OH TPLX 1/0 C", "OH TPLX 1/0 N", "OH TPLX 2/0 S1", "OH TPLX 2/0 S2", "OH TPLX 2/0 A", "OH TPLX 2/0 B", "OH TPLX 2/0 C", "OH TPLX 2/0 N", "OH TPLX 4/0 S1", "OH TPLX 4/0 S2", "OH TPLX 4/0 A", "OH TPLX 4/0 B", "OH TPLX 4/0 C", "OH TPLX 4/0 N", "OH AL #2 A", "OH AL #2 B", "OH AL #2 C", "OH AL #2 N", "OH AL #4 A", "OH AL #4 B", "OH AL #4 C", "OH AL #4 N", "OH AL 1/0 A", "OH AL 1/0 B", "OH AL 1/0 C", "OH AL 1/0 N", "OH AL 2/0 A", "OH AL 2/0 B", "OH AL 2/0 C", "OH AL 2/0 N", "OH AL 4/0 A", "OH AL 4/0 B", "OH AL 4/0 C", "OH AL 4/0 N", "OH AL 336kcmil A", "OH AL 336kcmil B", "OH AL 336kcmil C", "OH AL 336kcmil N", "OH AL 477kcmil A", "OH AL 477kcmil B", "OH AL 477kcmil C", "OH AL 477kcmil N", "OH AL 795kcmil A", "OH AL 795kcmil B", "OH AL 795kcmil C", "OH AL 795kcmil N", "UG TPLX #4 S1", "UG TPLX #4 S2", "UG TPLX #4 A", "UG TPLX #4 B", "UG TPLX #4 C", "UG TPLX #4 N", "UG TPLX 1/0 S1", "UG TPLX 1/0 S2", "UG TPLX 1/0 A", "UG TPLX 1/0 B", "UG TPLX 1/0 C", "UG TPLX 1/0 N", "UG TPLX 2/0 S1", "UG TPLX 2/0 S2", "UG TPLX 2/0 A", "UG TPLX 2/0 B", "UG TPLX 2/0 C", "UG TPLX 2/0 N", "UG TPLX 4/0 S1", "UG TPLX 4/0 S2", "UG TPLX 4/0 A", "UG TPLX 4/0 B", "UG TPLX 4/0 C", "UG TPLX 4/0 N", "UG AL #2 A", "UG AL #2 B", "UG AL #2 C", "UG AL #2 N", "UG AL #4 A", "UG AL #4 B", "UG AL #4 C", "UG AL #4 N", "UG AL 1/0 A", "UG AL 1/0 B", "UG AL 1/0 C", "UG AL 1/0 N", "UG AL 2/0 A", "UG AL 2/0 B", "UG AL 2/0 C", "UG AL 2/0 N", "UG AL 4/0 A", "UG AL 4/0 B", "UG AL 4/0 C", "UG AL 4/0 N", "UG AL 350kcmil A", "UG AL 350kcmil B", "UG AL 350kcmil C", "UG AL 350kcmil N", "UG AL 500kcmil A", "UG AL 500kcmil B", "UG AL 500kcmil C", "UG AL 500kcmil N", "UG AL 750kcmil A", "UG AL 750kcmil B", "UG AL 750kcmil C", "UG AL 750kcmil N", "UG AL 1000kcmil A", "UG AL 1000kcmil B", "UG AL 1000kcmil C", "UG AL 1000kcmil N"]`.
