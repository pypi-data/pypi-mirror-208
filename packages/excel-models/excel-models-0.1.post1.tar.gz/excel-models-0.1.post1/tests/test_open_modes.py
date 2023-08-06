import pytest

from excel_models.db import ExcelDB


class TestOpenModes:
    def test_o_exist(self, tmp_excel_file, tmp_excel_sheet_name):
        db = ExcelDB(tmp_excel_file, mode=ExcelDB.MODE_OPEN)
        assert set(db.wb.sheetnames) == {tmp_excel_sheet_name}

    def test_o_not_exist(self, tmp_path):
        tmp_excel_file = str(tmp_path / 'db.xlsx')
        db = ExcelDB(tmp_excel_file, mode=ExcelDB.MODE_OPEN)
        with pytest.raises(FileNotFoundError):
            _ = db.wb

    def test_n_exist(self, tmp_excel_file):
        db = ExcelDB(tmp_excel_file, mode=ExcelDB.MODE_CREATE)
        with pytest.raises(FileExistsError):
            _ = db.wb

    def test_n_not_exist(self, tmp_path):
        tmp_excel_file = str(tmp_path / 'db.xlsx')
        db = ExcelDB(tmp_excel_file, mode=ExcelDB.MODE_CREATE)
        assert len(db.wb.active._cells) == 0

    def test_w_exist(self, tmp_excel_file):
        db = ExcelDB(tmp_excel_file, mode=ExcelDB.MODE_OVERWRITE)
        assert len(db.wb.active._cells) == 0

    def test_w_not_exist(self, tmp_path):
        tmp_excel_file = str(tmp_path / 'db.xlsx')
        db = ExcelDB(tmp_excel_file, mode=ExcelDB.MODE_OVERWRITE)
        with pytest.raises(FileNotFoundError):
            _ = db.wb

    def test_a_exist(self, tmp_excel_file, tmp_excel_sheet_name):
        db = ExcelDB(tmp_excel_file, mode=ExcelDB.MODE_OPEN_CREATE)
        assert set(db.wb.sheetnames) == {tmp_excel_sheet_name}

    def test_a_not_exist(self, tmp_path):
        tmp_excel_file = str(tmp_path / 'db.xlsx')
        db = ExcelDB(tmp_excel_file, mode=ExcelDB.MODE_OPEN_CREATE)
        assert len(db.wb.active._cells) == 0

    def test_x_exist(self, tmp_excel_file):
        db = ExcelDB(tmp_excel_file, mode=ExcelDB.MODE_CREATE_OVERWRITE)
        assert len(db.wb.active._cells) == 0

    def test_x_not_exist(self, tmp_path):
        tmp_excel_file = str(tmp_path / 'db.xlsx')
        db = ExcelDB(tmp_excel_file, mode=ExcelDB.MODE_CREATE_OVERWRITE)
        assert len(db.wb.active._cells) == 0
