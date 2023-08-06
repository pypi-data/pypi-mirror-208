from __future__ import annotations
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from . import rule_type

class Rule(AdditionalDataHolder, Parsable):
    def __init__(self,) -> None:
        """
        Instantiates a new Rule and sets the default values.
        """
        # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
        self._additional_data: Dict[str, Any] = {}

        # The config property
        self._config: Optional[str] = None
        # The type property
        self._type: Optional[rule_type.RuleType] = None
    
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
    def config(self,) -> Optional[str]:
        """
        Gets the config property value. The config property
        Returns: Optional[str]
        """
        return self._config
    
    @config.setter
    def config(self,value: Optional[str] = None) -> None:
        """
        Sets the config property value. The config property
        Args:
            value: Value to set for the config property.
        """
        self._config = value
    
    @staticmethod
    def create_from_discriminator_value(parse_node: Optional[ParseNode] = None) -> Rule:
        """
        Creates a new instance of the appropriate class based on discriminator value
        Args:
            parseNode: The parse node to use to read the discriminator value and create the object
        Returns: Rule
        """
        if parse_node is None:
            raise Exception("parse_node cannot be undefined")
        return Rule()
    
    def get_field_deserializers(self,) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        from . import rule_type

        fields: Dict[str, Callable[[Any], None]] = {
            "config": lambda n : setattr(self, 'config', n.get_str_value()),
            "type": lambda n : setattr(self, 'type', n.get_enum_value(rule_type.RuleType)),
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
        writer.write_str_value("config", self.config)
        writer.write_enum_value("type", self.type)
        writer.write_additional_data_value(self.additional_data)
    
    @property
    def type(self,) -> Optional[rule_type.RuleType]:
        """
        Gets the type property value. The type property
        Returns: Optional[rule_type.RuleType]
        """
        return self._type
    
    @type.setter
    def type(self,value: Optional[rule_type.RuleType] = None) -> None:
        """
        Sets the type property value. The type property
        Args:
            value: Value to set for the type property.
        """
        self._type = value
    

