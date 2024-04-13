""" Simple script to listen for Slack direct message events and download received images
NOTE:  This slack bot requires both an application token and a bot token with correct permissions
for DM interaction
"""

import sys
import logging
from typing import Optional
import requests
import pathlib
import argparse
import re
import time
from urllib.parse import urlparse
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

#-----------------------
#--- Parameters
#-----------------------
frcEventName = "frc"
img_id = 0
data_path = pathlib.Path("./data")
verbosity = 1

#-----------------------
#--- Command line argument parser
#-----------------------
parser = argparse.ArgumentParser(
            prog='ScoutImageBot',
            description='Slack bot to collect robot images from pit scouting')
parser.add_argument("-e", "--event", type=str, default="frc", 
                    help='Event name', required=True)
parser.add_argument("-d", "--dst_path", type=str, default="./data", 
                    help='Path to where to save data')
parser.add_argument("-b", "--bot_token_path", type=str, default="./.slack_token", 
                    help="Path to file which contains the Slack BOT token")
parser.add_argument("-a", "--app_token_path", type=str, default="./.slack_apptoken",
                    help="Path to file which contains the Slack APP token")
parser.add_argument("-v", "--verbosity", type=int, default=1,
                    help="Path to file which contains the Slack APP token")
parser.add_argument("-t", "--time_window", type=int, default=0, 
                    help="Time window for which to accept new message events (minutes).  By default ignores any messages that were generated prior to start")
args = parser.parse_args()

frcEventName=args.event
data_path = pathlib.Path(args.dst_path)
verbosity = args.verbosity
init_time = time.time() - args.time_window*60

if verbosity==0:
    logging.basicConfig(level=logging.ERROR)
elif verbosity==1:
     logging.basicConfig(level=logging.INFO)
else:
     logging.basicConfig(level=logging.DEBUG)    


if not data_path.exists() or not data_path.is_dir():
    logging.error(f"The destination directory doesn't exist[{str(data_path)}]")
    sys.exit(1)

#-----------------------
#--- Helper
#-----------------------
def slack_usage_msg():
    return "Expected message format:  <team number> <photo attachements>"

def strip(s : Optional[str]) -> Optional[str]:
    """ Strips white space from string
    """
    if s is not None:
        return s.strip()   
    return None

def error_exit(msg):
    logging.error(msg)
    logging.error(parser.format_help())
    sys.exit(1)

def slack_error(err_func, msg, print_usage=False):
    """ Sends a slack response in case of error condition 
    """
    logging.error(msg)
    err_func(f"*ERROR*: {msg}")
    if print_usage: err_func(slack_usage_msg())

def resolveUsername(usr_id : str) -> str:
    resp=app.client.users_profile_get(user=usr_id)
    if resp.get("ok", False):
        return resp.get("profile")["real_name_normalized"].encode('ascii', 'ignore')
    else:
        logging.warning("Unable to resolve user name.  Returning original user id")
        return usr_id

#-----------------------
#--- Parse tokens files
#-----------------------
try:
    with open(args.app_token_path, "r") as f:
        auth_app_token=f.read() 
        auth_app_token = strip(auth_app_token)
except FileNotFoundError as e:
    error_exit("Unable to find slack BOT token file")

try:
    with open(args.bot_token_path, "r") as f:
        auth_token=f.read() 
        auth_token = strip(auth_token)
except FileNotFoundError as e:
    error_exit("Unable to find slack APP token file")

#-----------------------
#--- Create application
#-----------------------
app = App(token=auth_token)

#-----------------------
#--- Event handlers
#-----------------------
@app.event("message")
def handle_message(event, say):
    """ Message handler call back
    """
    global img_id
    global init_time

    nfiles = len(event.get("files", []))  
    username = resolveUsername(event['user'])
    currtime = int(time.time())
    team_number = event['text'].strip()
    
    logging.info(f"Received message [user: {username}, txt: {event['text']}, nfiles: {nfiles}]")

    ts = event.get("ts", 0.0)
    if float(ts) < init_time:
        logging.warning(f"Ignoring message. Time stamp is before the expected start window. [start: {init_time}, ts: {ts}]")
        return

    if nfiles==0:
        slack_error(say, f"ERROR: No pictures were attached to the received message", print_usage=True)
        return

    if not re.match(r"^[0-9]+$", team_number):
        slack_error(say, f"The team number is either empty or doesn't match expected format [num: {team_number}]",
                    print_usage=True)
        return

    if nfiles == 0: 
        slack_error(say, "Received message without any attachments", print_usage=True)
        return
    
    for i, f in enumerate(event["files"]):
        try:
            logging.debug(f"Attempting to download file [url: {f['url_private']}]")

            u = urlparse(f["url_private"])
            p = pathlib.Path(u.path)
            r = requests.get(f["url_private"], headers={"Authorization": f"Bearer {auth_token}"})

            file_name = f"{frcEventName}-{team_number}-{currtime}-{img_id}{p.suffix}"
            dest_path = data_path / file_name
            logging.debug(f"Saving file [path: {dest_path}]")
            with open(str(dest_path), 'wb') as file:
                file.write(r.content)

            img_id+=1

        except Exception as e:
            logging.warning(f"Unable to download attachement [{e}]")
            slack_error(say, f"*ERROR*: Unable to download attachement [{i}]")
            return

    say(f"*Thank you!* Received [team: {team_number}, num_pictures: {nfiles}].")


@app.event("app_home_opened")
def handle_app_home_opened_events(body, logger):
    """ Handler for when user visits the bot home page
    """
    pass
              

#-----------------------
#--- Main
#-----------------------
if __name__ == "__main__":
    logging.info("Starting socket mode handler")
    SocketModeHandler(app, auth_app_token).start()