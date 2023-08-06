
import logging
import os
import json
import collections
import itertools
import ibm_aigov_facts_client._wrappers.requests as requests

from typing import Optional

from typing import BinaryIO, Dict, List, TextIO, Union,Any
from ibm_aigov_facts_client.factsheet import assets 
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator,CloudPakForDataAuthenticator
from ibm_aigov_facts_client.utils.enums import AssetContainerSpaceMap, AssetContainerSpaceMapExternal,ContainerType, FactsType, ModelEntryContainerType, AllowedDefinitionType,FormatType, RenderingHints
from ibm_aigov_facts_client.utils.utils import validate_enum,validate_type,STR_TYPE
from ibm_aigov_facts_client.factsheet.asset_utils_me import ModelEntryUtilities
from ibm_cloud_sdk_core.utils import  convert_model


from ibm_aigov_facts_client.utils.config import *
from ibm_aigov_facts_client.utils.client_errors import *
from ibm_aigov_facts_client.utils.constants import *
from ibm_aigov_facts_client.utils.metrics_utils import convert_metric_value_to_float_if_possible


_logger = logging.getLogger(__name__) 


class NotebookExperimentRunsUtilities:

    """
        Model notebook experiment runs utilities. Running `client.assets.model()` makes all methods in NotebookExperimentUtilities object available to use.
    
    """
   
    def __init__(self,assets_client:'assets.Assets',cur_exp_runs=None,run_id:str=None,run_idx:str=None,run_info=None,facts_type: str=NOTEBOOK_EXP_FACTS) -> None:


        self._facts_type=facts_type
        
        self._cur_exp_runs=cur_exp_runs
        self._run_id=run_id
        self._run_idx=run_idx
        self._run_id=run_info.get(RUN_ID)
        self._run_date=run_info.get(RUN_DATE)
        self._metrics=run_info.get(METRICS_META_NAME)
        self._params=run_info.get(PARAMS_META_NAME)
        self._tags=run_info.get(TAGS_META_NAME)

        self._assets_client=assets_client
        self._facts_client=self._assets_client._facts_client
        self._is_cp4d=self._assets_client._is_cp4d
        self._external_model=self._assets_client._external_model
        self._asset_id = self._assets_client._asset_id
        self._container_type=self._assets_client._container_type
        self._container_id=self._assets_client._container_id


        if self._is_cp4d:
            self._cpd_configs=self._assets_client._cpd_configs

        self._get_notebook_exp_url=self._get_url_by_factstype_container(type_name=NOTEBOOK_EXP_FACTS)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, '_run_id') and self._run_id is not None:
            _dict['run_id'] = self._run_id
        if hasattr(self, '_run_date') and self._run_date is not None:
            _dict['run_date'] = self._run_date
        if hasattr(self, '_metrics') and self._metrics is not None:
            _dict['metrics'] = self._metrics
        if hasattr(self, '_params') and self._params is not None:
            _dict['params'] = self._params
        if hasattr(self, '_tags') and self._tags is not None:
            _dict['tags'] = self._tags
        
        return _dict
  
    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()
    
    def get_info(self):
        """
            Get run info. Supported for CPD version >=4.6.4


            A way to use me is:

            >>> run=exp.get_run() # returns latest if run_id is not given
            >>> run.get_info()


        """
        return self._to_dict()


    def set_custom_metric(self, metric_id:str, value:float)-> None:
        
        """ Set model training metric

        :param metric_id: Metric key name
        :type metric_id: str
        :param value: Metric value
        :type value: float
        :raises ClientError: Raises client error for exceptions
        :return: None


        A way to use me is:

        >>> model.set_custom_metric(metric_key=<key>,value=<value>)

        """

        if not self._cur_exp_runs:
            raise ClientError("No associated runs info found under notebook experiment")
        else:
            metric_idx=self._get_item_idx(self._metrics,metric_id)
            
            if metric_idx is None:
                cur_len=(0 if len(self._metrics)==0 else len(self._metrics))
                                
            if self._run_idx is not None  and metric_idx is not None:
                body = [
                    {
                        "op": REPLACE, 
                        "path": "/{}/{}/{}/{}/value".format(RUNS_META_NAME,self._run_idx,METRICS_META_NAME,metric_idx),
                        "value": value
                    }
                    ]
            else:
                
                body = [
                        {
                            "op": ADD, 
                            "path": "/{}/{}/{}/{}".format(RUNS_META_NAME,self._run_idx,METRICS_META_NAME,cur_len),
                            "value": {"key":metric_id,"value":value}
                        }
                        ]

            response = requests.patch(self._get_notebook_exp_url, data=json.dumps(body), headers=self._get_headers()) 
            if response.status_code==200:
                _logger.info("Set custom metric {} successfully to value {}".format(metric_id,value))
                self._metrics= self._refresh_cur_run(METRICS_META_NAME,self._run_id)
            else:
                raise ClientError("Failed to set custom metric {}. ERROR {}.{}".format(metric_id,response.status_code,response.text))   

    def set_custom_metrics(self, metrics_dict: Dict[str, Any])-> None:
        
        """ Set model training metrics

        :param metrics_dict: Metric key,value pairs.
        :type metrics_dict: dict
        :raises ClientError: Raises client error for exceptions
        :return: None

        A way to use me is:

        >>> model.set_custom_metrics(metrics_dict={"training_score":0.955, "training_mse":0.911})

        """
        final_body=[]


        if not self._cur_exp_runs:
            raise ClientError("No associated runs info found under notebook experiment")
        else:
            
            for key, val in metrics_dict.items(): 
                metric_value= convert_metric_value_to_float_if_possible(val)
                
                metric_idx=self._get_item_idx(self._metrics,key)
            
                if metric_idx is None:
                    cur_len=(0 if len(self._metrics)==0 else len(self._metrics))
                
                if self._run_idx is not None  and metric_idx is not None:
                    body = {
                                "op": REPLACE, 
                                "path": "/{}/{}/{}/{}/value".format(RUNS_META_NAME,self._run_idx,METRICS_META_NAME,metric_idx),
                                "value": metric_value
                            }
                            
                else:
                    body = {
                                "op": ADD, 
                                "path": "/{}/{}/{}/{}".format(RUNS_META_NAME,self._run_idx,METRICS_META_NAME,cur_len),
                                "value": {"key":key,"value":metric_value}
                            }
                final_body.append(body)
                            

            response = requests.patch(self._get_notebook_exp_url, data=json.dumps(final_body), headers=self._get_headers()) 
            if response.status_code==200:
                _logger.info("Set custom metrics {} successfully to values {}".format(list(metrics_dict.keys()),list(metrics_dict.values())))
                self._metrics= self._refresh_cur_run(METRICS_META_NAME,self._run_id)
            else:
                raise ClientError("Failed to set custom metrics {}. ERROR {}.{}".format(key,response.status_code,response.text))   
                    

    def set_custom_param(self, param_id:str, value:str)-> None:
        
        """ Set model training param

        :param param_id: Param key name
        :type param_id: str
        :param value: Param value
        :type value: str
        :raises ClientError: Raises client error for exceptions
        :return: None

        A way to use me is:

        >>> model.set_custom_param(param_id=<key>,value=<value>)

        """

        if not self._cur_exp_runs:
            raise ClientError("No associated runs info found under notebook experiment")
        else:

            param_idx=self._get_item_idx(self._params,param_id)
            
            if param_idx is None:
                cur_len=(0 if len(self._params)==0 else len(self._params))
                                
            if self._run_idx is not None  and param_idx is not None:
                body = [
                    {
                        "op": REPLACE, 
                        "path": "/{}/{}/{}/{}/value".format(RUNS_META_NAME,self._run_idx,PARAMS_META_NAME,param_idx),
                        "value": value
                    }
                    ]
            else:
                
                body = [
                        {
                            "op": ADD, 
                            "path": "/{}/{}/{}/{}".format(RUNS_META_NAME,self._run_idx,PARAMS_META_NAME,cur_len),
                            "value": {"key":param_id,"value":value}
                        }
                        ]

            response = requests.patch(self._get_notebook_exp_url, data=json.dumps(body), headers=self._get_headers()) 
            if response.status_code==200:
                _logger.info("Set custom param {} successfully to value {}".format(param_id,value))
                self._params= self._refresh_cur_run(PARAMS_META_NAME,self._run_id)
            else:
                raise ClientError("Failed to set custom param {}. ERROR {}.{}".format(param_id,response.status_code,response.text))   

    def set_custom_params(self, params_dict: Dict[str, Any])-> None:
        
        """ Set model training params

        :param params_dict: Params key,value pairs.
        :type params_dict: dict
        :raises ClientError: Raises client error for exceptions
        :return: None

        A way to use me is:

        >>> model.set_custom_params(params_dict={"num_class":3,"early_stopping_rounds":10})


        """

        final_body=[]


        if not self._cur_exp_runs:
            raise ClientError("No associated runs info found under notebook experiment")
        else:
            
            for key, val in params_dict.items(): 
                param_value= convert_metric_value_to_float_if_possible(val)
                
                param_idx=self._get_item_idx(self._params,key)
            
                if param_idx is None:
                    cur_len=(0 if len(self._params)==0 else len(self._params))
                
                if self._run_idx is not None  and param_idx is not None:
                    body = {
                                "op": REPLACE, 
                                "path": "/{}/{}/{}/{}/value".format(RUNS_META_NAME,self._run_idx,PARAMS_META_NAME,param_idx),
                                "value": param_value
                            }
                            
                else:
                    body = {
                                "op": ADD, 
                                "path": "/{}/{}/{}/{}".format(RUNS_META_NAME,self._run_idx,PARAMS_META_NAME,cur_len),
                                "value": {"key":key,"value":param_value}
                            }
                final_body.append(body)
                            

            response = requests.patch(self._get_notebook_exp_url, data=json.dumps(final_body), headers=self._get_headers()) 
            if response.status_code==200:
                _logger.info("Set custom params {} successfully to values {}".format(list(params_dict.keys()),list(params_dict.values())))
                self._params= self._refresh_cur_run(PARAMS_META_NAME,self._run_id)
            else:
                raise ClientError("Failed to set custom params {}. ERROR {}.{}".format(key,response.status_code,response.text)) 


    def set_custom_tag(self, tag_id:str, value:str)-> None:
        
        """ Set model training tag

        :param tag_id: Tag key name
        :type tag_id: str
        :param value: Tag value
        :type value: str
        :raises ClientError: Raises client error for exceptions
        :return: None

        A way to use me is:

        >>> model.set_custom_tag(tag_id=<key>,value=<value>)

        """

        if not self._cur_exp_runs:
            raise ClientError("No associated runs info found under notebook experiment")
        else:
            tag_idx=self._get_item_idx(self._tags,tag_id)
            
            if tag_idx is None:
                cur_len=(0 if len(self._tags)==0 else len(self._tags))
                                
            if self._run_idx is not None  and tag_idx is not None:
                body = [
                    {
                        "op": REPLACE, 
                        "path": "/{}/{}/{}/{}/value".format(RUNS_META_NAME,self._run_idx,TAGS_META_NAME,tag_idx),
                        "value": value
                    }
                    ]
            else:
                
                body = [
                        {
                            "op": ADD, 
                            "path": "/{}/{}/{}/{}".format(RUNS_META_NAME,self._run_idx,TAGS_META_NAME,cur_len),
                            "value": {"key":tag_id,"value":value}
                        }
                        ]

            response = requests.patch(self._get_notebook_exp_url, data=json.dumps(body), headers=self._get_headers()) 
            if response.status_code==200:
                _logger.info("Set custom tag {} successfully to value {}".format(tag_id,value))
                self._tags= self._refresh_cur_run(TAGS_META_NAME,self._run_id)
            else:
                raise ClientError("Failed to set custom tag {}. ERROR {}.{}".format(tag_id,response.status_code,response.text))   

    def set_custom_tags(self, tags_dict: Dict[str, Any])-> None:
        
        """ Set model training tags

        :param tags_dict: Tags key,value pairs.
        :type tags_dict: dict
        :raises ClientError: Raises client error for exceptions
        :return: None

        A way to use me is:

        >>> model.set_custom_tags(tags_dict={"tag1":<value>,"tag2":<value>})

        """

        final_body=[]


        if not self._cur_exp_runs:
            raise ClientError("No associated runs info found under notebook experiment")
        else:
            
            for key, val in tags_dict.items(): 
                tag_value= convert_metric_value_to_float_if_possible(val)
                
                tag_idx=self._get_item_idx(self._tags,key)
            
                if tag_idx is None:
                    cur_len=(0 if len(self._tags)==0 else len(self._tags))
                
                if self._run_idx is not None  and tag_idx is not None:
                    body = {
                                "op": REPLACE, 
                                "path": "/{}/{}/{}/{}/value".format(RUNS_META_NAME,self._run_idx,TAGS_META_NAME,tag_idx),
                                "value": tag_value
                            }
                            
                else:
                    body = {
                                "op": ADD, 
                                "path": "/{}/{}/{}/{}".format(RUNS_META_NAME,self._run_idx,TAGS_META_NAME,cur_len),
                                "value": {"key":key,"value":tag_value}
                            }
                final_body.append(body)
                            

            response = requests.patch(self._get_notebook_exp_url, data=json.dumps(final_body), headers=self._get_headers()) 
            if response.status_code==200:
                _logger.info("Set custom tags {} successfully to values {}".format(list(tags_dict.keys()),list(tags_dict.values())))
                self._tags= self._refresh_cur_run(TAGS_META_NAME,self._run_id)
            else:
                raise ClientError("Failed to set custom tags {}. ERROR {}.{}".format(key,response.status_code,response.text)) 
            
    
    def get_custom_metric(self, metric_id: str)->List:

        """
            Get custom metric value by id

            :param str metric_id: Custom metric id to retrieve.
            :rtype: list

            A way you might use me is:

            >>> model.get_custom_metric_by_id(metric_id="<metric_id>")

        """

        self._metrics= self._refresh_cur_run(METRICS_META_NAME,self._run_id)
        is_exists= any(item for item in self._metrics if item["key"] == metric_id)
        is_step_available= any(STEP in item for item in self._metrics)

        if not is_exists:
            if self._run_id:
                raise ClientError("Could not find value of metric_id {} in run {}".format(metric_id,self._run_id))
            else:
                raise ClientError("Could not find value of metric_id {}".format(metric_id))
        else:
            cur_item=[i for i in self._metrics if i["key"]==metric_id]
            final_output=[]
            if cur_item and is_step_available:
                final_output=[{row['key']: row['value'],STEP:row['step']} for row in cur_item]
            elif cur_item and not is_step_available :
                final_output.append({row['key']: row['value'] for row in cur_item})
            else:
                raise ClientError("Failed to get information for metric id {}".format(metric_id))
        return final_output

    def get_custom_metrics(self,metric_ids: List[str]=None)->List:

        """
            Get all logged custom metrics

            :param list metrics_ids: (Optional) Metrics ids to get. If not provided, returns all metrics available for the latest run 
            :rtype: list[dict]

            A way you might use me is:

            >>> model.get_custom_metrics() # uses last logged run
            >>> model.get_custom_metrics(metric_ids=["id1","id2"]) # uses last logged run

        """
            
        self._metrics= self._refresh_cur_run(METRICS_META_NAME,self._run_id)
        is_step_available= any(STEP in item for item in self._metrics)

        if not self._metrics:
            if self._run_id:
                raise ClientError("Could not find metrics information in run {}".format(self._run_id))
            else:
                raise ClientError("Could not find metrics information")
        else:
            final_result=[]
            if metric_ids:
                for item in metric_ids:
                    get_results= [i for i in self._metrics if i["key"]==item]
                    if get_results and is_step_available:
                        format_result=[{row['key']: row['value'],"step":row['step']} for row in get_results]
                        final_result.append(format_result)
                    elif get_results and not is_step_available:
                        format_result={row['key']: row['value'] for row in get_results}
                        final_result.append(format_result)
                    else:
                        _logger.info("Escaping metric id {}. Failed to get metric information.".format(item))
                
            else:
                if self._metrics and is_step_available:
                    final_result=[{row['key']: row['value'],"step":row['step']} for row in self._metrics]
                elif self._metrics and not is_step_available: 
                    format_result={row['key']: row['value'] for row in self._metrics}
                    final_result.append(format_result)
                else:
                    raise ClientError("Failed to get metrics information")
            
            return final_result

    def get_custom_param(self, param_id: str)->Dict:

        """
            Get custom param value by id

            :param str param_id: Custom param id to retrieve.
            :rtype: list

            A way you might use me is:

            >>> model.get_custom_param(param_id="<param_id>")

        """

        self._params= self._refresh_cur_run(PARAMS_META_NAME,self._run_id)
        is_exists= any(item for item in self._params if item["key"] == param_id)

        if not is_exists:
            if self._run_id:
                raise ClientError("Could not find value of param_id {} in run {}".format(param_id,self._run_id))
            else:
                raise ClientError("Could not find value of param_id {}".format(param_id))
        else:
            cur_item=[i for i in self._params if i["key"]==param_id]
            final_val=None
            if cur_item:
                final_val={row['key']: row['value'] for row in cur_item}
                return final_val
            else:
                raise ClientError("Failed to get information for param id {}".format(param_id))

    def get_custom_params(self,param_ids: List[str]=None)->List:

        """
            Get all logged params

            :param list param_ids: (Optional) Params ids to get. If not provided, returns all params available for the latest run 
            :rtype: list[dict]

            A way you might use me is:

            >>> model.get_custom_params() # uses last logged run
            >>> model.get_custom_params(param_ids=["id1","id2"]) # uses last logged run

        """ 

        self._params= self._refresh_cur_run(PARAMS_META_NAME,self._run_id)
        if not self._params:
            if self._run_id:
                raise ClientError("Could not find params information in run {}".format(self._run_id))
            else:
                raise ClientError("Could not find params information")
        else:
            final_result=[]
            if param_ids:
                for item in param_ids:
                    get_results= [i for i in self._params if i["key"]==item]
                    if get_results:
                        format_result={row['key']: row['value'] for row in get_results}
                        final_result.append(format_result)
                    else:
                        _logger.info("Escaping param id {}. Failed to get param information.".format(item))
                
            else:
                if self._params:
                    format_result={row['key']: row['value'] for row in self._params}
                    final_result.append(format_result)
                else:
                    raise ClientError("Failed to get params information")
            
            return final_result


    def get_custom_tag(self, tag_id: str)->Dict:

        """
            Get custom tag value by id

            :param str tag_id: Custom tag id to retrieve.
            :rtype: dict

            A way you might use me is:

            >>> model.get_custom_tag(tag_id="<tag_id>")

        """

        self._tags= self._refresh_cur_run(TAGS_META_NAME,self._run_id)
        is_exists= any(item for item in self._tags if item["key"] == tag_id)

        if not is_exists:
            if self._run_id:
                raise ClientError("Could not find value of tag_id {} in run {}".format(tag_id,self._run_id))
            else:
                raise ClientError("Could not find value of tag_id {}".format(tag_id))
        else:
            cur_item=[i for i in self._tags if i["key"]==tag_id]
            final_val=None
            if cur_item:
                final_val={row['key']: row['value'] for row in cur_item}
                return final_val
            else:
                raise ClientError("Failed to get information for tag id {}".format(tag_id))

    def get_custom_tags(self,tag_ids: List[str]=None)->List:

        """
            Get all logged tags

            :param list tag_ids: (Optional) Tags ids to get. If not provided, returns all tags available for the latest run 
            :rtype: list[dict]

            A way you might use me is:

            >>> model.get_custom_tags() # uses last logged run
            >>> model.get_custom_tags(tag_ids=["id1","id2"]) # uses last logged run

        """
        
        self._tags= self._refresh_cur_run(TAGS_META_NAME,self._run_id)
        if not self._tags:
            if self._run_id:
                raise ClientError("Could not find tags information in run {}".format(self._run_id))
            else:
                raise ClientError("Could not find tags information")
        else:
            final_result=[]
            if tag_ids:
                for item in tag_ids:
                    get_results= [i for i in self._tags if i["key"]==item]
                    if get_results:
                        format_result={row['key']: row['value'] for row in get_results}
                        final_result.append(format_result)
                    else:
                        _logger.info("Escaping tag id {}. Failed to get tag information.".format(item))
                
            else:
                if self._tags:
                    format_result={row['key']: row['value'] for row in self._tags}
                    final_result.append(format_result)
                else:
                    raise ClientError("Failed to get tags information")
            
            return final_result  

    def remove_custom_metric(self, metric_id: str)->None:

        """
            Remove metric by id

            :param str metric_id: Metric id to remove.

            A way you might use me is:

            >>> model.remove_custom_metric(metric_id=<metric_id>)


        """

        if not self._cur_exp_runs:
            raise ClientError("No associated runs info found under notebook experiment")
        else:
            metric_idx=self._get_item_idx(self._metrics,metric_id)
            
            if self._run_idx is not None and metric_idx is not None:
                    body = [
                        {
                            "op": REMOVE, 
                            "path": "/{}/{}/{}/{}".format(RUNS_META_NAME,self._run_idx,METRICS_META_NAME,metric_idx)
                        }
                        ]
            else:
                raise ClientError("Failed to get metric details for id {}".format(metric_id))

            response = requests.patch(self._get_notebook_exp_url, data=json.dumps(body), headers=self._get_headers()) 
            if response.status_code==200:
                if self._run_id:
                    _logger.info("Deleted metric {} successfully from run {}".format(metric_id,self._run_id))     
                else:
                    _logger.info("Deleted metric {} successfully".format(metric_id))
                self._metrics= self._refresh_cur_run(METRICS_META_NAME,self._run_id)
            else:
                raise ClientError("Failed to delete metric {}. ERROR {}.{}".format(metric_id,response.status_code,response.text))   

            

    def remove_custom_metrics(self, metric_ids:List[str])->None:

        """
            Remove multiple metrics

            :param list metric_ids: Metric ids to remove from run.

            A way you might use me is:

            >>> model.remove_custom_metrics(metric_ids=["id1","id2"]) #uses last logged run


        """
        
        final_body=[]

        if not self._cur_exp_runs:
            raise ClientError("No associated runs info found under notebook experiment")
        else:
            for key in metric_ids:
                metric_idx=self._get_item_idx(self._metrics,key)
                if self._run_idx is not None and metric_idx is not None:
                    body = {
                                "op": REMOVE, 
                                "path": "/{}/{}/{}/{}".format(RUNS_META_NAME,self._run_idx,METRICS_META_NAME,metric_idx)
                            }
                            
                    final_body.append(body)
                else:
                    _logger.info("Escaping metric {}. Failed to find metric details".format(key))
                    metric_ids.remove(key)

            response = requests.patch(self._get_notebook_exp_url, data=json.dumps(final_body), headers=self._get_headers()) 
            if response.status_code==200:
                if self._run_id:
                    _logger.info("Deleted metrics {} successfully from run {}".format(metric_ids,self._run_id))
                else:
                    _logger.info("Deleted metrics {} successfully from latest available run".format(metric_ids))
                self._metrics= self._refresh_cur_run(METRICS_META_NAME,self._run_id)
            else:
                raise ClientError("Failed to delete custom metrics {}. ERROR {}.{}".format(key,response.status_code,response.text))   
                    
    def remove_custom_param(self, param_id: str)->None:

        """
            Remove param by id

            :param str param_id: Param id to remove.

            A way you might use me is:

            >>> model.remove_custom_param(param_id=<param_id>)

        """

        if not self._cur_exp_runs:
            raise ClientError("No associated runs info found under notebook experiment")
        else:
            param_idx=self._get_item_idx(self._params,param_id)
            
            if self._run_idx is not None and param_idx is not None:
                    body = [
                        {
                            "op": REMOVE, 
                            "path": "/{}/{}/{}/{}".format(RUNS_META_NAME,self._run_idx,PARAMS_META_NAME,param_idx)
                        }
                        ]
            else:
                raise ClientError("Failed to get param details for id {}".format(param_id))

            response = requests.patch(self._get_notebook_exp_url, data=json.dumps(body), headers=self._get_headers()) 
            if response.status_code==200:
                if self._run_id:
                    _logger.info("Deleted param {} successfully from run {}".format(param_id,self._run_id))     
                else:
                    _logger.info("Deleted param {} successfully".format(param_id))
                self._params= self._refresh_cur_run(PARAMS_META_NAME,self._run_id)
            else:
                raise ClientError("Failed to delete param {}. ERROR {}.{}".format(param_id,response.status_code,response.text))   

            

    def remove_custom_params(self, param_ids:List[str])->None:

        """
            Remove multiple params

            :param list param_ids: Param ids to remove from run.

            A way you might use me is:

            >>> model.remove_custom_params(param_ids=["id1","id2"])

        """
        
        final_body=[]

        if not self._cur_exp_runs:
            raise ClientError("No associated runs info found under notebook experiment")
        else:
            for key in param_ids:
                param_idx=self._get_item_idx(self._params,key)
                if self._run_idx is not None and param_idx is not None:
                    body = {
                                "op": REMOVE, 
                                "path": "/{}/{}/{}/{}".format(RUNS_META_NAME,self._run_idx,PARAMS_META_NAME,param_idx)
                            }
                            
                    final_body.append(body)
                else:
                    _logger.info("Escaping param {}. Failed to find param details".format(key))
                    param_ids.remove(key)

            response = requests.patch(self._get_notebook_exp_url, data=json.dumps(final_body), headers=self._get_headers()) 
            if response.status_code==200:
                if self._run_id:
                    _logger.info("Deleted params {} successfully from run {}".format(param_ids,self._run_id))
                else:
                    _logger.info("Deleted params {} successfully from latest available run".format(param_ids))
                self._params= self._refresh_cur_run(PARAMS_META_NAME,self._run_id)
            else:
                raise ClientError("Failed to delete custom params {}. ERROR {}.{}".format(key,response.status_code,response.text))        
    
    
    def remove_custom_tag(self, tag_id: str)->None:
        
        """
            Remove tag by id

            :param str tag_id: Tag id to remove.
            
            A way you might use me is:

            >>> model.remove_custom_tag(tag_id=<tag_id>)

        """

        if not self._cur_exp_runs:
            raise ClientError("No associated runs info found under notebook experiment")
        else:
            tag_idx=self._get_item_idx(self._tags,tag_id)
            
            if self._run_idx is not None and tag_idx is not None:
                    body = [
                        {
                            "op": REMOVE, 
                            "path": "/{}/{}/{}/{}".format(RUNS_META_NAME,self._run_idx,TAGS_META_NAME,tag_idx)
                        }
                        ]
            else:
                raise ClientError("Failed to get tag details for id {}".format(tag_id))

            response = requests.patch(self._get_notebook_exp_url, data=json.dumps(body), headers=self._get_headers()) 
            if response.status_code==200:
                if self._run_id:
                    _logger.info("Deleted tag {} successfully from run {}".format(tag_id,self._run_id))     
                else:
                    _logger.info("Deleted tag {} successfully".format(tag_id))
                self._tags= self._refresh_cur_run(TAGS_META_NAME,self._run_id)
            else:
                raise ClientError("Failed to delete param {}. ERROR {}.{}".format(tag_id,response.status_code,response.text))   

            

    def remove_custom_tags(self, tag_ids:List[str])->None:

        """
            Remove multiple tags

            :param list tag_ids: Tag ids to remove from run.

            A way you might use me is:

            >>> model.remove_custom_tags(tag_ids=["id1","id2"])

        """
        
        final_body=[]

        if not self._cur_exp_runs:
            raise ClientError("No associated runs info found under notebook experiment")
        else:
            for key in tag_ids:
                tag_idx=self._get_item_idx(self._tags,key)
                if self._run_idx is not None and tag_idx is not None:
                    body = {
                                "op": REMOVE, 
                                "path": "/{}/{}/{}/{}".format(RUNS_META_NAME,self._run_idx,TAGS_META_NAME,tag_idx)
                            }
                            
                    final_body.append(body)
                else:
                    _logger.info("Escaping tag {}. Failed to find tag details".format(key))
                    tag_ids.remove(key)

            response = requests.patch(self._get_notebook_exp_url, data=json.dumps(final_body), headers=self._get_headers()) 
            if response.status_code==200:
                if self._run_id:
                    _logger.info("Deleted tags {} successfully from run {}".format(tag_ids,self._run_id))
                else:
                    _logger.info("Deleted tags {} successfully from latest available run".format(tag_ids))
                self._tags= self._refresh_cur_run(TAGS_META_NAME,self._run_id)
            else:
                raise ClientError("Failed to delete custom tags {}. ERROR {}.{}".format(key,response.status_code,response.text))  
            
    def _get_item_idx(self,data,key):
        
        cur_item_idx=None
        key_exists=False

        if self._run_id:  
                key_exists= any(item for item in data if item["key"] == key)
        else:
            key_exists= any(item for item in data if item["key"] == key)
        
        is_step_required= any(STEP in item for item in data)
        
        if key_exists and is_step_required:
            raise ClientError("Runs with iterative steps are not allowed to patch (set/remove)")
        elif key_exists and not is_step_required :
            cur_item_idx=next(idx for idx, item in enumerate(data) if item["key"] == key)

        return  cur_item_idx

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
    
    def _get_current_notebook_experiment_runs(self): 
        get_notebook_exp_url=self._get_url_by_factstype_container(type_name=NOTEBOOK_EXP_FACTS)
        cur_data = requests.get(get_notebook_exp_url,headers=self._get_headers())
        if cur_data.status_code==200:
            notebook_experiment_runs=cur_data.json()[NOTEBOOK_EXP_FACTS].get(RUNS_META_NAME)
            if notebook_experiment_runs:
                return notebook_experiment_runs
            else:
                return None
        else:
            return None
        
    def _refresh_cur_run(self,type,run_id:str=None):
        self._cur_exp_runs=self._get_current_notebook_experiment_runs()
        if self._cur_exp_runs:
            if run_id:
                _, run_info=self._get_latest_run_idx(self._cur_exp_runs,run_id=run_id)             
            else:
                _, run_info=self._get_latest_run_idx(self._cur_exp_runs)

            if type==METRICS_META_NAME:
                refreshed_data=run_info.get(METRICS_META_NAME)
            if type==PARAMS_META_NAME:
                refreshed_data=run_info.get(PARAMS_META_NAME)
            if type==TAGS_META_NAME:
                refreshed_data=run_info.get(TAGS_META_NAME)
            
            return refreshed_data
            
        else:
            raise ClientError("No run information is available")
        
    def _get_latest_run_idx(self,data,run_id=None):
        
        get_run_idx=None

        if run_id:
            get_latest_runs=[item for item in data if item["run_id"] == run_id]
            if not get_latest_runs:
                raise ClientError("No run information available for run id {}".format(run_id))
            else:
                get_run_idx=next(idx for idx, item in enumerate(data) if item["run_id"] == run_id and item["created_date"]==max(get_latest_runs, key=(lambda item: item["created_date"]))["created_date"])
                get_run_metadata= data[get_run_idx]   
        else:
            get_run_idx=max(range(len(data)), key=lambda index: data[index]['created_date'])
            get_run_metadata= data[get_run_idx]
    
        return get_run_idx,get_run_metadata

    def _get_latest_run_and_item(self,data,run_id=None):
        if run_id:
            get_latest_runs=[item for item in data if item["run_id"] == run_id]
            get_run_idx=next(idx for idx, item in enumerate(data) if item["run_id"] == run_id and item["created_date"]==max(get_latest_runs, key=(lambda item: item["created_date"]))["created_date"])
            get_run= data[get_run_idx]
            get_type_info= data[get_run_idx].get(NOTEBOOK_EXP_FACTS)

        else:
            get_run_idx=max(range(len(data)), key=lambda index: data[index]['created_date'])
            get_run= data[get_run_idx]
            get_type_info= data[get_run_idx].get(NOTEBOOK_EXP_FACTS)

        return get_run, get_type_info
    
    def _get_headers(self):
        token =  self._facts_client._authenticator.token_manager.get_token() if  ( isinstance(self._facts_client._authenticator, IAMAuthenticator) or (isinstance(self._facts_client._authenticator, CloudPakForDataAuthenticator))) else self._facts_client._authenticator.bearer_token
        iam_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer %s" % token
        }
        return iam_headers 
    
    