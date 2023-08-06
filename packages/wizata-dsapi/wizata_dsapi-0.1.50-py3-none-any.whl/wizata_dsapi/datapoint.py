import uuid
from enum import Enum
from .sql_dto import SqlDto


class BusinessType(Enum):
    TELEMETRY = 0
    SET_POINTS = 1
    LOGICAL = 2
    MEASUREMENT = 3


class DataPoint(SqlDto):
    """
    A datapoint reference a time-series tag stored on DB.

    :ivar hardware_id: The unique logical hardware Id of the datapoint.
    """

    def __init__(self,
                 hardware_id=None,
                 business_type: BusinessType = None):
        if hardware_id is None:
            self.hardware_id = uuid.uuid4()
        else:
            self.hardware_id = hardware_id
        self.business_type = business_type

    def from_json(self, obj):
        """
        Load the datapoint entity from a dictionary.

        :param obj: Dict version of the datapoint.
        """
        if "hardwareId" in obj.keys():
            self.hardware_id = obj["hardwareId"]

        if "businessType" in obj.keys():
            self.business_type = BusinessType(int(obj["businessType"]))

    def to_json(self):
        """
        Convert the datapoint to a dictionary compatible to JSON format.

        :return: dictionary representation of the datapoint object.
        """
        obj = {
            "hardwareId": str(self.hardware_id)
        }
        if self.business_type is not None and isinstance(self.business_type, BusinessType):
            obj["businessType"] = self.business_type.value
        return obj

