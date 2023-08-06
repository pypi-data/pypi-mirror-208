from __future__ import annotations
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from . import log_level, named_log_configuration

from . import named_log_configuration

class LogConfiguration(named_log_configuration.NamedLogConfiguration):
    def __init__(self,) -> None:
        """
        Instantiates a new LogConfiguration and sets the default values.
        """
        super().__init__()
        # The level property
        self._level: Optional[log_level.LogLevel] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: Optional[ParseNode] = None) -> LogConfiguration:
        """
        Creates a new instance of the appropriate class based on discriminator value
        Args:
            parseNode: The parse node to use to read the discriminator value and create the object
        Returns: LogConfiguration
        """
        if parse_node is None:
            raise Exception("parse_node cannot be undefined")
        return LogConfiguration()
    
    def get_field_deserializers(self,) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        from . import log_level, named_log_configuration

        fields: Dict[str, Callable[[Any], None]] = {
            "level": lambda n : setattr(self, 'level', n.get_enum_value(log_level.LogLevel)),
        }
        super_fields = super().get_field_deserializers()
        fields.update(super_fields)
        return fields
    
    @property
    def level(self,) -> Optional[log_level.LogLevel]:
        """
        Gets the level property value. The level property
        Returns: Optional[log_level.LogLevel]
        """
        return self._level
    
    @level.setter
    def level(self,value: Optional[log_level.LogLevel] = None) -> None:
        """
        Sets the level property value. The level property
        Args:
            value: Value to set for the level property.
        """
        self._level = value
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        Args:
            writer: Serialization writer to use to serialize this model
        """
        if writer is None:
            raise Exception("writer cannot be undefined")
        super().serialize(writer)
        writer.write_enum_value("level", self.level)
    

