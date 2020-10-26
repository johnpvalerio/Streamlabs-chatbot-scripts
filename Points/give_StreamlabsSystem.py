# ---------------------------------------
# Libraries and references
# ---------------------------------------
import codecs
import json
import os
import clr

clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")
# ---------------------------------------
# [Required] Script information
# ---------------------------------------
ScriptName = "Default Points Giving Script"
Website = "https://github.com/johnpvalerio"
Description = "Script for simpler points giving in Streamlabs Bot."
Creator = "AegisBlue"
Version = "1.1.0"
# ---------------------------------------
# Variables
# ---------------------------------------
configFile = "config.json"
settings = {}
NBVIEWERSCAP = 3


def Init():
    global settings

    path = os.path.dirname(__file__)
    try:
        with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as f:
            settings = json.load(f, encoding='utf-8-sig')
    except IOError:
        settings = {
            "command": "!give",
            "alias": "!g",
            "liveOnly": False,
            "defaultPoints": 50,
            "outputMsg": "Successfully given $user $points $currency"
        }


def is_digit(x):
    """
    Check if given is an int
    :param x: string
    :return: Boolean - true: int
    """
    try:
        int(x)
        return int(x)
    except ValueError:
        return None


def parse_input(data):
    """
    Gets user input and parses to get the users and amount of points to give
    :param data: String to parse
    :return: list: user strings (id), int: amount of points to give
    """
    pts = settings["defaultPoints"]  # set default amount of points
    userInput = []
    # get all inputs
    for i in range(1, data.GetParamCount()):
        userInput.append(data.GetParam(i))
    # check for user input for points
    temp_pts = is_digit(userInput[-1])
    if temp_pts or temp_pts == 0:
        pts = temp_pts
        userInput.pop(-1)
    # check if any users are just numbers (error: syntax input error)
    for u in userInput:
        if is_digit(u):
            userInput = []
            break
    return userInput, pts


def toUserId(users):
    """
    Converts entries as streamlabs ID's (lower case)
    :param users: list of users
    :return: List string userId's
    """
    output = []
    for i in range(len(users)):
        if users[i][0] == '@':
            output.append(users[i][1:].lower())
        else:
            output.append(users[i].lower())
    if 'all' in users:
        output = []
        for u in Parent.GetViewerList():
            output.append(u)
    return output


def validatePts(users, pts):
    """
    Sets how many points to remove/add
    If removing exceeds user total points, remove exact amount
    :param users: List string userIds
    :param pts: Int amount
    :return: List int
    """
    output = []
    for u in users:
        uPoints = Parent.GetPoints(u)
        if pts < 0:
            output.append(abs(pts) if uPoints + pts > 0 else uPoints)
        else:
            output.append(pts)
    return output


def getUsernames(users):
    """
    Converts entries from streamlabs ID's to username
    :param users:
    :return: /
    """
    for i in range(len(users)):
        users[i] = Parent.GetDisplayName(users[i])


def Execute(data):
    """
    Takes input from chat and adds into json file
    :param data:
    :return: /
    """
    global settings
    # (is chat message + is command called + is live only)
    if data.IsChatMessage() and \
            (data.GetParam(0).lower() == settings["command"].lower() or
             data.GetParam(0).lower() == settings["alias"].lower()) and \
            ((settings["liveOnly"] and Parent.IsLive()) or
             (not settings["liveOnly"])):

        Parent.Log(ScriptName, data.User + ' isMod: ' + str(Parent.HasPermission(data.User, "Moderator", "")))
        # check permissions - error
        if not Parent.HasPermission(data.User, "Moderator", ""):
            Parent.Log(ScriptName, 'no perm')
            return
        # check if empty args - error
        if data.GetParamCount() == 1:
            Parent.Log(ScriptName, 'no extra args')
            return

        # get all users and amount to give
        users, amount = parse_input(data)

        # check if user list empty - error
        if not users:
            Parent.Log(ScriptName, 'empty users')
            return

        # converts to streamlab's user IDs
        adjustedUsers = toUserId(users)
        # convert to how many points they should get
        adjustedPts = validatePts(adjustedUsers, amount)

        batchUserAmount = dict(zip(adjustedUsers, adjustedPts))

        # perform action depending on amount
        # 0 - do nothing
        # positive - add
        # negative - remove
        if amount == 0:
            return
        elif amount > 0:
            failedUsers = Parent.AddPointsAll(batchUserAmount)
        else:
            failedUsers = Parent.RemovePointsAll(batchUserAmount)

        passUsers = list(set(adjustedUsers) - set(failedUsers))

        getUsernames(failedUsers)  # might be useless
        getUsernames(passUsers)

        Parent.Log(ScriptName, 'pass users: ' + str(passUsers) + ' [' + str(amount) + '] | ' +
                   'failed users: ' + str(failedUsers))

        if 'all' in users:
            passUserStr = 'everyone'
        else:
            # shorten if too many users to add
            if len(passUsers) > NBVIEWERSCAP:
                passUserStr = ', '.join(passUsers[:NBVIEWERSCAP])
                passUserStr += ' and ' + str(len(passUsers) - NBVIEWERSCAP) + ' more'
            else:
                passUserStr = ', '.join(passUsers)

        output = settings["outputMsg"]
        output = output.replace('$user', passUserStr)
        output = output.replace('$points', str(amount))
        output = output.replace('$currency', Parent.GetCurrencyName())

        if passUsers:
            Parent.SendStreamMessage(output)
    return


def ReloadSettings(jsonData):
    Init()
    return


def Tick():
    return
