from __future__ import annotations
from datetime import datetime
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from . import artifact_state

class SearchedArtifact(AdditionalDataHolder, Parsable):
    """
    Models a single artifact from the result set returned when searching for artifacts.
    """
    def __init__(self,) -> None:
        """
        Instantiates a new SearchedArtifact and sets the default values.
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
        self._group_id: Optional[str] = None
        # The ID of a single artifact.
        self._id: Optional[str] = None
        # The labels property
        self._labels: Optional[List[str]] = None
        # The modifiedBy property
        self._modified_by: Optional[str] = None
        # The modifiedOn property
        self._modified_on: Optional[datetime] = None
        # The name property
        self._name: Optional[str] = None
        # Describes the state of an artifact or artifact version.  The following statesare possible:* ENABLED* DISABLED* DEPRECATED
        self._state: Optional[artifact_state.ArtifactState] = None
        # The type property
        self._type: Optional[str] = None
    
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
    def create_from_discriminator_value(parse_node: Optional[ParseNode] = None) -> SearchedArtifact:
        """
        Creates a new instance of the appropriate class based on discriminator value
        Args:
            parseNode: The parse node to use to read the discriminator value and create the object
        Returns: SearchedArtifact
        """
        if parse_node is None:
            raise Exception("parse_node cannot be undefined")
        return SearchedArtifact()
    
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
        from . import artifact_state

        fields: Dict[str, Callable[[Any], None]] = {
            "createdBy": lambda n : setattr(self, 'created_by', n.get_str_value()),
            "createdOn": lambda n : setattr(self, 'created_on', n.get_datetime_value()),
            "description": lambda n : setattr(self, 'description', n.get_str_value()),
            "groupId": lambda n : setattr(self, 'group_id', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_str_value()),
            "labels": lambda n : setattr(self, 'labels', n.get_collection_of_primitive_values(str)),
            "modifiedBy": lambda n : setattr(self, 'modified_by', n.get_str_value()),
            "modifiedOn": lambda n : setattr(self, 'modified_on', n.get_datetime_value()),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "state": lambda n : setattr(self, 'state', n.get_enum_value(artifact_state.ArtifactState)),
            "type": lambda n : setattr(self, 'type', n.get_str_value()),
        }
        return fields
    
    @property
    def group_id(self,) -> Optional[str]:
        """
        Gets the groupId property value. An ID of a single artifact group.
        Returns: Optional[str]
        """
        return self._group_id
    
    @group_id.setter
    def group_id(self,value: Optional[str] = None) -> None:
        """
        Sets the groupId property value. An ID of a single artifact group.
        Args:
            value: Value to set for the group_id property.
        """
        self._group_id = value
    
    @property
    def id(self,) -> Optional[str]:
        """
        Gets the id property value. The ID of a single artifact.
        Returns: Optional[str]
        """
        return self._id
    
    @id.setter
    def id(self,value: Optional[str] = None) -> None:
        """
        Sets the id property value. The ID of a single artifact.
        Args:
            value: Value to set for the id property.
        """
        self._id = value
    
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
        writer.write_str_value("groupId", self.group_id)
        writer.write_str_value("id", self.id)
        writer.write_collection_of_primitive_values("labels", self.labels)
        writer.write_str_value("modifiedBy", self.modified_by)
        writer.write_datetime_value("modifiedOn", self.modified_on)
        writer.write_str_value("name", self.name)
        writer.write_enum_value("state", self.state)
        writer.write_str_value("type", self.type)
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
    
    @property
    def type(self,) -> Optional[str]:
        """
        Gets the type property value. The type property
        Returns: Optional[str]
        """
        return self._type
    
    @type.setter
    def type(self,value: Optional[str] = None) -> None:
        """
        Sets the type property value. The type property
        Args:
            value: Value to set for the type property.
        """
        self._type = value
    

