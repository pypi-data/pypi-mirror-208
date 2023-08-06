import pytest

from excel_models.columns import Column
from excel_models.db import ExcelDB
from excel_models.models import ExcelModel


class User(ExcelModel):
    id = Column(cache=False)
    name = Column()


class MyDB(ExcelDB):
    users = User.as_table()


@pytest.fixture()
def db(tmp_excel_file):
    return MyDB(tmp_excel_file)


def test_get(db, tmp_excel_data):
    user = db.users[0]
    assert user.id == tmp_excel_data[0][0]
    assert user.name == tmp_excel_data[0][1]
    # if we update the cells directly, cached columns should not reflect the changes
    db.wb['users'].cell(2, 1).value = '10'
    db.wb['users'].cell(2, 2).value = 'A'
    assert user.id == '10'
    assert user.name == tmp_excel_data[0][1]


def test_set(db):
    user = db.users[0]
    user.name = 'B'
    assert user.name == 'B'
    assert db.wb['users'].cell(2, 2).value == 'B'


def test_del(db):
    user = db.users[0]
    del user.name
    assert 'name' not in user.__dict__
    assert db.wb['users'].cell(2, 2).value is None
