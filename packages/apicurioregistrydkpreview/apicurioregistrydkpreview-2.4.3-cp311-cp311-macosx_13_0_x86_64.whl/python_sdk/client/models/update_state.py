from __future__ import annotations
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from . import artifact_state

class UpdateState(AdditionalDataHolder, Parsable):
    def __init__(self,) -> None:
        """
        Instantiates a new UpdateState and sets the default values.
        """
        # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
        self._additional_data: Dict[str, Any] = {}

        # Describes the state of an artifact or artifact version.  The following statesare possible:* ENABLED* DISABLED* DEPRECATED
        self._state: Optional[artifact_state.ArtifactState] = None
    
    @property
    def additional_data(self,) -> Dict[str, Any]:
        """
        Gets the additionalData property value. Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
        Returns: Dict[str, Any]
        """
        return self._additional_data
    
    @additional_data.setter
    def additional_data(self,value: Dict[str, Any]) -> None:
        """
        Sets the additionalData property value. Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
        Args:
            value: Value to set for the AdditionalData property.
        """
        self._additional_data = value
    
    @staticmethod
    def create_from_discriminator_value(parse_node: Optional[ParseNode] = None) -> UpdateState:
        """
        Creates a new instance of the appropriate class based on discriminator value
        Args:
            parseNode: The parse node to use to read the discriminator value and create the object
        Returns: UpdateState
        """
        if parse_node is None:
            raise Exception("parse_node cannot be undefined")
        return UpdateState()
    
    def get_field_deserializers(self,) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        from . import artifact_state

        fields: Dict[str, Callable[[Any], None]] = {
            "state": lambda n : setattr(self, 'state', n.get_enum_value(artifact_state.ArtifactState)),
        }
        return fields
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        Args:
            writer: Serialization writer to use to serialize this model
        """
        if writer is None:
            raise Exception("writer cannot be undefined")
        writer.write_enum_value("state", self.state)
        writer.write_additional_data_value(self.additional_data)
    
    @property
    def state(self,) -> Optional[artifact_state.ArtifactState]:
        """
        Gets the state property value. Describes the state of an artifact or artifact version.  The following statesare possible:* ENABLED* DISABLED* DEPRECATED
        Returns: Optional[artifact_state.ArtifactState]
        """
        return self._state
    
    @state.setter
    def state(self,value: Optional[artifact_state.ArtifactState] = None) -> None:
        """
        Sets the state property value. Describes the state of an artifact or artifact version.  The following statesare possible:* ENABLED* DISABLED* DEPRECATED
        Args:
            value: Value to set for the state property.
        """
        self._state = value
    

