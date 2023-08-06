from __future__ import annotations
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from . import searched_group

class GroupSearchResults(AdditionalDataHolder, Parsable):
    """
    Describes the response received when searching for groups.
    """
    def __init__(self,) -> None:
        """
        Instantiates a new GroupSearchResults and sets the default values.
        """
        # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
        self._additional_data: Dict[str, Any] = {}

        # The total number of groups that matched the query that produced the result set (may be more than the number of groups in the result set).
        self._count: Optional[int] = None
        # The groups returned in the result set.
        self._groups: Optional[List[searched_group.SearchedGroup]] = None
    
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
        Gets the count property value. The total number of groups that matched the query that produced the result set (may be more than the number of groups in the result set).
        Returns: Optional[int]
        """
        return self._count
    
    @count.setter
    def count(self,value: Optional[int] = None) -> None:
        """
        Sets the count property value. The total number of groups that matched the query that produced the result set (may be more than the number of groups in the result set).
        Args:
            value: Value to set for the count property.
        """
        self._count = value
    
    @staticmethod
    def create_from_discriminator_value(parse_node: Optional[ParseNode] = None) -> GroupSearchResults:
        """
        Creates a new instance of the appropriate class based on discriminator value
        Args:
            parseNode: The parse node to use to read the discriminator value and create the object
        Returns: GroupSearchResults
        """
        if parse_node is None:
            raise Exception("parse_node cannot be undefined")
        return GroupSearchResults()
    
    def get_field_deserializers(self,) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        from . import searched_group

        fields: Dict[str, Callable[[Any], None]] = {
            "count": lambda n : setattr(self, 'count', n.get_int_value()),
            "groups": lambda n : setattr(self, 'groups', n.get_collection_of_object_values(searched_group.SearchedGroup)),
        }
        return fields
    
    @property
    def groups(self,) -> Optional[List[searched_group.SearchedGroup]]:
        """
        Gets the groups property value. The groups returned in the result set.
        Returns: Optional[List[searched_group.SearchedGroup]]
        """
        return self._groups
    
    @groups.setter
    def groups(self,value: Optional[List[searched_group.SearchedGroup]] = None) -> None:
        """
        Sets the groups property value. The groups returned in the result set.
        Args:
            value: Value to set for the groups property.
        """
        self._groups = value
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        Args:
            writer: Serialization writer to use to serialize this model
        """
        if writer is None:
            raise Exception("writer cannot be undefined")
        writer.write_int_value("count", self.count)
        writer.write_collection_of_object_values("groups", self.groups)
        writer.write_additional_data_value(self.additional_data)
    

