from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional, Type

import goodboy as gb
import mongoengine as me
from mongoengine.base.fields import BaseField

from goodboy_mongoengine.schemas import ObjectIdSchema


class FieldSchemaFactory(ABC):
    @abstractmethod
    def build(self, field: BaseField) -> gb.Schema:
        ...


class SimpleFieldSchemaFactory(FieldSchemaFactory):
    def __init__(self, schema: Type[gb.Schema]) -> None:
        self._schema = schema

    def build(self, field: BaseField) -> gb.Schema:
        return self._schema(allow_none=not field.required)


class StringFieldSchemaFactory(FieldSchemaFactory):
    def build(self, field: me.StringField) -> gb.Str:
        return gb.Str(
            allow_none=not field.required,
            max_length=field.max_length,
            min_length=field.min_length,
            pattern=field.regex,
            allowed=field.choices,
        )


class BooleanFieldSchemaFactory(FieldSchemaFactory):
    def build(self, field: me.BooleanField) -> gb.Bool:
        return gb.Bool(allow_none=not field.required)


class IntFieldSchemaFactory(FieldSchemaFactory):
    def build(self, field: me.IntField) -> gb.Int:
        return gb.Int(
            allow_none=not field.required,
            less_than=field.max_value,
            greater_than=field.min_value,
        )


class DecimalFieldSchemaFactory(FieldSchemaFactory):
    def build(self, field: me.Decimal128Field) -> gb.DecimalSchema:
        return gb.DecimalSchema(
            allow_none=not field.required,
            less_than=field.max_value,
            greater_than=field.min_value,
        )


class ObjectIdFieldSchemaFactory(FieldSchemaFactory):
    def build(self, field: me.ObjectIdField) -> ObjectIdSchema:
        return ObjectIdSchema(allow_none=not field.required)


class DictFieldFieldSchemaFactory(FieldSchemaFactory):
    def build(self, field: me.DictField) -> gb.Dict:
        return gb.Dict(allow_none=not field.required, key_schema=gb.Str())


ME_TYPE_MAPPING: dict[Type[BaseField], FieldSchemaFactory] = {
    me.StringField: StringFieldSchemaFactory(),
    me.DictField: DictFieldFieldSchemaFactory(),
    me.BooleanField: BooleanFieldSchemaFactory(),
    me.IntField: IntFieldSchemaFactory(),
    me.ObjectIdField: ObjectIdFieldSchemaFactory(),
    me.Decimal128Field: DecimalFieldSchemaFactory(),
}


class FieldSchemaBuilderError(Exception):
    pass


class FieldSchemaBuilder:
    def __init__(self, me_type_mapping: dict[Any, FieldSchemaFactory]):
        self._me_type_mapping = me_type_mapping

    def build(self, field: BaseField) -> gb.Schema:
        field_schema_factory = self._find_field_schema_factory(field)

        if not field_schema_factory:
            raise FieldSchemaBuilderError(
                f"unmapped MongoEngine field type {repr(field.__class__)}"
            )

        return field_schema_factory.build(field)

    def _find_field_schema_factory(
        self, field: BaseField
    ) -> Optional[FieldSchemaFactory]:
        for me_type, field_schema_factory in self._me_type_mapping.items():
            if isinstance(field, me_type):
                return field_schema_factory

        return None


field_schema_builder = FieldSchemaBuilder(ME_TYPE_MAPPING)
