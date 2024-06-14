#include <unistd.h>

#include <cmath>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <iostream>

#include "Judge.h"
#include "Point.h"
#include "Node.h"
using namespace std;
#pragma once

#define VERY_LARGE_NUMBER 10000000

//const double timelimit{1.7000 * CLOCKS_PER_SEC};
const double timelimit=2.2*CLOCKS_PER_SEC;

clock_t startTime;

class UCT{
    int width,height;
    Node* root;
    int ban_x,ban_y;//去掉的点的位置
    bool expanded=true;//是否已经被拓展

    //要写的函数
    //search  treepolicy expand  bestchild defaultpolicy  backup
    public:
    const Node* get_root() const { return root; }
    const int get_width() { return width; }
    const int get_height() { return height; }
    const int get_ban_x() { return ban_x; }
    const int get_ban_y() { return ban_y; }
    bool get_expanded() { return expanded; }
    //int* weight=NULL;
    //int full_weight=0;

    UCT(int width, int height, int ban_x, int ban_y, int** board, const int* top,
      bool expanded = true): width(width), height(height), ban_x(ban_x), ban_y(ban_y) {
        this->expanded = expanded;
        int *root_top=new int[width];
        for(int i=0;i<width;i++){
            root_top[i]=top[i];
        }
        root = new Node(board, root_top,this->get_height(),this->get_width(),this->get_ban_x(),this->get_ban_y());
        delete[] root_top;
    }

    ~UCT() { delete this->root; }

    Node* Search(){
        startTime=clock();
        //int top_id=root->must(root->get_owner());
        // if(top_id!=-1){
        //     int x=root->top[top_id]-1;
        //     root_board[x][]
        // }
        // if(top_id!=-1){
        //     int x=root->top[top_id]-1;
        //     root->top[top_id]--;
        //     root->board[x][top_id]=root->get_owner();
        //     if(root->get_ban_x()==x-1&&root->get_ban_y()==top_id)  root->top[top_id]--;
            
        //     int next_owner;
        //     if(root->get_owner()==1)  next_owner=2;
        //     else  next_owner=1;
        //     return root->children[top_id] =
        //          new Node(root->board, root->top,root->get_height(), root->get_width(),root->get_ban_x(), root->get_ban_y(),x,top_id,next_owner,root);

        // }
        
           //std::cerr<<"error"<<std::endl;
            int count=0;
            //std::cerr<<"1"<<std::endl;
            while (++count) {
                // if (count % 5000 == 0)
                //     std::cerr<<count<<endl;
                //std::cerr<<clock<<endl;
                if (double(clock() - startTime )> timelimit) break;
                //std::cerr<<"begin"<<clock()- startTime<<std::endl;
                Node* next_node = treePolicy(root);
                //std::cerr<<"treepolicy"<<clock()- startTime<<std::endl;
                //std::cerr<<"3"<<std::endl;
                // if(next_node)  //std::cerr<<"yes"<<std::endl;
                double profit = defaultPolicy(next_node);
                //std::cerr<<"defaultpolicy"<<clock()- startTime<<std::endl;
                //std::cerr<<"4"<<std::endl;
                backup(next_node, profit);
                //std::cerr<<"5"<<std::endl;
                //std::cerr<<"backup"<<clock()- startTime<<std::endl;
              
            }
            std::cerr<<"count"<<count<<endl;
           //打印第一代孩子的所有value
           for(int i=0;i<width;i++){
            std::cerr<<root->children[i]->get_profit()<<endl;
           }
           //std::cerr<<"6"<<std::endl;
           return bestChild(root);
        }

    void backup(Node* node, double profit) {
        while (node) {
            if(profit==node->get_owner()) node->get_profit()-=1;
            else if(profit!=0) node->get_profit()+=1;
            // node->get_profit() += profit;
            node->get_visit()++;
           // profit=-profit;
            node = node->parent;
        }
    }

    

    Node* bestChild(Node* node) {
        Node* bestChild = NULL;
        int index;
        double bestValue = -30000000.0;
        for (int i = 0; i < node->get_width(); ++i) {

            if(node->children[i]){
                //这里c的值要调参，暂时取0.7试试
                //std::cerr<<"yes"<<i<<endl;
                // int id;
                // if(node->get_owner()==1)  id=1;
                // else  id=-1;
                double value = double(node->children[i]->get_profit()) / node->children[i]->get_visit() +
                    0.7*sqrt(2 * log(double(node->get_visit())) / double(node->children[i]->get_visit()));
                    //std::cerr<<"value:"<<value<<std::endl;
                if (value > bestValue) {
                    bestValue = value;
                    bestChild = node->children[i];
                }
            }
            //if(!bestChild)  std::cerr<<"no"<<std::endl;
        }
        //std::cerr<<"bestchild"<<endl;
        
        return bestChild;    
    }

    Node* treePolicy(Node* node){
        // if (node)
            //std::cerr << "isnot null" << std::endl;
        bool terminate=false;
        //std::cerr<<"1"<<std::endl;
       
        while(true){
           
            //std::cerr<<count<<std::endl;
            // if (NULL == node) //std::cerr << "isnull" << std::endl;
            if (!node->parent) {
                terminate = false;
                //std::cerr << "!node->parent" << std::endl;
            }
            else if(((node->get_owner()==1) &&machineWin(node->get_position_x(), node->get_position_y(),
                           node->get_height(), node->get_width(),node->board))) {
                    terminate=true;
                    //std::cerr << "machineWin" << std::endl;
            }
            else if(((node->get_owner()==2) &&userWin(node->get_position_x(), node->get_position_y(),
                           node->get_height(), node->get_width(),node->board))) {
                    terminate=true;
                    //std::cerr << "userWin" << std::endl;
                           }
            else if(isTie(node->get_width(), node->top)) {
                terminate=true;
                //std::cerr << "isTie" << std::endl;
            }
            if(terminate)  break;
            //std::cerr << "didn't terminate" << std::endl;
            if(node->get_expandednum() > 0){
                //std::cerr<<"expand"<<endl;
                return expand(node);
            }
            else{
                //std::cerr<<"best1"<<endl;
                node =bestChild(node);
                //std::cerr<<"best"<<endl;
            }
             
        }
        //std::cerr<<"yes"<<endl;
        return node;

    }

    Node* expand(Node* node) {
        int index=rand()%(node->get_expandednum());
        int** new_board=new int*[node->get_height()];
        for(int i=0;i<node->get_height();i++){
            new_board[i]=new int[node->get_width()];
            for(int j=0;j<node->get_width();j++){
                new_board[i][j]=node->board[i][j];
            }
        }
        int* new_top=new int[node->get_width()];
        for(int i=0;i<node->get_width();i++){
            new_top[i]=node->top[i];
        }
        int y=node->expandable_nodes[index];
        int x=--(new_top[y]);
        int next_owner;
        if(node->get_owner()==1)  next_owner=2;
        else  next_owner=1;
        //new_board[x][y]=next_owner;
        new_board[x][y]=node->get_owner();
        if(node->get_ban_x()==x-1&&node->get_ban_y()==y)  new_top[y]--;
        
        node->children[y] =
                 new Node(new_board, new_top,node->get_height(), node->get_width(), node->get_ban_x(), node->get_ban_y(),x,y,next_owner,node);
        delete[] new_top;
        for (int i = 0; i < this->get_height(); ++i) {
        delete[] new_board[i];
        }
        delete[] new_board;
        std::swap(node->expandable_nodes[index],
              node->expandable_nodes[--(node->get_expandednum())]);
        return node->children[y];
    }

    double defaultPolicy(Node* node) {
        double profit=0.0;bool terminate=false;
        //std::cerr<<"_0"<<std::endl;
        int** new_board=new int*[height];
            for(int i=0;i<height;i++){
                new_board[i]=new int[width];
                for(int j=0;j<width;j++){
                    new_board[i][j]=node->board[i][j];
                }
            }
            //std::cerr<<"_1"<<std::endl;
        int* new_top=new int[width];
        for(int i=0;i<width;i++){
            new_top[i]=node->top[i];
        }
        //std::cerr<<"_2"<<std::endl;    
        if(((node->get_owner()==1) &&machineWin(node->get_position_x(), node->get_position_y(),
                        node->get_height(), node->get_width(),new_board))){
                        //std::cerr<<"_3"<<std::endl;
                profit=(double)(2);terminate=true;
                        }
        
        else if(((node->get_owner()==2) &&userWin(node->get_position_x(), node->get_position_y(),
                                    node->get_height(), node->get_width(),new_board))){
                                    //std::cerr<<"_4"<<std::endl;
                profit=(double)(1);terminate=true;
                }
        else if(isTie(node->get_width(), new_top)) {profit=(double)(0);terminate=true;}
        //std::cerr<<"1_"<<std::endl;
        int next_owner=node->get_owner();
        while(!terminate){
            next_owner = 3 - next_owner;
            // int index=rand()%(node->get_expandednum());
            // int y=node->expandable_nodes[index];
            int y=rand()%width;
            while(new_top[y]==0) y=rand()%width;
            int x=--(new_top[y]);
            new_board[x][y]=3-next_owner;
            if(node->get_ban_x()==x-1&&node->get_ban_y()==y)  new_top[y]--;
            
            //std::cerr<<"2_"<<std::endl;
            if(next_owner==1&&machineWin(x,y,node->get_height(),node->get_width(),new_board)){
                //std::cerr<<"3_"<<std::endl;
                profit=(double)(2);
                terminate=true;
            }
            else if(next_owner==2&&userWin(x,y,node->get_height(),node->get_width(),new_board)){
                //std::cerr<<"4_"<<std::endl;
                profit=(double)(1);
                terminate=true;
            }
            else if(isTie(node->get_width(), new_top)) {
                //std::cerr<<"5_"<<std::endl;
                profit=(double)(0);
                terminate=true;

            }
            else{
                //std::cerr<<"6_"<<std::endl;
                terminate=false;
            }
        }
        delete[] new_top;
        for(int i=0;i<height;i++)  delete[] new_board[i];
        delete[] new_board;
        //std::cerr<<"7_"<<std::endl;
        return profit;
    }
            
};




        
    







