# app/metadata/custom_fields.py
"""
Custom Fields & Metadata Management
Dynamic field definitions, validation, and templates.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any
from datetime import datetime


class FieldType(Enum):
    """Field data types."""
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"
    SELECT = "select"
    MULTISELECT = "multiselect"
    EMAIL = "email"
    URL = "url"
    CURRENCY = "currency"
    JSON = "json"


class ValidationRule(Enum):
    """Validation rules."""
    REQUIRED = "required"
    UNIQUE = "unique"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    PATTERN = "pattern"
    MIN_VALUE = "min_value"
    MAX_VALUE = "max_value"


@dataclass
class FieldValidator:
    """Field validator."""
    rule: ValidationRule
    value: Any = None
    error_message: str = ""
    
    def to_dict(self):
        return {
            'rule': self.rule.value,
            'value': self.value,
            'error_message': self.error_message
        }


@dataclass
class CustomField:
    """Custom field definition."""
    id: str
    name: str
    field_type: FieldType
    description: str = ""
    required: bool = False
    default_value: Optional[Any] = None
    options: List[str] = field(default_factory=list)  # For select fields
    validators: List[FieldValidator] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    visible_to_roles: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'field_type': self.field_type.value,
            'description': self.description,
            'required': self.required,
            'default_value': self.default_value,
            'options': self.options,
            'validators': [v.to_dict() for v in self.validators],
            'metadata': self.metadata,
            'visible_to_roles': self.visible_to_roles,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


@dataclass
class FieldTemplate:
    """Field template for quick creation."""
    id: str
    name: str
    description: str = ""
    field_ids: List[str] = field(default_factory=list)
    applicable_to: List[str] = field(default_factory=list)  # entities like 'task', 'project'
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'field_ids': self.field_ids,
            'applicable_to': self.applicable_to,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class FieldValue:
    """Field value instance."""
    id: str
    entity_type: str  # task, project, etc.
    entity_id: str
    field_id: str
    value: Any
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'field_id': self.field_id,
            'value': self.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class CustomFieldManager:
    """Manage custom fields and metadata."""
    
    def __init__(self):
        self.fields: Dict[str, CustomField] = {}
        self.templates: Dict[str, FieldTemplate] = {}
        self.values: Dict[str, FieldValue] = {}
        self.field_counter = 0
        self.value_counter = 0
    
    def create_field(self, name: str, field_type: str, description: str = "", 
                    required: bool = False, options: List[str] = None):
        """Create custom field."""
        self.field_counter += 1
        field_id = f"fld_{self.field_counter}"
        
        field = CustomField(
            field_id, name, FieldType(field_type), description, required,
            options=options or []
        )
        self.fields[field_id] = field
        return field
    
    def get_field(self, field_id: str):
        """Get field."""
        return self.fields.get(field_id)
    
    def list_fields(self):
        """List all fields."""
        return [f.to_dict() for f in self.fields.values()]
    
    def update_field(self, field_id: str, **kwargs):
        """Update field."""
        field = self.fields.get(field_id)
        if not field:
            return False
        
        for key, value in kwargs.items():
            if hasattr(field, key):
                setattr(field, key, value)
        
        field.updated_at = datetime.utcnow()
        return True
    
    def add_validator(self, field_id: str, rule: str, value: Any = None, 
                     error_message: str = ""):
        """Add validator to field."""
        field = self.fields.get(field_id)
        if not field:
            return False
        
        validator = FieldValidator(ValidationRule(rule), value, error_message)
        field.validators.append(validator)
        return True
    
    def validate_value(self, field_id: str, value: Any):
        """Validate field value."""
        field = self.fields.get(field_id)
        if not field:
            return False, "Field not found"
        
        if field.required and value is None:
            return False, "Field is required"
        
        return True, "Valid"
    
    def create_template(self, name: str, description: str = "", 
                       field_ids: List[str] = None):
        """Create field template."""
        template_id = f"tpl_{len(self.templates) + 1}"
        template = FieldTemplate(template_id, name, description, field_ids or [])
        self.templates[template_id] = template
        return template
    
    def get_template(self, template_id: str):
        """Get template."""
        return self.templates.get(template_id)
    
    def apply_template(self, entity_type: str, entity_id: str, template_id: str):
        """Apply template to entity."""
        template = self.templates.get(template_id)
        if not template:
            return False
        
        # Create field values for each field in template
        for field_id in template.field_ids:
            field = self.fields.get(field_id)
            if field:
                self.set_field_value(entity_type, entity_id, field_id, field.default_value)
        
        return True
    
    def set_field_value(self, entity_type: str, entity_id: str, field_id: str, 
                       value: Any):
        """Set field value for entity."""
        valid, msg = self.validate_value(field_id, value)
        if not valid:
            return False
        
        # Check if value already exists
        for v in self.values.values():
            if (v.entity_type == entity_type and v.entity_id == entity_id 
                and v.field_id == field_id):
                v.value = value
                v.updated_at = datetime.utcnow()
                return True
        
        # Create new value
        self.value_counter += 1
        value_id = f"val_{self.value_counter}"
        field_value = FieldValue(value_id, entity_type, entity_id, field_id, value)
        self.values[value_id] = field_value
        return True
    
    def get_entity_values(self, entity_type: str, entity_id: str):
        """Get all field values for entity."""
        values = []
        for v in self.values.values():
            if v.entity_type == entity_type and v.entity_id == entity_id:
                values.append(v.to_dict())
        return values
    
    def get_metadata_stats(self):
        """Get metadata statistics."""
        return {
            'total_fields': len(self.fields),
            'total_templates': len(self.templates),
            'total_values': len(self.values),
            'field_types': {
                ft.value: len([f for f in self.fields.values() if f.field_type == ft])
                for ft in FieldType
            }
        }


# Global instance
custom_field_manager = CustomFieldManager()
