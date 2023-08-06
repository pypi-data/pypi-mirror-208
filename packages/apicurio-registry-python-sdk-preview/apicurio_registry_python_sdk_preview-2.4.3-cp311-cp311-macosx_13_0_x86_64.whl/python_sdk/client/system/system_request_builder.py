from __future__ import annotations
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .info import info_request_builder
    from .limits import limits_request_builder

class SystemRequestBuilder():
    """
    Builds and executes requests for operations under /system
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Optional[Union[Dict[str, Any], str]] = None) -> None:
        """
        Instantiates a new SystemRequestBuilder and sets the default values.
        Args:
            pathParameters: The raw url or the Url template parameters for the request.
            requestAdapter: The request adapter to use to execute the requests.
        """
        if path_parameters is None:
            raise Exception("path_parameters cannot be undefined")
        if request_adapter is None:
            raise Exception("request_adapter cannot be undefined")
        # Url template to use to build the URL for the current request builder
        self.url_template: str = "{+baseurl}/system"

        url_tpl_params = get_path_parameters(path_parameters)
        self.path_parameters = url_tpl_params
        self.request_adapter = request_adapter
    
    @property
    def info(self) -> info_request_builder.InfoRequestBuilder:
        """
        Retrieve system information
        """
        from .info import info_request_builder

        return info_request_builder.InfoRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def limits(self) -> limits_request_builder.LimitsRequestBuilder:
        """
        Retrieve resource limits information
        """
        from .limits import limits_request_builder

        return limits_request_builder.LimitsRequestBuilder(self.request_adapter, self.path_parameters)
    

