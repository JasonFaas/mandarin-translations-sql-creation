import sqlite3
import os

import pandas as pd

import sys

from python_src.io_helper import IoHelper
from python_src.db_helper import DbHelper

print(sys.version)

FK_PARENT = '''fk_parent'''
MANUAL_LEVEL = '''Manual_Level'''
AUTO_LEVEL = '''Auto_Level'''
BLANKS = '''Blanks'''
ENGLISH = '''English'''
HANZI = '''Hanzi'''
PINYIN = '''Pinyin'''
PINYIN_2 = '''2nd_Pinyin'''
COLUMNS = (
    FK_PARENT,
    MANUAL_LEVEL,
    AUTO_LEVEL,
    BLANKS,
    ENGLISH,
    HANZI,
    PINYIN,
    PINYIN_2,
)
sleep_time = 0.1

ioHelper = IoHelper(sleep_time, COLUMNS, FK_PARENT, MANUAL_LEVEL, AUTO_LEVEL, BLANKS, ENGLISH, HANZI, PINYIN, PINYIN_2)
ioHelper.prepareAutoLevel()
ioHelper.runUnitTests()

data_location = '../data_raw'
OUTPUT_PATH = '{}/output/'.format(data_location)

output_file_names = os.listdir(OUTPUT_PATH)
output_file_names.sort()

print("Sleep each translation for {} seconds.".format(sleep_time))

for filename in output_file_names:
    print('Working with {}'.format(filename))
    output_csv_filename = '{}{}'.format(OUTPUT_PATH, filename)

    # read in output
    df_output = pd.read_csv(output_csv_filename, dtype=str)

    # verify no new input conflicts
    # TODO: Update verification that there no 2 hanzi are same
    # ioHelper.verify_no_new_old_duplicates(df_new_input, df_existing_output)

    df_output[HANZI] = df_output.apply(lambda row: ioHelper.spaces_for_hanzi_if_no_pinyin(row), axis=1)

    # TODO: Seriously, fix this
    df_output[PINYIN] = df_output.apply(lambda row: ioHelper.pinyin_from_hanzi_googletrans_if_no_pinyin(row), axis=1)

    df_output[PINYIN_2] = df_output.apply(lambda row: ioHelper.pinyin_2_none_to_empty(row), axis=1)

    df_output[AUTO_LEVEL] = df_output.apply(lambda row: ioHelper.auto_level_if_no_level(row), axis=1)

    # TODO: Hold this for now, but remove if all is well
    # df_new_input[MANUAL_LEVEL] = df_new_input.apply(lambda row: ioHelper.manual_level(row), axis=1)

    df_output.to_csv(output_csv_filename, index=False, header=True, columns=COLUMNS)


# TODO: Make ioHelper above and sqlCreation below different functions


# create database from output
database_name = "../sql/first.sqlite3"
os.remove(database_name)

con = sqlite3.connect(database_name)
cur = con.cursor()

dbHelper = DbHelper(cur, OUTPUT_PATH, COLUMNS, FK_PARENT, MANUAL_LEVEL, AUTO_LEVEL, BLANKS, ENGLISH, HANZI, PINYIN)
dbHelper.writeTranslations()




con.commit()
con.close()
