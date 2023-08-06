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
    from .....models import artifact_content, artifact_meta_data, error
    from .meta import meta_request_builder
    from .owner import owner_request_builder
    from .rules import rules_request_builder
    from .rules.item import with_rule_item_request_builder
    from .state import state_request_builder
    from .test import test_request_builder
    from .versions import versions_request_builder
    from .versions.item import with_version_item_request_builder

class WithArtifactItemRequestBuilder():
    """
    Manage a single artifact.
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Optional[Union[Dict[str, Any], str]] = None) -> None:
        """
        Instantiates a new WithArtifactItemRequestBuilder and sets the default values.
        Args:
            pathParameters: The raw url or the Url template parameters for the request.
            requestAdapter: The request adapter to use to execute the requests.
        """
        if path_parameters is None:
            raise Exception("path_parameters cannot be undefined")
        if request_adapter is None:
            raise Exception("request_adapter cannot be undefined")
        # Url template to use to build the URL for the current request builder
        self.url_template: str = "{+baseurl}/groups/{groupId}/artifacts/{artifactId}{?dereference*}"

        url_tpl_params = get_path_parameters(path_parameters)
        self.path_parameters = url_tpl_params
        self.request_adapter = request_adapter
    
    async def delete(self,request_configuration: Optional[WithArtifactItemRequestBuilderDeleteRequestConfiguration] = None) -> None:
        """
        Deletes an artifact completely, resulting in all versions of the artifact also beingdeleted.  This may fail for one of the following reasons:* No artifact with the `artifactId` exists (HTTP error `404`)* A server error occurred (HTTP error `500`)
        Args:
            requestConfiguration: Configuration for the request such as headers, query parameters, and middleware options.
        """
        request_info = self.to_delete_request_information(
            request_configuration
        )
        from .....models import error

        error_mapping: Dict[str, ParsableFactory] = {
            "404": error.Error,
            "500": error.Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, error_mapping)
    
    async def get(self,request_configuration: Optional[WithArtifactItemRequestBuilderGetRequestConfiguration] = None) -> bytes:
        """
        Returns the latest version of the artifact in its raw form.  The `Content-Type` of theresponse depends on the artifact type.  In most cases, this is `application/json`, but for some types it may be different (for example, `PROTOBUF`).If the latest version of the artifact is marked as `DISABLED`, the next available non-disabled version will be used.This operation may fail for one of the following reasons:* No artifact with this `artifactId` exists or all versions are `DISABLED` (HTTP error `404`)* A server error occurred (HTTP error `500`)
        Args:
            requestConfiguration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: bytes
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from .....models import error

        error_mapping: Dict[str, ParsableFactory] = {
            "404": error.Error,
            "500": error.Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_primitive_async(request_info, "bytes", error_mapping)
    
    async def put(self,body: Optional[artifact_content.ArtifactContent] = None, request_configuration: Optional[WithArtifactItemRequestBuilderPutRequestConfiguration] = None) -> Optional[artifact_meta_data.ArtifactMetaData]:
        """
        Updates an artifact by uploading new content.  The body of the request canbe the raw content of the artifact or a JSON object containing both the raw content anda set of references to other artifacts..  This is typically in JSON format for *most*of the supported types, but may be in another format for a few (for example, `PROTOBUF`).The type of the content should be compatible with the artifact's type (it would bean error to update an `AVRO` artifact with new `OPENAPI` content, for example).The update could fail for a number of reasons including:* Provided content (request body) was empty (HTTP error `400`)* No artifact with the `artifactId` exists (HTTP error `404`)* The new content violates one of the rules configured for the artifact (HTTP error `409`)* A server error occurred (HTTP error `500`)When successful, this creates a new version of the artifact, making it the most recent(and therefore official) version of the artifact.
        Args:
            body: The request body
            requestConfiguration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[artifact_meta_data.ArtifactMetaData]
        """
        if body is None:
            raise Exception("body cannot be undefined")
        request_info = self.to_put_request_information(
            body, request_configuration
        )
        from .....models import error

        error_mapping: Dict[str, ParsableFactory] = {
            "404": error.Error,
            "409": error.Error,
            "500": error.Error,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .....models import artifact_meta_data

        return await self.request_adapter.send_async(request_info, artifact_meta_data.ArtifactMetaData, error_mapping)
    
    def rules_by_id(self,id: str) -> with_rule_item_request_builder.WithRuleItemRequestBuilder:
        """
        Manage the configuration of a single artifact rule.
        Args:
            id: Unique identifier of the item
        Returns: with_rule_item_request_builder.WithRuleItemRequestBuilder
        """
        if id is None:
            raise Exception("id cannot be undefined")
        from .rules.item import with_rule_item_request_builder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["rule"] = id
        return with_rule_item_request_builder.WithRuleItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    def to_delete_request_information(self,request_configuration: Optional[WithArtifactItemRequestBuilderDeleteRequestConfiguration] = None) -> RequestInformation:
        """
        Deletes an artifact completely, resulting in all versions of the artifact also beingdeleted.  This may fail for one of the following reasons:* No artifact with the `artifactId` exists (HTTP error `404`)* A server error occurred (HTTP error `500`)
        Args:
            requestConfiguration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation()
        request_info.url_template = self.url_template
        request_info.path_parameters = self.path_parameters
        request_info.http_method = Method.DELETE
        if request_configuration:
            request_info.add_request_headers(request_configuration.headers)
            request_info.add_request_options(request_configuration.options)
        return request_info
    
    def to_get_request_information(self,request_configuration: Optional[WithArtifactItemRequestBuilderGetRequestConfiguration] = None) -> RequestInformation:
        """
        Returns the latest version of the artifact in its raw form.  The `Content-Type` of theresponse depends on the artifact type.  In most cases, this is `application/json`, but for some types it may be different (for example, `PROTOBUF`).If the latest version of the artifact is marked as `DISABLED`, the next available non-disabled version will be used.This operation may fail for one of the following reasons:* No artifact with this `artifactId` exists or all versions are `DISABLED` (HTTP error `404`)* A server error occurred (HTTP error `500`)
        Args:
            requestConfiguration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation()
        request_info.url_template = self.url_template
        request_info.path_parameters = self.path_parameters
        request_info.http_method = Method.GET
        if request_configuration:
            request_info.add_request_headers(request_configuration.headers)
            request_info.set_query_string_parameters_from_raw_object(request_configuration.query_parameters)
            request_info.add_request_options(request_configuration.options)
        return request_info
    
    def to_put_request_information(self,body: Optional[artifact_content.ArtifactContent] = None, request_configuration: Optional[WithArtifactItemRequestBuilderPutRequestConfiguration] = None) -> RequestInformation:
        """
        Updates an artifact by uploading new content.  The body of the request canbe the raw content of the artifact or a JSON object containing both the raw content anda set of references to other artifacts..  This is typically in JSON format for *most*of the supported types, but may be in another format for a few (for example, `PROTOBUF`).The type of the content should be compatible with the artifact's type (it would bean error to update an `AVRO` artifact with new `OPENAPI` content, for example).The update could fail for a number of reasons including:* Provided content (request body) was empty (HTTP error `400`)* No artifact with the `artifactId` exists (HTTP error `404`)* The new content violates one of the rules configured for the artifact (HTTP error `409`)* A server error occurred (HTTP error `500`)When successful, this creates a new version of the artifact, making it the most recent(and therefore official) version of the artifact.
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
        request_info.headers["Accept"] = ["application/json"]
        if request_configuration:
            request_info.add_request_headers(request_configuration.headers)
            request_info.add_request_options(request_configuration.options)
        request_info.set_content_from_parsable(self.request_adapter, "application/create.extended+json", body)
        return request_info
    
    def versions_by_id(self,id: str) -> with_version_item_request_builder.WithVersionItemRequestBuilder:
        """
        Manage a single version of a single artifact in the registry.
        Args:
            id: Unique identifier of the item
        Returns: with_version_item_request_builder.WithVersionItemRequestBuilder
        """
        if id is None:
            raise Exception("id cannot be undefined")
        from .versions.item import with_version_item_request_builder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["version"] = id
        return with_version_item_request_builder.WithVersionItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    @property
    def meta(self) -> meta_request_builder.MetaRequestBuilder:
        """
        Manage the metadata of a single artifact.
        """
        from .meta import meta_request_builder

        return meta_request_builder.MetaRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def owner(self) -> owner_request_builder.OwnerRequestBuilder:
        """
        Manage the ownership of a single artifact.
        """
        from .owner import owner_request_builder

        return owner_request_builder.OwnerRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def rules(self) -> rules_request_builder.RulesRequestBuilder:
        """
        Manage the rules for a single artifact.
        """
        from .rules import rules_request_builder

        return rules_request_builder.RulesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def state(self) -> state_request_builder.StateRequestBuilder:
        """
        Manage the state of an artifact.
        """
        from .state import state_request_builder

        return state_request_builder.StateRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def test(self) -> test_request_builder.TestRequestBuilder:
        """
        Test whether content would pass update rules.
        """
        from .test import test_request_builder

        return test_request_builder.TestRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def versions(self) -> versions_request_builder.VersionsRequestBuilder:
        """
        Manage all the versions of an artifact in the registry.
        """
        from .versions import versions_request_builder

        return versions_request_builder.VersionsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class WithArtifactItemRequestBuilderDeleteRequestConfiguration():
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        # Request headers
        headers: Optional[Dict[str, Union[str, List[str]]]] = None

        # Request options
        options: Optional[List[RequestOption]] = None

    
    @dataclass
    class WithArtifactItemRequestBuilderGetQueryParameters():
        """
        Returns the latest version of the artifact in its raw form.  The `Content-Type` of theresponse depends on the artifact type.  In most cases, this is `application/json`, but for some types it may be different (for example, `PROTOBUF`).If the latest version of the artifact is marked as `DISABLED`, the next available non-disabled version will be used.This operation may fail for one of the following reasons:* No artifact with this `artifactId` exists or all versions are `DISABLED` (HTTP error `404`)* A server error occurred (HTTP error `500`)
        """
        # Allows the user to specify if the content should be dereferenced when being returned
        dereference: Optional[bool] = None

    
    @dataclass
    class WithArtifactItemRequestBuilderGetRequestConfiguration():
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        # Request headers
        headers: Optional[Dict[str, Union[str, List[str]]]] = None

        # Request options
        options: Optional[List[RequestOption]] = None

        # Request query parameters
        query_parameters: Optional[WithArtifactItemRequestBuilder.WithArtifactItemRequestBuilderGetQueryParameters] = None

    
    @dataclass
    class WithArtifactItemRequestBuilderPutRequestConfiguration():
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        # Request headers
        headers: Optional[Dict[str, Union[str, List[str]]]] = None

        # Request options
        options: Optional[List[RequestOption]] = None

    

