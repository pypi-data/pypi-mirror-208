from __future__ import annotations
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from . import searched_version

class VersionSearchResults(AdditionalDataHolder, Parsable):
    """
    Describes the response received when searching for artifacts.
    """
    def __init__(self,) -> None:
        """
        Instantiates a new VersionSearchResults and sets the default values.
        """
        # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
        self._additional_data: Dict[str, Any] = {}

        # The total number of versions that matched the query (may be more than the number of versionsreturned in the result set).
        self._count: Optional[int] = None
        # The collection of artifact versions returned in the result set.
        self._versions: Optional[List[searched_version.SearchedVersion]] = None
    
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
    def count(self,) -> Optional[int]:
        """
        Gets the count property value. The total number of versions that matched the query (may be more than the number of versionsreturned in the result set).
        Returns: Optional[int]
        """
        return self._count
    
    @count.setter
    def count(self,value: Optional[int] = None) -> None:
        """
        Sets the count property value. The total number of versions that matched the query (may be more than the number of versionsreturned in the result set).
        Args:
            value: Value to set for the count property.
        """
        self._count = value
    
    @staticmethod
    def create_from_discriminator_value(parse_node: Optional[ParseNode] = None) -> VersionSearchResults:
        """
        Creates a new instance of the appropriate class based on discriminator value
        Args:
            parseNode: The parse node to use to read the discriminator value and create the object
        Returns: VersionSearchResults
        """
        if parse_node is None:
            raise Exception("parse_node cannot be undefined")
        return VersionSearchResults()
    
    def get_field_deserializers(self,) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        from . import searched_version

        fields: Dict[str, Callable[[Any], None]] = {
            "count": lambda n : setattr(self, 'count', n.get_int_value()),
            "versions": lambda n : setattr(self, 'versions', n.get_collection_of_object_values(searched_version.SearchedVersion)),
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
        writer.write_int_value("count", self.count)
        writer.write_collection_of_object_values("versions", self.versions)
        writer.write_additional_data_value(self.additional_data)
    
    @property
    def versions(self,) -> Optional[List[searched_version.SearchedVersion]]:
        """
        Gets the versions property value. The collection of artifact versions returned in the result set.
        Returns: Optional[List[searched_version.SearchedVersion]]
        """
        return self._versions
    
    @versions.setter
    def versions(self,value: Optional[List[searched_version.SearchedVersion]] = None) -> None:
        """
        Sets the versions property value. The collection of artifact versions returned in the result set.
        Args:
            value: Value to set for the versions property.
        """
        self._versions = value
    

