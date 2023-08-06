from __future__ import annotations
from datetime import datetime
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from . import artifact_reference, artifact_state, properties

class SearchedVersion(AdditionalDataHolder, Parsable):
    """
    Models a single artifact from the result set returned when searching for artifacts.
    """
    def __init__(self,) -> None:
        """
        Instantiates a new SearchedVersion and sets the default values.
        """
        # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
        self._additional_data: Dict[str, Any] = {}

        # The contentId property
        self._content_id: Optional[int] = None
        # The createdBy property
        self._created_by: Optional[str] = None
        # The createdOn property
        self._created_on: Optional[datetime] = None
        # The description property
        self._description: Optional[str] = None
        # The globalId property
        self._global_id: Optional[int] = None
        # The labels property
        self._labels: Optional[List[str]] = None
        # The name property
        self._name: Optional[str] = None
        # User-defined name-value pairs. Name and value must be strings.
        self._properties: Optional[properties.Properties] = None
        # The references property
        self._references: Optional[List[artifact_reference.ArtifactReference]] = None
        # Describes the state of an artifact or artifact version.  The following statesare possible:* ENABLED* DISABLED* DEPRECATED
        self._state: Optional[artifact_state.ArtifactState] = None
        # The type property
        self._type: Optional[str] = None
        # The version property
        self._version: Optional[str] = None
    
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
    def content_id(self,) -> Optional[int]:
        """
        Gets the contentId property value. The contentId property
        Returns: Optional[int]
        """
        return self._content_id
    
    @content_id.setter
    def content_id(self,value: Optional[int] = None) -> None:
        """
        Sets the contentId property value. The contentId property
        Args:
            value: Value to set for the content_id property.
        """
        self._content_id = value
    
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
    def create_from_discriminator_value(parse_node: Optional[ParseNode] = None) -> SearchedVersion:
        """
        Creates a new instance of the appropriate class based on discriminator value
        Args:
            parseNode: The parse node to use to read the discriminator value and create the object
        Returns: SearchedVersion
        """
        if parse_node is None:
            raise Exception("parse_node cannot be undefined")
        return SearchedVersion()
    
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
        from . import artifact_reference, artifact_state, properties

        fields: Dict[str, Callable[[Any], None]] = {
            "contentId": lambda n : setattr(self, 'content_id', n.get_int_value()),
            "createdBy": lambda n : setattr(self, 'created_by', n.get_str_value()),
            "createdOn": lambda n : setattr(self, 'created_on', n.get_datetime_value()),
            "description": lambda n : setattr(self, 'description', n.get_str_value()),
            "globalId": lambda n : setattr(self, 'global_id', n.get_int_value()),
            "labels": lambda n : setattr(self, 'labels', n.get_collection_of_primitive_values(str)),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "properties": lambda n : setattr(self, 'properties', n.get_object_value(properties.Properties)),
            "references": lambda n : setattr(self, 'references', n.get_collection_of_object_values(artifact_reference.ArtifactReference)),
            "state": lambda n : setattr(self, 'state', n.get_enum_value(artifact_state.ArtifactState)),
            "type": lambda n : setattr(self, 'type', n.get_str_value()),
            "version": lambda n : setattr(self, 'version', n.get_str_value()),
        }
        return fields
    
    @property
    def global_id(self,) -> Optional[int]:
        """
        Gets the globalId property value. The globalId property
        Returns: Optional[int]
        """
        return self._global_id
    
    @global_id.setter
    def global_id(self,value: Optional[int] = None) -> None:
        """
        Sets the globalId property value. The globalId property
        Args:
            value: Value to set for the global_id property.
        """
        self._global_id = value
    
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
    
    @property
    def references(self,) -> Optional[List[artifact_reference.ArtifactReference]]:
        """
        Gets the references property value. The references property
        Returns: Optional[List[artifact_reference.ArtifactReference]]
        """
        return self._references
    
    @references.setter
    def references(self,value: Optional[List[artifact_reference.ArtifactReference]] = None) -> None:
        """
        Sets the references property value. The references property
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
        writer.write_int_value("contentId", self.content_id)
        writer.write_str_value("createdBy", self.created_by)
        writer.write_datetime_value("createdOn", self.created_on)
        writer.write_str_value("description", self.description)
        writer.write_int_value("globalId", self.global_id)
        writer.write_collection_of_primitive_values("labels", self.labels)
        writer.write_str_value("name", self.name)
        writer.write_object_value("properties", self.properties)
        writer.write_collection_of_object_values("references", self.references)
        writer.write_enum_value("state", self.state)
        writer.write_str_value("type", self.type)
        writer.write_str_value("version", self.version)
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
    
    @property
    def version(self,) -> Optional[str]:
        """
        Gets the version property value. The version property
        Returns: Optional[str]
        """
        return self._version
    
    @version.setter
    def version(self,value: Optional[str] = None) -> None:
        """
        Sets the version property value. The version property
        Args:
            value: Value to set for the version property.
        """
        self._version = value
    

