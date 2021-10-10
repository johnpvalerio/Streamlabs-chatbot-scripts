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
import mouse as ms
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
Version = "1.0.1"
# ---------------------------------------
# Variables
# ---------------------------------------
configFile = "config.json"
cmdFile = "cmd_list.json"
settings = {}
commands = {}


def Init():
    """
    Init settings setup
    :return: None
    """
    global settings, commands

    path = os.path.dirname(__file__)
    try:
        with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
            settings = json.load(file, encoding='utf-8-sig')
        with codecs.open(os.path.join(path, cmdFile), encoding='utf-8-sig', mode='r') as file:
            commands = json.load(file, encoding='utf-8-sig')
    except IOError:
        settings = {
            "command": "!chaos",
            "cost": 1000,
            "useCost": True,
            "userCd": 15,
            "globalCd": 10,
            "liveOnly": True,
            "programName": "",
            "outputMsg": "{user} has chosen {action}",
            "debugMode": False
        }
        commands = {
            'good':[
                ('ctrl+page down', 'Zoom Out'), 
                ('ctrl+Z', "Undo")
            ],
            'bad':[
                ('ctrl+s', 'Save')
            ]
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
        activeWindow = getActiveWindow()

        if settings['programName'].lower() not in activeWindow.lower() or settings['programName'].lower() == '':
            if settings["debugMode"]:
                Parent.Log(ScriptName, activeWindow + ' not the target window')
            return
        
        # perform action
        action = randomHotkey()
        activate(action[0], action[2])

        output = settings["outputMsg"].format(user=userName, action=action[1])

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
    if settings["debugMode"]:
        time.sleep(2)
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)

    try:
        ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
    except Exception as e:
        if settings["debugMode"]:
            Parent.Log(ScriptName, str(e) + buff.value.encode('utf-8'))

    return buff.value.encode('utf-8')

def randomHotkey():
    """
    Get a random hotkey string
    :param:
    :return: tuple - (command key, command name)
    """
    badHotkeys = commands['bad']
    goodHotkeys = commands['good']
    hotkeyList= badHotkeys + goodHotkeys
    length = len(hotkeyList)
    rng = Parent.GetRandom(0, length)
    return hotkeyList[rng]

def activate(cmd, repeat):
    """
    Keep spinning while mouse is held, once released do action
    """
    while(ms.is_pressed()):
        continue
    if repeat != 1:
        repeat = Parent.GetRandom(1, repeat)
    for i in range(repeat):
        kb.send(cmd)


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