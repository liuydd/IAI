# 程序结构
- ./data：存放预训练得到的词向量
- ./Dataset：存放原始数据
- ./model：存放训练好的、在验证集上准确率最高的最优模型
- ./wandb：已经完成的模型训练结果
- ./data.py：Dataset类
- ./preprocess.py：数据预处理
- ./main.py：模型架构与训练评测
- ./ReadMe.md：说明文档

# 程序运行方式
- python preprocess.py：将所有训练数据转化成词向量组成的句子，统一句子长度，以.npy文件的形式存在./data文件夹中，在训练模型的时候可以直接使用
- python main.py：训练模型
  - -m/--model：更改想要训练的模型，默认训练MLP模型，可选择的参数有MLP、TextCNN、LSTM
  - -l/--learning_rate：更改学习率，默认为0.001
  - -e/--epochs：更改训练轮次，默认为10
  - -b/--batch_size：更改训练批次大小，默认为32