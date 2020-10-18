# ---------------------------------------
# Libraries and references
# ---------------------------------------
import codecs
import json
import os
import clr
import sys
import System

clr.AddReference([asbly for asbly in System.AppDomain.CurrentDomain.GetAssemblies() if "AnkhBotR2" in str(asbly)][0])
import AnkhBotR2
from TwitchLib.PubSub import TwitchPubSub

clr.AddReference("IronPython.SQLite.dll")
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + r"\References")
clr.AddReference("IronPython.Modules.dll")

# ---------------------------------------
# [Required] Script information
# ---------------------------------------
ScriptName = "Points Conversion"
Website = "https://github.com/johnpvalerio"
Description = "Script for converting Twitch channel point rewards to chatbot currency."
Creator = "AegisBlue"
Version = "0.0.0"
# Based from EncryptedThoughts repo
# ---------------------------------------
# Variables
# ---------------------------------------
configFile = "config.json"
settings = {}
EventReceiver = None


def Init():
    """
    Init settings setup
    :return: None
    """
    global settings

    path = os.path.dirname(__file__)
    try:
        with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as f:
            settings = json.load(f, encoding='utf-8-sig')
    except IOError:
        settings = {
            "rewardName": "",
            "liveOnly": True,
            "useOutputMsg": False,
            "useRewardCost": True,
            "defaultRewardCost": 1000,
            "minDiff": 100,
            "maxDiff": 100,
            "outputMsg": "$user gained $points $currency"
        }


def Execute(data):
    """
    Chat command execute - Not used
    :param data: /
    :return: /
    """
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
    Parent.Log(ScriptName, "Starting receiver")

    global EventReceiver
    EventReceiver = TwitchPubSub()

    EventReceiver.OnPubSubServiceConnected += EventReceiverConnected
    EventReceiver.OnRewardRedeemed += EventReceiverRewardRedeemed

    try:
        EventReceiver.Connect()
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
    oauth = AnkhBotR2.Managers.GlobalManager.Instance.VMLocator.StreamerLogin.Token.replace("oauth:", "")

    headers = {"Authorization": 'OAuth ' + oauth}
    data = json.loads(Parent.GetRequest("https://id.twitch.tv/oauth2/validate", headers))
    Parent.Log(ScriptName, str(data))

    userid = json.loads(data["response"])['user_id']
    Parent.Log(ScriptName, "Event receiver connected, sending topics for channel id: " + str(userid))

    EventReceiver.ListenToRewards(userid)
    EventReceiver.SendTopics(oauth)
    return


def EventReceiverRewardRedeemed(sender, e):
    """
    Processes rewards redeemed
    :param sender: /
    :param e: Claimed reward event info
    :return: None
    """
    userID = e.Login
    userName = e.DisplayName
    # if reward NOT assigned, stop
    if e.RewardTitle.lower() != settings["rewardName"].lower():
        return
    # else process reward
    if settings["useRewardCost"]:
        ptsGained = int(e.RewardCost)
    else:
        ptsGained = settings["defaultRewardCost"]

    minBound = settings["minDiff"] - ptsGained
    maxBound = settings["maxDiff"] + ptsGained

    ptsGained = Parent.GetRandom(minBound, maxBound)
    Parent.AddPoints(userID, userName, ptsGained)

    output = settings["outputMsg"]
    output = output.replace('$user', userName)
    output = output.replace('$points', str(ptsGained))
    output = output.replace('$currency', Parent.GetCurrencyName())
    Parent.Log(ScriptName, output)
    if settings["useOutputMsg"]:
        Parent.SendStreamMessage(output)
    return
