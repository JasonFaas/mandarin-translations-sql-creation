import csv
import sqlite3
import os
import pinyin

import jieba

import pandas as pd

import sys

print(sys.version)

def pinyin_from_hanzi (row):
    nh2 = row['Hanzi']

    seg_list = jieba.cut(nh2)
    what = " ".join(seg_list)
    hanzi_arr = what.split(" ")
    pinyin_arr = pinyin.get(nh2, delimiter=" ").split(" ")

    pinyin_itr = 0
    pinyin_final = ""
    for hanzi_group in hanzi_arr:
        pinyin_group = pinyin_arr[pinyin_itr:pinyin_itr + len(hanzi_group)]
        pinyin_corr = ""
        for pinyin_char in pinyin_group:
            pinyin_corr += pinyin_char
        pinyin_final += pinyin_corr + " "
        pinyin_itr += len(hanzi_group)

    return pinyin_final.strip()

def hanzi_with_spaces (row):
    nh2 = row['Hanzi']

    seg_list = jieba.cut(nh2)
    what = " ".join(seg_list)
    return what


csv_file_path = '../raw_data/first.csv'
df = pd.read_csv(csv_file_path)
print(df)
df['pinyin'] = df.apply(lambda row: pinyin_from_hanzi(row), axis=1)
df['Hanzi'] = df.apply(lambda row: hanzi_with_spaces(row), axis=1)

df.to_csv('../sql/final.csv', index=False)


database_name = "../sql/first.sqlite3"

os.remove(database_name)

con = sqlite3.connect(database_name)
cur = con.cursor()
columns = ('''Hanzi''', '''English''', '''Difficulty''')
cur.execute('''CREATE TABLE Translations
             (
                 [generated_id] INTEGER PRIMARY KEY,
                 [%s] text, 
                 [%s] text,
                 [%s] INTEGER
             )
             ''' % columns)

with open(csv_file_path, 'rt') as fin:  # `with` statement available in 2.5+
    # csv.DictReader uses first line in file for column headings by default
    dr = csv.DictReader(fin)  # comma is default delimiter
    to_db = [
                (
                    i[('%s' % columns[0])],
                    i[('%s' % columns[1])],
                    i[('%s' % columns[2])],
                )
            for i in dr]

percent_s = ", ".join(['%s'] * len(columns))
question_mark = ", ".join(['?'] * len(columns))
insert_str = ("INSERT INTO Translations (" + percent_s + ") VALUES (" + question_mark + ");")
cur.executemany(insert_str % columns, to_db)
con.commit()
con.close()
