from __future__ import annotations
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

class Limits(AdditionalDataHolder, Parsable):
    """
    List of limitations on used resources, that are applied on the current instance of Registry.Keys represent the resource type and are suffixed by the corresponding unit.Values are integers. Only non-negative values are allowed, with the exception of -1, which means that the limit is not applied.
    """
    def __init__(self,) -> None:
        """
        Instantiates a new Limits and sets the default values.
        """
        # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
        self._additional_data: Dict[str, Any] = {}

        # The maxArtifactDescriptionLengthChars property
        self._max_artifact_description_length_chars: Optional[int] = None
        # The maxArtifactLabelsCount property
        self._max_artifact_labels_count: Optional[int] = None
        # The maxArtifactNameLengthChars property
        self._max_artifact_name_length_chars: Optional[int] = None
        # The maxArtifactPropertiesCount property
        self._max_artifact_properties_count: Optional[int] = None
        # The maxArtifactsCount property
        self._max_artifacts_count: Optional[int] = None
        # The maxLabelSizeBytes property
        self._max_label_size_bytes: Optional[int] = None
        # The maxPropertyKeySizeBytes property
        self._max_property_key_size_bytes: Optional[int] = None
        # The maxPropertyValueSizeBytes property
        self._max_property_value_size_bytes: Optional[int] = None
        # The maxRequestsPerSecondCount property
        self._max_requests_per_second_count: Optional[int] = None
        # The maxSchemaSizeBytes property
        self._max_schema_size_bytes: Optional[int] = None
        # The maxTotalSchemasCount property
        self._max_total_schemas_count: Optional[int] = None
        # The maxVersionsPerArtifactCount property
        self._max_versions_per_artifact_count: Optional[int] = None
    
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
    def create_from_discriminator_value(parse_node: Optional[ParseNode] = None) -> Limits:
        """
        Creates a new instance of the appropriate class based on discriminator value
        Args:
            parseNode: The parse node to use to read the discriminator value and create the object
        Returns: Limits
        """
        if parse_node is None:
            raise Exception("parse_node cannot be undefined")
        return Limits()
    
    def get_field_deserializers(self,) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        fields: Dict[str, Callable[[Any], None]] = {
            "maxArtifactsCount": lambda n : setattr(self, 'max_artifacts_count', n.get_int_value()),
            "maxArtifactDescriptionLengthChars": lambda n : setattr(self, 'max_artifact_description_length_chars', n.get_int_value()),
            "maxArtifactLabelsCount": lambda n : setattr(self, 'max_artifact_labels_count', n.get_int_value()),
            "maxArtifactNameLengthChars": lambda n : setattr(self, 'max_artifact_name_length_chars', n.get_int_value()),
            "maxArtifactPropertiesCount": lambda n : setattr(self, 'max_artifact_properties_count', n.get_int_value()),
            "maxLabelSizeBytes": lambda n : setattr(self, 'max_label_size_bytes', n.get_int_value()),
            "maxPropertyKeySizeBytes": lambda n : setattr(self, 'max_property_key_size_bytes', n.get_int_value()),
            "maxPropertyValueSizeBytes": lambda n : setattr(self, 'max_property_value_size_bytes', n.get_int_value()),
            "maxRequestsPerSecondCount": lambda n : setattr(self, 'max_requests_per_second_count', n.get_int_value()),
            "maxSchemaSizeBytes": lambda n : setattr(self, 'max_schema_size_bytes', n.get_int_value()),
            "maxTotalSchemasCount": lambda n : setattr(self, 'max_total_schemas_count', n.get_int_value()),
            "maxVersionsPerArtifactCount": lambda n : setattr(self, 'max_versions_per_artifact_count', n.get_int_value()),
        }
        return fields
    
    @property
    def max_artifact_description_length_chars(self,) -> Optional[int]:
        """
        Gets the maxArtifactDescriptionLengthChars property value. The maxArtifactDescriptionLengthChars property
        Returns: Optional[int]
        """
        return self._max_artifact_description_length_chars
    
    @max_artifact_description_length_chars.setter
    def max_artifact_description_length_chars(self,value: Optional[int] = None) -> None:
        """
        Sets the maxArtifactDescriptionLengthChars property value. The maxArtifactDescriptionLengthChars property
        Args:
            value: Value to set for the max_artifact_description_length_chars property.
        """
        self._max_artifact_description_length_chars = value
    
    @property
    def max_artifact_labels_count(self,) -> Optional[int]:
        """
        Gets the maxArtifactLabelsCount property value. The maxArtifactLabelsCount property
        Returns: Optional[int]
        """
        return self._max_artifact_labels_count
    
    @max_artifact_labels_count.setter
    def max_artifact_labels_count(self,value: Optional[int] = None) -> None:
        """
        Sets the maxArtifactLabelsCount property value. The maxArtifactLabelsCount property
        Args:
            value: Value to set for the max_artifact_labels_count property.
        """
        self._max_artifact_labels_count = value
    
    @property
    def max_artifact_name_length_chars(self,) -> Optional[int]:
        """
        Gets the maxArtifactNameLengthChars property value. The maxArtifactNameLengthChars property
        Returns: Optional[int]
        """
        return self._max_artifact_name_length_chars
    
    @max_artifact_name_length_chars.setter
    def max_artifact_name_length_chars(self,value: Optional[int] = None) -> None:
        """
        Sets the maxArtifactNameLengthChars property value. The maxArtifactNameLengthChars property
        Args:
            value: Value to set for the max_artifact_name_length_chars property.
        """
        self._max_artifact_name_length_chars = value
    
    @property
    def max_artifact_properties_count(self,) -> Optional[int]:
        """
        Gets the maxArtifactPropertiesCount property value. The maxArtifactPropertiesCount property
        Returns: Optional[int]
        """
        return self._max_artifact_properties_count
    
    @max_artifact_properties_count.setter
    def max_artifact_properties_count(self,value: Optional[int] = None) -> None:
        """
        Sets the maxArtifactPropertiesCount property value. The maxArtifactPropertiesCount property
        Args:
            value: Value to set for the max_artifact_properties_count property.
        """
        self._max_artifact_properties_count = value
    
    @property
    def max_artifacts_count(self,) -> Optional[int]:
        """
        Gets the maxArtifactsCount property value. The maxArtifactsCount property
        Returns: Optional[int]
        """
        return self._max_artifacts_count
    
    @max_artifacts_count.setter
    def max_artifacts_count(self,value: Optional[int] = None) -> None:
        """
        Sets the maxArtifactsCount property value. The maxArtifactsCount property
        Args:
            value: Value to set for the max_artifacts_count property.
        """
        self._max_artifacts_count = value
    
    @property
    def max_label_size_bytes(self,) -> Optional[int]:
        """
        Gets the maxLabelSizeBytes property value. The maxLabelSizeBytes property
        Returns: Optional[int]
        """
        return self._max_label_size_bytes
    
    @max_label_size_bytes.setter
    def max_label_size_bytes(self,value: Optional[int] = None) -> None:
        """
        Sets the maxLabelSizeBytes property value. The maxLabelSizeBytes property
        Args:
            value: Value to set for the max_label_size_bytes property.
        """
        self._max_label_size_bytes = value
    
    @property
    def max_property_key_size_bytes(self,) -> Optional[int]:
        """
        Gets the maxPropertyKeySizeBytes property value. The maxPropertyKeySizeBytes property
        Returns: Optional[int]
        """
        return self._max_property_key_size_bytes
    
    @max_property_key_size_bytes.setter
    def max_property_key_size_bytes(self,value: Optional[int] = None) -> None:
        """
        Sets the maxPropertyKeySizeBytes property value. The maxPropertyKeySizeBytes property
        Args:
            value: Value to set for the max_property_key_size_bytes property.
        """
        self._max_property_key_size_bytes = value
    
    @property
    def max_property_value_size_bytes(self,) -> Optional[int]:
        """
        Gets the maxPropertyValueSizeBytes property value. The maxPropertyValueSizeBytes property
        Returns: Optional[int]
        """
        return self._max_property_value_size_bytes
    
    @max_property_value_size_bytes.setter
    def max_property_value_size_bytes(self,value: Optional[int] = None) -> None:
        """
        Sets the maxPropertyValueSizeBytes property value. The maxPropertyValueSizeBytes property
        Args:
            value: Value to set for the max_property_value_size_bytes property.
        """
        self._max_property_value_size_bytes = value
    
    @property
    def max_requests_per_second_count(self,) -> Optional[int]:
        """
        Gets the maxRequestsPerSecondCount property value. The maxRequestsPerSecondCount property
        Returns: Optional[int]
        """
        return self._max_requests_per_second_count
    
    @max_requests_per_second_count.setter
    def max_requests_per_second_count(self,value: Optional[int] = None) -> None:
        """
        Sets the maxRequestsPerSecondCount property value. The maxRequestsPerSecondCount property
        Args:
            value: Value to set for the max_requests_per_second_count property.
        """
        self._max_requests_per_second_count = value
    
    @property
    def max_schema_size_bytes(self,) -> Optional[int]:
        """
        Gets the maxSchemaSizeBytes property value. The maxSchemaSizeBytes property
        Returns: Optional[int]
        """
        return self._max_schema_size_bytes
    
    @max_schema_size_bytes.setter
    def max_schema_size_bytes(self,value: Optional[int] = None) -> None:
        """
        Sets the maxSchemaSizeBytes property value. The maxSchemaSizeBytes property
        Args:
            value: Value to set for the max_schema_size_bytes property.
        """
        self._max_schema_size_bytes = value
    
    @property
    def max_total_schemas_count(self,) -> Optional[int]:
        """
        Gets the maxTotalSchemasCount property value. The maxTotalSchemasCount property
        Returns: Optional[int]
        """
        return self._max_total_schemas_count
    
    @max_total_schemas_count.setter
    def max_total_schemas_count(self,value: Optional[int] = None) -> None:
        """
        Sets the maxTotalSchemasCount property value. The maxTotalSchemasCount property
        Args:
            value: Value to set for the max_total_schemas_count property.
        """
        self._max_total_schemas_count = value
    
    @property
    def max_versions_per_artifact_count(self,) -> Optional[int]:
        """
        Gets the maxVersionsPerArtifactCount property value. The maxVersionsPerArtifactCount property
        Returns: Optional[int]
        """
        return self._max_versions_per_artifact_count
    
    @max_versions_per_artifact_count.setter
    def max_versions_per_artifact_count(self,value: Optional[int] = None) -> None:
        """
        Sets the maxVersionsPerArtifactCount property value. The maxVersionsPerArtifactCount property
        Args:
            value: Value to set for the max_versions_per_artifact_count property.
        """
        self._max_versions_per_artifact_count = value
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        Args:
            writer: Serialization writer to use to serialize this model
        """
        if writer is None:
            raise Exception("writer cannot be undefined")
        writer.write_int_value("maxArtifactsCount", self.max_artifacts_count)
        writer.write_int_value("maxArtifactDescriptionLengthChars", self.max_artifact_description_length_chars)
        writer.write_int_value("maxArtifactLabelsCount", self.max_artifact_labels_count)
        writer.write_int_value("maxArtifactNameLengthChars", self.max_artifact_name_length_chars)
        writer.write_int_value("maxArtifactPropertiesCount", self.max_artifact_properties_count)
        writer.write_int_value("maxLabelSizeBytes", self.max_label_size_bytes)
        writer.write_int_value("maxPropertyKeySizeBytes", self.max_property_key_size_bytes)
        writer.write_int_value("maxPropertyValueSizeBytes", self.max_property_value_size_bytes)
        writer.write_int_value("maxRequestsPerSecondCount", self.max_requests_per_second_count)
        writer.write_int_value("maxSchemaSizeBytes", self.max_schema_size_bytes)
        writer.write_int_value("maxTotalSchemasCount", self.max_total_schemas_count)
        writer.write_int_value("maxVersionsPerArtifactCount", self.max_versions_per_artifact_count)
        writer.write_additional_data_value(self.additional_data)
    

