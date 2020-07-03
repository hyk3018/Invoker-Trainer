import Game

"""
Class that manages a single account at a time, as there is currently no
intention in using multiple accounts at the same time
"""

class Accounts:

    # Sets up key class attributes, with current account assigned None at first
    # as no account object had been parsed yet. Same applies to loginDetails.

    def __init__(self):

        self.currentAccount = None
        self.ACCOUNT_PATH = "account"
        self.LOGIN_PATH = "login"
        self.loginDetails = {}

    # Parse the options and match data to allow creation of an instance of current account

    def loadAccount(self,username):
            
        # Get list of game data and settings dictionary
        gameData = self.parseGameData(username)
        settings = self.parseSettings(username)

        self.currentAccount = Account(username,gameData,settings)
    
    # Save any of the account's data and set it to null

    def unloadAccount(self):
        self.saveGameData()
        self.saveSettings()
        self.currentAccount = None
    
    # Generate Account Files

    def createAccount(self,username):

        # Assign name of the files to be created
        gameDataPath = self.ACCOUNT_PATH + r"\game_data\\" + username + ".txt"
        settingsPath = self.ACCOUNT_PATH + r"\settings\\" + username + ".txt"

        # Get data from default settings file
        defaultSettings = open(self.ACCOUNT_PATH + r"\default_options.txt","r")
        defaultData = defaultSettings.read()
        defaultSettings.close()

        # Create the files, writing default data to the settings file
        dataFile = open(gameDataPath,"w")
        dataFile.close()

        settingsFile = open(settingsPath,"w")
        settingsFile.write(defaultData)
        settingsFile.close()
        
    def parseGameData(self,username):

        # Get path name for the game data and set up file handler
        gameDataPath = self.ACCOUNT_PATH + r"\game_data\\" + username + ".txt"
        gameDataFile = open(gameDataPath, "r")
        gameDataLines = gameDataFile.readlines()
        gameDataFile.close()

        # Remove the \n from each line
        gameDataLines = list(map(lambda line:line[:-1],gameDataLines))

        # Parse games
        games = []
        currentGame = []
        for line in gameDataLines:

            # If the end of the data set is reached then add the add and reset currentGame list
            if line == "END_OF_DATA":
                games.append(currentGame)
                currentGame = []
            else:
                currentGame.append(line)

        games = list(map(Game.Game,games))
        return games

    def parseSettings(self,username):
        
        # Get path name for settings and set up file handler
        settingsPath = self.ACCOUNT_PATH + r"\settings\\" + username + ".txt"
        settingsFile = open(settingsPath, "r")
        settingsLines = settingsFile.readlines()
        settingsFile.close()

        # Remove the \n from each line
        settingsLines = list(map(lambda line:line[:-1],settingsLines))

        # Parse settings
        settings = {}
        for line in settingsLines:
            keyAndValue = line.split("=")
            settings[keyAndValue[0]] = keyAndValue[1]

        settings["AGHANIMS"] = int(settings["AGHANIMS"])
        settings["OCTARINE"] = int(settings["OCTARINE"])
        settings["ARCANE_RUNE"] = int(settings["ARCANE_RUNE"])
        settings["QUICKCAST"] = int(settings["QUICKCAST"])
        return settings

    # Turn the game data in accounts list to string to be written to file

    def saveGameData(self):

        if self.currentAccount == None:
            return

        # Set up the file handler and new string to be written to file
        dataFile = open(self.ACCOUNT_PATH + r"\game_data\\" + self.currentAccount.name + ".txt", "r+")
        dataString = ""

        # Add each game's data to data string and add "END_OF_DATA" between each game for future parsing
        for game in self.currentAccount.games:
            dataString += str(game.id) + "\n"

            dataString += "["
            for option in game.options:
                dataString += option + ","

            # Remove the last common then close the array and add new line
            dataString = dataString[:-1] + "]\n" if len(game.options) != 0 else dataString + "]\n"

            dataString += str(game.score) + "\n"

            for combo in game.combos:
                dataString += "[" + str(combo[0]) + "," + str(combo[1]) + "]\n"
            dataString += "END_OF_DATA\n"


        # Write to the files and then close
        dataFile.write(dataString)
        dataFile.close()

    # Turn the settings in a string to be saved to the account's setting file
    # Similar to saveGameData, only the string manipulation is different

    def saveSettings(self):

        if self.currentAccount == None:
            return

        # Set up handler and write string
        settingsFile = open(self.ACCOUNT_PATH + r"\settings\\" + self.currentAccount.name + ".txt", "r+")
        settingsString = ""

        # Write the settings key and the setting value separated by "=" key
        for option in self.currentAccount.settings:
            settingsString += option + "=" + str(self.currentAccount.settings[option]) + "\n"

        # Write and close file
        settingsFile.write(settingsString)
        settingsFile.close()
        
    # Parse login data into dictionary

    def loadLogin(self):
        
        # Instantiate login file handler and obtain all lines
        loginFile = open(self.LOGIN_PATH + r"\account_details.txt")
        loginLines = loginFile.readlines()
        loginFile.close()

        loginLines = list(map(lambda line:line[:-1],loginLines))

        # Every 4 lines contains data for a single user
        # Assign each 4 lines as key and value to login details dict
        for i in range(int((len(loginLines))/4)):
            username = loginLines[i*4]
            self.loginDetails[username] = []
            self.loginDetails[username].append(loginLines[i*4+1])
            self.loginDetails[username].append(int(loginLines[i*4+2]))
            self.loginDetails[username].append(int(loginLines[i*4+3]))
    
    # Save the login details onto the file

    def saveLogin(self):

        loginFile = open(self.LOGIN_PATH + "\\account_details.txt", "r+")
        loginString = ""

        # For each login detail, add the username, hashed password, salt, and login flag
        for account in self.loginDetails:

            loginString += account + "\n"
            loginString += str(self.loginDetails[account][0]) + "\n"
            loginString += str(self.loginDetails[account][1]) + "\n"
            loginString += str(self.loginDetails[account][2]) + "\n"
        
        loginFile.write(loginString)
        loginFile.close()

    # Add a new Game object to list of games in current account

    def addGameData(self,score,options,combos):

        # New game data ID is 1 higher than the previous
        if len(self.currentAccount.games) == 0:
            id = 1
        else:
            id = self.currentAccount.games[-1].id + 1
        self.currentAccount.games.append(Game.Game(id,options,score,combos))

    # Change the settings dictionary in the current loaded account

    def changeSettings(self,newSettings):
        self.currentAccount.settings = newSettings
        self.saveSettings()

    # Adds an accout to the login details dictionary

    def addLogin(self,username,password,salt):
        self.loginDetails[username] = [password,salt,1]
        self.saveLogin()

    # Returns whether a username already exists

    def userExists(self,username):
        for existing in self.loginDetails:
            if username == existing:
                return True
        return False

class Account:

    def __init__(self,name,games,settings):
        self.name = name
        self.games = games
        self.settings = settings
