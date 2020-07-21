import os
import sys
import json
import codecs

import clr

clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

ScriptName = "Dice Roll Script"
Website = "https://github.com/johnpvalerio"
Description = "Rolls a given type of dice for Streamlabs Bot"
Creator = "AegisBlue"
Version = "1.0.0"
configFile = "config.json"
settings = {}


def Init():
    global settings

    path = os.path.dirname(__file__)
    try:
        with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
            settings = json.load(file, encoding='utf-8-sig')
    except FileExistsError:
        settings = {
            "command": "!roll",
            "alias": '!dice',
            "useCooldown": True,
            "userCdMin": 10,
            "userCdSec": 0,
            "liveOnly": False,
            "numDiceCap": 10,
            "typeDiceCap": 1000
        }


def Execute(data):
    if data.IsChatMessage() and (
            data.GetParam(0).lower() == settings["command"] or data.GetParam(0).lower() == settings["alias"]) and (
            (settings["liveOnly"] and Parent.IsLive()) or (not settings["liveOnly"])):
        userID = data.User
        userName = data.UserName
        numDice = 1
        typeDice = 20
        result = []
        userInput = "1d20"

        # get input (optional) xdy
        if data.GetParamCount() == 2:
            try:
                userInput = data.GetParam(1).upper()
                index_d = userInput.index('D')
                if settings["numDiceCap"] < int(userInput[:index_d]) or\
                        int(userInput[:index_d]) < 1:     # x
                    return
                if userInput[index_d] != 'D':                             # d
                    return
                if settings["typeDiceCap"] < int(userInput[index_d+1:]) or\
                        int(userInput[index_d+1:]) < 1:    # y
                    return
                numDice = int(userInput[:index_d])
                typeDice = int(userInput[index_d+1:])
            except:     # catch all bad inputs
                return
        elif data.GetParamCount() > 2:  # too many input arguments
            return

        # check if user is on cooldown
        if settings["useCooldown"] and Parent.IsOnUserCooldown(ScriptName, settings["command"], userID):
            time = Parent.GetUserCooldownDuration(ScriptName, settings["command"], userID)
            min_cd = time / 60
            sec_cd = time % 60
            if min_cd == 0:
                Parent.SendStreamMessage(userName + ", command cooldown for " + str(sec_cd) + "s.")
            else:
                Parent.SendStreamMessage(userName + ", command cooldown for " + str(min_cd) + "m" + str(sec_cd) + "s.")
            return
        # perform dice action
        else:
            for i in range(numDice):
                rng = Parent.GetRandom(1, typeDice+1)      # [1,typeDice]
                result.append(rng)
            outcome = ", ".join([str(x) for x in result])

            Parent.Log(ScriptName, userName + ' ' + userInput + ' - ' + str(result))

            msg = userName + ' rolled ' + outcome
            Parent.SendStreamMessage(msg)

            # set user cooldown if enabled
            if settings["useCooldown"]:
                time = int(settings["userCdMin"]) * 60 + int(settings["userCdSec"])
                Parent.AddUserCooldown(ScriptName, settings["command"], userID, time)
    return


def ReloadSettings(jsonData):
    Init()
    return


def Tick():
    return
