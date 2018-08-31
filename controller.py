import socket
import sys
from threading import Thread
import json
import os
import shutil
import pickle

from colorama import Fore, Back, Style, init
init()

envi = json.load(open("environment.json"))
print("Environment loaded")
print(envi)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

HOST=''
PORT=8888

try:
	s.bind((HOST, PORT))
except socket.error:
	print("Error starting controller")
	sys.exit()
	
s.listen(20)
print("Controller now online")

class ControlOptions():
	def __init__(self):
		pass
	def reset(self):
		#print(os.listdir(path="baseFiles/"))
		for x in os.listdir(path="baseFiles/"):
			#print(x)
			shutil.copyfile("baseFiles/" + x, x)
		json.dump(envi, open("environment.json"))
		return envi
	def quit(self, envi):
		json.dump(envi, open("environment.json", "w"), indent=2)
		s.close()
		os._exit(1)
		
	def start(self):
		startfile = open("startfiles.txt", 'r')
		conf = input("Start all programs in startfile?(Y/n)> ").lower()
		if conf == "n":
			print("Not started")
		else:
			try:
				if sys.platform == 'win32':
					for x in startfile:
						file = x.rstrip()
						os.popen("python {0}".format(file))
				else:
					for x in startfile:
						file = x.rstrip()
						os.popen("python3 {0}".format(file))
				print("files started")	
			except:
				print("Could not start programs")
		
				
				
def controlSelect():
	protectedFiles = ["controller.py",]
	baseFiles = []
	while True:
		selectedOption = input("> ").lower()
		if selectedOption == "reset":
			ControlOptions().reset()
		elif selectedOption == "exit" or selectedOption == "quit":
			ControlOptions().quit(envi)
		elif selectedOption == "start":
			ControlOptions().start()
		elif selectedOption == "resources":
			print(envi)
		elif selectedOption == "temperature":
			newTemp = input("What temperature would you like?> ")
			try:
				newTemp = round(int(newTemp))
				if newTemp > envi["temperature"]:
					print(Fore.RED + Style.BRIGHT + "Temperature raised to {0}".format(newTemp) + Style.RESET_ALL)
				elif newTemp < envi["temperature"]:
					print(Fore.CYAN + "Temperature lowered to {0}".format(newTemp) + Style.RESET_ALL)
				else:
					print("Temperature not changed")
					#envi["temperature"] = newTemp
			except:
				print("Error, you need to input a number")

def clientConnection(conn):
	tmp = 0
	#while tmp == 1:
	conn
	data = conn.recv(1024).rstrip()
	lists = pickle.loads(data)
	#print(lists)
	required = lists[0]
	produced = lists[1]
	
	
	for x in required:
		if (envi[x[0]] - x[1]) < 0:
			conn.send("dead".encode("utf-8"))
			conn.shutdown(socket.SHUT_WR)
			conn.close()
			break
		else:
			tmp += 1
	if tmp == len(required):
		for x in required:
			envi[x[0]] -= x[1]
			
		for x in produced:
			envi[x[0]] += x[1]
			
		conn.send(str(envi["temperature"]).encode("utf-8"))
		conn.shutdown(socket.SHUT_WR)
		conn.close()
	
Thread(target=controlSelect).start()
#controlSelect()

while True:
	conn, addr = s.accept()
	Thread(target=clientConnection, args=(conn,)).start()
	
conn.close()
s.close()