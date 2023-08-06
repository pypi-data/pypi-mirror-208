import uuid
from .sql_dto import SqlDto


class DataPoint(SqlDto):
    """
    A datapoint reference a time-series tag stored on DB.

    :ivar hardware_id: The unique logical hardware Id of the datapoint.
    """

    def __init__(self, hardware_id=None):
        if hardware_id is None:
            self.hardware_id = uuid.uuid4()
        else:
            self.hardware_id = hardware_id

    def from_json(self, obj):
        """
        Load the datapoint entity from a dictionary.

        :param obj: Dict version of the datapoint.
        """
        if "hardwareId" in obj.keys():
            self.hardware_id = obj["hardwareId"]

    def to_json(self):
        """
        Convert the datapoint to a dictionary compatible to JSON format.

        :return: dictionary representation of the datapoint object.
        """
        obj = {
            "hardwareId": str(self.hardware_id)
        }
        return obj

