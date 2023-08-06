import pytest

from excel_db.columns import Column
from excel_db.db import ExcelDB
from excel_db.models import ExcelModel


class User(ExcelModel):
    id = Column()
    name = Column()


class MyDB(ExcelDB):
    users = User.as_table()


@pytest.fixture()
def db(tmp_excel_file):
    return MyDB(tmp_excel_file)


def test_get_by_row(db, tmp_excel_data):
    row = db.users[0]
    assert (row.id, row.name) == tmp_excel_data[0]


def test_get_by_column(db, tmp_excel_data):
    col = db.users.name
    assert (col[0], col[1], col[2]) == tuple(x[1] for x in tmp_excel_data)


def test_set_by_row(db):
    row = db.users[1]
    row.name = 'Chris'
    assert db.wb['users'].cell(3, 2).value == 'Chris'


def test_set_by_col(db):
    col = db.users.name
    col[1] = 'Chris'
    assert db.wb['users'].cell(3, 2).value == 'Chris'


def test_del_by_row(db):
    row = db.users[2]
    del row.name
    assert db.wb['users'].cell(4, 2).value is None


def test_del_by_col(db):
    col = db.users.name
    del col[2]
    assert db.wb['users'].cell(4, 2).value is None
