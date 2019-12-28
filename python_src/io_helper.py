import jieba
import pinyin

from googletrans import Translator

import random


class IoHelper(object):

    def __init__(self):
        self.googletrans_translator = Translator()
        self.hsk_word_list = {}
        self.hsk_char_list = {}

    def pinyin_from_hanzi(self, row):
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

    def auto_level(self, row):
        nh2 = row['Hanzi'].replace(' ', '')
        print(nh2)

        # TODO: About to put auto here:
        # If in a hsk_word_list, multiple by 10 and that is the level
        # Else
        #   find char_level for each char
        #   If char level cannot be found, then make it 7
        #   (Highest_value * 10) + each of other levels
        #   Max level 99


        return random.randint(1, 99)

    def hanzi_with_spaces(self, row):
        nh2 = row['Hanzi'].replace(' ', '')

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

    def pinyin_from_hanzi_googletrans(self, row):
        hanzi = row['Hanzi'].replace(' ', '')
        gt_translation = self.googletrans_translator.translate(hanzi, src='zh-cn', dest='en')
        # print(gt_translation, flush=True)
        # print(gt_translation.extra_data, flush=True)
        # print(gt_translation.origin, ' -> ', gt_translation.text, flush=True)
        translation_return = gt_translation.extra_data['translation'][1][-1].lower()
        # print(gt_translation.origin, ' -> ', translation_return)
        # print('\n', flush=True)

        return translation_return

    def verify_no_new_old_duplicates(self, df_1, df_2):
        set_1 = set(df_1['Hanzi'].tolist())
        set_2 = set(df_2['Hanzi'].tolist())

        if len(set_1.intersection(set_2)) > 0:
            print('\n\nERROR_ERROR_ERROR:\nNew and old sets should not overlap')
            print(set_1)
            print(set_2)
            exit(0)

    def prepareAutoLevel(self):
        for hsk_level in range(1,7):
            with open('../hsk_list/HSK_{}.txt'.format(hsk_level), mode='r', encoding='utf-8-sig') as fp:
                content = fp.readlines()
            content = [x.strip() for x in content]
            self.hsk_word_list[hsk_level] = content
            self.hsk_char_list[hsk_level] = ''.join(content)
