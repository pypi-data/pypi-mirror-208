from __future__ import annotations

from typing import Any, Callable, Optional, Type

import goodboy as gb
import mongoengine as me
from mongoengine.base.fields import BaseField

from goodboy_mongoengine.field_schemas import FieldSchemaBuilder, field_schema_builder


class Field(gb.Key):
    def __init__(
        self,
        name: str,
        schema: Optional[gb.Schema] = None,
        *,
        document_field_name: Optional[str] = None,
        required: Optional[bool] = None,
        default: Optional[Any] = None,
        predicate: Optional[Callable[[dict], bool]] = None,
        unique: bool = False,
    ):
        super().__init__(
            name, schema, required=required, default=default, predicate=predicate
        )

        has_default = default is not None

        if has_default and required:
            raise ValueError("key with default value cannot be required")

        self.has_default = has_default
        self.default = default
        self.document_field_name = document_field_name or name
        self.unique = unique

    def with_predicate(self, predicate: Callable[[dict], bool]) -> Field:
        return Field(
            self.name,
            self._schema,
            required=self.required,
            default=self.default,
            predicate=predicate,
            unique=self.unique,
        )

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__

        return super().__eq__(other)


class FieldBuilderError(Exception):
    pass


class FieldBuilder:
    def __init__(self, field_schema_builder: FieldSchemaBuilder):
        self._field_schema_builder = field_schema_builder

    def build(
        self, document_class: Type[me.Document], field_names: list[str]
    ) -> list[Field]:
        result: list[Field] = []

        for field_name in field_names:
            if field_name not in document_class._fields:
                document_class_name = document_class.__name__
                raise FieldBuilderError(
                    f"document class {document_class_name} has no field {field_name}"
                )

            mongo_field = document_class._fields[field_name]
            result.append(self._build_field(mongo_field, field_name))

        return result

    def _build_field(self, mongo_field: BaseField, field_name: str) -> Field:
        schema = self._field_schema_builder.build(mongo_field)

        if mongo_field.required:
            default = None
        else:
            default = mongo_field.default

        return Field(
            field_name,
            schema,
            required=mongo_field.required,
            default=default,
            unique=mongo_field.unique,
        )


field_builder = FieldBuilder(field_schema_builder)
