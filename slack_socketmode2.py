import os
import logging
import requests
import pathlib
import slack
from urllib.parse import urlparse
from slack_sdk import WebClient
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
logging.basicConfig(level=logging.DEBUG)

with open("./slack_apptoken", "r") as f:
    auth_app_token=f.read() 

with open("./slack_token", "r") as f:
    auth_token=f.read() 

app = App(token=auth_app_token)

@app.event("message")
def handle_mention(event, say):
   logging.info("Received message!")
   logging.info(f"txt: {event}")

   if "files" in event:
     for f in event["files"]:
        logging.info(f"url:{f["url_private"]}")
        u = urlparse(f["url_private"])
        p = pathlib.Path(u.path)
        r=requests.get(f["url_private"], headers={"Authorization": f"Bearer {auth_token}"})
        with open(event["text"] + "." + f["filetype"], 'ab') as file:
           file.write(r.content)
           
#35-48: download all past files not already downloaded from a conversation
client = WebClient(auth_token)
response = client.conversations_history(
   channel=""
)
assert response["ok"]
messages = response["messages"]

for m in messages:
   text = m["text"]
   if "files" in m:
      for f in m["files"]:
        r=requests.get(f["url_private"], headers={"Authorization": f"Bearer {auth_token}"})
        with open(text+"."+f["filetype"], "ab") as file:
           file.write(r.content)


if __name__ == "__main__":
    logging.info("Starting socket mode handler")
    SocketModeHandler(app, auth_app_token).start()
