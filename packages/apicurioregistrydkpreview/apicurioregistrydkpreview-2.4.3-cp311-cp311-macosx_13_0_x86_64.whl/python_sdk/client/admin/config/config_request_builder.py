from __future__ import annotations
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .properties import properties_request_builder
    from .properties.item import with_property_name_item_request_builder

class ConfigRequestBuilder():
    """
    Builds and executes requests for operations under /admin/config
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Optional[Union[Dict[str, Any], str]] = None) -> None:
        """
        Instantiates a new ConfigRequestBuilder and sets the default values.
        Args:
            pathParameters: The raw url or the Url template parameters for the request.
            requestAdapter: The request adapter to use to execute the requests.
        """
        if path_parameters is None:
            raise Exception("path_parameters cannot be undefined")
        if request_adapter is None:
            raise Exception("request_adapter cannot be undefined")
        # Url template to use to build the URL for the current request builder
        self.url_template: str = "{+baseurl}/admin/config"

        url_tpl_params = get_path_parameters(path_parameters)
        self.path_parameters = url_tpl_params
        self.request_adapter = request_adapter
    
    def properties_by_id(self,id: str) -> with_property_name_item_request_builder.WithPropertyNameItemRequestBuilder:
        """
        Manage a single configuration property (by name).
        Args:
            id: Unique identifier of the item
        Returns: with_property_name_item_request_builder.WithPropertyNameItemRequestBuilder
        """
        if id is None:
            raise Exception("id cannot be undefined")
        from .properties.item import with_property_name_item_request_builder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["propertyName"] = id
        return with_property_name_item_request_builder.WithPropertyNameItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    @property
    def properties(self) -> properties_request_builder.PropertiesRequestBuilder:
        """
        Manage configuration properties.
        """
        from .properties import properties_request_builder

        return properties_request_builder.PropertiesRequestBuilder(self.request_adapter, self.path_parameters)
    

