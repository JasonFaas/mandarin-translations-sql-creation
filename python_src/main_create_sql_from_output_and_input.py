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

ioHelper = IoHelper(sleep_time, COLUMNS, FK_PARENT, MANUAL_LEVEL, AUTO_LEVEL, BLANKS, ENGLISH, HANZI, PINYIN)
ioHelper.prepareAutoLevel()
ioHelper.runUnitTests()

data_location = '../data_raw'
empty_csv = '{}/empty.csv'.format(data_location)
input_path = '{}/input/'.format(data_location)
output_path = '{}/output/'.format(data_location)

input_file_names = os.listdir(input_path)
input_file_names.sort()

print("Sleep each translation for {} seconds.".format(sleep_time))

for filename in input_file_names:
    print('Working with {}'.format(filename))
    input_csv_filename = '{}{}'.format(input_path, filename)
    output_csv_filename = '{}{}'.format(output_path, filename)

    # read in known output
    df_new_input = pd.read_csv(input_csv_filename, dtype=str)
    if os.path.isfile(output_csv_filename):
        df_existing_output = pd.read_csv(output_csv_filename)
    else:
        df_existing_output = pd.read_csv(empty_csv)

    # verify no new input conflicts
    ioHelper.verify_no_new_old_duplicates(df_new_input, df_existing_output)

    # get info for new input to output
    df_new_input[PINYIN] = df_new_input.apply(lambda row: ioHelper.pinyin_from_hanzi_googletrans(row), axis=1)
    exit(66)
    df_new_input[HANZI] = df_new_input.apply(lambda row: ioHelper.hanzi_with_spaces(row), axis=1)
    df_new_input[AUTO_LEVEL] = df_new_input.apply(lambda row: ioHelper.auto_level(row), axis=1)
    df_new_input[MANUAL_LEVEL] = df_new_input.apply(lambda row: ioHelper.manual_level(row), axis=1)

    df_merged = pd.concat([df_existing_output, df_new_input], ignore_index=True, sort=False)

    # update output file
    df_merged.to_csv(output_csv_filename, index=False, header=True, columns=COLUMNS)

    # remove all data from input file
    df_empty = df_new_input[0:0]
    df_empty.to_csv(input_csv_filename, index=False)

    os.remove(input_csv_filename)

# TODO: Make ioHelper above and sqlCreation below different functions


# create database from output
database_name = "../sql/first.sqlite3"
os.remove(database_name)

con = sqlite3.connect(database_name)
cur = con.cursor()

dbHelper = DbHelper(cur, output_path, COLUMNS, FK_PARENT, MANUAL_LEVEL, AUTO_LEVEL, BLANKS, ENGLISH, HANZI, PINYIN)
dbHelper.writeTranslations()




con.commit()
con.close()
