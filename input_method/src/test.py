import json

gen_sentence = []
with open('./data/output.txt', 'r', encoding='utf-8') as f:
    for line in f:
        gen_sentence.append(line.strip())

std_sentence = []
with open('./data/std_output.txt', 'r', encoding='utf-8') as f:
    for line in f:
        std_sentence.append(line.strip())

#计算两个字符串中不一样的字符数
def count_different_characters(str1, str2):
    count = 0
    min_len = min(len(str1), len(str2))
    for i in range(min_len):
        if str1[i] != str2[i]:
            count += 1
    count += abs(len(str1) - len(str2))   
    return count

sen_count = 0
right_sentence = []
wrong_sentence = []
sample_sentence = []
part_count = 0
for i in range(len(gen_sentence)):
    if gen_sentence[i] == std_sentence[i]:
        sen_count += 1
        right_sentence.append(gen_sentence[i])
    else:
        s = count_different_characters(gen_sentence[i], std_sentence[i])
        if s>=4: part_count += 1
        wrong_sentence.append(gen_sentence[i])
        sample_sentence.append(std_sentence[i])
sentence_acc = sen_count / len(gen_sentence)
# with open('./data/right_sentence.txt', 'w', encoding='utf-8') as f:
#     for i in range(len(right_sentence)):
#         f.write(right_sentence[i] + '\n')
# with open('./data/wrong_sentence.txt', 'w', encoding='utf-8') as f:
#     for i in range(len(wrong_sentence)):
#         f.write(wrong_sentence[i] + '\n')
#         f.write(sample_sentence[i] + '\n')
print("句子总数:", len(gen_sentence))
print("正确句子数:", sen_count)
print('sentence accuracy:', sentence_acc)
print("错别字大于等于4的句子数:", part_count)

char_count = 0
total_char_count = 0
for i in range(len(gen_sentence)):
    total_char_count += len(gen_sentence[i])
    for j in range(len(gen_sentence[i])):
        if gen_sentence[i][j] == std_sentence[i][j]:
            char_count += 1
char_acc = char_count / total_char_count
print("字总数:", total_char_count)
print("正确字数:", char_count)
print('character accuracy:', char_acc)