from __future__ import annotations
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from . import searched_artifact

class ArtifactSearchResults(AdditionalDataHolder, Parsable):
    """
    Describes the response received when searching for artifacts.
    """
    def __init__(self,) -> None:
        """
        Instantiates a new ArtifactSearchResults and sets the default values.
        """
        # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
        self._additional_data: Dict[str, Any] = {}

        # The artifacts returned in the result set.
        self._artifacts: Optional[List[searched_artifact.SearchedArtifact]] = None
        # The total number of artifacts that matched the query that produced the result set (may be more than the number of artifacts in the result set).
        self._count: Optional[int] = None
    
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
    def artifacts(self,) -> Optional[List[searched_artifact.SearchedArtifact]]:
        """
        Gets the artifacts property value. The artifacts returned in the result set.
        Returns: Optional[List[searched_artifact.SearchedArtifact]]
        """
        return self._artifacts
    
    @artifacts.setter
    def artifacts(self,value: Optional[List[searched_artifact.SearchedArtifact]] = None) -> None:
        """
        Sets the artifacts property value. The artifacts returned in the result set.
        Args:
            value: Value to set for the artifacts property.
        """
        self._artifacts = value
    
    @property
    def count(self,) -> Optional[int]:
        """
        Gets the count property value. The total number of artifacts that matched the query that produced the result set (may be more than the number of artifacts in the result set).
        Returns: Optional[int]
        """
        return self._count
    
    @count.setter
    def count(self,value: Optional[int] = None) -> None:
        """
        Sets the count property value. The total number of artifacts that matched the query that produced the result set (may be more than the number of artifacts in the result set).
        Args:
            value: Value to set for the count property.
        """
        self._count = value
    
    @staticmethod
    def create_from_discriminator_value(parse_node: Optional[ParseNode] = None) -> ArtifactSearchResults:
        """
        Creates a new instance of the appropriate class based on discriminator value
        Args:
            parseNode: The parse node to use to read the discriminator value and create the object
        Returns: ArtifactSearchResults
        """
        if parse_node is None:
            raise Exception("parse_node cannot be undefined")
        return ArtifactSearchResults()
    
    def get_field_deserializers(self,) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        from . import searched_artifact

        fields: Dict[str, Callable[[Any], None]] = {
            "artifacts": lambda n : setattr(self, 'artifacts', n.get_collection_of_object_values(searched_artifact.SearchedArtifact)),
            "count": lambda n : setattr(self, 'count', n.get_int_value()),
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
        writer.write_collection_of_object_values("artifacts", self.artifacts)
        writer.write_int_value("count", self.count)
        writer.write_additional_data_value(self.additional_data)
    

