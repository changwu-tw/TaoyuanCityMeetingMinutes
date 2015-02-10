#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import filecmp
import os
import pytz
import requests
import sys
import urllib


from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding("utf-8")

BASE = 'http://www.tycg.gov.tw/ch/'
TODAY = datetime.datetime.now(pytz.timezone('US/Central')).strftime('%Y%m%d')
DIR_PATH = 'docs/'


def isSameFile(file1, file2):
    return filecmp.cmp(file1, file2)


def extarctPdf(path):
    from cStringIO import StringIO
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfpage import PDFPage

    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = file(path, 'rb')
    for page in PDFPage.get_pages(infile):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close
    return text


def getPdfUrl(url):
    pdfList = []
    r = requests.get(url)
    bs = BeautifulSoup(r.text).findAll('td', {'class', 'style_44-3'})
    for td in bs:
        path = td.find('a')['href']
        filename = td.find('a').text
        pdfList.append((path, filename))
    return pdfList


def getMeetingList():
    r = requests.get('http://www.tycg.gov.tw/ch/home.jsp?id=10233&parentpath=0,4')
    bs = BeautifulSoup(r.text).findAll('a', {'class', 'news_a'}, href=True)
    return [BASE+a['href'] for a in bs]


if __name__ == '__main__':
    urlList = getMeetingList()

    for url in urlList:
        pdfList = getPdfUrl(url)
        for (urlpath, filename) in pdfList:
            filepath = DIR_PATH + filename
            if os.path.isfile(filepath):
                # new file
                source = urllib.urlopen(urlpath).read()
                newname = filename[:filename.find('.')] + '_' + TODAY + '.pdf'
                newpath = DIR_PATH+newname
                with open(newpath, 'w') as f:
                    f.write(source)
                # compare two files
                if isSameFile(filepath, newpath):
                    os.remove(newpath)
                else:
                    textname = newname[:newname.find('.')] + '.txt'
                    with open(DIR_PATH+textname, 'w') as f:
                        f.write(extarctPdf(newpath))
            else:
                # pdf
                source = urllib.urlopen(urlpath).read()
                with open(filepath, 'w') as f:
                    f.write(source)
                # txt
                textname = filename[:filename.find('.')] + '.txt'
                with open(DIR_PATH+textname, 'w') as f:
                    f.write(extarctPdf(filepath))


