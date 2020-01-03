import csv
import sqlite3
import os

import pandas as pd

import sys

from python_src.io_helper import IoHelper

print(sys.version)

columns = (
    '''fk_parent''',
    '''Manual_Level''',
    '''Auto_Level''',
    '''Blanks''',
    '''English''',
    '''Hanzi''',
    '''Pinyin''',
)
fk_parent_row = 0
manual_level_row = 1
auto_level_row = 2
blanks_row = 3
english_row = 4
hanzi_row = 5
pinyin_row = 6

ioHelper = IoHelper()
ioHelper.prepareAutoLevel()
ioHelper.runUnitTests()

data_location = '../data_raw'
empty_csv = '{}/empty.csv'.format(data_location)
input_path = '{}/input/'.format(data_location)
output_path = '{}/output/'.format(data_location)

input_file_names = os.listdir(input_path)
input_file_names.sort()

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
    df_new_input[columns[pinyin_row]] = df_new_input.apply(lambda row: ioHelper.pinyin_from_hanzi_googletrans(row), axis=1)
    df_new_input[columns[hanzi_row]] = df_new_input.apply(lambda row: ioHelper.hanzi_with_spaces(row), axis=1)
    df_new_input[columns[auto_level_row]] = df_new_input.apply(lambda row: ioHelper.auto_level(row), axis=1)
    df_new_input[columns[manual_level_row]] = df_new_input.apply(lambda row: ioHelper.manual_level(row), axis=1)

    df_merged = pd.concat([df_existing_output, df_new_input], ignore_index=True, sort=False)

    # update output file
    df_merged.to_csv(output_csv_filename, index=False, header=True, columns=columns)

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

output_file_names = os.listdir(output_path)
output_file_names.sort()

db_in_mem = {}

for file_idx, filename in enumerate(output_file_names):
    is_input_to_primary_table = filename[0] == '0'
    if is_input_to_primary_table:
        table_name = 'translations'
    else:
        table_name = filename[filename.index('_') + 1:filename.index('.')]

    output_csv_filename = '{}{}'.format(output_path, filename)
    with open(output_csv_filename, 'rt') as fin:  # `with` statement available in 2.5+
        # csv.DictReader uses first line in file for column headings by default
        dr = csv.DictReader(fin)  # comma is default delimiter
        to_db = [
            (
                i[('%s' % columns[0])],
                i[('%s' % columns[1])],
                i[('%s' % columns[2])],
                i[('%s' % columns[3])],
                i[('%s' % columns[4])],
                i[('%s' % columns[5])],
                i[('%s' % columns[6])],
            )
            for i in dr]

    if not is_input_to_primary_table:
        db_in_mem[table_name] = {}
        for idx, row in enumerate(to_db):
            english_value = row[english_row]
            db_in_mem[table_name][english_value] = idx

    fk_parent = to_db[0][0]
    no_fk_ref = fk_parent == "" or fk_parent == '-1'
    if no_fk_ref:
        table_contents_fk_ref = ''
        for idx in range(len(to_db)):
            to_db[idx] = (-1,) + to_db[idx][1:]
    else:
        foreign_key_table_name = fk_parent[0:fk_parent.index('.')]
        table_contents_fk_ref = ',FOREIGN KEY({}) REFERENCES {}(id)'.format(columns[0], foreign_key_table_name)
        for idx in range(len(to_db)):
            ref_split = str(to_db[idx][0]).split('.')
            to_db[idx] = (db_in_mem[ref_split[0]][ref_split[1]] + 1,) + to_db[idx][1:]

    if file_idx == 0 or not is_input_to_primary_table:

        table_cont_new = '('
        table_cont_new += '[id] INTEGER PRIMARY KEY,'
        for col in columns[:3]:
            table_cont_new += '[{}] INTEGER,'.format(col)
        for col in columns[3:-1]:
            table_cont_new += '[{}] text,'.format(col)
        for col in columns[-1:]:
            table_cont_new += '[{}] text'.format(col)
        table_cont_new += table_contents_fk_ref
        table_cont_new += ')'

        contents = '''CREATE TABLE ''' + table_name + ''' ''' + table_cont_new
        cur.execute(contents)

    percent_s = ", ".join(['%s'] * len(columns))
    question_mark = ", ".join(['?'] * len(columns))
    insert_str = ("INSERT INTO " + table_name + " (" + percent_s + ") VALUES (" + question_mark + ");")

    cur.executemany(insert_str % columns, to_db)

con.commit()
con.close()
