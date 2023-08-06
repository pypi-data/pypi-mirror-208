#定义函数Smith_Waterman（)
#生成打分矩阵score_matrix和方向矩阵direction_matrix
#ref为参考序列
#seq为比对序列
#match_score和mismatch_score表示组成序列的元素之间的相似性的得分
#w1是空位罚分
#0、1、2、3分别代表打分来自0、左上方、上方、左方
def Smith_Waterman(ref,seq,match_score,mismatch_score,w1):
    n=len(ref)
    m=len(seq)
#[0 for i in range(m+1)]是建立一个长度为m+1的全是0的列表
    score_matrix=[[0 for i in range(m+1)] for i in range(n+1)]
    direction_matrix=[[0 for i in range(m+1)] for i in range(n+1)]
    for i in range(1,n+1):
        for j in range(1,m+1):
            if ref[i-1]==seq[j-1]:
                s=match_score
            else:
                s=mismatch_score
            zero=0
            top_left=score_matrix[i-1][j-1]+s
            top=score_matrix[i-1][j]-w1
            left=score_matrix[i][j-1]-w1
            score=[zero,top_left,top,left]
            score_matrix[i][j]=max(score)
#每计算一个位置的得分，将该位置在score[]的索引写入方向矩阵对应的位置
            direction_matrix[i][j]=score.index(score_matrix[i][j])
    return score_matrix,direction_matrix


#求矩阵的最大值及其坐标
def maximum(score_matrix):
    max_coord=[]
    for i in range(0,len(score_matrix)):
        for j in range(0,len(score_matrix[i])):
#max()函数里面至少需要输入两个参数，一个参数的话必须是可迭代对象
#什么是可迭代对象，查了一些发现看不懂,反正int不可迭代，但list可迭代
#map()函数返回的一个'map'类型的序列，显然这里是可迭代的
#map()函数里面作用对象同样要求可迭代
            if score_matrix[i][j]==max(map(max,score_matrix)):
                max_coord.append((i,j))
    return max_coord


#回溯得到序列比对的结果
#max_coord为最大值的坐标之一
#direction_matrix为方向矩阵
#ref和seq为两条序列
def traceback(max_coord,direction_matrix,ref,seq):
    res_seq=[[[],[]]]
    i=max_coord[0]
    j=max_coord[1]
    while direction_matrix[i][j]>0:
        if direction_matrix[i][j]==1:
            res_seq[0][0].append(ref[i-1])
            res_seq[0][1].append(seq[j-1])
            i-=1
            j-=1
        elif direction_matrix[i][j]==2:
            res_seq[0][0].append(ref[i-1])
            res_seq[0][1].append("-")
            i-=1
        elif direction_matrix[i][j]==3:
            res_seq[0][0].append("-")
            res_seq[0][1].append(seq[j-1])
            j-=1
#reverse()函数对列表元素进行逆序排列
#"sep".join(seq),sep是分隔符，可以为空，seq是需要连接的元素序列
    res_seq[0][0].reverse()
    res_seq[0][1].reverse()
    res_seq[0][0]="".join(res_seq[0][0])
    res_seq[0][1]="".join(res_seq[0][1])
    return res_seq



