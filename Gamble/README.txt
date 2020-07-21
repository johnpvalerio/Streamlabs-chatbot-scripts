# ---------------------------------------
# Script information
# ---------------------------------------
ScriptName = "Default Points Giving Script"
Website = "https://github.com/johnpvalerio"
Description = "Gambling mini game for Streamlabs Bot."
Creator = "AegisBlue"
Version = "1.0.0"

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
!<command name> <amount>
    <command name>  - given command name or command alias, not case sensitive
                        DEFAULT: "!give" or "!g"
    <amount>        - amount of channel points to wager
                       may be number, percentage or "all"
                       if decimal, will be rounded down to nearest integer
                        ex: !g 50
                            !g all
                            !g 30%

# ---------------------------------------
# Version History
# ---------------------------------------
1.0.0:
    ~ First Release version
