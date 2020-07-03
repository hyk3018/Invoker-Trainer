import xml.etree.ElementTree as ET 

"""
Dota object is instantiated and called when data regarding
Dota is needed. It has minimal functionality - basically
acts as a data store.
"""

class Dota:

    # Initialisation will set the path of the xml files to read from
    # The Element Tree class from the xml library will then use this to generate 

    def __init__(self):
        self.combosPath = r"game\combos.xml"
        self.mechanicsPath = r"game\mechanics.xml"
        
        self.combos = ET.parse(self.combosPath)
        self.combos = self.combos.getroot()
        self.mechanics = ET.parse(self.mechanicsPath)
        self.mechanics = self.mechanics.getroot()
        self.parseCooldowns()
        self.parseSpells()
        self.parseCombos()

    # Get cooldown data from XML

    def parseCooldowns(self):
        self.absoluteCD = {}
        self.percentageCD = {}
        
        # Look for absolute and percentage tags
        for cdType in self.mechanics[1]:
            if cdType.tag == "absolute":

                # For each item create CD item and add to appropriate dictionary with ID as key
                for cd in cdType:
                    id = cd.attrib.get("id")
                    self.absoluteCD[id] = CDItem(id,cd[0].text,"absolute",int(cd[1].text))
            elif cdType.tag == "percentage":
                for cd in cdType:
                    id = cd.attrib.get("id")
                    self.percentageCD[id] = CDItem(id,cd[0].text,"percentage",int(cd[1].text))
        return

    # Get spell data from XML

    def parseSpells(self):

        # Loop through each spell and add them to dictionary with id as key
        self.spells = {}

        for spell in self.mechanics[0]:

            # Get list of actions for the spell
            spellSequence = []
            for action in spell[2]:
                spellSequence.append(action.text)

            self.spells[spell.attrib.get("id")] = DotaSpell(spell.attrib.get("id"),spell[0].text,spell[1].text,spellSequence)
        return

    # Get combo data from XML

    def parseCombos(self):

        # Split combos in different stages of game and add to active and inactive depending on time of use string
        self.allCombos = []
        self.activeCombos = {"early":[], "mid":[], "late":[]}
        self.inactiveCombos = {"early":[], "mid":[], "late":[]}

        for active in self.combos[0]:
            timeOfUse = active[0].text
            spells = list(map(lambda spellNode : spellNode.text, active[1:]))
            combo = Combo(active.attrib.get("id"),active.attrib.get("name"),spells)
            if timeOfUse[0] == "1":
                self.activeCombos["early"].append(combo)
            if timeOfUse[1] == "1":
                self.activeCombos["mid"].append(combo)
            if timeOfUse[2] == "1":
                self.activeCombos["late"].append(combo)
            self.allCombos.append(combo)

        for inactive in self.combos[1]:
            timeOfUse = inactive[0].text
            spells = list(map(lambda spellNode : spellNode.text, inactive[1:]))
            combo = Combo(inactive.attrib.get("id"),inactive.attrib.get("name"),spells)
            if timeOfUse[0] == "1":
                self.inactiveCombos["early"].append(combo)
            if timeOfUse[1] == "1":
                self.inactiveCombos["mid"].append(combo)
            if timeOfUse[2] == "1":
                self.inactiveCombos["late"].append(combo)
            self.allCombos.append(combo)
        return

class DotaSpell:

    def __init__(self,id,name,castType,castSequence):
        self.id = id
        self.name = name
        self.castType = castType
        self.castSequence = castSequence

class Combo:

    def __init__(self,id,name,spells):
        self.id = id
        self.name = name
        self.spells = spells

class CDItem:

    def __init__(self,id,name,cdType,cdValue):
        self.id = id
        self.name = name
        self.cdType = cdType
        self.cdValue = cdValue