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
    from ......models import artifact_content, artifact_meta_data, editable_meta_data, error, version_meta_data

class MetaRequestBuilder():
    """
    Manage the metadata of a single artifact.
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Optional[Union[Dict[str, Any], str]] = None) -> None:
        """
        Instantiates a new MetaRequestBuilder and sets the default values.
        Args:
            pathParameters: The raw url or the Url template parameters for the request.
            requestAdapter: The request adapter to use to execute the requests.
        """
        if path_parameters is None:
            raise Exception("path_parameters cannot be undefined")
        if request_adapter is None:
            raise Exception("request_adapter cannot be undefined")
        # Url template to use to build the URL for the current request builder
        self.url_template: str = "{+baseurl}/groups/{groupId}/artifacts/{artifactId}/meta{?canonical*}"

        url_tpl_params = get_path_parameters(path_parameters)
        self.path_parameters = url_tpl_params
        self.request_adapter = request_adapter
    
    async def get(self,request_configuration: Optional[MetaRequestBuilderGetRequestConfiguration] = None) -> Optional[artifact_meta_data.ArtifactMetaData]:
        """
        Gets the metadata for an artifact in the registry, based on the latest version. If the latest version of the artifact is marked as `DISABLED`, the next available non-disabled version will be used. The returned metadata includesboth generated (read-only) and editable metadata (such as name and description).This operation can fail for the following reasons:* No artifact with this `artifactId` exists  or all versions are `DISABLED` (HTTP error `404`)* A server error occurred (HTTP error `500`)
        Args:
            requestConfiguration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[artifact_meta_data.ArtifactMetaData]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ......models import error

        error_mapping: Dict[str, ParsableFactory] = {
            "404": error.Error,
            "500": error.Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ......models import artifact_meta_data

        return await self.request_adapter.send_async(request_info, artifact_meta_data.ArtifactMetaData, error_mapping)
    
    async def post(self,body: Optional[artifact_content.ArtifactContent] = None, request_configuration: Optional[MetaRequestBuilderPostRequestConfiguration] = None) -> Optional[version_meta_data.VersionMetaData]:
        """
        Gets the metadata for an artifact that matches the raw content.  Searches the registryfor a version of the given artifact matching the content provided in the body of thePOST.This operation can fail for the following reasons:* Provided content (request body) was empty (HTTP error `400`)* No artifact with the `artifactId` exists (HTTP error `404`)* No artifact version matching the provided content exists (HTTP error `404`)* A server error occurred (HTTP error `500`)
        Args:
            body: The request body
            requestConfiguration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[version_meta_data.VersionMetaData]
        """
        if body is None:
            raise Exception("body cannot be undefined")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        from ......models import error

        error_mapping: Dict[str, ParsableFactory] = {
            "404": error.Error,
            "500": error.Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ......models import version_meta_data

        return await self.request_adapter.send_async(request_info, version_meta_data.VersionMetaData, error_mapping)
    
    async def put(self,body: Optional[editable_meta_data.EditableMetaData] = None, request_configuration: Optional[MetaRequestBuilderPutRequestConfiguration] = None) -> None:
        """
        Updates the editable parts of the artifact's metadata.  Not all metadata fields canbe updated.  For example, `createdOn` and `createdBy` are both read-only properties.This operation can fail for the following reasons:* No artifact with the `artifactId` exists (HTTP error `404`)* A server error occurred (HTTP error `500`)
        Args:
            body: The request body
            requestConfiguration: Configuration for the request such as headers, query parameters, and middleware options.
        """
        if body is None:
            raise Exception("body cannot be undefined")
        request_info = self.to_put_request_information(
            body, request_configuration
        )
        from ......models import error

        error_mapping: Dict[str, ParsableFactory] = {
            "404": error.Error,
            "500": error.Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[MetaRequestBuilderGetRequestConfiguration] = None) -> RequestInformation:
        """
        Gets the metadata for an artifact in the registry, based on the latest version. If the latest version of the artifact is marked as `DISABLED`, the next available non-disabled version will be used. The returned metadata includesboth generated (read-only) and editable metadata (such as name and description).This operation can fail for the following reasons:* No artifact with this `artifactId` exists  or all versions are `DISABLED` (HTTP error `404`)* A server error occurred (HTTP error `500`)
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
            request_info.add_request_options(request_configuration.options)
        return request_info
    
    def to_post_request_information(self,body: Optional[artifact_content.ArtifactContent] = None, request_configuration: Optional[MetaRequestBuilderPostRequestConfiguration] = None) -> RequestInformation:
        """
        Gets the metadata for an artifact that matches the raw content.  Searches the registryfor a version of the given artifact matching the content provided in the body of thePOST.This operation can fail for the following reasons:* Provided content (request body) was empty (HTTP error `400`)* No artifact with the `artifactId` exists (HTTP error `404`)* No artifact version matching the provided content exists (HTTP error `404`)* A server error occurred (HTTP error `500`)
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
            request_info.set_query_string_parameters_from_raw_object(request_configuration.query_parameters)
            request_info.add_request_options(request_configuration.options)
        request_info.set_content_from_parsable(self.request_adapter, "application/get.extended+json", body)
        return request_info
    
    def to_put_request_information(self,body: Optional[editable_meta_data.EditableMetaData] = None, request_configuration: Optional[MetaRequestBuilderPutRequestConfiguration] = None) -> RequestInformation:
        """
        Updates the editable parts of the artifact's metadata.  Not all metadata fields canbe updated.  For example, `createdOn` and `createdBy` are both read-only properties.This operation can fail for the following reasons:* No artifact with the `artifactId` exists (HTTP error `404`)* A server error occurred (HTTP error `500`)
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
        request_info.http_method = Method.PUT
        if request_configuration:
            request_info.add_request_headers(request_configuration.headers)
            request_info.add_request_options(request_configuration.options)
        request_info.set_content_from_parsable(self.request_adapter, "application/json", body)
        return request_info
    
    @dataclass
    class MetaRequestBuilderGetRequestConfiguration():
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        # Request headers
        headers: Optional[Dict[str, Union[str, List[str]]]] = None

        # Request options
        options: Optional[List[RequestOption]] = None

    
    @dataclass
    class MetaRequestBuilderPostQueryParameters():
        """
        Gets the metadata for an artifact that matches the raw content.  Searches the registryfor a version of the given artifact matching the content provided in the body of thePOST.This operation can fail for the following reasons:* Provided content (request body) was empty (HTTP error `400`)* No artifact with the `artifactId` exists (HTTP error `404`)* No artifact version matching the provided content exists (HTTP error `404`)* A server error occurred (HTTP error `500`)
        """
        # Parameter that can be set to `true` to indicate that the server should "canonicalize" the content when searching for a matching version.  Canonicalization is unique to each artifact type, but typically involves removing any extra whitespace and formatting the content in a consistent manner.
        canonical: Optional[bool] = None

    
    @dataclass
    class MetaRequestBuilderPostRequestConfiguration():
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        # Request headers
        headers: Optional[Dict[str, Union[str, List[str]]]] = None

        # Request options
        options: Optional[List[RequestOption]] = None

        # Request query parameters
        query_parameters: Optional[MetaRequestBuilder.MetaRequestBuilderPostQueryParameters] = None

    
    @dataclass
    class MetaRequestBuilderPutRequestConfiguration():
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        # Request headers
        headers: Optional[Dict[str, Union[str, List[str]]]] = None

        # Request options
        options: Optional[List[RequestOption]] = None

    

