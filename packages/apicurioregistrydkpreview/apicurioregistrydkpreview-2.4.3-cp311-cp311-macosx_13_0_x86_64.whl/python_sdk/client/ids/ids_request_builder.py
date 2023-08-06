from __future__ import annotations
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .content_hashes import content_hashes_request_builder
    from .content_hashes.item import with_content_hash_item_request_builder
    from .content_ids import content_ids_request_builder
    from .content_ids.item import with_content_item_request_builder
    from .global_ids import global_ids_request_builder
    from .global_ids.item import with_global_item_request_builder

class IdsRequestBuilder():
    """
    Builds and executes requests for operations under /ids
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Optional[Union[Dict[str, Any], str]] = None) -> None:
        """
        Instantiates a new IdsRequestBuilder and sets the default values.
        Args:
            pathParameters: The raw url or the Url template parameters for the request.
            requestAdapter: The request adapter to use to execute the requests.
        """
        if path_parameters is None:
            raise Exception("path_parameters cannot be undefined")
        if request_adapter is None:
            raise Exception("request_adapter cannot be undefined")
        # Url template to use to build the URL for the current request builder
        self.url_template: str = "{+baseurl}/ids"

        url_tpl_params = get_path_parameters(path_parameters)
        self.path_parameters = url_tpl_params
        self.request_adapter = request_adapter
    
    def content_hashes_by_id(self,id: str) -> with_content_hash_item_request_builder.WithContentHashItemRequestBuilder:
        """
        Access artifact content utilizing the SHA-256 hash of the content.
        Args:
            id: Unique identifier of the item
        Returns: with_content_hash_item_request_builder.WithContentHashItemRequestBuilder
        """
        if id is None:
            raise Exception("id cannot be undefined")
        from .content_hashes.item import with_content_hash_item_request_builder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["contentHash"] = id
        return with_content_hash_item_request_builder.WithContentHashItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    def content_ids_by_id(self,id: str) -> with_content_item_request_builder.WithContentItemRequestBuilder:
        """
        Access artifact content utilizing the unique content identifier for that content.
        Args:
            id: Unique identifier of the item
        Returns: with_content_item_request_builder.WithContentItemRequestBuilder
        """
        if id is None:
            raise Exception("id cannot be undefined")
        from .content_ids.item import with_content_item_request_builder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["contentId"] = id
        return with_content_item_request_builder.WithContentItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    def global_ids_by_id(self,id: str) -> with_global_item_request_builder.WithGlobalItemRequestBuilder:
        """
        Access artifact content utilizing an artifact version's globally unique identifier.
        Args:
            id: Unique identifier of the item
        Returns: with_global_item_request_builder.WithGlobalItemRequestBuilder
        """
        if id is None:
            raise Exception("id cannot be undefined")
        from .global_ids.item import with_global_item_request_builder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["globalId"] = id
        return with_global_item_request_builder.WithGlobalItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    @property
    def content_hashes(self) -> content_hashes_request_builder.ContentHashesRequestBuilder:
        """
        The contentHashes property
        """
        from .content_hashes import content_hashes_request_builder

        return content_hashes_request_builder.ContentHashesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def content_ids(self) -> content_ids_request_builder.ContentIdsRequestBuilder:
        """
        The contentIds property
        """
        from .content_ids import content_ids_request_builder

        return content_ids_request_builder.ContentIdsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def global_ids(self) -> global_ids_request_builder.GlobalIdsRequestBuilder:
        """
        The globalIds property
        """
        from .global_ids import global_ids_request_builder

        return global_ids_request_builder.GlobalIdsRequestBuilder(self.request_adapter, self.path_parameters)
    

