from __future__ import annotations
from dataclasses import dataclass
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.method import Method
from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.request_option import RequestOption
from kiota_abstractions.response_handler import ResponseHandler
from kiota_abstractions.serialization import Parsable, ParsableFactory
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ..models import create_group_meta_data, error, group_meta_data, group_search_results

class GroupsRequestBuilder():
    """
    Collection of the groups in the registry.
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Optional[Union[Dict[str, Any], str]] = None) -> None:
        """
        Instantiates a new GroupsRequestBuilder and sets the default values.
        Args:
            pathParameters: The raw url or the Url template parameters for the request.
            requestAdapter: The request adapter to use to execute the requests.
        """
        if path_parameters is None:
            raise Exception("path_parameters cannot be undefined")
        if request_adapter is None:
            raise Exception("request_adapter cannot be undefined")
        # Url template to use to build the URL for the current request builder
        self.url_template: str = "{+baseurl}/groups{?limit*,offset*,order*,orderby*}"

        url_tpl_params = get_path_parameters(path_parameters)
        self.path_parameters = url_tpl_params
        self.request_adapter = request_adapter
    
    async def get(self,request_configuration: Optional[GroupsRequestBuilderGetRequestConfiguration] = None) -> Optional[group_search_results.GroupSearchResults]:
        """
        Returns a list of all groups.  This list is paged.
        Args:
            requestConfiguration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[group_search_results.GroupSearchResults]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ..models import error

        error_mapping: Dict[str, ParsableFactory] = {
            "500": error.Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ..models import group_search_results

        return await self.request_adapter.send_async(request_info, group_search_results.GroupSearchResults, error_mapping)
    
    async def post(self,body: Optional[create_group_meta_data.CreateGroupMetaData] = None, request_configuration: Optional[GroupsRequestBuilderPostRequestConfiguration] = None) -> Optional[group_meta_data.GroupMetaData]:
        """
        Creates a new group.This operation can fail for the following reasons:* A server error occurred (HTTP error `500`)* The group already exist (HTTP error `409`)
        Args:
            body: The request body
            requestConfiguration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[group_meta_data.GroupMetaData]
        """
        if body is None:
            raise Exception("body cannot be undefined")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        from ..models import error

        error_mapping: Dict[str, ParsableFactory] = {
            "409": error.Error,
            "500": error.Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ..models import group_meta_data

        return await self.request_adapter.send_async(request_info, group_meta_data.GroupMetaData, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[GroupsRequestBuilderGetRequestConfiguration] = None) -> RequestInformation:
        """
        Returns a list of all groups.  This list is paged.
        Args:
            requestConfiguration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation()
        request_info.url_template = self.url_template
        request_info.path_parameters = self.path_parameters
        request_info.http_method = Method.GET
        request_info.headers["Accept"] = ["application/json"]
        if request_configuration:
            request_info.add_request_headers(request_configuration.headers)
            request_info.set_query_string_parameters_from_raw_object(request_configuration.query_parameters)
            request_info.add_request_options(request_configuration.options)
        return request_info
    
    def to_post_request_information(self,body: Optional[create_group_meta_data.CreateGroupMetaData] = None, request_configuration: Optional[GroupsRequestBuilderPostRequestConfiguration] = None) -> RequestInformation:
        """
        Creates a new group.This operation can fail for the following reasons:* A server error occurred (HTTP error `500`)* The group already exist (HTTP error `409`)
        Args:
            body: The request body
            requestConfiguration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise Exception("body cannot be undefined")
        request_info = RequestInformation()
        request_info.url_template = self.url_template
        request_info.path_parameters = self.path_parameters
        request_info.http_method = Method.POST
        request_info.headers["Accept"] = ["application/json"]
        if request_configuration:
            request_info.add_request_headers(request_configuration.headers)
            request_info.add_request_options(request_configuration.options)
        request_info.set_content_from_parsable(self.request_adapter, "application/json", body)
        return request_info
    
    @dataclass
    class GroupsRequestBuilderGetQueryParameters():
        """
        Returns a list of all groups.  This list is paged.
        """
        # The number of groups to return.  Defaults to 20.
        limit: Optional[int] = None

        # The number of groups to skip before starting the result set.  Defaults to 0.
        offset: Optional[int] = None

        # Sort order, ascending (`asc`) or descending (`desc`).
        order: Optional[str] = None

        # The field to sort by.  Can be one of:* `name`* `createdOn`
        orderby: Optional[str] = None

    
    @dataclass
    class GroupsRequestBuilderGetRequestConfiguration():
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        # Request headers
        headers: Optional[Dict[str, Union[str, List[str]]]] = None

        # Request options
        options: Optional[List[RequestOption]] = None

        # Request query parameters
        query_parameters: Optional[GroupsRequestBuilder.GroupsRequestBuilderGetQueryParameters] = None

    
    @dataclass
    class GroupsRequestBuilderPostRequestConfiguration():
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        # Request headers
        headers: Optional[Dict[str, Union[str, List[str]]]] = None

        # Request options
        options: Optional[List[RequestOption]] = None

    

