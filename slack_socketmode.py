import os
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
logging.basicConfig(level=logging.DEBUG)

with open(".slack_apptoken", "r") as f:
    auth_token=f.read() 

# Install the Slack app and get xoxb- token in advance
app = App(token=auth_token)

@app.event("message")
def handle_mention(event, say):
   logging.info("Received message!")


if __name__ == "__main__":
    logging.info("Starting socket mode handler")
    SocketModeHandler(app, auth_token).start()