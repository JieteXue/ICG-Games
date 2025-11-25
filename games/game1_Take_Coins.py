AUTHOR= 'Jiete Xue'
TESTER= 'Jiahao Liu'
DATE= '2025/11/11'
VERSION= '1.1'







description='''n positions on a line. \n
There are initially several coins at each position on the line. \n
You can choose a position to add a coin, and remove a coin from each side of its neighboring position, if it is possible. \n
The player who can not move loses.'''






#------------------initial setting-------------------#
import random
import copy

def pre_words():
    print("We are going to start the game of taking coins.")
    print("")
    n=input("Enter the number of positions to put coins (larger than 8, or enter directly for random setting): ")
    if n.isdigit(): 
        return int(n)

def random_list(n=-1):
    '''Generate a random list of coins.'''
    if n is None or type(n)!=int or n<=2:
        list=[random.randint(1,3) for i in range(random.randint(8,14))]
    else:
        list=[random.randint(1,3) for i in range(n)]
    return list

def initial_setting():
    return(random_list(pre_words()))




#------------------judge functions-------------------#
from functools import lru_cache
'''O(2^n), only for short lists'''
@lru_cache(maxsize=None)
def _judge_win_internal(state):
    """Internal function, accept tuple"""
    n = len(state)
    

    has_legal_move = False
    for i in range(1, n - 1):
        if state[i - 1] >= 1 and state[i + 1] >= 1:
            has_legal_move = True
            new_state = list(state)
            new_state[i - 1] -= 1
            new_state[i] += 1
            new_state[i + 1] -= 1
            

            if new_state[i - 1] >= 0 and new_state[i + 1] >= 0:

                if not _judge_win_internal(tuple(new_state)):
                    return True 
    return False

def judge_win(lst):
    return _judge_win_internal(tuple(lst))

def judge_move_local(lst,i):

    '''Check whether the given point can be moved.'''

    if i==0 or i==len(lst)-1:
        return False
    else:
        if lst[i-1]*lst[i+1]==0:
            return False
        else:
            return True

def judge_move_global(lst):

    '''Check each point of the given list whether it can be moved,
    if it can be moved, return the index of the points. 
    If all the points cannot be moved, return [].'''

    moving=[]
    for i in range(len(lst)):
        if judge_move_local(lst,i):
            moving.append(i)
    return moving
    
def judge_foresee(lst):
    l=judge_move_global(lst)
    s=[]
    for i in range(len(lst)):
        p=copy.copy(lst)
        if i in l:
            s.append(judge_win(acted_list(p,i)))
        else:
            s.append(None)
    return s
#------------------action functions-------------------#
def acted_list(lst,i):
    lst[i]+=1
    lst[i-1]-=1
    lst[i+1]-=1
    return lst



#------------------Test-------------------#
if __name__ == "__main__":
    lst=[2,3,4,1,2,2,1]
    print(judge_win(lst))
    print(judge_move_global(lst))
    print(acted_list(lst,judge_move_global(lst)[0]))
    lst=initial_setting()
    step=0
    while judge_move_global(lst)!=[]:
        step+=1
        print('------------------step {}-------------------'.format(step))
        print(lst)
        l=judge_move_global(lst)
        print(l)
        print(judge_win(lst))
        foresee=judge_foresee(lst)
        print(foresee)
        for i in range(len(lst)):
            if i<=9:
                if foresee[i]==False:
                    print('  {}    '.format(i),end='')
                else:
                    print('  {}   '.format(i),end='')
            else:
                if foresee[i]==False:
                    print(' {}    '.format(i),end='')
                else:
                    print(' {}   '.format(i),end='')
        print('\n')
        a=int(input())
        if a in l:
            acted_list(lst,a)
        else:
            step-=1
            continue
    else:
        print('------------------Game is over-------------------')
        print(lst)