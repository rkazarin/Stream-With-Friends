# Stream-With-Friends
by Roman Kazarin and Tyler Coffman

A P2P music streaming application that allows a group of users to share their music libraries with each other.

Installation Requiremenets:
- Only Mac OS X and Linux OS supported
- [VLC](http://www.videolan.org/vlc/index.html) must be installed
- python 2.7
- ports 9002 and 8080 open

The following screenshot shows an example of a swarm with 3 nodes. The shown user queries an empty string, which shows all files contained across all peers in the swarm. The user then decides he wants to stream song 1, which is actually located on peer 128.111.43.47's machine.

![Screenshot1](https://github.com/rkazarin/Stream-With-Friends/raw/master/screenshots/sample_screenshot1.png)

