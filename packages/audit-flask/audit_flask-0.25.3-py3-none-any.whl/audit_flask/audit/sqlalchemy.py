from sqlalchemy import inspect
from sqlalchemy import event
from blinker import Signal

from audit_flask.utils.json import (serializar_dict)
from audit_flask.audit.kwargs import (create_kwargs)


signal = Signal('Send args')


def keep_logs_models(cls):

    @event.listens_for(cls, 'after_insert')
    def after_insert(mapper, connection, target):
        __audit((cls, target), 'create', None)

    @event.listens_for(cls, 'before_update')
    def before_update(mapper, connection, target):
        state = inspect(target)
        changes = {}
        object_before_changed = {}

        for attr in state.attrs:
            hist = attr.load_history()
            hist_attr = hist.deleted or hist.unchanged
            if len(hist_attr) > 0:
                object_before_changed[attr.key] = hist_attr[0]
            else:
                object_before_changed[attr.key] = None
            if not hist.has_changes():
                continue
            changes[attr.key] = hist.added
        if len(changes) > 0:
            __audit((cls, target), 'update', changes, object_before_changed)

    @event.listens_for(cls, 'after_delete')
    def after_delete(mapper, connection, target):
        __audit((cls, target), 'delete', None)

    def __audit(cls_target, method, changes: dict, object_before_changed=None):
        if changes is not None:
            changes = {key: value[0] for key, value in changes.items()}

        cls, target = cls_target
        target_dictionary = target.__dict__
        columns = dict(map(lambda x: (x.name, None), inspect(cls).columns))
        object_repr = {column: target_dictionary[column] for column in columns if column in target_dictionary}

        args = {
            'object_pk': getattr(target, cls.__mapper__.primary_key[0].name),
            'content_type': cls.__tablename__,
            'object_repr': serializar_dict(object_repr),
            'action': method,
            'changes': serializar_dict(changes),
            'object_before_changed': serializar_dict(object_before_changed)
        }
        signal.send(None, **create_kwargs(args))
