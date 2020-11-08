# ---------------------------------------
# Libraries and references
# ---------------------------------------
import codecs
import json
import os
import clr
import time

clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")
# ---------------------------------------
# [Required] Script information
# ---------------------------------------
ScriptName = "Scheduled Points"
Website = "https://github.com/johnpvalerio"
Description = "Script for giving additional points after a set time."
Creator = "AegisBlue"
Version = "1.0.0"
# ---------------------------------------
# Variables
# ---------------------------------------
configFile = "config.json"
settings = {}
triggerTime = None  # time when to activate
isActivating = True  # bool check to trigger (one time or continuous)


def Init():
    global settings

    path = os.path.dirname(__file__)
    try:
        with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
            settings = json.load(file, encoding='utf-8-sig')
    except IOError:
        settings = {
            "useOneTime": False,
            "intervalHrs": 2,
            "intervalMin": 0,
            "intervalSec": 0,
            "pts": 200,
            "outputMsg": "$time $points $currency"
        }


def Execute(data):
    return


def ReloadSettings(jsonData):
    Init()
    return


def Unload():
    """
    Unload scripts and services, calls stop event
    :return: None
    """
    global triggerTime, isActivating
    Parent.Log(ScriptName, str(triggerTime))
    triggerTime = None
    isActivating = True
    Parent.Log(ScriptName, "unload")
    return


def Tick():
    """
    Clock tick
    sets and triggers activation
    :return: None
    """
    global triggerTime, isActivating
    # if not live, do nothing
    if not Parent.IsLive():
        return
    # start schedule
    if triggerTime is None:
        triggerTime = nextTime()
        Parent.Log(ScriptName, "Starting time: " + str(triggerTime))
    # trigger
    if isActivating and time.time() >= triggerTime:
        viewers = []
        pts = []
        for u in Parent.GetViewerList():
            viewers.append(u)
            pts.append(settings["pts"])
        batchUserAmount = dict(zip(viewers, pts))
        Parent.AddPointsAll(batchUserAmount)
        triggerTime = nextTime()
        if settings["useOneTime"]:
            isActivating = False

        output = settings["outputMsg"]

        timeStr = (str(settings["intervalHrs"]) + 'h') if settings["intervalHrs"] > 0 else ""
        timeStr += (str(settings["intervalMin"]) + 'min') if settings["intervalMin"] > 0 else ""
        timeStr += (str(settings["intervalSec"]) + 'sec') if settings["intervalSec"] > 0 else ""

        output = output.replace('$time', timeStr)
        output = output.replace('$points', str(settings["pts"]))
        output = output.replace('$currency', Parent.GetCurrencyName())

        Parent.Log(ScriptName, str(settings["pts"]) + ' ' + str(viewers))
        Parent.SendStreamMessage(output)

    return


def nextTime():
    """
    Converts settings time into seconds
    :return: None
    """
    return time.time() + \
           settings["intervalHrs"] * 60 * 60 + \
           settings["intervalMin"] * 60 + \
           settings["intervalSec"]
