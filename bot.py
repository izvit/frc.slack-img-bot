import os
import logging
import requests
import pathlib
from urllib.parse import urlparse
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
logging.basicConfig(level=logging.DEBUG)

with open(".slack_apptoken", "r") as f:
    auth_app_token=f.read() 

with open(".slack_token", "r") as f:
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
        with open(p.name, 'wb') as file:
           file.write(r.content)


if __name__ == "__main__":
    logging.info("Starting socket mode handler")
    SocketModeHandler(app, auth_app_token).start()