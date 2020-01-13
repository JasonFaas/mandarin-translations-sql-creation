import jieba
import pinyin
import time

from googletrans import Translator

import random

MAX_HSK_LEVEL_PLUS_ONE = 7 + 1


class IoHelper(object):

    def __init__(self, sleep_time, COLUMNS, FK_PARENT, MANUAL_LEVEL, AUTO_LEVEL, BLANKS, ENGLISH, HANZI, PINYIN, PINYIN_2):
        self.googletrans_translator = Translator()
        self.hsk_word_list = {}
        self.hsk_char_list = {}
        self.sleep_time = sleep_time

        self.COLUMNS = COLUMNS
        self.FK_PARENT = FK_PARENT
        self.MANUAL_LEVEL = MANUAL_LEVEL
        self.AUTO_LEVEL = AUTO_LEVEL
        self.BLANKS = BLANKS
        self.ENGLISH = ENGLISH
        self.HANZI = HANZI
        self.PINYIN = PINYIN
        self.PINYIN_2 = PINYIN_2

    def pinyin_from_hanzi(self, row):
        nh2 = row[self.HANZI]

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

    def manual_level(self, row):
        return str(int(float(row[self.MANUAL_LEVEL])))

    def auto_level_if_no_level(self, row):
        return_level = 100

        try:
            current_level = str(row[self.AUTO_LEVEL])
            verify = int(current_level) > 0
            return current_level
        except Exception as e:
            pass


        hanzi_with_spaces = str(row[self.HANZI])
        if ',' in hanzi_with_spaces:
            raise Exception(":{}: has an invalid character".format(hanzi_with_spaces))
        for char_to_remove in ['.', '。', '？', '?']:
            hanzi_with_spaces = hanzi_with_spaces.replace(char_to_remove, '')
        without_spaces = hanzi_with_spaces.replace(' ', '')

        try:
            hsk_level = self.get_word_hsk_level(without_spaces)
            return_level = hsk_level * 3
        except Exception as e:
            auto_level = 0
            while '{' in hanzi_with_spaces:
                auto_level += 5
                open_index = max(hanzi_with_spaces.index('{') - 1, 0)
                close_index = min(hanzi_with_spaces.index('}') + 1, len(hanzi_with_spaces))
                hanzi_with_spaces = hanzi_with_spaces[:open_index] + hanzi_with_spaces[close_index:]
                hanzi_with_spaces = hanzi_with_spaces.strip()

            word_split = hanzi_with_spaces.split(' ')
            level_list = []
            for word in word_split:
                try:
                    level = self.get_word_hsk_level(word)
                    level_list.append(level * 2)
                except Exception as e:
                    try:
                        for single_char in word:
                            level = self.get_char_hsk_level(single_char)
                            level_list.append(level * 4)
                    except Exception as e:
                        level_list.append(100)


            level_list_val = auto_level

            if len(level_list) > 0:
                level_list_val += sum(level_list)
            else:
                level_list_val += 5
            return_level = level_list_val
        return str(return_level)

    def get_word_hsk_level(self, without_spaces):
        for hsk_level in range(1, MAX_HSK_LEVEL_PLUS_ONE):
            if without_spaces in self.hsk_word_list[hsk_level]:
                return hsk_level
        raise Exception('Word not in HSK list')

    def get_char_hsk_level(self, single_hanzi):
        for hsk_level in range(1, MAX_HSK_LEVEL_PLUS_ONE):
            if single_hanzi in self.hsk_char_list[hsk_level]:
                return hsk_level
        raise Exception('Single Char not in HSK list')

    def spaces_for_hanzi_if_no_pinyin(self, row):
        pinyin_value = row[self.PINYIN]

        try:
            if pinyin_value and pinyin_value is str and len(pinyin_value) > 0:
                return row[self.HANZI]
        except Exception as e:
            print('Jason')
            print(row[self.HANZI])
            print(type(pinyin_value))
            print(pinyin_value)
            print('Faas')
            raise e


        nh2 = row[self.HANZI].replace(' ', '')

        seg_list = jieba.cut(nh2)
        with_spaces = ''
        inside_bracket = False
        for piece in seg_list:
            with_spaces += piece
            if piece == '{':
                inside_bracket = True
            if piece == '}':
                inside_bracket = False

            if not inside_bracket:
                with_spaces += ' '
        return with_spaces.strip()

    def pinyin_2_none_to_empty(self, row):
        pinyin_2 = row[self.PINYIN_2]
        if pinyin_2:
            return pinyin_2
        else:
            return ''

    def pinyin_from_hanzi_googletrans_if_no_pinyin(self, row):
        column_count = len(row)
        if column_count != 8:
            raise Exception("Columns did not equal 8".format(column_count))

        hanzi_value = row[self.HANZI]
        pinyin_value = row[self.PINYIN]
        hanzi = hanzi_value.replace(' ', '')
        print('\n{} {} jason'.format(hanzi, pinyin_value))

        if pinyin_value and pinyin_value is str and len(pinyin_value) > 0:
            return pinyin_value

        # TODO: Delete line below...why isn't that working???
        return 'JAF_Test'

        time.sleep(self.sleep_time)

        gt_translation = self.googletrans_translator.translate(hanzi, src='zh-cn', dest='en')
        print(gt_translation, flush=True)
        print(gt_translation.extra_data, flush=True)
        print(gt_translation.origin, ' -> ', gt_translation.text, flush=True)
        translation_ = gt_translation.extra_data['translation']
        if len(translation_) < 2:
            return 'JAF_Error'
        translation__ = translation_[1]
        translation___ = translation__[-1]
        translation_return = translation___.lower()
        # print(gt_translation.origin, ' -> ', translation_return)
        # print('\n', flush=True)

        return translation_return

    # TODO: Supposed to update this to output-only paradigm
    # def verify_no_new_old_duplicates(self, df_1, df_2):
    #     set_1 = set(df_1[self.HANZI].tolist())
    #     set_2 = set(df_2[self.HANZI].tolist())
    #
    #     if len(set_1.intersection(set_2)) > 0:
    #         print('\n\nERROR_ERROR_ERROR:\nNew and old sets should not overlap')
    #         print(set_1)
    #         print(set_2)
    #         exit(0)

    def prepareAutoLevel(self):
        for hsk_level in range(1, MAX_HSK_LEVEL_PLUS_ONE):
            with open('../hsk_list/HSK_{}.txt'.format(hsk_level), mode='r', encoding='utf-8-sig') as fp:
                content = fp.readlines()
            content = [x.strip() for x in content]
            self.hsk_word_list[hsk_level] = content
            self.hsk_char_list[hsk_level] = ''.join(content)

    def runUnitTests(self):
        assert str(10) == self.manual_level({'Manual_Level': 10.0, })
        assert str(10) == self.manual_level({'Manual_Level': 10, })
        assert str(10) == self.manual_level({'Manual_Level': '10.0', })
        assert str(10) == self.manual_level({'Manual_Level': '10', })


        self.test_auto_level_phrase_and_expected('爸爸', 1 * 3)
        self.test_auto_level_phrase_and_expected('爸爸 和 妈妈', (1 + 1 + 1) * 2)
        self.test_auto_level_phrase_and_expected('{ref:0;example:exampless} 我 最 喜欢 的 {ref:1;type:food_type} 是 {ref:2;type:food;fk_ref:1}',
                                                 (3 * 5 + ((1 * 4) + 2) * 2))
        self.test_auto_level_phrase_and_expected('你 好', 2 + 2)
        self.test_auto_level_phrase_and_expected('你好', 4 + 4)

    def test_auto_level_phrase_and_expected(self, phrase, expected_level):
        auto_level = self.auto_level_if_no_level(self.autoPackage(phrase))
        assert str(expected_level) == auto_level, auto_level

    def autoPackage(self, phrase):
        return {self.HANZI: phrase, }
