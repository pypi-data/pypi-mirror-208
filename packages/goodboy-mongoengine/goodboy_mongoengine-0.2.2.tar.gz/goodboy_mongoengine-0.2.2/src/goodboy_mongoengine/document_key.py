from __future__ import annotations

from abc import ABC, abstractmethod, abstractproperty
from typing import Any, Mapping, Optional, Type

import goodboy as gb
import mongoengine as me
from mongoengine.base.fields import BaseField

from goodboy_mongoengine.field import Field
from goodboy_mongoengine.messages import DEFAULT_MESSAGES


class DocumentKey(ABC):
    @abstractproperty
    def name(self):
        ...

    @abstractproperty
    def result_key_name(self):
        ...

    @abstractproperty
    def required(self):
        ...

    @abstractproperty
    def has_default(self) -> bool:
        ...

    @abstractproperty
    def default(self) -> Any:
        ...

    @abstractmethod
    def predicate_result(self, prev_values: Mapping[str, Any]) -> bool:
        ...

    @abstractmethod
    def validate(
        self,
        value,
        typecast: bool,
        context: dict,
        instance: Optional[Any] = None,
    ):
        ...


class DocumentFieldKey(DocumentKey):
    def __init__(
        self,
        document_class: Type[me.Document],
        mongo_field: BaseField,
        mongo_pk_field: BaseField,
        field: Field,
        messages: gb.MessageCollectionType = DEFAULT_MESSAGES,
    ):
        self._document_class = document_class
        self._mongo_field = mongo_field
        self._mongo_pk_field = mongo_pk_field
        self._field = field
        self._messages = messages

    @property
    def name(self):
        return self._field.name

    @property
    def result_key_name(self):
        return self._field.document_field_name

    @property
    def required(self):
        return self._field.required

    @property
    def has_default(self) -> bool:
        return self._field.default is not None

    @property
    def default(self) -> Any:
        return self._field.default

    def predicate_result(self, prev_values: Mapping[str, Any]) -> bool:
        return self._field.predicate_result(prev_values)

    def validate(
        self,
        value,
        typecast: bool,
        context: dict,
        instance: Optional[me.Document] = None,
    ):
        value = self._field.validate(value, typecast, context)

        if self._field.unique:
            conds = {self._field.name: value}

            if instance:
                conds[f"{self._mongo_pk_field.name}__ne"] = instance.id

            exists = bool(
                self._document_class.objects(**conds).only(self._field.name).first()
            )

            if exists:
                raise gb.SchemaError([self._error("already_exists")])

        return value

    def _error(self, code: str, args: dict = {}, nested_errors: dict = {}):
        return gb.Error(code, args, nested_errors, self._messages.get_message(code))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__

        return super().__eq__(other)


class DocumentPropertyKey(DocumentKey):
    def __init__(self, key: gb.Key):
        self._key = key

    @property
    def name(self):
        return self._key.name

    @property
    def result_key_name(self):
        return self._key.name

    @property
    def required(self):
        return self._key.required

    def predicate_result(self, prev_values: Mapping[str, Any]) -> bool:
        return self._key.predicate_result(prev_values)

    @property
    def has_default(self) -> bool:
        return self._key.default is not None

    @property
    def default(self) -> Any:
        return self._key.default

    def validate(
        self,
        value,
        typecast: bool,
        context: dict,
        instance: Optional[me.Document] = None,
    ):
        return self._key.validate(value, typecast, context)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__

        return super().__eq__(other)


class DocumentKeyBuilderError(Exception):
    pass


class DocumentKeyBuilder:
    def build(
        self,
        document_class: Type[me.Document],
        keys: list[gb.Key],
        messages: gb.MessageCollectionType = DEFAULT_MESSAGES,
    ) -> list[DocumentKey]:
        result: list[DocumentKey] = []

        for key in keys:
            result.append(self._build_document_key(document_class, key, messages))

        return result

    def _build_document_key(
        self,
        document_class: Type[me.Document],
        key: gb.Key,
        messages: gb.MessageCollectionType,
    ) -> DocumentKey:
        if isinstance(key, Field):
            return DocumentFieldKey(
                document_class,
                self._get_mongo_field(document_class, key.document_field_name),
                self._get_pk_mongo_field(document_class),
                key,
                messages,
            )
        else:
            return DocumentPropertyKey(key)

    def _get_mongo_field(
        self, document_class: Type[me.Document], field_name: str
    ) -> BaseField:
        if field_name not in document_class._fields:
            raise DocumentKeyBuilderError(
                f"document class {document_class.__name__} has no field {field_name}"
            )

        return document_class._fields[field_name]

    def _get_pk_mongo_field(self, document_class: Type[me.Document]) -> BaseField:
        field: BaseField

        for field in document_class._fields.values():
            if field.primary_key:
                return Field

        if "id" in document_class._fields:
            return document_class._fields["id"]

        raise DocumentKeyBuilderError(
            f"document class {document_class.__name__} has no primary key field"
        )


document_key_builder = DocumentKeyBuilder()
