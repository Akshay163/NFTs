# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 15:25:44 2022

@author: pandi
"""
import os
import json
# Make sure that you are in the NFT folder

path = r"./images/cyberkongz/image_data"
os.chdir(path)

bg = []
traits = []
for i in range(1,5001):
    path = f"{i :04d}"+".json"
    guestFile = open(path,'r')
    guestData = guestFile.read()
    guestFile.close()
    gdfJson = json.loads(guestData)
    bg.append(gdfJson['background_color'])
    