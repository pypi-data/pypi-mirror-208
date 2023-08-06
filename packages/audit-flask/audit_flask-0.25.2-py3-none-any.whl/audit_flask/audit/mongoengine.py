import copy
from mongoengine import signals
from mongoengine.base import BaseDocument
from blinker import Signal
from typing import Tuple

from audit_flask.audit.kwargs import create_kwargs
from audit_flask.utils.json import (serializar_dict, serialize_field)

signal = Signal('Send args')


class Audit(BaseDocument):
    _before_change = {}

    @classmethod
    def __audit(cls, document, **kwargs):
        changes = None
        updates, removals = document._delta()
        if 'created' in kwargs:
            method = 'create'
            if kwargs['created'] is False:
                if (isinstance(updates, Tuple)):
                    changes = dict((key, value) for key, value in updates)
                else:
                    changes = updates
                method = 'update'
        else:
            method = 'delete'
        before_doc = None
        if method != 'create':
            doc = serializar_dict({**document.to_mongo()})
            before_doc = copy.deepcopy(doc)
            for key, value in document._before_change.items():
                before_doc[key] = serialize_field(value)

        args = {
            'object_pk': document.pk,
            'content_type': document._collection.name,
            'object_repr': serializar_dict({**document.to_mongo()}),
            'action': method,
            'changes': serializar_dict(changes),
            'object_before_changed': before_doc
        }
        signal.send(None, **create_kwargs(args))

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        cls.__audit(document, **kwargs)
        document._before_change = {}

    @classmethod
    def post_delete(cls, sender, document, **kwargs):
        cls.__audit(document, **kwargs)

    def _mark_as_changed(self, key):
        # Es necesario sobrescribir este metodo para
        # guardar el valor que va a cambiar en un diccionario,
        # esto se determina leyendo el código de mongoengine
        super()._mark_as_changed(key)
        if hasattr(self, key):
            self._before_change[key] = getattr(self, key)


def register_signals_model(cls):
    signals.post_save.connect(cls.post_save, sender=cls)
    signals.post_delete.connect(cls.post_delete, sender=cls)
