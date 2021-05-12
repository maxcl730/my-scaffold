# coding=utf-8
import xlwt


class Excel(object):
    _default_sheet = 'sheet1'
    filename = None
    workbook = None
    sheets = dict()

    def __init__(self, filename):
        # 初始化excel文件
        self.filename = filename
        self.workbook = xlwt.Workbook()
        self.sheets['sheet1'] = self.workbook.add_sheet(sheetname=self._default_sheet, cell_overwrite_ok=True)

    def save(self):
        #  保存文件
        self.workbook.save(self.filename)

    def add_sheet(self, sheetname):
        self.sheets[sheetname] = self.workbook.add_sheet(sheetname=sheetname, cell_overwrite_ok=True)

    def write(self, row, col, content, sheetname=None):
        if sheetname is None:
            sheetname = self._default_sheet
        try:
            self.sheets[sheetname].write(row, col, content)
            return True
        except KeyError:
            print('{} not exists!'.format(sheetname))
            return False
