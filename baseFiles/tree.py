import time
import random
import os
import sys
from threading import Thread
import socket
import pickle

#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

species = "tree"
mutationChance = 5
lifespan = 10
restingTime = 30
deviationValue = 2
diseaseResistance = 10
idealTemp = 75
tempVar = 30
resourceUseTime = 10
requiredResources = [["carbonDioxide", 20]]
producedResources = [["oxygen", 20]]

def mutation(allVariables, mutationChance):
	intVariables = []
	for x in allVariables:
		if type(eval(x)) == int:
			intVariables.append(x)
			
	if mutationChance >= 1:
		mutate = random.randint(1, mutationChance)
	else:
		mutate = random.randint(mutationChance, 1)

	if mutate == 1:
		mutate = True
		changeID = random.randint(0, (len(intVariables)-1))
		changeVar = intVariables[changeID]
	else:
		mutate = False
		changeVar = None

	return mutate, changeVar
	
	
def replicate(mutate, changeVar, deviationValue):
	#creates new file
	fileName = os.path.basename(__file__)
	newFileName = species + str(random.randint(1, 99999999)) + ".py"
	newFile = open(newFileName, 'w+') 
	
	#opens file + writes to file
	with open(fileName, 'r') as file:
		for x in file:
			#checks if mutating
			if mutate:
				if ("{0} = ".format(changeVar)) in x:
					currentValue = eval(changeVar)
					deviation = currentValue / deviationValue
					newValue = round(random.gauss(currentValue, deviation))
					newLine = "{0} = {1}\n".format(changeVar, newValue)
					newFile.write(newLine)
				else:
					newFile.write(x)
			else:
				newFile.write(x)
	newFile.close()

	if sys.platform == 'win32':
		os.popen("python {0}".format(newFileName))
	else:
		os.popen("python3 {0}".format(newFileName))
	print("other file started")
	

allVariables = set(dir()) - set(dir(__builtins__))

def useResource(useTime, required, produced):
	message = [required, produced]
	HOST = 'localhost'
	PORT = 8888
	remote_ip = socket.gethostbyname(HOST)
	while True:
		time.sleep(useTime)
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((remote_ip, PORT))
		s.send(pickle.dumps(message))
		response = s.recv(1024).decode("utf-8").rstrip()
		if response == "dead":
			s.shutdown(socket.SHUT_WR)
			s.close()
			os.remove(__file__)
			os._exit(1)
		temp = int(response)
		if (idealTemp + tempVar) < temp or (idealTemp - tempVar) > temp:
			s.shutdown(socket.SHUT_WR)
			s.close()
			os.remove(__file__)
			os._exit(1)
			
		s.shutdown(socket.SHUT_WR)
		s.close()

Thread(target=useResource, args=(resourceUseTime, requiredResources, producedResources)).start()
#useResource(resourceUseTime, requiredResources, producedResources)
	
#replicates while alive
while lifespan > 0:
	time.sleep(restingTime)
	mutate, changeVar = mutation(allVariables, mutationChance)
	replicate(mutate, changeVar, deviationValue)
	lifespan-=1
os.remove(__file__)
os._exit(1)
