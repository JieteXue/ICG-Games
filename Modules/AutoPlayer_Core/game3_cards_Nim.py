AUTHOR= 'Jiete Xue'
DATE= '2025/11/18'
VERSION= '1.0'


description='''n positions on a line. \n
There are initially several cards at each position on the line. \n
You can choose a position to take any cards at this position, if it is possible. \n
The player who can not move loses.'''


#------------------initial setting-------------------#
import random

def pre_words():
    print("We are going to start the game of taking cards.\n")
    n=input("Enter the number of positions to put cards (larger than 1, or enter directly for random setting): ")
    if n.isdigit(): 
        return int(n)

def random_list(n=-1):
    '''Generate a random list of cards.'''
    if n is None or type(n)!=int or n<=1:
        list=[random.randint(1,10) for i in range(random.randint(5,10))]
    else:
        list=[random.randint(1,10) for i in range(n)]
    return list

def initial_setting():
    return(random_list(pre_words()))




#------------------judge functions-------------------#
def judge_win(list):

    '''Check whether the given list is a winning list.'''

    F=0
    for i in range(len(list)):
        F^=list[i]
    if F==0:
        return False
    else:
        return True

def judge_move_local(list,i):

    '''Check whether the given action can be moved.'''
    '''i=[index in the list you choose, number of cards you choose]'''

    if list[i[0]]>=i[1] and i[1]>0:
        return True
    else:
        return False

def judge_move_global(list):

    '''Return a list of possible actions'''

    moving=[]
    for i in range(len(list)):
        for j in range(list[i]+1):
            if judge_move_local(list,[i,j]):
                moving.append([i,j])
    return moving
    

#------------------action functions-------------------#
def acted_list(list,i):
    list[i[0]]-=i[1]
    return list




#------------------Test-------------------#

if __name__ == "__main__":
    import ast
    lis=initial_setting()
    step=0
    while judge_move_global(lis)!=[]:
        step+=1
        print('------------------step {}-------------------'.format(step))
        print(lis)
        l=judge_move_global(lis)
        print(l)
        print(judge_win(lis))
        a=list_data = ast.literal_eval(input())
        print(type(a))
        if a in l:
            acted_list(lis,a)
        else:
            step-=1
            continue
    else:
        print('------------------Game is over-------------------')
        print(lis)