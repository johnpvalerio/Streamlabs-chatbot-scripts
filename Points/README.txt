# ---------------------------------------
# Script information
# ---------------------------------------
ScriptName = "Default Points Giving Script"
Website = "https://github.com/johnpvalerio"
Description = "Script for simpler points giving in Streamlabs Bot."
Creator = "AegisBlue"
Version = "1.1.0"

# ---------------------------------------
# Setup
# ---------------------------------------
Download current Streamlabs Chatbot version: https://streamlabs.com/chatbot

Download and install Python 2.7.13 since that's needed for Chatbot and the Script features:
https://www.python.org/ftp/python/2.7.13/python-2.7.13.msi

Open the SL Chatbot and go to the "Scripts" tab in the left sidebar.
Click on the cogwheel in the top right and set your Python directory to the `Lib` folder where you installed Python
(By default it should be `C:\Python27\Lib`).

Copy the scripts you want to use into the folder from the SL Chatbot. You can also use the Import function per button on the top right in the "Scripts" tab.
(By default it should be `C:\Users\<Username>\AppData\Roaming\Streamlabs\Streamlabs Chatbot\Services\Scripts`)

Go back to the `Scripts` tab in Chatbot and rightclick the background and click "Reload Scripts".
Afterwards the list of installed scripts should appear and you can start configuring those.

# ---------------------------------------
# How to use
# ---------------------------------------
Command format
!<command name> <user target> [amount]
    <command name>  - given command name or command alias, not case sensitive
                        DEFAULT: "!give" or "!g"
    <user target>   - user(s) in chat, "@" names are also valid
                      may use many user name targets
                      may use "all" to target every viewer in chat
                        ex: !give @AegisBlue StreamlabsBot 50
    [amount]        - (optional) amount of channel points to give to user(s)
                       may be positive or negative amount
                       if none given, gives default amount (Default amount settings input)
                        ex: !g AegisBlue

# ---------------------------------------
# Version History
# ---------------------------------------
1.1.0:
    ~ Added ability to use "all" to target all viewers
    ~ Added functionality to give negative amounts
1.0.0:
    ~ First Release version
