import os
import random
import json
import codecs
import time
from collections import defaultdict

import clr

clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

ScriptName = "AC Fishing Script"
Website = "https://github.com/johnpvalerio"
Description = "Fish animal crossing creatures"
Creator = "AegisBlue"
Version = "1.0.4.1"
configFile = "config.json"
fishFile = 'fish.json'
playerFile = 'player.json'
settings = {}
fish = {}

maxRange = 0
biggestCatch = {'user': None,
                'item': None,
                'price': 0}
usersDone = []              # users who played
payoutRatio = 0.01          # fraction coefficient of payout

isActive = False            # is command active (button pressed)
activeStopTime = None       # variable to hold the time when the event ends, if None: cmd not active
cdStopTime = 0              # when the event is activated again


def Init():
    global settings, fish, isActive, activeStopTime, maxRange, usersDone

    path = os.path.dirname(__file__)
    try:
        with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
            settings = json.load(file, encoding='utf-8-sig')
        with codecs.open(os.path.join(path, fishFile), encoding='utf-8-sig', mode='r') as file:
            fish = json.load(file, encoding='utf-8-sig')
    except IOError:
        settings = {
            "command": "!fish",
            "alias": '!f',
            "useCost": 10,
            "cmdCdMin": 30,
            "cmdCdSec": 0,
            "activeSec": 60,
            "liveOnly": False,
            "commonChance": 45,
            "fCommChance": 20,
            "uCommChance": 15,
            "scarceChance": 6,
            "rareChance": 3,
            "vRareChance": 1,
            "missChance": 10,
            "topCatch": True,
            "startMsg": "Nobody can resist the siren song of the Fishing Tourney. Start castin' !fish/!f ($cost)",
            "stopMsg": "Reel it in! The Fishing Tourney is Over!"
        }
    finally:
        maxRange = calcMax()
        Unload()


def calcMax():
    """
    Calculates the max range of chances
    :return:
    """
    return sum([settings["missChance"],
                settings["commonChance"],
                settings["fCommChance"],
                settings["uCommChance"],
                settings["scarceChance"],
                settings["rareChance"],
                settings["vRareChance"]])


def calcRest(current):
    """
    Calculates max range of given rarity
    :param current: string given rarity
    :return: int max range of rarity
    """
    rarity = ["missChance", "commonChance", "fCommChance", "uCommChance", "scarceChance", "rareChance", "vRareChance"]
    index = rarity.index(current)
    rarity = rarity[:index + 1]     # get range from lowest rarity to given rarity (included)
    output = 0
    for x in rarity:
        output += settings[x]
    return output


def getUserInfo(userId):
    """
    Returns a players info as a dict
    :param userId: int
    :return: dict user data, dict all data
    """
    # open player file if available
    try:
        with codecs.open(os.path.join(os.path.dirname(__file__), playerFile), encoding='utf-8-sig', mode='r') as file:
            players = json.load(file, encoding='utf-8-sig')
        userData = players[userId]
        userCatch = defaultdict(int, userData['catch'])
        userData['catch'] = userCatch
    # create new player profile for player file
    except KeyError:
        userData = {'skill': 0, 'catch': defaultdict(int)}
    # create new player file
    except IOError:
        userData = {'skill': 0, 'catch': defaultdict(int)}
        players = {}
    return userData, players


def updateUserInfo(info, item, isFish=True):
    """
    Updates user info
    :param info: dict user stats
    :param item: string caught item
    :param isFish: bool if fish item or not
    :return: None
    """
    userSkill = info['skill']
    userCatch = info['catch']
    userCatch[item] += 1
    if isFish:
        info.update({'skill': userSkill + 1})
    info.update({'catch': userCatch})


def updateUserFile(userId, allPlayers, info):
    """
    Updates user entry in player json file
    :param userId: int user ID
    :param allPlayers: dict all players info
    :param info: dict user info
    :return: None
    """
    allPlayers.update({userId: info})
    with codecs.open(os.path.join(os.path.dirname(__file__), playerFile), encoding='utf-8-sig', mode='w') as file:
        json.dump(allPlayers, file, indent=4)


def updateBiggestCatch(user, item, price):
    """
    Sets biggest catch variable with new values
    :param user: string userID
    :param item: string item (fish/junk)
    :param price: int item value
    :return: None
    """
    global biggestCatch
    if biggestCatch['user'] is None or biggestCatch['price'] < price:
        biggestCatch['user'] = user
        biggestCatch['item'] = item
        biggestCatch['price'] = price
    return


def Execute(data):
    global usersDone
    if data.IsChatMessage() and (
            data.GetParam(0).lower() == settings["command"] or data.GetParam(0).lower() == settings["alias"]) and (
            (settings["liveOnly"] and Parent.IsLive()) or (not settings["liveOnly"]) and
            cdStopTime <= time.time() and
            isActive):

        userID = data.User
        userName = data.UserName
        userPoints = Parent.GetPoints(userID)

        # check if user is on cooldown
        if userID in usersDone:
            return
        # check if user has enough to play
        elif settings['useCost'] > userPoints:
            return
        # perform fishing action
        else:
            stat, allPlayers = getUserInfo(userID)
            rng = Parent.GetRandom(1, maxRange + 1)
            isFish = True
            if rng <= calcRest("missChance"):
                rarity = "miss"
                isFish = False
            elif rng <= calcRest("commonChance"):
                rarity = "common"
            elif rng <= calcRest("fCommChance"):
                rarity = "fairly common"
            elif rng <= calcRest("uCommChance"):
                rarity = "uncommon"
            elif rng <= calcRest("scarceChance"):
                rarity = "scarce"
            elif rng <= calcRest("rareChance"):
                rarity = "rare"
            else:
                rarity = "very rare"

            itemCaught = random.choice(fish[rarity].values())  # pick random fish entry

            name = itemCaught["name"]  # get item name
            quote = itemCaught["quote"]  # get item quote
            amount = int(itemCaught["price"] * payoutRatio)  # get actual payout price

            msg = quote.replace("$user", userName)  # add username to quote

            updateBiggestCatch(userName, name, amount)
            updateUserInfo(stat, name, isFish)  # add fish and skill to user
            updateUserFile(userID, allPlayers, stat)  # write to file

            Parent.RemovePoints(userID, userName, settings['useCost'])
            Parent.AddPoints(userID, userName, amount)  # add channel points to user
            usersDone.append(userID)  # add user to list who played

            # notify log and chat
            Parent.SendStreamMessage(msg + " " + str(amount) + " " + Parent.GetCurrencyName())
            Parent.Log(ScriptName, userName + ' - ' + str(rng) + ' - ' + name)
    return


def ReloadSettings(jsonData):
    Init()
    return


def Unload():
    """
    Script unload function
    Resets all variables to initial state
    :return: None
    """
    global isActive, activeStopTime, cdStopTime
    cdStopTime = 0
    isActive = False
    activeStopTime = None
    clearCatch()
    return


def clearCatch():
    """
    Resets catch information: list of users and biggest catch info
    :return: None
    """
    global usersDone, biggestCatch
    usersDone = []
    biggestCatch = {'user': None,
                    'item': None,
                    'price': 0}
    return


def startTimer():
    """
    Starts timer for active action execution
    :return: None
    """
    global isActive, activeStopTime
    Unload()    # reset everything
    isActive = True
    activeStopTime = time.time() + settings["activeSec"]
    Parent.Log(ScriptName, "Active [" + str(settings["activeSec"]) + ' sec]')
    msg = settings["startMsg"]  # get start message
    msg = msg.replace("$time", str(settings["activeSec"]) + " seconds")     # add how long active for
    msg = msg.replace("$cost", str(settings["useCost"]) + " " + Parent.GetCurrencyName())   # add command cost
    Parent.SendStreamMessage(msg)


def Tick():
    """
    Clock to toggle between active and cooldown period
    :return: None
    """
    global isActive, activeStopTime, usersDone, cdStopTime
    curTime = time.time()
    # start button not pressed yet (not active)
    if activeStopTime is None:
        return
    # timer expired and button pressed  (active)
    # event over, set on cooldown
    if activeStopTime <= curTime and isActive:
        isActive = False
        cd = settings["cmdCdMin"] * 60 + settings["cmdCdSec"]   # set on cooldown
        cdStopTime = curTime + cd   # set when active again
        Parent.Log(ScriptName, "Cd [" + str(cd) + ' sec]')

        Parent.SendStreamMessage(settings["stopMsg"])

        # display top catch if enabled
        if biggestCatch['user'] is not None and settings["topCatch"]:
            winMsg = "The best catch goes to " + biggestCatch['user'] + \
                     ' with a ' + biggestCatch['item'] + \
                     ' worth ' + str(biggestCatch['price']) + ' ' + Parent.GetCurrencyName()
            Parent.SendStreamMessage(winMsg)
        clearCatch()    # reset who already played
    # cooldown over, restart event
    elif cdStopTime <= curTime and isActive is False:
        startTimer()
    return
