# URBANopt District System

*Schema for an URBANopt District System object*

## Properties

- <a id="properties/id"></a>**`id`** *(string)*: Unique id used to refer to this feature within this dataset.
- <a id="properties/project_id"></a>**`project_id`** *(string)*: Project which this feature belongs to.
- <a id="properties/type"></a>**`type`** *(string, required)*: Type of feature. Must be one of: "District System".
- <a id="properties/source_name"></a>**`source_name`** *(string)*: Name of the original data source.
- <a id="properties/source_id"></a>**`source_id`** *(string)*: Id of the feature in original data source.
- <a id="properties/name"></a>**`name`** *(string)*: Feature name.
- <a id="properties/legal_name"></a>**`legal_name`** *(string)*: Legal name used to identify this feature.
- <a id="properties/address"></a>**`address`** *(string)*: Street address.
- <a id="properties/district_system_type"></a>**`district_system_type`** *(required)*: Refer to *[#/definitions/districtSystemType](#definitions/districtSystemType)*.
- <a id="properties/detailed_model_filename"></a>**`detailed_model_filename`** *(string)*: Name of a detailed model which can be loaded from disk as a seed model or complete model. Mapper class decides which measures to disable if this is present.
- <a id="properties/weather_filename"></a>**`weather_filename`** *(string)*: Name of EPW weather file for this district system. Defaults to site's weather_filename.
- <a id="properties/tariff_filename"></a>**`tariff_filename`** *(string)*: Name of the tariff file for this district system. Defaults to site's tariff_filename.
- <a id="properties/equipment"></a>**`equipment`** *(array)*: List of equipment in this plant.
  - <a id="properties/equipment/items"></a>**Items** *(string)*: Refer to *[#/definitions/equipmentType](#definitions/equipmentType)*.
- <a id="properties/user_data"></a>**`user_data`**: Arbitrary user data.
## Definitions

- <a id="definitions/districtSystemType"></a>**`districtSystemType`** *(string)*: Type of district system. Must be one of: "Central Chilled Water", "Central Hot Water", "Central Hot and Chilled Water", "Central Ambient Water", "Central Hot and Cold Water", "Community Photovoltaic", "Transformer", "Transformer with Storage", "Capacitor", or "Electrical Substation".
- <a id="definitions/equipmentType"></a>**`equipmentType`** *(string)*: Type of equipment, listed in order of load served. Must be one of: "Air-Cooled Chiller--Cold Water", "Air-Cooled Chiller--Ambient Water", "Water-Cooled Chiller--Cold Water", "Water-Cooled Chiller---Ambient Water", "Capacitor--150KVAR", "Capacitor--450KVAR", "Cooling Tower--Heat Rejection from Chiller, Cold Water", "Cooling Tower--Heat Rejection from Chiller, Ambient Water", "Cooling Tower--Direct--Chilled Water", "Cooling Tower--Direct--Ambient Water", "Boiler--Hot Water", "Boiler--Ambient Water", "Boiler--Combined Heat and Power--Hot Water", "Boiler--Combined Heat and Power--Ambient Water", "Water to Water Heat Pump--Ambient Water", "Water to Water Heat Pump--Cold Water", "Water to Water Heat Pump--Hot Water", "Air to Water Heat Pump--Ambient Water", "Air to Water Heat Pump--Cold Water", "Air to Water Heat Pump--Hot Water", "Ground Source Heat Pump--Ambient Water", "Ground Source Heat Pump--Cold Water", "Ground Source Heat Pump--Hot Water", "Solar Thermal Array--Ambient Water", "Solar Thermal Array--Hot Water", "Storage--Hot Water", "Storage--Cold Water", "Storage--Ambient Water", "Transformer--25KVA CT", "Transformer--50KVA CT", "Transformer--75KVA CT", "Transformer--25KVA PM", "Transformer--50KVA PM", "Transformer--75KVA PM", "Transformer--100KVA PM", "Transformer--150KVA PM", "Transformer--300KVA PM", "Waste Heat Source--Hot Water", or "Waste Heat Source--Ambient Water".
