#Get parameters from config file ~/.pastell-admin
import os, shutil, configparser

def getConfiguration():
    user_config_dir = os.path.expanduser("~")
    user_config = user_config_dir + "/.pastell-admin"
    if not os.path.isfile(user_config):
        os.makedirs(user_config_dir, exist_ok=True)
        shutil.copyfile("./pastell-admin.dist", user_config)

    config = configparser.ConfigParser()
    config.optionxform = lambda option: option
    config.read(user_config)
    return config