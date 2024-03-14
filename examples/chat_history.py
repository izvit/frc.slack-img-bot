from slack_sdk import WebClient
import requests

#Download all past files not already downloaded from a conversation

with open("./slack_token", "r") as f:
    auth_token=f.read() 

client = WebClient(auth_token)
response = client.conversations_history(
   channel="D06NVHY9DJQ"
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