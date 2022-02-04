class Game:

    def __init__(self) -> None:

        # Game Board
        self.board = "---|---|---\n"*2 + "---|---|---"

        # Hash table to mark the visited position
        self.visited = {}

        # Hash table to map positions to indexes in the string
        self.hash = {1:[0,3], 2:[4,7], 3:[8,11], 
                     4:[12,15], 5:[16,19], 6:[20,23],
                     7:[24,27], 8:[28,31], 9:[32, 35]}

    def input_game(self, symbol, position) -> bool:

        # If there is already a symbol in the position, return False
        if position in self.visited:
            return False       

        # Add symbol to board and mark it as visited 
        self.visited[position] = symbol
        self.board = self.board[:self.hash[position][0]] + " " + symbol + " " +  self.board[self.hash[position][1]:]   
        return True

    def end_game(self) -> bool:

        one = self.board[self.hash[1][0]:self.hash[1][1]]
        two = self.board[self.hash[2][0]:self.hash[2][1]]
        three = self.board[self.hash[3][0]:self.hash[3][1]]
        four = self.board[self.hash[4][0]:self.hash[4][1]]
        five = self.board[self.hash[5][0]:self.hash[5][1]]
        six = self.board[self.hash[6][0]:self.hash[6][1]]
        seven = self.board[self.hash[7][0]:self.hash[7][1]]
        eight = self.board[self.hash[8][0]:self.hash[8][1]]
        nine = self.board[self.hash[9][0]:self.hash[9][1]]

        # First row is the same symbol
        if one == two == three and one!= "---":
            return True

        # Second row is the same symbol
        elif four == five == six and four!= "---":
            return True

        # Third row is the same symbol
        elif seven == eight == nine and seven!= "---":
            return True

        # First diagonal is the same symbol
        elif one == five == nine and one!= "---":
            return True

        # Second diagonal is the same symbol
        elif three == five == seven and three!= "---":
            return True       

        # First col is the same symbol
        if two == five == eight and two != "---":
            return True

        # Second col is the same symbol
        if one == four == seven and one != "---":
            return True

        # third col is the same symbol
        if three == six == nine and nine != "---":
            return True

        # No victory condition is reached
        else:
            return False    

if __name__ == "__main__":
    xoxo = Game()
    print(xoxo.board)
    print("\n")
    xoxo.input_game("X", 2)
    xoxo.input_game("X", 5)
    xoxo.input_game("X", 8)
    print(xoxo.board)
    print(xoxo.end_game())
    