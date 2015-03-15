#!/bin/sh

# Tyler Coffman, Roman Kazarin
# CS 176B Winter 2015
# Media library module

import os
import sys

music_dir = "./Music"
if(os.path.isdir(music_dir) == False):
    print ("Error: the directory 'Music' must exist in the current working directory")
    sys.exit(0)

class MediaLibrary:
    def __init__(self):
        self.library = ["item1", "item2"]

def searchFileName(song_name):
    result = []
    for root, dirs, files in os.walk(music_dir):
        for f in files:
            relativeDir = os.path.relpath(root,music_dir)
            filename = os.path.join(relativeDir, f)
            if(f.endswith('.mp3') and song_name in filename):
                result.append(filename)
    return result
