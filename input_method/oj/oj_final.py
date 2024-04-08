"""
37.2!!!
2024.4.1 0:07 想哭
做实验二的测试时发现句准确率和字准确率高得离谱, 不理解为什么oj上的那么低。于是将oj代码根据实验二的情况修改了处理了特殊情况, 然后分数就提高到37.2了呜呜呜
应该是初始化错了, 还是应该大部分初始化为单字的概率, 而不是10
"""
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
one_word_count = {}
for pinyin in unigram:
    if pinyin not in one_word_count:
        one_word_count[pinyin] = 0
    one_word_count[pinyin] += sum(unigram[pinyin]['counts'])
char_possibility = {}
for pinyin in unigram:
    if pinyin not in char_possibility:
        char_possibility[pinyin] = {}
    cp = {}
    for i in range(len(unigram[pinyin]['words'])):
        word = unigram[pinyin]['words'][i]
        count = unigram[pinyin]['counts'][i]
        poss = math.log(one_word_count[pinyin]) - math.log(count)
        cp[word] = poss
    char_possibility[pinyin] = cp
    
#得到双字的概率, bigram_possibility = {'pinyin1_pinyin2': {'词语1': 概率1, '词语2': 词语2, ...}, ...}
with open('./2_word.txt', 'r', encoding='utf-8') as f:
    bigram = json.load(f)
two_word_count = {}
for pinyins in bigram:
    if pinyins not in two_word_count:
        two_word_count[pinyins] = 0
    two_word_count[pinyins] += sum(bigram[pinyins]['counts'])
word_possibility = {}
for pinyin2 in bigram:
    if pinyin2 not in word_possibility:
        word_possibility[pinyin2] = {}
    word_list = bigram[pinyin2]['words']
    count_list = bigram[pinyin2]['counts']
    for i in range(len(word_list)):
        #if count_list[i] < 10: continue
        word_possibility[pinyin2][word_list[i]] = math.log(two_word_count[pinyin2]) - math.log(count_list[i])
        #word_possibility[pinyin2][word_list[i]] = count_list[i] / two_word_count

# with open('./cleaned_1_word.txt', 'r', encoding='utf-8') as f:
#     char_possibility = json.load(f)
# with open('./cleaned_2_word.txt', 'r', encoding='utf-8') as f:
#     word_possibility = json.load(f)
        
def vertebi(pinyin_list, char_list, stack):
    length = len(pinyin_list)
    str_len = 0 #目前计算到的字符串长度
    for key in stack:
        str_len = len(key)
        break
    if str_len == length:
        return stack
    pinyins = ' '.join(pinyin_list[str_len-1 : str_len+1])
    new_stack = {}
    for char in char_list[str_len]:
        p = 10000
        index = ''
        for key in stack:
            last_char = key[len(key) - 1]
            chars = last_char + ' ' + char
            flag = True
            if pinyins not in word_possibility:
                flag = False
            elif chars not in word_possibility[pinyins]:
                flag = False
            tmp_p = 0
            if flag:
                if last_char not in char_possibility[pinyin_list[str_len - 1]]:
                    tmp_p = stack[key] + word_possibility[pinyins][chars] - 10
                else: tmp_p = stack[key] + word_possibility[pinyins][chars] - char_possibility[pinyin_list[str_len - 1]][last_char]
            else:
                tmp_p = stack[key] + 17
            if str_len == (length - 1):
                tmp_p += 17
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
        if char not in char_possibility[pinyin_list[0]]: continue
        init_stack[char] = char_possibility[pinyin_list[0]][char]
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
