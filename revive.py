import os
def set_up(startbot=True):
    os.system("pip install virtualenv")
    os.system("python3 -m venv venv")
    os.system("virtualenv venv -p python3")
    os.system("source ./venv/bin/activate")
    os.system("python3 -m pip install -r requirements.txt")
    if startbot:
        run()
def run():
    os.system("python lichess-bot.py")