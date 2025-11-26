AUTHOR= 'Jiete Xue'
DATE= '2025/11/25'
VERSION= '1.0'


description='''Given: initial integer n, threshold k (1 ≤ k < n) \n

Players take turns: \n
- Let current number = m  \n
- Choose a divisor d of m where 1 ≤ d < m \n
- Compute new_number = m - d \n
- If new_number < k: current player loses \n
- Else: continue with new_number \n

Goal: Force your opponent into a position where they must make a losing move.'''


#------------------initial setting-------------------#
import random

def pre_words():
    print("We are going to start the game of Subtract_Factor.\n")
    n=input("Enter the number of initial integer n (larger than 100, or enter directly for random setting): ")
    k=input("Enter the threshold (larger than the square root of n, or enter directly for random setting): ")
    if n.isdigit() and k.isdigit():
        if int(n)**0.5<int(k):
            return [int(n),int(k)]

def random_list(lst):
    '''Generate a (random) list of bottles.'''
    if lst is None:
        n=random.randint(100,1000)
        k=random.randint(n**0.5//1,2 * (n**0.5//1))
        lst = [n,k]
    
    return lst

'''Here the winning list can be determined, for less computational cost, we deal with it here.'''  

def winner_optimized(n, k):
        global win
        win = [False] * (n + 1)
        if k <= n:
            win[k] = False

        for m in range(k + 1, n + 1):
            found_win_move = False
            # enumerate factors
            d = 1
            while d * d <= m:
                if m % d == 0:
                    for factor in [d, m // d]:
                        if factor < m:  # true factor
                            new_val = m - factor
                            if new_val < k:
                                continue
                            if not win[new_val]:
                                found_win_move = True
                                break
                    if found_win_move:
                        break
                d += 1
            win[m] = found_win_move

        return win[n]
def initial_setting():
    lst=random_list(pre_words())
    winner_optimized(lst[0],lst[1])
    return(lst)




#------------------judge functions-------------------#

def get_factors_optimized(n):
    if not isinstance(n, int) or n < 1:
        raise ValueError("Input must be a positive integer.")
    
    if n == 1:
        return [1]
    
    small = []
    large = []
    
    i = 1
    while i * i <= n:
        if n % i == 0:
            small.append(i)
            if i != n // i:
                large.append(n // i)
        i += 1
    
    return small + large[::-1]
    
def judge_win(lst):

    '''Check whether the given list is a winning list.'''

    return win[lst[0]]
    

def judge_move_local(lst,i):

    '''Check whether the given action can be moved.'''
    '''lst=[m (current number),k]'''
    '''i: an factor of lst[0]'''

    return i in get_factors_optimized(lst[0]) and lst[0]-i>=lst[1]

def judge_move_global(lst):

    '''Return a list of possible actions'''
    '''lst=[m (current number),k]'''
    '''i: an factor of lst[0]'''

    moving=[]
    factor=get_factors_optimized(lst[0])
    j=0

    while lst[0]-factor[j]>=lst[1]:
        moving.append(factor[j])
        j+=1

    return moving
    

#------------------action functions-------------------#
def acted_list(list,i):
    list[0]-=i
    return list




#------------------Test-------------------#

if __name__ == "__main__":
    import ast
    lst=initial_setting()
    print(win)
    while judge_move_global(lst)!=[]:
        print(lst)
        l=judge_move_global(lst)
        print(l)
        print(judge_win(lst))
        a=int(input("Choose your action from the list above: "))
        if a in l:
            acted_list(lst,a)
        else:
            continue
    else:
        print(lst)
        print('Game is over')