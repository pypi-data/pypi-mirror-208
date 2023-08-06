# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2017/9/29 0029
import os
import json
import xlrd
import chardet
from demo_xml import demo_xml
try:
    import csv
except:
    pass
__author__ = 'huohuo'
if __name__ == "__main__":
    pass


class File:

    def __init__(self, base_dir=''):
        self.__description__ = '文件相关， 包括读文件，写文件， 下载文件'
        self.base_dir = base_dir

    def read(self, file_name, sheet_name='Sheet1', read_type='r', dict_name='', to_json=True, table_sheet=True, **kwargs):
        file_type = file_name.split('.')[-1]
        url = os.path.join(self.base_dir, dict_name, file_name)
        if os.path.exists(url) is False:
            print 'File not exists, %s. Please check.' % url
            return None
        to_string = kwargs.get('to_string')
        if file_type in ['xlsx', 'xls']:
            table_sheet = kwargs.get('table_sheet')
            data = xlrd.open_workbook(url)
            table = data.sheet_by_name(sheet_name)
            if table_sheet:
                return table
            items = []
            ths = table.row_values(0)
            strings = '\t'.join(ths)
            items1 = [ths]
            nrow = table.nrows
            for i in range(1, nrow):
                item1 = []
                item = {}
                item2 = ''
                for j in range(0, len(ths)):
                    cell = table.cell_value(i, j)
                    item[ths[j]] = cell
                    item1.append(cell)
                    item2 += '%s\t' % cell
                if to_string:
                    strings += '\n%s' % (item2.strip('\t'))
                items.append(item)
                items1.append(item1)
            if to_string:
                return strings.strip('\n')
            if to_json:
                return items
            return items1
        f = open(url, read_type)
        text = f.read()
        f.close()
        if not to_string:
            if file_type in ['csv', 'tsv'] or 'sep' in kwargs:
                encoding = chardet.detect(text)['encoding']
                sep = ',' if file_type == 'csv' else '\t'
                if 'sep' in kwargs:
                    sep = kwargs['sep']
                delimiter = {'delimiter': sep}
                f = open(url, read_type)
                # csv.register_dialect('my_dialect', **delimiter)
                cons = csv.reader(f, **delimiter)
                items = []
                keys = next(cons)
                for c in cons:
                    if to_json:
                        item = {}
                        for i in range(len(keys)):
                            k = keys[i].decode(encoding).encode('utf-8')
                            item[k] = c[i].decode(encoding).encode('utf-8')
                        items.append(item)
                    else:
                        items.append([x.decode(encoding).encode('utf-8') for x in c])
                # csv.unregister_dialect('my_dialect')
                if to_json is False:
                    items = [keys] + items
                return items
            if file_type == 'json':
                return json.loads(text)
        return text

    def read_message(self, file_name, file_type='json', sheet_name='', read_type='r', developer='huohuo', message='success'):
        error_message = u'【开发者】：%s\n' % developer
        error_message += u'【文件类型】：%s\n' % file_type
        if file_type in ['xlsx', 'xls']:
            error_message += u'【sheet_name】：%s\n' % sheet_name
        error_message += u'【消息】：%s\n' % message
        error_message += u'【文件名】：\n%s\n' % file_name

    def write(self, file_name, data):
        file_type = file_name.split('.')[-1]
        url = os.path.join(self.base_dir, file_name)
        f = open(url, "w")
        if file_type == 'json':
            try:
                f.write(json.dumps(data, sort_keys=True, indent=4, ensure_ascii=False))
            except:
                f.write(json.dumps(data, sort_keys=True, indent=4, ensure_ascii=True))
        else:
            f.write(data)
        f.close()
        return 5

    def download(self, pkg_parts, file_name):
        temp_data = demo_xml.replace('<pkg:part id="pkg_parts"></pkg:part>', pkg_parts)
        temp_data = temp_data.replace('\n', '')
        return self.write(file_name, temp_data)

    def get_file_list(self, file_type, pre='', postfix=None):
        file_list = []
        folder_list = []
        full_path = os.path.join(self.base_dir, pre)
        for file_name in os.listdir(full_path):
            path_file = os.path.join(full_path, file_name)
            file_dict = {
                'file_name': file_name,
                'url': path_file,
                'dir_path': os.path.dirname(path_file),
                'full_path': file_name,
                'relative_path': os.path.relpath(path_file, self.base_dir)
            }
            if os.path.isdir(path_file):
                folder_list.append(file_dict)
            elif os.path.isfile(path_file):
                file_dict["type"] = file_type
                file_dict['file_size'] = self.get_file_size(path_file)
                is_selected = self.is_selected(file_name, postfix)
                file_dict['is_selected'] = is_selected
                if is_selected:
                    file_list.append(file_dict)
        folder_list.sort()
        file_list.sort()
        return {'data': {'folder': folder_list, 'file': file_list}}

    def get_file_size(self, path_file):
        try:
            size = os.path.getsize(path_file)
        except Exception, e:
            return '未知'
        if size > 1024 ** 3:
            return '%.02fGB' % (float(size) / 1024 ** 3)
        elif size > 1024 ** 2:
            return '%.02fMB' % (float(size) / 1024 ** 2)
        elif size > 1024:
            return '%0.2fKB' % (float(size) / 1024)
        else:
            return '%0.2fB' % (float(size))

    def get_file_item(self, file_name, path_file):
        return {
            'file_name': file_name,
            'url': path_file,
            'dir_path': os.path.dirname(path_file),
            'full_path': file_name,
            'relative_path': os.path.relpath(path_file, self.base_dir)
        }

    def is_selected(self, file_name, postfix=None):
        if postfix is None:
            return True
        for p in postfix:
            if file_name.endswith(p):
                return True
        return False