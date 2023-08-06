import uuid
from .api_dto import ApiDto


class Experiment(ApiDto):
    """
    An experiment is a container to track all executions made in the same context.

    :ivar experiment_id: The UUID of the Experiment.
    :ivar key: Logical String ID of the Experiment
    :ivar name: A simple name helping the user identifying the experiment.
    """
    def __init__(self, experiment_id=None, key=None, name=None, description=None):
        if experiment_id is None:
            self.experiment_id = uuid.uuid4()
        else:
            self.experiment_id = experiment_id
        self.key = key
        self.name = name
        self.description = description
        self.twinId = None
        self.twinGraphId = None
        self.createdById = None
        self.createdDate = None
        self.updatedById = None
        self.updatedDate = None

    def api_id(self) -> str:
        """
        Id of the experiment (experiment_id)

        :return: string formatted UUID of the Experiment.
        """
        return str(self.experiment_id).upper()

    def endpoint(self) -> str:
        """
        Name of the endpoints used to manipulate execution.
        :return: Endpoint name.
        """
        return "Experiments"

    def to_json(self):
        """
        Convert to a json version of Experiment definition.
        """
        obj = {
            "id": str(self.experiment_id)
        }
        if self.key is not None:
            obj["key"] = str(self.key)
        if self.name is not None:
            obj["name"] = str(self.name)
        if self.description is not None:
            obj["description"] = str(self.description)
        if self.twinId is not None:
            obj["twinId"] = str(self.twinId)
        if self.twinGraphId is not None:
            obj["twinGraphId"] = str(self.twinGraphId)
        if self.createdById is not None:
            obj["createdById"] = str(self.createdById)
        if self.createdDate is not None:
            obj["createdDate"] = str(self.createdDate)
        if self.updatedById is not None:
            obj["updatedById"] = str(self.updatedById)
        if self.updatedDate is not None:
            obj["updatedDate"] = str(self.updatedDate)
        return obj

    def from_json(self, obj):
        """
        Load an experiment from a stored JSON object.
        """
        if "id" in obj.keys():
            self.experiment_id = uuid.UUID(obj["id"])
        if "key" in obj.keys() and obj["key"] is not None:
            self.key = obj["key"]
        if "name" in obj.keys() and obj["name"] is not None:
            self.name = obj["name"]
        if "description" in obj.keys() and obj["description"] is not None:
            self.description = obj["description"]
        if "twinId" in obj.keys() and obj["twinId"] is not None:
            self.twinId = obj["twinId"]
        if "twinGraphId" in obj.keys() and obj["twinGraphId"] is not None:
            self.twinGraphId = obj["twinGraphId"]
        if "createdById" in obj.keys() and obj["createdById"] is not None:
            self.createdById = obj["createdById"]
        if "createdDate" in obj.keys() and obj["createdDate"] is not None:
            self.createdDate = obj["createdDate"]
        if "updatedById" in obj.keys() and obj["updatedById"] is not None:
            self.updatedById = obj["updatedById"]
        if "updatedDate" in obj.keys() and obj["updatedDate"] is not None:
            self.updatedDate = obj["updatedDate"]

