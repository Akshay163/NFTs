# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 00:48:50 2022

@author: pandi
"""
import requests
import os
os.chdir(r"D:/NFTs") # Change directory accordingly
import json
import math
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

# This is where you add the collection name to the URL
CollectionName = "Cyberkongz".lower()

# Random User Agent
software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
user_agent = user_agent_rotator.get_random_user_agent()

# Headers for the request. Currently this is generating random user agents
# Use a custome header version here -> https://www.whatismybrowser.com/guides/the-latest-user-agent/
headers = {
      'User-Agent': user_agent
  }

# Get information regarding collection

collection = requests.get(f"http://api.opensea.io/api/v1/collection/{CollectionName}?format=json")

if collection.status_code == 429:
    print("Server returned HTTP 429. Request was throttled. Please try again in about 5 minutes.")

if collection.status_code == 404:
    print("NFT Collection not found.\n\n(Hint: Try changing the name of the collection in the Python script, line 6.)")
    exit()


collectioninfo = json.loads(collection.content.decode())

# Create image folder if it doesn't exist.

if not os.path.exists('./images'):
    os.mkdir('./images')

if not os.path.exists(f'./images/{CollectionName}'):
    os.mkdir(f'./images/{CollectionName}')

if not os.path.exists(f'./images/{CollectionName}/image_data'):
    os.mkdir(f'./images/{CollectionName}/image_data')

# Get total NFT count

count = int(collectioninfo["collection"]["stats"]["count"])

# Opensea limits to 50 assets per API request, so here we do the division and round up.

iter = math.ceil(count / 50)

print(f"\nBeginning download of \"{CollectionName}\" collection.\n")

# Define variables for statistics

stats = {
"DownloadedData": 0,
"AlreadyDownloadedData": 0,
"DownloadedImages": 0,
"AlreadyDownloadedImages": 0,
"FailedImages": 0
}

# Iterate through every unit
for i in range(iter):
    offset = i * 50
    data = json.loads(requests.get(
                f"https://api.opensea.io/api/v1/assets?order_direction=asc&offset={offset}"
                f"&limit=50&collection={CollectionName}&format=json", headers=headers).content.decode())

    if "assets" in data:
        for asset in data["assets"]:
          formatted_number = f"{int(asset['token_id']):04d}"

          print(f"\n#{formatted_number}:")

          # Check if data for the NFT already exists, if it does, skip saving it
          if os.path.exists(f'./images/{CollectionName}/image_data/{formatted_number}.json'):
              print(f"  Data  -> [\u2713] (Already Downloaded)")
              stats["AlreadyDownloadedData"] += 1
          else:
                # Take the JSON from the URL, and dump it to the respective file.
                dfile = open(f"./images/{CollectionName}/image_data/{formatted_number}.json", "w+")
                json.dump(asset, dfile, indent=3)
                dfile.close()
                print(f"  Data  -> [\u2713] (Successfully downloaded)")
                stats["DownloadedData"] += 1

          # Check if image already exists, if it does, skip saving it
          if os.path.exists(f'./images/{CollectionName}/{formatted_number}.png'):
              print(f"  Image -> [\u2713] (Already Downloaded)")
              stats["AlreadyDownloadedImages"] += 1
          else:
            if not asset["image_url"] is None:
                image = requests.get(asset["image_url"])

          # If the URL returns status code "200 Successful", save the image into the "images" folder.
            if image.status_code == 200:
                file = open(f"./images/{CollectionName}/{formatted_number}.png", "wb+")
                file.write(image.content)
                file.close()
                print(f"  Image -> [\u2713] (Successfully downloaded)")
                stats["DownloadedImages"] += 1
            # If the URL returns a status code other than "200 Successful", alert the user and don't save the image
            else:
                print(f"  Image -> [!] (HTTP Status {image.status_code})")
                stats["FailedImages"] += 1
                continue

print(f"""
Finished downloading collection.
Statistics
-=-=-=-=-=-
Total of {count} units in collection "{CollectionName}".
Downloads:
  JSON Files ->
    {stats["DownloadedData"]} successfully downloaded
    {stats["AlreadyDownloadedData"]} already downloaded
  Images ->
    {stats["DownloadedImages"]} successfully downloaded
    {stats["AlreadyDownloadedImages"]} already downloaded
    {stats["FailedImages"]} failed
You can find the images in the images/{CollectionName} folder.
The JSON for each NFT can be found in the images/{CollectionName}/image_data folder.
Press enter to exit...""")
input()
