import json
import numpy as np
import math

def read_word2pinyin(file_path):
    word2pinyin = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            word, pinyin = line.strip().split()
            word2pinyin[word] = pinyin
    return word2pinyin

def read_unigram(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        unigram = json.load(f)
    return unigram

def read_bigram(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        bigram = json.load(f)
    return bigram

def viterbi(input_pinyin, word2pinyin, unigram, bigram):
    pinyin_list = list(word2pinyin.values())
    word_list = list(word2pinyin.keys())
    pinyin_word = {pinyin: sum(item['counts']) for pinyin, item in unigram.items()}
    total_count = sum(pinyin_word.values())
    initial_prob = {pinyin: math.log(total_count) - math.log(count) for pinyin, count in pinyin_word.items()}
    
    N = len(input_pinyin)
    delta = np.zeros((N, len(pinyin_list)))
    path = np.zeros((N, len(pinyin_list)), dtype=int)
    
    for idx, pinyin in enumerate(pinyin_list):
        if input_pinyin[0] in word2pinyin.values():
            if pinyin == input_pinyin[0]:
                delta[0][idx] = initial_prob[pinyin]
        else:
            delta[0][idx] = initial_prob[pinyin]
    
    for t in range(1, N):
        for j, pinyin in enumerate(pinyin_list):
            min_prob = 1
            best_pinyin = None
            for i, prev_pinyin in enumerate(pinyin_list):
                if f"{prev_pinyin} {pinyin}" in bigram:
                    prev_count = sum(unigram[prev_pinyin]["counts"])
                    bigram_count = sum(bigram[f"{prev_pinyin} {pinyin}"]["counts"])
                    if delta[t - 1][i] >0: t1 = math.log(delta[t - 1][i])
                    else: t1 = 0
                    if bigram_count > 0: t2 = math.log(bigram_count)
                    else: t2 = 0
                    if prev_count > 0: t3 = math.log(prev_count)
                    else: t3 = 0
                    prob = -t1 - t2 + t3
                    if prob < min_prob:
                        min_prob = prob
                        best_pinyin = i
            if input_pinyin[t] in word2pinyin.values():
                if pinyin == input_pinyin[t]:
                    delta[t][j] = min_prob
                    path[t][j] = best_pinyin
            else:
                delta[t][j] = min_prob
                path[t][j] = best_pinyin
    
    best_path_end = np.argmax(delta[N - 1])
    best_path = [best_path_end]
    
    for t in range(N - 2, -1, -1):
        prev_best_pinyin = path[t + 1][best_path[0]]
        best_path.insert(0, prev_best_pinyin)
    
    result = [word_list[pinyin] for pinyin in best_path]
    
    return result

def process_input(word2pinyin, unigram, bigram):
    while True:
        try:
            line = input().strip()
            if not line:
                break
            pinyin_list = line.split()
            result = viterbi(pinyin_list, word2pinyin, unigram, bigram)
            print(''.join(result))
        except EOFError:
            break

def main():
    word2pinyin = read_word2pinyin('./word2pinyin.txt')
    unigram = read_unigram('./1_word.txt')
    bigram = read_bigram('./2_word.txt')
    process_input(word2pinyin, unigram, bigram)
    

if __name__ == "__main__":
    main()


