class Base(object):
    """
    Base class of the model connectors. The connectors can utilize various methods to create a building (or other
    feature) to a detailed Modelica connection. For example, a simple RC model (using TEASER), a ROM, CSV file, etc.
    """

    def __init__(self, urbanopt_building):
        # extract data out of the urbanopt_building object and store into the base object

        # TODO: Need to convert units, these should exist on the urbanopt_building object
        # TODO: Abstract out the GeoJSON functionality
        self.area = urbanopt_building.feature.properties['floor_area'] * 0.092936  # ft2 -> m2
        self.building = urbanopt_building
        self.building_id = urbanopt_building.feature.properties['id']
        self.building_type = urbanopt_building.feature.properties['building_type']
        self.floor_height = urbanopt_building.feature.properties['height'] * 0.3048  # ft -> m
        self.num_stories = urbanopt_building.feature.properties['number_of_stories_above_ground']
        self.num_stories_below_grade = urbanopt_building.feature.properties['number_of_stories'] - self.num_stories
        self.year_built = urbanopt_building.feature.properties['year_built']

    # These methods need to be defined in each of the derived model connectors
    # def to_modelica(self):
