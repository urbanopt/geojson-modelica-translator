class GeoJsonValidationError(Exception):
    pass


class UrbanOptLoad:
    """An UrbanOptLoad is a container for holding Building-related data in a dictionary. This object
    does not do much work on the GeoJSON definition of the data at the moment, rather it creates
    an isolation layer between the GeoJSON data and the GMT.
    """

    def __init__(self, feature):
        self.feature = feature
        self.id = feature.get("properties", {}).get("id", None)

        # do some validation
        if self.id is None:
            raise GeoJsonValidationError("GeoJSON feature requires an ID property but value was null")

    def __str__(self):
        return f"ID: {self.id}"
