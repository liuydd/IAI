import json
import math

#得到pinyin->汉字的转化, pinyin2char = {'pinyin': ['汉字1', '汉字2', ...], ...}
with open('./word2pinyin.txt', 'r', encoding='utf-8') as f:
    pinyin2char = {}
    for line in f:
        word, pinyin = line.strip().split()
        if pinyin not in pinyin2char:
            pinyin2char[pinyin] = []
        pinyin2char[pinyin].append(word)

#得到单字的概率, char_possibility = {'pinyin': {'汉字1': 概率1, '汉字2': 概率2, ...}, ...}
with open('./1_word.txt', 'r', encoding='utf-8') as f:
    unigram = json.load(f)    
one_word_count = 0
for pinyin in unigram:
    one_word_count += sum(unigram[pinyin]['counts'])
char_possibility = {}
for pinyin in unigram:
    if pinyin not in char_possibility:
        char_possibility[pinyin] = {}
    cp = {}
    for i in range(len(unigram[pinyin]['words'])):
        word = unigram[pinyin]['words'][i]
        count = unigram[pinyin]['counts'][i]
        poss = math.log(one_word_count) - math.log(count)
        cp[word] = poss
    char_possibility[pinyin] = cp
    
#word_possibility = {'汉字': {'pinyin': {'汉字': 概率, ...}, ...}, ...}    
with open('./2_word.txt', 'r', encoding='utf-8') as f:
    bigram = json.load(f)
two_word_count = 0
for pinyins in bigram:
    two_word_count += sum(bigram[pinyins]['counts'])
word_possibility = {}
for pinyin2 in bigram:
    pinyin_list = pinyin2.strip().split()
    word_list = bigram[pinyin2]['words']
    count_list = bigram[pinyin2]['counts']
    for i in range(len(word_list)):
        words = word_list[i]
        word = words.strip().split()
        if word[0] not in word_possibility:
            word_possibility[word[0]] = {}
        if pinyin_list[1] not in word_possibility[word[0]]:
            word_possibility[word[0]][pinyin_list[1]] = {}
        word_possibility[word[0]][pinyin_list[1]][word[1]] = math.log(two_word_count) - math.log(count_list[i])


def vertebi(pinyin_list, char_list, stack):
    length = len(pinyin_list)
    str_len = 0 #目前计算到的字符串长度
    for key in stack:
        str_len = len(key)
        break
    if str_len == length:
        return stack
    new_stack = {}
    for char in char_list[str_len]:
        p = 10000
        index = ''
        for key in stack:
            last_char = key[len(key) - 1]
            flag = True
            if last_char not in word_possibility:
                flag = False
            elif pinyin_list[str_len] not in word_possibility[last_char]:
                flag = False
            elif char not in word_possibility[last_char][pinyin_list[str_len]]:
                flag = False
            tmp_p = 0
            if flag:
                tmp_p = stack[key] + word_possibility[last_char][pinyin_list[str_len]][char]
            else:
                tmp_p = stack[key] + 15
            if str_len == (length - 1):
                tmp_p += 10
            if tmp_p < p:
                p = tmp_p
                index = key
        if not index == '':
            new_stack[index + char] = p
    this_stack = vertebi(pinyin_list, char_list, new_stack)
    return this_stack

#pinyin_list为待转换的拼音列表
def find(pinyin_list): 
    char_list = []
    for pinyin in pinyin_list:
        char_list.append(pinyin2char[pinyin])
    init_stack = {}
    for char in char_list[0]:
        init_stack[char] = 10
    final_stack = vertebi(pinyin_list, char_list, init_stack)
    #print(final_stack)
    ans = dict(sorted(final_stack.items(), key=lambda x: x[1]))       
    return list(ans.keys())[0]    

def process_input():
    while True:
        try:
            line = input().strip()
            if not line:
                break
            pinyin_list = line.split()
            result = find(pinyin_list)
            print(result)
        except EOFError:
            break
        
def main():
    process_input()
    

if __name__ == "__main__":
    main()