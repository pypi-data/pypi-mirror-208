from audit_flask.audit import mongoengine

from test import SETUP
import random
import datetime
from mongoengine import connect
from mongoengine.document import DynamicDocument
from mongoengine.fields import (SequenceField, StringField, DictField, DateTimeField, IntField)

connect(host=SETUP.URL_MONGO)


def signal_mongoengine(*args, **kwargs):
    print('CHANGES LIBRARY MONGOENGINE')
    print(kwargs)


class PersistentCache(DynamicDocument, mongoengine.Audit):
    id_persistentcache = SequenceField(primary_key=True)
    nit = StringField(required=True)
    user_id = IntField(default=0)
    service = StringField(required=True)
    code_request = StringField(required=False)
    response = DictField()
    raw_response = StringField()
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)
    refresh_interval = IntField(default=720)
    meta = {
        'indexes': ['nit']
    }


mongoengine.register_signals_model(PersistentCache)


mongoengine.signal.connect(signal_mongoengine)


def create_row():
    model = PersistentCache(
        nit='123456',
        user_id=1,
        service='testing',
    )

    model.save()


def change_row():
    model = PersistentCache.objects(_id=1).first()
    print('=====ANTES================================\n', model.nit)
    model.nit = random.randrange(100, 900).__str__()
    model.save()


change_row()
