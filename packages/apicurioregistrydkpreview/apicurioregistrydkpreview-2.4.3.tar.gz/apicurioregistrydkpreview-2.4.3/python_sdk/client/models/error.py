from __future__ import annotations
from kiota_abstractions.api_error import APIError
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

class Error(APIError):
    """
    All error responses, whether `4xx` or `5xx` will include one of these as the responsebody.
    """
    def __init__(self,) -> None:
        """
        Instantiates a new Error and sets the default values.
        """
        # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
        self._additional_data: Dict[str, Any] = {}

        # Full details about the error.  This might contain a server stack trace, for example.
        self._detail: Optional[str] = None
        # The server-side error code.
        self._error_code: Optional[int] = None
        # The short error message.
        self._message: Optional[str] = None
        # The error name - typically the classname of the exception thrown by the server.
        self._name: Optional[str] = None
    
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
    def create_from_discriminator_value(parse_node: Optional[ParseNode] = None) -> Error:
        """
        Creates a new instance of the appropriate class based on discriminator value
        Args:
            parseNode: The parse node to use to read the discriminator value and create the object
        Returns: Error
        """
        if parse_node is None:
            raise Exception("parse_node cannot be undefined")
        return Error()
    
    @property
    def detail(self,) -> Optional[str]:
        """
        Gets the detail property value. Full details about the error.  This might contain a server stack trace, for example.
        Returns: Optional[str]
        """
        return self._detail
    
    @detail.setter
    def detail(self,value: Optional[str] = None) -> None:
        """
        Sets the detail property value. Full details about the error.  This might contain a server stack trace, for example.
        Args:
            value: Value to set for the detail property.
        """
        self._detail = value
    
    @property
    def error_code(self,) -> Optional[int]:
        """
        Gets the error_code property value. The server-side error code.
        Returns: Optional[int]
        """
        return self._error_code
    
    @error_code.setter
    def error_code(self,value: Optional[int] = None) -> None:
        """
        Sets the error_code property value. The server-side error code.
        Args:
            value: Value to set for the error_code property.
        """
        self._error_code = value
    
    def get_field_deserializers(self,) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        fields: Dict[str, Callable[[Any], None]] = {
            "detail": lambda n : setattr(self, 'detail', n.get_str_value()),
            "error_code": lambda n : setattr(self, 'error_code', n.get_int_value()),
            "message": lambda n : setattr(self, 'message', n.get_str_value()),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
        }
        return fields
    
    @property
    def message(self,) -> Optional[str]:
        """
        Gets the message property value. The short error message.
        Returns: Optional[str]
        """
        return self._message
    
    @message.setter
    def message(self,value: Optional[str] = None) -> None:
        """
        Sets the message property value. The short error message.
        Args:
            value: Value to set for the message property.
        """
        self._message = value
    
    @property
    def name(self,) -> Optional[str]:
        """
        Gets the name property value. The error name - typically the classname of the exception thrown by the server.
        Returns: Optional[str]
        """
        return self._name
    
    @name.setter
    def name(self,value: Optional[str] = None) -> None:
        """
        Sets the name property value. The error name - typically the classname of the exception thrown by the server.
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
        writer.write_str_value("detail", self.detail)
        writer.write_int_value("error_code", self.error_code)
        writer.write_str_value("message", self.message)
        writer.write_str_value("name", self.name)
        writer.write_additional_data_value(self.additional_data)
    

