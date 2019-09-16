import csv
import sqlite3
import os

import sys
import pinyin

import jieba

print(sys.version)

nh = '你 好'
print(nh)
print(pinyin.get(nh))

print("\n")

# nh2 = '我是美国人'
nh2 = '我是美国人'
print(nh2)
print(pinyin.get(nh2, delimiter=" "))
print(pinyin.get(nh2, format="strip", delimiter=" "))
print(pinyin.get(nh2, format="numerical"))
print(pinyin.get_initial(nh2))

print("\n Starting Jieba")
seg_list = jieba.cut(nh2, cut_all=True)
print("Cut All True:\t" + " ".join(seg_list))  # 全模式

seg_list = jieba.cut(nh2, cut_all=False)
print("Cut All False:\t" + " ".join(seg_list))  # 默认模式

seg_list = jieba.cut(nh2)
print("Default Mode:\t" + " ".join(seg_list))

seg_list = jieba.cut_for_search(nh2)  # 搜索引擎模式
print("Cut For Search:\t" + " ".join(seg_list))

# What Jason is interested in:
print("\nJason")
seg_list = jieba.cut(nh2)
what = " ".join(seg_list)
print(what)
hanzi_arr = what.split(" ")
print(hanzi_arr)
pinyin_arr = pinyin.get(nh2, delimiter=" ").split(" ")
print(pinyin_arr)

print("\n")
pinyin_itr = 0
pinyin_final = ""
for hanzi_group in hanzi_arr:
    print(hanzi_group)
    pinyin_group = pinyin_arr[pinyin_itr:pinyin_itr + len(hanzi_group)]
    pinyin_corr = ""
    for pinyin_char in pinyin_group:
        pinyin_corr += pinyin_char
    pinyin_final += pinyin_corr + " "
    print(pinyin_corr)
    pinyin_itr += len(hanzi_group)
    print("")

print(pinyin_final.strip())
