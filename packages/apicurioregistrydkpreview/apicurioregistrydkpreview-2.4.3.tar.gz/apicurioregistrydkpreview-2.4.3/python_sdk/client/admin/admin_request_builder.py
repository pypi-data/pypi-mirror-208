from __future__ import annotations
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .artifact_types import artifact_types_request_builder
    from .config import config_request_builder
    from .export import export_request_builder
    from .import_ import import_request_builder
    from .loggers import loggers_request_builder
    from .loggers.item import with_logger_item_request_builder
    from .role_mappings import role_mappings_request_builder
    from .role_mappings.item import with_principal_item_request_builder
    from .rules import rules_request_builder
    from .rules.item import with_rule_item_request_builder

class AdminRequestBuilder():
    """
    Builds and executes requests for operations under /admin
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Optional[Union[Dict[str, Any], str]] = None) -> None:
        """
        Instantiates a new AdminRequestBuilder and sets the default values.
        Args:
            pathParameters: The raw url or the Url template parameters for the request.
            requestAdapter: The request adapter to use to execute the requests.
        """
        if path_parameters is None:
            raise Exception("path_parameters cannot be undefined")
        if request_adapter is None:
            raise Exception("request_adapter cannot be undefined")
        # Url template to use to build the URL for the current request builder
        self.url_template: str = "{+baseurl}/admin"

        url_tpl_params = get_path_parameters(path_parameters)
        self.path_parameters = url_tpl_params
        self.request_adapter = request_adapter
    
    def loggers_by_id(self,id: str) -> with_logger_item_request_builder.WithLoggerItemRequestBuilder:
        """
        Manage logger settings/configurations.
        Args:
            id: Unique identifier of the item
        Returns: with_logger_item_request_builder.WithLoggerItemRequestBuilder
        """
        if id is None:
            raise Exception("id cannot be undefined")
        from .loggers.item import with_logger_item_request_builder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["logger"] = id
        return with_logger_item_request_builder.WithLoggerItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    def role_mappings_by_id(self,id: str) -> with_principal_item_request_builder.WithPrincipalItemRequestBuilder:
        """
        Manage the configuration of a single role mapping.
        Args:
            id: Unique identifier of the item
        Returns: with_principal_item_request_builder.WithPrincipalItemRequestBuilder
        """
        if id is None:
            raise Exception("id cannot be undefined")
        from .role_mappings.item import with_principal_item_request_builder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["principalId"] = id
        return with_principal_item_request_builder.WithPrincipalItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    def rules_by_id(self,id: str) -> with_rule_item_request_builder.WithRuleItemRequestBuilder:
        """
        Manage the configuration of a single global artifact rule.
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
    
    @property
    def artifact_types(self) -> artifact_types_request_builder.ArtifactTypesRequestBuilder:
        """
        The list of artifact types supported by this instance of Registry.
        """
        from .artifact_types import artifact_types_request_builder

        return artifact_types_request_builder.ArtifactTypesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def config(self) -> config_request_builder.ConfigRequestBuilder:
        """
        The config property
        """
        from .config import config_request_builder

        return config_request_builder.ConfigRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def export(self) -> export_request_builder.ExportRequestBuilder:
        """
        Provides a way to export registry data.
        """
        from .export import export_request_builder

        return export_request_builder.ExportRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def import_(self) -> import_request_builder.ImportRequestBuilder:
        """
        Provides a way to import data into the registry.
        """
        from .import_ import import_request_builder

        return import_request_builder.ImportRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def loggers(self) -> loggers_request_builder.LoggersRequestBuilder:
        """
        Manage logger settings/configurations.
        """
        from .loggers import loggers_request_builder

        return loggers_request_builder.LoggersRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def role_mappings(self) -> role_mappings_request_builder.RoleMappingsRequestBuilder:
        """
        Collection to manage role mappings for authenticated principals
        """
        from .role_mappings import role_mappings_request_builder

        return role_mappings_request_builder.RoleMappingsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def rules(self) -> rules_request_builder.RulesRequestBuilder:
        """
        Manage the global rules that apply to all artifacts if not otherwise configured.
        """
        from .rules import rules_request_builder

        return rules_request_builder.RulesRequestBuilder(self.request_adapter, self.path_parameters)
    

