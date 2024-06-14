#include "UCT.h"
#include "Judge.h"
#include<iostream>
#include<cmath>
#include<cstring>
using namespace std;

UCT::UCT(){
    c = 0;
    board_M = board_N = not_x = not_y = uct_length = 0;
    for(int i = 0; i < 12; i++) cur_top[i] = 0;
}

int UCT::win_point(bool side){ //必胜节点
    int ans = -1;
    for(int i = 0; i < board_N; i++){ //遍历每一列
        if(cur_top[i]){
            cur_board[cur_top[i] - 1][i] = side + 1;
            if(side && machineWin(cur_top[i] - 1, i, board_M, board_N, cur_board)) ans = i;
            if((!side) && userWin(cur_top[i] - 1, i, board_M, board_N, cur_board)) ans = i;
            cur_board[cur_top[i] - 1][i] = 0;
            if(ans >= 0) break;
        }
    }
    return ans;
}

int UCT::lose_point(bool side){ //迫手节点
    int ans = -1;
    for(int i = 0; i < board_N; i++){
        if(cur_top[i]){
            cur_board[cur_top[i] - 1][i] = 2 - side;
            if(side && userWin(cur_top[i] - 1, i, board_M, board_N, cur_board)) ans = i;
            if((!side) && machineWin(cur_top[i] - 1, i, board_M, board_N, cur_board)) ans = i;
            cur_board[cur_top[i] - 1][i] = 0;
            if(ans >= 0) break;
        }
    }
    return ans;
}

bool UCT::BeBlock(bool side, int y){ //判断该节点是否是下一个被堵死的落子点
    if(cur_top[y] < 2) return false;
    bool ans = false;
    cur_board[cur_top[y] - 2][y] = side + 1;
    if(side && machineWin(cur_top[y] - 2, y, board_M, board_N, cur_board)) ans = true;
    if((!side) && userWin(cur_top[y] - 2, y, board_M, board_N, cur_board)) ans = true;
    cur_board[cur_top[y] - 2][y] = 0;
    return ans;
}

bool UCT::WillLose(bool side, int y){ //判断该节点是否是下一个会输的落子点
    if(cur_top[y] < 2) return false;
    bool ans = false;
    cur_board[cur_top[y] - 2][y] = (!side) + 1;
    if(side && userWin(cur_top[y] - 2, y, board_M, board_N, cur_board)) ans = true;
    if((!side) && machineWin(cur_top[y] - 2, y, board_M, board_N, cur_board)) ans = true;
    cur_board[cur_top[y] - 2][y] = 0;
    return ans;
}

int UCT::treePolicy(int node){
    int next_node = node;
    double max = -1000000;
    double poss;
    for(int child = uct[node].child[0]; child <= uct[node].child[1]; child++){
        if(uct[node].side){
            poss = getScore(uct[child].score, uct[child].visit, uct[node].visit);
        }
        else{
            poss = getScore(-uct[child].score, uct[child].visit, uct[node].visit);
        }
        if(poss > max){
            max = poss;
            next_node = child;
        }
    }
    chess(uct[next_node].location[0], uct[next_node].location[1], uct[node].side);
    return next_node;
}


void UCT::chess(int x, int y, bool side){ //落子，改变(x, y)处的棋盘值与状态
    cur_board[x][y] = side + 1;
    cur_top[y]--;
    if ((x == (not_x + 1)) && (y == not_y)) cur_top[y]--; //如果某一步所落的子的上面恰是不可落子点, top--
}

int UCT::get_status(int x, int y, bool side){ //side方在(x, y)处落子后棋局状态
    // int ans = 2;
    if((!side) && userWin(x, y, board_M, board_N, cur_board)) return -1;
    if(side && machineWin(x, y, board_M, board_N, cur_board)) return 1;
    if(isTie(board_N, cur_top)) return 0;
    return 2;
}

void UCT::BackUp(int node, int delta){ //回溯，delta为节点得分
    while(node > 0){
        uct[node].visit++;
        uct[node].score += delta;
        node = uct[node].fa;
    }
    uct[0].visit++;
}

void UCT::Expand(int node){ //节点扩展
    uct[node].child[0] = uct_length + 1;
    for(int i = 0; i < board_N; i++){
        if(cur_top[i] == 0) continue;
        uct[++uct_length].child[0] = -1, uct[uct_length].fa = node;
        uct[uct_length].location[0] = cur_top[i] - 1;
        uct[uct_length].location[1] = i;
        uct[uct_length].score = uct[uct_length].visit = 0;
        uct[uct_length].status = 2;
        uct[uct_length].side = !uct[node].side;
    }
    uct[node].child[1] = uct_length;
}

double UCT::getScore(int child_score, int child_visit, int fa_visit){ //返回节点得分
    double X = (double)(child_score) / ((double)(child_visit) + 0.0001); //防止visit为0
    double Y = c * sqrt(2 * log((double)(fa_visit) + 1.01) / ((double)(child_visit) + 0.0001));
    double ans = X + Y;
    return ans;
}