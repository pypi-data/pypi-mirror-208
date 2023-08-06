class SqlDto:

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
