#!/bin/sh

# Tyler Coffman, Roman Kazarin
# CS 176B Winter 2015
# Communications module

import socket
import logging
import asyncore
import json
import content_library
import sys

LISTEN_PORT = 9002
peers = {}

library = content_library.MediaLibrary()

BUFFER_SIZE = 8192

socket_error_message = {
	"action" : "socket_error"
	}

ack_message = {
	"action" : "ack"
	}

#
def recv_json(connection):
    data = ""
    done = False
    while done == False:
        try:
            data = data + connection.recv(BUFFER_SIZE)
            if len(data) == 0:
                done = True
                break
            result = json.loads(data)
            done = True
            break
        except ValueError, e:
            continue
    return data

#PROTIP: don't have a media library that takes more than 100MB to represent
#TODO: rename send_string to send_json_string because it doesn't work with anything but json strings
def send_string(message,TCP_IP, TCP_PORT):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    try:
        s.connect((TCP_IP, TCP_PORT))
        s.send(message)
        data = recv_json(s)
        s.close()
        return data
    except socket.error, e:
        if TCP_IP in peers:
            del peers[TCP_IP]
        print e.message
        print "Caught socket exception error. TCP_IP: " + TCP_IP + " TCP_PORT: " + str(TCP_PORT) + "\n"
        return json.dumps(socket_error_message)

class commHandler(asyncore.dispatcher_with_send):
    def __init__(self,sock,addr):
        asyncore.dispatcher_with_send.__init__(self,sock)
        self.addr = addr

    def handle_read(self):
        data = recv_json(self)
        if data:
            try:
                cmd = json.loads(data)
                if self.addr[0] == "127.0.0.1":
                    self.handle_local_command(cmd,data)
                else:
                    self.handle_remote_request(cmd,data)
            except ValueError:
                print "Failed to parse JSON from data stream."

    def handle_local_command(self,cmd,data):
        if cmd["action"] == "connect":
            #get the response text from the other peer
            response_text = send_string(data,cmd["host"],cmd["port"])
            #convert response to JSON
            response = json.loads(response_text)
            if response["action"] == "peerlist":
                #set our peer list to be what was returned, because if contacting any of them fails, send_string will
                #will remove them from the peer list
                global peers
                peers = response["peerlist"]
                #for ip_address, port in peers.copy().iteritems():
                #    newCmd = { "action": "connect", "host": ip_address, "port": port }
                #    send_string(json.dumps(newCmd), ip_address, LISTEN_PORT)
                peers[cmd["host"]] = cmd["port"]
            self.socket.sendall(json.dumps(peers))
        elif cmd["action"] == "search":
            search_results = {
                "action": "search_results",
                "dict": {}
            }
            for ip_address, port in peers.copy().iteritems():
                response_text = send_string(data, ip_address, LISTEN_PORT)
                response_json = json.loads(response_text)
                if(response_json["action"] == "search_results"):
                    search_results["dict"][ip_address] = response_json["list"]      
            self.socket.sendall(json.dumps(search_results))
        else:
            error_response = { "action": "error", "message": "invalid_action" }
            self.socket.sendall(json.dumps(error_response))

    def handle_remote_request(self,cmd,data):
        if cmd["action"] == "connect":
            #TODO make sure we don't tell a peer to put themselves in their own peerlist.
            newCmd = {
                "action" : "peerlist",
                "peerlist" : peers.copy() }
            if self.addr[0] in newCmd["peerlist"]:
                del newCmd["peerlist"][self.addr[0]]
            self.socket.sendall(json.dumps(newCmd))
            #now re-send peerlist to all peers.
            peers[self.addr[0]] = self.addr[1]
            for ip_address, port in peers.copy().iteritems():
            	newCmd["peerlist"] = peers.copy()
            	if ip_address in newCmd["peerlist"]:
            		del newCmd["peerlist"][ip_address]
            	if ip_address != self.addr[0]:
					send_string(json.dumps(newCmd), ip_address, LISTEN_PORT)
        elif cmd["action"] == "search":
            searchResults = {
                "action": "search_results",
                "list": content_library.searchFileName(cmd["value"])
            }
            self.socket.sendall(json.dumps(searchResults))
        elif cmd["action"] == "peerlist":
        	peers.update(cmd["peerlist"])
        	self.socket.sendall(json.dumps(ack_message))
        else:
            error_response = { "action": "error", "message": "invalid_action" }
            self.socket.sendall(json.dumps(error_response))
        peers[self.addr[0]] = self.addr[1] #add this peer to peer map

class StreamServer(asyncore.dispatcher):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(("",port))
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            handler = commHandler(sock,addr)

def main():
    server = StreamServer("localhost", LISTEN_PORT)
    asyncore.loop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        None
    except socket.error:
        print "Communications service crashed. Terminating"
        raise KeyboardInterrupt


