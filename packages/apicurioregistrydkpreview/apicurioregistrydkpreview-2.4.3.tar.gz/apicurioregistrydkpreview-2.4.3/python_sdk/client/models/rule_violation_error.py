from __future__ import annotations
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from . import error

from . import error

class RuleViolationError(error.Error):
    """
    All error responses, whether `4xx` or `5xx` will include one of these as the responsebody.
    """
    def __init__(self,) -> None:
        """
        Instantiates a new RuleViolationError and sets the default values.
        """
        super().__init__()
        # Full details about the error.  This might contain a server stack trace, for example.
        self.detail: Optional[str] = None
        # The server-side error code.
        self.error_code: Optional[int] = None
        # The short error message.
        self.message: Optional[str] = None
        # The error name - typically the classname of the exception thrown by the server.
        self.name: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: Optional[ParseNode] = None) -> RuleViolationError:
        """
        Creates a new instance of the appropriate class based on discriminator value
        Args:
            parseNode: The parse node to use to read the discriminator value and create the object
        Returns: RuleViolationError
        """
        if parse_node is None:
            raise Exception("parse_node cannot be undefined")
        return RuleViolationError()
    
    def get_field_deserializers(self,) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        from . import error

        fields: Dict[str, Callable[[Any], None]] = {
        }
        super_fields = super().get_field_deserializers()
        fields.update(super_fields)
        return fields
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        Args:
            writer: Serialization writer to use to serialize this model
        """
        if writer is None:
            raise Exception("writer cannot be undefined")
        super().serialize(writer)
    

