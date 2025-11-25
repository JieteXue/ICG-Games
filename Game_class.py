'''REMAIN_BUGS: 
'''



import random, copy
class Game:

    #------------------initialization-------------------#
    def __init__(self, id, name, initial_setting, judge_win, movement_global, acted_situation, description=""):
        self.name = name
        self.id = id
        self.original_initial_setting = initial_setting
        self.judge_win = judge_win # get the situation and return True (can win 100%) or False
        self.movement_global = movement_global # get the situation and return all the possible moves (list of which can determine a move/action)
        self.acted_situation = acted_situation # get the situation and the moving advise to return the new situation
        self.description = description
        self.dict_difficulty = {'1':"Easy", '2':"Normal", '3':"Hard", '4':"Insane"}
        self.difficulty_movement_random = {'1':0.1, '2':0.5, '3':0.9, '4':1}
    
    def information(self):
        return(f"Game ID: {self.id}\t Game Name: {self.name}\n A Brief Description:\n\n {self.description}")
    
    def get_difficulty(self):
        return input("Please choose your game difficulty:\n 1. Easy\t 2. Normal\t 3. Hard\t 4. Insane\n ")
    

    def initial_setting(self): # Use this!!!
            self.difficulty = self.get_difficulty()
            print(f"Your choice is: {self.dict_difficulty[self.difficulty]}\n")
            self.situation=self.original_initial_setting()

    

    
    
    
   
#------------------judge functions-------------------#
    def judge_end(self):
        if self.movement_global(self.situation)==[]:
            return True
        else:
            return False
    
    def moving_advise(self):
    # FUCK HERE!
        temp_situation = copy.deepcopy(self.situation)
        for i in self.movement_global(temp_situation):
            if not self.judge_win(self.acted_situation(copy.deepcopy(temp_situation), i)):
                return i
        return self.movement_global(temp_situation)[0]

#------------------action functions-------------------#

    def refresh_situation(self, new_situation):
        self.situation = new_situation

    def random_move(self):
        if random.random()<=self.difficulty_movement_random[self.difficulty]:
            self.refresh_situation(self.acted_situation(self.situation,self.moving_advise()))
        else:
            self.refresh_situation(self.acted_situation(self.situation,random.choice(self.movement_global(self.situation))))
        
           











# Test
if __name__ == "__main__":

    n=int(input("Please choose a game:\n 1. Take Coins\n 2. Take and Split Cards\n 3. Cards Nim\n 4. Dawson's Kayles\n"))

    if n == 1:
        import games.game1_Take_Coins as game_1
        game1=Game(1,"Take Coins", game_1.initial_setting, game_1.judge_win, game_1.judge_move_global, game_1.acted_list, game_1.description)

        game1.initial_setting()
        print(game1.difficulty,game1.situation)
        print(game1.movement_global(game1.situation))
        print(game1.judge_win(game1.situation))
        if game1.judge_end():
            pass
        else:
            game1.random_move()
            print(game1.situation)

    if n == 2:
        import games.game2_Take_and_Split_Cards as game_2
        game2=Game(2,"Take and Split Cards", game_2.initial_setting, game_2.judge_win, game_2.judge_move_global, game_2.acted_list, game_2.description)

        game2.initial_setting()
        print(game2.difficulty,game2.situation)
        print(game2.movement_global(game2.situation))
        print(game2.judge_win(game2.situation))
        if game2.judge_end():
            pass
        else:
            game2.random_move()
            print(game2.situation)

    if n == 3:
        import games.game3_Nim as game_3
        game3=Game(3,"Nim", game_3.initial_setting, game_3.judge_win, game_3.judge_move_global, game_3.acted_list, game_3.description)

        game3.initial_setting()
        print(game3.difficulty,game3.situation)
        print(game3.movement_global(game3.situation))
        print(game3.judge_win(game3.situation))
        if game3.judge_end():
            pass
        else:
            game3.random_move()
            print(game3.situation)
    
    if n == 4:
        import games.game4_Dawson_Kayles as game_4
        game4=Game(4,"Dawson's Kayles", game_4.initial_setting, game_4.judge_win, game_4.judge_move_global, game_4.acted_list, game_4.description)

        game4.initial_setting()
        print(game4.difficulty,game4.situation)
        print(game4.movement_global(game4.situation))
        print(game4.judge_win(game4.situation))
        if game4.judge_end():
            pass
        else:
            game4.random_move()
            print(game4.situation)


        
        
