class ApiDto:

    def api_id(self) -> str:
        """
        return current object id on Web API format.
        """
        pass

    def endpoint(self) -> str:
        """
        return endpoint name in Web API
        """
        pass

    def to_json(self):
        """
        transform current object into a dumpable dict compatible with JSON format.
        :return: dumpable dict.
        """
        pass

    def from_json(self, obj):
        """
        load the object from a dict originating of a JSON format.
        :param obj: object to load information from.
        """
        pass
