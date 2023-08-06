from __future__ import annotations
from datetime import datetime
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

class SearchedGroup(AdditionalDataHolder, Parsable):
    """
    Models a single group from the result set returned when searching for groups.
    """
    def __init__(self,) -> None:
        """
        Instantiates a new SearchedGroup and sets the default values.
        """
        # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
        self._additional_data: Dict[str, Any] = {}

        # The createdBy property
        self._created_by: Optional[str] = None
        # The createdOn property
        self._created_on: Optional[datetime] = None
        # The description property
        self._description: Optional[str] = None
        # An ID of a single artifact group.
        self._id: Optional[str] = None
        # The modifiedBy property
        self._modified_by: Optional[str] = None
        # The modifiedOn property
        self._modified_on: Optional[datetime] = None
    
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
    def created_by(self,) -> Optional[str]:
        """
        Gets the createdBy property value. The createdBy property
        Returns: Optional[str]
        """
        return self._created_by
    
    @created_by.setter
    def created_by(self,value: Optional[str] = None) -> None:
        """
        Sets the createdBy property value. The createdBy property
        Args:
            value: Value to set for the created_by property.
        """
        self._created_by = value
    
    @property
    def created_on(self,) -> Optional[datetime]:
        """
        Gets the createdOn property value. The createdOn property
        Returns: Optional[datetime]
        """
        return self._created_on
    
    @created_on.setter
    def created_on(self,value: Optional[datetime] = None) -> None:
        """
        Sets the createdOn property value. The createdOn property
        Args:
            value: Value to set for the created_on property.
        """
        self._created_on = value
    
    @staticmethod
    def create_from_discriminator_value(parse_node: Optional[ParseNode] = None) -> SearchedGroup:
        """
        Creates a new instance of the appropriate class based on discriminator value
        Args:
            parseNode: The parse node to use to read the discriminator value and create the object
        Returns: SearchedGroup
        """
        if parse_node is None:
            raise Exception("parse_node cannot be undefined")
        return SearchedGroup()
    
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
        fields: Dict[str, Callable[[Any], None]] = {
            "createdBy": lambda n : setattr(self, 'created_by', n.get_str_value()),
            "createdOn": lambda n : setattr(self, 'created_on', n.get_datetime_value()),
            "description": lambda n : setattr(self, 'description', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_str_value()),
            "modifiedBy": lambda n : setattr(self, 'modified_by', n.get_str_value()),
            "modifiedOn": lambda n : setattr(self, 'modified_on', n.get_datetime_value()),
        }
        return fields
    
    @property
    def id(self,) -> Optional[str]:
        """
        Gets the id property value. An ID of a single artifact group.
        Returns: Optional[str]
        """
        return self._id
    
    @id.setter
    def id(self,value: Optional[str] = None) -> None:
        """
        Sets the id property value. An ID of a single artifact group.
        Args:
            value: Value to set for the id property.
        """
        self._id = value
    
    @property
    def modified_by(self,) -> Optional[str]:
        """
        Gets the modifiedBy property value. The modifiedBy property
        Returns: Optional[str]
        """
        return self._modified_by
    
    @modified_by.setter
    def modified_by(self,value: Optional[str] = None) -> None:
        """
        Sets the modifiedBy property value. The modifiedBy property
        Args:
            value: Value to set for the modified_by property.
        """
        self._modified_by = value
    
    @property
    def modified_on(self,) -> Optional[datetime]:
        """
        Gets the modifiedOn property value. The modifiedOn property
        Returns: Optional[datetime]
        """
        return self._modified_on
    
    @modified_on.setter
    def modified_on(self,value: Optional[datetime] = None) -> None:
        """
        Sets the modifiedOn property value. The modifiedOn property
        Args:
            value: Value to set for the modified_on property.
        """
        self._modified_on = value
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        Args:
            writer: Serialization writer to use to serialize this model
        """
        if writer is None:
            raise Exception("writer cannot be undefined")
        writer.write_str_value("createdBy", self.created_by)
        writer.write_datetime_value("createdOn", self.created_on)
        writer.write_str_value("description", self.description)
        writer.write_str_value("id", self.id)
        writer.write_str_value("modifiedBy", self.modified_by)
        writer.write_datetime_value("modifiedOn", self.modified_on)
        writer.write_additional_data_value(self.additional_data)
    

