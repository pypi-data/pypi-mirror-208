import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy import (Column, String, Integer, Boolean, DateTime)

from audit_flask.audit import sqlalchemy as sqlalchemy_audit_flask


SQLALCHEMY_DATABASE_URL = "postgresql://{}:{}@{}/{}".format('Finkargo', 'Finkargo', 'localhost:5432', 'Testing')
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
)
Base = declarative_base()
session = Session(autocommit=False, autoflush=False, bind=engine)


def signal_sqlalchemy(*args, **kwargs):
    print('CHANGES LIBRARY SQLALCHEMY')
    print(kwargs)
    print(len(kwargs['object_repr']) == len(kwargs['object_before_changed'] or []))


class User(Base):
    __tablename__ = 'User'
    id_user = Column(Integer, primary_key=True, comment='id único')
    name = Column(String, comment='Nombre del usuario')
    surname = Column(String, comment='Apellido del usuario')
    email = Column(String, unique=False, comment='correo electrónico del usuario')
    status = Column(Boolean, comment='Si el usaurio está activo')
    generic = Column(Boolean, default=True, comment='Si es usuario generico')
    cellphone_number = Column(String, comment='Número celular del usuario')
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now)


Base.metadata.create_all(engine)

sqlalchemy_audit_flask.keep_logs_models(User)

sqlalchemy_audit_flask.signal.connect(signal_sqlalchemy)


def test_create_row():
    user = User(
        name='Test',
        surname='Test',
        email='test@example.com',
        status=True,
        generic=True,
        cellphone_number='123456789'
    )
    session.add(user)
    session.commit()


def test_change_row():
    user = session.query(User).filter(User.id_user == 2).first()
    print('antes=====', user.name, user.email)
    user.name = 'sdsd sas'
    user.email = 'sadasdas@wasd.com'
    session.commit()


def test_delete_row():
    user = session.query(User).filter(User.id_user == 1).first()
    session.delete(user)
    session.commit()


# test_create_row()
test_change_row()
# test_delete_row()
