#!/usr/bin/python
import os 
import time
import signal
import subprocess
import sys
import atexit

cmd1 = "python edna.py"
cmd2 = "python comm.py"
cmd3 = "python cli.py"

edna_proc = None # the mp3 http server
comm_proc = None
cli_proc = None

FNULL = open(os.devnull, 'w')

def cleanup_method():
    os.killpg(edna_proc.pid, signal.SIGINT)
    os.killpg(comm_proc.pid, signal.SIGINT)
atexit.register(cleanup_method)

try:
    os.chdir("./edna-0.6/")
    print("Loading mp3 server...")
    edna_proc = subprocess.Popen(cmd1, stdout=FNULL, stderr=FNULL, shell=True, preexec_fn=os.setsid)
    time.sleep(2)
    os.chdir("../")
    print("Loading comm...")
    comm_proc = subprocess.Popen(cmd2, shell=True, preexec_fn=os.setsid)
    time.sleep(2)
    print("Starting cli...")
    cli_proc = subprocess.Popen(cmd3, stdout=sys.stdout, stdin=sys.stdin, shell=True)
    cli_proc.wait()
except KeyboardInterrupt:
    print("\nExiting the application. Goodbye.\n")
    sys.exit(0)
except EOFError:
    print("\nExiting the application. Goodbye.\n")
    sys.exit(0)

    

