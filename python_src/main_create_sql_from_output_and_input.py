import csv
import sqlite3
import os
import pinyin

import jieba

import pandas as pd

import sys

print(sys.version)

def pinyin_from_hanzi(row):
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

def hanzi_with_spaces(row):
    nh2 = row['Hanzi'].replace(' ', '')

    seg_list = jieba.cut(nh2)
    what = " ".join(seg_list)
    return what


from googletrans import Translator
googletrans_translator = Translator()
def pinyin_from_hanzi_googletrans(row):
    global googletrans_translator

    hanzi = row['Hanzi'].replace(' ', '')
    gt_translation = googletrans_translator.translate(hanzi, src='zh-cn', dest='en')
    print(gt_translation, flush=True)
    print(gt_translation.extra_data, flush=True)
    # print(gt_translation.origin, ' -> ', gt_translation.text, flush=True)
    translation_return = gt_translation.extra_data['translation'][1][-1].lower()
    print(gt_translation.origin, ' -> ', translation_return)
    print('\n', flush=True)

    return translation_return


def verify_no_new_old_duplicates(df_1, df_2):
    set_1 = set(df_1['Hanzi'].tolist())
    set_2 = set(df_2['Hanzi'].tolist())

    if len(set_1.intersection(set_2)) > 0:
        print('\n\nERROR_ERROR_ERROR:\nNew and old sets should not overlap')
        print(set_1)
        print(set_2)
        exit(0)


output_csv_filename = '../raw_data/output.csv'
input_csv_filename = '../raw_data/input.csv'

# read in known output
df_existing_output = pd.read_csv(output_csv_filename)
df_new_input = pd.read_csv(input_csv_filename)

# verify no new input conflicts
verify_no_new_old_duplicates(df_new_input, df_existing_output)

# get info for new input to output

df_new_input['Pinyin'] = df_new_input.apply(lambda row: pinyin_from_hanzi_googletrans(row), axis=1)
df_new_input['Hanzi'] = df_new_input.apply(lambda row: hanzi_with_spaces(row), axis=1)

df_merged = pd.concat([df_existing_output, df_new_input], ignore_index=True)
print(df_merged)

# update output file
df_merged.to_csv(output_csv_filename, index=False)

# remove all data from input file
df_empty = df_new_input[0:0]
df_empty.to_csv(input_csv_filename, index=False)

# create database from output
database_name = "../sql/first.sqlite3"
os.remove(database_name)

con = sqlite3.connect(database_name)
cur = con.cursor()
columns = ('''Hanzi''',
           '''English''',
           '''Difficulty''',
           '''Pinyin''')
cur.execute('''CREATE TABLE Translations
             (
                 [id] INTEGER PRIMARY KEY,
                 [%s] text, 
                 [%s] text,
                 [%s] INTEGER,
                 [%s] text
             )
             ''' % columns)

with open(output_csv_filename, 'rt') as fin:  # `with` statement available in 2.5+
    # csv.DictReader uses first line in file for column headings by default
    dr = csv.DictReader(fin)  # comma is default delimiter
    to_db = [
        (
            i[('%s' % columns[0])],
            i[('%s' % columns[1])],
            i[('%s' % columns[2])],
            i[('%s' % columns[3])],
        )
        for i in dr]

percent_s = ", ".join(['%s'] * len(columns))
question_mark = ", ".join(['?'] * len(columns))
insert_str = ("INSERT INTO Translations (" + percent_s + ") VALUES (" + question_mark + ");")
cur.executemany(insert_str % columns, to_db)
con.commit()
con.close()
