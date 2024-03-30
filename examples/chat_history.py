import argparse
from pathlib import Path
from slack_sdk import WebClient
import requests

#Download all past files not already downloaded from a conversation

with open(".slack_token", "r") as f:
    auth_token=f.read()

#Command line arguments
parser = argparse.ArgumentParser(
   prog="ChatHistory",
   description="Downloads files from a conversation's history")
parser.add_argument("-c", "--channel_id", type=str, default="D06QBFAUXGQ",
      help="Channel from which to retrieve files")
parser.add_argument("-e", "--event", type=str, default="frc", 
      help='Event name')
parser.add_argument("-d", "--dst_path", type=str, default="./data", 
      help='Path to where to save data')
parser.add_argument("-b", "--bot_token_path", type=str, default="./.slack_token", 
      help="Path to file which contains the Slack BOT token")
parser.add_argument("-a", "--app_token_path", type=str, default="./.slack_apptoken",
      help="Path to file which contains the Slack APP token")
parser.add_argument("-v", "--verbosity", type=int, default=1,
      help="Path to file which contains the Slack APP token")
args=parser.parse_args()

data_path = Path(args.dst_path)
client = WebClient(auth_token)
response = client.conversations_history(
   channel=args.channel_id
)
assert response["ok"]
messages = response["messages"]

for m in messages:
   text = m["text"]
   if "files" in m:
      for i, f in enumerate(m["files"]):
        r=requests.get(f["url_private"], headers={"Authorization": f"Bearer {auth_token}"})
        with open(data_path / f"{text}_{i}.{f["filetype"]}", "ab") as file:
           file.write(r.content)