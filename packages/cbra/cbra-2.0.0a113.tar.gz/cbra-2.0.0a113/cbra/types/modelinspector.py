# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import collections
import inspect

import pydantic.fields
from pydantic.fields import ModelField
from .basemodel import BaseModel
from .modelmetadata import ModelMetadata
from .versionconflict import VersionConflict


class ModelInspector:
    __module__: str = 'cbra.types'

    def check_metadata(self, old: ModelMetadata | None, new: ModelMetadata) -> bool:
        """Check if the metadata state is valid. Mainly used to prevent
        version conflicts.
        """
        if old is None:
            return True
        if old.generation != new.generation:
            raise VersionConflict(f'Version mismatch: {old.generation} != {new.generation}')
        return True

    def get_column_fields(
        self,
        model: type[BaseModel] | BaseModel
    ) -> dict[str, pydantic.fields.ModelField]:
        """Return a mapping for field names for :class:`pydantic.field.ModelField`
        instances representing the fields that are not first-class storage
        entities i.e. having their own table or being a distinct kind.
        """
        return collections.OrderedDict([
            (k, v)
            for k, v in model.__fields__.items()
            if not self.is_first_class_entity(v.type_)
        ])
    
    def get_entity_name(self, model: type[BaseModel] | BaseModel) -> str:
        """Return the entity name of the model. The default implementation
        returns the class name.
        """
        if model.Config.title:
            return model.Config.title
        if isinstance(model, BaseModel):
            model = type(model)
        return model.__name__
    
    def has_children(self, model: type[BaseModel] | BaseModel) -> bool:
        """Return a boolean indicating if the model has child entities."""
        return any([
            self.is_first_class_entity(field.type_)
            for field in model.__fields__.values()
        ])
    
    def auto_increments(self, obj: type[BaseModel] | BaseModel) -> bool:
        """Return a boolean indicating if the model has an auto incrementing
        field.
        """
        raise NotImplementedError
    
    def get_primary_key_field(self, obj: type[BaseModel] | BaseModel) -> ModelField | None:
        """"""
        for model_field in obj.__fields__.values():
            if not model_field.field_info.extra.get('primary_key'):
                continue
            field = model_field
            break
        else:
            field = None
        return field
    
    def has_identity(self, obj: type[BaseModel] | BaseModel) -> bool:
        """Return a boolean indicating if the model has an identity."""
        raise NotImplementedError

    def is_first_class_entity(self, obj: type) -> bool:
        """Return a boolean indicating if the type is a first-class
        entity.
        """
        return inspect.isclass(obj) and issubclass(obj, BaseModel)