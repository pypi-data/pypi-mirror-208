import pytest
from openpyxl.cell import Cell

from excel_models.columns import Column
from excel_models.db import ExcelDB
from excel_models.models import ExcelModel


@pytest.fixture()
def excel(lazy_init_excel):
    return lazy_init_excel('users', 'name', 'John\nDoe', None, 'Bob', 1.5)


class User(ExcelModel):
    @Column()
    def name(self, cell: Cell):
        if cell.value is None or cell.value == '':
            return []
        return cell.value.split('\n')

    @name.setter
    def name(self, value, cell: Cell):
        if not value:
            cell.value = ''
            return
        cell.value = '\n'.join(value)

    @name.deleter
    def name(self, cell: Cell):
        cell.value = ''

    @name.error_handler
    def name(self, cell: Cell, ex: Exception):
        return [str(cell.value)]


class MyDB(ExcelDB):
    users = User.as_table()


@pytest.fixture()
def db(excel):
    return MyDB(excel)


def test_get(db):
    assert db.users.name[:] == [['John', 'Doe'], [], ['Bob'], ['1.5']]


def test_set(db):
    db.users[1].name = ['Chris']
    assert db.wb['users'].cell(3, 1).value == 'Chris'


def test_del(db):
    del db.users[2].name
    assert db.wb['users'].cell(4, 1).value == ''
