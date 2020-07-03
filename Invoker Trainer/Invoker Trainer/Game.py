"""
Game object holds data for a game played by a user. Should
not be confused with the class for actually playing the game.

"""

class Game():
    
    # Constructor can take raw data or formatted data from the actual game

    def __init__(self,*data):

        # Raw data if the length of arguments is 1
        if len(data) == 1:
            self.id = int(data[0][0])
            self.options = []
            self.score = int(data[0][2])
            self.combos = []

            self.parseOptions(data[0][1])
            self.parseCombos(data[0][3:])
        else:
            self.id = data[0]
            self.options = data[1]
            self.score = data[2]
            self.combos = data[3]
    
    # Function parses a string of options into the appropriate structure

    def parseOptions(self,data):
        splitData = data[1:-1].split(",")

        for option in splitData:
            self.options.append(option)

    # Function parses a list of sentences into the appropriate structure 

    def parseCombos(self,data):
        for combo in data:
            splitData = combo[1:-2].split(",")
            self.combos.append([int(splitData[0]),float(splitData[1])])



