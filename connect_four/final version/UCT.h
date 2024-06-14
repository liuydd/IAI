#ifndef UCT_H_
#define UCT_H_

struct UCTNode {
    int score; //当前节点的得分。由本节点拓展的棋局AI胜利加一分，对手胜利扣一分，平局分数不变
    int visit; //当前节点被访问的次数
    bool side; //当前棋局轮到谁下棋，side==true: AI, side==false: user
    int status; //当前棋局的状态。-1: AI失败; 0: 平局; 1: AI胜利; 2: 未结束
    int fa; //当前节点的父节点
    int child[2]; //当前节点的子节点
    int location[2]; //当前节点在棋盘上的位置

    UCTNode(){
        score = 0;
        visit = 0;
        side = true;
        status = 2;
        fa = 0;
        child[0] = child[1] = 0;
        location[0] = location[1] = 0;
    }
};


int win_point(bool side);
int lost_point(bool side);

int treePolicy(int node);//用于在uct树中，决定下一个访问的子节点的函数
void chess(int x, int y, bool side);
int get_status(int x, int y, bool side);
void BackUp(int node, int delta);//node是节点编号，delta是节点得分
void Expand(int node);//拓展一个节点的子节点
double getScore(int child_score, int child_visit, int fa_visit, double c); //返回节点得分
#endif