#!/usr/bin/env python

import socket
import sys
import comm
import json
import os
from sys import platform as _platform
import urllib
import signal
import subprocess
import content_library
 #/Users/Roman/Music/iTunes/iTunes Media/Music

FNULL = open(os.devnull, 'w')

def send_string(cmd):
    return comm.send_string(cmd,"127.0.0.1",9002)

connectCmd = {
        "action": "connect",
        "port": 9002
}

queryCmd = {
    "action": "search",
    "value": ""
}

def playSong(song_location):
    if "darwin" in _platform:
        cmd = '/Applications/VLC.app/Contents/MacOS/VLC ' + '"' + song_location +'"'
    else:
        cmd = 'vlc ' + '"' + song_location +'"'
    print cmd
    play_proc = None
    try:
        play_proc = subprocess.Popen(cmd, stdout=FNULL, stderr=FNULL, shell=True, preexec_fn=os.setsid)
        play_till_input = raw_input("Press any key to stop song and go back to search:")
        os.killpg(play_proc.pid, signal.SIGTERM)
    except KeyboardInterrupt:
        print("Caught ctrl-c interrupt, need to kill process!")
        os.killpg(play_proc.pid, signal.SIGTERM)
        raise
    except EOFError:
        print("Caught ctrl-d interrupt, need to kill process!")
        os.killpg(play_proc.pid, signal.SIGTERM)
        raise
    except IOError:
        print("Caught IO Error")

#INTERFACE 
try:
    ip_address = raw_input("Enter the IP address of a machine on the network you are trying to connect to: ")
    response = ""
    if ip_address != "":
        connectCmd["host"] = ip_address
        response = send_string(json.dumps(connectCmd))
    while(True):
        song_name = raw_input("SEARCH: Enter a song name:")
        print("Looking for: " + song_name + " ...")
        local_results = content_library.searchFileName(song_name)
        queryCmd["value"] = song_name
        results = send_string(json.dumps(queryCmd))
        try:
            results = json.loads(results)
        except Exception, e:
            print e.message
            print results

        if results["action"] == "search_results":
            results["dict"]["127.0.0.1"] = local_results
            print "\n\tSearch results"
            print "========================================="
            flattened_results = []
            i = 1

            #print list of peers
            print "  results from %d peers" % (len(results["dict"].keys())-1)
            print "  Peers: ",
            for host in results["dict"].keys():
                if host != "127.0.0.1":
                    print host,
            print "\n========================================="

            #print matching song list
            for host, songlist in results["dict"].iteritems():
                for song in songlist:
                    flattened_results.append((host, song))
                    print str(i) + ": " + song
                    i += 1
            try:
                choice = int(raw_input("Enter your choice (a number) or blank to cancel: "))
                host, song = flattened_results[choice-1]
                url = "http://" + host + ":8080/" + urllib.quote(song)
                playSong(url)
            except ValueError, e:
                print "You must enter a number"
            except IndexError, e:
                print "That number is not a valid choice. No song exists for that index."
            except KeyboardInterrupt:
                raise
            except:
                print "An error occured."
except KeyboardInterrupt:
    None





