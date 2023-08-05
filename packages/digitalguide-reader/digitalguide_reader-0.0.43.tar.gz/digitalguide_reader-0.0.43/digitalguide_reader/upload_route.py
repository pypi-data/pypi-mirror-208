from digitalguide.whatsapp_sync.db_objects import WhatsAppAction, WhatsAppHandler
import mongoengine
import os
import re

import yaml

from configparser import ConfigParser

def upload_route():
    config = ConfigParser()
    config.read("config.ini")

    dbname = config["bot"]["bot_name"]
    db_url=os.environ.get("DATABASE_URL")
    db_url = re.sub("admin", dbname, db_url, 1)
    mongoengine.connect(alias=dbname, host=db_url)

    # Read YAML file
    with open(config["yaml"]["datei_states"], 'r') as states_file:
        states = yaml.safe_load(states_file)

    with open(config["yaml"]["datei_actions"], 'r') as actions_file:
        actions = yaml.safe_load(actions_file)

    WhatsAppHandler.objects.delete()
    for key, value in states.items():
        WhatsAppHandler(SateName=key, Handlers=value).save()

    WhatsAppAction.objects.delete()
    for key, value in actions.items():
        WhatsAppAction(ActionName=key, Action=value).save()

    mongoengine.disconnect(alias=dbname)