import uuid
import json
from .api_dto import ApiDto


class Template(ApiDto):
    """
    Template of a solution and/or asset.

    :ivar template_id: UUID of the Template.
    :ivar key: str unique id identifying the Template.
    :ivar name: logical display name of the Template.
    :ivar properties: list of Property { type , name } of the solution.

    Properties only support type 'datapoint', 'float', 'integer' or 'string'
    """

    def __init__(self, template_id=None, key=None, name=None, properties=None):
        if template_id is None:
            self.template_id = uuid.uuid4()
        else:
            self.template_id = template_id
        self.key = key
        self.name = name
        self.properties = properties

    def api_id(self) -> str:
        """
        Id of the Template (template_id)

        :return: string formatted UUID of the template.
        """
        return str(self.template_id).upper()

    def endpoint(self) -> str:
        """
        Name of the endpoints used to manipulate templates.
        :return: Endpoint name.
        """
        return "Templates"

    def from_json(self, obj):
        """
        Load the Template entity from a dictionary.

        :param obj: Dict version of the Template.
        """
        if "id" in obj.keys():
            self.template_id = uuid.UUID(obj["id"])
        if "key" in obj.keys() and obj["key"] is not None:
            self.key = obj["key"]
        if "name" in obj.keys() and obj["name"] is not None:
            self.name = obj["name"]
        if "properties" in obj.keys() and obj["properties"] is not None:
            if isinstance(obj["properties"], str):
                properties = json.loads(obj["properties"])
            else:
                properties = obj["properties"]
            # add properties to add method to ensure unicity of name and validity of type
            for to_add in properties:
                self.add_property(to_add)

    def to_json(self):
        """
        Convert the template to a dictionary compatible to JSON format.

        :return: dictionary representation of the Template object.
        """
        obj = {
            "id": str(self.template_id)
        }
        if self.key is not None:
            obj["key"] = str(self.key)
        if self.name is not None:
            obj["name"] = str(self.name)
        if self.properties is not None:
            obj["properties"] = json.dumps(self.properties)
        return obj

    def add_property(self, property_value):
        """
        add a property in list of properties
        :param property_value: property { type , name }
        """
        if self.properties is None:
            self.properties = []
        if "type" not in property_value:
            raise KeyError("property must have a type.")
        if "name" not in property_value:
            raise KeyError("property must have a name")
        if property_value["type"] not in ['datapoint', 'float', 'integer', 'string']:
            raise ValueError('property type must be datapoint, float, integer or string')
        for existing_property in self.properties:
            if existing_property["name"] == property_value["name"]:
                raise ValueError(f'property {property_value["name"]} already exists in template.')
        self.properties.append(property_value)

    def remove_property(self, name):
        """
        remove a property from the list based on its name
        :param name: property to remove
        """
        found_property = None
        for existing_property in self.properties:
            if existing_property["name"] == name:
                found_property = existing_property
        if self.properties is not None and found_property is not None:
            self.properties.remove(found_property)


