# ---------------------------------------
# Libraries and references
# ---------------------------------------
import os
import sys
import json
import codecs
import clr

clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")
# ---------------------------------------
# [Required] Script information
# ---------------------------------------
ScriptName = "Gambling Script"
Website = "https://github.com/johnpvalerio"
Description = "Gambling mini game for Streamlabs Bot"
Creator = "AegisBlue"
Version = "1.0.0"
# ---------------------------------------
# Variables
# ---------------------------------------
configFile = "config.json"
settings = {}


def Init():
    """
    Init settings setup
    :return: None
    """
    global settings

    path = os.path.dirname(__file__)
    try:
        with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
            settings = json.load(file, encoding='utf-8-sig')
    except IOError:
        settings = {
            "command": "!gamble",
            "alias": "!g",
            "winThresh": 50,
            "rewardMul": 1,
            "useCooldown": True,
            "userCdMin": 10,
            "userCdSec": 0,
            "liveOnly": False,
            "useCapBet": False,
            "capBet": 0
        }


def Execute(data):
    """
    Processes/validates data to execute gambling game
    :param data: Data - chat message object
    :return: None
    """
    if data.IsChatMessage() and (
            data.GetParam(0).lower() == settings["command"] or data.GetParam(0).lower() == settings["alias"]) and (
            (settings["liveOnly"] and Parent.IsLive()) or (not settings["liveOnly"])):
        userID = data.User
        userName = data.UserName
        userPoints = Parent.GetPoints(userID)

        if data.GetParamCount() == 2:
            try:        # numbered input
                costs = int(data.GetParam(1))  # rounds down if decimal
            except:     # string input
                wagerInput = data.GetParam(1)
                if wagerInput == 'all':         # all
                    costs = userPoints
                elif wagerInput[-1] == '%':     # percentage amount
                    wagerPerc = float(wagerInput[:-1]) / 100
                    costs = int(userPoints * wagerPerc)
                else:
                    return
        else:
            return

        # check if user has enough points
        if costs > userPoints:
            Parent.SendStreamMessage(userName + ", not enough points")
            return
        # check if negative
        elif costs <= 0:
            return
        elif costs > settings["capBet"] and settings["useCapBet"]:
            Parent.SendStreamMessage(userName + ", bet amount over max bet: " + str(settings["capBet"]) + " " + Parent.GetCurrencyName())
            return
        # check if user is on cooldown
        elif settings["useCooldown"] and Parent.IsOnUserCooldown(ScriptName, settings["command"], userID):
            time = Parent.GetUserCooldownDuration(ScriptName, settings["command"], userID)
            min = time / 60
            sec = time % 60
            if min == 0:
                Parent.SendStreamMessage(userName + ", command cooldown for " + str(sec) + "s.")
            else:
                Parent.SendStreamMessage(userName + ", command cooldown for " + str(min) + "m" + str(sec) + "s.")
            return
        # perform point transaction
        else:
            rng = Parent.GetRandom(0, 100)
            # Parent.SendStreamMessage("rolled: " + str(rng) + ' wager: ' + str(costs))
            Parent.Log(ScriptName,
                       userName + ' - ' + str(rng) + ' [' + str(costs) + '] threshold:' + str(settings['winThresh']))

            # win
            if rng >= settings['winThresh']:
                winnings = costs * settings["rewardMul"]
                Parent.AddPoints(userID, userName, winnings)
                Parent.SendStreamMessage(userName + ' WON ' + str(winnings) + " " + Parent.GetCurrencyName() +
                                         " - total earnings: " + str(Parent.GetPoints(userID)) + " " + Parent.GetCurrencyName())
            # lose
            else:
                Parent.RemovePoints(userID, userName, costs)
                Parent.SendStreamMessage(userName + ' LOST ' + str(costs) + " " + Parent.GetCurrencyName() +
                                         " - total earnings: " + str(Parent.GetPoints(userID)) + " " + Parent.GetCurrencyName())
            # set user cooldown if enabled
            if settings["useCooldown"]:
                time = int(settings["userCdMin"]) * 60 + int(settings["userCdSec"])
                Parent.AddUserCooldown(ScriptName, settings["command"], userID, time)
    return


def ReloadSettings(jsonData):
    """
    Reload settings
    :param jsonData: JSON data
    :return: None
    """
    Init()
    return


def Tick():
    """
    Clock tick
    :return: None
    """
    return
