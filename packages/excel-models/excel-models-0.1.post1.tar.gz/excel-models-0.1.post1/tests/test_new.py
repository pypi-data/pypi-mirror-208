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


def test_new_row(db):
    row = db.users.new()
    assert isinstance(row, User)
    assert row.idx == 3
    assert row.row_num == 5

    row2 = db.users.new()
    assert isinstance(row2, User)
    assert row2.idx == 4
    assert row2.row_num == 6
