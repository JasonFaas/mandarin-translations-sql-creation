import csv
import sqlite3
import os

import pandas as pd

import sys

from python_src.io_helper import IoHelper

print(sys.version)

# TODO: Delete verification of helper file
ioHelper = IoHelper()
print(ioHelper.other_file('Verification of Helper File'))

data_location = '../data_raw'
empty_csv = '{}/empty.csv'.format(data_location)
input_path = '{}/input/'.format(data_location)
output_path = '{}/output/'.format(data_location)

# print list of files in input
input_file_names = os.listdir(input_path)
input_file_names.sort()

for filename in input_file_names:
    print(filename)
    input_csv_filename = '{}{}'.format(input_path, filename)
    output_csv_filename = '{}{}'.format(output_path, filename)

    # read in known output
    df_new_input = pd.read_csv(input_csv_filename)
    if os.path.isfile(output_csv_filename):
        df_existing_output = pd.read_csv(output_csv_filename)
    else:
        df_existing_output = pd.read_csv(empty_csv)

    # verify no new input conflicts
    ioHelper.verify_no_new_old_duplicates(df_new_input, df_existing_output)

    # get info for new input to output
    df_new_input['Pinyin'] = df_new_input.apply(lambda row: ioHelper.pinyin_from_hanzi_googletrans(row), axis=1)
    df_new_input['Hanzi'] = df_new_input.apply(lambda row: ioHelper.hanzi_with_spaces(row), axis=1)

    df_merged = pd.concat([df_existing_output, df_new_input], ignore_index=True)
    print(df_merged)

    # update output file
    df_merged.to_csv(output_csv_filename, index=False)

    # remove all data from input file
    df_empty = df_new_input[0:0]
    df_empty.to_csv(input_csv_filename, index=False)

# TODO: Make ioHelper above and sqlCreation below different functions


# create database from output
database_name = "../sql/first.sqlite3"
os.remove(database_name)

con = sqlite3.connect(database_name)
cur = con.cursor()
columns = (
    '''fk_parent''',
    '''Difficulty''',
    '''English''',
    '''Hanzi''',
    '''Pinyin'''
)

output_file_names = os.listdir(output_path)
output_file_names.sort()

for filename in output_file_names:
    print('')
    table_name = filename[filename.index('_') + 1:filename.index('.')]
    print(table_name)

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
            )
            for i in dr]
    fk_parent = to_db[0][0]
    if fk_parent == "" or fk_parent == '-1':
        print('no foreign key')
        table_contents_fk_dec = ''
        table_contents_fk_ref = ''
    else:
        foreign_key_table_name = fk_parent[0:fk_parent.index('.')]
        print('foreign key is:{}'.format(foreign_key_table_name))
        fk_column_name = 'fk_{}'.format(foreign_key_table_name)
        table_contents_fk_dec = '[{}] INTEGER,'.format(fk_column_name)
        table_contents_fk_ref = ',FOREIGN KEY({}) REFERENCES {}(id)'.format(fk_column_name, foreign_key_table_name)
    print(to_db[0][2])

    table_contents = '({}{}{}{}{}{}{})'.format(
        '[id] INTEGER PRIMARY KEY,',
        table_contents_fk_dec,
        '[{}] INTEGER,'.format(columns[1]),
        '[{}] text,'.format(columns[2]),
        '[{}] text,'.format(columns[3]),
        '[{}] text'.format(columns[4]),
        table_contents_fk_ref
    )
    contents = '''CREATE TABLE ''' + table_name + ''' ''' + table_contents
    cur.execute(contents)


con.commit()
con.close()

exit(66)

percent_s = ", ".join(['%s'] * len(columns))
question_mark = ", ".join(['?'] * len(columns))
insert_str = ("INSERT INTO " + table_name + " (" + percent_s + ") VALUES (" + question_mark + ");")
cur.executemany(insert_str % columns, to_db)
con.commit()
con.close()
