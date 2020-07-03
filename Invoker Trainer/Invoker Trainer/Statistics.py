# Go through each game and their list of options matches
# with the required then add them to the filtered data

def filterDataByOptions(games,options):
    filteredData = []
    # If no options given then set options to "", required due to parsing formatting
    options = [""] if options == [] else options
    for game in games:
        matchedCriteria = False
        if game.options == options:
            matchedCriteria = True
        if matchedCriteria:
            filteredData.append(game)
    return filteredData

# Same as filter by options but adds each combo in a game where combo ID matches, along
# with the combo's execution time

def filterDataByCombo(games,comboID):
    comboData = []
    for game in games:
        for combo in game.combos:
            if combo[0] == comboID:
                comboData.append([combo[0],combo[1]])
    return comboData

def findHighest(data):
    return round(max(data),2) if len(data) > 0 else "N/A"

def findLowest(data):
    return round(min(data),2) if len(data) > 0 else "N/A"

def findAverage(data):
    return round(sum(data)/len(data),2) if len(data) > 0 else "N/A"

def findSize(data):
    return len(data)

