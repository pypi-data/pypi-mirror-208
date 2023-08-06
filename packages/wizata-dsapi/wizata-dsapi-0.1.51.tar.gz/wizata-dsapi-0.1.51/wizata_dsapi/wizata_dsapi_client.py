import datetime
import json
import uuid
import sys
from typing import Tuple

import dill
import requests
import pickle
import pandas
import plotly
import msal
import os
import types
import sklearn
import wizata_dsapi
from pandas import DataFrame
from wizata_dsapi import MLModel

import string
import random

from .plot import Plot
from .request import Request
from .mlmodel import MLModel
from .experiment import Experiment
from .script import Script
from .execution import Execution
from .dsapi_json_encoder import DSAPIEncoder
from .ds_dataframe import DSDataFrame
from .model_toolkit import predict
from .template import Template
from .twinregistration import TwinRegistration
from .twin import Twin

class WizataDSAPIClient:

    def __init__(self,
                 client_id=None,
                 scope=None,
                 tenant_id=None,
                 username=None,
                 password=None,
                 domain="localhost",
                 protocol="https"):

        # properties
        self.domain = domain
        self.protocol = protocol

        # authentication
        self.__username = username
        self.__password = password

        self.__client_id = client_id
        self.__tenant_id = tenant_id
        if tenant_id is not None:
            self.__authority = "https://login.microsoftonline.com/" + tenant_id
        self.__scopes = [scope]

        self.__interactive_token = None

        self.__app = msal.PublicClientApplication(
            client_id=self.__client_id,
            authority=self.__authority
        )

    def authenticate(self):
        result = self.__app.acquire_token_interactive(
            scopes=self.__scopes,
            success_template="""<html><body>You are authenticated and your code is running, you can close this page.<script>setTimeout(function(){window.close()}, 3000);</script></body></html> """
        )
        self.__interactive_token = result["access_token"]

    def __url(self):
        return self.protocol + "://" + self.domain + "/dsapi/"

    def __token(self):
        # Interactive Authentication
        if self.__interactive_token is not None:
            return self.__interactive_token

        # Silent Authentication
        result = None
        accounts = self.__app.get_accounts(username=self.__username)
        if accounts:
            # If there is an account in the cache, try to get the token silently
            result = self.__app.acquire_token_silent(scopes=self.__scopes, account=accounts[0])

        if not result:
            # If there is no cached token, try to get a new token using the provided username and password
            result = self.__app.acquire_token_by_username_password(
                username=self.__username,
                password=self.__password,
                scopes=self.__scopes
            )

        if "error_description" in result.keys():
            raise RuntimeError(str(result["error_description"]))

        if "access_token" in result.keys():
            return result["access_token"]
        else:
            raise RuntimeError(str(result))

    def __header(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.__token()}'
        }

    def __raise_error(self, response):
        json_content = response.json()
        if "errors" in json_content.keys():
            message = json_content["errors"][0]["message"]
            return RuntimeError(str(response.status_code) + " - " + message)
        else:
            return RuntimeError(str(response.status_code) + " - " + response.reason)

    def lists(self, str_type):
        """
        lists all elements of a specific entity.

        :param str_type: plural name of the entity (e.g. scripts, plots, mlmodels, dataframes...)
        :return: list of all elements with at least the id property.
        """
        if str_type == "scripts":
            response = requests.request("GET",
                                        self.__url() + "scripts/",
                                        headers=self.__header()
                                        )
            if response.status_code == 200:
                scripts = []
                for json_model in response.json():
                    scripts.append(Script(uuid.UUID(json_model["id"])))
                return scripts
            else:
                raise self.__raise_error(response)
        elif str_type == "plots":
            response = requests.request("GET",
                                        self.__url() + "plots/",
                                        headers=self.__header()
                                        )
            if response.status_code == 200:
                plots = []
                for plot in response.json():
                    plots.append(Plot(plot["id"]))
                return plots
            else:
                raise self.__raise_error(response)
        elif str_type == "mlmodels":
            response = requests.request("GET",
                                        self.__url() + "mlmodels/",
                                        headers=self.__header()
                                        )
            if response.status_code == 200:
                json_models = response.json()
                ml_models = []
                for json_model in json_models:
                    ml_models.append(MLModel(uuid.UUID(json_model["id"])))
                return ml_models
            else:
                raise self.__raise_error(response)
        elif str_type == "dataframes":
            response = requests.request("GET",
                                        self.__url() + "dataframes/",
                                        headers=self.__header()
                                        )
            if response.status_code == 200:
                json_dfs = response.json()
                dfs = []
                for json_model in json_dfs:
                    dfs.append(DSDataFrame(uuid.UUID(json_model["id"])))
                return dfs
            else:
                raise self.__raise_error(response)
        elif str_type == "templates":
            response = requests.request("GET",
                                        self.__url() + "templates/",
                                        headers=self.__header()
                                        )
            if response.status_code == 200:
                templates_json = response.json()
                templates = []
                for template_json in templates_json:
                    template = Template()
                    template.from_json(template_json)
                    templates.append(template)
                return templates
            else:
                raise self.__raise_error(response)
        else:
            raise TypeError("Type not supported.")

    def get(self,
            obj=None,
            script_name=None,
            experiment_key=None,
            model_key=None,
            template_key=None,
            twin_hardware_id=None):
        """
        get full content of an object identified with is id.

        :param obj: object of a supported entity with at list its id
        :param script_name: alternatively you can use a function name to get a script
        :param experiment_key: alternatively you can use an experiment key to get an experiment
        :param model_key: model key you want to get.
        :param template_key: template key you want to get.
        :param twin_hardware_id: twin hardware id you want to get.
        :return: object completed with all properties on server (None if not found or raise Error if with id)
        """
        if script_name is not None:
            response = requests.request("GET",
                                        self.__url() + "scripts/" + str(script_name) + "/",
                                        headers=self.__header()
                                        )
            if response.status_code == 200:
                script_bytes = response.content
                return dill.loads(script_bytes)
            else:
                raise self.__raise_error(response)
        elif experiment_key is not None:
            response = requests.request("GET",
                                        self.__url() + "experiments/",
                                        params={
                                            'key': experiment_key
                                        },
                                        headers=self.__header()
                                        )
            if response.status_code == 200:
                for obj_json in response.json():
                    obj = Experiment()
                    obj.from_json(obj_json)
                    return obj
                return None
            else:
                raise self.__raise_error(response)

        elif model_key is not None:
            response = requests.request("GET",
                                        self.__url() + "mlmodels/",
                                        params={
                                            'key': model_key
                                        },
                                        headers=self.__header()
                                        )
            if response.status_code == 200:
                for obj_json in response.json():
                    obj = MLModel()
                    obj.from_json(obj_json)
                    return obj
                return None
            else:
                raise self.__raise_error(response)

        elif template_key is not None:
            response = requests.request("GET",
                                        self.__url() + "templates/",
                                        params={
                                            'key': template_key
                                        },
                                        headers=self.__header()
                                        )
            if response.status_code == 200:
                for obj_json in response.json():
                    obj = Template()
                    obj.from_json(obj_json)
                    return obj
                return None
            else:
                raise self.__raise_error(response)

        elif twin_hardware_id is not None:
            response = requests.request("GET",
                                        self.__url() + "twins/",
                                        params={
                                            'key': twin_hardware_id
                                        },
                                        headers=self.__header()
                                        )
            if response.status_code == 200:
                for obj_json in response.json():
                    obj = Twin()
                    obj.from_json(obj_json)
                    return obj
                return None
            else:
                raise self.__raise_error(response)

        elif obj is not None:
            if isinstance(obj, Execution):
                response = requests.request("GET",
                                            self.__url() + "execute/" + str(obj.execution_id) + "/",
                                            headers=self.__header()
                                            )
                if response.status_code == 200:
                    obj.from_json(response.json())
                    return obj
                else:
                    raise self.__raise_error(response)
            if isinstance(obj, MLModel):
                response = requests.request("GET",
                                            self.__url() + "mlmodels/" + str(obj.model_id) + "/",
                                            headers=self.__header()
                                            )
                if response.status_code == 200:
                    mlmodel_bytes = response.content
                    return pickle.loads(mlmodel_bytes)
                else:
                    raise self.__raise_error(response)
            elif isinstance(obj, Script):
                response = requests.request("GET",
                                            self.__url() + "scripts/" + str(obj.name) + "/",
                                            headers=self.__header()
                                            )
                if response.status_code == 200:
                    script_bytes = response.content
                    return dill.loads(script_bytes)
                else:
                    raise self.__raise_error(response)
            elif isinstance(obj, Plot):
                response = requests.request("GET",
                                            self.__url() + "plots/" + str(obj.plot_id) + "/",
                                            headers=self.__header()
                                            )
                if response.status_code == 200:
                    obj.from_json(response.json())
                    return obj
                else:
                    raise self.__raise_error(response)
            elif isinstance(obj, DSDataFrame):
                response = requests.request("GET",
                                            self.__url() + "dataframes/" + str(obj.df_id) + "/",
                                            headers=self.__header()
                                            )
                if response.status_code == 200:
                    df_bytes = response.content
                    return pickle.loads(df_bytes)
                else:
                    raise self.__raise_error(response)
            elif isinstance(obj, Request):
                response = requests.request("POST", self.__url() + "execute/data",
                                            headers=self.__header(),
                                            data=json.dumps(obj.prepare(), cls=DSAPIEncoder))
                if response.status_code == 200:
                    return pickle.loads(response.content)
                else:
                    raise self.__raise_error(response)
            elif isinstance(obj, Experiment):
                response = requests.request("GET",
                                            self.__url() + "experiments/" + str(obj.experiment_id) + "/",
                                            headers=self.__header()
                                            )
                if response.status_code == 200:
                    obj.from_json(response.json())
                    return obj
                else:
                    raise self.__raise_error(response)
            elif isinstance(obj, Template):
                response = requests.request("GET",
                                            self.__url() + "templates/" + str(obj.template_id) + "/",
                                            headers=self.__header()
                                            )
                if response.status_code == 200:
                    obj.from_json(response.json())
                    return obj
                else:
                    raise self.__raise_error(response)
            else:
                raise TypeError("Type not supported.")

    def create(self, obj):
        """
        create and save an object on the server

        :param obj: object to save on the server (any id is ignored and replaced)
        :return: id of created object
        """
        if callable(obj) and isinstance(obj, types.FunctionType):
            obj = Script(
                function=obj
            )
        if isinstance(obj, Script):
            response = requests.post(self.__url() + "scripts/",
                                     headers=self.__header(),
                                     data=dill.dumps(obj))
            if response.status_code == 200:
                obj.script_id = uuid.UUID(response.json()["id"])
                return obj.script_id
            else:
                raise self.__raise_error(response)
        elif isinstance(obj, Experiment):
            response = requests.post(self.__url() + "experiments/",
                                     headers=self.__header(),
                                     data=json.dumps(obj.to_json()))
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        elif isinstance(obj, Template):
            response = requests.post(self.__url() + "templates/",
                                     headers=self.__header(),
                                     data=json.dumps(obj.to_json()))
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        else:
            raise TypeError("Type not supported.")

    def update(self, obj):
        """
        update and save an object on the server

        :param obj: object to update on the server
        :return: None
        """
        if callable(obj) and isinstance(obj, types.FunctionType):
            obj = Script(
                function=obj
            )
        if isinstance(obj, Script):
            response = requests.put(self.__url() + "scripts/" + str(obj.script_id) + "/",
                                    headers=self.__header(),
                                    data=dill.dumps(obj))
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        elif isinstance(obj, Experiment):
            response = requests.put(self.__url() + "experiments/" + str(obj.experiment_id) + "/",
                                    headers=self.__header(),
                                    data=json.dumps(obj.to_json()))
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        elif isinstance(obj, Template):
            response = requests.put(self.__url() + "templates/" + str(obj.template_id) + "/",
                                     headers=self.__header(),
                                     data=json.dumps(obj.to_json()))
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        else:
            raise TypeError("Type not supported.")

    def upsert(self, obj):
        """
        upsert on object on the server
        work with Script, MLModel or directly a function name

        :param obj: object to upsert on the server
        :return: ID of the object created or updated
        """
        if callable(obj) and isinstance(obj, types.FunctionType):
            obj = Script(
                function=obj
            )
        if isinstance(obj, Script):
            response = requests.put(self.__url() + "scripts/",
                                    headers=self.__header(),
                                    data=dill.dumps(obj))
            if response.status_code == 200:
                obj.script_id = uuid.UUID(response.json()['id'])
                return obj.script_id
            else:
                raise self.__raise_error(response)
        if isinstance(obj, MLModel):
            response = requests.put(self.__url() + "mlmodels/",
                                    headers=self.__header(),
                                    data=pickle.dumps(obj))
            if response.status_code == 200:
                obj.model_id = uuid.UUID(response.json()['id'])
                return obj.model_id
            else:
                raise self.__raise_error(response)
        if isinstance(obj, Template):
            return self.upsert_template(obj.key, obj.name)
        else:
            raise TypeError("Type not supported.")

    def delete(self, obj):
        """
        delete an object on the server

        :param obj: object to delete including all content
        :return: None
        """
        if isinstance(obj, Experiment):
            response = requests.delete(self.__url() + "experiments" + "/" + str(obj.experiment_id) + "/",
                                       headers=self.__header())
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        if isinstance(obj, Script):
            response = requests.delete(self.__url() + "scripts" + "/" + str(obj.script_id) + "/",
                                       headers=self.__header())
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        elif isinstance(obj, Plot):
            response = requests.delete(self.__url() + "plots" + "/" + str(obj.plot_id) + "/",
                                       headers=self.__header())
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        elif isinstance(obj, MLModel):
            response = requests.delete(self.__url() + "mlmodels" + "/" + str(obj.model_id) + "/",
                                       headers=self.__header())
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        elif isinstance(obj, DSDataFrame):
            response = requests.delete(self.__url() + "dataframes" + "/" + str(obj.df_id) + "/",
                                       headers=self.__header())
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        elif isinstance(obj, Template):
            response = requests.delete(self.__url() + "templates" + "/" + str(obj.template_id) + "/",
                                       headers=self.__header())
            if response.status_code == 200:
                return
            else:
                raise self.__raise_error(response)
        else:
            raise TypeError("Type not supported.")

    def query(self,
              datapoints: list[str] = None,
              start: datetime = None,
              end: datetime = None,
              interval: int = None,
              agg_method: str = "mean",
              template: str = None,
              twin: str = None,
              null: str = None,
              filters: dict = None,
              options: dict = None) -> pandas.DataFrame:
        """
        Query a dataframe from API.
        :param agg_method:
        :param datapoints: list of datapoints to fetch.
        :param start: start datetime of range to fetch
        :param end: end datetime of range to fetch
        :param interval: interval in milliseconds.
        :param template: template to fetch.
        :param twin: hardware ID of twin to fetch based on template.
        :param null: By default at 'drop' and dropping NaN values. If not intended behavior please set it to 'ignore' or 'all'.
        :param filters: dict of filters.
        :param options: dict of options.
        :return: dataframe
        """
        request = Request()

        if datapoints is not None:
            request.add_datapoints(datapoints)

        if start is not None:
            request.start = start
        else:
            raise ValueError('start datetime is required.')

        if end is not None:
            request.end = end
        else:
            raise ValueError('end datetime is required.')

        if null is not None:
            request.null = null

        if interval is None:
            raise ValueError('interval is required.')
        request.set_aggregation(agg_method, interval)

        if template is not None and twin is not None:
            request.select_template(
                template_key=template,
                twin_hardware_id=twin
            )

        if filters is not None:
            request.filters = filters

        if options is not None:
            request.options = options

        return self.get(request)

    def execute(self,
                execution: Execution = None,
                request: Request = None,
                dataframe=None,
                script=None,
                ml_model=None,
                isAnomalyDetection=False,
                function=None,
                experiment=None,
                properties: dict = None
                ) -> Execution:
        """
        execute an experimentation on the server.
        :param execution: Execution to execute on the server with configuration (Request, Script, ML Model, ...)
        :param request: Request to use to generate a dataframe
        :param dataframe: dataframe to be used as input (pandas or DS API type)
        :param script: Script to be executed (accept Script,uuid or script function name)
        :param ml_model: MLModel to be executed (accept MLModel, ml_model(id) or uuid)
        :param isAnomalyDetection: set to true to execute automatic anomaly detection
        :param function: set to name of a built-in function to execute it
        :param experiment: ID or experiment to link the execution too
        :param properties: dictionary of properties.
        :return: Execution updated with expected content (Data, Anomalies, Plots, ML Models, ...)
        """
        # Prepare
        if execution is None:
            execution = Execution()
        if request is not None:
            execution.request = request
        if dataframe is not None:
            if isinstance(dataframe, pandas.DataFrame):
                execution.dataframe = dataframe
            elif isinstance(dataframe, DSDataFrame):
                execution.input_ds_dataframe = dataframe
        if script is not None:
            if isinstance(script, uuid.UUID) or (isinstance(script, str) and is_valid_uuid(script)):
                execution.script = Script(script)
            elif isinstance(script, str):
                execution.script = self.get(script_name=script)
            elif isinstance(script, Script):
                execution.script = script
        if ml_model is not None:
            if isinstance(ml_model, uuid.UUID) or (isinstance(script, str) and is_valid_uuid(ml_model)):
                execution.ml_model = MLModel(ml_model)
            elif isinstance(ml_model, str):
                execution.ml_model = self.get(model_key=ml_model)
            elif isinstance(ml_model, MLModel):
                execution.ml_model = ml_model
        if isAnomalyDetection:
            execution.isAnomalyDetection = True
        if function is not None:
            execution.function = function
        if experiment is not None:
            if isinstance(experiment, uuid.UUID):
                execution.experiment_id = experiment
            elif isinstance(experiment, str):
                execution.experiment_id = self.get(experiment_key=experiment).experiment_id
            elif isinstance(experiment, Experiment):
                execution.experiment_id = experiment.experiment_id
        if properties is not None and isinstance(properties, dict):
            execution.properties = properties

        # Execute
        if isinstance(execution, Execution):
            response = requests.post(self.__url() + "execute/",
                                     headers=self.__header(),
                                     data=json.dumps(execution.to_json(), cls=DSAPIEncoder))

            # Parse
            if response.status_code == 200:
                obj = response.json()
                if "plots" in obj.keys():
                    for plot in obj["plots"]:
                        execution.plots.append(self.get(Plot(plot_id=plot["id"])))
                if "models" in obj.keys():
                    for mlmodel in obj["models"]:
                        execution.models.append(self.get(MLModel(model_id=mlmodel["id"])))
                if "resultDataframe" in obj.keys() and obj["resultDataframe"]["id"] is not None:
                    execution.output_ds_dataframe = self.get(DSDataFrame(df_id=obj["resultDataframe"]["id"]))
                if "anomaliesList" in obj.keys() and isinstance(obj["anomaliesList"], str):
                    execution.anomalies = json.loads(obj["anomaliesList"])
                return execution
            else:
                raise self.__raise_error(response)
        else:
            raise TypeError("No execution have been loaded from parameters.")

    def validate(self,
                 execution: Execution = None,
                 request: Request = None,
                 dataframe=None,
                 script=None,
                 properties: dict = None) -> Script:
        """
        run an execution to validate the script used.
        Do not store anything on the DS API nor return anything.
        In case of error, set the Script as invalid.

        :param execution: Execution to validate - must contain a dataframe or a query and a script
        :param request: Request to use to generate a dataframe
        :param dataframe: dataframe to be used as input (pandas or DS API type)
        :param script: Script to be executed (accept Script, string(id) or uuid)
        :param properties: dictionary of properties.
        :return: validated script properties (do not use update or it will invalidate the script)
        """
        if execution is None:
            execution = Execution()
        if request is not None:
            execution.request = request
        if dataframe is not None:
            if isinstance(dataframe, pandas.DataFrame):
                execution.dataframe = dataframe
            elif isinstance(dataframe, DSDataFrame):
                execution.input_ds_dataframe = dataframe
        if script is not None:
            if isinstance(script, uuid.UUID):
                execution.script = Script(script)
            elif isinstance(script, str):
                execution.script = self.get(script_name=script)
            elif isinstance(script, Script):
                execution.script = script

        if properties is not None and isinstance(properties, dict):
            execution.properties = properties

        if isinstance(execution, Execution):
            if execution.script is None:
                raise ValueError("Execution must contains at least a Script.")
            response = requests.post(self.__url() + "execute/validate",
                                     headers=self.__header(),
                                     data=json.dumps(execution.to_json(), cls=DSAPIEncoder))
            if response.status_code == 200:
                response_script = Script()
                response_script.from_json(response.json())
                return response_script
            else:
                raise self.__raise_error(response)
        else:
            raise TypeError("Type not supported.")

    def test(self,
             execution: Execution = None,
             request: Request = None,
             dataframe=None,
             script=None,
             ml_model=None,
             detect_anomalies=False,
             function=None,
             properties: dict = None
             ) -> Execution:
        """
        test an experimentation on the server.

        DO NOT STORE ANYTHING ON SERVER.

        :param execution: Execution to execute on the server with configuration (Request, Script, ML Model, ...)
        :param request: Request to use to generate a dataframe
        :param dataframe: dataframe to be used as input (pandas or DS API type)
        :param script: Script to be executed (accept Script, string(id) or uuid)
        :param ml_model: MLModel to be executed (accept MLModel, ml_model(id) or uuid)
        :param detect_anomalies: set to true to execute automatic anomaly detection
        :param function: set to name of a built-in function to execute it
        :param properties: dictionary of properties.
        :return: Execution updated with expected content (Data, Anomalies, Plots, ML Models, ...)
        """
        # Prepare
        if execution is None:
            execution = Execution()
        if request is not None:
            execution.request = request
        if dataframe is not None:
            if isinstance(dataframe, pandas.DataFrame):
                execution.dataframe = dataframe
            elif isinstance(dataframe, DSDataFrame):
                execution.input_ds_dataframe = dataframe
        if script is not None:
            if isinstance(script, uuid.UUID) or (isinstance(script, str) and is_valid_uuid(script)):
                execution.script = Script(script)
            elif isinstance(script, str):
                execution.script = self.get(script_name=script)
            elif isinstance(script, Script):
                execution.script = script
        if ml_model is not None:
            if isinstance(ml_model, uuid.UUID) or (isinstance(script, str) and is_valid_uuid(ml_model)):
                execution.ml_model = MLModel(ml_model)
            elif isinstance(ml_model, str):
                execution.ml_model = self.get(model_key=ml_model)
            elif isinstance(ml_model, MLModel):
                execution.ml_model = ml_model
        if detect_anomalies:
            execution.isAnomalyDetection = True
        if function is not None:
            execution.function = function

        if properties is not None and isinstance(properties, dict):
            execution.properties = properties

        # Execute
        if isinstance(execution, Execution):
            if execution.script is None and execution.ml_model is None:
                raise ValueError("Execution must contains at least a Script or a Model")
            response = requests.post(self.__url() + "execute/test",
                                     headers=self.__header(),
                                     data=json.dumps(execution.to_json(), cls=DSAPIEncoder))
            if response.status_code == 200:
                return dill.loads(response.content)
            else:
                raise self.__raise_error(response)
        else:
            raise TypeError("Type not supported.")

    def plot(self, plot_id: str = None, plot: Plot = None, figure=None,):
        """
        Fetch and show plot.
        :param plot: Wizata Plot Object
        :param figure: JSON Figure
        :param plot_id: Plot Id
        :return:
        """
        if plot is not None and plot.figure is not None:
            return plotly.io.from_json(plot.figure)
        elif plot is not None and plot.figure is None:
            plot = self.get(plot)
            if plot.figure is not None:
                return plotly.io.from_json(plot.figure)
            else:
                raise ValueError('No plot has been fetch.')
        elif figure is not None:
            return plotly.io.from_json(plot.figure)
        elif id is not None:
            plot = self.get(Plot(plot_id=plot_id))
            if plot.figure is not None:
                return plotly.io.from_json(plot.figure)
            else:
                raise ValueError('No plot has been fetch.')
        else:
            raise KeyError('No valid arguments.')

    def register_model(self,
                       model_key,
                       train_model,
                       df: pandas.DataFrame,
                       scaler=None,
                       has_anomalies: bool = False,
                       has_target_feat: bool = False,
                       experiment_key = None) -> tuple[MLModel, pandas.DataFrame]:
        """
        Register a Machine Learning model to Wizata.
        Model is tested by the API against a sample dataframe.
        :param model_key: logical string id to identify the model.
        :param train_model: trained model (must be compatible with pickle library)
        :param df: sample dataframe.
        :param scaler: scaler (must be compatible with pickle library)
        :param has_anomalies: True is model generate Anomalies
        :param has_target_feat: True if model need a target feature to be selected
        :param experiment_key: Reference of an experiment to which link the generated ML Model
        :return: registered ML Model , pandas.DataFrame
        """
        if model_key is None and isinstance(model_key, str):
            raise ValueError('Please provide a str Model Key to identify the model.')
        if train_model is None:
            raise ValueError('Trained Machine Learning model should not be null')
        elif df is None:
            raise ValueError('A sample dataframe must be provided')

        # Create a ML Model object
        ml_model = MLModel()
        ml_model.trained_model = train_model
        if scaler is not None:
            ml_model.scaler = scaler
        ml_model.has_anomalies = has_anomalies
        ml_model.has_target_feat = has_target_feat
        ml_model.input_columns = df.columns
        ml_model.key = model_key

        if experiment_key is not None:
            ml_model.experimentId = self.get(experiment_key=experiment_key).experiment_id

        try:
            result_df = predict(df, ml_model)
            if result_df is not None:
                ml_model.status = "valid"
                self.upsert(ml_model)
                return ml_model, result_df
            else:
                raise RuntimeError('no dataframe was generated by your model while testing predict capabilities')
        except Exception as e:
            raise RuntimeError('not able to validated the model : ' + str(e))

    def upsert_template(self, key: str, name: str):
        """
        Upsert a template.
        :param key: unique key identifying the template.
        :param name: display name of the template
        :return: upserted template.
        """

        template = self.get(template_key=key)
        if template is not None:
            found = True
        else:
            template = Template(
                key=key,
                name=name
            )
            found = False

        if not found:
            return self.create(template)
        else:
            return self.update(template)

    def add_template_property(self, template, property_name: str, property_type: str = "datapoint"):

        if property_type not in ['datapoint', 'float', 'integer', 'string']:
            raise ValueError('property type must be datapoint, float, integer or string')

        if isinstance(template, str):
            template = self.get(template_key=template)
        elif not isinstance(template, Template):
            raise TypeError('template must be a key str referring template or a proper wizata_dsapi Template')

        if property_name is None:
            raise ValueError('please provide a valid name for the property')

        property_dict = {
            "type": property_type,
            "name": property_name
        }

        response = requests.post(self.__url() + "templates/" + str(template.template_id) + '/properties/',
                                 headers=self.__header(),
                                 data=json.dumps(property_dict))
        if response.status_code == 200:
            return
        else:
            raise self.__raise_error(response)

    def remove_template_property(self, template, property_name: str):

        if isinstance(template, str):
            template = self.get(template_key=template)
        elif not isinstance(template, Template):
            raise TypeError('template must be a key str referring template or a proper wizata_dsapi Template')

        if property_name is None:
            raise ValueError('please provide a valid name for the property')

        property_dict = {
            "name": property_name
        }

        response = requests.delete(self.__url() + "templates/" + str(template.template_id) + '/properties/',
                                   headers=self.__header(),
                                   data=json.dumps(property_dict))
        if response.status_code == 200:
            return
        else:
            raise self.__raise_error(response)

    def register_twin(self, template, twin, properties: dict, override=True):
        """
        register a twin on a specific template using a map.
        :param template: template object, UUID or str key.
        :param twin: twin object, UUID or str key.
        :param properties: dict where key = template property and value = datapoint name or const value (str, int or float).
        :param override: by default at True - allow overriding any existing subscription
        """

        if template is None:
            raise ValueError('template must be specified.')
        elif isinstance(template, uuid.UUID):
            template = self.get(wizata_dsapi.Template(template_id=template))
        elif isinstance(template, str):
            template = self.get(template_key=template)
        elif not isinstance(template, Template):
            raise TypeError('template must be UUID, a key str referring template or a proper wizata_dsapi Template')

        if twin is None:
            raise ValueError('twin must be specified.')
        elif isinstance(twin, uuid.UUID):
            twin_id = twin
        elif isinstance(twin, str):
            twin_id = self.get(twin_hardware_id=twin).twin_id
        elif isinstance(twin, Twin):
            twin_id = twin.twin_id
        else:
            raise TypeError('twin must be UUID, a key str referring hardware ID or a proper wizata_dsapi Twin')

        if template.properties is None or len(template.properties) == 0:
            raise ValueError('template chosen does not contains any properties')

        if properties is None or len(properties.keys()) == 0:
            raise ValueError('your map dictionary must contains properties matching template')

        twin_properties = {
            "properties": []
        }
        for key in properties.keys():
            property_type = None
            for template_property in template.properties:
                if key == template_property['name']:
                    property_type = template_property['type']
            if property_type is None:
                raise ValueError(f'cannot find property {key} in template or cannot determine its type')
            twin_properties["properties"].append({
                'name': key,
                property_type: properties[key]
            })

        # Check if already exist
        exists = False
        response_exists = requests.get(self.__url() + "templates/" + str(template.template_id)
                                       + '/registrations/' + str(twin_id) + '/',
                                       headers=self.__header())
        if response_exists.status_code == 200:
            exists = True

        if exists and not override:
            raise ValueError("registration already exists and override not allowed.")

        if exists and override:
            response = requests.put(self.__url() + "templates/" + str(template.template_id)
                                    + '/registrations/' + str(twin_id) + '/',
                                    headers=self.__header(),
                                    data=json.dumps(twin_properties))
        else:
            response = requests.post(self.__url() + "templates/" + str(template.template_id)
                                     + '/registrations/' + str(twin_id) + '/',
                                     headers=self.__header(),
                                     data=json.dumps(twin_properties))

        if response.status_code == 200:
            return
        else:
            raise self.__raise_error(response)

    def unregister_twin(self, template, twin):
        """
        un-register a twin from a specific template.
        :param template: template object, UUID or str key.
        :param twin: twin object, UUID or str key.
        """

        if template is None:
            raise ValueError('template must be specified.')
        elif isinstance(template, uuid.UUID):
            template = self.get(wizata_dsapi.Template(template_id=template))
        elif isinstance(template, str):
            template = self.get(template_key=template)
        elif not isinstance(template, Template):
            raise TypeError('template must be UUID, a key str referring template or a proper wizata_dsapi Template')

        if twin is None:
            raise ValueError('twin must be specified.')
        elif isinstance(twin, uuid.UUID):
            twin_id = twin
        elif isinstance(twin, str):
            twin_id = self.get(twin_hardware_id=twin).twin_id
        elif isinstance(twin, Twin):
            twin_id = twin.twin_id
        else:
            raise TypeError('twin must be UUID, a key str referring hardware ID or a proper wizata_dsapi Twin')

        response = requests.delete(self.__url() + "templates/" + str(template.template_id)
                                   + '/registrations/' + str(twin_id) + '/',
                                   headers=self.__header())
        if response.status_code == 200:
            return
        else:
            raise self.__raise_error(response)


def api() -> WizataDSAPIClient:
    """
    Create a WizataDSAPIClient from environment variables.
    :return: client
    """
    protocol = 'https'

    if os.environ.get('WIZATA_PROTOCOL') is not None:
        protocol = os.environ.get('WIZATA_PROTOCOL')

    return WizataDSAPIClient(
        tenant_id=os.environ.get('WIZATA_TENANT_ID'),
        client_id=os.environ.get('WIZATA_CLIENT_ID'),
        scope=os.environ.get('WIZATA_SCOPE'),
        username=os.environ.get('WIZATA_USERNAME'),
        password=os.environ.get('WIZATA_PASSWORD'),
        domain=os.environ.get('WIZATA_DOMAIN'),
        protocol=protocol
    )


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False
