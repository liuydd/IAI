#include <unistd.h>

#include <cmath>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <iostream>

#include "Judge.h"
#include "Point.h"
using namespace std;
#pragma once




class Node{
    int position_x=-1,position_y=-1;//落子位置
    int height,width;
    int owner;//当前玩家
    bool expanded;//是否已经拓展
    int expandednum=0;//可拓展节点数
    int visit=0;//总访问次数
    int ban_x,ban_y;
    double profit=0.0;

    public:
    int get_position_x(){return position_x;}
    int get_position_y(){return position_y;}
    int get_owner(){return owner;}
    int& get_visit(){return visit;}
    int& get_expandednum(){return expandednum;}
    int get_height(){return height;}
    int get_width(){return width;}
    bool get_expanded(){return expanded;}
    int get_ban_x(){return ban_x;}
    int get_ban_y(){return ban_y;}
    double& get_profit(){return profit;}
    int** board;  // 当前局面状况
    int* top;     // 当前每一列顶部状况

    int* expandable_nodes=NULL;//可拓展节点的列序号数组
    Node* parent{NULL};  // 父节点
    Node** children;     // 子节点
    Node(int **board,int *top,int height,int width,int ban_x,int ban_y,int position_x=-1,int position_y=-1,int owner=2,Node* parent=NULL):
        position_x(position_x),position_y(position_y),height(height),width(width),owner(owner),expanded(false),expandednum(0),visit(0),
        ban_x(ban_x),ban_y(ban_y),parent(parent)
    {
        children=new Node*[width];
        for(int i=0;i<width;i++)
            children[i]=NULL;
        this->top = new int[width];
        for (int i = 0; i < width; ++i) {
            this->top[i] = top[i];
        }
        this->board = new int*[height];
        for (int i = 0; i < height; ++i) {
            this->board[i] = new int[width];
            for (int j = 0; j < width; ++j) {
                this->board[i][j] = board[i][j];
            }
        }
        expandable_nodes=new int[width];
        for(int i=0;i<width;i++){
            if(top[i]>0){
                expandable_nodes[expandednum]=i;
                expandednum++;
            }
    }
    }
    ~Node()
    {   
        for (int i = 0; i < width; ++i)
            if (children[i]) delete children[i];
        delete[] children;
        delete[] top;
        for(int i=0;i<height;i++)
            delete[] board[i];
        delete[] board;
        delete[] expandable_nodes;
    }
    
    


       
    
};

