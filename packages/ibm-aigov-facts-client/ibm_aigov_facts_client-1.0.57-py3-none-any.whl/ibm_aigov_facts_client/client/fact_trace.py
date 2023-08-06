# coding: utf-8

# Copyright 2020,2021 IBM All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mlflow

from typing import Optional

from ibm_aigov_facts_client.base_classes.auth import FactsAuthClient
from ibm_cloud_sdk_core.authenticators import BearerTokenAuthenticator, CloudPakForDataAuthenticator, IAMAuthenticator, NoAuthAuthenticator
from ibm_cloud_sdk_core.utils import  convert_model

from ibm_aigov_facts_client.export.export_facts import *
from ibm_aigov_facts_client.export.export_facts_manual import *
from ibm_aigov_facts_client.utils.enums import ContainerType
from ibm_aigov_facts_client.utils.experiments.experiments_utils import Experiments
from ibm_aigov_facts_client.utils.runs.runs_utils import Runs
from ibm_aigov_facts_client.utils.support_scope_meta import FrameworkSupportOptions
from ibm_aigov_facts_client.factsheet.factsheet_utility import FactSheetElements
from ibm_aigov_facts_client.factsheet.external_modelfacts_utility import ExternalModelFactsElements
from ibm_aigov_facts_client.utils.me_containers_meta import AssetsContainersDefinitions
from ibm_aigov_facts_client.factsheet.assets import Assets
from .autolog import AutoLog
from .manual_log import ManualLog


from ibm_aigov_facts_client.utils.utils import validate_enum, validate_external_connection_props, version, validate_type, get_instance_guid,_is_active
from ibm_aigov_facts_client.utils.client_errors import *
from ibm_aigov_facts_client.utils.logging_utils import *
from ibm_aigov_facts_client.store.autolog.autolog_utils import *
from ibm_aigov_facts_client.utils.constants import SPARK_JAR_PKG
from ibm_aigov_facts_client.utils.config import *
from ibm_aigov_facts_client.utils.cp4d_utils import CloudPakforDataConfig
from ibm_aigov_facts_client.supporting_classes.cp4d_authenticator import CP4DAuthenticator



class FactsClientAdapter(FactsAuthClient):

    """
    AI GOVERNANCE FACTS CLIENT

    :var version: Returns version of the python library.
    :vartype version: str

    :param str experiment_name: Name of the Experiment.
    :param str container_type: (Optional) Name of the container where model would be saved. Currently supported options are `SPACE` or `PROJECT`.  It is (Required) when using Watson Machine Learning.
    :param str container_id: (Optional) container id specific to container type.It is (Required) when using Watson Machine Learning.
    :param bool set_as_current_experiment: (Optional) if `True` new experiment will not be created if experiment already exists with same experiment name.By default set to False.
    :param bool enable_autolog: (Optional) if False, manual log option will be available. By default set to True.
    :param bool external_model: (Optional) if True, external models tracing would be enabled. By default set to False. 
    :param CloudPakforDataConfig cloud_pak_for_data_configs: (Optional) Cloud pak for data cluster details.
    :param bool disable_tracing: (Optional) if True, tracing and logging utilities will be disabled. Default to False.


    A way you might use me is:

    For IBM Cloud:

    >>> from ibm_aigov_facts_client import AIGovFactsClient
    >>> client = AIGovFactsClient(api_key=<API_KEY>, experiment_name="test",container_type="space or project",container_id=<space_id or project_id>)


    If using existing experiment as current:

    >>> client = AIGovFactsClient(api_key=<API_KEY>, experiment_name="test",container_type="space",container_id=<space_id>,set_as_current_experiment=True)


    If using external models with manual log:

    >>> client= AIGovFactsClient(api_key=API_KEY,experiment_name="external",enable_autolog=False,external_model=True)

    If using external models with Autolog:

    >>> client= AIGovFactsClient(api_key=API_KEY,experiment_name="external",external_model=True)


    For Cloud Pak for Data:

    >>> from ibm_aigov_facts_client import AIGovFactsClient,CloudPakforDataConfig
    >>> cpd_creds=CloudPakforDataConfig(service_url="<hosturl>",username="<username>",password="<password>")
    >>> client = AIGovFactsClient(experiment_name="<name of experiment>",container_type="<space or project>",container_id="<space_id or project_id>",cloud_pak_for_data_configs=cpd_creds)

    OR use API_KEY
    
    >>> from ibm_aigov_facts_client import AIGovFactsClient,CloudPakforDataConfig
    >>> cpd_creds=CloudPakforDataConfig(service_url="<hosturl>",username="<username>",api_key="<api_key>")
    >>> client = AIGovFactsClient(experiment_name="<name of experiment>",container_type="<space or project>",container_id="<space_id or project_id>",cloud_pak_for_data_configs=cpd_creds)

    if Cloud Pak for Data platform has IAM enabled:

    >>> from ibm_aigov_facts_client import AIGovFactsClient,CloudPakforDataConfig
    >>> cpd_creds=CloudPakforDataConfig(service_url="<hosturl>",username="<username>",password="<password>",bedrock_url="<cluster bedrock url>")
    >>> client = AIGovFactsClient(experiment_name="<name of experiment>",container_type="<space or project>",container_id="<space_id or project_id>",cloud_pak_for_data_configs=cpd_creds )
    
    if disable tracing as a whole and use other features like custom facts and facts definitions

    >>> client = AIGovFactsClient(container_type=<project or space>,container_id=<space or project id>,cloud_pak_for_data_configs=creds,disable_tracing=True)
    >>> client = AIGovFactsClient(external_model=True,cloud_pak_for_data_configs=creds,disable_tracing=True)

    For Standalone use in localhost without factsheet functionality:

    >>> from ibm_aigov_facts_client import AIGovFactsClient
    >>> client = AIGovFactsClient(experiment_name="test")
    """

    _authenticator = None
    _container_type = None
    _container_id = None
    _autolog = None
    _external = None
    _is_cp4d=None
    _cp4d_version=None
    _trace_obj=None


    def __init__(self,
                 experiment_name: str=None,
                 container_type: Optional[str] = None,
                 container_id: Optional[str] = None,
                 api_key: Optional[str] = None,
                 set_as_current_experiment: Optional[bool] = False,
                 enable_autolog: Optional[bool] = True,
                 external_model: Optional[bool]=False,
                 cloud_pak_for_data_configs:'CloudPakforDataConfig'=None,
                 disable_tracing: Optional[bool]= False
                 ) -> None:
                 
        self.experiment_name = experiment_name
        FactsClientAdapter._container_type = container_type
        FactsClientAdapter._container_id = container_id
        self.set_as_current_exp = set_as_current_experiment
        FactsClientAdapter._is_cp4d = False
        FactsClientAdapter._cp4d_version = None
        FactsClientAdapter._autolog = enable_autolog
        FactsClientAdapter._external= external_model
        self.cp4d_configs=None
        self._api_key=api_key


        if ((self.experiment_name is None or self.experiment_name == "") and not disable_tracing):
            raise MissingValue("experiment_name", "Experiment name is missing")

        if (not api_key and not cloud_pak_for_data_configs) or (api_key and cloud_pak_for_data_configs):
            raise ClientError("Either IBM cloud API_KEY or CP4D configs should be used")
        
        if cloud_pak_for_data_configs:
            FactsClientAdapter._is_cp4d=True
            super().set_disable_ssl_verification(self._is_cp4d)
            self.cp4d_configs=convert_model(cloud_pak_for_data_configs)
            if self.cp4d_configs["url"].endswith("/"):
                self.cp4d_configs["url"]= self.cp4d_configs["url"][0:self.cp4d_configs["url"].index("/",9)]
            
            if self.cp4d_configs.get("api_key") and self.cp4d_configs.get("password"):
                raise AuthorizationError("Either IAM enabled platform api_key or password should be used")

        
        _ENV = get_env()

        if api_key is not None and not FactsClientAdapter._is_cp4d:
            __is_active_api=_is_active(api_key=api_key,env=_ENV)
            
            if _ENV == 'dev' or _ENV == 'test':
                if __is_active_api:
                    FactsClientAdapter._authenticator = IAMAuthenticator(
                        apikey=api_key, url=dev_config['IAM_URL'])
                else:
                    raise AuthorizationError("Test account API_KEY is inactive or invalid, please use an active IBM Cloud API_KEY")

            elif _ENV == 'prod' or _ENV is None:
                if __is_active_api:
                    FactsClientAdapter._authenticator = IAMAuthenticator(
                    apikey=api_key)
                else:
                    raise AuthorizationError("Production account API_KEY is inactive or invalid, please use an active IBM Cloud API_KEY")
            else:
                if __is_active_api:
                    FactsClientAdapter._authenticator = IAMAuthenticator(
                    apikey=api_key)
                else:
                    raise AuthorizationError("API_KEY is inactive or invalid, please use an active IBM Cloud API_KEY")
        
        elif FactsClientAdapter._is_cp4d and self.cp4d_configs.get("password"):
            FactsClientAdapter._authenticator=CloudPakForDataAuthenticator(url=self.cp4d_configs['url'],
                                                                            username=self.cp4d_configs['username'],
                                                                            password=self.cp4d_configs['password'],
                                                                            disable_ssl_verification=self.cp4d_configs['disable_ssl_verification']
                                                                            )
        elif FactsClientAdapter._is_cp4d and self.cp4d_configs.get("api_key"):
            FactsClientAdapter._authenticator=CloudPakForDataAuthenticator(url=self.cp4d_configs['url'],
                                                                            username=self.cp4d_configs['username'],
                                                                            apikey=self.cp4d_configs["api_key"],
                                                                            disable_ssl_verification=self.cp4d_configs['disable_ssl_verification']
                                                                            )

        else:
            FactsClientAdapter._authenticator = NoAuthAuthenticator()


        super().__init__(authenticator=FactsClientAdapter._authenticator)

       
        if FactsClientAdapter._container_type==ContainerType.CATALOG:
            raise ClientError("Only project and space context supported when initiating client")
    
        if type(FactsClientAdapter._authenticator) in [NoAuthAuthenticator]:
            if not disable_tracing:
                if FactsClientAdapter._autolog:
                    AutoLog(experiment_name=self.experiment_name,
                            set_as_current_exp=self.set_as_current_exp)
                else:
                    self.manual_log = ManualLog(experiment_name=self.experiment_name,
                                                set_as_current_exp=self.set_as_current_exp)
            else:
                pass

        elif type(FactsClientAdapter._authenticator) in [CloudPakForDataAuthenticator, IAMAuthenticator, BearerTokenAuthenticator]:
            validate_type(FactsClientAdapter._authenticator, "authenticator", [
                BearerTokenAuthenticator, CloudPakForDataAuthenticator, IAMAuthenticator
            ], True)

            if isinstance(FactsClientAdapter._authenticator, CloudPakForDataAuthenticator):
                url = FactsClientAdapter._authenticator.token_manager.url[0:FactsClientAdapter._authenticator.token_manager.url.index("/",9)]
                username = FactsClientAdapter._authenticator.token_manager.username
                password = FactsClientAdapter._authenticator.token_manager.password
                apikey = FactsClientAdapter._authenticator.token_manager.apikey
                disable_ssl_verification=FactsClientAdapter._authenticator.token_manager.disable_ssl_verification
                FactsClientAdapter._authenticator = CP4DAuthenticator(url=url,
                                            username=username,
                                            password=password,
                                            apikey = apikey,
                                            disable_ssl_verification=disable_ssl_verification,
                                            bedrock_url = self.cp4d_configs.get("bedrock_url", None))

            if not FactsClientAdapter._external:
                # if not FactsClientAdapter._autolog:
                #     raise ClientError("Manual logging is supported for external models, set `external_model=True` when initiating client") 

                if not FactsClientAdapter._container_type  or not FactsClientAdapter._container_id:
                    raise MissingValue("container_type/container_id",
                                    "Provide container type and id or if using external model set `external_model=True`")

                # container id validations
                if FactsClientAdapter._container_type==ContainerType.SPACE:
                    self.space_validation(FactsClientAdapter._container_id)
                if FactsClientAdapter._container_type==ContainerType.PROJECT:
                    self.project_validation(FactsClientAdapter._container_id)

                elif(FactsClientAdapter._container_type is not None):
                    validate_enum(FactsClientAdapter._container_type,
                                "container_type", ContainerType, False)

                self.valid_service_instance = get_instance_guid(
                    FactsClientAdapter._authenticator, _ENV, FactsClientAdapter._container_type,is_cp4d=FactsClientAdapter._is_cp4d)
            else:

                if FactsClientAdapter._container_type or FactsClientAdapter._container_id:
                    raise ClientError("Container type and id is specific to IBM Cloud or CP4D only")

                self.valid_service_instance = get_instance_guid(
                    FactsClientAdapter._authenticator, _ENV,is_cp4d=FactsClientAdapter._is_cp4d)

            if FactsClientAdapter._is_cp4d:
                FactsClientAdapter._cp4d_version = self.get_CP4D_version()

            if not self.valid_service_instance:
                raise ClientError("Valid service instance/s not found")
            else:
                if not disable_tracing:
                    if FactsClientAdapter._autolog:
                        AutoLog(experiment_name=self.experiment_name,
                                set_as_current_exp=self.set_as_current_exp)

                        self.export_facts = ExportFacts(self)

                        if external_model:
                            self.external_model_facts = ExternalModelFactsElements(self)
                    else:
                        if external_model and (FactsClientAdapter._container_type or FactsClientAdapter._container_id):
                            raise ClientError("Container type or id is only applicable for Watson Machine learning models") 
                        
                        self.manual_log = ManualLog(experiment_name=self.experiment_name,
                                                    set_as_current_exp=self.set_as_current_exp)
                        self.export_facts = ExportFactsManual(self)

                        if external_model:
                            self.external_model_facts = ExternalModelFactsElements(self)
                
                    self.experiments = Experiments()
                    self.runs = Runs()
                    self.assets=Assets(self)
                
                else:
                    self.external_model_facts = ExternalModelFactsElements(self)
                    self.assets=Assets(self)
        else:
            raise AuthorizationError("Could not initiate client")

        
        self.version = version()
        self.FrameworkSupportNames = FrameworkSupportOptions()
        #self.AssetsContainersDefinitions=AssetsContainersDefinitions()

    
    def space_validation(self,space_id):
        url=self._get_url_space(space_id)
        response=requests.get(url,headers=self._get_headers())
        if response.status_code!=200:
            raise AuthorizationError("Invalid container id {}. ERROR {}. {}".format(space_id,response.status_code,response.text))
        else:
            pass

    def project_validation(self,project_id):
        url=self._get_url_project(project_id)
        response=requests.get(url,headers=self._get_headers())
        if response.status_code!=200:
            raise AuthorizationError("Invalid container id {}. ERROR {}. {}".format(project_id,response.status_code,response.text))
        else:
            pass

    def _get_url_space(self,space_id:str):
        if FactsClientAdapter._is_cp4d:
            cpd_url=FactsClientAdapter._authenticator.token_manager.url
            url = cpd_url + \
                    '/v2/spaces/' + space_id 
        else:
            if get_env() == 'dev':
                url = dev_config["DEFAULT_DEV_SERVICE_URL"] + \
                    '/v2/spaces/' + space_id 
            elif get_env() == 'test':
                url = test_config["DEFAULT_TEST_SERVICE_URL"] + \
                    '/v2/spaces/' + space_id 
            else:
                url = prod_config["DEFAULT_SERVICE_URL"] + \
                    '/v2/spaces/' + space_id 
        return url

    def _get_url_project(self,project_id:str):
    
        if FactsClientAdapter._is_cp4d:
            cpd_url=FactsClientAdapter._authenticator.token_manager.url
            url = cpd_url + \
                '/v2/projects/' + project_id 
        else:
            if get_env() == 'dev':
                url = dev_config["DEFAULT_DEV_SERVICE_URL"] + \
                    '/v2/projects/' + project_id 
            elif get_env() == 'test':
                url = test_config["DEFAULT_TEST_SERVICE_URL"] + \
                    '/v2/projects/' + project_id 
            else:
                url = prod_config["DEFAULT_SERVICE_URL"] + \
                    '/v2/projects/' + project_id 
        return url

    def get_CP4D_version(self):

        url=self._get_url_heartbeat()
        response=requests.get(url,headers=self._get_headers())
        if response.status_code==200:
            version_str = (response.json()["version"]).replace(".","")

            if len(version_str) == 4:
                version_str=version_str[0:2]+'00'+version_str[2:]
            elif len(version_str) == 5:
                version_str=version_str[0:2]+'0'+version_str[2:]

            version_val = int(version_str)

            if version_val > 450000 and version_val < 451000:
                CP4D_version = "4.5.0"
            elif version_val > 451000 and version_val < 452000:
                CP4D_version = "4.5.1"
            elif version_val > 452000 and version_val < 453000:
                CP4D_version = "4.5.2"
            elif version_val > 453000 and version_val < 454000:
                CP4D_version = "4.5.3"
            elif version_val > 454000 and version_val < 455000:
                CP4D_version = "4.5.4"
            elif version_val > 455000 and version_val < 456000:
                CP4D_version = "4.5.5"
            elif version_val > 460000 and version_val < 461000:
                CP4D_version = "4.6.0"
            elif version_val > 461000 and version_val < 462000:
                CP4D_version = "4.6.1"
            elif version_val > 462000 and version_val < 463000:
                CP4D_version = "4.6.2"
            elif version_val > 463000 and version_val < 464000:
                CP4D_version = "4.6.3"
            elif version_val > 464000 and version_val < 465000:
                CP4D_version = "4.6.4"
            elif version_val > 465000 and version_val < 466000:
                CP4D_version = "4.6.5"
            elif version_val > 470000 and version_val < 471000:
                CP4D_version = "4.7.0"
            elif version_val > 471000 and version_val < 472000:
                CP4D_version = "4.7.1"
            elif version_val > 472000 and version_val < 473000:
                CP4D_version = "4.7.2"
            else:
                CP4D_version = "0.0.0"

            return CP4D_version

    def _get_url_heartbeat(self):
        if FactsClientAdapter._is_cp4d:
            cpd_url=FactsClientAdapter._authenticator.token_manager.url
            url = cpd_url + '/v1/aigov/factsheet/heartbeat'
        return url
        
    def _get_headers(self):
        token =  FactsClientAdapter._authenticator.token_manager.get_token() if  ( isinstance(FactsClientAdapter._authenticator, IAMAuthenticator) or (isinstance(FactsClientAdapter._authenticator, CloudPakForDataAuthenticator))) else FactsClientAdapter._authenticator.bearer_token
        iam_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer %s" % token
        }
        return iam_headers 



