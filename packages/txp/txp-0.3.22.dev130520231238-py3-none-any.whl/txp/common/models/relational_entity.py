"""
This file contains the abstract concept of relational entity in the project.

A Relational entity is some object from the problem space that has been
modeled as a persistent unit with certain attributes.

This TxpRelationalEntity contains utility operations that are useful
when dealing with the persistence layer, since we can generalize
information handling independently from the DBMS where the information resides.

"""

import abc
from typing import List, Dict
import txp.common.models.protos.models_pb2 as models_pb2
from google.protobuf.json_format import MessageToDict, ParseDict
import dataclasses
import logging
from txp.common.config import settings
log = logging.getLogger(__name__)
log.setLevel(settings.txp.general_log_level)


@dataclasses.dataclass
class TxpRelationalEntity(abc.ABC):
    def __post_init__(self):
        self._proto = None  # Persisted proto ref for dict access.

    @classmethod
    @abc.abstractmethod
    def get_proto_class(cls):
        """Returns the proto model python class defined for this entity."""
        pass

    @classmethod
    @abc.abstractmethod
    def firestore_collection_name(cls) -> str:
        pass

    @classmethod
    def get_db_query_fields(
        cls,
        required_tags: List[type(models_pb2.EntityFieldRequiredByEnum)]
    ) -> List[str]:
        """Returns a List of the query field based on the received tags.

        Args:
            required_tags: list of required field for a database query based on the
                context of the client.
        """
        proto = cls.get_proto_class()
        fields_to_query = []
        for field in proto.DESCRIPTOR.fields:
            if (
                field.GetOptions().Extensions[models_pb2.required_by] in required_tags
            ):
              fields_to_query.append(field.name)
        return fields_to_query

    @classmethod
    def from_dict(cls, values: Dict):
        return cls.get_instance_from_proto(
            cls.get_proto_from_dict(
                values
            )
        )

    @classmethod
    def get_proto_from_dict(cls, values: Dict):
        """Get a proto instance of the class from a dictionary representation.
        """
        message = ParseDict(values, cls.get_proto_class()(), ignore_unknown_fields=True)
        return message

    def _set_proto(self, p):
        self._proto = p

    @classmethod
    def get_instance_from_proto(cls, p) -> "TxpRelationalEntity":
        """Returns an instance of the child class from the corresponding
        proto instance `p`.

        Note: The Dictionary keys from the proto `p` and the
            children class init parameters should match.
        """
        try:
            dict_ob = MessageToDict(p, preserving_proto_field_name=True, including_default_value_fields=True)
            instance = cls(**dict_ob)
            instance._set_proto(p)
            return instance
        except Exception as e:
            log.error("Error creating instance from dict object: "
                      f"{dict_ob}")
            raise e


    def get_dict(self, include_defautls=False) -> Dict:
        if self._proto:
            dict_ob = MessageToDict(
                self._proto,
                preserving_proto_field_name=True,
                including_default_value_fields=include_defautls
            )
            return dict_ob
        else:
            return {}
