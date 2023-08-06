import pytest

from excel_models.columns import Column
from excel_models.db import ExcelDB
from excel_models.models import ExcelModel


class User(ExcelModel):
    id = Column()
    name = Column()


class MyDB(ExcelDB):
    users = User.as_table()


@pytest.fixture()
def db(tmp_excel_file):
    return MyDB(tmp_excel_file)


def test_len(db, tmp_excel_data):
    assert len(db.users) == len(tmp_excel_data)


def test_iter_table(db, tmp_excel_data):
    for user, data in zip(db.users, tmp_excel_data, strict=True):
        assert (user.id, user.name) == data


def test_slice_table(db):
    assert db.users[1:] == [db.users[1], db.users[2]]


def test_row_as_dict(db, tmp_excel_columns, tmp_excel_data):
    assert db.users[0].as_dict() == dict(zip(tmp_excel_columns, tmp_excel_data[0]))


def test_row_set_dict(db):
    db.users[0].set_dict({'name': 'Chris'})
    assert db.wb['users'].cell(2, 2).value == 'Chris'
    db.users[1].set_dict(name='Carol')
    assert db.wb['users'].cell(3, 2).value == 'Carol'


def test_column_iter(db, tmp_excel_data):
    for name, data in zip(db.users.name, tmp_excel_data, strict=True):
        assert name == data[1]


def test_column_slice(db, tmp_excel_data):
    assert db.users.name[:-1] == [data[1] for data in tmp_excel_data[:-1]]


def test_column_slice_set(db):
    db.users.name[:2] = ('Chris', 'Carol')
    assert db.wb['users'].cell(2, 2).value == 'Chris'
    assert db.wb['users'].cell(3, 2).value == 'Carol'


def test_column_slice_del(db):
    del db.users.name[1:]
    assert db.wb['users'].cell(3, 2).value is None
    assert db.wb['users'].cell(4, 2).value is None
