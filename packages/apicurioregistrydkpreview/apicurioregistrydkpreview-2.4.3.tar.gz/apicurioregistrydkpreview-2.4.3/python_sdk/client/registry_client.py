from __future__ import annotations
from kiota_abstractions.api_client_builder import enable_backing_store_for_serialization_writer_factory, register_default_deserializer, register_default_serializer
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.serialization import ParseNodeFactoryRegistry, SerializationWriterFactoryRegistry
from kiota_serialization_json.json_parse_node_factory import JsonParseNodeFactory
from kiota_serialization_json.json_serialization_writer_factory import JsonSerializationWriterFactory
from kiota_serialization_text.text_parse_node_factory import TextParseNodeFactory
from kiota_serialization_text.text_serialization_writer_factory import TextSerializationWriterFactory
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .admin import admin_request_builder
    from .groups import groups_request_builder
    from .groups.item import with_group_item_request_builder
    from .ids import ids_request_builder
    from .search import search_request_builder
    from .system import system_request_builder
    from .users import users_request_builder

class RegistryClient():
    """
    The main entry point of the SDK, exposes the configuration and the fluent API.
    """
    def __init__(self,request_adapter: RequestAdapter) -> None:
        """
        Instantiates a new RegistryClient and sets the default values.
        Args:
            requestAdapter: The request adapter to use to execute the requests.
        """
        if request_adapter is None:
            raise Exception("request_adapter cannot be undefined")
        # Path parameters for the request
        self.path_parameters: Dict[str, Any] = {}

        # Url template to use to build the URL for the current request builder
        self.url_template: str = "{+baseurl}"

        self.request_adapter = request_adapter
        register_default_serializer(JsonSerializationWriterFactory)
        register_default_serializer(TextSerializationWriterFactory)
        register_default_deserializer(JsonParseNodeFactory)
        register_default_deserializer(TextParseNodeFactory)
    
    def groups_by_id(self,id: str) -> with_group_item_request_builder.WithGroupItemRequestBuilder:
        """
        Collection to manage a single group in the registry.
        Args:
            id: Unique identifier of the item
        Returns: with_group_item_request_builder.WithGroupItemRequestBuilder
        """
        if id is None:
            raise Exception("id cannot be undefined")
        from .groups.item import with_group_item_request_builder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["groupId"] = id
        return with_group_item_request_builder.WithGroupItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    @property
    def admin(self) -> admin_request_builder.AdminRequestBuilder:
        """
        The admin property
        """
        from .admin import admin_request_builder

        return admin_request_builder.AdminRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def groups(self) -> groups_request_builder.GroupsRequestBuilder:
        """
        Collection of the groups in the registry.
        """
        from .groups import groups_request_builder

        return groups_request_builder.GroupsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def ids(self) -> ids_request_builder.IdsRequestBuilder:
        """
        The ids property
        """
        from .ids import ids_request_builder

        return ids_request_builder.IdsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def search(self) -> search_request_builder.SearchRequestBuilder:
        """
        The search property
        """
        from .search import search_request_builder

        return search_request_builder.SearchRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def system(self) -> system_request_builder.SystemRequestBuilder:
        """
        The system property
        """
        from .system import system_request_builder

        return system_request_builder.SystemRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def users(self) -> users_request_builder.UsersRequestBuilder:
        """
        The users property
        """
        from .users import users_request_builder

        return users_request_builder.UsersRequestBuilder(self.request_adapter, self.path_parameters)
    

