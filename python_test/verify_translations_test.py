import sys
import pinyin

from googletrans import Translator

"""
LANGUAGES = {
    'af': 'afrikaans',
    'sq': 'albanian',
    'am': 'amharic',
    'ar': 'arabic',
    'hy': 'armenian',
    'az': 'azerbaijani',
    'eu': 'basque',
    'be': 'belarusian',
    'bn': 'bengali',
    'bs': 'bosnian',
    'bg': 'bulgarian',
    'ca': 'catalan',
    'ceb': 'cebuano',
    'ny': 'chichewa',
    'zh-cn': 'chinese (simplified)',
    'zh-tw': 'chinese (traditional)',
    'co': 'corsican',
    'hr': 'croatian',
    'cs': 'czech',
    'da': 'danish',
    'nl': 'dutch',
    'en': 'english',
    'eo': 'esperanto',
    'et': 'estonian',
    'tl': 'filipino',
    'fi': 'finnish',
    'fr': 'french',
    'fy': 'frisian',
    'gl': 'galician',
    'ka': 'georgian',
    'de': 'german',
    'el': 'greek',
    'gu': 'gujarati',
    'ht': 'haitian creole',
    'ha': 'hausa',
    'haw': 'hawaiian',
    'iw': 'hebrew',
    'hi': 'hindi',
    'hmn': 'hmong',
    'hu': 'hungarian',
    'is': 'icelandic',
    'ig': 'igbo',
    'id': 'indonesian',
    'ga': 'irish',
    'it': 'italian',
    'ja': 'japanese',
    'jw': 'javanese',
    'kn': 'kannada',
    'kk': 'kazakh',
    'km': 'khmer',
    'ko': 'korean',
    'ku': 'kurdish (kurmanji)',
    'ky': 'kyrgyz',
    'lo': 'lao',
    'la': 'latin',
    'lv': 'latvian',
    'lt': 'lithuanian',
    'lb': 'luxembourgish',
    'mk': 'macedonian',
    'mg': 'malagasy',
    'ms': 'malay',
    'ml': 'malayalam',
    'mt': 'maltese',
    'mi': 'maori',
    'mr': 'marathi',
    'mn': 'mongolian',
    'my': 'myanmar (burmese)',
    'ne': 'nepali',
    'no': 'norwegian',
    'ps': 'pashto',
    'fa': 'persian',
    'pl': 'polish',
    'pt': 'portuguese',
    'pa': 'punjabi',
    'ro': 'romanian',
    'ru': 'russian',
    'sm': 'samoan',
    'gd': 'scots gaelic',
    'sr': 'serbian',
    'st': 'sesotho',
    'sn': 'shona',
    'sd': 'sindhi',
    'si': 'sinhala',
    'sk': 'slovak',
    'sl': 'slovenian',
    'so': 'somali',
    'es': 'spanish',
    'su': 'sundanese',
    'sw': 'swahili',
    'sv': 'swedish',
    'tg': 'tajik',
    'ta': 'tamil',
    'te': 'telugu',
    'th': 'thai',
    'tr': 'turkish',
    'uk': 'ukrainian',
    'ur': 'urdu',
    'uz': 'uzbek',
    'vi': 'vietnamese',
    'cy': 'welsh',
    'xh': 'xhosa',
    'yi': 'yiddish',
    'yo': 'yoruba',
    'zu': 'zulu',
    'fil': 'Filipino',
    'he': 'Hebrew'
}
"""

print(sys.version, flush=True)
verifications = [
    ['你好', 'nǐhǎo'],
    ['我今年三十二岁', 'wǒjīnniánsānshí\'èrsuì'],
    ['你叫什么名字', 'nǐjiàoshénmemíngzì'],
]

print('\nVerifying Translations With \'pinyin\'', flush=True)
pinyin_errors = False
for hanzi_text, pinyin_text in verifications:
    translation = pinyin.get(hanzi_text, delimiter="")
    if translation != pinyin_text:
        pinyin_errors = True
        print('{} -> {} != {}'.format(hanzi_text, translation, pinyin_text), flush=True)



what_me = {'translation':
    [
        ["I'm thirty-two year", '我今年三十二岁', None, None, 0],
        [None, None, None, "Wǒ jīnnián sānshí'èr suì"]
    ],
    }
# print("\nTesting\n")
# first = what_me['translation'][1][-1]
# print(first)
# print(first.lower())
# # second = first[1]
# # print(second)
# # third = second[-1]
# # print(third)
# # # fourth = third[-1]
# # # print(fourth)
# # print(what_me)
# exit(0)

print('\nVerifying Translations With \'googletrans\'', flush=True)
googletrans_errors = False
googletrans_translator = Translator()
for hanzi_text, pinyin_text in verifications:
    translation = googletrans_translator.translate(hanzi_text, src='zh-cn', dest='en')
    print(translation, flush=True)
    print(translation.extra_data, flush=True)
    # print(translation.origin, ' -> ', translation.text, flush=True)
    googletrans_to_pinyin = translation.extra_data['translation'][1][-1].lower().replace(' ', '')
    print(translation.origin, ' -> ', googletrans_to_pinyin)
    print('\n', flush=True)

    if googletrans_to_pinyin != pinyin_text:
        googletrans_errors = True
        print('{} -> {} != {}'.format(hanzi_text, googletrans_to_pinyin, pinyin_text), flush=True)

print('\n', flush=True)
assert not googletrans_errors
assert not pinyin_errors
