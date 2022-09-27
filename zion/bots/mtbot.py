#
# MTBot - simple bot to run checks for bad words
# in messages
# Usage:
#   Add new wordlists with names and then add those
#   names as arguments to check decorator
#

from bot import Bot

# Creating new bot
MTBot = Bot("MTBot")

# Add new wordlists here
MTBot.addWordlists({"Fun": "wordlists/fun.txt"})


# Don't forget to add names of wordlists here!
@MTBot.check(wordlists=["Fun"])
def check(msg, wordlist):
    for word in msg.split(" "):
        if word.lower() in wordlist:
            return True
    return False
