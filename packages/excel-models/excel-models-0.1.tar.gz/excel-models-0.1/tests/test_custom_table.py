import pytest

from excel_db.columns import Column
from excel_db.db import ExcelDB
from excel_db.models import ExcelModel
from excel_db.tables import ExcelTable


class User(ExcelModel):
    id = Column()
    name = Column()


class MyUserTable(ExcelTable):
    def add_user(self, id_, name):
        user = self.new()
        user.id = id_
        user.name = name


class MyDB(ExcelDB):
    users = User.as_table(table_class=MyUserTable)


@pytest.fixture()
def db(tmp_excel_file):
    return MyDB(tmp_excel_file)


def test_custom_table(db):
    db.users.add_user(10, 'Mary')
    assert db.wb['users'].cell(5, 1).value == 10
    assert db.wb['users'].cell(5, 2).value == 'Mary'
