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

from enum import Enum


class ContainerType:
    """
        Describes possible container types. Client initialization works for SPACE or PROJECT only.
        Contains: [PROJECT,SPACE,CATALOG]
    """
    PROJECT = 'project'
    SPACE = 'space'
    CATALOG= "catalog"

class FormatType:
    """
        Describes output formats options
        Contains: [DICT,STR]
    """
    DICT = 'dict'
    STR = 'str'

class ModelEntryContainerType:
    """
        Describes possible model usecase container types.
        Contains: [DEVELOP,TEST,VALIDATE,OPERATE]
    """
    DEVELOP = 'develop'
    TEST = 'test'
    VALIDATE= 'validate'
    OPERATE= 'operate'


class AllowedDefinitionType:
    """
        Describes possible CAMS data types for definitions.
        Contains: [INTEGER,STRING,DATE]
    """
    INTEGER = 'int'
    STRING = 'str'
    DATE= 'date'


class FactsType:
    """
        Describes possible Factsheet custom asset types. Only MODEL_FACTS_USER and MODEL_USECASE_USER supported when creating definitions.
        Contains: [MODEL_FACTS_USER,MODEL_USECASE_USER,MODEL_FACTS_USER_OP,MODEL_FACTS_SYSTEM,MODEL_FACTS_GLOBAL]

        - The modelfacts user AssetType to capture the user defined attributes of a model
        - The model usecase user asset type to capture user defined attributes of a model usecase
        - The modelfacts user AssetType to capture the user defined attributes of a model to be synced to OpenPages
        - The modelfacts system AssetType to capture the system defined attributes of a model
        - The modelfacts global AssetType to capture the global attributes of physical model (external model)

    """
    MODEL_FACTS_USER = 'modelfacts_user'
    MODEL_USECASE_USER = 'model_entry_user'
    MODEL_FACTS_USER_OP= 'modelfacts_user_op'
    MODEL_FACTS_SYSTEM= 'modelfacts_system'
    MODEL_FACTS_GLOBAL= 'modelfacts_global'


class AssetContainerSpaceMap(Enum):
    """
    Describes possible environment and space types.
    Contains: [DEVELOP,TEST,VALIDATE,OPERATE]

    """
    DEVELOP= ''
    TEST = 'development'
    VALIDATE= 'pre-production'
    OPERATE= 'production'


class AssetContainerSpaceMapExternal(Enum):
    """
    Describes possible environment and space types for external models.
    Contains: [DEVELOP,TEST,VALIDATE,OPERATE]

    """
    DEVELOP = 'development'
    TEST= 'development'
    VALIDATE= 'pre-production'
    OPERATE= 'production'

class RenderingHints:

    """Describes rendering hints for attachment facts.
    Contains: [INLINE_HTML,INLINE_IMAGE,LINK_DOWNLOAD,LINK_NEW_TAB]
    """
    
    INLINE_HTML='inline_html'
    INLINE_IMAGE='inline_image'
    LINK_DOWNLOAD='link_download'
    LINK_NEW_TAB='link_new_tab'


class OnErrorTypes:
    """
    expected behaviour on error.
    """
    STOP = 'stop'
    CONTINUE = 'continue'


class ContentTypes:
    """
    The type of the input. A character encoding can be specified by including a
    `charset` parameter. For example, 'text/csv;charset=utf-8'.
    """
    APPLICATION_JSON = 'application/json'
    TEXT_CSV = 'text/csv'

class StatusStateType:
    ACTIVE = "active"
    RUNNING = "running"
    FINISHED = "finished"
    PREPARING = "preparing"
    SUCCESS = "success"
    COMPLETED = "completed"
    FAILURE = "failure"
    FAILED = "failed"
    ERROR = "error"
    CANCELLED = "cancelled"
    CANCELED = "canceled"



