# 拼音输入法
本文档简单描述了文件结构和运行方式，详细分析见[PDF](https://cloud.tsinghua.edu.cn/f/f776d2daff39468ca3f8/)

## 文件说明
```
├── README.md
├── data
│   ├── std_input.txt
│   └── std_output.txt
├── src
│    ├── preprocess.py
│    ├── pinyin.py
│    ├── pinyin_triple.py
│    └── test.py
├── training_data
│   ├── 拼音汉字表.txt
│   └── 一二级汉字表.txt
└── 语料库
    └── sina_news_gbk
        ├── 2016-04.txt
        ├── 2016-05.txt
        ├── 2016-06.txt
        ├── 2016-07.txt
        ├── 2016-08.txt
        ├── 2016-09.txt
        ├── 2016-10.txt
        └── 2016-11.txt
```
请按照上述文件结构放置训练材料和语料库材料。
./data/std_input.txt和./data/std_output.txt为标准输入输出，./data/output.txt为在标准输入的基础上使用字的二元模型得到的输出，./data/output_triple.txt为在标准输入的基础上使用字的三元模型得到的输出。
./src/preprocess.py为数据预处理文件，./src/pinyin.py和./src/pinyin_triple.py分别为基于字的二元和三元模型的拼音输入法，./src/test.py为测试输出的文件。

注：由于预处理语料库的时间可能较长，你也可以通过[此链接](https://cloud.tsinghua.edu.cn/d/bd6e8a0bf0604478a452/)下载预处理后得到的文件。

## 程序运行方式
在根目录下运行：
`python ./src/preprocess.py`: 数据预处理
`python ./src/pinyin.py <input_file> <output_file>`: 基于字的二元模型训练，得到输出结果
`python ./src/pinyin_triple.py <input_file> <output_file>`: 基于字的三元模型训练，得到输出结果
`python ./src/test.py`: 输出结果测试