import uuid
from datetime import datetime, timedelta, timezone


class Request:
    """
    A Request to fetch dataframes from Wizata App.

    To execute the request please use a DS API client.

    :ivar equipments: List of Equipments containing Digital Twin item and datapoints to fetch.

    :ivar template_id: UUID of the template.
    :ivar template: str unique id of the template.
    :ivar twin_id: UUID of the Digital Twin.
    :ivar twin: str hardware id of the Digital Twin.

    :ivar start: Datetime defining beginning of period.
    :ivar end: Datetime defining end of period.
    :ivar aggregation: Aggregation method to fetch, accept "mean" and "stddev".
    :ivar interval: Interval in seconds between each aggregation.
    :ivar filters: Filter to apply on the query (not yet fully implemented).
    :ivar connections: Connections rules between equipment to align data in time (not yet fully implemented).
    :ivar null: By default at 'drop' and dropping NaN values. If not intended behavior please set it to 'ignore' or 'all'.
    """

    def __init__(self,
                 datapoints=None,
                 start=None,
                 end=None,
                 agg_method='mean',
                 interval=None,
                 null='drop',
                 template_id=None,
                 template=None,
                 twin_id=None,
                 twin=None,
                 request_id=None,
                 filters=None,
                 options=None):
        if request_id is None:
            request_id = uuid.uuid4()
        self.request_id = request_id
        self.function = None

        # Equipments & Data Points
        self.equipments = []
        if datapoints is not None:
            self.add_datapoints(datapoints)

        # Template & Registration
        self.template = None
        self.select_template(
             template_id=template_id,
             template_key=template,
             twin_id=twin_id,
             twin_hardware_id=twin
        )

        self.start = start
        self.end = end

        self.aggregation = agg_method
        if interval is not None:
            self.interval = int(interval) / 1000

        self.filters = filters
        self.options = options

        self.on_off_sensor = None
        self.restart_time = None
        self.sensitivity = None
        self.dataframe = None
        self.extra_data = None
        self.target_feat = None
        self.connections = None
        self.name = None

        self.null = null

    def prepare(self):
        """
        prepare a dict JSON compatible only for the QUERY part of the request.

        :return: a dict JSON compatible
        """
        query = {}
        if self.request_id is not None:
            query["id"] = str(self.request_id)
        if self.equipments is not None:
            query["equipments_list"] = self.equipments
        else:
            raise KeyError("Missing data points inside the query - add_datapoints")
        if self.start is not None and self.end is not None:
            query["timeframe"] = {
                "start": self.__format_date(self.start),
                "end": self.__format_date(self.end)
            }
        else:
            raise KeyError("Missing start and end date, please use datatime format")
        if self.aggregation is not None and self.interval:
            query["aggregations"] = {
                "agg_method": self.aggregation,
                "interval": self.interval * 1000
            }
        else:
            raise KeyError("Missing aggregations information inside the request")
        if self.null is not None and self.null != 'drop':
            query['null'] = self.null
        if self.template is not None:
            query['template'] = self.template
        if self.filters is not None:
            query['filters'] = self.filters
        if self.options is not None:
            query['options'] = self.options
        return query

    def __format_date(self, dt_to_format):
        if isinstance(dt_to_format, datetime):
            millisec = dt_to_format.timestamp() * 1000
            return int(millisec)
        else:
            raise TypeError("date is not a valid datetime")

    # add datapoints without any reference to an equipment
    def add_datapoints(self, datapoints, shift: int = 0):
        """
        Add datapoints to fetch without defining its equipments.
        :param datapoints: List(str) of datapoints to fetch identified by Hardware ID.
        :param shift: Shift to apply in seconds on timestamp, by default 0.
        """
        self.equipments.append({
            "id": None,
            "datapoints": list(datapoints),
            "shift": str(shift) + "s"
        })

    def add_equipment(self, equipment_id: uuid.UUID, datapoints, shift=0):
        """
        Add datapoints to fetch with a Digital Twin ID identification.
        :param equipment_id: UUID of the Digital Twin ID to which the datapoints are linked.
        :param datapoints: List(str) of datapoints to fetch identified by Hardware ID.
        :param shift: Shift to apply in seconds on timestamp, by default 0.
        """
        if not isinstance(equipment_id, uuid.UUID):
            raise TypeError("equipment_id must be of type uuid.UUID")
        for equipment in self.equipments:
            if "id" in equipment.keys() and equipment["id"] == str(equipment_id):
                raise ValueError("equipment_id is already in the request please remove it before adding datapoints.")
        self.equipments.append({
            "id": str(equipment_id),
            "datapoints": list(datapoints),
            "shift": str(shift) + "s"
        })

    # attempt to remove equipment from the query if exists
    def remove_equipment(self, equipment_id: uuid.UUID):
        """
        Remove an equipment from the list including all its listed datapoints.
        :param equipment_id: UUID of the Digital Twin item.
        """
        if equipment_id is not None and not isinstance(equipment_id, uuid.UUID):
            raise TypeError("equipment_id must be None or of type uuid.UUID")
        found = None
        for equipment in self.equipments:
            if "id" in equipment.keys() and equipment["id"] == str(equipment_id):
                found = equipment
        if found is not None:
            self.equipments.remove(equipment)

    def set_aggregation(self, method, interval):
        """
        Specifies aggregation properties
        :param method: 'mean' or 'stddev'
        :param interval: interval in ms (will be stored in seconds)
        """
        self.aggregation = method
        if interval is not None:
            self.interval = int(interval) / 1000

    def select_template(self,
                        template_id=None,
                        template_key=None,
                        twin_id=None,
                        twin_hardware_id=None):
        """
        Select a template and its registration.
        :param template_id: template UUID
        :param template_key: template key ( ignored if template_id specified )
        :param twin_id: Digital Twin UUID
        :param twin_hardware_id: hardware ID of Digital Twin ( ignored if twin_id specified )
        """
        if template_id is None and template_key is None and twin_id is None and twin_hardware_id is None:
            self.template = None
            return
        else:
            self.template = {}

            if template_id is not None:
                self.template['template_id'] = uuid.UUID(template_id)
            elif template_key is not None:
                self.template['template_key'] = str(template_key)
            else:
                raise ValueError('A twin can only be specified with its template')

            if twin_id is not None:
                self.template['twin_id'] = uuid.UUID(twin_id)
            elif twin_hardware_id is not None:
                self.template['twin_hardware_id'] = str(twin_hardware_id)
            else:
                raise ValueError('A template can only be specified with its registered twin')

    def to_json(self):
        """
        convert to a dict JSON compatible for all properties. For query only, use prepare().

        :return: a dict JSON compatible
        """

        # Prepare is 'to_json' without future obsolete properties
        obj = self.prepare()

        if self.target_feat is not None:
            obj["target_feat"] = {
                "sensor": self.target_feat["sensor"],
                "operator": self.target_feat["operator"],
                "threshold": self.target_feat["threshold"]
            }
        if self.on_off_sensor is not None and self.restart_time is not None:
            obj["restart_filter"] = {
                "on_off_sensor": self.on_off_sensor,
                "stop_restart_time": self.restart_time
            }

        if self.sensitivity is not None:
            obj["sensitivity"] = self.sensitivity

        if self.extra_data is not None:
            obj["extra_data"] = self.extra_data

        return obj

    def from_json(self, json_data):
        """
        load a request based on dict from a JSON file.

        :param json_data: JSON formatted dictionnary object representing a query.
        """
        if "id" in json_data.keys():
            self.request_id = uuid.UUID(json_data["id"])

        if "name" in json_data.keys():
            self.name = json_data["name"]

        found_dps = False
        if "equipments_list" in json_data.keys():
            self.equipments = json_data["equipments_list"]
            for equipment in self.equipments:
                if "datapoints" not in equipment.keys():
                    raise KeyError("No 'data points' have been provided for equipment with id '" +
                                   str(equipment["id"]) + "'")
                else:
                    found_dps = True

        if not found_dps:
            if "template" in json_data.keys():
                self.template = json_data["template"]
            else:
                raise KeyError('no equipments lists nor template specified.')

        if "timeframe" not in json_data.keys():
            raise KeyError("No 'time range' have been selected, please set it up and re-try.")

        if "start" not in json_data["timeframe"].keys():
            raise KeyError("No 'start time' have been selected, please set it up and re-try.")
        self.start = datetime.fromtimestamp(json_data["timeframe"]["start"] / 1000, timezone.utc)

        if "end" not in json_data["timeframe"].keys():
            raise KeyError("No 'end time' have been selected, please set it up and re-try.")
        self.end = datetime.fromtimestamp(json_data["timeframe"]["end"] / 1000, timezone.utc)

        if "aggregations" not in json_data.keys():
            raise KeyError("No 'aggregations' have been selected, please set it up and re-try.")

        if "agg_method" not in json_data["aggregations"].keys():
            raise KeyError("No 'Aggregation Method' have been selected, please set it up and re-try.")
        self.aggregation = json_data["aggregations"]["agg_method"]

        if "interval" not in json_data["aggregations"].keys():
            raise KeyError("No 'Aggregation Interval' have been selected, please set it up and re-try.")
        self.interval = int(json_data["aggregations"]["interval"] / 1000)

        if "filters" in json_data.keys():
            self.filters = json_data["filters"]
        else:
            self.filters = {}

        if "options" in json_data.keys():
            self.options = json_data["options"]
        else:
            self.options = {}

        if "connections" in json_data.keys():
            self.connections = json_data["connections"]

        if "null" in json_data.keys():
            self.null = json_data["null"]

        if "target_feat" in json_data.keys():
            self.target_feat = json_data["target_feat"]
            if "sensor" not in self.target_feat.keys():
                raise KeyError("No 'sensor' have been declared inside the target feature, this is a technical error.")
            if "operator" not in self.target_feat.keys():
                raise KeyError("No 'operator' have been declared inside the target feature, this is a technical error.")
            if "threshold" not in self.target_feat.keys():
                raise KeyError("No 'threshold' have been declared inside the target feature, this is a technical error.")

        if "restart_filter" in json_data.keys():
            self.on_off_sensor = json_data["restart_filter"]["on_off_sensor"]
            self.restart_time = json_data["restart_filter"]["stop_restart_time"]

        if "sensitivity" in json_data.keys():
            self.sensitivity = json_data["sensitivity"]

        if "extra_data" in json_data.keys():
            self.extra_data = json_data["extra_data"]


