from typing import Optional
import re


class OID(object):
    """
    Represents an ORKG ID
    """

    id: str
    type: Optional[str]

    def __init__(self, id: str, type: Optional[str] = None):
        """
        :param id: the id
        :param type: the type of the id (optional)
        """
        self.id = id
        self.type = type

    def __str__(self):
        return self.id

    def __repr__(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id and self.type == other.type

    def __hash__(self):
        return hash(self.id)

    def __bool__(self):
        return bool(self.id)

    def is_literal_id(self) -> bool:
        return re.match(r'^L\d+$', self.id) is not None

    def is_resource_id(self) -> bool:
        return re.match(r'^R\d+$', self.id) is not None

    def is_predicate_id(self) -> bool:
        return re.match(r'^P\d+$', self.id) is not None

    def is_class_id(self) -> bool:
        return re.match(r'^C\d+$', self.id) is not None

    def is_custom_id(self) -> bool:
        return not self.is_literal_id() and not self.is_resource_id() and not self.is_predicate_id() and not self.is_class_id()

    def to_orkg_json(self) -> dict:
        obj = {'@id': self.id}
        if self.type:
            obj['@type'] = self.type
        return obj
