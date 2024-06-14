#include <iostream>
#include <unistd.h>
#include <math.h>
#include "Point.h"
#include "Strategy.h"
#include <stdio.h>
#include <stdlib.h>
#include "UCT.h"
#include <chrono>
#include <ctime>
using namespace std;

UCTNode uct[10000000];
int board_M, board_N, not_x, not_y, uct_length = 0;
int** cur_board;
int cur_top[12];
double c = 0.7;
/*
    策略函数接口,该函数被对抗平台调用,每次传入当前状态,要求输出你的落子点,该落子点必须是一个符合游戏规则的落子点,不然对抗平台会直接认为你的程序有误
    
    input:
        为了防止对对抗平台维护的数据造成更改，所有传入的参数均为const属性
        M, N : 棋盘大小 M - 行数 N - 列数 均从0开始计， 左上角为坐标原点，行用x标记，列用y标记
        top : 当前棋盘每一列列顶的实际位置. e.g. 第i列为空,则_top[i] == M, 第i列已满,则_top[i] == 0
        _board : 棋盘的一维数组表示, 为了方便使用，在该函数刚开始处，我们已经将其转化为了二维数组board
                你只需直接使用board即可，左上角为坐标原点，数组从[0][0]开始计(不是[1][1])
                board[x][y]表示第x行、第y列的点(从0开始计)
                board[x][y] == 0/1/2 分别对应(x,y)处 无落子/有用户的子/有程序的子,不可落子点处的值也为0
        lastX, lastY : 对方上一次落子的位置, 你可能不需要该参数，也可能需要的不仅仅是对方一步的
                落子位置，这时你可以在自己的程序中记录对方连续多步的落子位置，这完全取决于你自己的策略
        noX, noY : 棋盘上的不可落子点(注:涫嫡饫锔?龅膖op已经替你处理了不可落子点，也就是说如果某一步
                所落的子的上面恰是不可落子点，那么UI工程中的代码就已经将该列的top值又进行了一次减一操作，
                所以在你的代码中也可以根本不使用noX和noY这两个参数，完全认为top数组就是当前每列的顶部即可,
                当然如果你想使用lastX,lastY参数，有可能就要同时考虑noX和noY了)
        以上参数实际上包含了当前状态(M N _top _board)以及历史信息(lastX lastY),你要做的就是在这些信息下给出尽可能明智的落子点
    output:
        你的落子点Point
*/
extern "C" Point* getPoint(const int M, const int N, const int* top, const int* _board,
    const int lastX, const int lastY, const int noX, const int noY){
    /*
        不要更改这段代码
    */
    int x = -1, y = -1;//最终将你的落子点存到x,y中
    int** board = new int*[M];
    for(int i = 0; i < M; i++){
        board[i] = new int[N];
        for(int j = 0; j < N; j++){
            board[i][j] = _board[i * N + j];
        }
    }
    
    /*
        根据你自己的策略来返回落子点,也就是根据你的策略完成对x,y的赋值
        该部分对参数使用没有限制，为了方便实现，你可以定义自己新的类、.h文件、.cpp文件
    */
    //Add your own code below
    /*
     //a naive example
    for (int i = N-1; i >= 0; i--) {
        if (top[i] > 0) {
            x = top[i] - 1;
            y = i;
            break;
        }
    }
    */
    cur_board = new int*[M];
    for(int i = 0; i < M; i++) cur_board[i] = new int[N];
    board_M = M;
    board_N = N;
    not_x = noX;
    not_y = noY;
    //初始化根节点uct[0]
    uct[0].fa = -1;
    uct[0].side = true;
    uct[0].status = 2;
    uct[0].child[0] = -1; //左孩子
    auto start = std::chrono::steady_clock::now();
    srand(time(NULL));
    int im = 0; //模拟次数
    uct_length = 0;
    
    while((std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count() < 2.3) && im < 700000){
        im++;
        //更新棋盘状态
        for(int i = 0; i < M; ++i){ //M为行数，用x标记
            for(int j = 0; j < N; ++j)
                cur_board[i][j] = board[i][j];
        }
        for(int i = 0; i < N; ++i) cur_top[i] = top[i];

        // for(int i = 0; i< M; i++){ //M为行数，用x标记
		// 	for(int j = 0; j < N; j++){
		// 		// cout<<uuct.cur_board[i][j]<<endl;
		// 		cout<<board[i][j]<<endl;
		// 	}
		// }

        //从根节点开始遍历
        int node = 0;
        while((uct[node].child[0] >= 0) && (node >= 0)){
            node = treePolicy(node);
        }
        if(node == -1) break;
        
        
        //获取当前棋局的状态
        if(uct[node].visit == 0){
            uct[node].status = get_status(uct[node].location[0], uct[node].location[1], !uct[node].side);
        } 
        if(uct[node].status <= 1) {
            BackUp(node, uct[node].status);
            continue;
        }
        
        // for(int i = 0; i< M; i++){ //M为行数，用x标记
		// 	for(int j = 0; j < N; j++){
		// 		// cout<<uuct.cur_board[i][j]<<endl;
		// 		cout<<board[i][j]<<endl;
		// 	}
		// }
        
        //模拟
		//看棋盘中是否存在必胜节点，若存在，只扩展必胜节点，并回溯此次模拟结果
        int must_point = win_point(uct[node].side);
        if(must_point >= 0){
            uct[node].child[0] = ++uct_length;
            uct[node].child[1] = uct_length;
            uct[uct_length].location[0] = cur_top[must_point] - 1;
            uct[uct_length].location[1] = must_point;
            uct[uct_length].fa = node;
            uct[uct_length].side = !uct[node].side;
            uct[uct_length].child[0] = -1;
            uct[uct_length].visit = 0;
            uct[uct_length].score = 0;
            if (uct[node].side) uct[uct_length].status = 1;
            else uct[uct_length].status = -1;
            BackUp(uct_length, uct[uct_length].status);
            continue;
        }
        //看棋盘中是否存在迫手节点，若存在，只扩展迫手节点
        must_point = lost_point(uct[node].side);
        if(must_point >= 0){
            uct[node].child[0] = ++uct_length;
            uct[node].child[1] = uct_length;
            uct[uct_length].location[0] = cur_top[must_point] - 1;
            uct[uct_length].location[1] = must_point;
            uct[uct_length].fa = node;
            uct[uct_length].side = !uct[node].side;
            uct[uct_length].status = 2;
            uct[uct_length].child[0] = -1;
            uct[uct_length].visit = 0;
        }
        //否则，扩展全部可能的节点
        else Expand(node);
        
        //进行随机下棋模拟，并不扩展节点，模拟结束后回溯，从而进行下一次模拟
        int child = (rand() % (uct[node].child[1] - uct[node].child[0] + 1)) + uct[node].child[0], Bstatus;
        chess(uct[child].location[0], uct[child].location[1], uct[node].side);
        uct[child].status = get_status(uct[child].location[0], uct[child].location[1], uct[node].side);
        Bstatus = uct[child].status;
        bool Bside = uct[child].side;
        while(Bstatus == 2){
            int yy = rand() % board_N, xx;
            while (cur_top[yy] == 0) yy = rand() % board_N;
            xx = cur_top[yy] - 1;
            chess(xx, yy, Bside);
            Bstatus = get_status(xx, yy, Bside);
            Bside = !Bside;
        }
        BackUp(child, Bstatus);
    }
    
    int ans = 0;
    for(int i = 0; i < M; ++i){ //在模拟后更新棋盘状态
        for(int j = 0; j < N; ++j){
            cur_board[i][j] = board[i][j];
        }
    }
    for(int i = 0; i < board_N; ++i) cur_top[i] = top[i];
    ans = win_point(1); //优先选择必胜节点
    if(ans >= 0){
        x = top[ans] - 1;
        y = ans;
    }
    else{
        ans = lost_point(1); //其次是迫手节点
        if(ans >= 0){
            x = top[ans] - 1;
            y = ans;
        } 
        else{ //最后是胜率最高节点
            double best_score = -100000;
            double now_score;
            for (int i = uct[0].child[0]; i <= uct[0].child[1]; ++i) {
                now_score = ((double)(uct[i].score) / ((double)(uct[i].visit) + 0.0001));
                if (now_score > best_score){
                    best_score = now_score;
                    ans = i;
                }
            }
            x = uct[ans].location[0], y = uct[ans].location[1];
        }
    }
    
    clearArray(M, N, cur_board);
    /*
        不要更改这段代码
    */
    clearArray(M, N, board);
    return new Point(x, y);
}


/*
    getPoint函数返回的Point指针是在本dll模块中声明的，为避免产生堆错误，应在外部调用本dll中的
    函数来释放空间，而不应该在外部直接delete
*/
extern "C" void clearPoint(Point* p){
    delete p;
    return;
}

/*
    清除top和board数组
*/
void clearArray(int M, int N, int** board){
    for(int i = 0; i < M; i++){
        delete[] board[i];
    }
    delete[] board;
}


/*
    添加你自己的辅助函数，你可以声明自己的类、函数，添加新的.h .cpp文件来辅助实现你的想法
*/
