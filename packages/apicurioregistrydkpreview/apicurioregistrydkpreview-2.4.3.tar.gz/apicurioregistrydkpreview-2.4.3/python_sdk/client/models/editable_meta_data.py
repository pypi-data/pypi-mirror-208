from __future__ import annotations
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from . import properties

class EditableMetaData(AdditionalDataHolder, Parsable):
    def __init__(self,) -> None:
        """
        Instantiates a new EditableMetaData and sets the default values.
        """
        # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
        self._additional_data: Dict[str, Any] = {}

        # The description property
        self._description: Optional[str] = None
        # The labels property
        self._labels: Optional[List[str]] = None
        # The name property
        self._name: Optional[str] = None
        # User-defined name-value pairs. Name and value must be strings.
        self._properties: Optional[properties.Properties] = None
    
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
    def create_from_discriminator_value(parse_node: Optional[ParseNode] = None) -> EditableMetaData:
        """
        Creates a new instance of the appropriate class based on discriminator value
        Args:
            parseNode: The parse node to use to read the discriminator value and create the object
        Returns: EditableMetaData
        """
        if parse_node is None:
            raise Exception("parse_node cannot be undefined")
        return EditableMetaData()
    
    @property
    def description(self,) -> Optional[str]:
        """
        Gets the description property value. The description property
        Returns: Optional[str]
        """
        return self._description
    
    @description.setter
    def description(self,value: Optional[str] = None) -> None:
        """
        Sets the description property value. The description property
        Args:
            value: Value to set for the description property.
        """
        self._description = value
    
    def get_field_deserializers(self,) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        from . import properties

        fields: Dict[str, Callable[[Any], None]] = {
            "description": lambda n : setattr(self, 'description', n.get_str_value()),
            "labels": lambda n : setattr(self, 'labels', n.get_collection_of_primitive_values(str)),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "properties": lambda n : setattr(self, 'properties', n.get_object_value(properties.Properties)),
        }
        return fields
    
    @property
    def labels(self,) -> Optional[List[str]]:
        """
        Gets the labels property value. The labels property
        Returns: Optional[List[str]]
        """
        return self._labels
    
    @labels.setter
    def labels(self,value: Optional[List[str]] = None) -> None:
        """
        Sets the labels property value. The labels property
        Args:
            value: Value to set for the labels property.
        """
        self._labels = value
    
    @property
    def name(self,) -> Optional[str]:
        """
        Gets the name property value. The name property
        Returns: Optional[str]
        """
        return self._name
    
    @name.setter
    def name(self,value: Optional[str] = None) -> None:
        """
        Sets the name property value. The name property
        Args:
            value: Value to set for the name property.
        """
        self._name = value
    
    @property
    def properties(self,) -> Optional[properties.Properties]:
        """
        Gets the properties property value. User-defined name-value pairs. Name and value must be strings.
        Returns: Optional[properties.Properties]
        """
        return self._properties
    
    @properties.setter
    def properties(self,value: Optional[properties.Properties] = None) -> None:
        """
        Sets the properties property value. User-defined name-value pairs. Name and value must be strings.
        Args:
            value: Value to set for the properties property.
        """
        self._properties = value
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        Args:
            writer: Serialization writer to use to serialize this model
        """
        if writer is None:
            raise Exception("writer cannot be undefined")
        writer.write_str_value("description", self.description)
        writer.write_collection_of_primitive_values("labels", self.labels)
        writer.write_str_value("name", self.name)
        writer.write_object_value("properties", self.properties)
        writer.write_additional_data_value(self.additional_data)
    

