import Accounts, Dota, Statistics
import tkinter as tk
import sys, random, hashlib, math
from PIL import Image, ImageTk
from tkinter import messagebox
import pygame
from InvokerGame import InvokerGame

"""
Class implements user interface through tkinter module
Inherits from the Frame object in tkinter so that it can
be added to the root window
"""

class Application(tk.Frame):

    # Set parent and initialise Frame instantiation code, passing in parent object
    # Set title of the window and add necessary panel objects
    # Initialise other important Singleton objects, such as Account system

    def __init__(self,parent):

        # Set parent and initialise frame
        self.parent = parent
        tk.Frame.__init__(self,self.parent)

        # Handle close event
        self.parent.protocol("WM_DELETE_WINDOW", self.onClose)

        # Set title and window size
        self.winfo_toplevel().title("Invoker Trainer")
        self.parent.resizable(0,0)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Initialise Singleton instances
        
        self.accountManager = Accounts.Accounts()
        self.accountManager.loadLogin()

        # Initialise Panel Objects
        self.panels = {}

        for Panel in (EntryPanel,MenuPanel,DataViewPanel,SettingsPanel):
            panel = Panel(self)
            self.panels[Panel] = panel

        # Show the window and set the first shown panel to be the entry panel
        self.pack(side="top",fill="both",expand=True)
        self.showPanel(EntryPanel)

    # Catch disallowed close commands and save any data

    def onClose(self):
        # Catch closing the tkinter window from Pygame
        try:
            # Only close if they confirm quit
            if messagebox.askokcancel("Quit", "Are you sure you wish to quit?"):
                #Close pygame and tkinter
                pygame.quit()
                self.parent.destroy()

                # Save account data
                self.accountManager.saveGameData()
                self.accountManager.saveSettings()
                self.accountManager.saveLogin()
                try:
                    sys.exit()
                except:
                    pass
        except:
            if messagebox.askokcancel("Quit", "Are you sure you wish to quit?"):
                pygame.quit()
                self.parent.destroy()
                self.accountManager.saveGameData()
                self.accountManager.saveSettings()
                self.accountManager.saveLogin()
                try:
                    sys.exit()
                except:
                    pass

    # Called when login is completed, shows the menu panel and loads the account
    # Also commences the menu panel's scrolling text news reader

    def transitionMenu(self,username=None):
        if username != None:
            self.accountManager.loadAccount(username)
        self.showPanel(MenuPanel)
        
        # Initiate the news reader
        self.panels[MenuPanel].scrollText()

    def transitionLogin(self):
        self.accountManager.unloadAccount()
        self.showPanel(LoginPanel)

    # Removes current panel from grid and grids the required one

    def showPanel(self,newPanel,firstTime=False):
        if newPanel == MenuPanel:
            if firstTime:
                self.panels[MenuPanel].changeImage("help")
            else:
                self.panels[MenuPanel].changeImage("normal")
        for panel in self.panels:
            self.panels[panel].grid_remove()

        self.panels[newPanel].grid()
"""
Class implements the Entry panel that will be what is first
shown when the program is opened - allows for logging in and
registration
"""

class EntryPanel(tk.Frame):

    # Constructor sets out the structure of the panel and any widgets needed
    def __init__(self,parent):

        # Set parent as the application
        self.parent = parent
        tk.Frame.__init__(self,self.parent)
        self.rowconfigure(1,weight=1)
        self.columnconfigure(1,weight=1)
        
        # Initialise the variables linked to the entry widgets so they can be accessed as class attributes
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.username.set("")
        self.password.set("")

        # Set up the inner Frame objects used to structure the layout of the panel
        self.interface = tk.Frame(self,padx=10)
        self.interfaceTop = tk.Frame(self.interface,pady=10)
        self.interfaceBottom = tk.Frame(self.interface)

        # Set up the individual widgets and link them to variables where necesssary
        self.usernameLabel = tk.Label(self.interfaceTop,text="Username:")
        self.passwordLabel = tk.Label(self.interfaceTop,text="Password:")
        self.usernameEntry = tk.Entry(self.interfaceTop,textvariable=self.username)
        self.passwordEntry = tk.Entry(self.interfaceTop,textvariable=self.password,show="●")

        # Set up the buttons and assign the functions they should call when clicked on
        self.loginButton = tk.Button(self.interfaceBottom,command=self.login,text="Login",width=10)
        self.registerButton = tk.Button(self.interfaceBottom,command=self.register,text="Register",width=10)
        
        # Code for placing the widgets in the Frames and showing the objects
        self.usernameLabel.grid(row=0,column=0,sticky="e")
        self.passwordLabel.grid(row=1,column=0,sticky="e")
        self.usernameEntry.grid(row=0,column=1)
        self.passwordEntry.grid(row=1,column=1)
        self.loginButton.grid(row=0,column=0)
        self.registerButton.grid(row=0,column=1)

        # Assign weight to the Frames so that the widgets can stretch out and display
        self.interfaceBottom.grid_columnconfigure(0, weight=1)
        self.interfaceBottom.grid_columnconfigure(1, weight=1)
        self.interface.grid(row=0,column=0,rowspan=2)
        self.interfaceTop.grid(row=0,column=0)
        self.interfaceBottom.grid(row=1,column=0,sticky="we")

        # Load the decorative image and assign it to Label widget
        self.decoration = tk.Frame(self)
        self.invokerImage = Image.open(r"C:\Users\Tommy\Desktop\CS\CS Project\Invoker Trainer\Invoker Trainer\assets\start_background.png")
        self.invokerImage = ImageTk.PhotoImage(self.invokerImage)
        self.imageLabel = tk.Label(self.decoration,image=self.invokerImage)
        self.imageLabel.grid(row=0,column=0)
        self.decoration.grid(row=0,column=2,rowspan=2)

        self.grid(row=0,column=0,rowspan=2,sticky="nsew")

    # Function takes data from entry and validates it against pre-existing login data

    def login(self):
        # Obtain local copy of username and password
        username = self.username.get()
        password = self.password.get()

        if self.parent.accountManager.userExists(username):

            # Hash input password and compare against actual password
            salt = str(self.parent.accountManager.loginDetails[username][1])
            inputHash = str(hashlib.pbkdf2_hmac("sha256",password.encode("utf-8"),salt.encode("utf-8"),1000000))

            if inputHash == str(self.parent.accountManager.loginDetails[username][0]):
                messagebox.showinfo("Successful login.","You are now logged in as {0}.".format(username))
                self.parent.accountManager.loadAccount(username)

                # Check if first time logging in
                if self.parent.accountManager.loginDetails[username][2] == 1:
                    self.parent.showPanel(MenuPanel,True)

                    # Change first time login to false for future logins
                    self.parent.accountManager.loginDetails[username][2] = 0
                    self.parent.accountManager.saveLogin()
                else:
                    self.parent.showPanel(MenuPanel)
                self.parent.panels[MenuPanel].usernameLabel.config(text="Logged in as : " + username)
                
                self.usernameEntry.focus()
                self.username.set("")
                self.password.set("")
            else:
                messagebox.showinfo("Login Fail","Invalid username and/or password.")
                self.usernameEntry.focus()
                self.username.set("")
                self.password.set("")
        else:

            # Display login failure and reset entry
            messagebox.showinfo("Login Fail","Invalid username and/or password.")
            self.usernameEntry.focus()
            self.username.set("")
            self.password.set("")


    # Function takes data from entry, validates it and adds to login details file is successful

    def register(self):

        # Obtain local copy of entry data so there are less data access function calls
        username = self.username.get()
        password = self.password.get()
        usernameLength = len(username)
        passwordLength = len(password)

        # Validate the length of the username and password
        if usernameLength >= 6 and usernameLength <= 18 and passwordLength >= 6 and passwordLength <= 18: 
            # Validate the username doesn't exist
            if self.parent.accountManager.userExists(username):
                messagebox.showinfo("Registration Failed.","Username already exists.")

                # If registration fails, reset entry values and focus on the username once again
                self.usernameEntry.focus()
                self.username.set("")
                self.password.set("")
                return
            else:
                # If username and password is valid, generate salt and hash the password using SHA256 function
                salt = str(random.randint(1000,9999))
                hashedPassword = hashlib.pbkdf2_hmac("sha256",password.encode("utf-8"),salt.encode("utf-8"),1000000)

                # Add the login account to file
                self.parent.accountManager.addLogin(username,hashedPassword,salt)
                messagebox.showinfo("Registration Successful.","You are now registered and can log in.")

                # Create account files
                self.parent.accountManager.createAccount(username)

                self.usernameEntry.focus()
                self.username.set("")
                self.password.set("")
                return

        else:

            # If invalid length, output message and reset data
            messagebox.showinfo("Registration Failed.","Username and password should be 6-18 characters in length.")
            self.usernameEntry.focus()
            self.username.set("")
            self.password.set("")
            return

"""
Class implements the Main Menu panel that will be raised when
login is successful, and allows for navigation to other components
"""

class MenuPanel(tk.Frame):

    # Construtor sets up panel structure and widgets

    def __init__(self,parent):

        # Set parent and initialise superclass constructor
        self.parent = parent
        tk.Frame.__init__(self,parent)

        self.gamePlaying = False

        self.mechanics = Dota.Dota()

        # Load the messages and get a random one from the list
        self.messages = self.loadMessages()
        self.randomMessage = tk.StringVar()
        self.randomMessage.set(random.choice(self.messages))

        # If the message is short, add spaces so it fits the window better
        if len(self.randomMessage.get()) < 130:
            self.randomMessage.set(self.randomMessage.get() + (130-len(self.randomMessage.get())) * " ")

        # Set up structure
        self.main = tk.Frame(self)
        self.bottom = tk.Frame(self)

        self.mainTop = tk.Frame(self.main,padx=5)
        self.mainBottom = tk.Frame(self.main,padx=5)

        # Add in main widgets
        self.title = tk.Label(self.mainTop,text="Invoker Trainer",pady=20)
        self.playButton = tk.Button(self.mainTop,text="Play Game",command=self.startGame,bg="gray")
        self.dataViewButton = tk.Button(self.mainTop,text="Data View",command=self.changeDataView,bg="gray")
        self.settingsButton = tk.Button(self.mainTop,text="Settings",command=self.changeSettings,bg="gray",)
        self.helpButton = tk.Button(self.mainBottom,text="Help",command=self.openHelp,bg="gray")
        self.logoutButton = tk.Button(self.mainBottom,text="Log Out",command=self.logout,bg="gray")

        self.credits = tk.Label(self.bottom,text="Tips Provided by Tsunami")
        self.messageLabel = tk.Label(self.bottom,textvariable=self.randomMessage,width=72,bg="orange2")

        # Grid main structure
        self.main.grid(row=0,column=0)
        self.bottom.grid(row=1,column=0,sticky="we")
        self.bottom.grid_columnconfigure(0,weight=1)
        self.bottom.grid_columnconfigure(1,weight=1)

        # Grid the widgets onto the main UI
        self.mainTop.grid(row=0,column=0,sticky="we")
        self.mainTop.grid_columnconfigure(0,weight=1)
        self.title.grid(row=0,column=0,sticky="we",pady=5)
        self.playButton.grid(row=1,column=0,sticky="we",pady=5)
        self.dataViewButton.grid(row=2,column=0,sticky="we",pady=5)
        self.settingsButton.grid(row=3,column=0,sticky="we",pady=5)

        self.mainBottom.grid(row=1,column=0,sticky="swe")
        self.helpButton.grid(row=0,column=0,sticky="we",padx=5,pady=10)
        self.logoutButton.grid(row=0,column=1,sticky="we",padx=5,pady=10)

        # Grid the bottom info widgets
        self.bottom.grid_columnconfigure(0,weight=1)
        self.bottom.grid_columnconfigure(1,weight=1)
        self.messageLabel.grid(row=0,column=0,sticky="nswe")
        self.credits.grid(row=0,column=1,sticky="nsew",padx=5)

        # Intitialise and grid the decorative image
        self.decoration = tk.Frame(self.main)
        self.imageState = "normal"
        self.invokerImage = Image.open(r"C:\Users\Tommy\Desktop\CS\CS Project\Invoker Trainer\Invoker Trainer\assets\menu_background.png")
        self.helpImage = Image.open(r"C:\Users\Tommy\Desktop\CS\CS Project\Invoker Trainer\Invoker Trainer\assets\help.png")
        self.invokerImage = ImageTk.PhotoImage(self.invokerImage)
        self.helpImage = ImageTk.PhotoImage(self.helpImage)
        self.imageLabel = tk.Label(self.decoration,image=self.invokerImage)
        self.usernameLabel = tk.Label(self.decoration)

        self.decoration.grid(row=0,column=1,rowspan=2)
        self.imageLabel.grid(row=0,column=0)
        self.usernameLabel.grid(row=0,column=0,sticky="ne")

        # Grid entire panel
        self.grid(row=0,column=0,rowspan=2,columnspan=2,sticky="nsew")

        # Start scrolling marquee
        self.scrollText()
    
    # Function opens the messages file and randomly gets a message

    def loadMessages(self):

        msgFile = open(r"C:\Users\Tommy\Desktop\CS\CS Project\Invoker Trainer\Invoker Trainer\messages.txt","r")
        messages = msgFile.readlines()
        msgFile.close()

        # Remove the new line character
        messages = list(map(lambda message:message[:-1],messages))

        return messages

    # Function called every 130 milliseconds to keep the marquee text scrolling

    def scrollText(self):

        # Take the first character and move it to back of string
        self.randomMessage.set(str(self.randomMessage.get()[1:] + self.randomMessage.get()[0]))

        if not self.gamePlaying:
            self.parent.parent.after(130,self.scrollText)

    # Function called to change the image when needed - for login and help functionality

    def changeImage(self,imageName):

        if imageName == "help":
            self.imageLabel.config(image=self.helpImage)
            self.imageState = "help"
        elif imageName == "normal":
            self.imageLabel.config(image=self.invokerImage)
            self.imageState = "normal"

    # Open the Pygame window

    def startGame(self):
        # Stop the scrolling
        self.gamePlaying = True

        # Disable all buttons
        self.playButton.config(state="disabled")
        self.dataViewButton.config(state="disabled")
        self.settingsButton.config(state="disabled")
        self.helpButton.config(state="disabled")
        self.logoutButton.config(state="disabled")
        self.playButton.update()
        self.dataViewButton.update()
        self.settingsButton.update()
        self.logoutButton.update()

        # Initialise game object and pass in the return function that is to be called when game window closes
        self.game = InvokerGame(self.parent,self.endGame,self.mechanics)

    # Reset buttons

    def endGame(self):

        # Restart scrolling text and set gamePlaying to false so that the scroll keeps calling itself
        self.game = None
        self.gamePlaying = False
        self.scrollText()

        # Reset the buttons so theycan be used again
        self.playButton.config(state="normal")
        self.dataViewButton.config(state="normal")
        self.settingsButton.config(state="normal")
        self.helpButton.config(state="normal")
        self.logoutButton.config(state="normal")
        self.playButton.update()
        self.dataViewButton.update()
        self.settingsButton.update()
        self.logoutButton.update()

    # Switch to Data View panel

    def changeDataView(self):
        self.parent.accountManager.loadAccount(self.parent.accountManager.currentAccount.name)
        self.parent.panels[DataViewPanel].loadData(self.parent.accountManager.currentAccount.games)
        self.parent.showPanel(DataViewPanel)

    # Switch to Settings panel and initialise settings object

    def changeSettings(self):
        self.parent.panels[SettingsPanel].loadSettings(self.parent.accountManager.currentAccount.settings)
        self.parent.showPanel(SettingsPanel)

    # Help button pressed

    def openHelp(self):
        if self.imageState == "normal":
            self.changeImage("help")
        else:
            self.changeImage("normal")

    # Removes account instance and switches to login panel

    def logout(self):
        if messagebox.askyesno("Log Out","Do you wish to log out?"):
            self.parent.accountManager.unloadAccount()
            self.parent.showPanel(EntryPanel)

"""
Class implements Data View Panel that will be in charge of
allowing users to view their performance in game
"""

class DataViewPanel(tk.Frame):

    # Constructor sets up panel structure and widgets

    def __init__(self,parent):
        
        self.parent = parent
        tk.Frame.__init__(self,parent,padx=10,pady=10)
        self.gameData = None

        self.controlFrame = tk.Frame(self)
        self.graphFrame = tk.Frame(self)

        # Set up title
        self.title = tk.Label(self,text="Data View")
        self.title.grid(row=0,column=0,columnspan=2,sticky="we")

        # Set up sub frames for left side
        self.gameDataFrame = tk.Frame(self.controlFrame,pady=10,padx=10,bg="snow4")
        self.optionGameFrame = tk.Frame(self.controlFrame,pady=10,padx=10,bg="snow4")
        self.comboDataFrame = tk.Frame(self.controlFrame,pady=10,padx=10,bg="snow4")
        self.filterFrame = tk.Frame(self.controlFrame,pady=10,padx=10,bg="snow4")

        # Set up buttons for left side
        self.updateStatsButton = tk.Button(self.controlFrame,text="Update Stats",command=lambda:self.loadData(self.gameData),padx=10,bg="snow2")
        self.returnToMenuButton = tk.Button(self.controlFrame,text="Return To Menu",command=self.returnToMenu,padx=10,bg="snow2")

        # Initialise general game stat objects
        self.generalTitle = tk.Label(self.gameDataFrame,text="General Stats",bg="sienna2")

        self.gamesPlayedVariable = tk.StringVar()
        self.gamesPlayedLabel = tk.Label(self.gameDataFrame,text="Games Played:",padx=8,bg="snow4")
        self.gamesPlayedValueLabel = tk.Label(self.gameDataFrame,textvariable=self.gamesPlayedVariable,width=10,bg="snow4")

        self.highestScoreVariable = tk.StringVar()
        self.highestScoreLabel = tk.Label(self.gameDataFrame,text="Highest Score:",padx=8,bg="snow4")
        self.highestScoreValueLabel = tk.Label(self.gameDataFrame,textvariable=self.highestScoreVariable,width=10,bg="snow4")

        self.averageScoreVariable = tk.StringVar()
        self.averageScoreLabel = tk.Label(self.gameDataFrame,text="Average Score:",padx=8,bg="snow4")
        self.averageScoreValueLabel = tk.Label(self.gameDataFrame,textvariable=self.averageScoreVariable,width=10,bg="snow4")

        # Put objects on grid
        self.generalTitle.grid(row=0,column=0,columnspan=2,sticky="we")
        self.gamesPlayedLabel.grid(row=1,column=0,sticky="e")
        self.gamesPlayedValueLabel.grid(row=1,column=1,sticky="we")
        self.highestScoreLabel.grid(row=2,column=0,sticky="e")
        self.highestScoreValueLabel.grid(row=2,column=1,sticky="we")
        self.averageScoreLabel.grid(row=3,column=0,sticky="e")
        self.averageScoreValueLabel.grid(row=3,column=1,sticky="we")
        
        self.gameDataFrame.grid_columnconfigure(0,weight=1)
        self.gameDataFrame.grid_columnconfigure(1,weight=1)
        self.gameDataFrame.grid(row=0,column=0,sticky="nsew")

        # Initialise option specific game stat objects
        self.optionTitle = tk.Label(self.optionGameFrame,text="Option Stats",bg="sienna2")

        self.gamesPlayedOptionVariable = tk.StringVar()
        self.gamesPlayedOptionLabel = tk.Label(self.optionGameFrame,text="Games Played:",padx=8,bg="snow4")
        self.gamesPlayedOptionValueLabel = tk.Label(self.optionGameFrame,textvariable=self.gamesPlayedOptionVariable,width=10,bg="snow4")

        self.highestScoreOptionVariable = tk.StringVar()
        self.highestScoreOptionLabel = tk.Label(self.optionGameFrame,text="Highest Score:",padx=8,bg="snow4")
        self.highestScoreOptionValueLabel = tk.Label(self.optionGameFrame,textvariable=self.highestScoreOptionVariable,width=10,bg="snow4")

        self.averageScoreOptionVariable = tk.StringVar()
        self.averageScoreOptionLabel = tk.Label(self.optionGameFrame,text="Average Score:",padx=8,bg="snow4")
        self.averageScoreOptionValueLabel = tk.Label(self.optionGameFrame,textvariable=self.averageScoreOptionVariable,width=10,bg="snow4")

        # Put objects on grid
        self.optionTitle.grid(row=0,column=0,columnspan=2,sticky="we")
        self.gamesPlayedOptionLabel.grid(row=1,column=0,sticky="e")
        self.gamesPlayedOptionValueLabel.grid(row=1,column=1,sticky="we")
        self.highestScoreOptionLabel.grid(row=2,column=0,sticky="e")
        self.highestScoreOptionValueLabel.grid(row=2,column=1,sticky="we")
        self.averageScoreOptionLabel.grid(row=3,column=0,sticky="e")
        self.averageScoreOptionValueLabel.grid(row=3,column=1,sticky="we")

        self.optionGameFrame.grid_columnconfigure(0,weight=1)
        self.optionGameFrame.grid_columnconfigure(1,weight=1)
        self.optionGameFrame.grid(row=1,column=0,sticky="nsew")

        # Initialise combo specific stat objects
        self.comboTitle = tk.Label(self.comboDataFrame,text="Combo Stats",bg="dark turquoise")
        dota = Dota.Dota()
        self.comboList = []
        self.comboDict = {}
        for combo in dota.allCombos:
            self.comboList.append(combo.name)
            self.comboDict[combo.name] = combo.id

        self.comboVariable = tk.StringVar()
        self.comboVariable.set(self.comboList[0])
        self.comboSelector = tk.OptionMenu(self.comboDataFrame,self.comboVariable, *self.comboList)
        self.comboSelector.config(width=60)

        self.comboTitle.grid(row=0,column=0,columnspan=2,sticky="we")
        self.comboSelector.grid(row=1,column=0,columnspan=2,sticky="we")

        self.combosPlayedVariable = tk.StringVar()
        self.combosPlayedLabel = tk.Label(self.comboDataFrame,text="Combos Played:",padx=8,bg="snow4")
        self.combosPlayedValueLabel = tk.Label(self.comboDataFrame,textvariable=self.combosPlayedVariable,width=10,bg="snow4")

        self.avgExecutionTimeVariable = tk.StringVar()
        self.avgExecutionTimeLabel = tk.Label(self.comboDataFrame,text="Average Execution Time:",padx=8,bg="snow4")
        self.avgExecutionTimeValueLabel = tk.Label(self.comboDataFrame,textvariable=self.avgExecutionTimeVariable,width=10,bg="snow4")

        self.fastestExecutionTimeVariable = tk.StringVar()
        self.fastestExecutionTimeLabel = tk.Label(self.comboDataFrame,text="Fastest Execution Time:",padx=8,bg="snow4")
        self.fastestExecutionTimeValueLabel = tk.Label(self.comboDataFrame,textvariable=self.fastestExecutionTimeVariable,width=10,bg="snow4")

        # Put objects on grid
        self.combosPlayedLabel.grid(row=2,column=0,sticky="e")
        self.combosPlayedValueLabel.grid(row=2,column=1,sticky="we")
        self.avgExecutionTimeLabel.grid(row=3,column=0,sticky="e")
        self.avgExecutionTimeValueLabel.grid(row=3,column=1,sticky="we")
        self.fastestExecutionTimeLabel.grid(row=4,column=0,sticky="e")
        self.fastestExecutionTimeValueLabel.grid(row=4,column=1,sticky="we")
        self.comboDataFrame.grid_columnconfigure(0,weight=1)
        self.comboDataFrame.grid_columnconfigure(1,weight=1)
        self.comboDataFrame.grid(row=2,column=0,sticky="nsew")

        # Set up checkbox objects for selecting what data to filter
        self.filterTitle = tk.Label(self.filterFrame,text="Stats to Include:",bg="chartreuse2")
        self.checkButtons = {}

        # Keep them in dictionary for easy use
        for option in ("AGHANIMS","OCTARINE","ARCANE_RUNE"):
            self.checkButtons[option] = []
            self.checkButtons[option].append(tk.BooleanVar())
            self.checkButtons[option].append(tk.Checkbutton(self.filterFrame,text=option,variable=self.checkButtons[option][0]))
            self.checkButtons[option][1].config(bg="snow4",activebackground="snow3")
        # Aghanims is True by default as it is most common option
        self.checkButtons["AGHANIMS"][0].set(True)

        # Put objects onto grid
        self.filterTitle.grid(row=0,column=0,columnspan=2,sticky="we")
        self.checkButtons["AGHANIMS"][1].grid(row=1,column=0,columnspan=2,sticky="w")
        self.checkButtons["OCTARINE"][1].grid(row=2,column=0,columnspan=2,sticky="w")
        self.checkButtons["ARCANE_RUNE"][1].grid(row=3,column=0,columnspan=2,sticky="w")
        
        self.filterFrame.grid_columnconfigure(0,weight=1)
        self.filterFrame.grid_columnconfigure(1,weight=1)
        self.filterFrame.grid(row=3,column=0,sticky="nsew")

        self.updateStatsButton.grid(row=4,column=0,sticky="we")
        self.returnToMenuButton.grid(row=5,column=0,sticky="swe")
        self.controlFrame.grid(row=1,column=0,sticky="nsew")

        # Initialise graph objects and required buttons
        self.graphTitle = tk.Label(self.graphFrame,text="Performance")
        
        self.graphCanvas = tk.Canvas(self.graphFrame,width=800,height=800)
        self.graphCanvas.create_rectangle(0,0,800,800,fill="honeydew3",outline="")
        
        # Draw axes and label
        gameAxis = self.graphCanvas.create_line(100,700,700,700,fill="red")
        scoreAxis = self.graphCanvas.create_line(100,100,100,700,fill="red")
        gameLabel = self.graphCanvas.create_text(400,750,text="Game")
        scoreLabel = self.graphCanvas.create_text(20,400,text="Score",angle=90)

        self.gameNumbering = []
        self.scoreLabels = []
        self.scoreLines = []
        self.scorePoints = []

        self.previousTenButton = tk.Button(self.graphFrame,text="Previous 10",command=self.previousTen)
        self.nextTenButton = tk.Button(self.graphFrame,text="Next 10",command=self.nextTen)
        self.recentTenButton = tk.Button(self.graphFrame,text="Recent 10",command=self.recentTen)

        # Put objects onto grid
        self.graphTitle.grid(row=0,column=0,columnspan=3,sticky="nsew")
        self.previousTenButton.grid(row=2,column=0,sticky="nsew")
        self.nextTenButton.grid(row=2,column=1,sticky="nsew")
        self.recentTenButton.grid(row=2,column=2,sticky="nsew")
        self.graphCanvas.grid(row=1,column=0,columnspan=3,sticky="nsew")

        self.graphFrame.grid(row=1,column=1,sticky="nsew")

    # Changes the labels to correctly show stats

    def loadData(self,gameData):
        # Update own instance of data so it can be reused if the update stats is clicked
        self.gameData = gameData

        # Get list of scores of all games for general stats
        self.gameScore = list(map(lambda game:game.score,gameData))

        # Get required options into list so the filter function can be applied to data
        wantedOptions = []
        for option in ("AGHANIMS","ARCANE_RUNE","OCTARINE"):
            if self.checkButtons[option][0].get() == True:
                wantedOptions.append(option)
        optionData = Statistics.filterDataByOptions(gameData,wantedOptions)
        
        # Get list of scores of filtered games for option specific stats
        optionScore = list(map(lambda game:game.score,optionData))

        # Filter option specific stats even further to those that test the required combo and get list of combo times for them
        comboData = Statistics.filterDataByCombo(optionData,int(self.comboDict[self.comboVariable.get()]))
        comboExecution = list(map(lambda combo:combo[1],comboData))

        # Compute the data size, average, and highest/lowest of data size
        self.gamesPlayedVariable.set(str(Statistics.findSize(self.gameScore)))
        self.averageScoreVariable.set(str(Statistics.findAverage(self.gameScore)))
        self.highestScoreVariable.set(str(Statistics.findHighest(self.gameScore)))

        self.gamesPlayedOptionVariable.set(str(Statistics.findSize(optionScore)))
        self.averageScoreOptionVariable.set(str(Statistics.findAverage(optionScore)))
        self.highestScoreOptionVariable.set(str(Statistics.findHighest(optionScore)))

        # Lowest is required because that is what players would want to see
        self.combosPlayedVariable.set(str(Statistics.findSize(comboExecution)))
        self.avgExecutionTimeVariable.set(str(Statistics.findAverage(comboExecution)))
        self.fastestExecutionTimeVariable.set(str(Statistics.findLowest(comboExecution)))

        # Adjust score axis labels
        for label in self.scoreLabels:
            self.graphCanvas.delete(label)

        # Get highest score and find power of 10 for maximum score
        highestScore = Statistics.findHighest(self.gameScore)
        if highestScore == "N/A":
            highestScore = 0
            self.scaleBoundary = 10
        else:
            exponent = math.floor(math.log10(highestScore))
            if exponent == 0:
                self.scaleBoundary = 10
            else:
                normalised = highestScore / (10**exponent)
                self.scaleBoundary = math.ceil(normalised) * (10**exponent)

        for i in range(1,11):
            y = 700 - i * 60
            self.scoreLabels.append(self.graphCanvas.create_text(60,y,text=str(int((self.scaleBoundary*i)/10))))
           
        # Set graph position to the 10th before last
        self.graphPosition = len(self.gameScore) - 10
        if self.graphPosition < 0:
            self.graphPosition = 0
        self.updateGraph(self.gameScore[self.graphPosition:])

    # Update graph values

    def updateGraph(self,data):
        # Change numbering
        for numbering in self.gameNumbering:
            self.graphCanvas.delete(numbering)
        for i in range(1,11):
            x = 100 + 60*i
            self.gameNumbering.append(self.graphCanvas.create_text(x,725,text=str(i+self.graphPosition)))

        # Remove points and lines
        for line in self.scoreLines:
            self.graphCanvas.delete(line)
        for point in self.scorePoints:
            self.graphCanvas.delete(point)

        # Determine size of data so lines and points algorithm can wor properly
        if len(data) >= 10:
            lines = 9
        elif len(data) == 0:
            lines = 0
        else:
            lines = len(data) - 1

        # Max point is the data set to go up to and is used if set is too small
        maxPoint = len(data) if len(data) >= 10 else len(data)
        for i in range(lines):
            point1 = 700 - ((data[-(maxPoint-i)] / self.scaleBoundary) * 600)
            try:
                point2 = 700 - ((data[-(maxPoint-1-i)] / self.scaleBoundary) * 600)
                self.scoreLines.append(self.graphCanvas.create_line(160+60*i,point1,220+60*i,point2))
            except:
                pass

        for i in range(len(data)):
            y = 700 - ((data[-(maxPoint-i)] / self.scaleBoundary) * 600)
            self.scorePoints.append(self.graphCanvas.create_oval((160+60*i)-3,y-3,(160+60*i)+3,y+3,fill="green3"))

    # Go back 10 games

    def previousTen(self):
        # Move position back and if less than 0 set to 0
        self.graphPosition -= 10
        if self.graphPosition <= 0:
            self.graphPosition = 0
        # Get 10 items starting from position
        data = self.gameScore[self.graphPosition:self.graphPosition+10]
        self.updateGraph(data)

    # Same as previousTen() but goes forwards

    def nextTen(self):
        self.graphPosition += 10
        # If reached the end then set to position 10 before last
        if self.graphPosition >= len(self.gameScore) - 10:
            self.graphPosition = len(self.gameScore) - 10
            if self.graphPosition <= 0:
                self.graphPosition = 0
        data = self.gameScore[self.graphPosition:self.graphPosition+10] 
        self.updateGraph(data)

    # Set to most recent ten by changing position to 10 before last

    def recentTen(self):
        self.graphPosition = len(self.gameScore) - 10 if len(self.gameScore) - 10 >= 0 else 0
        data = self.gameScore[self.graphPosition:self.graphPosition+10]
        self.updateGraph(data)

    # Returns to menu, no need to save 

    def returnToMenu(self):
        self.parent.showPanel(MenuPanel)

"""
Class implements Settings Panel that will be in charge of
allowing users to change their default game settings
"""

class SettingsPanel(tk.Frame):

    # Constructor sets up panel structure and widgets

    def __init__(self,parent):

        # Mostly the same as other panel code
        self.parent = parent
        tk.Frame.__init__(self,parent)

        # Current settings is empty prior to logging in and opening settings panel
        self.currentSettings = None

        self.title = tk.Label(self,text="Settings")
        self.controlsFrame = tk.Frame(self)
        self.mechanicsFrame = tk.Frame(self)

        # Settings widgets dictionary allows it to be used alongside the settings dictionary in account
        self.settingsWidgets = {}

        self.controlsLabel = tk.Label(self.controlsFrame,text="Controls")
        self.mechanicsLabel = tk.Label(self.mechanicsFrame,text="Mechanics")
        
        # Settings widgets in both controls and mechanics
        self.characterSettings = []

        self.settingsWidgets["QUAS"] = CharacterSetting(self.controlsFrame,"Quas",self.characterSettings)
        self.settingsWidgets["WEX"] = CharacterSetting(self.controlsFrame,"Wex",self.characterSettings)
        self.settingsWidgets["EXORT"] = CharacterSetting(self.controlsFrame,"Exort",self.characterSettings)
        self.settingsWidgets["INVOKE"] = CharacterSetting(self.controlsFrame,"Invoke",self.characterSettings)
        self.settingsWidgets["SPELL_1"] = CharacterSetting(self.controlsFrame,"Spell 1",self.characterSettings)
        self.settingsWidgets["SPELL_2"] = CharacterSetting(self.controlsFrame,"Spell 2",self.characterSettings)
        self.settingsWidgets["QUICKCAST"] = BinaryRadioSetting(self.controlsFrame,"Quickcast","On","Off")
        self.settingsWidgets["AGHANIMS"] = BinaryRadioSetting(self.mechanicsFrame,"Aghanims","On","Off")
        self.settingsWidgets["OCTARINE"] = BinaryRadioSetting(self.mechanicsFrame,"Octarine","On","Off")
        self.settingsWidgets["ARCANE_RUNE"] = BinaryRadioSetting(self.mechanicsFrame,"Arcane Rune","On","Off")

        self.characterSettings.append(self.settingsWidgets["QUAS"])
        self.characterSettings.append(self.settingsWidgets["WEX"])
        self.characterSettings.append(self.settingsWidgets["EXORT"])
        self.characterSettings.append(self.settingsWidgets["INVOKE"])
        self.characterSettings.append(self.settingsWidgets["SPELL_1"])
        self.characterSettings.append(self.settingsWidgets["SPELL_2"])

        self.saveButton = tk.Button(self.controlsFrame,text="Save Settings",command=self.saveSettings,bg="thistle3")
        self.menuButton = tk.Button(self.controlsFrame,text="Return to Menu",command=self.returnMenu,bg="thistle4")

        # Code actually places the widgets onto the grid
        self.title.grid(row=0,column=0,columnspan=2,sticky="nswe")

        self.controlsFrame.grid(row=1,column=0,padx=5,pady=5,sticky="nsew")
        self.controlsFrame.grid_columnconfigure(0,weight=1)
        self.mechanicsFrame.grid(row=1,column=1,padx=15,pady=5,sticky="nsew")
        self.mechanicsFrame.grid_columnconfigure(0,weight=1)

        self.controlsLabel.grid(row=0,column=0,sticky="we",pady=5,padx=5)
        self.mechanicsLabel.grid(row=0,column=0,sticky="we",pady=5,padx=5)

        self.settingsWidgets["QUAS"].grid(row=1,column=0,sticky="e",pady=5)
        self.settingsWidgets["WEX"].grid(row=2,column=0,sticky="e",pady=5)
        self.settingsWidgets["EXORT"].grid(row=3,column=0,sticky="e",pady=5)
        self.settingsWidgets["INVOKE"].grid(row=4,column=0,sticky="e",pady=5)
        self.settingsWidgets["SPELL_1"].grid(row=5,column=0,sticky="e",pady=5)
        self.settingsWidgets["SPELL_2"].grid(row=6,column=0,sticky="e",pady=5)
        self.settingsWidgets["QUICKCAST"].grid(row=7,column=0,sticky="e",pady=5)
        self.settingsWidgets["AGHANIMS"].grid(row=1,column=0,sticky="e",pady=5)
        self.settingsWidgets["OCTARINE"].grid(row=2,column=0,sticky="e",pady=5)
        self.settingsWidgets["ARCANE_RUNE"].grid(row=3,column=0,sticky="e",pady=5)

        self.saveButton.grid(row=8,column=0,sticky="nsew",pady=5,padx=5)
        self.menuButton.grid(row=9,column=0,sticky="nsew",pady=5,padx=5)

        self.grid(row=0,column=0,rowspan=2,columnspan=2,sticky="nsew")

    # Function gets settings from current account object

    def loadSettings(self,settings):
        self.currentSettings = settings

        for setting in self.currentSettings:
            self.settingsWidgets[setting].property.set(self.currentSettings[setting])

        for setting in self.currentSettings:
            if self.settingsWidgets[setting].__class__.__name__ == "CharacterSetting":
                self.settingsWidgets[setting].property.trace("w",self.settingsWidgets[setting].limitCharacter)

    # Called when menu button is pressed

    def returnMenu(self):

        # If confirmed, save and go to menu
        if messagebox.askyesno("Return to Menu","Save current settings?"):
            if self.saveSettings():
                self.parent.showPanel(MenuPanel)
        else:
            self.parent.showPanel(MenuPanel)

    # For each setting, assign widgets' values to account's settings

    def saveSettings(self):
        
        # Check all settings are valid before any saving transaction can occur
        validSettings = True
        for setting in self.characterSettings:
            if setting.valid == False:
                validSettings = False
                break
        
        if not validSettings:
            messagebox.showinfo("Saving failed.","One or more settings are invalid.")
            return False

        for setting in self.currentSettings:
            # If invalid, stop saving and 
            settingValue = self.settingsWidgets[setting].property.get()

            # If Boolean, set to string 1 or 0, to ensure safe saving and reparsing
            if settingValue == True:
                self.currentSettings[setting] = 1
            elif settingValue == False:
                self.currentSettings[setting] = 0
            else:
                self.currentSettings[setting] = self.settingsWidgets[setting].property.get()
            
        self.parent.accountManager.changeSettings(self.currentSettings)
        messagebox.showinfo("Success","Settings are saved.")
        return True

"""
Encapsulates a set of labels and radio buttons for representing a true/false setting
"""

class BinaryRadioSetting(tk.Frame):

    # Initialisation code is standard

    def __init__(self,parent,property,option1,option2,default=True):
        self.parent = parent
        tk.Frame.__init__(self,parent)

        self.property = tk.BooleanVar()
        self.property.set(default)

        self.descriptionLabel = tk.Label(self,text=property+":")
        self.radioOne = tk.Radiobutton(self,text=option1,variable=self.property,value=True)
        self.radioTwo = tk.Radiobutton(self,text=option2,variable=self.property,value=False)
        
        self.descriptionLabel.grid(row=0,column=0,sticky="nswe")
        self.radioOne.grid(row=0,column=1,sticky="we")
        self.radioTwo.grid(row=0,column=2,sticky="we")
        
        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
        self.grid_columnconfigure(2,weight=1)

"""
Encapsulates a label and entry for representing a character/key setting
"""
class CharacterSetting(tk.Frame):

    # Initialisation code is standard except for the character limit

    def __init__(self,parent,property,otherSettings,default=None):
        self.parent = parent
        tk.Frame.__init__(self,parent)
        self.others = otherSettings

        # Trace the variable so that any time it changes, the limit function is called
        self.property = tk.StringVar()

        self.descriptionLabel = tk.Label(self,text=property+":")
        self.characterEntry = tk.Entry(self,textvariable=self.property,width=7,justify="center",bg="LightBlue3")
        self.descriptionLabel.grid(row=0,column=0,sticky="w")
        self.characterEntry.grid(row=0,column=1,sticky="ens")

        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)

        self.property.set(default)
        self.valid = True

    # Test if length of the entry variable is greater than 1
    # If so, set string to latest inputted character

    def limitCharacter(self,*args):
        value = self.property.get()

        # Keep the value to the last character entered and turn to lowercase
        if len(value) > 1:
            value = value[1:]
        self.property.set(value.lower())

        # Check for special invalid characters
        if value == "" or value == " ":
            self.valid = False
            self.characterEntry.config(bg="red")
        # Check for same character
        else:
            # Group settings into whether they share characters
            settingSets = {}
            for setting in self.others:
                otherValue = setting.property.get()
                if otherValue in settingSets:
                    settingSets[otherValue].append(setting)
                else:
                    settingSets[otherValue] = [setting]
            # Go through the sets and assign valid/invalid depending on size of set
            for settingCharacter in settingSets:
                if len(settingSets[settingCharacter]) > 1:
                    for setting in settingSets[settingCharacter]:
                        setting.valid = False
                        setting.characterEntry.config(bg="red")
                else:
                    settingSets[settingCharacter][0].valid = True
                    settingSets[settingCharacter][0].characterEntry.config(bg="LightBlue3")

