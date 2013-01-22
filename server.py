#!/usr/bin/env python

##################################
# Musical control server
# written for python3
##################################

import os
import sys
import socket
import ctypes
from threading import Thread # we'll run commands in a new thread, just in case they block

# Used to listen for connections
LISTEN_ADDRESS = ''
LISTEN_PORT = 12345
BUFFER_SIZE = 512

# Used for emulating key presses. This gives us access to user32.dll
user32 = ctypes.windll.user32
# Virtual keys
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_STOP = 0xB2
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_PLAY = 0xFA

# NOTE: bug in python, if using os.system(my_str) where my_str 
#       contains at least 2 sets of quotes, your must prefix "call" (windows only)
# Playlists
playlist_local = "call \"C:\\program files\\Windows Media Player\\wmplayer.exe\" /playlist \"Party - Jan2012\""
playlist_eh = "\"C:\\program files\\Windows Media Player\\wmplayer.exe\" http://scfire-ntc-aa04.stream.aol.com:80/stream/1025"
playlist_dm = "\"C:\\program files\\Windows Media Player\\wmplayer.exe\" http://80.94.69.106:6104/"

# Mapping expected input to actions
bytes_to_keys = {}
bytes_to_keys["1"] = VK_MEDIA_PLAY_PAUSE
bytes_to_keys["2"] = VK_MEDIA_NEXT_TRACK
bytes_to_keys["3"] = VK_MEDIA_PREV_TRACK
bytes_to_keys["4"] = VK_MEDIA_STOP
bytes_to_commands = {}
bytes_to_commands["a"] = playlist_local
bytes_to_commands["b"] = playlist_eh
bytes_to_commands["c"] = playlist_dm



def run_command(cmd):
	os.system(cmd)

def do_action(char):
	'''Takes a 1-character code and executes the action assoliated with it'''
	if char in bytes_to_keys:
		key_code = bytes_to_keys[char]
		user32.keybd_event(key_code, 0, 0, 0) # press
		user32.keybd_event(key_code, 0, 2, 0) # release
	elif char in bytes_to_commands:
		command = bytes_to_commands[char]
		# print("running command:", command)
		Thread(target=run_command, args=(command,)).start()
	else:
		print("unknown instruction:", char)


##########################################
################## Main ##################
##########################################

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((LISTEN_ADDRESS, LISTEN_PORT))
print("Starting server on port", LISTEN_PORT)
s.listen(1)


while True:
	conn, addr = s.accept()
	print('Connection address:', addr)
	try:
		while True:
			data = conn.recv(BUFFER_SIZE)
			if not data: break
			str_data = bytes.decode(data) # data is non-unicode, but all python strings need to be
			print("received data: \"{0}\"".format(str_data))
			for char in str_data: # highly unlikely, but crazier things have happened
				do_action(char)
		print("Client disconnected")
	except socket.error as e:
		print("Socket error:", e)
	except socket.timeout:
		print("Connection timed-out")
	except Exception as e:
		print("Exception:", e)
	finally:
		conn.close()
print("Exit")
