from __future__ import annotations
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from . import artifact_reference

class ArtifactContent(AdditionalDataHolder, Parsable):
    def __init__(self,) -> None:
        """
        Instantiates a new ArtifactContent and sets the default values.
        """
        # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
        self._additional_data: Dict[str, Any] = {}

        # Raw content of the artifact or a valid (and accessible) URL where the content can be found.
        self._content: Optional[str] = None
        # Collection of references to other artifacts.
        self._references: Optional[List[artifact_reference.ArtifactReference]] = None
    
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
    
    @property
    def content(self,) -> Optional[str]:
        """
        Gets the content property value. Raw content of the artifact or a valid (and accessible) URL where the content can be found.
        Returns: Optional[str]
        """
        return self._content
    
    @content.setter
    def content(self,value: Optional[str] = None) -> None:
        """
        Sets the content property value. Raw content of the artifact or a valid (and accessible) URL where the content can be found.
        Args:
            value: Value to set for the content property.
        """
        self._content = value
    
    @staticmethod
    def create_from_discriminator_value(parse_node: Optional[ParseNode] = None) -> ArtifactContent:
        """
        Creates a new instance of the appropriate class based on discriminator value
        Args:
            parseNode: The parse node to use to read the discriminator value and create the object
        Returns: ArtifactContent
        """
        if parse_node is None:
            raise Exception("parse_node cannot be undefined")
        return ArtifactContent()
    
    def get_field_deserializers(self,) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        from . import artifact_reference

        fields: Dict[str, Callable[[Any], None]] = {
            "content": lambda n : setattr(self, 'content', n.get_str_value()),
            "references": lambda n : setattr(self, 'references', n.get_collection_of_object_values(artifact_reference.ArtifactReference)),
        }
        return fields
    
    @property
    def references(self,) -> Optional[List[artifact_reference.ArtifactReference]]:
        """
        Gets the references property value. Collection of references to other artifacts.
        Returns: Optional[List[artifact_reference.ArtifactReference]]
        """
        return self._references
    
    @references.setter
    def references(self,value: Optional[List[artifact_reference.ArtifactReference]] = None) -> None:
        """
        Sets the references property value. Collection of references to other artifacts.
        Args:
            value: Value to set for the references property.
        """
        self._references = value
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        Args:
            writer: Serialization writer to use to serialize this model
        """
        if writer is None:
            raise Exception("writer cannot be undefined")
        writer.write_str_value("content", self.content)
        writer.write_collection_of_object_values("references", self.references)
        writer.write_additional_data_value(self.additional_data)
    

