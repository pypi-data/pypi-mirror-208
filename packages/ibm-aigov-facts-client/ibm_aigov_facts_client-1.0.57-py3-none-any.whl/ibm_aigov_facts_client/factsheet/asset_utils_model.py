import logging
import os
import json
import collections
import itertools
import uuid
import ibm_aigov_facts_client._wrappers.requests as requests

from typing import Optional
from datetime import datetime

from typing import BinaryIO, Dict, List, TextIO, Union,Any
from ibm_aigov_facts_client.factsheet import assets 
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator,CloudPakForDataAuthenticator
from ibm_aigov_facts_client.utils.enums import AssetContainerSpaceMap, AssetContainerSpaceMapExternal,ContainerType, FactsType, ModelEntryContainerType, AllowedDefinitionType,FormatType, RenderingHints
from ibm_aigov_facts_client.utils.utils import validate_enum,validate_type,STR_TYPE
from ibm_aigov_facts_client.factsheet.asset_utils_me import ModelEntryUtilities
from ibm_aigov_facts_client.factsheet.asset_utils_experiments import NotebookExperimentUtilities
from ibm_cloud_sdk_core.utils import  convert_model
from ibm_aigov_facts_client.utils.metrics_utils import convert_metric_value_to_float_if_possible
from ibm_aigov_facts_client.utils.cell_facts import CellFactsMagic


from ibm_aigov_facts_client.utils.config import *
from ibm_aigov_facts_client.utils.client_errors import *
from ibm_aigov_facts_client.utils.constants import *


_logger = logging.getLogger(__name__) 


class ModelAssetUtilities:

    """
        Model asset utilities. Running `client.assets.model()` makes all methods in ModelAssetUtilities object available to use.
    
    """

    def __init__(self,assets_client:'assets.Assets',model_id:str=None, container_type: str=None, container_id: str=None,facts_type: str=None) -> None:

        self._asset_id = model_id
        self._container_type=container_type
        self._container_id=container_id
        self._facts_type=facts_type

        self._assets_client=assets_client
        self._facts_client=self._assets_client._facts_client
        self._is_cp4d=self._assets_client._is_cp4d
        self._external_model=self._assets_client._external_model
        
        if self._is_cp4d:
            self._cpd_configs=self._assets_client._cpd_configs
            self._cp4d_version=self._assets_client._cp4d_version

        self._facts_definitions=self._get_fact_definitions()
        self._facts_definitions_op= self._get_fact_definitions(type_name=FactsType.MODEL_FACTS_USER_OP)

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'ModelAssetUtilities':
        """Initialize a ModelAssetUtilities object from a json dictionary."""
        args = {}
        if '_asset_id' in _dict:
            args['asset_id'] = _dict.get('_asset_id')
       
        if '_container_type' in _dict:
            args['container_type'] = _dict.get('_container_type') #[convert_model(x) for x in metrics]
        else:
            raise ValueError('Required property \'container_type\' not present in AssetProps JSON')
        
        if '_container_id' in _dict:
            args['container_id'] = _dict.get('_container_id') #[convert_model(x) for x in metrics]
        else:
            raise ValueError('Required property \'container_id\' not present in AssetProps JSON')
        
        if '_facts_type' in _dict:
            args['facts_type'] = _dict.get('_facts_type') #[convert_model(x) for x in metrics]
        else:
            raise ValueError('Required property \'facts_type\' not present in AssetProps JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, '_asset_id') and self._asset_id is not None:
            _dict['asset_id'] = self._asset_id
        if hasattr(self, '_container_type') and self._container_type is not None:
            _dict['container_type'] = self._container_type
        if hasattr(self, '_container_id') and self._container_id is not None:
            _dict['container_id'] = self._container_id
        if hasattr(self, '_facts_type') and self._facts_type is not None:
            _dict['facts_type'] = self._facts_type
        
        return _dict
  

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def get_info(self,verbose=False)-> Dict:
        """Get model object details

            :param verbose: If True, returns additional model details. Defaults to False
            :type verbose: bool, optional
            :rtype: dict

            The way to use me is:

            >>> get_model.get_info()
            >>> get_model.get_info(verbose=True)

        """
        if verbose:
            url=self._get_assets_url(self._asset_id,self._container_type,self._container_id)
            response = requests.get(url, headers=self._get_headers())
            if response.status_code==200:
                cur_metadata=self._to_dict()
                additional_data={}

                model_name=response.json()["metadata"].get("name")
                asset_type=response.json()["metadata"].get("asset_type")
                desc=response.json()["metadata"].get("description")
                if self._is_cp4d:
                    if self._container_type==ContainerType.CATALOG:
                        url=CATALOG_PATH.format(self._cpd_configs["url"],self._container_id,self._asset_id)
                    elif self._container_type==ContainerType.PROJECT:
                        url=PROJECT_PATH.format(self._cpd_configs["url"],self._asset_id,self._container_id)
                    elif self._container_type==ContainerType.SPACE:
                        url=SPACE_PATH.format(self._cpd_configs["url"],self._asset_id,self._container_id)
                else:
                    if self._container_type==ContainerType.CATALOG:
                        url=CATALOG_PATH.format(CLOUD_URL,self._container_id,self._asset_id)
                    elif self._container_type==ContainerType.PROJECT:
                        url=PROJECT_PATH.format(CLOUD_URL,self._asset_id,self._container_id)
                    elif self._container_type==ContainerType.SPACE:
                        url=SPACE_PATH.format(CLOUD_URL,self._asset_id,self._container_id)

                additional_data["name"]=model_name
                if desc:
                    additional_data["description"]=desc
                additional_data["asset_type"]=asset_type
                additional_data["url"]=url
                additional_data.update(cur_metadata)
                return additional_data
            else:
                raise ClientError("Failed to get additional asset information. ERROR {}. {}".format(response.status_code,response.text))
        else:
            return self._to_dict()


    def _get_fact_definitions(self,type_name=None)->Dict:

        """
            Get all facts definitions

            :rtype: dict

        """

        facts_type=type_name or self._facts_type

        if self._is_cp4d:
            url = self._cpd_configs["url"] + \
                    "/v2/asset_types/" + facts_type + "?" + self._container_type + "_id=" + self._container_id
        else:
            if get_env() == 'dev':
                url = dev_config["DEFAULT_DEV_SERVICE_URL"] + \
                    "/v2/asset_types/" + facts_type + "?" + self._container_type + "_id=" + self._container_id
            elif get_env() == 'test':
                url = test_config["DEFAULT_TEST_SERVICE_URL"] + \
                    "/v2/asset_types/" + facts_type + "?" + self._container_type + "_id=" + self._container_id
            else:
                url = prod_config["DEFAULT_SERVICE_URL"] + \
                    "/v2/asset_types/" + facts_type + "?" + self._container_type + "_id=" + self._container_id

        response = requests.get(url, headers=self._get_headers())
        if not response.ok:
            return None
        else:
            return response.json()

    def _get_tracking_model_usecase_info(self):

        """
            Get model use case info associated to the model.

        """

        url=self._get_assets_url(self._asset_id,self._container_type,self._container_id)
        response = requests.get(url, headers=self._get_headers())

        #get model use case
        
        if response.status_code==200:
            all_resources=response.json().get("entity")
            get_facts=all_resources.get(FactsType.MODEL_FACTS_SYSTEM)
            modelentry_information = get_facts.get(MODEL_USECASE_TAG)
            if not modelentry_information:
                raise ClientError ("Model use case info is not available for asset id {}".format(self._asset_id))
            else:
                lmid = modelentry_information.get('lmid')
                if not lmid:
                    raise ClientError ("Model {} is not tracked by a model use case".format(self._asset_id))
                lmdidParts = lmid.split(':')
                if len(lmdidParts) < 2:
                    return None
                container_id = lmdidParts[0]
                model_usecase_id = lmdidParts[1]
            
            self._current_model_usecase= ModelEntryUtilities(self,model_usecase_id=model_usecase_id,container_type=MODEL_USECASE_CONTAINER_TYPE_TAG,container_id=container_id,facts_type=FactsType.MODEL_USECASE_USER)
        
            return self._current_model_usecase.to_dict()

        else:
            raise ClientError("Asset model use case information is not available for model id {}. ERROR. {}. {}".format(self._asset_id,response.status_code,response.text))

 

    def get_tracking_model_usecase(self)-> ModelEntryUtilities:

        """
            Get model use case associated to the model.
            
            :rtype: ModelEntryUtilities

            A way you might use me is:

            >>> model.get_tracking_model_usecase()

        """

        url=self._get_assets_url(self._asset_id,self._container_type,self._container_id)
        response = requests.get(url, headers=self._get_headers())

        #get model use case
        
        if response.status_code==200:
            all_resources=response.json().get("entity")
            get_facts=all_resources.get(FactsType.MODEL_FACTS_SYSTEM)
            modelentry_information = get_facts.get(MODEL_USECASE_TAG)
            if not modelentry_information:
                raise ClientError ("Model {} is not tracked by a model use case".format(self._asset_id))
            else:
                lmid = modelentry_information.get('lmid')
                if not lmid:
                    raise ClientError ("Model {} is not tracked by a model use case. lmid is missing".format(self._asset_id))
                lmdidParts = lmid.split(':')
                if len(lmdidParts) < 2:
                    return None
                container_id = lmdidParts[0]
                model_usecase_id = lmdidParts[1]
            
            self._current_model_usecase= ModelEntryUtilities(self,model_usecase_id=model_usecase_id,container_type=MODEL_USECASE_CONTAINER_TYPE_TAG,container_id=container_id,facts_type=FactsType.MODEL_USECASE_USER)
        
            return self._current_model_usecase

        else:
            raise ClientError("Asset model use case information is not available for model id {}. ERROR. {}. {}".format(self._asset_id,response.status_code,response.text))


    def add_tracking_model_usecase(self,model_usecase_name:str=None,model_usecase_desc:str=None,model_usecase_id:str=None,model_usecase_catalog_id:str=None,grc_model_id:str=None):
        
        """
            Link Model to model use case. Model asset should be stored in either Project or Space and corrsponding ID should be provided when registering to model use case. 

            
            :param str model_usecase_name: (Optional) New model use case name. Used only when creating new model use case. 
            :param str model_usecase_desc: (Optional) New model use case description. Used only when creating new model use case.
            :param str model_usecase_id: (Optional) Existing model use case to link with.
            :param str model_usecase_catalog_id: (Optional) Catalog ID where model use case exist.
            :param str grc_model_id: (Optional) Openpages model id. Only applicable for CPD environments.  


            For new model use case:

            >>> model.add_tracking_model_usecase(model_usecase_name=<name>,model_usecase_desc=<description>)
        
            For linking to existing model use case:

            >>> model.add_tracking_model_usecase(model_usecase_id=<model use case id to link with>,model_usecase_catalog_id=<model use case catalog id>)


        """

        model_asset_id=self._asset_id
        container_type=self._container_type
        container_id=self._container_id
    
        
        params={}
        payload={}
        
        params[container_type +'_id']=container_id


        if grc_model_id and not self._is_cp4d:
            raise WrongParams ("grc_model_id is only applicable for Openpages enabled CPD platform")

        
        payload['model_entry_catalog_id']=model_usecase_catalog_id or self._assets_client._get_pac_catalog_id()
        
        if model_usecase_name or (model_usecase_name and model_usecase_desc):
            if model_usecase_id:
                raise WrongParams("Please provide either NAME and DESCRIPTION or MODEL_USECASE_ID")
            payload['model_entry_name']=model_usecase_name
            if model_usecase_desc:
                payload['model_entry_description']=model_usecase_desc        
            
        elif model_usecase_id:
            if model_usecase_name and model_usecase_desc:
                raise WrongParams("Please provide either NAME and DESCRIPTION or MODEL_USECASE_ID")
            payload['model_entry_asset_id']=model_usecase_id 
            
        else:
            raise WrongParams("Please provide either NAME and DESCRIPTION or MODEL_USECASE_ID")

        wkc_register_url=WKC_MODEL_REGISTER.format(model_asset_id)

        if self._is_cp4d:
            if grc_model_id:
                payload['grc_model_id']=grc_model_id
            url = self._cpd_configs["url"] + \
                 wkc_register_url
        else:
            if get_env() == 'dev':
                url = dev_config["DEFAULT_DEV_SERVICE_URL"] + \
                wkc_register_url
            elif get_env() == 'test':
                url = test_config["DEFAULT_TEST_SERVICE_URL"] + \
                    wkc_register_url
            else:
                url = prod_config["DEFAULT_SERVICE_URL"] + \
                    wkc_register_url
        
        if model_usecase_id:
            _logger.info("Initiate linking model to existing model use case {}".format(model_usecase_id))
        else:
            _logger.info("Initiate linking model to new model use case......")
        
        response = requests.post(url,
                                headers=self._get_headers(),
                                params=params,
                                data=json.dumps(payload))

        
        if response.status_code == 200:
            _logger.info("Successfully finished linking Model {} to model use case".format(model_asset_id))
        else:
            error_msg = u'Model registration failed'
            reason = response.text
            _logger.info(error_msg)
            raise ClientError(error_msg + '. Error: ' + str(response.status_code) + '. ' + reason)

        return response.json()

    def remove_tracking_model_usecase(self):
        """
            Unregister from model use case

            Example for IBM Cloud or CPD:

            >>> model.remove_tracking_model_usecase()

        """

        wkc_unregister_url=WKC_MODEL_REGISTER.format(self._asset_id)

        params={}
        params[self._container_type +'_id']=self._container_id

        if self._is_cp4d:
            url = self._cpd_configs["url"] + \
                 wkc_unregister_url
        else:
            if get_env() == 'dev':
                url = dev_config["DEFAULT_DEV_SERVICE_URL"] + \
                wkc_unregister_url
            elif get_env() == 'test':
                url = test_config["DEFAULT_TEST_SERVICE_URL"] + \
                    wkc_unregister_url
            else:
                url = prod_config["DEFAULT_SERVICE_URL"] + \
                    wkc_unregister_url
        
        response = requests.delete(url,
                                headers=self._get_headers(),
                                params=params,
                                )

        if response.status_code == 204:
            _logger.info("Successfully finished unregistering WKC Model {} from model use case.".format(self._asset_id))
        else:
            error_msg = u'WKC model use case unregistering failed'
            reason = response.text
            _logger.info(error_msg)
            raise ClientError(error_msg + '. Error: ' + str(response.status_code) + '. ' + reason)
    
    
    def set_custom_fact(self, fact_id: str, value: Any)->None:

        """
            Set custom fact by given id.

            :param str fact_id: Custom fact id.
            :param any value: Value of custom fact. It can be string, integer, date. if custom fact definition attribute `is_array` is set to `True`, value can be a string or list of strings.

            A way you might use me is:

            >>> model.set_custom_fact(fact_id="custom_int",value=50)
            >>> model.set_custom_fact(fact_id="custom_string",value="test")
            >>> model.set_custom_fact(fact_id="custom_string",value=["test","test2"]) # allowed if attribute property `is_array` is true.

        """
        attr_is_array=None
        if not value or value=='':
            raise ClientError("Value can not be empty")

        val_mfacts,val_mfacts_op= self._get_fact_definition_properties(fact_id)
        cur_val=val_mfacts or val_mfacts_op
        
        if val_mfacts_op:
            facts_type=FactsType.MODEL_FACTS_USER_OP
            url=self._get_url_by_factstype_container(type_name=facts_type)
            
        elif val_mfacts:
            facts_type=self._facts_type
            url=self._get_url_by_factstype_container()
        else:
            raise ClientError("Fact id {} is not defined under custom asset definitions".format(fact_id))

        if cur_val:
            attr_is_array=cur_val.get("is_array")

        value_type_array=(type(value) is not str and isinstance(value, collections.Sequence))
        
        if isinstance(value, list) and any(isinstance(x, dict) for x in value ):
            raise ClientError("Value should be a list of Strings but found Dict")

        self._type_check_by_id(fact_id,value)
        
        path= "/" + fact_id
        op = ADD

     
        if (attr_is_array and value_type_array) or value_type_array:
            body = [
                {
                    "op": op, 
                    "path": path,
                    "value": "[]"
                }
            ]
            response = requests.patch(url, data=json.dumps(body), headers=self._get_headers())
            
            if not response.status_code==200:
                raise ClientError("Patching array type values failed. ERROR {}. {}".format(response.status_code,response.text))
            
            op=REPLACE

        body = [
                {
                    "op": op, 
                    "path": path,
                    "value": value
                }
            ]

        
        response = requests.patch(url, data=json.dumps(body), headers=self._get_headers())
        
        if response.status_code==200:
            _logger.info("Custom fact {} successfully set to new value {}".format(fact_id,value))

        elif response.status_code==404:
            # to check and exclude modelfacts_user_op

            url=self._get_assets_attributes_url()

            body =  {
                        "name": facts_type,
                        "entity": {fact_id: value}
                        }

            response = requests.post(url,data=json.dumps(body), headers=self._get_headers())
            
            if response.status_code==201:
                _logger.info("Custom fact {} successfully set to new value {}".format(fact_id,value))
            else:
                _logger.error("Something went wrong. ERROR {}.{}".format(response.status_code,response.text))
        else:
            raise ClientError("Failed to add custom fact {}. ERROR: {}. {}".format(fact_id,response.status_code,response.text))


    def set_custom_facts(self, facts_dict: Dict[str, Any])->None:

        
        """
            Set multiple custom facts.

            :param dict facts_dict: Multiple custom facts. Example: {id: value, id1: value1, ...}

            A way you might use me is:

            >>> model.set_custom_facts({"fact_1": 2, "fact_2": "test", "fact_3":["data1","data2"]})

        """
        body=[]
        body_op=[]
        op_facts=[]
        non_op_facts=[]
        url_op=None
        url_non_op=None

        for key, val in list(facts_dict.items()):
            is_array=None

            attr_is_array,attr_is_array_op=self._get_fact_definition_properties(key)

            if attr_is_array_op:
                facts_type=FactsType.MODEL_FACTS_USER_OP
                url_op=self._get_url_by_factstype_container(type_name=facts_type)
        
            elif attr_is_array:
                facts_type=self._facts_type
                url_non_op=self._get_url_by_factstype_container()
            
            else:
                _logger.info("Escaping Fact id {} as it is not defined under custom asset definitions".format(key))

            cur_val= attr_is_array or attr_is_array_op
            
            if cur_val:
                is_array=cur_val.get("is_array")

                value_type_array=(type(val) is not str and isinstance(val, collections.Sequence))
                
                self._type_check_by_id(key,val)

                path= "/" + key
                op = ADD

                
                if (is_array and value_type_array) or value_type_array:
                    
                    tmp_body = {
                            "op": op, 
                            "path": path,
                            "value": "[]"
                        }


                    if facts_type==FactsType.MODEL_FACTS_USER_OP:
                        body_op.append(tmp_body)
                    else:
                        body.append(tmp_body)

                    op=REPLACE

                v = {
                    "op": op, #"replace",
                    "path": path,
                    "value": val
                }

                if facts_type==FactsType.MODEL_FACTS_USER_OP:
                    op_facts.append({key:val})
                    body_op.append(v)
                else:
                    non_op_facts.append({key:val})
                    body.append(v)

        if body_op:
            response_op = requests.patch(url_op, data=json.dumps(body_op), headers=self._get_headers())
            if response_op.status_code==200:
                _logger.info("Custom Openpages facts {} successfully set to values {}".format(list(set().union(*(d.keys() for d in op_facts))), list(itertools.chain(*[list(row.values()) for row in op_facts])) ))
            else:
                raise ClientError("Failed to set Openpages custom facts. ERROR: {}-{}".format(response.status_code,response.text))
        
        if body:
            response = requests.patch(url_non_op, data=json.dumps(body), headers=self._get_headers())
            if response.status_code==200:
                    _logger.info("Custom facts {} successfully set to values {}".format(list(set().union(*(d.keys() for d in non_op_facts))), list(itertools.chain(*[list(row.values()) for row in non_op_facts])) ))
        
            elif response.status_code==404:
                # to check and exclude modelfacts_user_op

                url=self._get_assets_attributes_url()

                body =  {
                            "name": self._facts_type,
                            "entity": facts_dict
                            }

                response = requests.post(url,data=json.dumps(body), headers=self._get_headers())
                if response.status_code==201:
                    _logger.info("Custom facts {} successfully set to values {}".format(list(set().union(*(d.keys() for d in non_op_facts))), list(itertools.chain(*[list(row.values()) for row in non_op_facts]))))
                else:
                    _logger.error("Something went wrong. ERROR {}.{}".format(response.status_code,response.text))

            else:
                raise ClientError("Failed to add custom facts. ERROR: {}-{}".format(response.status_code,response.text))
    
    
    def get_custom_fact_by_id(self, fact_id: str):

        """
            Get custom fact value/s by id

            :param str fact_id: Custom fact id to retrieve.

            A way you might use me is:

            >>> model.get_custom_fact_by_id(fact_id="fact_id")

        """

        val_mfacts,val_mfacts_op= self._get_fact_definition_properties(fact_id)
        
        if val_mfacts_op:
            facts_type=FactsType.MODEL_FACTS_USER_OP
            url=self._get_url_by_factstype_container(type_name=facts_type)
            
        else:
            facts_type=self._facts_type
            url=self._get_url_by_factstype_container()
        
        response = requests.get(url, headers=self._get_headers())

        if response.status_code==200:
            fact_details = response.json().get(facts_type)
            id_val=fact_details.get(fact_id)
            if not id_val:
                raise ClientError("Could not find value of fact_id {}".format(fact_id))
            else:
                return id_val

    def get_custom_facts(self)->Dict:

        """
            Get all defined custom facts for modelfacts_user fact type.

            :rtype: dict

            A way you might use me is:

            >>> model.get_custom_facts()

        """
        
        url=self._get_url_by_factstype_container()
        
        response = requests.get(url, headers=self._get_headers())

        if response.status_code==200:
            user_facts = response.json().get(self._facts_type)
            return user_facts
        else:
            raise ClientError("Failed to get facts. ERROR. {}. {}".format(response.status_code,response.text))


    
    def get_all_facts(self)->Dict:

        """
            Get all facts related to asset.
            
            :rtype: dict

            A way you might use me is:

            >>> model.get_all_facts()

        """
        
        url=self._get_assets_url(self._asset_id,self._container_type,self._container_id)
        response = requests.get(url, headers=self._get_headers())
        if response.status_code==200:
             return response.json() 
        else:
            raise ClientError("Failed to get facts. ERROR. {}. {}".format(response.status_code,response.text))


    def get_facts_by_type(self,facts_type:str=None)-> Dict:
        
        """
            Get custom facts by asset type. 

            :param str facts_type: (Optional) Custom facts asset type. Default to modelfacts_user type. For Openpages facts, use `modelfacts_user_op`.
            :rtype: dict

            A way you might use me is:

            >>> model.get_facts_by_type(facts_type=<type name>)

        """
        if not facts_type:
            facts_type=self._facts_type
        
        get_all_first=self.get_all_facts()
        all_resources=get_all_first.get("entity")
        if all_resources and all_resources.get(facts_type)!=None:
            return all_resources.get(facts_type)
        else:
            raise ClientError("Could not find custom facts for type {}".format(facts_type)) 


    def remove_custom_fact(self, fact_id: str)->None:

        """
            Remove custom fact by id

            :param str fact_id: Custom fact id value/s to remove.

            A way you might use me is:

            >>> model.remove_custom_fact(fact_id=<fact_id>)

        """

        val_mfacts,val_mfacts_op= self._get_fact_definition_properties(fact_id)
        
        if val_mfacts_op:
            facts_type=FactsType.MODEL_FACTS_USER_OP
            url=self._get_url_by_factstype_container(type_name=facts_type)
            
        else:
            facts_type=self._facts_type
            url=self._get_url_by_factstype_container()
        
        response = requests.get(url, headers=self._get_headers())

        if response.status_code==200:
            fact_details = response.json().get(facts_type)
            check_val_exists_for_id=fact_details.get(fact_id)
        if not check_val_exists_for_id:
            raise ClientError("Fact id {} is invalid or have no associated value to remove".format(fact_id))

        body = [
            {
                "op": "remove",  # "replace",
                "path": "/" + fact_id,
            }
        ]

        response = requests.patch(url, data=json.dumps(body), headers=self._get_headers())
        if response.status_code==200:
            _logger.info(" Value of Fact id {} removed successfully".format(fact_id))
        else:
            raise ClientError("Could not delete the fact_id {}. ERROR. {}. {}".format(fact_id,response.status_code,response.text))
            

    def remove_custom_facts(self, fact_ids:List[str])->None:

        """
            Remove multiple custom facts 

            :param list fact_ids: Custom fact ids to remove.

            A way you might use me is:

            >>> model.remove_custom_facts(fact_ids=["id1","id2"])

        """
        body=[]
        body_op=[]
        op_facts=[]
        non_op_facts=[]
        url_op=None
        url_non_op=None

        for fact_id in fact_ids:
            val_mfacts,val_mfacts_op= self._get_fact_definition_properties(fact_id)

            if val_mfacts_op:
                facts_type=FactsType.MODEL_FACTS_USER_OP
                url_op=self._get_url_by_factstype_container(type_name=facts_type)
                response = requests.get(url_op, headers=self._get_headers())
                
            else:
                facts_type=self._facts_type
                url_non_op=self._get_url_by_factstype_container()
                response = requests.get(url_non_op, headers=self._get_headers())


            if response.status_code==200:
                fact_details = response.json().get(facts_type)
            else:
                raise ClientError("Failed to find facts information for fact id {}. ERROR {}. {}".format(fact_id,response.status_code,response.text))
        
            cur_val=fact_details.get(fact_id)

            if cur_val:
                val = {
                    "op": "remove", #"replace",
                    "path": "/" + fact_id
                }

                if facts_type==FactsType.MODEL_FACTS_USER_OP:
                    op_facts.append(fact_id)
                    body_op.append(val)
                else:
                    non_op_facts.append(fact_id)
                    body.append(val)

            else:
                if facts_type==FactsType.MODEL_FACTS_USER_OP:
                    _logger.info("Escaping Openpages fact_id {} as either it is invalid or have no value to remove".format(fact_id))
                else:
                    _logger.info("Escaping fact_id {} as either it is invalid or have no value to remove".format(fact_id))
            
        if body_op:
            response_op = requests.patch(url_op, data=json.dumps(body_op), headers=self._get_headers())
            if response_op.status_code==200:
                _logger.info("Values of Openpages Fact ids {} removed successfully".format(op_facts))
            else:
                raise ClientError("Could not delete the Openpages fact_ids. ERROR. {}. {}".format(response.status_code,response.text))
        
        if body:
            response = requests.patch(url_non_op, data=json.dumps(body), headers=self._get_headers())
        
            if response.status_code==200:
                _logger.info("Values of Fact ids {} removed successfully".format(non_op_facts))
            else:
                raise ClientError("Could not delete the fact_ids. ERROR. {}. {}".format(response.status_code,response.text))

        
    def get_environment_type(self)-> Dict:

        """
            Get current environement details for related model asset. .

            :rtype: dict

            A way you might use me is:

            >>> model.get_environment_type()

        """


        container_info={}
        msg="The space {} {} which is considered as {} environment and asset shows under {} stage"
        
        container_asset_id=self._asset_id
        asset_container_type=self._container_type
        asset_container_id=self._container_id

        
        if container_asset_id and asset_container_type and asset_container_id:
        
            url=self._get_url_sysfacts_container(container_asset_id,asset_container_type,asset_container_id)
            
            response = requests.get(url, headers=self._get_headers())

            
            if self._external_model:

                space_info_exists=response.json().get(FactsType.MODEL_FACTS_SYSTEM).get(SPACE_DETAILS)
                deployment_details_exists=response.json().get(FactsType.MODEL_FACTS_SYSTEM).get(DEPLOYMENT_DETAILS)

                if space_info_exists:
                    space_type=space_info_exists.get(SPACE_TYPE)

                    if (space_type==AssetContainerSpaceMapExternal.DEVELOP.value or space_type=='') and not deployment_details_exists:
                        container_info["classification"]=AssetContainerSpaceMapExternal.DEVELOP.name
                        container_info["reason"]="The space type is {} and deployment_details are not available which is considered as {} environment and asset shows under {} stage".format(space_type,DEVELOP,AssetContainerSpaceMapExternal.DEVELOP.name)
                    
                    elif space_type==AssetContainerSpaceMapExternal.TEST.value and deployment_details_exists:
                        container_info["classification"]=AssetContainerSpaceMap.TEST.name
                        container_info["reason"]="The space type is {} and deployment_details are available which is considered as {} environment and asset shows under {} stage".format(space_type,TEST,AssetContainerSpaceMap.TEST.name)
                    
                    elif space_type ==AssetContainerSpaceMapExternal.VALIDATE.value:
                        container_info["classification"]=AssetContainerSpaceMapExternal.VALIDATE.name
                        container_info["reason"]="The space is marked as {} by Watson Open Scale which is considered as PRE-PRODUCTION environment and asset shows under {} stage".format(space_type,AssetContainerSpaceMapExternal.VALIDATE.name)

                    
                    elif space_type== AssetContainerSpaceMapExternal.OPERATE.value:
                        container_info["classification"]=AssetContainerSpaceMapExternal.OPERATE.name
                        container_info["reason"]="The space is marked as {} by Watson Open Scale which is considered as PRODUCTION environment and asset shows under {} stage".format(space_type,AssetContainerSpaceMapExternal.OPERATE.name)
                    
                    else:
                        raise ClientError ("Invalid space type {} found".format(space_type))
                else:
                     raise ClientError("Associated space details not found for asset {}".format(container_asset_id))
            
            else:

                try:
                    sys_facts=response.json().get(FactsType.MODEL_FACTS_SYSTEM)
                    space_info_exists= sys_facts.get(SPACE_DETAILS)
                except:
                    raise ClientError("Failed to get space information details")

                if space_info_exists:
                    space_type=space_info_exists.get(SPACE_TYPE)

                    if space_type==AssetContainerSpaceMap.TEST.value:
                            container_info["classification"]=AssetContainerSpaceMap.TEST.name
                            container_info["reason"]=msg.format("type is", space_type,TEST,AssetContainerSpaceMap.TEST.name)
                    
                    elif space_type == AssetContainerSpaceMap.VALIDATE.value:
                            container_info["classification"]=AssetContainerSpaceMap.VALIDATE.name
                            container_info["reason"]="The space is marked as {} by Watson Open Scale which is considered as PRE-PRODUCTION environment and asset shows under {} stage".format(AssetContainerSpaceMap.VALIDATE.value,AssetContainerSpaceMap.VALIDATE.name)
                            
                            
                    elif space_type== AssetContainerSpaceMap.OPERATE.value:
                            container_info["classification"]=AssetContainerSpaceMap.OPERATE.name
                            container_info["reason"]="The space is marked as {} by Watson Open Scale which is considered as PRODUCTION environment and asset shows under {} stage".format(AssetContainerSpaceMap.OPERATE.value,AssetContainerSpaceMap.OPERATE.name)
                    
                    elif space_type=='':
                        container_info["classification"]=AssetContainerSpaceMap.DEVELOP.name
                        container_info["reason"]= msg.format("type is",space_type,DEVELOP,AssetContainerSpaceMap.DEVELOP.name)
                    
                    else:
                        raise ClientError ("Invalid space type {} found".format(space_type))
                
                else:
                    container_info["classification"]=AssetContainerSpaceMap.DEVELOP.name
                    container_info["reason"]="Asset is developed in project so it is considered in {} stage".format(DEVELOP)

            
            return container_info
        else:
            raise ClientError("Valid asset informations not used (asset_id, container_type and contaoner_id)")


    def set_environment_type(self, from_container: str, to_container: str)->None:
        
        """
            Set current container for model asset. For available options check :func:`~ibm_aigov_facts_client.utils.enums.ModelEntryContainerType`

            :param str from_container: Container name to move from
            :param str to_container: Container name to move to

            
            A way you might use me is:

            >>> model.set_environment_type(from_container="test",to_container="validate")

        """
        
        if self._external_model:
            self._set_environment_classification_external(from_container,to_container)
            
        else:
            validate_enum(from_container,"from_container", ModelEntryContainerType, True)
            validate_enum(to_container,"to_container", ModelEntryContainerType, True)

            container_asset_id=self._asset_id
            asset_container_type=self._container_type
            asset_container_id=self._container_id

            if (from_container==to_container) or from_container=='' or to_container=='':
                raise ClientError("From and To containers can not be same or empty string")

            try:
                self._get_tracking_model_usecase_info()
                cur_container_info=self.get_environment_type()
            except:
                raise ClientError("Current container details not found")
            
            if cur_container_info.get("classification")==to_container.upper():
                raise ClientError("Asset is already set to {} container".format(to_container))

            if cur_container_info.get("classification")==ModelEntryContainerType.DEVELOP.upper() and asset_container_type==ContainerType.PROJECT:
                raise ClientError(" Asset in project should be promoted to space before invoking this method")

            if container_asset_id and asset_container_type and asset_container_id:
            
                url=self._get_url_sysfacts_container(container_asset_id,asset_container_type,asset_container_id)
                
                try:
                    sys_facts_response = requests.get(url, headers=self._get_headers())
                    sys_facts=sys_facts_response.json().get(FactsType.MODEL_FACTS_SYSTEM)
                except:
                    raise ClientError("System facts for asset id {} are not found".format(container_asset_id))
                

                is_wml_model=(WML_MODEL==sys_facts.get(MODEL_INFO_TAG).get(ASSET_TYPE_TAG))
                
                space_details=sys_facts.get(SPACE_DETAILS)

                if is_wml_model and space_details:

                    current_model_usecase=self._get_tracking_model_usecase_info()

                    if not current_model_usecase:
                        raise ClientError("Could not find related model use case information. Please make sure, the model is associated to a model use case")

                    current_space_id= space_details.get(SPACE_ID)
                    get_spaces_url= self._get_url_space(current_space_id)
                    space_info=requests.get(get_spaces_url, headers=self._get_headers())             
                    get_tags=space_info.json()["entity"].get("tags")

                    if ((from_container==ModelEntryContainerType.DEVELOP and (to_container==ModelEntryContainerType.TEST or to_container==ModelEntryContainerType.VALIDATE or to_container==ModelEntryContainerType.OPERATE) ) \
                        or (to_container==ModelEntryContainerType.DEVELOP and (from_container==ModelEntryContainerType.TEST or from_container==ModelEntryContainerType.VALIDATE or from_container==ModelEntryContainerType.OPERATE ))):
                        
                        raise ClientError ("Model asset can not be moved from {} to {} container".format(from_container,to_container))
                    
                    elif from_container==ModelEntryContainerType.TEST and to_container==ModelEntryContainerType.VALIDATE:
                        
                        if get_tags:

                            body=[
                                {
                                    "op": "add",
                                    "path": "/tags/-",
                                    "value": SPACE_PREPROD_TAG
                                }
                                ]
                        else:
                            body= [
                                {
                                    "op": "add",
                                    "path": "/tags",
                                    "value": [SPACE_PREPROD_TAG]
                                }
                                ]

                        response = requests.patch(get_spaces_url,data=json.dumps(body), headers=self._get_headers())

                        if response.status_code==200:
                            trigger_status=self._trigger_container_move(container_asset_id,asset_container_type,asset_container_id)
                            if trigger_status==200:
                                _logger.info("Asset successfully moved from {} to {} environment".format(from_container,to_container))
                        else:
                            raise ClientError("Asset space update failed. ERROR {}. {}".format(response.status_code,response.text))
                    
                    elif from_container==ModelEntryContainerType.TEST and to_container==ModelEntryContainerType.OPERATE:

                        if get_tags:

                            body=[
                                {
                                    "op": "add",
                                    "path": "/tags/-",
                                    "value": SPACES_PROD_TAG
                                }
                                ]
                        else:
                            body= [
                                {
                                    "op": "add",
                                    "path": "/tags",
                                    "value": [SPACES_PROD_TAG]
                                }
                                ]

                        response = requests.patch(get_spaces_url,data=json.dumps(body), headers=self._get_headers())
                        
                        if response.status_code==200:
                            trigger_status=self._trigger_container_move(container_asset_id,asset_container_type,asset_container_id)
                            if trigger_status==200:
                                _logger.info("Asset successfully moved from {} to {} environment".format(from_container,to_container))
                        else:
                            raise ClientError("Asset space update failed. ERROR {}. {}".format(response.status_code,response.text))

                    elif (from_container==ModelEntryContainerType.VALIDATE or from_container==ModelEntryContainerType.OPERATE) and to_container==ModelEntryContainerType.TEST:
                        
                        
                        openscale_monitored= space_details.get(SPACE_OS_MONITOR_TAG)

                        if openscale_monitored:
                            raise ClientError("The model deployment is already evaluated in Watson OpenScale and can not be moved from {} to {}".format(ModelEntryContainerType.VALIDATE,ModelEntryContainerType.TEST))
                        else:
                            if get_tags:
                                if from_container==ModelEntryContainerType.VALIDATE:
                                    get_tag_idx=get_tags.index(SPACE_PREPROD_TAG)
                                else:
                                    get_tag_idx=get_tags.index(SPACES_PROD_TAG)
                            else:
                                raise ClientError("Could not resolve space tags")

                            body=[{
                                    "op": "remove",
                                    "path": "/tags/" + str(get_tag_idx)
                                }
                                ]

                            response = requests.patch(get_spaces_url,data=json.dumps(body), headers=self._get_headers())

                            if response.status_code==200:
                                trigger_status=self._trigger_container_move(container_asset_id,asset_container_type,asset_container_id)
                                if trigger_status==200:
                                    _logger.info("Asset successfully moved from {} to {} environment".format(from_container,to_container))
                            else:
                                raise ClientError("Asset space update failed. ERROR {}. {}".format(response.status_code,response.text))

                    elif from_container==ModelEntryContainerType.VALIDATE and to_container==ModelEntryContainerType.OPERATE:
                        
                        openscale_monitored= space_details.get(SPACE_OS_MONITOR_TAG)

                        if openscale_monitored:
                            raise ClientError("The model deployment is already evaluated in Watson OpenScale and can not be moved from {} to {}".format(ModelEntryContainerType.VALIDATE,ModelEntryContainerType.TEST))
                        else:

                            if get_tags:
                                get_tag_idx=get_tags.index(SPACE_PREPROD_TAG)
                            else:
                                raise ClientError("Could not resolve space tags")

                            updated_space_info=requests.get(get_spaces_url, headers=self._get_headers())
                            get_updated_tags=updated_space_info.json()["entity"].get("tags")
                            
                            # todo check entity.tags
                            if get_updated_tags:
                                add_tag_body={
                                    "op": "add",
                                    "path": "/tags/-",
                                    "value": SPACES_PROD_TAG
                                }
                            else:
                                add_tag_body={
                                    "op": "add",
                                    "path": "/tags",
                                    "value": [SPACES_PROD_TAG]
                                }

                            body=[ {
                                "op": "remove",
                                "path": "/tags/" + str(get_tag_idx)
                            },add_tag_body
                            
                            ]

                            response = requests.patch(get_spaces_url,data=json.dumps(body), headers=self._get_headers())
                            if response.status_code==200:
                                trigger_status=self._trigger_container_move(container_asset_id,asset_container_type,asset_container_id)
                                if trigger_status==200:
                                    _logger.info("Asset successfully moved from {} to {} environment".format(from_container,to_container))
                            else:
                                raise ClientError("Asset space update failed. ERROR {}. {}".format(response.status_code,response.text))

                    elif from_container==ModelEntryContainerType.OPERATE and to_container==ModelEntryContainerType.VALIDATE:
                        openscale_monitored= space_details.get(SPACE_OS_MONITOR_TAG)

                        if openscale_monitored:
                            raise ClientError("The model deployment is already evaluated in Watson OpenScale and can not be moved from {} to {}".format(ModelEntryContainerType.VALIDATE,ModelEntryContainerType.TEST))
                        else:
                            if get_tags:
                                get_tag_idx=get_tags.index(SPACES_PROD_TAG)
                            else:
                                raise ClientError("Could not resolve space tags")

                            updated_space_info=requests.get(get_spaces_url, headers=self._get_headers())
                            get_updated_tags=updated_space_info.json()["entity"].get("tags")
                            
                            # todo check entity.tags
                            if get_updated_tags:
                                add_tag_body={
                                    "op": "add",
                                    "path": "/tags/-",
                                    "value": SPACE_PREPROD_TAG
                                }
                            else:
                                add_tag_body={
                                    "op": "add",
                                    "path": "/tags",
                                    "value": [SPACE_PREPROD_TAG]
                                }

                            body=[ {
                                "op": "remove",
                                "path": "/tags/" + str(get_tag_idx)
                            },add_tag_body
                            
                            ]

                            response = requests.patch(get_spaces_url,data=json.dumps(body), headers=self._get_headers())
                            if response.status_code==200:
                                trigger_status=self._trigger_container_move(container_asset_id,asset_container_type,asset_container_id)
                                if trigger_status==200:
                                    _logger.info("Asset successfully moved from {} to {} environment".format(from_container,to_container))
                            else:
                                raise ClientError("Asset space update failed. ERROR {}. {}".format(response.status_code,response.text))
                    else:
                        raise ClientError ("Could not set asset from {} to {} container".format(from_container,to_container))
                else:
                    raise ClientError("Asset should be in TEST stage (Deploy to space) before using this feature")
            else:
                raise ClientError(" Valid asset informations not used. please check provided asset_id, container_type and container_id")


    def _set_environment_classification_external(self, from_container: str, to_container: str)->None:
        
        """
            Set current container for external model asset. For available options check :func:`ibm_aigov_facts_client.utils.enums.ModelEntryContainerType`

            :param str from_container: Container name to move from
            :param str to_container: Container name to move to
            
        """
        
        validate_enum(from_container,"from_container", ModelEntryContainerType, True)
        validate_enum(to_container,"to_container", ModelEntryContainerType, True)

        if (from_container==to_container) or from_container=='' or to_container=='':
            raise ClientError("From and To containers can not be same or empty string")
        
        if from_container==ModelEntryContainerType.DEVELOP and to_container==ModelEntryContainerType.TEST:
            raise ClientError("Model asset in develop stage can not be moved to test. You can add deployment_details when saving model asset that will move asset to test environment")

        
        container_asset_id= self._asset_id
        asset_container_type= self._container_type
        asset_container_id= self._container_id

        url=self._get_url_sysfacts_container(container_asset_id,asset_container_type,asset_container_id)
            
        try:
            sys_facts_response = requests.get(url, headers=self._get_headers())
            sys_facts=sys_facts_response.json().get(FactsType.MODEL_FACTS_SYSTEM)
            is_ext_model=(EXT_MODEL==sys_facts.get(MODEL_INFO_TAG).get(ASSET_TYPE_TAG))
        except:
            raise ClientError("System facts for asset id {} are not found".format(container_asset_id))
        
        if is_ext_model:

            if asset_container_type!=ContainerType.CATALOG:
                raise ClientError("For external model, container type should be catalog only")

            try:
                cur_container_info=self.get_environment_type()
            except:
                raise ClientError("Current container details not found")
        
            if cur_container_info.get("CONTAINER_CARD")==to_container.upper():
                raise ClientError("Asset is already set to {} container".format(to_container))

            
            current_model_usecase=self._get_tracking_model_usecase_info()

            if current_model_usecase:  
            
                try:
                    space_details=sys_facts.get(SPACE_DETAILS)
                except:
                    raise ClientError("Space details information not found")
                
                deploy_details=sys_facts.get(DEPLOYMENT_DETAILS)

                if ((from_container==ModelEntryContainerType.DEVELOP and (to_container==ModelEntryContainerType.TEST or to_container==ModelEntryContainerType.VALIDATE or to_container==ModelEntryContainerType.OPERATE)) and not deploy_details) or (from_container==ModelEntryContainerType.TEST and to_container==ModelEntryContainerType.DEVELOP):
                    raise ClientError ("Model asset can not be moved from {} to {} container".format(from_container,to_container))
                
                elif from_container==ModelEntryContainerType.TEST and to_container==ModelEntryContainerType.VALIDATE:
                    
                    body=[
                        {"op":"add"
                        ,"path":"/space_details/space_type"
                        ,"value":SPACE_PREPROD_TAG_EXTERNAL}
                        ]
                    
                    patch_sys_facts = requests.patch(url,data=json.dumps(body), headers=self._get_headers())

                    if patch_sys_facts.status_code==200:
                        global_facts_url=self._get_url_sysfacts_container(current_model_usecase["model_usecase_id"],current_model_usecase["container_type"],current_model_usecase["catalog_id"],key=FactsType.MODEL_FACTS_GLOBAL)

                        response = requests.get(global_facts_url, headers=self._get_headers())
                        if response.status_code==200:
                            get_facts= response.json()
                        else:
                            raise ClientError("Facts global metadata not found. ERROR {}. {}".format(response.status_code,response.text)) 

                        try:
                            physical_models=get_facts.get('modelfacts_global').get('physical_models')
                            get_idx=physical_models.index(next(filter(lambda n: n.get('id') == self._asset_id, physical_models)))
                        except:
                            raise ClientError(" No physical model details found in modelfacts_global")

                        body= [
                            {"op":"add"
                            ,"path":"/physical_models/{}/deployment_space_type".format(get_idx)
                            ,"value":SPACE_PREPROD_TAG_EXTERNAL}
                            ]

                        patch_physical_model = requests.patch(global_facts_url,data=json.dumps(body), headers=self._get_headers())

                        if patch_physical_model.status_code==200:

                            _logger.info("Asset successfully moved from {} to {} environment".format(from_container,to_container))
                        else:
                            raise ClientError ("Could not update physical model definition. ERROR {}. {}".format(patch_physical_model.status_code,patch_physical_model.text))
                    else:
                        raise ClientError("Asset space update failed. ERROR {}. {}".format(patch_sys_facts.status_code,patch_sys_facts.text))
                
                elif (from_container==ModelEntryContainerType.TEST or from_container==ModelEntryContainerType.VALIDATE) and to_container==ModelEntryContainerType.OPERATE:

                    openscale_monitored= space_details.get(SPACE_OS_MONITOR_TAG)
                    
                    if openscale_monitored:
                        raise ClientError("The model deployment is already evaluated in Watson OpenScale and can not be moved from {} to {}".format(from_container,to_container))
                    
                    else:
                        body=[
                            {"op":"add"
                            ,"path":"/space_details/space_type"
                            ,"value":SPACES_PROD_TAG_EXTERNAL
                            }
                            ]
                        
                        patch_sys_facts = requests.patch(url,data=json.dumps(body), headers=self._get_headers())

                        if patch_sys_facts.status_code==200:
                            
                            global_facts_url=self._get_url_sysfacts_container(current_model_usecase["model_usecase_id"],current_model_usecase["container_type"],current_model_usecase["catalog_id"],key=FactsType.MODEL_FACTS_GLOBAL)
                            response = requests.get(global_facts_url, headers=self._get_headers())
                            if response.status_code==200:
                                get_facts= response.json()
                            else:
                                raise ClientError("Facts global metadata not found. ERROR {}. {}".format(response.status_code,response.text)) 

                            try:
                                physical_models=get_facts.get('modelfacts_global').get('physical_models')
                                get_idx=physical_models.index(next(filter(lambda n: n.get('id') == self._asset_id, physical_models)))
                                
                            except:
                                raise ClientError(" No physical model details found in modelfacts_global")

                            body= [
                                {"op":"add"
                                ,"path":"/physical_models/{}/deployment_space_type".format(get_idx)
                                ,"value":SPACES_PROD_TAG_EXTERNAL}]

                            patch_physical_model = requests.patch(global_facts_url,data=json.dumps(body), headers=self._get_headers())

                            if patch_physical_model.status_code==200:

                                _logger.info("Asset successfully moved from {} to {} environment".format(from_container,to_container))
                            else:
                                raise ClientError ("Could not update physical model definition. ERROR {}. {}".format(patch_physical_model.status_code,patch_physical_model.text))
                        
                        
                        else:
                            raise ClientError("Asset space update failed. ERROR {}. {}".format(patch_sys_facts.status_code,patch_sys_facts.text))
                
                elif (from_container==ModelEntryContainerType.VALIDATE or from_container== ModelEntryContainerType.OPERATE) and to_container==ModelEntryContainerType.TEST:
                    
                    openscale_monitored= space_details.get(SPACE_OS_MONITOR_TAG)
                    
                    if openscale_monitored:
                        raise ClientError("The model deployment is already evaluated in Watson OpenScale and can not be moved from {} to {}".format(from_container,to_container))
                    
                    else:

                        body=[
                        {"op":"add"
                        ,"path":"/space_details/space_type"
                        ,"value":SPACE_TEST_TAG
                        }
                        ]
                    
                    patch_sys_facts = requests.patch(url,data=json.dumps(body), headers=self._get_headers())

                    if patch_sys_facts.status_code==200:
                        global_facts_url=self._get_url_sysfacts_container(current_model_usecase["model_usecase_id"],current_model_usecase["container_type"],current_model_usecase["catalog_id"],key=FactsType.MODEL_FACTS_GLOBAL)

                        response = requests.get(global_facts_url, headers=self._get_headers())
                        if response.status_code==200:
                            get_facts= response.json()
                        else:
                            raise ClientError("Facts global metadata not found. ERROR {}. {}".format(response.status_code,response.text)) 

                        try:
                            physical_models=get_facts.get('modelfacts_global').get('physical_models')
                            get_idx=physical_models.index(next(filter(lambda n: n.get('id') == self._asset_id, physical_models)))
                        except:
                            raise ClientError(" No physical model details found in modelfacts_global")

                        body= [
                            {"op":"add"
                            ,"path":"/physical_models/{}/deployment_space_type".format(get_idx)
                            ,"value":SPACE_TEST_TAG}]

                        patch_physical_model = requests.patch(global_facts_url,data=json.dumps(body), headers=self._get_headers())

                        if patch_physical_model.status_code==200:
                            _logger.info("Asset successfully moved from {} to {} environment".format(from_container,to_container))

                        else:
                            raise ClientError ("Could not update physical model definition. ERROR {}. {}".format(patch_physical_model.status_code,patch_physical_model.text))
                elif from_container==ModelEntryContainerType.OPERATE and to_container== ModelEntryContainerType.VALIDATE:
                    
                    openscale_monitored= space_details.get(SPACE_OS_MONITOR_TAG)
                    
                    if openscale_monitored:
                        raise ClientError("The model deployment is already evaluated in Watson OpenScale and can not be moved from {} to {}".format(from_container,to_container))
                    
                    else:

                        body=[
                        {"op":"add"
                        ,"path":"/space_details/space_type"
                        ,"value":SPACE_PREPROD_TAG_EXTERNAL
                        }
                        ]
                    
                    patch_sys_facts = requests.patch(url,data=json.dumps(body), headers=self._get_headers())

                    if patch_sys_facts.status_code==200:
                        global_facts_url=self._get_url_sysfacts_container(current_model_usecase["model_usecase_id"],current_model_usecase["container_type"],current_model_usecase["catalog_id"],key=FactsType.MODEL_FACTS_GLOBAL)

                        response = requests.get(global_facts_url, headers=self._get_headers())
                        if response.status_code==200:
                            get_facts= response.json()
                        else:
                            raise ClientError("Facts global metadata not found. ERROR {}. {}".format(response.status_code,response.text)) 

                        try:
                            physical_models=get_facts.get('modelfacts_global').get('physical_models')
                            get_idx=physical_models.index(next(filter(lambda n: n.get('id') == self._asset_id, physical_models)))
                        except:
                            raise ClientError(" No physical model details found in modelfacts_global")

                        body= [
                            {"op":"add"
                            ,"path":"/physical_models/{}/deployment_space_type".format(get_idx)
                            ,"value":SPACE_PREPROD_TAG_EXTERNAL}]

                        patch_physical_model = requests.patch(global_facts_url,data=json.dumps(body), headers=self._get_headers())

                        if patch_physical_model.status_code==200:
                            _logger.info("Asset successfully moved from {} to {} environment".format(from_container,to_container))

                        else:
                            raise ClientError ("Could not update physical model definition. ERROR {}. {}".format(patch_physical_model.status_code,patch_physical_model.text))
                    
                else:
                    raise ClientError ("Could not set external model asset from {} to {} container".format(from_container,to_container))
            else:
                raise ClientError("Could not find related model use case information. Please make sure, the model is associated to a model use case")
        else:
            raise ClientError("For Watson Machine Learning models, use `set_asset_container()` instead")
    
    
    
    def set_attachment_fact(self, 
                        file_to_upload,
                        description:str,
                        fact_id:str,
                        html_rendering_hint:str=None
                        )->None:
    
        """
            Set attachment fact for given asset. Supported for CPD version >=4.6.5.
            
            :param str file_to_upload: Attachment file path to upload
            :param str description: Description about the attachment file
            :param str fact_id: Fact id for the attachment
            :param str html_rendering_hint: (Optional) html rendering hint. Available options are in :func:`~ibm_aigov_facts_client.utils.enums.RenderingHints`

            A way to use me is:

            >>> model.set_attachment_fact(fileToUpload="./artifacts/image.png",description=<file description>,fact_id=<custom fact id>)
            >>> model.set_attachment_fact(fileToUpload="./artifacts/image.png",description=<file description>,fact_id=<custom fact id>,html_rendering_hint=<render hint>)

        """
        
        if self._is_cp4d and self._cp4d_version < "4.6.5":
            raise ClientError("Version mismatch: Attachment functionality is only supported in CP4D version 4.6.5 or higher. Current version of CP4D is "+self._cp4d_version)

        model_asset_id=self._asset_id
        model_container_type= self._container_type
        model_container_id= self._container_id

        if os.path.exists(file_to_upload):
            file_size=os.stat(file_to_upload).st_size
            #<500MB
            if file_size>MAX_SIZE:
                raise ClientError("Maximum file size allowed is 500 MB")
        else:
            raise ClientError("Invalid file path provided")

        if html_rendering_hint:
            validate_enum(html_rendering_hint,"html_rendering_hint", RenderingHints, False)

        # check if have attachment for given fact id. only one attachment allowed per fact_id.
        get_factid_attachment=self.list_attachments(filter_by_factid=fact_id)

        if get_factid_attachment:
            raise ClientError("Fact id {} already have an attachment set and only allowed to have one. You can remove and set new attachment if needed".format(fact_id))
        
        else:
            #create attachment

            mimetype=self._get_mime(file_to_upload)

            attachment_url=self._get_url_attachments(model_asset_id,model_container_type,model_container_id)

            #base_filename = os.path.basename(file_to_upload)
            base_filename_before = os.path.basename(file_to_upload)
            base_filename = base_filename_before.replace(" ","_")

            # convert png to jpeg
            flag=False
            if mimetype=="image/png":
                from PIL import Image

                ima=Image.open(file_to_upload)
                rgb_im = ima.convert('RGB')
                rgb_im.save(os.path.splitext(file_to_upload)[0]+".jpg", format='JPEG')
                mimetype="image/jpg"
                #base_filename=os.path.splitext(file_to_upload)[0]+".jpg"
                #file_to_upload=base_filename
                base_filename=os.path.splitext(base_filename)[0]+".jpg"
                file_to_upload=os.path.splitext(file_to_upload)[0]+".jpg"
                flag=True

            
            attachment_data = {}

            if fact_id: 
                attachment_data["fact_id"] = fact_id
            if html_rendering_hint: 
                attachment_data["html_rendering_hint"] = html_rendering_hint

            body = "{ \"asset_type\": \""+self._facts_type+"\" \
                    , \"name\": \"" + base_filename + "\",\"mime\": \"" + mimetype \
                    + "\",\"data_partitions\" : 0,\"private_url\": \"false\",\"is_partitioned\": \"false\",\"description\": \"" \
                    + description + "\",\"user_data\": " + json.dumps(attachment_data) + "}"
            

            create_attachment_response = requests.post(attachment_url, data=body, headers=self._get_headers())

            if create_attachment_response.status_code==400:
                url=self._get_assets_attributes_url()

                body =  {
                            "name": self._facts_type,
                            "entity": {}
                            }

                response = requests.post(url,data=json.dumps(body), headers=self._get_headers())
            
                if response.status_code==201:
                   create_attachment_response = requests.post(attachment_url, data=body, headers=self._get_headers())
                else:
                    raise ClientError("Failed to initiate {} attribute. ERROR {}. {}".format(self._facts_type,response.status_code,response.text))
            
            if create_attachment_response.status_code==201:
                get_upload_uri=create_attachment_response.json().get("url1")
                if not get_upload_uri:
                    raise ClientError("Upload url not found")
            else:
                raise ClientError("Failed to create attachment URL. ERROR {}. {}".format(create_attachment_response.status_code,create_attachment_response.text))

            if self._is_cp4d:
                get_upload_uri = self._cpd_configs["url"] + get_upload_uri
            
            attachment_id=create_attachment_response.json()["attachment_id"]

            # upload file

            if self._is_cp4d:
                files= {'file': (file_to_upload, open(file_to_upload, 'rb').read(),mimetype)}
                response_update = requests.put(get_upload_uri, files=files)

            else:
                # headers=self._get_headers()
                with open(file_to_upload, 'rb') as f:
                    data=f.read()
                    response_update=requests.put(get_upload_uri,data=data)

            if response_update.status_code==201 or response_update.status_code==200:

                #complete attachment
                completion_url=self._get_url_attachments(model_asset_id,model_container_type,model_container_id,attachment_id,action="complete")
                completion_response=requests.post(completion_url,headers=self._get_headers())
                

                if completion_response.status_code==200:
                    
                    #get attachment info
                    get_attachmentUrl=self._get_url_attachments(model_asset_id,model_container_type,model_container_id,attachment_id,mimetype,action="get")
                    
                    if (mimetype.startswith("image/") or mimetype.startswith("application/pdf")
                            or mimetype.startswith("text/html")):
                        get_attachmentUrl += '&response-content-disposition=inline;filename=' + file_to_upload

                    else: 
                        get_attachmentUrl += '&response-content-disposition=attachment;filename=' + file_to_upload

                    response_get=requests.get(get_attachmentUrl,headers=self._get_headers())

                    if response_get.status_code==200:
                        if self._is_cp4d:
                            url= self._cpd_configs["url"] + response_get.json().get("url")
                            _logger.info("Attachment uploaded successfully and access url (15min valid) is - {}".format(url))
                        else:
                            _logger.info("Attachment uploaded successfully and access url (15min valid) is - {}".format(response_get.json().get("url")))
                        if flag:
                            os.remove(file_to_upload)
                    else:
                        raise ClientError("Could not fetch attachment url. ERROR {}. {}".format(response_get.status_code,response_get.text))  

                else:
                    raise ClientError("Failed to mark attachment as complete. ERROR {}. {} ".format(completion_response.status_code,completion_response.text))

            else:
                raise ClientError("Failed to upload file using URI {}. ERROR {}. {}".format(get_upload_uri ,response_update.status_code,response_update.text))

    def set_cell_attachment_fact(self, 
                        description:str,
                        fact_id:str
                        )->None:
    
        """
            Set attachment fact using captured cell output. Supported for CPD version >=4.6.5.
            
            :param str description: Description about the cell facts attachment file
            :param str fact_id: Fact id for the attachment

            A way to use me is:

            >>> model.set_cell_attachment_fact(description=<file description>,fact_id=<custom fact id>)

        """
        
        if self._is_cp4d and self._cp4d_version < "4.6.5":
            raise ClientError("Version mismatch: Attachment functionality is only supported in CP4D version 4.6.5 or higher. Current version of CP4D is "+self._cp4d_version)

        model_asset_id=self._asset_id
        model_container_type= self._container_type
        model_container_id= self._container_id

        
        file_to_upload="{}/{}/{}".format(os.getcwd(),CELL_FACTS_TMP_DIR,CellFactsMagic._fname)
        
        if not os.path.exists(file_to_upload):
            raise ClientError("Invalid file path. Failed to find {}".format(CellFactsMagic._fname))

        # check if have attachment for given fact id. only one attachment allowed per fact_id.
        get_factid_attachment=self.list_attachments(filter_by_factid=fact_id)

        if get_factid_attachment:
            raise ClientError("Fact id {} already have an attachment set and only allowed to have one. You can remove and set new attachment if needed".format(fact_id))
        
        else:
            #create attachment

            mimetype=self._get_mime(file_to_upload)

            attachment_url=self._get_url_attachments(model_asset_id,model_container_type,model_container_id)

            base_filename = os.path.basename(file_to_upload)

            
            attachment_data = {}

            if fact_id: 
                attachment_data["fact_id"] = fact_id
            attachment_data["html_rendering_hint"] = "inline_html"

            body = "{ \"asset_type\": \""+self._facts_type+"\" \
                    , \"name\": \"" + base_filename + "\",\"mime\": \"" + mimetype \
                    + "\",\"data_partitions\" : 0,\"private_url\": \"false\",\"is_partitioned\": \"false\",\"description\": \"" \
                    + description + "\",\"user_data\": " + json.dumps(attachment_data) + "}"
            

            create_attachment_response = requests.post(attachment_url, data=body, headers=self._get_headers())

            if create_attachment_response.status_code==400:
                url=self._get_assets_attributes_url()

                body =  {
                            "name": self._facts_type,
                            "entity": {}
                            }

                response = requests.post(url,data=json.dumps(body), headers=self._get_headers())
            
                if response.status_code==201:
                   create_attachment_response = requests.post(attachment_url, data=body, headers=self._get_headers())
                else:
                    raise ClientError("Failed to initiate {} attribute. ERROR {}. {}".format(self._facts_type,response.status_code,response.text))
            
            if create_attachment_response.status_code==201:
                get_upload_uri=create_attachment_response.json().get("url1")
                if not get_upload_uri:
                    raise ClientError("Upload url not found")
            else:
                raise ClientError("Failed to create attachment URL. ERROR {}. {}".format(create_attachment_response.status_code,create_attachment_response.text))

            if self._is_cp4d:
                get_upload_uri = self._cpd_configs["url"] + get_upload_uri
            
            attachment_id=create_attachment_response.json()["attachment_id"]

            # upload file

            if self._is_cp4d:
                files= {'file': (file_to_upload, open(file_to_upload, 'rb').read(),mimetype)}
                response_update = requests.put(get_upload_uri, files=files)

            else:
                # headers=self._get_headers()
                with open(file_to_upload, 'rb') as f:
                    data=f.read()
                    response_update=requests.put(get_upload_uri,data=data)

            if response_update.status_code==201 or response_update.status_code==200:

                #complete attachment
                completion_url=self._get_url_attachments(model_asset_id,model_container_type,model_container_id,attachment_id,action="complete")
                completion_response=requests.post(completion_url,headers=self._get_headers())
                

                if completion_response.status_code==200:
                    
                    #get attachment info
                    get_attachmentUrl=self._get_url_attachments(model_asset_id,model_container_type,model_container_id,attachment_id,mimetype,action="get")
                    
                    get_attachmentUrl += '&response-content-disposition=inline;filename=' + file_to_upload

                    response_get=requests.get(get_attachmentUrl,headers=self._get_headers())

                    if response_get.status_code==200:
                        if self._is_cp4d:
                            url= self._cpd_configs["url"] + response_get.json().get("url")
                            _logger.info("Cell facts attachment uploaded successfully and access url (15min valid) is - {}".format(url))
                        else:
                            _logger.info("Cell facts attachment uploaded successfully and access url (15min valid) is - {}".format(response_get.json().get("url")))
                        
                        os.remove(file_to_upload)
                    else:
                        raise ClientError("Could not fetch attachment url. ERROR {}. {}".format(response_get.status_code,response_get.text))  

                else:
                    raise ClientError("Failed to mark attachment as complete. ERROR {}. {} ".format(completion_response.status_code,completion_response.text))

            else:
                raise ClientError("Failed to upload file using URI {}. ERROR {}. {}".format(get_upload_uri ,response_update.status_code,response_update.text))

    def has_attachment(self,fact_id:str=None)-> bool:
        """ Check if attachment/s exist. Supported for CPD version >=4.6.5

        :param fact_id: Id of attachment fact 
        :type fact_id: str, optional

        :rtype: bool

        The way to use me is :

        >>> model.has_attachment()
        >>> model.has_attachment(fact_id=<fact id>)

        """

        if self._is_cp4d and self._cp4d_version < "4.6.5":
            raise ClientError("Version mismatch: Attachment functionality is only supported in CP4D version 4.6.5 or higher. Current version of CP4D is "+self._cp4d_version)

        url=self._get_assets_url(self._asset_id,self._container_type,self._container_id)
        response=requests.get(url,headers=self._get_headers())
        all_attachments=response.json().get(ATTACHMENT_TAG)
        if all_attachments:
            attachments=[ i for i in all_attachments if i.get('asset_type')==self._facts_type and (fact_id==None or fact_id==i.get("user_data").get("fact_id"))]
            if attachments:
                return True
            else:
                return False

    def list_attachments(self,filter_by_factid:str=None, format:str=FormatType.DICT):

        """
            List available attachments facts. Supported for CPD version >=4.6.5
            
            :param str filter_by_factid: (Optional) Fact id for the attachment to filter by
            :param str format: Result output format. Default to dict. Available options are in :func:`~ibm_aigov_facts_client.utils.enums.FormatType`

            A way to use me is:


            >>> model.list_attachments(format="str") # use this format if using output for `set_custom_fact()`
            >>> model.list_attachments() # get all attachment facts
            >>> model.list_attachments(filter_by_factid=<"fact_id_1">) # filter by associated fact_id_1

        """

        if self._is_cp4d and self._cp4d_version < "4.6.5":
            raise ClientError("Version mismatch: Attachment functionality is only supported in CP4D version 4.6.5 or higher. Current version of CP4D is "+self._cp4d_version)

        model_asset_id=self._asset_id
        model_container_type=self._container_type
        model_container_id= self._container_id

        url=self._get_assets_url(model_asset_id,model_container_type,model_container_id)

       
        response=requests.get(url,headers=self._get_headers())
        all_attachments=response.json().get(ATTACHMENT_TAG)
        results=[]
        if all_attachments:
            attachments=[ i for i in all_attachments if i.get('asset_type')==self._facts_type and (filter_by_factid==None or filter_by_factid==i.get("user_data").get("fact_id"))]

            for a in attachments:
                if format==FormatType.STR:
                    get_url=self._get_attachment_download_url(model_asset_id, model_container_type, model_container_id, a.get("id"), a.get("mime"), a.get("name"))
                    if self._is_cp4d and get_url:
                        get_url=self._cpd_configs["url"] + get_url
                    output_fmt = "{} - {} {}".format(a.get("name"),a.get("mime"),get_url) 
                    results.append(output_fmt)

                else:
                    attachment_dict={}
                    attachment_dict["attachment_id"]=a.get("id")
                    attachment_dict["description"]=a.get("description")
                    attachment_dict["name"]=a.get("name")
                    attachment_dict["mime"]=a.get("mime")
                    if a.get("user_data"):
                        if a.get("user_data").get("fact_id"):
                            attachment_dict["fact_id"]=a.get("user_data").get("fact_id")
                        if a.get("user_data").get("html_rendering_hint"):
                            attachment_dict["html_rendering_hint"]=a.get("user_data").get("html_rendering_hint")
                    
                    get_url=self._get_attachment_download_url(model_asset_id, model_container_type, model_container_id, a.get("id"), a.get("mime"), a.get("name"))
                    if self._is_cp4d and get_url:
                        get_url=self._cpd_configs["url"] + get_url
                    attachment_dict["url"]=get_url
                    results.append(attachment_dict)
            return results
        
        else:
            return results

    def remove_attachment(self,fact_id:str):

        """
            Remove available attachments facts for given id.Supported for CPD version >=4.6.5
            
            :param str fact_id:  Fact id of the attachment

            A way to use me is:

            >>> model.remove_attachment(fact_id=<fact id of attachment>)


        """

        if self._is_cp4d and self._cp4d_version < "4.6.5":
            raise ClientError("Version mismatch: Attachment functionality is only supported in CP4D version 4.6.5 or higher. Current version of CP4D is "+self._cp4d_version)

        model_asset_id=self._asset_id
        model_container_type=self._container_type
        model_container_id= self._container_id

        get_attachment=self.list_attachments(filter_by_factid=fact_id)
        
        if get_attachment:
            get_id=get_attachment[0].get("attachment_id")
            del_url=self._get_url_attachments(model_asset_id,model_container_type,model_container_id,get_id,action="del")
            response=requests.delete(del_url,headers=self._get_headers())
            if response.status_code==204:
                _logger.info("Deleted attachment for fact id: {} successfully".format(fact_id))
            else:
                _logger.error("Failed to delete attachment for fact id: {}. ERROR {}. {}".format(fact_id,response.status_code,response.text))
        else:
            raise ClientError("No valid attachment found related to fact id {}".format(fact_id))


    def remove_all_attachments(self): 

        """
            Remove all attachments facts for given asset. Supported for CPD version >=4.6.5


            A way to use me is:

            >>> model.remove_all_attachments()


        """
    
        if self._is_cp4d and self._cp4d_version < "4.6.5":
            raise ClientError("Version mismatch: Attachment functionality is only supported in CP4D version 4.6.5 or higher. Current version of CP4D is "+self._cp4d_version)

        model_asset_id=self._asset_id
        model_container_type=self._container_type
        model_container_id=self._container_id
        
        url=self._get_assets_url(model_asset_id,model_container_type,model_container_id)

        get_assets=requests.get(url,headers=self._get_headers())
        all_attachments=get_assets.json().get(ATTACHMENT_TAG)
        if all_attachments == None:
            raise ClientError("No attachments available to remove")
        filtered_attachment_ids=[ i.get('id') for i in all_attachments if i.get(ASSET_TYPE_TAG)==self._facts_type]
        if not filtered_attachment_ids:
            raise ClientError("No attachments available to remove")
        else:
            for id in filtered_attachment_ids:
                del_url=self._get_url_attachments(model_asset_id,model_container_type,model_container_id,id,action="del")
                response=requests.delete(del_url,headers=self._get_headers())
                if response.status_code==204:
                    _logger.info("Deleted attachment id {} successfully".format(id))
                else:
                    _logger.error("Could not delete attachment id {}. ERROR {}. {}".format(id,response.status_code,response.text))
            _logger.info("All attachments deleted successfully")
    
#============= custom log training facts===========================================

    def get_experiment(self, experiment_name:str=None)-> NotebookExperimentUtilities:

        """
            Get notebook experiment. Supported for CPD version >=4.6.4


            A way to use me is:

            >>> exp=model.get_experiment() # returns  experiment
            >>> exp=model.get_experiment(experiment_name="test") # In case notebook experiment not available, you can initiate a new one and run to add details.


        """

        get_notebook_exp_url=self._get_url_by_factstype_container(type_name=NOTEBOOK_EXP_FACTS)
        cur_data = requests.get(get_notebook_exp_url,headers=self._get_headers())

        if cur_data.status_code==200:

            cur_notebook_experiment=cur_data.json()[NOTEBOOK_EXP_FACTS]
            exp_id=cur_notebook_experiment[EXP_ID]
            exp_name=cur_notebook_experiment[EXP_NAME]
            get_exp=NotebookExperimentUtilities(self,exp_id=exp_id,exp_name=exp_name)
        
        elif cur_data.status_code==404:
            if not experiment_name:
                raise ClientError("Notebook experiment asset attribute is missing. Please provide a experiment name to create new experiment and run")
            #patch a new one
            url=self._get_assets_attributes_url()
            exp_id=uuid.uuid4().hex
            run_id=uuid.uuid4().hex
            created_date=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            exp_name=experiment_name

            body =  {
                        "name": NOTEBOOK_EXP_FACTS,
                        "entity": {EXP_ID: exp_id, EXP_NAME:exp_name,RUNS_META_NAME:[{RUN_ID:run_id,RUN_DATE:created_date,METRICS_META_NAME:[],PARAMS_META_NAME:[],TAGS_META_NAME:[]}]}
                        }

            response = requests.post(url,data=json.dumps(body), headers=self._get_headers())
            
            if response.status_code==201:
                 get_exp=NotebookExperimentUtilities(self,exp_id=exp_id,exp_name=exp_name)
                
            else:
                _logger.error("Something went wrong. ERROR {}.{}".format(response.status_code,response.text))
        else:
            raise ClientError("Failed to get experiment info. ERROR {}. {}".format(response.status_code,response.text))

        return get_exp



# utils===============================================================
    def _get_latest_run_and_item(self,data,fact_type,run_id=None):
        if run_id:
            get_latest_runs=[item for item in data if item["run_id"] == run_id]
            get_run_idx=next(idx for idx, item in enumerate(data) if item["run_id"] == run_id and item["created_date"]==max(get_latest_runs, key=(lambda item: item["created_date"]))["created_date"])
            get_run= data[get_run_idx]
            get_type_info= data[get_run_idx].get(fact_type)

        else:
            get_run_idx=max(range(len(data)), key=lambda index: data[index]['created_date'])
            get_run= data[get_run_idx]
            get_type_info= data[get_run_idx].get(fact_type)

        return get_run, get_type_info

    def _get_latest_run_idx_and_item_idx(self,data,key,fact_type,run_id=None):
        
        cur_item_idx=None
        get_run_idx=None
        key_exists=False

        if run_id:
            get_latest_runs=[item for item in data if item["run_id"] == run_id]
            if not get_latest_runs:
                raise ClientError("No run information available for run id {}".format(run_id))
            else:
                get_run_idx=next(idx for idx, item in enumerate(data) if item["run_id"] == run_id and item["created_date"]==max(get_latest_runs, key=(lambda item: item["created_date"]))["created_date"])
                get_run_type_metadata= data[get_run_idx].get(fact_type)    
                key_exists= any(item for item in get_run_type_metadata if item["key"] == key)
        else:
            get_run_idx=max(range(len(data)), key=lambda index: data[index]['created_date'])
            get_run_type_metadata= data[get_run_idx].get(fact_type)
            key_exists= any(item for item in get_run_type_metadata if item["key"] == key)
        
        is_step_required= any(STEP in item for item in get_run_type_metadata)
        
        if key_exists and is_step_required:
            raise ClientError("Runs with iterative steps are not allowed to patch (set/remove)")
        elif key_exists and not is_step_required :
            cur_item_idx=next(idx for idx, item in enumerate(get_run_type_metadata) if item["key"] == key)
        # else:
        #     raise ClientError("Failed to get info for fact id {}".format(key))
        return get_run_idx, cur_item_idx


    def _get_headers(self):
        token =  self._facts_client._authenticator.token_manager.get_token() if  ( isinstance(self._facts_client._authenticator, IAMAuthenticator) or (isinstance(self._facts_client._authenticator, CloudPakForDataAuthenticator))) else self._facts_client._authenticator.bearer_token
        iam_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer %s" % token
        }
        return iam_headers 

    def _check_if_op_enabled(self):
        url=self._cpd_configs["url"] + "/v1/aigov/model_inventory/grc/config"
        response = requests.get(url,
                    headers=self._get_headers()
                    )
        return response.json().get("grc_integration")
    
    def _get_assets_url(self,asset_id:str=None,container_type:str=None,container_id:str=None):
       

        asset_id=asset_id or self._asset_id
        container_type=container_type or self._container_type
        container_id= container_id or self._container_id

        if self._is_cp4d:
            url = self._cpd_configs["url"] + \
                '/v2/assets/' + asset_id + '?'+ container_type + '_id=' + container_id
        else:
            if get_env() == 'dev':
                url = dev_config["DEFAULT_DEV_SERVICE_URL"] + \
                    '/v2/assets/' + asset_id + '?'+ container_type + '_id=' + container_id
            elif get_env() == 'test':
                url = test_config["DEFAULT_TEST_SERVICE_URL"] + \
                    '/v2/assets/' + asset_id + '?'+ container_type + '_id=' + container_id
            else:
                url = prod_config["DEFAULT_SERVICE_URL"] + \
                    '/v2/assets/' + asset_id + '?'+ container_type + '_id=' + container_id
        return url
    
    
    def _get_fact_definition_properties(self,fact_id):
        props_by_id=None
        props_by_id_op=None
        
        if self._facts_definitions and self._facts_definitions_op:
            props=self._facts_definitions.get(PROPERTIES)
            props_by_id=props.get(fact_id)
            props_op=self._facts_definitions_op.get(PROPERTIES)
            props_by_id_op=props_op.get(fact_id)

        elif self._facts_definitions and not self._facts_definitions_op:
            props=self._facts_definitions.get(PROPERTIES)
            props_by_id=props.get(fact_id)

        elif self._facts_definitions_op and not self._facts_definitions:
            props_op=self._facts_definitions_op.get(PROPERTIES)
            props_by_id_op=props_op.get(fact_id)
        else:
            data=self._get_fact_definitions()
            if data:
                props=data.get(PROPERTIES)
                props_by_id=props.get(fact_id)

            data_op=self._get_fact_definitions(type_name=FactsType.MODEL_FACTS_USER_OP)
            if data_op:
                props_op=data_op.get(PROPERTIES)
                props_by_id_op=props_op.get(fact_id)

        
        if props_by_id and props_by_id_op:
            raise ClientError(" Fact id {} exists in both modelfacts_user and modelfacts_user_op. Please remove duplicates and try again".format(fact_id))
        # elif not props_by_id and not props_by_id_op:
        #     raise ClientError("Could not find properties for fact id {} ".format(fact_id)) 
        else:
            return props_by_id, props_by_id_op

    
    def _type_check_by_id(self,id,val):
        cur_type=None
        is_arr=None

        val_main,val_op= self._get_fact_definition_properties(id)
        cur_val=val_main or val_op

        if cur_val:
            cur_type=cur_val.get("type")
            is_arr=cur_val.get("is_array")

        if cur_type=="integer" and not isinstance(val, int):
            raise ClientError("Invalid value used for type of Integer")
        elif cur_type=="string" and not isinstance(val, str) and not is_arr:
            raise ClientError("Invalid value used for type of String")
        elif (cur_type=="string" and is_arr) and (not isinstance(val, str) and not isinstance(val, list)) :
            raise ClientError("Invalid value used for type of String. Value should be either a string or list of strings")

    def _trigger_container_move(self,asset_id:str,container_type:str=None,container_id:str=None):
        
        asset_id=asset_id or self._asset_id
        container_type= container_type or self._container_type
        container_id= container_id or self._container_id

        try:
            get_assets_url=self._get_assets_url(asset_id,container_type,container_id)
            assets_data=requests.get(get_assets_url, headers=self._get_headers())
            get_desc=assets_data.json()["metadata"].get("description")
            get_name=assets_data.json()["metadata"].get("name")
        except:
            raise ClientError("Asset details not found for asset id {}".format(asset_id))

        if get_desc:
            body= [
                {
                    "op": "add",
                    "path": "/metadata/description",
                    "value": get_desc +' '
                }
                ]
        else:
            body= [
                {
                    "op": "add",
                    "path": "/metadata/description",
                    "value": get_name
                }
                ]
        response = requests.patch(get_assets_url,data=json.dumps(body), headers=self._get_headers())
        
        if response.status_code ==200:
           return response.status_code
        else:
            raise ClientError("Could not update asset container. ERROR {}. {}".format(response.status_code,response.text))


    
    def _get_mime(self,file):
        # pip install python-magic
        # On a Mac you may also have to run a "brew install libmagic"
        import magic
        mime = magic.Magic(mime=True)
        magic_mimetype_result = mime.from_file(file) 
        # sometimes we need to post-correct where the magic result is just not
        if file.endswith(".csv") and not magic_mimetype_result.endswith("/csv"): 
            return "text/csv"
        if file.endswith(".html") and not magic_mimetype_result.endswith("/html"): 
            return "text/html"
        return magic_mimetype_result
    
    
    def _get_assets_attributes_url(self):

            if self._is_cp4d:
                url = self._cpd_configs["url"] + \
                    '/v2/assets/' + self._asset_id + "/attributes?" + self._container_type + "_id=" + self._container_id
            else:
                if get_env() == 'dev':
                    url = dev_config["DEFAULT_DEV_SERVICE_URL"] + \
                        '/v2/assets/' + self._asset_id + "/attributes?" + self._container_type + "_id=" + self._container_id
                elif get_env() == 'test':
                    url = test_config["DEFAULT_TEST_SERVICE_URL"] + \
                        '/v2/assets/' + self._asset_id + "/attributes?" + self._container_type + "_id=" + self._container_id
                else:
                    url = prod_config["DEFAULT_SERVICE_URL"] + \
                        '/v2/assets/'+ self._asset_id + "/attributes?" + self._container_type + "_id=" + self._container_id

            return url

    def _get_url_by_factstype_container(self,type_name=None):

        facts_type= type_name or self._facts_type
        
        if self._is_cp4d:
           
           url = self._cpd_configs["url"] + \
                '/v2/assets/' + self._asset_id + "/attributes/" + \
            facts_type + "?" + self._container_type + "_id=" + self._container_id
        
        else:

            if get_env() == 'dev':
                url = dev_config["DEFAULT_DEV_SERVICE_URL"] + \
                    '/v2/assets/' + self._asset_id + "/attributes/" + \
                facts_type + "?" + self._container_type + "_id=" + self._container_id
            elif get_env() == 'test':
                url = test_config["DEFAULT_TEST_SERVICE_URL"] + \
                    '/v2/assets/' + self._asset_id + "/attributes/" + \
                facts_type + "?" + self._container_type + "_id=" + self._container_id
            else:
                url = prod_config["DEFAULT_SERVICE_URL"] + \
                    '/v2/assets/'+ self._asset_id + "/attributes/" + \
                facts_type + "?" + self._container_type + "_id=" + self._container_id
        
        return url

    def _get_url_sysfacts_container(self,asset_id:str=None, container_type:str=None, container_id: str=None,key:str=FactsType.MODEL_FACTS_SYSTEM):

        asset_id=asset_id or self._asset_id
        container_type=container_type or self._container_type
        container_id=container_id or self._container_id
        
        if self._is_cp4d:
                url = self._cpd_configs["url"] + \
                    '/v2/assets/' + asset_id + "/attributes/" + \
                key + "?" + container_type + "_id=" + container_id

        else:
            if get_env() == 'dev':
                url = dev_config["DEFAULT_DEV_SERVICE_URL"] + \
                    '/v2/assets/' + asset_id + "/attributes/" + \
                key + "?" + container_type + "_id=" + container_id
            elif get_env() == 'test':
                url = test_config["DEFAULT_TEST_SERVICE_URL"] + \
                    '/v2/assets/' + asset_id + "/attributes/" + \
                key + "?" + container_type + "_id=" + container_id
            else:
                url = prod_config["DEFAULT_SERVICE_URL"] + \
                    '/v2/assets/'+ asset_id + "/attributes/" + \
                key + "?" + container_type + "_id=" + container_id
        
        return url
    
    def _get_url_space(self,space_id:str):
        
        if self._is_cp4d:
                url = self._cpd_configs["url"] + \
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

    def _get_url_attachments(self,asset_id:str,container_type:str, container_id:str,attachment_id:str=None,mimetype:str=None,action:str=None):

        if action=="del":
            if self._is_cp4d:
                    url = self._cpd_configs["url"] + \
                        '/v2/assets/' + asset_id + '/attachments/' + attachment_id + '?'+ container_type + '_id=' + container_id
            else:
                if get_env() == 'dev':
                    url = dev_config["DEFAULT_DEV_SERVICE_URL"] + \
                        '/v2/assets/' + asset_id + '/attachments/' + attachment_id + '?'+ container_type + '_id=' + container_id 
                elif get_env() == 'test':
                    url = test_config["DEFAULT_TEST_SERVICE_URL"] + \
                        '/v2/assets/' + asset_id + '/attachments/' + attachment_id + '?'+ container_type + '_id=' + container_id 
                else:
                    url = prod_config["DEFAULT_SERVICE_URL"] + \
                        '/v2/assets/' + asset_id + '/attachments/' + attachment_id + '?'+ container_type + '_id=' + container_id 


        elif attachment_id and mimetype and action=="get":
            if self._is_cp4d:
                    url = self._cpd_configs["url"] + \
                        '/v2/assets/' + asset_id + '/attachments/' + attachment_id + '?'+ container_type + '_id=' + container_id + '&response-content-type=' + mimetype
            else:
                if get_env() == 'dev':
                    url = dev_config["DEFAULT_DEV_SERVICE_URL"] + \
                        '/v2/assets/' + asset_id + '/attachments/' + attachment_id + '?'+ container_type + '_id=' + container_id + '&response-content-type=' + mimetype
                elif get_env() == 'test':
                    url = test_config["DEFAULT_TEST_SERVICE_URL"] + \
                        '/v2/assets/' + asset_id + '/attachments/' + attachment_id + '?'+ container_type + '_id=' + container_id + '&response-content-type=' + mimetype
                else:
                    url = prod_config["DEFAULT_SERVICE_URL"] + \
                        '/v2/assets/' + asset_id + '/attachments/' + attachment_id + '?'+ container_type + '_id=' + container_id + '&response-content-type=' + mimetype

        
        elif attachment_id and action=="complete":
            if self._is_cp4d:
                    url = self._cpd_configs["url"] + \
                        '/v2/assets/' + asset_id + '/attachments/' + attachment_id + '/complete?'+ container_type + '_id=' + container_id
            else:
                if get_env() == 'dev':
                    url = dev_config["DEFAULT_DEV_SERVICE_URL"] + \
                        '/v2/assets/' + asset_id + '/attachments/' + attachment_id + '/complete?'+ container_type + '_id=' + container_id
                elif get_env() == 'test':
                    url = test_config["DEFAULT_TEST_SERVICE_URL"] + \
                         '/v2/assets/' + asset_id + '/attachments/' + attachment_id + '/complete?'+ container_type + '_id=' + container_id
                else:
                    url = prod_config["DEFAULT_SERVICE_URL"] + \
                         '/v2/assets/' + asset_id + '/attachments/' + attachment_id + '/complete?'+ container_type + '_id=' + container_id
        
        else:
            if self._is_cp4d:
                    url = self._cpd_configs["url"] + \
                        '/v2/assets/' + asset_id + '/attachments?'+ container_type + '_id=' + container_id 
            else:
                if get_env() == 'dev':
                    url = dev_config["DEFAULT_DEV_SERVICE_URL"] + \
                        '/v2/assets/' + asset_id + '/attachments?'+ container_type + '_id=' + container_id
                elif get_env() == 'test':
                    url = test_config["DEFAULT_TEST_SERVICE_URL"] + \
                        '/v2/assets/' + asset_id + '/attachments?'+ container_type + '_id=' + container_id
                else:
                    url = prod_config["DEFAULT_SERVICE_URL"] + \
                        '/v2/assets/' + asset_id + '/attachments?'+ container_type + '_id=' + container_id
        return url



    def _get_attachment_download_url(self, asset_id, container_type, container_id, attachment_id, mimetype, filename):
        
        url = self._get_url_attachments(asset_id,container_type,container_id,attachment_id,mimetype,action="get")
        if mimetype.startswith("image/") or mimetype.startswith("application/pdf") or mimetype.startswith("text/html") :
            url += "&response-content-disposition=inline;filename=" + filename

        else :
            url += "&response-content-disposition=attachment;filename=" + filename

        response=requests.get(url, headers=self._get_headers())
        download_url = response.json().get("url")
        return download_url


