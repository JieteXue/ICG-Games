AUTHOR= 'Jiete Xue'
DATE= '2025/11/18'
VERSION= '1.0'






description='''There are initially n cards in one bunch on the table. \n
You can choose to take 1-k cards from one bunch, or split them into two bunches (each bunch can't be empty). \n
The player who get the last card on the table wins.'''







#------------------initial setting-------------------#
import random

def pre_words():
    print("We are going to start the game of taking and splitting cards.\n")
    n=input("Enter the number of initial cards (larger than 5, or enter directly for random setting): ")
    k=input("Enter the maximum number of cards you can take (larger than 1, or enter directly for random setting): ")
    if n.isdigit() and k.isdigit(): 
        if int(n)>5 and int(k)>1:
            return [int(k),int(n)]

def initial_list(lst=None):

    '''We use a list to record the number of cards in each bunch.

    ATTENTION: the first element is the max number of cards you can take.'''

    if lst is None:
        lst=[random.randint(2,10),random.randint(6,20)]
    return lst

def initial_setting():
    return(initial_list(pre_words()))






#------------------judge functions-------------------#

def SG(n,k):

    '''Given n(the number of initial cards) and 
    k(the maximum number of cards you can take), 
    return the value of SG.'''

    if n%(2**k) == 0:
        return n-1
    elif n%(2**k) == 2**k-1:
        return n+1
    else:
        return n

def judge_win(lst):

    '''Check whether the given list is a winning list.'''
    sg=0
    for i in range(1,len(lst)):
        sg^=SG(list[i],lst[0])
    if sg==0:
        return False
    else:
        return True

def judge_move_local(lst,i):

    '''Check whether the given action can be moved.'''
    '''i is exactly a list (for convenience of representing actions)
    i=[index in the list you choose, number of cards you choose, (if split, place you choose)]
    Two mode: split or take
    (1) i[0]==0: split, i[1]=rest number of cards at the place you choose, i[2]=place you choose
    (2) i[0]!=0: take, i[1]=number of cards you choose'''

    if i[0]==0:
        if lst[i[2]]<=i[1] or i[2]<=0:
            return False
        else:
            return True
    else:
        if lst[i[0]]<i[1] or i[1]>lst[0] or i[1]<1:
            return False
        else:
            return True

def judge_move_global(lst):

    '''Check each point of the given list whether it can be moved,
    if it can be moved, return the index of the points. 
    If all the points cannot be moved, return [].'''

    moving=[]
    # Take
    for i in range(1,len(lst)):
        for num in range(1,lst[0]+1):
            if judge_move_local(lst,[i,num]):
                moving.append([i,num])

    # Split
    for i in range(1,len(lst)):
        if lst[i]>1:
            for j in range(1,lst[i]):
                if judge_move_local(lst,[0,j,i]):
                    moving.append([0,j,i])
    return moving




#------------------action functions-------------------#
def acted_list(lst,i):

    '''Return the list after one move.
        i=[index in the list you choose, number of cards you choose, (if split, place you choose)]
        Two mode: split or take
        (1) i[0]==0: split, i[1]=rest number of cards at the place you choose, i[2]=place you choose
        (2) i[0]!=0: take, i[1]=number of cards you choose'''

    if i[0]==0:
        lst.append(lst[i[2]]-i[1])
        lst[i[2]]=i[1]
    else:
        lst[i[0]]-=i[1]
    return lst
    

    









#------------------Test-------------------#

if __name__ == "__main__":
    #list setting part
    print(initial_setting())

    #judge win part
    list=[2,3,4,1,2,2,1]
    print(judge_win(list))

    #judge move part
    list=[2,3,4,1,2,2,1]
    print(judge_move_global(list))

    #acted list part
    list=[2,3,4,1,2,2,1]
    print(acted_list(list,[0,2,1]))




