AUTHOR= 'Jiete Xue'
DATE= '2025/11/21'
VERSION= '1.0'


description='''n bottles on a line. \n
You can take two adjacent bottles, if it is possible. \n
The player who can not move loses.'''


#------------------initial setting-------------------#
import random

def pre_words():
    print("We are going to start the game of Dawson's Kayles Taking bottles.\n")
    n=input("Enter the number of initial bottles (larger than 1, or enter directly for random setting): ")
    if n.isdigit(): 
        return int(n)

def random_list(n=-1):
    '''Generate a (random) list of bottles.'''
    if n is None or type(n)!=int or n<=1:
        lst=[1 for i in range(random.randint(5,10))]
    else:
        lst=[1 for i in range(n)]
    return lst

def initial_setting():
    return(random_list(pre_words()))




#------------------judge functions-------------------#

def SG(n):
    # Grundy numbers (0-51)
    base_grundy = [
        0, 0, 1, 1, 2, 0, 3, 1, 1, 0, 3, 3, 2, 2, 4, 0, 5, 2, 2, 3, 3,
        0, 1, 1, 3, 0, 2, 1, 1, 0, 4, 5, 2, 4, 0, 1, 1, 2, 0, 3, 1, 1,
        0, 3, 3, 2, 2, 4, 4, 0, 5, 4
    ]
    
    # For n >= 52，SG(n) = SG(n - 34*k) where n-34*k < 52
    if n < len(base_grundy):
        return base_grundy[n]
    else:
        period = 34
        start_period = 52
        equivalent_n = (n - start_period) % period + (start_period - period)
        return base_grundy[equivalent_n]
    
def judge_win(lst):

    '''Check whether the given list is a winning list.'''

    splits=[]
    count=0
    for i in range(len(lst)):
        if list[i]==1:
            count+=1
        else:
            if count!=0:
                splits.append(count)
            count=0
    if count!=0:
        splits.append(count)
    sg=0
    for i in range(len(splits)):
        sg^=SG(splits[i])
    return sg!=0
    

def judge_move_local(list,i):

    '''Check whether the given action can be moved.'''
    '''i: take bottles which index are i and i+1'''

    return i>=0 and i<len(list)-1 and list[i]==1 and list[i+1]==1

def judge_move_global(lst):

    '''Return a list of possible actions'''

    moving=[]
    for i in range(len(lst)-1):
        if judge_move_local(lst,i):
                moving.append(i)
    return moving
    

#------------------action functions-------------------#
def acted_list(lst,i):
    lst[i]=0
    lst[i+1]=0
    return lst




#------------------Test-------------------#

if __name__ == "__main__":
    import ast
    lst=initial_setting()
    step=0
    while judge_move_global(lst)!=[]:
        step+=1
        print('------------------step {}-------------------'.format(step))
        print(lst)
        l=judge_move_global(lst)
        print(l)
        print(judge_win(lst))
        a=int(input("Choose your action from the list above: "))
        if a in l:
            acted_list(lst,a)
        else:
            step-=1
            continue
    else:
        print('------------------Game is over-------------------')
        print(lst)