import csv
import os


class DbHelper(object):
    def __init__(self, cur, OUTPUT_PATH, COLUMNS, FK_PARENT, MANUAL_LEVEL, AUTO_LEVEL, BLANKS, ENGLISH, HANZI, PINYIN):
        self.cur = cur
        self.OUTPUT_PATH = OUTPUT_PATH
        self.COLUMNS = COLUMNS
        self.FK_PARENT = FK_PARENT
        self.MANUAL_LEVEL = MANUAL_LEVEL
        self.AUTO_LEVEL = AUTO_LEVEL
        self.BLANKS = BLANKS
        self.ENGLISH = ENGLISH
        self.HANZI = HANZI
        self.PINYIN = PINYIN

        self.COLUMNS_QUESTION_MARKS = ", ".join(['?'] * len(self.COLUMNS))
        self.INSERT_BASE = "INSERT INTO {{}} {} VALUES ( {} )".format(str(self.COLUMNS), self.COLUMNS_QUESTION_MARKS)

    def writeTranslations(self):
        output_file_names = os.listdir(self.OUTPUT_PATH)
        output_file_names.sort()

        db_in_mem = {}

        for filename in output_file_names:
            if filename[0] == '-':
                continue
            print('Writing to {}'.format(filename))
            is_input_to_primary_table = filename[0] == '0'
            is_hsk_file = 'HSK_' == filename[:4]

            create_new_table = False

            if is_input_to_primary_table:
                table_name = 'translations'
                create_new_table = '0000' == filename[0:4]
            elif is_hsk_file:
                table_name = 'hsk'
                create_new_table = 'HSK_1.csv' == filename
            else:
                table_name = filename[filename.index('_') + 1:filename.index('.')]
                create_new_table = True

            output_csv_filename = '{}{}'.format(self.OUTPUT_PATH, filename)
            with open(output_csv_filename, 'rt') as fin:  # `with` statement available in 2.5+
                # csv.DictReader uses first line in file for column headings by default
                dr = csv.DictReader(fin)  # comma is default delimiter

                # TODO: Fix bug here, but trying to get through a few things first
                # print('\n')
                # for what in dr:
                #     print(what)

                to_db = [
                    (
                        i[('%s' % self.COLUMNS[0])],
                        i[('%s' % self.COLUMNS[1])],
                        i[('%s' % self.COLUMNS[2])],
                        i[('%s' % self.COLUMNS[3])],
                        i[('%s' % self.COLUMNS[4])],
                        i[('%s' % self.COLUMNS[5])],
                        i[('%s' % self.COLUMNS[6])],
                        i[('%s' % self.COLUMNS[7])],
                    )
                    for i in dr]

            if not is_input_to_primary_table:
                db_in_mem[table_name] = {}
                for idx, row in enumerate(to_db):
                    english_value = row[self.COLUMNS.index(self.ENGLISH)]
                    db_in_mem[table_name][english_value] = idx

            fk_parent = to_db[0][0]
            no_fk_ref = fk_parent == "" or fk_parent == '-1'
            if no_fk_ref:
                table_contents_fk_ref = ''
                for idx in range(len(to_db)):
                    to_db[idx] = (-1,) + to_db[idx][1:]
            else:
                foreign_key_table_name = fk_parent[0:fk_parent.index('.')]
                table_contents_fk_ref = ',FOREIGN KEY({}) REFERENCES {}(id)'.format(self.FK_PARENT, foreign_key_table_name)
                for idx in range(len(to_db)):
                    ref_split = str(to_db[idx][0]).split('.')
                    to_db[idx] = (db_in_mem[ref_split[0]][ref_split[1]] + 1,) + to_db[idx][1:]

            if create_new_table:
                print("Creating new table {}".format(table_name))
                # TODO: Be careful here with `self.COLUMNS[:3]:`
                # TODO: Clean this up!!!

                table_cont_new = '('
                table_cont_new += '[id] INTEGER PRIMARY KEY,'
                for col in self.COLUMNS[:3]:
                    table_cont_new += '[{}] INTEGER,'.format(col)
                for col in self.COLUMNS[3:-1]:
                    table_cont_new += '[{}] text,'.format(col)
                for col in self.COLUMNS[-1:]:
                    table_cont_new += '[{}] text'.format(col)
                table_cont_new += table_contents_fk_ref
                table_cont_new += ')'

                contents = '''CREATE TABLE ''' + table_name + ''' ''' + table_cont_new
                self.cur.execute(contents)

            insert_str = self.INSERT_BASE.format(table_name)

            self.cur.executemany(insert_str, to_db)

    # def writeHskTable(self):
    #     table_name = '''hsk_info'''
    #
    #     hsk_table_creation = '''CREATE TABLE'''
    #     hsk_table_creation += ''' '''
    #     hsk_table_creation += table_name
    #     hsk_table_creation += ''' '''
    #     hsk_table_creation += '''([id] INTEGER PRIMARY KEY,[fk_parent] INTEGER,[Manual_Level] INTEGER,[Auto_Level] INTEGER,[Blanks] text,[English] text,[Hanzi] text,[Pinyin] text)'''
    #     self.cur.execute(hsk_table_creation)
    #
    #     insert_str = self.INSERT_BASE.format(table_name)
    #
    #     self.cur.executemany(insert_str, to_db)
