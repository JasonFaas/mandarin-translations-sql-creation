import jieba
import pinyin

from googletrans import Translator


class IoHelper(object):

    def __init__(self):
        self.googletrans_translator = Translator()

    def other_file(self, import_str):
        return '{} World'.format(import_str)

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

    def hanzi_with_spaces(self, row):
        nh2 = row['Hanzi'].replace(' ', '')

        seg_list = jieba.cut(nh2)
        what = " ".join(seg_list)
        return what

    def pinyin_from_hanzi_googletrans(self, row):
        hanzi = row['Hanzi'].replace(' ', '')
        gt_translation = self.googletrans_translator.translate(hanzi, src='zh-cn', dest='en')
        print(gt_translation, flush=True)
        print(gt_translation.extra_data, flush=True)
        # print(gt_translation.origin, ' -> ', gt_translation.text, flush=True)
        translation_return = gt_translation.extra_data['translation'][1][-1].lower()
        print(gt_translation.origin, ' -> ', translation_return)
        print('\n', flush=True)

        return translation_return

    def verify_no_new_old_duplicates(self, df_1, df_2):
        set_1 = set(df_1['Hanzi'].tolist())
        set_2 = set(df_2['Hanzi'].tolist())

        if len(set_1.intersection(set_2)) > 0:
            print('\n\nERROR_ERROR_ERROR:\nNew and old sets should not overlap')
            print(set_1)
            print(set_2)
            exit(0)
