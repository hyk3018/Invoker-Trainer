import pygame, sys
from Dota import Dota
from tkinter import messagebox
import math, random

keyToEventMap = {"1":pygame.K_1,"2":pygame.K_2,"3":pygame.K_3,"4":pygame.K_4,"5":pygame.K_5,"6":pygame.K_6,"7":pygame.K_7,
                 "8":pygame.K_8,"9":pygame.K_9,"0":pygame.K_0,"a":pygame.K_a,"b":pygame.K_b,"c":pygame.K_c,"d":pygame.K_d,
                 "e":pygame.K_e,"f":pygame.K_f,"g":pygame.K_g,"h":pygame.K_h,"i":pygame.K_i,"j":pygame.K_j,"k":pygame.K_k,
                 "l":pygame.K_l,"m":pygame.K_l,"n":pygame.K_n,"o":pygame.K_o,"p":pygame.K_p,"q":pygame.K_q,"r":pygame.K_r,
                 "s":pygame.K_s,"t":pygame.K_t,"u":pygame.K_u,"v":pygame.K_v,"w":pygame.K_w,"x":pygame.K_x,"y":pygame.K_y,
                 "z":pygame.K_z}

spellStringMap = {"qqq":"cs","qqw":"gw","qqe":"iw","www":"emp","qww":"tor","wwe":"ala","eee":"sun","qee":"for","wee":"chm",
                  "qwe":"dfb"}

alphabet = {"q":1,"w":2,"e":3}

# Function used by multiple classes to load images

def loadImage(name,transparent=False):
    # First try to get the image and if it fails, the program cannot run.
    # Saving is unnecessary as resources have to be successfully loaded
    # before the game can even be played.
    try:
        image = pygame.image.load(r"assets\\" + name + ".png")
    except pygame.error:
        messagebox.showinfo("Failed to load.","Can't locate image resources.")
        sys.exit()

    # Convert image to correct pixel format, function depends on image transparency
    if transparent:
        image = image.convert_alpha()
    else:
        image = image.convert()
    return image, image.get_rect()

"""
Implement's Pygame program
"""

class InvokerGame:

    # Set up main variables and start main loop

    def __init__(self,mainApp,returnFunction,mechanics):

        pygame.init()
        pygame.font.init()
        self.accountManager = mainApp.accountManager
        self.root = mainApp.parent
        self.endGame = returnFunction
        self.mechanics = mechanics

        self.screenDimensions = (800,600)
        self.running = True

        # Create screen (starts the program in effect)
        self.screen = pygame.display.set_mode(self.screenDimensions,0,32)
        pygame.display.set_caption("Invoker Trainer")

        self.states = {}
        self.states[StartMenu]= StartMenu(self,self.accountManager.currentAccount.settings)
        self.states[Main] = Main(self,self.mechanics)
        self.states[Paused] = Paused(self)
        self.currentState = self.states[StartMenu]

        self.mainLoop()

    # Changes state

    def changeState(self,state,*args):
        self.currentState = self.states[state]
        if not len(args) == 0:
            self.currentState.changeState(args[0])
        if state == Paused:
            self.currentState.backgroundDrawn = False
        return

    # Makes use of tkinter's after() method to effectively run a loop

    def mainLoop(self):
        
        # Get the events and use the current state to handle them
        events = pygame.event.get()
        self.currentState.handleEvents(events)

        # Handle quit event and if quit, set running to false so the return function can be called
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                break

        # Get current state to render and update
        self.currentState.update()
        if self.running:
            self.currentState.render(surface = self.screen)
        else:
            if self.currentState == self.states[Main]:
                self.saveData()
            pygame.display.quit()
            pygame.font.quit()
            pygame.quit()
            self.endGame()
            return

        pygame.display.flip()

        # Only loop if still running
        if not self.running:
            
            pygame.display.quit()
            pygame.font.quit()
            pygame.quit()
            self.endGame()
        else:
            self.root.after(17,self.mainLoop)
    
    def saveData(self):
        settingsUsed = []
        if self.currentState.settings["AGHANIMS"] == 1:
            settingsUsed.append("AGHANIMS")
        if self.currentState.settings["ARCANE_RUNE"] == 1:
            settingsUsed.append("ARCANE_RUNE")
        if self.currentState.settings["OCTARINE"] == 1:
            settingsUsed.append("OCTARINE")
        if self.currentState.settings["QUICKCAST"] == 1:
            settingsUsed.append("QUICKCAST")
                
        self.accountManager.addGameData(self.currentState.score,settingsUsed,self.currentState.comboExecutionTimes)
        self.accountManager.saveGameData()

"""
Game State is a generic class that all state classes inherit from
"""

class GameState():

    def __init__(self,gameObject):
        self.game = gameObject

        self.sprites = pygame.sprite.LayeredUpdates()

        self.internalStates = {"INITIALISATION":"init"}
        self.internalState = self.internalStates["INITIALISATION"]
        self.background = None

    def handleEvents(self,**args):
        return

    def update(self,**args):
        return

    def render(self,**kwargs):
        kwargs["surface"].blit(self.background,(0,0))
        self.sprites.draw(kwargs["surface"])
        return
    
    def changeState(self,state):
        self.internalState = self.internalStates[state]

"""
Start State
"""

class StartMenu(GameState):

    def __init__(self,gameObject,settings):

        self.currentSettings = dict(settings)


        # Initialise state by instantiating sprites and background, put into appropriate groups
        GameState.__init__(self,gameObject)
        self.background = pygame.sprite.Sprite()
        self.background, self.backgroundRect = loadImage("start_panel")

        self.sprites = pygame.sprite.Group()

        # Group button objects efficiently
        self.buttons = {}
        self.buttons["AGHANIMS"] = RadioButton(320,110)
        self.buttons["OCTARINE"] = RadioButton(320,148)
        self.buttons["ARCANE_RUNE"] = RadioButton(320,186)
        self.buttons["START"] = Button(480,420,["start_button"],self.startGame)

        # Add buttons to sprite group so their update, render, etc... can be called each game loop
        for buttonName in self.buttons:
            self.sprites.add(self.buttons[buttonName])

        # Set button values according to current account's settings

        self.buttons["AGHANIMS"].changeOption(settings["AGHANIMS"])
        self.buttons["OCTARINE"].changeOption(settings["OCTARINE"])
        self.buttons["ARCANE_RUNE"].changeOption(settings["ARCANE_RUNE"])

    # Check if a button has been clicked

    def handleEvents(self,events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                mousePos = pygame.mouse.get_pos()
                for sprite in self.sprites:
                    if sprite.rect.collidepoint(mousePos):
                        try:
                            sprite.onClick()
                        except:
                            pass

    # Function is called when start game is clicked, changes the game state
    # Updates settings to any change

    def startGame(self):
        self.currentSettings["AGHANIMS"] = int(self.buttons["AGHANIMS"].state)
        self.currentSettings["OCTARINE"] = int(self.buttons["OCTARINE"].state)
        self.currentSettings["ARCANE_RUNE"] = int(self.buttons["ARCANE_RUNE"].state)
        self.game.changeState(Main,"INITIALISATION")
        self.game.currentState.changeSettings(self.currentSettings)

"""
Main Game
"""

class Main(GameState):

    # Initialisation, setting up background and mechanics

    def __init__(self,gameObject,mechanics):
        # Set up states and key variables
        GameState.__init__(self,gameObject)
        self.background = pygame.sprite.Sprite()
        self.background, self.backgroundRect = loadImage("background")
        self.dota = mechanics

        self.internalStates["MAIN"] = "main"
        self.internalStates["START_COMBO"] = "sc"

        self.pausedTime = None

        # Set up score and timer
        self.score = 0
        self.comboExecutionTimes = []
        self.scoreSprite = Text(30,30,"Score : " + str(self.score),(255,255,255))
        self.sprites.add(self.scoreSprite,layer=1)

        self.timerBackground = GameObject(30,60,["bar_holder"],True)
        self.timer = TimerObject(35,65,[self.endGame])
        self.sprites.add(self.timerBackground,layer=1)
        self.sprites.add(self.timer,layer=2)

        self.comboNameSprite = Text(0,0,"Current Combo: ",(255,255,255))
        self.comboNameSprite.centralise(x = 400,y = 105)
        self.sprites.add(self.comboNameSprite)

        # Instantiate combo objects
        self.coldSnapComboSprite = GameObject(0,0,["cold_snap_icon"],True)
        self.ghostWalkComboSprite = GameObject(0,0,["ghost_walk_icon"],True)
        self.iceWallComboSprite = GameObject(0,0,["ice_wall_icon"],True)
        self.empComboSprite = GameObject(0,0,["emp_icon"],True)
        self.tornadoComboSprite = GameObject(0,0,["tornado_icon"],True)
        self.alacrityTargetComboSprite = GameObject(0,0,["alacrity_target_icon"],True)
        self.alacritiySelfComboSprite = GameObject(0,0,["alacrity_self_icon"],True)
        self.sunStrikeComboSprite = GameObject(0,0,["sun_strike_icon"],True)
        self.chaosMeteorComboSprite = GameObject(0,0,["chaos_meteor_icon"],True)
        self.forgedSpiritComboSprite = GameObject(0,0,["forged_spirit_icon"],True)
        self.deafeningBlastComboSprite = GameObject(0,0,["deafening_blast_icon"],True)

        self.comboSprites = {"cs":self.coldSnapComboSprite,"gw":self.ghostWalkComboSprite,"iw":self.iceWallComboSprite,
                             "emp":self.empComboSprite,"tor":self.tornadoComboSprite,"als":self.alacritiySelfComboSprite,
                             "ala":self.alacrityTargetComboSprite,"sun":self.sunStrikeComboSprite,"for":self.forgedSpiritComboSprite,
                             "chm":self.chaosMeteorComboSprite,"dfb":self.deafeningBlastComboSprite}

        self.comboArrow = GameObject(0,0,["arrow"],True)
        self.sprites.add(self.comboArrow)

        # Resize the combo sprites
        for sprite in self.comboSprites:
            self.comboSprites[sprite].resize(70,70)

        # Instantiate spell objects
        self.orbQueueObject = OrbQueueObject(129,250,self.sprites)
        self.invokeSpellSprite = GameObject(543,250,["invoke_icon","invoke_cd_icon"],True)
        self.spellQueueObject = SpellQueue(267,400,self.sprites)

        self.sprites.add(self.invokeSpellSprite,layer=2)

        self.orbQueue = []

    # Used when main state starts to ensure settings are correct and up to date

    def changeSettings(self,newSettings):
        self.settings = newSettings

    # Update

    def update(self):
        # Initial state gets the time funciton for entire game and starts countdown
        if self.internalState == "init":
            self.startTime = pygame.time.get_ticks()
            # Reset the score and combo data at start of the game
            self.score = 0
            self.comboExecutionTimes = []
            self.scoreSprite.changeText("Score : " + str(self.score))

            # Get the time function for the game and commence the start of the first combo
            self.timeFunction = self.getTimeFunction()
            self.game.changeState(Paused,"CD_START")

            # Change internal state so game starts when countdown finishes
            self.changeState("START_COMBO")
            self.render(surface = self.game.screen)

        # Get combo start time and combo and start main combo routine
        elif self.internalState == "sc":
            self.startCombo()
            self.changeState("MAIN")

        # Wait for input and change combos done / respond
        elif self.internalState == "main":
            if pygame.time.get_ticks() - self.lastInvokePressed >= self.invokeCooldown:
                self.invokeSpellSprite.changeSprite("invoke_icon")
            else:
                self.invokeSpellSprite.changeSprite("invoke_cd_icon")
                image = self.invokeSpellSprite.images["invoke_cd_icon"][0]
                self.game.screen.blit(image,self.invokeSpellSprite.rect)
                pygame.display.flip()
            if self.actionQueue == []:
                self.score += 1
                timeTaken = round((pygame.time.get_ticks()-self.comboStartTime)/1000,2)
                self.comboExecutionTimes.append([self.currentCombo.id,timeTaken])
                self.scoreSprite.changeText("Score : " + str(self.score))
                self.startCombo()
            self.sprites.update()
            return

    # Handle input
    def handleEvents(self,events):
        for event in events:
            if self.internalState == "main":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.game.changeState(Paused,"PAUSED_S")
                        self.pausedTime = pygame.time.get_ticks()
                    # If any of the 3 orb keys then add the corresponding character to queue and if queue full then dequeue before adding
                    elif event.key == keyToEventMap[self.settings["QUAS"]]:
                        self.orbQueue.append("q")
                        self.orbQueueObject.addOrb("q")
                        if len(self.orbQueue) > 3:
                            self.orbQueue = self.orbQueue[1:]
                    elif event.key == keyToEventMap[self.settings["WEX"]]:
                        self.orbQueue.append("w")
                        self.orbQueueObject.addOrb("w")
                        if len(self.orbQueue) > 3:
                            self.orbQueue = self.orbQueue[1:]
                    elif event.key == keyToEventMap[self.settings["EXORT"]]:
                        self.orbQueue.append("e")
                        self.orbQueueObject.addOrb("e")
                        if len(self.orbQueue) > 3:
                            self.orbQueue = self.orbQueue[1:]

                    # Check if spell casted is correct
                    elif event.key == keyToEventMap[self.settings["SPELL_1"]]:
                        if self.spellQueueObject.spells[0] == self.actionQueue[0] or (self.spellQueueObject.spells[0] == "ala"
                            and (self.actionQueue[0] == "ala" or self.actionQueue[0] == "als")):

                            # Check if the spell is completed
                            if self.actionQueue[0] == "als" and self.actionQueue[1] != "als" and self.actionQueue[1] != "click":
                                self.comboArrow.move(self.comboArrow.rect.x + 74,122 + 80)
                            elif self.actionQueue[0] == "for" or self.actionQueue[0] == "iw":
                                self.comboArrow.move(self.comboArrow.rect.x + 74,122 + 80)
                            self.actionQueue = self.actionQueue[1:]
                        else:
                            self.endGame()
                    elif event.key == keyToEventMap[self.settings["SPELL_2"]]:
                        if self.spellQueueObject.spells[1] == self.actionQueue[0] or (self.spellQueueObject.spells[1] == "ala"
                            and (self.actionQueue[0] == "ala" or self.actionQueue[0] == "als")):

                            # Check if the spell is completed
                            if self.actionQueue[0] == "als" and self.actionQueue[1] != "als" and self.actionQueue[1] != "click":
                                self.comboArrow.move(self.comboArrow.rect.x + 74,122 + 80)
                            elif self.actionQueue[0] == "for" or self.actionQueue[0] == "iw":
                                self.comboArrow.move(self.comboArrow.rect.x + 74,122 + 80)
                            self.actionQueue = self.actionQueue[1:]
                        else:
                            self.endGame()

                    # Check invoke is off cooldown and if so then invoke spell in queue
                    elif event.key == keyToEventMap[self.settings["INVOKE"]]:
                        if pygame.time.get_ticks() - self.lastInvokePressed >= self.invokeCooldown:
                            self.invoke()
                        break
                # If click is correct, remove it from action queue
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.actionQueue[0] == "click":
                        self.comboArrow.move(self.comboArrow.rect.x + 74,122 + 80)
                        self.actionQueue = self.actionQueue[1:]
        return
    
    # Called when a new combo starts (could be start of game or when one combo has been completed)

    def startCombo(self):
        self.getCombo()
        self.timeGiven = self.timeFunction(pygame.time.get_ticks() - self.startTime,[2,4,34,4,3,3,3])
        self.timer.setTime(self.timeGiven)
        self.comboStartTime = pygame.time.get_ticks()
        self.lastInvokePressed = pygame.time.get_ticks() - self.invokeCooldown

        # Instantiate spell objects
        self.orbQueueObject = OrbQueueObject(129,250,self.sprites)
        self.spellQueueObject = SpellQueue(267,400,self.sprites)

    # Outputs list of moves in order

    def getCombo(self):
        # Find time passed to determine what kind of spells can be used
        timePassed = pygame.time.get_ticks() - self.startTime

        allowedCombos = self.dota.activeCombos["early"]
        if timePassed >= 20000:
            allowedCombos += self.dota.activeCombos["mid"]
        if timePassed >= 40000:
            allowedCombos += self.dota.activeCombos["late"]

        # Choose combo from list and update the text
        self.currentCombo = random.choice(allowedCombos)
        self.comboNameSprite.changeText("Current Combo : " + self.currentCombo.name)
        self.comboNameSprite.centralise(x = 400,y = None)

        # Show the correct spells and align them correctly
        for combo in self.comboSprites:
            self.comboSprites[combo].remove(self.sprites)

        for i in range(len(self.currentCombo.spells)):
            self.comboSprites[self.currentCombo.spells[i]].move((400-(74 * len(self.currentCombo.spells))/2 + i*72),122)
            self.sprites.add(self.comboSprites[self.currentCombo.spells[i]])

        # Reset arrow position
        self.comboArrow.move(400-(74 * len(self.currentCombo.spells))/2 +25,122 + 80)

        # From combo, get list of actions required
        self.actionQueue = []
        for spell in self.currentCombo.spells:
            spellSequence = self.dota.spells[spell].castSequence

            # Depending on quickcast and spell type, remove the spell cast confirmation actions (last actions)
            if self.game.accountManager.currentAccount.settings["QUICKCAST"] == True:
                if len(spellSequence) > 1:
                    self.actionQueue += spellSequence[:-1]
            else:
                self.actionQueue += spellSequence
            

    # Function returns a randomised function used throughout an entire game

    def getTimeFunction(self):
        
        amplifier = random.randint(1000,2000)/1000
        x_positioning = math.pi / 2
        frequency = random.randint(500,1000)/1000

        def timeFunction(t,combo):

            # Time variance (changes every game)
            time = (amplifier * math.sin((frequency * t) + x_positioning)**2) / (t + x_positioning) + random.randint(200,500)/1000
            # Add constant time depending on combo length and settings
            cooldown = None
            
            # Set cooldown to a constant depending on whether Aghanims is selected
            if self.settings["AGHANIMS"] == 1:
                cooldown = self.dota.absoluteCD["aghs"].cdValue
            else:
                cooldown = self.dota.absoluteCD["no_aghs"].cdValue

            # Reduce the cooldown based on percentage multipliers by other items
            cooldownReductionPercentage = 1
            if self.settings["OCTARINE"] == 1:
                cooldownReductionPercentage *= (self.dota.percentageCD["oct"].cdValue/100) 
            if self.settings["ARCANE_RUNE"] == 1:
                cooldownReductionPercentage *= (self.dota.percentageCD["arc"].cdValue/100)
            cooldown *= cooldownReductionPercentage

            # Add time according to cooldown, proportional to length of combo
            time += (cooldown + 0.2) * len(combo)

            self.invokeCooldown = cooldown * 1000

            return time * 1000

        return timeFunction

    # Handles combo press

    def invoke(self):
        self.orbQueue = list(sorted(self.orbQueue,key=lambda word: [alphabet.get(c, ord(c)) for c in word]))
        spellString = self.orbQueue[0] + self.orbQueue[1] + self.orbQueue[2]

        invokedSpell = spellStringMap[spellString]

        if self.actionQueue[0] == invokedSpell or (invokedSpell == "ala" and (self.actionQueue[0] == "als" or self.actionQueue[0] == "ala")):
            self.spellQueueObject.addSpell(invokedSpell)
            self.lastInvokePressed = pygame.time.get_ticks()
        else:
            self.endGame()
            pass

    def endGame(self):
        self.game.saveData()
        self.game.changeState(Paused,"END_S")
        

"""
Paused
"""

class Paused(GameState):

    def __init__(self,gameObject):
        GameState.__init__(self,gameObject)

        # Create transulcent surface
        self.background = pygame.Surface((800,600),pygame.SRCALPHA)
        self.background.fill((26, 35, 48,200))

        # Set up internal states, more than typical game state due to transitions
        self.internalStates["CD_START"] = "cds"
        self.internalStates["COUNTDOWN"] = "cd"
        self.internalStates["PAUSED_S"] = "pausedStart"
        self.internalStates["PAUSED"] = "paused"
        self.internalStates["END_S"] = "endStart"
        self.internalStates["END"] = "end"

        # Flag helps rendering conrrectly
        self.backgroundDrawn = None

        mainBackground = GameObject(200,150,["pause_or_end"],False)

        self.sprites.add(mainBackground,layer=1)

    # Only draw translucent background if it is not drawn already to ensure the opacity is retained

    def render(self,**kwargs):
        if not self.backgroundDrawn:  
            kwargs["surface"].blit(self.background,(0,0))
            self.backgroundDrawn = True
        self.sprites.draw(kwargs["surface"])
        return

    # Update the counter if on cooldown, or set up text objects if in transition

    def update(self):
        if self.internalState == "cds":
            countdown = Countdown(350,250,3,self.returnToGame)
            self.sprites.add(countdown,layer=2)
            self.changeState("COUNTDOWN")
        elif self.internalState == "cd":
            self.sprites.update()
        elif self.internalState == "pausedStart":
            paused = Text(0,0,"Paused",(255,255,255))
            paused.centralise(x=400,y=300)
            self.sprites.add(paused,layer=2)
            self.changeState("PAUSED")
        elif self.internalState == "endStart":
            endGame = Text(0,0,"Game Over",(255,255,255))
            endGame.centralise(x=400,y=200)

            scoreString = "Score : " + str(self.game.states[Main].score)
            score = Text(0,0,scoreString,(255,255,255))
            score.centralise(x=400,y=250)
            
            restartButton = Button(310,350,["restart"],self.restartGame)
            closeButton = Button(420,350,["close"],self.closeGame)

            self.sprites.add(endGame,layer=2)
            self.sprites.add(score,layer=2)
            self.sprites.add(restartButton,layer=2)
            self.sprites.add(closeButton,layer=2)

            self.changeState("END")

    # If in paused state, handle the unpause event

    def handleEvents(self,events):
        if self.internalState == "paused":
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Clear the state and change to start of countdown
                        self.sprites.remove_sprites_of_layer(2)
                        self.changeState("CD_START")
        elif self.internalState == "end":
            for event in events:
                if event.type == pygame.MOUSEBUTTONUP:
                    mousePos = pygame.mouse.get_pos()
                    for sprite in self.sprites:
                        if sprite.rect.collidepoint(mousePos):
                            try:
                                sprite.onClick()
                            except:
                                pass
        return
    
    # Passed to countdown object so it can be called to exit paused status

    def returnToGame(self):
        # Clear the state and change to main state, adding paused time if necessary
        self.sprites.remove_sprites_of_layer(2)
        self.game.changeState(Main)
        if self.game.states[Main].pausedTime != None:
            self.game.states[Main].timer.addPause(pygame.time.get_ticks() - self.game.states[Main].pausedTime)

    # Clean up objects and quit pygame
    def closeGame(self):
        self.sprites.remove_sprites_of_layer(2)
        pygame.display.quit()
        pygame.font.quit()
        pygame.quit()
        self.game.running = False
        self.game.endGame()

    # Clean up objects and go back to start menu state
    def restartGame(self):
        self.sprites.remove_sprites_of_layer(2)
        self.game.changeState(StartMenu)

"""
Spell Queue
"""

class SpellQueue:

    def __init__(self,x,y,sprites):
        self.full = False
        self.spellNames = {"n":"empty_spell","cs":"cold_snap_icon","gw":"ghost_walk_icon","iw":"ice_wall_icon","emp":"emp_icon",
                           "tor":"tornado_icon","ala":"alacrity_icon","sun":"sun_strike_icon","chm":"chaos_meteor_icon",
                           "for":"forged_spirit_icon","dfb":"deafening_blast_icon"}
        self.spells = ["n","n"]
        self.spellOne = GameObject(x,y,list(self.spellNames.values()),True)
        self.spellTwo = GameObject(x+138,y,list(self.spellNames.values()),True)
        sprites.add(self.spellOne)
        sprites.add(self.spellTwo)

    def addSpell(self,spellName):
        if self.full == True:
            self.spells = self.spells[1:]
            self.spells.append(spellName)
        else:
            for i in range(2):
                if self.spells[i] == "n":
                    self.spells[i] = spellName
                    if i == 1:
                        self.full = True
                    break

        self.spellOne.changeSprite(self.spellNames[self.spells[0]])
        self.spellTwo.changeSprite(self.spellNames[self.spells[1]])

"""
Generic Game Object
"""

class GameObject(pygame.sprite.Sprite):

    def __init__(self,x,y,imageNames,alpha):
        pygame.sprite.Sprite.__init__(self)

        # Set up images depending on the image name(s) given
        if len(imageNames) == 1:
            self.image, self.rect = loadImage(imageNames[0],alpha)
        else:
            self.images = {}
            for name in imageNames:
                self.images[name] = loadImage(name,alpha)
            self.image, self.rect = self.images[imageNames[0]][0], self.images[imageNames[0]][1]
        self.rect.move_ip(x,y)

    # Uses name to access dictionary and change self.image

    def changeSprite(self,name):
        self.image = self.images[name][0]

    # Changes the rect and image to given dimensions

    def resize(self,newWidth,newHeight):
        self.rect.width = newWidth
        self.rect.height = newHeight
        self.image = pygame.transform.scale(self.image,(self.rect.width,self.rect.height))

    def move(self,x,y):
        self.rect.move_ip((x-self.rect.x),(y-self.rect.y))    

"""
Generic Text Object
"""

class Text(pygame.sprite.Sprite):

    # Set up the standard font and render the correct text

    def __init__(self,x,y,text,colour):
        self.colour = colour
        pygame.sprite.Sprite.__init__(self)      
        self.mainFont = pygame.font.SysFont("Avant Garde",30)
        self.image = self.mainFont.render(text,True,colour)
        self.rect = self.image.get_rect()

        self.rect.move_ip(x,y)

    # Changes the text and also colour

    def changeText(self,newText,colour=None):
        self.image = self.mainFont.render(newText,True,self.colour if colour == None else colour)
        self.rect = self.image.get_rect().move(self.rect.x,self.rect.y)

    # Moves image so it is centralised
     
    def centralise(self,**kwargs):
        if kwargs["x"] != None:
            self.move((kwargs["x"] - (self.rect.width / 2)),self.rect.y)
        if kwargs["y"] != None:
            self.move(self.rect.x,(kwargs["y"] - (self.rect.height / 2)))

    def move(self,x,y):
        self.rect.move_ip((x-self.rect.x),(y-self.rect.y))

"""
Orb Queue
"""

class OrbQueueObject:

    # Set queue to initially be empty

    def __init__(self,x,y,sprites):
        self.full = False
        self.orbQueue = ["n","n","n"]
        self.orbNames = {"n":"empty_spell","q":"quas_icon","w":"wex_icon","e":"exort_icon"}
        self.orbOne = GameObject(x,y,["empty_spell","quas_icon","wex_icon","exort_icon"],True)
        self.orbTwo = GameObject(x+138,y,["empty_spell","quas_icon","wex_icon","exort_icon"],True)
        self.orbThree = GameObject(x+276,y,["empty_spell","quas_icon","wex_icon","exort_icon"],True)
        sprites.add(self.orbOne,layer=2)
        sprites.add(self.orbTwo,layer=2)
        sprites.add(self.orbThree,layer=2)

    # When adding orb, add according to fullness

    def addOrb(self,orb):
        if self.full == True:
            # If full, get rid of first item in queue and add latest item
            self.orbQueue = self.orbQueue[1:]
            self.orbQueue.append(orb)
        else:
            for i in range(3):
                if self.orbQueue[i] == "n":
                    self.orbQueue[i] = orb
                    if i == 2:
                        self.full = True
                    break

        # Visually update orbs
        self.orbOne.changeSprite(self.orbNames[self.orbQueue[0]])
        self.orbTwo.changeSprite(self.orbNames[self.orbQueue[1]])
        self.orbThree.changeSprite(self.orbNames[self.orbQueue[2]])



"""
Timer Object
"""

class TimerObject(GameObject):

    def __init__(self,x,y,stopFunction):
        GameObject.__init__(self,x,y,["time_bar"],True)
        self.trueWidth = 730
        self.rect.width = self.trueWidth
        self.image = pygame.transform.scale(self.image,(self.rect.width,self.rect.height))
        self.stop = stopFunction[0]

    def update(self):
        nowtime = pygame.time.get_ticks()
        self.current = self.total - (pygame.time.get_ticks() - self.startTime)
        self.rect.width = (self.current / self.total) * self.trueWidth

        if self.rect.width <= 0:
            self.stop()
            return
        self.image = pygame.transform.scale(self.image,(self.rect.width,self.rect.height))

    def setTime(self,time):
        self.total = time
        self.current = time
        self.startTime = pygame.time.get_ticks()

    def addPause(self,addedTime):
        self.startTime += addedTime

""" 
Countdown Sprite
"""

class Countdown(pygame.sprite.Sprite):

    # Set up the number of milliseconds remaining and also set up images so they can be referenced by second number

    def __init__(self,x,y,timerLength,endFunction):
        pygame.sprite.Sprite.__init__(self)

        self.end = endFunction
        self.remainingTime = timerLength * 1000
        self.clock = pygame.time.Clock()
        self.clock.tick()

        self.images = []
        for i in range(timerLength):
            self.images.append(loadImage("cd" + str(i+1),True))

        self.currentSprite = 2
        self.image, self.rect = self.images[2][0], self.images[2][1]
        self.rect.move_ip(x,y)

    # Take away time passed and let the image be the floor of the remaining time / 1000

    def update(self):
        self.remainingTime -= self.clock.tick()
        if self.remainingTime <= 0:
            self.end()
        else:
            self.currentSprite = math.floor(self.remainingTime / 1000)
            self.image = self.images[self.currentSprite][0]


"""
Button Sprite
"""

class Button(pygame.sprite.Sprite):

    def __init__(self,x,y,images,clickHandler=None):
        pygame.sprite.Sprite.__init__(self)

        # Determine if there are multiple images / "sprites"
        if len(images) > 1:

            # If multiple sprites then loop through each and load the image
            self.sprites = {}
            for imageName in images:
                self.sprites[imageName], self.rect = loadImage(imageName,True)
                self.sprites[imageName], self.rect = loadImage(imageName,True)

            # Set current image to first image
            self.image = self.sprites[images[0]]
        else:

            # If single sprite, load first (and only) image
            self.image, self.rect = loadImage(images[0])

        # Set button to correct position
        self.rect.move_ip(x,y)

        # Set click handler, default is nothing
        if clickHandler != None:
            self.onClick = clickHandler

    def onClick(self):
        return

"""
Radio Button
"""

class RadioButton(Button):

    # Load images and map them to states in dictionary

    def __init__(self,x,y):
        Button.__init__(self,x,y,["offOption","onOption"])
        self.state = False
        self.stateNames = {"True":"onOption","False":"offOption"}

    # Call change option depending on current state

    def onClick(self):
        self.changeOption(True if self.state == False else False)

    # Change image and change state depending on parameter

    def changeOption(self,option):
        self.state = True if option == True else False
        self.image = self.sprites[self.stateNames[str(self.state)]]

