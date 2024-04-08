import json
import time
import sys

#读取处理好的文件
with open('./src/pinyin2char.json', 'r', encoding='utf-8') as f:
    pinyin2char = json.load(f)
with open('./src/char_possibility.json', 'r', encoding='utf-8') as f:
    char_possibility = json.load(f)
with open('./src/word_possibility.json', 'r', encoding='utf-8') as f:
    word_possibility = json.load(f)

lbd = 0.08

#维特比算法
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
                    tmp_p = stack[key] + (word_possibility[pinyins][chars] - 10) + lbd * char_possibility.get(pinyin_list[str_len], {}).get(char, 10)
                else: tmp_p = stack[key] + (word_possibility[pinyins][chars] - char_possibility[pinyin_list[str_len - 1]][last_char]) + lbd * char_possibility.get(pinyin_list[str_len], {}).get(char, 10)
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
    

def main(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    res = []
    for line in lines:
        pinyin_list = line.strip().split()
        result = find(pinyin_list)
        res.append(result)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(res))
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python pinyin.py input_file output_file")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    main(input_file, output_file)