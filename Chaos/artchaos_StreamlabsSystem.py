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
Version = "1.1.0"
# ---------------------------------------
# Variables
# ---------------------------------------
configFile = "config.json"
cmdFile = "cmd.json"
settings = {}
commands = {}
EventReceiver = None

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
        with codecs.open(os.path.join(path, cmdFile), encoding='utf-8-sig', mode='r') as file:
            commands = json.load(file, encoding='utf-8-sig')
    except IOError:
        settings = {
            "rewardName": "chaos",
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
    :param data: Data - chat message object
    :return: None
    """
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
            Parent.Log(ScriptName, str(e))

    return buff.value.encode('utf-8')

def randomHotkey():
    """
    Get a random hotkey string
    :param:
    :return: tuple - (command key, command name)
    """
    badHotkeys = commands['bad']
    goodHotkeys = commands['good']
    hotkeyList = badHotkeys + goodHotkeys
    length = len(hotkeyList)
    rng = Parent.GetRandom(0, length)
    return hotkeyList[rng]

def activate(cmd):
    """
    Keep spinning while mouse is held, once released do action
    """
    while(ms.is_pressed()):
        continue
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


def Unload():
    """
    Unload scripts and services, calls stop event
    :return: None
    """
    StopEventReceiver()
    return


def ScriptToggled(state):
    """
    Event when script toggled ON/OFF
    :param state: Boolean
    :return: None
    """
    if state:
        if EventReceiver is None:
            RestartEventReceiver()
    else:
        StopEventReceiver()

    return


def StartEventReceiver():
    """
    Starts twitch Convert event receiver
    :return: None
    """
    if settings["debugMode"]:
        Parent.Log(ScriptName, "Starting receiver")

    global EventReceiver
    EventReceiver = TwitchPubSub()

    EventReceiver.OnPubSubServiceConnected += EventReceiverConnected
    EventReceiver.OnRewardRedeemed += EventReceiverRewardRedeemed

    try:
        EventReceiver.Connect()
        if settings["debugMode"]:
            Parent.Log(ScriptName, "connected")
    except Exception as e:
        Parent.Log(ScriptName, "Unable to start event receiver. Exception: " + str(e))
    return


def StopEventReceiver():
    """
    Stop twitch pubsub event receiver
    :return: None
    """
    global EventReceiver
    try:
        if EventReceiver is None:
            return
        EventReceiver.Disconnect()
        if settings["debugMode"]:
            Parent.Log(ScriptName, "Event receiver disconnected")
        EventReceiver = None

    except Exception as e:
        Parent.Log(ScriptName, "Event receiver already disconnected. Exception: " + str(e))
    return


def RestartEventReceiver():
    """
    Restarts receiver
    :return: None
    """
    StopEventReceiver()
    StartEventReceiver()
    return


def EventReceiverConnected(sender, e):
    """
    Twitch pubsub event callback for on connected event
    Sets Reward topic listener
    :param sender: /
    :param e: /
    :return: None
    """
    # create request payload
    oauth = AnkhBotR2.Managers.GlobalManager.Instance.VMLocator.StreamerLogin.Token.replace("oauth:", "")
    data = json.loads(Parent.GetRequest("https://id.twitch.tv/oauth2/validate", {"Authorization": 'OAuth ' + oauth}))
    
    if settings["debugMode"]:
        Parent.Log(ScriptName, str(data))

    channelId = json.loads(data["response"])['user_id']
    if settings["debugMode"]:
        Parent.Log(ScriptName, "Event receiver connected, sending topics for channel id: " + str(channelId))
    
    # Set pubsub to listen
    EventReceiver.ListenToRewards(channelId)
    EventReceiver.SendTopics(oauth)
    return


def EventReceiverRewardRedeemed(sender, e):
    """
    Processes rewards redeemed
    :param sender: /
    :param e: Claimed reward event info
    :return: None
    """
    # if reward NOT assigned, stop
    if e.RewardTitle.lower() != settings["rewardName"].lower():
        return

    # check correct target window
    if settings["debugMode"]:
        Parent.Log(ScriptName, 'getting active window')
    activeWindow = getActiveWindow()
    if settings['programName'].lower() not in activeWindow.lower() or settings['programName'].lower() == '':
        if settings["debugMode"]:
            Parent.Log(ScriptName, activeWindow + ' not the target window')
        return

    action = randomHotkey()
    activate(action[0])
    userName = e.DisplayName
    output = settings["outputMsg"].format(user=userName, action=action[1])
    # output = output.replace('$user', userName)
    # output = output.replace('$action', action[1])

    if settings["debugMode"]:
        Parent.Log(ScriptName, 'activating - ' + output)

    Parent.SendStreamMessage(output)
