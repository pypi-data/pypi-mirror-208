# -*- coding: utf-8 -*-
import sys
import uuid
import hashlib
import time
import requests
from jy_word.File import File

reload(sys)
sys.setdefaultencoding('utf-8')

YOUDAO_URL = 'https://openapi.youdao.com/api'
APP_KEY = '77aa07b662b2a223'
APP_SECRET = '1ITqWf7O92mdBe4QzZHUHoLR98XeLPmO'


my_file = File()
tumor_evidence_data = my_file.read('tumor_evidence.json')
tumor_evidences = tumor_evidence_data.get('data')


def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()


def truncate(q):
    if q is None:
        return None
    q_utf8 = q.decode("utf-8")
    size = len(q_utf8)
    return q_utf8 if size <= 20 else q_utf8[0:10] + str(size) + q_utf8[size - 10:size]


def do_request(data):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    return requests.post(YOUDAO_URL, data=data, headers=headers)


def connect(q):
    data = {}
    data['from'] = '源语言'
    data['to'] = '目标语言'
    data['signType'] = 'v3'
    curtime = str(int(time.time()))
    data['curtime'] = curtime
    salt = str(uuid.uuid1())
    signStr = APP_KEY + truncate(q) + salt + curtime + APP_SECRET
    sign = encrypt(signStr)
    data['appKey'] = APP_KEY
    data['q'] = q
    data['salt'] = salt
    data['sign'] = sign

    response = do_request(data)
    contentType = response.headers['Content-Type']
    if contentType == "audio/mp3":
        millis = int(round(time.time() * 1000))
        filePath = "合成的音频存储路径" + str(millis) + ".mp3"
        fo = open(filePath, 'wb')
        fo.write(response.content)
        fo.close()
    else:
        res = response.json()
        if res is not None:
            translation = res.get('translation')
            if isinstance(translation, list):
                if len(translation) > 0:
                    return translation[0]
    return None


import os
dir_name = 'evidences'
if os.path.exists(dir_name) is False:
    os.makedirs(dir_name)


def get_item(item):
    no = item.get('no')
    evidence_statement = item.get('evidence_statement')
    evidence_statement_cn = ''
    if evidence_statement:
        evidence_statement = evidence_statement.strip()
        if evidence_statement:
            evidence_statement_cn = connect(evidence_statement)
    print no, evidence_statement_cn
    item['evidence_statement_cn'] = evidence_statement_cn or ''
    file_path = os.path.join(dir_name, '%s.json' % no)
    my_file.write(file_path, item)
    return item


def get_items():
    items = []
    for item in tumor_evidences:
        item = get_item(item)
        items.append(item)
    my_file.write('tumor_evidences_cn.json', items)


def evidence2excel():
    items = my_file.read('tumor_evidences_cn.json')
    import xlwt
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('Sheet1')
    for index, item in enumerate(items):
        for col, k in enumerate(item.keys()):
            v = item.get(k)
            if index == 0:
                sheet.write(index, col, label=k)
            sheet.write(index+1, col, label=v)
    wb.save('tumor_evidences_cn.xls')


if __name__ == '__main__':
    # get_items()
    evidence2excel()