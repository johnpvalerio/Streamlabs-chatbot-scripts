# ---------------------------------------
# Libraries and references
# ---------------------------------------
import os
import sys
import json
import codecs
import clr

sys.platform = "win32"
import keyboard as kb
import time
import ctypes

clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")
# ---------------------------------------
# [Required] Script information
# ---------------------------------------
ScriptName = "Chaos art hotkeys Script"
Website = "https://github.com/johnpvalerio"
Description = "Dumb hotkey script for Streamlabs Bot"
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
            "command": "!chaos",
            "cost": 1000,
            "useCost": True,
            "userCd": 15,
            "globalCd": 10,
            "liveOnly": True,
            "programName": "",
            "outputMsg": "$user has chosen $action",
            "debugMode": False
        }


def Execute(data):
    """
    Processes/validates data to execute gambling game
    :param data: Data - chat message object
    :return: None
    """
    if data.IsChatMessage() and (
            data.GetParam(0).lower() == settings["command"] ) and (
            (settings["liveOnly"] and Parent.IsLive()) or (not settings["liveOnly"])):
        # check user
        userID = data.User
        userName = data.UserName
        # user cooldown
        if Parent.IsOnUserCooldown(ScriptName,settings['command'],data.User):
            if settings["debugMode"]:
                Parent.Log(ScriptName, userName + ' user cooldown: ' + str(Parent.GetUserCooldownDuration(ScriptName,settings['command'],userID)))
            return
        # global cooldown
        if Parent.IsOnCooldown(ScriptName,settings['command']):
            if settings["debugMode"]:
                Parent.Log(ScriptName, 'global cooldown: ' + str(Parent.GetCooldownDuration(ScriptName,settings['command'])) )
            return

        # check points
        userPoints = Parent.GetPoints(userID)
        cost = settings['cost']
        if cost > userPoints:
            if settings["debugMode"]:
                Parent.Log(ScriptName, userName + ' not enough points')
            return
        # check correct target window
        Parent.Log(ScriptName, 'getting active window')
        activeWindow = getActiveWindow()
        if settings['programName'].lower() not in activeWindow.lower() or settings['programName'].lower() == '':
            if settings["debugMode"]:
                Parent.Log(ScriptName, activeWindow + ' not the target window')
            return
        # perform action
        action = randomHotkey()
        kb.send(action[0])

        output = settings["outputMsg"]
        output = output.replace('$user', userName)
        output = output.replace('$action', action[1])

        if settings["debugMode"]:
            Parent.Log(ScriptName, 'activating - ' + output)

        if settings['useCost']:
            Parent.RemovePoints(userID, userName, cost)

        Parent.SendStreamMessage(output)
        Parent.AddCooldown(ScriptName,settings['command'],settings['globalCd'])
        Parent.AddUserCooldown(ScriptName,settings['command'],userID,settings['userCd'])
    return

def getActiveWindow():
    """
    Get active window as a string
    :param:
    :return: string - active window name
    """
    time.sleep(2)
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)

    ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)

    return buff.value.encode('utf-8')

def randomHotkey():
    """
    Get a random hotkey string
    :param:
    :return: tuple - (command key, command name)
    """
    badHotkeys = [('ctrl+page down', 'Zoom Out'), ('ctrl+Z', "Undo")]
    goodHotkeys = [('ctrl+s', 'Save')]
    hotkeyList= badHotkeys + goodHotkeys
    length = len(hotkeyList)
    rng = Parent.GetRandom(0, length)
    return hotkeyList[rng]

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
