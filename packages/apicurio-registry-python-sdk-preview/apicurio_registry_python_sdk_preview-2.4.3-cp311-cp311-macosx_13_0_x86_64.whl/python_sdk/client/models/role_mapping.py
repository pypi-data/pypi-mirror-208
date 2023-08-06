from __future__ import annotations
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from . import role_type

class RoleMapping(AdditionalDataHolder, Parsable):
    """
    The mapping between a user/principal and their role.
    """
    def __init__(self,) -> None:
        """
        Instantiates a new RoleMapping and sets the default values.
        """
        # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
        self._additional_data: Dict[str, Any] = {}

        # The principalId property
        self._principal_id: Optional[str] = None
        # A friendly name for the principal.
        self._principal_name: Optional[str] = None
        # The role property
        self._role: Optional[role_type.RoleType] = None
    
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
    def create_from_discriminator_value(parse_node: Optional[ParseNode] = None) -> RoleMapping:
        """
        Creates a new instance of the appropriate class based on discriminator value
        Args:
            parseNode: The parse node to use to read the discriminator value and create the object
        Returns: RoleMapping
        """
        if parse_node is None:
            raise Exception("parse_node cannot be undefined")
        return RoleMapping()
    
    def get_field_deserializers(self,) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        from . import role_type

        fields: Dict[str, Callable[[Any], None]] = {
            "principalId": lambda n : setattr(self, 'principal_id', n.get_str_value()),
            "principalName": lambda n : setattr(self, 'principal_name', n.get_str_value()),
            "role": lambda n : setattr(self, 'role', n.get_enum_value(role_type.RoleType)),
        }
        return fields
    
    @property
    def principal_id(self,) -> Optional[str]:
        """
        Gets the principalId property value. The principalId property
        Returns: Optional[str]
        """
        return self._principal_id
    
    @principal_id.setter
    def principal_id(self,value: Optional[str] = None) -> None:
        """
        Sets the principalId property value. The principalId property
        Args:
            value: Value to set for the principal_id property.
        """
        self._principal_id = value
    
    @property
    def principal_name(self,) -> Optional[str]:
        """
        Gets the principalName property value. A friendly name for the principal.
        Returns: Optional[str]
        """
        return self._principal_name
    
    @principal_name.setter
    def principal_name(self,value: Optional[str] = None) -> None:
        """
        Sets the principalName property value. A friendly name for the principal.
        Args:
            value: Value to set for the principal_name property.
        """
        self._principal_name = value
    
    @property
    def role(self,) -> Optional[role_type.RoleType]:
        """
        Gets the role property value. The role property
        Returns: Optional[role_type.RoleType]
        """
        return self._role
    
    @role.setter
    def role(self,value: Optional[role_type.RoleType] = None) -> None:
        """
        Sets the role property value. The role property
        Args:
            value: Value to set for the role property.
        """
        self._role = value
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        Args:
            writer: Serialization writer to use to serialize this model
        """
        if writer is None:
            raise Exception("writer cannot be undefined")
        writer.write_str_value("principalId", self.principal_id)
        writer.write_str_value("principalName", self.principal_name)
        writer.write_enum_value("role", self.role)
        writer.write_additional_data_value(self.additional_data)
    

