#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 08/06/2019
# @Author  : Yuhong Zhai
# @Desc    : 把pdf转换成excel可读的csv格式
# @File    : extract_from_pdf_to_csv.py
# @Software: PyCharm


import tabula
import csv
import pandas as pd
import numpy as np
import math
import os 
import pyocr
import importlib
import sys
import time
import os.path
from pdfminer.pdfparser import  PDFParser,PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal,LAParams
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed

def parse(path):
    fp = open(path, 'rb') # 以二进制读模式打开
    #用文件对象来创建一个pdf文档分析器
    praser = PDFParser(fp)
    # 创建一个PDF文档
    doc = PDFDocument()
    # 连接分析器 与文档对象
    praser.set_document(doc)
    doc.set_parser(praser)
    doc.initialize()
    # 检测文档是否提供txt转换，不提供就忽略

    if not doc.is_extractable:
        raise PDFTextExtractionNotAllowed
    else:
        # 创建PDf 资源管理器 来管理共享资源
        rsrcmgr = PDFResourceManager()
        # 创建一个PDF设备对象
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        # 创建一个PDF解释器对象
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        # 循环遍历列表，每次处理一个page的内容
        for page in doc.get_pages(): # doc.get_pages() 获取page列表
            interpreter.process_page(page)
            # 接受该页面的LTPage对象
            layout = device.get_result()
            # 这里layout是一个LTPage对象 里面存放着 这个page解析出的各种对象 一般包括LTTextBox, LTFigure, LTImage, LTTextBoxHorizontal 等等 想要获取文本就获得对象的text属性，
            for x in layout:
                if (isinstance(x, LTTextBoxHorizontal)):
                    results = x.get_text()
                    if results != None and len(results) > 6 and results.find('表') > 0:
                        results = results.replace('\n','')
                        return results
    return ""

def read_pdf_to_csv(filename):
#    file_title = parse(filename) #获得文章标题
    file_title = ""
    df = tabula.read_pdf(filename, pages='all') #提取pdf中的表格到dataframe格式数据(df)中 

    #如果df是空的，就说明里面没有表格，直接返回
    if df is None:
        print("This is an empty document")
        return
#    print(len(df))
#    print(df)


#得到到第几行都是标题头
    flag = 0
    count = 0
    for count in range(len(df)):
        if type(df.index[0]) != type(2):
            count = 0
            break
        flag = 0
        for j in range(len(df.loc[count])):
            if type(df.loc[count].values[j]) == type(float('nan')):
                flag = 1
        if flag == 0:
            break

#将标题头替换
    if count != 0:
        for k in range(count - 1):
            for i in range(len(df.loc[k])):
                if type(df.loc[k].values[i]) != type(float('nan')):
                    if type(df.loc[k + 1].values[i]) != type(float('nan')):
                        df.loc[k + 1].values[i] = df.loc[k].values[i] + df.loc[k + 1].values[i]
                    else:
                        df.loc[k + 1].values[i] = df.loc[k].values[i]

        for i in range(len(df.loc[count - 1])):
            if type(df.loc[count - 1].values[i]) != type("as"):
                continue
            if df.loc[count - 1].values[i].endswith('%'):
                df.loc[count - 1].values[i] = df.loc[count - 1].values[i][:-1] + "%"

#修改标题头，符合人的直观感受，减少操作，增加可读性
        title = list(df.loc[count - 1])
        for i in range(len(df.columns)):
            if type(df.columns[i].startswith('U')) != type("as"):
                continue;
            if not df.columns[i].startswith('U'):
                title[i] = df.columns[i] + title[i]

        new_title = []
        title_find = 0
        for i in range(len(title)):
            if type(title[i]) != type("as"):
                title_find = 1
                continue
            if title[i].find(' '):
                st = title[i].split(' ')
                new_title.append("".join(st))
            else:
                new_title.append(title[i])
        if title_find == 0:
            df.columns = new_title
        df = df[count:]
        index = [i for i in range(len(df))]
        df.index = index
#删除之前的行 得到index

    output_name = ""
    roots = filename.split("/")
    if len(file_title) < 1:
        original_name = roots[len(roots) - 1].split(".")
        original_name[1] = "csv"
        output_name = ".".join(original_name) #从pdf的文件名，得到csv的文件名，只改了后缀
    else:
        output_name = file_title + ".csv"
#    roots[len(roots) - 1] = "transfer"
#    path_ = "/".join(roots)
#    if not os.path.exists(path_): #如果文件目录不存在，建立目录
#        os.makedirs(path_)
    roots[-1] = output_name
    final_name = "/".join(roots)
    df.to_csv(final_name, encoding = 'utf-8-sig') #把dataframe格式的数据，输出为相应的csv文件
#    df.to_csv(final_name) #把dataframe格式的数据，输出为相应的csv文件

def file_name(file_dir): #得到file_dir路径下的所有文件的完整路径
    names = []
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            if os.path.splitext(file)[1] == '.pdf':
                names.append(os.path.join(root, file))
    return names

if __name__ == '__main__':
    files = file_name("/Users/yulei/成都") #这里是文件夹的名字
    for file in files:
        print(file)
        read_pdf_to_csv(file)   #转换文件到csv

#filename = "/Users/tekiuniji/webcrawler/data/成都/成都市2019年财政预算调整方案的报告及相关附件表格/f109ba73108f4191bb5deebd9bb02d52.pdf"
#df = read_pdf_to_csv(filename)
#print(df)

'''
files = file_name("/Users/tekiuniji/webcrawler/data/成都/") #这里是文件夹的名字
for file in files:
    print(file) #打印要转换的pdf的文件名
    read_pdf_to_csv(file)   #转换文件到csv
'''

