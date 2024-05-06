import torch
import torch.nn as nn
import torch.nn.functional as F
from preprocess import word2id, word2vec
from sklearn.metrics import accuracy_score,f1_score
import numpy as np
from torch.utils.data import DataLoader
from data import MyDataset
import argparse
import time
import wandb


word2id_dict = word2id()
word2vec_dict = word2vec("./Dataset/wiki_word2vec_50.bin", word2id_dict) 

class MyConfig(object):
    embedding_dim = 50  # 词向量维度
    seq_length = 200  # 输入矩阵的宽度
    num_classes = 2  # 类别数
    num_filters = 20  # 卷积核数目
    kernel_size = [3, 4, 5]  # 卷积核尺寸，即卷积核覆盖的词汇数量
    vocab_size = len(word2id_dict) + 1  # 词汇表大小

    hidden_dim = 128  # 全连接层神经元

    dropout_keep_prob = 0.5  # dropout保留比例
    learning_rate = 1e-3  # 学习率

    batch_size = 32  # 每批训练大小
    num_epochs = 10  # 总迭代轮次
    
    pretrained_embed = word2vec_dict  # 预训练的词嵌入模型

    print_per_batch = 100  # 每多少轮输出一次结果
    save_per_batch = 10  # 每多少轮存入tensorboard

class MLP(nn.Module):
    def __init__(self, config):
        super(MLP, self).__init__()
        embedding_dim = config.embedding_dim
        seq_length = config.seq_length
        num_classes = config.num_classes
        num_filters = config.num_filters
        vocab_size = config.vocab_size
        kernel_size = config.kernel_size
        hidden_dim = config.hidden_dim
        dropout_keep_prob = config.dropout_keep_prob
        pretrained_embed = config.pretrained_embed
        
        self.__name__ = 'MLP'
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.embedding.weight.data.copy_(torch.from_numpy(pretrained_embed))
        self.ReLU = nn.ReLU()
        self.fc = nn.Linear(embedding_dim, hidden_dim)
        self.dropout = nn.Dropout(dropout_keep_prob)
        self.linear = nn.Linear(hidden_dim, num_classes)
        for n, p in self.named_parameters():
            if p.requires_grad:
                torch.nn.init.normal_(p, mean = 0, std = 0.01)

    def forward(self, sentence):
        sentence = self.embedding(sentence.to(torch.int64))
        sentence = self.fc(sentence)                                 
        sentence = self.ReLU(sentence).permute(0, 2, 1)
        sentence = self.dropout(sentence)            
        sentence = F.max_pool1d(sentence, sentence.size(2)).squeeze(2)
        pred = self.linear(sentence)
        return pred


class TextCNN(nn.Module):
    def __init__(self, config):
        super(TextCNN, self).__init__()
        embedding_dim = config.embedding_dim
        seq_length = config.seq_length
        num_classes = config.num_classes
        num_filters = config.num_filters
        vocab_size = config.vocab_size
        kernel_size = config.kernel_size
        hidden_dim = config.hidden_dim
        dropout_keep_prob = config.dropout_keep_prob
        pretrained_embed = config.pretrained_embed
        
        self.__name__ = 'TextCNN'
        #嵌入层
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.embedding.weight.data.copy_(torch.from_numpy(pretrained_embed)) #加载预训练词向量
        #卷积层
        self.convs = nn.ModuleList([nn.Conv2d(1, num_filters, (size, embedding_dim)) for size in kernel_size])
        #Dropout
        self.dropout = nn.Dropout(dropout_keep_prob)
        #全连接层
        self.fc = nn.Linear(len(kernel_size) * num_filters, num_classes)
    
    def forward(self, sentence):
        x = self.embedding(sentence.to(torch.int64)).unsqueeze(1)
        #x = sentence.unsqueeze(1) # (N, Ci, W, D)
        x = [F.relu(conv(x)).squeeze(3) for conv in self.convs] # [(N, Co, W), ...]*len(Ks)
        x = [F.max_pool1d(i, i.size(2)).squeeze(2) for i in x] # [(N, Co), ...]*len(Ks)
        x = torch.cat(x, 1)
        x = self.dropout(x) # (N, len(Ks)*Co)
        x = self.fc(x)  # (N, C)
        return x
    
    
class LSTM(nn.Module):
    def __init__(self, config):
        super(LSTM, self).__init__()
        embedding_dim = config.embedding_dim
        seq_length = config.seq_length
        num_classes = config.num_classes
        num_filters = config.num_filters
        vocab_size = config.vocab_size
        kernel_size = config.kernel_size
        hidden_dim = config.hidden_dim
        dropout_keep_prob = config.dropout_keep_prob
        pretrained_embed = config.pretrained_embed
        
        self.__name__ = 'LSTM'
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.embedding.weight.data.copy_(torch.from_numpy(pretrained_embed)) #加载预训练词向量
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers=num_classes, bidirectional=True, dropout=dropout_keep_prob)
        self.fc = nn.Linear(hidden_dim * 2, num_classes)
        self.dropout = nn.Dropout(dropout_keep_prob)
        
    def forward(self, sentence):
        #sentence = sentence.permute(1, 0, 2)
        sentence = self.embedding(sentence.to(torch.int64)).permute(1, 0, 2)
        output, (h_n, c_n) = self.lstm(sentence)
        h_n = torch.cat((h_n[-2, :, :], h_n[-1, :, :]), dim=1)
        h_n = self.dropout(h_n)
        pred = self.fc(h_n)
        return pred
        
    
def train_loop(dataloader, model, loss_fn, optimizer, device, batch_size):
    size = len(dataloader.dataset)
    # Set the model to training mode - important for batch normalization and dropout layers
    # Unnecessary in this situation but added for best practices
    model.train()
    train_loss, train_acc = 0.0, 0.0
    y_true = []
    y_pred = []
    for batch, (X, y) in enumerate(dataloader):
        X = X.to(device)
        y = y.to(device)
        # Compute prediction and loss
        pred = model(X)
        loss = loss_fn(pred, y)
        # Backpropagation
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        train_loss += loss.item()
        y_true.extend(y.cpu().numpy().tolist())
        y_pred.extend(pred.argmax(1).cpu().numpy().tolist())
    train_loss *= batch_size
    train_loss /= size
    f1 = f1_score(y_true, y_pred, average='binary')
    accuracy = accuracy_score(y_true, y_pred)
    print('Accuracy={}, F1Score={}, Train Loss={}'.format(accuracy, f1, train_loss))
    return train_loss, accuracy, f1


def test_loop(dataloader, model, loss_fn, device, batch_size):
    # Set the model to evaluation mode - important for batch normalization and dropout layers
    # Unnecessary in this situation but added for best practices
    model.eval()
    size = len(dataloader.dataset)
    num_batches = len(dataloader)
    test_loss, correct = 0, 0
    y_true = []
    y_pred = []
    # Evaluating the model with torch.no_grad() ensures that no gradients are computed during test mode
    # also serves to reduce unnecessary gradient computations and memory usage for tensors with requires_grad=True
    with torch.no_grad():
        for batch, (X, y) in enumerate(dataloader):
            X = X.to(device)
            y = y.to(device)
            pred = model(X)
            test_loss += loss_fn(pred, y).item()
            correct += (pred.argmax(1) == y).type(torch.float).sum().item()
            y_true.extend(y.cpu().numpy().tolist())
            y_pred.extend(pred.argmax(1).cpu().numpy().tolist())
    test_loss *= batch_size
    test_loss /= size
    f1 = f1_score(y_true, y_pred, average='binary')
    accuracy = accuracy_score(y_true, y_pred)
    print('Accuracy={}, F1Score={}, Test Loss={}'.format(accuracy, f1, test_loss))
    return test_loss, accuracy, f1
    

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # set device
train_dataset = MyDataset(np.load('./data/train_text.npy', allow_pickle=True), np.load('./data/train_label.npy', allow_pickle=True))
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
valid_dataset = MyDataset(np.load('./data/valid_text.npy', allow_pickle=True), np.load('./data/valid_label.npy', allow_pickle=True))
valid_loader = DataLoader(valid_dataset, batch_size=32, shuffle=True)
test_dataset = MyDataset(np.load('./data/test_text.npy', allow_pickle=True), np.load('./data/test_label.npy', allow_pickle=True))
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=True)  # DataLoader prepared

loss_fn = nn.CrossEntropyLoss().to(device)
config = MyConfig()

def set_parse():
    parser = argparse.ArgumentParser(description='Emotion Classification')
    parser.add_argument('-m', '--model', dest = 'model_name', type=str, default='MLP', help='choose model')
    parser.add_argument('-l', '--learning_rate', dest = 'learning_rate', type=float, default=0.001, help='learning rate')
    parser.add_argument('-e', '--epochs', dest = 'epochs', type=int, default=10, help='epochs')
    parser.add_argument('-b', '--batch_size', dest = 'batch_size', type=int, default=32, help='batch size')
    args = parser.parse_args()
    model_name = args.model_name
    learning_rate = args.learning_rate
    epochs = args.epochs
    batch_size = args.batch_size
    return model_name, learning_rate, epochs, batch_size

if __name__ == '__main__':
    wandb.init(
        # set the wandb project where this run will be logged
        project="Emotion Classification",
        config={
            "learning_rate": 0.001,
            "epochs": 10,
            "batch_size": 32
        }
    )
    model_name, learning_rate, epochs, batch_size = set_parse()
    if model_name == 'MLP':
        model = MLP(config).to(device)
    elif model_name == 'TextCNN':
        model = TextCNN(config).to(device)
    elif model_name == 'LSTM':
        model = LSTM(config).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    max_accuracy = -1
    
    all_train_beg = time.time()
    for i in range(epochs):
        print('Epoch {}/{}'.format(i+1, epochs))
        print('Begin Training..............')
        train_beg = time.time()
        train_loss, train_accuracy, train_f1 = train_loop(train_loader, model, loss_fn, optimizer, device, batch_size)
        train_end = time.time()
        print('Train Time: {:.2f}s'.format(train_end - train_beg))
        print('Begin Validating..............')
        valid_beg = time.time()
        valid_loss, valid_accuracy, valid_f1 = test_loop(valid_loader, model, loss_fn, device, batch_size)
        valid_end = time.time()
        print('Valid Time: {:.2f}s'.format(valid_end - valid_beg))
        print('Begin Testing..............')
        t_beg = time.time()
        test_loss, test_accuracy, test_f1 = test_loop(test_loader, model, loss_fn, device, batch_size)
        t_end = time.time()
        print('Test Time: {:.2f}s'.format(t_end - t_beg))
        #保存best model
        if valid_accuracy > max_accuracy:
            max_accuracy = valid_accuracy
            save_path = './model/' + model_name + '.pt'
            print('a better model')
            torch.save(model.state_dict(), save_path)
        #使用wandb可视化
        wandb.log({
            "train_loss": train_loss,
            "train_accuracy": train_accuracy,
            "train_f1": train_f1,
            "valid_loss": valid_loss,
            "valid_accuracy": valid_accuracy,
            "valid_f1": valid_f1,
            "test_loss": test_loss,
            "test_accuracy": test_accuracy,
            "test_f1": test_f1
        })
    all_train_end = time.time()
    print('All Train Time: {:.2f}s'.format(all_train_end - all_train_beg))
    
    print('Begin Best Model Testing..............')
    test_beg = time.time()
    best_model_path = './model/' + model_name + '.pt'
    model.load_state_dict(torch.load(best_model_path))
    test_loss, test_accuracy, test_f1 = test_loop(test_loader, model, loss_fn, device, batch_size)
    test_end = time.time()
    print('Best Model Test Time: {:.2f}s'.format(test_end - test_beg))