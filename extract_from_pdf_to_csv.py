import tabula
import csv
import pandas as pd
import numpy as np
import math
import os 

def read_pdf_to_csv(filename):
    df = tabula.read_pdf(filename, pages='all')
    if df is None:
        print("This is an empty document")
        return
#    print(len(df))
#    print(df)
#得到到第几行都是标题头
    flag = 0
    count = 0
    for count in range(len(df)):
        flag = 0
        for j in range(len(df.loc[count])):
            if type(df.loc[count].values[j]) == type(float('nan')):
                flag = 1
        if flag == 0:
            break;

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
            if df.loc[count - 1].values[i].endswith('%'):
                df.loc[count - 1].values[i] = df.loc[count - 1].values[i][:-1] + "%"

#修改标题头
        title = list(df.loc[count - 1])
        for i in range(len(df.columns)):
            if not df.columns[i].startswith('U'):
                title[i] = df.columns[i] + title[i]

        new_title = []
        for i in range(len(title)):
            if title[i].find(' '):
                st = title[i].split(' ')
                new_title.append("".join(st))
            else:
                new_title.append(title[i])
    
        df.columns = new_title
        df = df[count:]
        index = [i for i in range(len(df))]
        df.index = index
#删除之前的行 得到index

    original_name = filename.split(".")
    original_name[1] = "csv"
    output_name = ".".join(original_name)
    df.to_csv(output_name)

def file_name(file_dir):
    names = []
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            if os.path.splitext(file)[1] == '.pdf':
                names.append(os.path.join(root, file))
    return names

files = file_name("/Users/yulei/chengdu") #这里是文件夹的名字
for file in files:
    print(file)
    read_pdf_to_csv(file)