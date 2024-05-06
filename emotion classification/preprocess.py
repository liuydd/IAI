import numpy as np
import os
from collections import Counter
import gensim
import json
from tensorflow import keras

#给train.txt和validation.txt中的词一个id
#word2id_dict = {word: id, ...}, id从0开始
def word2id():
    files = os.listdir('./Dataset')
    file_paths = []
    for file_name in files:
        if file_name.endswith('.txt'):
            file_paths.append('./Dataset/'+file_name)
    word2id_dict = Counter()
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                sentence = line.strip().split()
                for word in sentence[1:]:
                    if word not in word2id_dict.keys():
                        word2id_dict[word] = len(word2id_dict)
    # with open('word2id.json', 'w', encoding='utf-8') as fp:
    #     json.dump(word2id_dict, fp, ensure_ascii=2)
    return word2id_dict

#将train.txt和validation.txt中的词转换为词向量
#word2vec_dict = {id: vector}
def word2vec(file_path, word2id_dict):
    preModel = gensim.models.KeyedVectors.load_word2vec_format(file_path, binary=True)
    word2vec_dict = np.zeros([len(word2id_dict) + 1, preModel.vector_size])
    for word in word2id_dict:
        if word in preModel:
            word2vec_dict[word2id_dict[word]] = preModel[word]
    # with open('word2vec.json', 'w', encoding='utf-8') as fp:
    #     json.dump(word2vec_dict.tolist(), fp, ensure_ascii=2)
    return word2vec_dict

word2id_dict = word2id()
#print(len(word2id_dict)) #59289
word2vec_dict = word2vec("./Dataset/wiki_word2vec_50.bin", word2id_dict)      

#将数据集从文字转换为固定长度的id序列表示
def process_file(file_path, word2id_dict, max_length = 50):
    contents, labels = np.array([0] * max_length), np.array([])
    with open(file_path, encoding="utf-8", errors="ignore") as f:
        for line in f.readlines():
            sentence = line.strip().split()
            content = np.asarray([word2id_dict.get(w, 0) for w in sentence[1:]])[:max_length]
            padding = max(max_length - len(content), 0)
            content = np.pad(content, ((0, padding)), "constant", constant_values=0)
            labels = np.append(labels, int(sentence[0]))
            contents = np.vstack([contents, content])
    contents = np.delete(contents, 0, axis=0)
    return contents, labels

train_contents, train_labels = process_file("./Dataset/train.txt", word2id_dict)
valid_contents, valid_labels = process_file("./Dataset/validation.txt", word2id_dict)
test_contents, test_labels = process_file("./Dataset/test.txt", word2id_dict)

np.save("./data/train_text.npy", train_contents)
np.save("./data/train_label.npy", train_labels)
np.save("./data/valid_text.npy", valid_contents)
np.save("./data/valid_label.npy", valid_labels)
np.save("./data/test_text.npy", test_contents)
np.save("./data/test_label.npy", test_labels)