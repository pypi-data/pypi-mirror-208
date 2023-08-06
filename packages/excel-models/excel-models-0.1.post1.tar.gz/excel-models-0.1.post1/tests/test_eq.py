import pytest

from excel_models.columns import Column
from excel_models.db import ExcelDB
from excel_models.models import ExcelModel


class User(ExcelModel):
    id = Column()
    name = Column()


class MyDB(ExcelDB):
    users = User.as_table()
    accounts = User.as_table()


@pytest.fixture()
def db(tmp_excel_file):
    return MyDB(tmp_excel_file)


def test_table_eq(db):
    assert db.users is not db.users
    assert db.users == db.users
    assert db.users != db.accounts


def test_row_eq(db):
    users = db.users
    assert users[0] is not users[0]
    assert users[0] == users[0]
    assert users[0] != users[1]


def test_column_eq(db):
    users = db.users
    assert users.id is users.id  # columns are cached
    assert users.id == users.id
    assert users.id != users.name
