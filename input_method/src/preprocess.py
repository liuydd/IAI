import json
import re
import string
import os
from pypinyin import lazy_pinyin, Style
import time
import math


start_time1 = time.time()
#得到pinyin->汉字的转化, pinyin2char = {'pinyin': ['汉字1', '汉字2', ...], ...}
with open('./training_data/拼音汉字表.txt', 'r', encoding='gbk') as f:
    pinyin2char = {}
    for line in f:
        items = line.strip().split()
        pinyin = items[0]
        hanzi = items[1:]
        if pinyin not in pinyin2char:
            pinyin2char[pinyin] = []
        pinyin2char[pinyin].extend(hanzi)
with open('./src/pinyin2char.json', 'w', encoding='utf-8') as f:
    json.dump(pinyin2char, f, ensure_ascii=False, indent=4)
end_time1 = time.time()
print('处理拼音汉字表耗时：', end_time1 - start_time1)


start_time2 = time.time()
#有效的汉字，valid_char = [汉字1, 汉字2, ...]
with open('./training_data/一二级汉字表.txt', 'r', encoding='gbk') as f:
    valid_char = list(f.readline().strip())
end_time2 = time.time()
print('处理一二级汉字表耗时：', end_time2 - start_time2)


#处理语料库
start_time3 = time.time()
#得到单字的概率, char_possibility = {'pinyin': {'汉字1': 概率1, '汉字2': 概率2, ...}, ...}
char_possibility = {}

# 定义符号模式
puncs = re.compile(r"\s|[a-zA-Z]|\.|\(|\)|" + "|".join(["，", "。", "、", "：", "；", "？", "！", "（", "）", "《", "》",
                                                       "-", "——", "·", "……", "‘", "’", "“", "”", "/", r"\\", "\\[",
                                                       "\\]", "【", "】", "\\|", "℃"]))

def filter_sentence(sentence):
    # 创建一个包含所有标点符号的字符串
    punctuation = string.punctuation
    # 过滤标点符号和数字
    filtered_sentence = ''.join(char for char in sentence if char not in punctuation and not char.isdigit())
    filtered_sentence = puncs.sub("", filtered_sentence)
    filtered_sentence = re.sub(r'[^\u4e00-\u9fa5]', '', filtered_sentence)
    return filtered_sentence

#word_count = {'汉字1': 频率1, '汉字2': 频率2, ...}
word_count = {}
def cal_freq(file_name):
    with open(file_name, 'r', encoding='gbk') as f:
        for line in f:
            data = json.loads(line)
            html = data['html']
            title = data['title']
            article = title + html
            article = filter_sentence(article)
            pinyin_list = lazy_pinyin(article, style=Style.NORMAL) #考虑会有多音字，故用pypinyin库来注音
            for i in range(len(pinyin_list)):
                #if article[i] not in valid_char: continue
                if pinyin_list[i] not in char_possibility:
                    char_possibility[pinyin_list[i]] = {}
                if article[i] not in char_possibility[pinyin_list[i]]:
                    char_possibility[pinyin_list[i]][article[i]] = 0
                char_possibility[pinyin_list[i]][article[i]] += 1  
                

def cal_freq_without_duoyin(file_name):
    with open(file_name, 'r', encoding='gbk') as f:
        for line in f:
            data = json.loads(line)
            html = data['html']
            title = data['title']
            article = title + html
            article = filter_sentence(article)  
            #不考虑多音字
            for word in article:
                if word not in valid_char: continue
                if word not in word_count:
                    word_count[word] = 0
                word_count[word] += 1 

def gen_char_possibility():
    file_path = './语料库/sina_news_gbk'
    files = os.listdir(file_path)
    for file in files[1:8]:
        print("start one file")
        cal_freq(os.path.join(file_path, file))
        print("finished this file")
    with open('./src/char_frequency.json', 'w', encoding='utf-8') as f: 
        f.write(json.dumps(char_possibility, ensure_ascii=False, indent=2))
    with open('./src/char_frequency.json', 'r', encoding='utf-8') as f:
        char_possibility = json.load(f)
    for pinyin in char_possibility:
        one_pinyin_count = sum(char_possibility[pinyin].values())
        for hanzi in char_possibility[pinyin]:
            char_possibility[pinyin][hanzi] = math.log(one_pinyin_count) - math.log(char_possibility[pinyin][hanzi])
    with open('./src/char_possibility.json', 'w', encoding='utf-8') as f: 
        f.write(json.dumps(char_possibility, ensure_ascii=False, indent=2))
       
        
def gen_char_possibility_without_duoyin():
    file_path = './语料库/sina_news_gbk'
    files = os.listdir(file_path)
    for file in files[1:8]:
        print("start one file")
        cal_freq_without_duoyin(os.path.join(file_path, file))
        print("finished this file")
    for pinyin in pinyin2char:
        item = {}
        for hanzi in pinyin2char[pinyin]:
            item[hanzi] = word_count.get(hanzi, 1)
        char_possibility[pinyin] = item
    for pinyin in char_possibility:
        one_pinyin_count = sum(char_possibility[pinyin].values())
        for hanzi in char_possibility[pinyin]:
            char_possibility[pinyin][hanzi] = math.log(one_pinyin_count) - math.log(char_possibility[pinyin][hanzi])
    with open('./src/char_possibility.json', 'w', encoding='utf-8') as f: 
        f.write(json.dumps(char_possibility, ensure_ascii=False, indent=2))


gen_char_possibility()
end_time3 = time.time()
print('处理语料库得到单字概率耗时：', end_time3 - start_time3)


#得到双字的概率，word_possibility = {'pinyin1_pinyin2': {'词语1': 概率1, '词语2': 概率2, ...}, ...}
start_time4 = time.time()
word_possibility = {}
two_word_count = {}
word_freq = {}
def cal_two_freq(file_name):
    with open(file_name, 'r', encoding='gbk') as f:
        for line in f:
            data = json.loads(line)
            html = data['html']
            title = data['title']
            article = title + html
            article = filter_sentence(article)
            words = list(article)
            for i in range(len(words) - 1):
                two_word = words[i] + ' ' + words[i + 1]
                if two_word not in two_word_count:
                    two_word_count[two_word] = 0
                two_word_count[two_word] += 1
        
file_path = './语料库/sina_news_gbk'
files = os.listdir(file_path)
for file in files[1:8]:
    print("start one file")
    cal_two_freq(os.path.join(file_path, file))
    print("finished this file")   
    
for two_word in two_word_count:
    word_list = two_word.strip().split()
    pinyin_list = lazy_pinyin(''.join(word_list), style=Style.NORMAL)
    pinyins = ' '.join(pinyin_list)
    if pinyins not in word_freq:
        word_freq[pinyins] = {}
    word_freq[pinyins][two_word] = two_word_count[two_word]
with open('./src/word_frequency.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(word_freq, ensure_ascii=False, indent=2))


for pinyins in word_freq:
    two_word_count = sum(word_freq[pinyins].values())
    for hanzi in word_freq[pinyins]:
        word_freq[pinyins][hanzi] = math.log(two_word_count) - math.log(word_freq[pinyins][hanzi])
with open('./src/word_possibility.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(word_freq, ensure_ascii=False, indent=2))
end_time4 = time.time()
print('处理语料库得到双字概率耗时：', end_time4 - start_time4)


#得到三字的概率，trip_possibility = {'pinyin1_pinyin2_pinyin3': {'词语1': 概率1, '词语2': 概率2, ...}, ...}
start_time5 = time.time()
trip_possibility = {}
three_word_count = {}
trip_freq = {}
def cal_three_freq(file_name):
    with open(file_name, 'r', encoding='gbk') as f:
        for line in f:
            data = json.loads(line)
            html = data['html']
            title = data['title']
            article = title + html
            article = filter_sentence(article)
            words = list(article)
            for i in range(len(words) - 2):
                three_word = words[i] + ' ' + words[i + 1] + ' ' + words[i + 2]
                if three_word not in three_word_count:
                    three_word_count[three_word] = 0
                three_word_count[three_word] += 1

        
file_path = './语料库/sina_news_gbk'
files = os.listdir(file_path)
for file in files[1:8]:
    print("start one file")
    cal_three_freq(os.path.join(file_path, file))
    print("finished this file")   
    
for three_word in three_word_count:
    word_list = three_word.strip().split()
    pinyin_list = lazy_pinyin(''.join(word_list), style=Style.NORMAL)
    pinyins = ' '.join(pinyin_list)
    if pinyins not in trip_freq:
        trip_freq[pinyins] = {}
    trip_freq[pinyins][three_word] = three_word_count[three_word]
with open('./src/trip_frequency.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(trip_freq, ensure_ascii=False, indent=2))


for pinyins in trip_freq:
    three_word_count = sum(trip_freq[pinyins].values())
    for hanzi in trip_freq[pinyins]:
        trip_freq[pinyins][hanzi] = math.log(three_word_count) - math.log(trip_freq[pinyins][hanzi])
with open('./src/trip_possibility.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(trip_freq, ensure_ascii=False, indent=2))
end_time5 = time.time()
print("处理语料库得到三字概率耗时：", end_time5 - start_time5)