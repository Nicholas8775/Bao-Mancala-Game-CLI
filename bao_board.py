class Board:

    def __init__(self, current_state=None): # check back later
        self.player_pits = \
        [
            [
                [f'b{i}' for i in range(8, 0, -1)],
                [f'a{i}' for i in range(8, 0, -1)]
            ][::-1],
            [
                [f'A{i}' for i in range(1, 9)],
                [f'B{i}' for i in range(1, 9)]
            ],
        ][::-1]

        if current_state is None:
            self.state = {"1": 22, "2": 22, "N1": True, "N2": True}
            for side in self.player_pits:
                for row in side:
                    for pit in row:
                        if pit in ["A5", "a5"]:
                            self.state[pit] = 6
                        elif pit in ["A6", "A7", "a6", "a7"]:
                            self.state[pit] = 2 
                        else:
                            self.state[pit] = 0
        else:
            self.state = current_state

    def play_game(self):
        current_player = 0
        move_types = [self.tax, self.namu_capture, self.namu_takasa, \
            self.mtaji_capture, self.mtaji_takasa]

        while True:
            current_moves = self.get_available_moves(current_player)
            choice = self.give_options(current_moves[1])
            outcome = move_types[current_moves[0]](choice, current_player)
            if outcome[0] == 1:
                print("Player 1 has won!")
                break
            elif outcome[0] == 2:
                print("Player 2 has won!")
                break
            else:
                current_player = 1 - current_player
                self.state = outcome[1]
        self.state = outcome[1]
        self.display_board()

    def tax(self, move, player_num):
        """Tax the Nyumba. Special move in Takasa Namu

        Parameters
        ----------
        move : str
            notation for the move
        player_num : int
            which player is playing

        Returns
        -------
        tuple of (int, dict of {str : int or bool})
            status number and new state of board after the move
        """

        new_state = self.state.copy()

        # Remove seed from store like we are planting
        new_state[str(player_num + 1)] -= 1

        # Treating the Nyumba as if we are sowing a singleton - remove one seed
        new_state[move[:-1]] -= 1

        # Are we sowing left or right? Convert notation into an integer
        change = {"R" : 1, "L" : -1}[move[-1]]

        # Consecutively sow the two seeds
        new_state[move[0] + str(5 + change)] += 1
        new_state[move[0] + str(5 + (change*2))] += 1

        return (0, new_state)

    def namu_capture(self, move, player_num, current_state=None):
        """Performs a capture in the Namu stage of the game

        Parameters
        ----------
        move : str
            Notation of the move
        player_num : int
            which player is playing
        current_state : dict of {str : int or bool}, optional
            Current state of the board if you don't want
            to modify the current state property, by default None

        Returns
        -------
        tuple of (int, dict of {str : int or bool})
            status of play and current state of the game after the move
        """

        # Use board's state if not supplied with one
        if current_state is None:
            state = self.state.copy()
        else:
            state = current_state.copy()

        # Get direction of move from notation
        is_clockwise = int("R" == move[2])

        # Plant seed
        state = self.plant(player_num, move[:-1], state, is_clockwise)
        
        #number_of_min_seeds = [3, 2][state["N" + str(player_num + 1)] and \
        #    (state[self.player_pits[player_num][0][5]] >= 6)]
        
        # Perform caputre and prepare for the sowing
        outcome = self.capture(move[:-1], player_num, is_clockwise, state)
        is_clockwise = outcome[2]
        emptied_slot = outcome[1]
        next_slot = self.player_pits[player_num][0][[player_num-1, -player_num][is_clockwise]]

        # Sow with captured seeds
        while True:

            # Sowing
            outcome = self.sow(player_num, next_slot, emptied_slot, is_clockwise, last_round=state)
            status = outcome[0]
            state = outcome[1].copy()
            current_slot = outcome[2]


            # Select between different outcome cases from sowing:

            # Empty slot finished in - end turn
            if status == 0:
                break

            # Can capture again
            elif status == 2:
                intermediate_step = self.capture(current_slot, player_num, is_clockwise, state)
                emptied_slot = intermediate_step[1]
                is_clockwise = intermediate_step[2]
                next_slot = [["A8", "A1"], ["a8", "a1"]][player_num][is_clockwise]

            # Nyumba potential safari case
            elif status == 1 and state["N" + str(player_num + 1)] and state[["A5", "a5"][player_num]] > 6  \
                             and current_slot == ["A5", "a5"][player_num]:
                choice = self.get_choice(current_board_state=state)
                if choice == "r":
                    break
                emptied_slot = current_slot
                next_slot = self.get_next_slot(emptied_slot, is_clockwise)

            # Repeat sowing
            elif status == 1:
                emptied_slot = current_slot
                next_slot = self.get_next_slot(emptied_slot, is_clockwise)

            # In case there is a case unaccounted for, throw error with details
            else:
                print("Status: ", status)
                print("current slot: ", current_slot)
                print("Changed direction?: ", outcome[3])
                Board(state).display_board()
                raise AssertionError("An unexpected situation in Namu Capture") # is there another situation I am forgetting?

        # TODO: Determine if a player has won or not, and return that instead of 0
        return (0, outcome[1])

    def get_choice(self, current_board_state=None):
        """Get choice from a human player if they want to safari or rest in the Nyumba

        Parameters
        ----------
        current_board_state : dict of {str : int or bool}, optional
            Current board state if we don't want to use the state currently tied to the object, by default None

        Returns
        -------
        str
            letter representing the choice made
                r = rest
                s = safari
        """

        if current_board_state is None:
            state = self.state
        else:
            state = current_board_state
        
        while True:
            Board(state).display_board()
            x = input("\nDo you want to rest in the house, or go on a safari (chain sowing), thereby destroying the house?\n\
                (s = safari, r = rest)\n>>> ")
            if x not in ["s", "r"]:
                print("Bad input. You can only input s or r.")
            else:
                return x

    def namu_takasa(self, move, player_num, current_state=None):
        if current_state is None:
            state = self.state.copy()
        else:
            state = current_state.copy()
        is_clockwise = int("R" == move[2])
        state = self.plant(player_num, move[:-1], state)
        next_slot = self.get_next_slot(move[:-1], is_clockwise)
        emptied_slot = move[:-1]

        while True:
            outcome = self.sow(player_num, next_slot, emptied_slot, is_clockwise, last_round=state)
            # TODO: Add a check for end state here and return early if outcome is positive
            if outcome[0] == 0 or (outcome[1]["N" + str(player_num + 1)] and outcome[2].lower() == "a5"):
                break
            else:
                next_slot = self.get_next_slot(outcome[2], is_clockwise)
                emptied_slot = outcome[2]
                state = outcome[1]

        # TODO: Determine if a player has won or not, and return that instead of 0
        return (0, outcome[1])    

    def mtaji_capture(self, move, player_num):
        print("Mtaji Capture")
        pass

    def mtaji_takasa(self, move, player_num):
        print("Mtaji Takasa")
        pass

    def give_options(self, moves):
        full_options = [move[0] + direction for move in moves for direction in move[1]]
        while True:
            print("\n")
            self.display_board()
            print("Options:")
            for option in moves:
                sub_options = " or ".join(option[1])
                print(f" [{option[0]}# ({sub_options})]", end=" ")
            choice = input("\nWhich one?\n>>> ")

            if choice in full_options:
                return choice
            else:
                print(f"Not an available move: \"{choice}\"")

    def get_available_moves(self, player_num):
        """
        # moves: (move_type (int), available_moves (list)):
        # 0 = Namu + Taxing the Nyumba
        # 1 = Namu + Capture
        # 2 = Namu + Takasa
        # 3 = Mtaji + Capture
        # 4 = Mtaji + Takasa
        """
        if self.state[str(player_num+1)] > 0:
            moves = self.get_namu_move_type(player_num)
        else:
            moves = self.get_mtaji_move_type(player_num)

        return moves

    def get_namu_move_type(self, player_num):
        takasa_moves = []
        kula_moves = []
        for pit in self.player_pits[player_num][0]:
            if self.state[pit] == 0:
                continue
            elif self.state[pit[0].swapcase() + str(9 - int(pit[1]))] >= 1:
                if pit.lower() in ["a1", "a2"]:
                    kula_moves.append((pit, ["R"]))
                elif pit.lower() in ["a7", "a8"]:
                    kula_moves.append((pit, ["L"]))
                else:
                    kula_moves.append((pit, ["R", "L"]))
            else:
                takasa_moves.append((pit, ["R", "L"]))
        if len(kula_moves) != 0:
            return (1, kula_moves)

        potential_house_pit = ["A5", "a5"][player_num]
        if len(takasa_moves) == 1 and takasa_moves[0][0].lower() in ["a1", "a8"]:
            # can't sow towards back row - the front row would become temporarily empty and that is a lose state
            if takasa_moves[0][0].lower() == "a1":
                return (2, [(takasa_moves[0][0], ["R"])])
            else:
                return (2, [(takasa_moves[0][0], ["L"])])
        # You can't play a singleton unless 1. it is the only occupied hole in the front row left, or 2. the house is still present.
        # It is easier to work as if it was the formulated positively - that you can play a singleton unless there are occupied pits
        # in the front row which aren't singletons or there isn't a functional house
        elif (not self.state["N" + str(player_num + 1)]) or (self.state[potential_house_pit] < 6):
            check = [pit for pit in takasa_moves if self.state[pit[0]] > 1]
            # Unless singletons are the only remaining occupied holes in the front row (making check empty), singletons can't be played
            if len(check) != 0:
                takasa_moves = check
        elif len(takasa_moves) == 1:
            # Only a functioning house remains, so tax it
            return (0, takasa_moves)
        else:
            # Can't takasa the house since other options are available
            takasa_moves = [pit for pit in takasa_moves if pit[0] != potential_house_pit]

        return (2, takasa_moves)

    def get_mtaji_move_type(self, player_num):
        takasa_moves = []
        kula_moves = []
        for pit in self.player_pits[player_num][0]:
            if self.state[pit] in [0, 1]:
                continue
            move_outcomes = self.test_sow(player_num, pit)
            if move_outcomes[0] == 2:
                kula_moves.append((pit,[]))
                if move_outcomes[0] == 2:
                    kula_moves[-1][1].append("R")
                if move_outcomes[1] == 2:
                    kula_moves[-1][1].append("L") 
            elif move_outcomes[0] == 1:
                takasa_moves.append((pit,[]))
                if move_outcomes[0] is not None:
                    takasa_moves[-1][1].append("R")
                if move_outcomes[1] is not None:
                    takasa_moves[-1][1].append("L")
        if len(kula_moves) != 0:
            return (1, kula_moves)

    def plant(self, player_num, slot, current_state=None, display_result=False): # check back later
        if current_state is None:
            result = self.state.copy()
        else:
            result = current_state.copy()
        
        result[str(player_num + 1)] -= 1
        result[slot] += 1

        if display_result:
            Board(result).display_board()

        return result

    def capture(self, capturing_slot, player_num, old_direction, last_round=None): # check back later
        if last_round is None:
            current_state = self.state.copy()
        else:
            current_state = last_round.copy()

        captured_slot = capturing_slot[0].swapcase() + str(9 - int(capturing_slot[1]))
        print("capturing slot: " + capturing_slot)
        left_change = ["1", "2"]
        right_change = ["8", "7"]
        if capturing_slot[1] in left_change:
            new_direction = True
        elif capturing_slot[1] in right_change:
            new_direction = False
        else:
            new_direction = old_direction
        
        print(new_direction)
        
        return (1, captured_slot, new_direction)

    def sow(self, player_num, starting_slot, slot_to_be_emptied, is_clockwise, last_round=None, display_board=False): # check back later
        """
        Input: 
            player_num: int (the player sowing)
            starting_slot: int (the starting slot where the sowing will start)
            slot_to_be_emptied: string (the slot containing seeds to be sowed)
            is_clockwise: bool (the direction of sowing)

        Return:
            tuple of (
                int (status of play) (0 = regular end, 1 = repetition, 2 = capture),
                dictionary of strings (resulting state),
                str (current slot),
                bool or none (if capture then if a change in the direction)
            )
            or None

        Preform the main action of the game, sowing.
        """

        if last_round is None:
            result = self.state.copy()
        else:
            result = last_round
        player_side = self.player_pits[player_num][0] + self.player_pits[player_num][1]

        # If the slot to be emptied is already empty, this is an invalid move
        if result[slot_to_be_emptied] == 0:
            return None

        # Valid input. Preparation for sowing
        current_slot = self.get_next_slot(starting_slot, not is_clockwise) # helps simplify the logic by starting from the lot in the other direction

        if slot_to_be_emptied.lower() == "a5": # Sowing the Nyumba destroys it
            result["N" + str(player_num + 1)] = False
        
        seeds_left = result[slot_to_be_emptied] # Pick up all the seeds in the slot
        result[slot_to_be_emptied] = 0 # Slot now empty after all the seeds are taken

        # Start sowing!
        while seeds_left > 0:
            current_slot = self.get_next_slot(current_slot, is_clockwise) # Go to next slot
            result[current_slot] += 1 # Sow a seed
            seeds_left -= 1 # Lose the sowed seed to the slot

        if display_board:
            Board(current_state=result).display_board()
        
        flipside = current_slot[0].swapcase() + str(9 - int(current_slot[1]))
        if result[current_slot] > 1 and flipside in self.player_pits[1-player_num][0] and result[flipside] >= 1:
            return (2, result, current_slot, is_clockwise)
        if result[current_slot] > 1:
            return (1, result, current_slot, is_clockwise)
        return (0, result, current_slot, None)

    def get_next_slot(self, slot, clockwise): # check back later
        """
        Input: slot: str (current slot)
               clockwise: bool (decide if direction is clockwise or not)

        Return: str (next slot) 

        Gets the next slot on the board.
        """

        useful_number = -(((ord(slot[0].lower()) - ord("a")) * 2) - 1)
        
        
        new_slot_number = int(slot[1]) + ((clockwise * 2) - 1) * useful_number
        
        if new_slot_number not in list(range(1,9)):
            return chr(ord(slot[0]) + useful_number) + slot[1]
        else:
            return slot[0] + str(new_slot_number) 

    def is_in_end_state(self): # to update
        """
        Input:
            No input

        Return:
            Int (state of the game)

        Checks if game has reached its end state
        """
        # 0 = game still on, 1 = player one has won, 2 = player two has won

        current_state_p1 = [[self.state[x] for x in self.player_pits[0][0]], [self.state[x] for x in self.player_pits[0][1]]]
        current_state_p2 = [[self.state[x] for x in self.player_pits[1][0]], [self.state[x] for x in self.player_pits[1][1]]]
        # empty front rows check
        if False in [x >= 1 for x in current_state_p1[0]]:
            return 2
        if False in [x >= 1 for x in current_state_p2[0]]:
            return 1

        # If in Mtaji phase (2nd phase, no planting seeds left) then no pits with more than 1 seeds is game over.
        # If still in Kunamua phase (1st phase, planting seeds left) then they are safe.
        if self.state["1"] == 0:
            if False in [x > 1 for x in current_state_p1[0]] \
                      + [x > 1 for x in current_state_p1[1]]:
                      return 2
        if self.state["2"] == 0:
            if False in [x > 1 for x in current_state_p2[0]] \
                      + [x > 1 for x in current_state_p2[1]]:
                      return 1

        return 0

    def test_sow(self, player_num, slot): # return to this
        move_clockwise = self.sow(player_num, self.get_next_slot(slot, True), slot, True)
        move_anticlockwise = self.sow(player_num, self.get_next_slot(slot, False), slot, False)

        if move_clockwise is None:
            return None
        elif move_clockwise[0] in [0, 1] and move_anticlockwise[0] in [0, 1]:
            return [1, (slot, 2)]
        elif move_clockwise[0] == 2 and move_anticlockwise[0] == 2:
            return [2, (slot, 2)] 
        else:
            return [2, (slot, int(move_clockwise[0] > move_anticlockwise[0]))]

    def display_board(self):
        player_1_side = [[self.state[x] for x in row] for row in self.player_pits[0]]
        player_2_side = [[self.state[x] for x in row] for row in self.player_pits[1]]
        def fix_string(a): return (" " * (2 - len(str(a)))) + str(a)
        player_len = len(self.player_pits[0][0])
        fixed_player_1_side_inner_row = list(map(fix_string, player_1_side[0]))
        fixed_player_1_side_outer_row = list(map(fix_string, player_1_side[1]))
        fixed_player_2_side_inner_row = list(map(fix_string, player_2_side[0]))
        fixed_player_2_side_outer_row = list(map(fix_string, player_2_side[1]))

        Nyuma_p2 = [
            ["/Shimo \\|~|"],
            [ "     {} |~|"],
            [ "        |~|"],
            [ "{}      |~|"],
            ["\\ Kete /|~|"],
        ]
        Mbele_p2 = [
            ["/Shimo \\|~|"],
            [ "     {} |~|"],
            [ "        |~|"],
            [ "{}      |~|"],
            ["\\ Kete /|~|"],
        ]
        Mbele_p1 = [
            ["/Shimo \\|~|"],
            [ "     {} |~|"],
            [ "        |~|"],
            [ "{}      |~|"],
            ["\\ Kete /|~|"],
        ]
        Nyuma_p1 = [
            ["/Shimo \\|~|"],
            [ "     {} |~|"],
            [ "        |~|"],
            [ "{}      |~|"],
            ["\\ Kete /|~|"],
        ]

        Nyuma_p2 = [x * player_len for x in Nyuma_p2]
        for i in Nyuma_p2:
            i[-1] = i[-1][:-3]
        Nyuma_p2[1] = list(map(lambda x, y: y.format(x), self.player_pits[1][1], Nyuma_p2[1]))
        Nyuma_p2[3] = list(map(lambda x, y: y.format(x), fixed_player_2_side_outer_row, Nyuma_p2[3]))
        
        Mbele_p2 = [x * player_len for x in Mbele_p2]
        for i in Mbele_p2:
            i[-1] = i[-1][:-3]
        if self.state["N2"]:
            Mbele_p2[0][3] = "\\Shimo /|~|"
            Mbele_p2[1][3] = ">   {} <|~|"
            Mbele_p2[2][3] =  "[Nyumba]|~|"
            Mbele_p2[3][3] =  ">{}    <|~|"
            Mbele_p2[4][3] = "/ Kete \\|~|"
        Mbele_p2[1] = list(map(lambda x, y: y.format(x), self.player_pits[1][0], Mbele_p2[1]))
        Mbele_p2[3] = list(map(lambda x, y: y.format(x), fixed_player_2_side_inner_row, Mbele_p2[3]))
        Mbele_p2[2][0] = " Kichwa |~|"
        Mbele_p2[2][-1] = " Kichwa "
        Mbele_p2[2][1] = " Kimbi  |~|"
        Mbele_p2[2][-2] = " Kimbi  |~|"
        
        Mbele_p1 = [x * player_len for x in Mbele_p1]
        for i in Mbele_p1:
            i[-1] = i[-1][:-3]
        if self.state["N1"]:
            Mbele_p1[0][4] = "\\Shimo /|~|"
            Mbele_p1[1][4] = ">   {} <|~|"
            Mbele_p1[2][4] =  "[Nyumba]|~|"
            Mbele_p1[3][4] =  ">{}    <|~|"
            Mbele_p1[4][4] = "/ Kete \\|~|"
        Mbele_p1[1] = list(map(lambda x, y: y.format(x), self.player_pits[0][0], Mbele_p1[1]))
        Mbele_p1[3] = list(map(lambda x, y: y.format(x), fixed_player_1_side_inner_row, Mbele_p1[3]))
        Mbele_p1[2][0] = " Kichwa |~|"
        Mbele_p1[2][-1] = " Kichwa "
        Mbele_p1[2][1] = " Kimbi  |~|"
        Mbele_p1[2][-2] = " Kimbi  |~|"

        fixed_p1_Nemo = ("0" * (2 - len(str(self.state["1"])))) + str(self.state["1"])
        fixed_p2_Nemo = ("0" * (2 - len(str(self.state["2"])))) + str(self.state["2"])
        
        Nyuma_p1 = [x * player_len for x in Nyuma_p1]
        for i in Nyuma_p1:
            i[-1] = i[-1][:-3]
        Nyuma_p1[1] = list(map(lambda x, y: y.format(x), self.player_pits[0][1], Nyuma_p1[1]))
        Nyuma_p1[3] = list(map(lambda x, y: y.format(x), fixed_player_1_side_outer_row, Nyuma_p1[3]))

        print(                                                                                                  )
        print( ":=====================" +          ("===========" * player_len)[:-3] + "=====================:" )
        print( "|#|~~~~~~~~~~~~~~~~|#|" +          ("~~~~~~~~|#|" * player_len)[:-3] + "|#|~~~~~~~~~~~~~~~~|#|" )
        print( "|=+================+=+" +          ("========+=+" * player_len)[:-3] + "+=+================+=|" )
        print( "|~|################|~|" +                       "".join(Nyuma_p2[0]) + "|~|                |~|" )
        print( "|~|################|~|" +                       "".join(Nyuma_p2[1]) + "|~|    Mchezaji    |~|" )
        print( "|~|####  Nyuma  -->|~|" +                       "".join(Nyuma_p2[2]) + "|~|                |~|" )
        print( "|~|################|~|" +                       "".join(Nyuma_p2[3]) + "|~|       #2       |~|" )
        print( "|~|################|~|" +                       "".join(Nyuma_p2[4]) + "|~|                |~|" )
        print( "|~|################|=+" +          ("========+=+" * player_len)[:-3] + "+=+================+=|" )
        print( "|~|################|#|" +          ("~~~~~~~~|#|" * player_len)[:-3] + "|#|~~~~Kaskazini~~~|#|" )
        print( "|~|################|=+" +          ("========+=+" * player_len)[:-3] + "+=+================+=|" )
        print( "|~|################|~|" +                       "".join(Mbele_p2[0]) + "|~|                |~|" )
        print( "|~|################|~|" +                       "".join(Mbele_p2[1]) + "|~|     Ghala      |~|" )
        print( "|~|####  Mbele  -->|~|" +                       "".join(Mbele_p2[2]) + "|~|                |~|" )
        print( "|~|################|~|" +                       "".join(Mbele_p2[3]) + "|~|    {} Nemo     |~|".format(fixed_p2_Nemo))
        print( "|~|################|~|" +                       "".join(Mbele_p2[4]) + "|~|                |~|" )
        print( "|=+================+=+" +          ("========+=+" * player_len)[:-3] + "+=+================+=|" )
        print( "|#|~~~~~~~~~~~~~~~~|#|" +          ("###########" * player_len)[:-3] + "|#|~~~~~~~~~~~~~~~~|#|" )
        print( "|=+================+=+" +          ("========+=+" * player_len)[:-3] + "+=+================+=|" )
        print( "|~|                |~|" +                       "".join(Mbele_p1[0]) + "|~|################|~|" )
        print( "|~|     Ghala      |~|" +                       "".join(Mbele_p1[1]) + "|~|################|~|" )
        print( "|~|                |~|" +                       "".join(Mbele_p1[2]) + "|~|<--  Mbele  ####|~|" )
        print( "|~|    {} Nemo     |~|".format(fixed_p1_Nemo) + "".join(Mbele_p1[3]) + "|~|################|~|" )
        print( "|~|                |~|" +                       "".join(Mbele_p1[4]) + "|~|################|~|" )
        print( "|=+================+=+" +          ("========+=+" * player_len)[:-3] + "+=|################|~|" )
        print( "|#|~~~~~Kusini~~~~~|#|" +          ("~~~~~~~~|#|" * player_len)[:-3] + "|#|################|~|" )
        print( "|=+================+=+" +          ("========+=+" * player_len)[:-3] + "+=|################|~|" )
        print( "|~|                |~|" +                       "".join(Nyuma_p1[0]) + "|~|################|~|" )
        print( "|~|    Mchezaji    |~|" +                       "".join(Nyuma_p1[1]) + "|~|################|~|" )
        print( "|~|                |~|" +                       "".join(Nyuma_p1[2]) + "|~|<--  Nyuma  ####|~|" )
        print( "|~|       #1       |~|" +                       "".join(Nyuma_p1[3]) + "|~|################|~|" )
        print( "|~|                |~|" +                       "".join(Nyuma_p1[4]) + "|~|################|~|" )
        print( "|=+================+=+" +          ("========+=+" * player_len)[:-3] + "+=+================+=|" )
        print( "|#|~~~~~~~~~~~~~~~~|#|" +          ("~~~~~~~~|#|" * player_len)[:-3] + "|#|~~~~~~~~~~~~~~~~|#|" )
        print( ":=====================" +          ("===========" * player_len)[:-3] + "=====================:" )
        print(                                                                                                  )



if __name__ == "__main__":
    a = Board()
    a.play_game()
