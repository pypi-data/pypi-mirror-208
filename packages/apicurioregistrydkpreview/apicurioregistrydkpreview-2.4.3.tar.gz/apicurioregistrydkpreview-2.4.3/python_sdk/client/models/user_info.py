from __future__ import annotations
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

class UserInfo(AdditionalDataHolder, Parsable):
    """
    Information about a single user.
    """
    def __init__(self,) -> None:
        """
        Instantiates a new UserInfo and sets the default values.
        """
        # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
        self._additional_data: Dict[str, Any] = {}

        # The admin property
        self._admin: Optional[bool] = None
        # The developer property
        self._developer: Optional[bool] = None
        # The displayName property
        self._display_name: Optional[str] = None
        # The username property
        self._username: Optional[str] = None
        # The viewer property
        self._viewer: Optional[bool] = None
    
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
    def admin(self,) -> Optional[bool]:
        """
        Gets the admin property value. The admin property
        Returns: Optional[bool]
        """
        return self._admin
    
    @admin.setter
    def admin(self,value: Optional[bool] = None) -> None:
        """
        Sets the admin property value. The admin property
        Args:
            value: Value to set for the admin property.
        """
        self._admin = value
    
    @staticmethod
    def create_from_discriminator_value(parse_node: Optional[ParseNode] = None) -> UserInfo:
        """
        Creates a new instance of the appropriate class based on discriminator value
        Args:
            parseNode: The parse node to use to read the discriminator value and create the object
        Returns: UserInfo
        """
        if parse_node is None:
            raise Exception("parse_node cannot be undefined")
        return UserInfo()
    
    @property
    def developer(self,) -> Optional[bool]:
        """
        Gets the developer property value. The developer property
        Returns: Optional[bool]
        """
        return self._developer
    
    @developer.setter
    def developer(self,value: Optional[bool] = None) -> None:
        """
        Sets the developer property value. The developer property
        Args:
            value: Value to set for the developer property.
        """
        self._developer = value
    
    @property
    def display_name(self,) -> Optional[str]:
        """
        Gets the displayName property value. The displayName property
        Returns: Optional[str]
        """
        return self._display_name
    
    @display_name.setter
    def display_name(self,value: Optional[str] = None) -> None:
        """
        Sets the displayName property value. The displayName property
        Args:
            value: Value to set for the display_name property.
        """
        self._display_name = value
    
    def get_field_deserializers(self,) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        fields: Dict[str, Callable[[Any], None]] = {
            "admin": lambda n : setattr(self, 'admin', n.get_bool_value()),
            "developer": lambda n : setattr(self, 'developer', n.get_bool_value()),
            "displayName": lambda n : setattr(self, 'display_name', n.get_str_value()),
            "username": lambda n : setattr(self, 'username', n.get_str_value()),
            "viewer": lambda n : setattr(self, 'viewer', n.get_bool_value()),
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
        writer.write_bool_value("admin", self.admin)
        writer.write_bool_value("developer", self.developer)
        writer.write_str_value("displayName", self.display_name)
        writer.write_str_value("username", self.username)
        writer.write_bool_value("viewer", self.viewer)
        writer.write_additional_data_value(self.additional_data)
    
    @property
    def username(self,) -> Optional[str]:
        """
        Gets the username property value. The username property
        Returns: Optional[str]
        """
        return self._username
    
    @username.setter
    def username(self,value: Optional[str] = None) -> None:
        """
        Sets the username property value. The username property
        Args:
            value: Value to set for the username property.
        """
        self._username = value
    
    @property
    def viewer(self,) -> Optional[bool]:
        """
        Gets the viewer property value. The viewer property
        Returns: Optional[bool]
        """
        return self._viewer
    
    @viewer.setter
    def viewer(self,value: Optional[bool] = None) -> None:
        """
        Sets the viewer property value. The viewer property
        Args:
            value: Value to set for the viewer property.
        """
        self._viewer = value
    

