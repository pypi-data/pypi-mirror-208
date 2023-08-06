import threading
import time
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import ssl
#import base64
import random, string
#import math
import json
import time
import csv
#import os
import datetime

# fonction qui retourne une chaine aléatoire
def randomword(length):
    lettresEtChiffres = string.ascii_letters + string.digits
    chaineAleatoire = ''.join((random.choice(lettresEtChiffres) for i in range(length)))
    return chaineAleatoire

def creationFichier(nomFichier,champs): # exemple nomFichier = 'donnees.csv' 
    with open(nomFichier, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';',quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        #date = [datetime.datetime.now()]
        champs = ["date"] + champs
        writer.writerow(champs)

def enregistreFichier(nomFichier,champs,tab1): # exemple nomFichier = 'donnees.csv' 
    #if not os.path.exists(nomFichier):
    #    with open(nomFichier, 'w', newline='') as file:
    #        writer = csv.writer(file, delimiter=';',quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
    #        #date = [datetime.datetime.now()]
    #        champs = ["date"] + champs
    #        writer.writerow(champs)
    #else :
    with open(nomFichier, 'a', newline='') as file:
        writer = csv.writer(file, delimiter=';',quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        date = [datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")]
        tab1 = date +tab1
        writer.writerow(tab1)
       #    i+=1

# fonction qui retourne une liste de listes pour les données à afficher. mytab est une liste de listes. 
# exemple : mytab = [["ecl","temps"],["pression",temperature,humidite]]
def createData(mytab):
        mydata = [[] for i in range(0,len(mytab))]
        for i in range(len(mytab)):
            mydata[i] = [[] for i in range(0,len(mytab[i])+1)] # ajout du temps de reception en dernier
        return mydata

class MQTT_Thread (threading.Thread):
    def __init__(self, url, port, user, pwd, proto):      # données supplémentaires
        threading.Thread.__init__(self)  # ne pas oublier cette ligne
        # (appel au constructeur de la classe mère)
        self.url = url           # donnée supplémentaire ajoutée à la classe
        self.port = port
        self.user = user
        self.pwd = pwd
        self.data = [] # contient les données sous forme de listes
        self.msg = '' # dernier json message reçu
        self.nomFichier = "donnees.csv"
        self.record = False
        self.maxData = 500
        self.proto = proto 
        self.Key =[]# pour selection des clefs des données voulues
        self.tempsDepart = time.time() #en secondes
        self.temps = 0 # en secondes
        self.topic = []
        self.client = mqtt.Client(client_id= randomword(8),clean_session=True,protocol=mqtt.MQTTv311,transport=self.proto) # transport="tcp" ou "websockets" )
        self.client.username_pw_set(username=self.user,password=self.pwd)
        self.client.tls_set(tls_version=ssl.PROTOCOL_TLSv1_2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        

    def run(self):
        creationFichier(self.nomFichier,self.Key)
        self.client.connect(self.url, self.port, 60)
        self.client.loop_forever()
        
    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
      print("Connected with result code "+str(rc))
      # Subscribing in on_connect()
      for i in range(len(self.topic)): 
         self.client.subscribe(self.topic[i])

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        self.msg = msg.payload.decode("utf-8").strip('\r\n') # decode et enlève les \r \n
        self.messageArrived()# fonction qui est lancée quand un message arrive et qui peut être personnalisée pour l'instance
        # par défaut cette fonction self.messageArrived() ne fait rien
        
        #print("message reçu")
        tab = []
        # rajouter si len(self.Key != 0)
        try:
            y = json.loads(self.msg)
            if len(self.Key) != 0:
                for i in range(0,len(self.Key)):
                    if self.Key[i] in y :
                        tab.append(float(y[self.Key[i]]))# prends la valeurs ecl self.data[i] est une liste !!!!!
                        self.data[i].append(tab[i])
                if (len(self.data[0]) > self.maxData) :
                    for i in range(0,len(self.Key)):
                        self.data[i].pop(0) # enlève le 1er élément de la liste self.data[i] 
        except:
            print("-- except key json : ",self.msg)
        else:
            print(self.msg)
            if self.record :
                enregistreFichier(self.nomFichier,self.Key,tab)
            #for i in range(len(tab)): 
            #    self.data[i].append(tab[i])
            
    def selectTopic(self,top):
        self.topic = top
    
    def selectKey(self,tab): #pour sélection des clés des données voulues utilisé pour tracer une courbe, enregistre dans self.data
        self.data = [[] for i in range(0,len(tab))] # self.data est une liste de listes !!!!!!
        self.Key = tab
        
    def selectMaxData(self,Nbmax):
        self.maxData = Nbmax
        
    def selectNomFichier(self,nomFic):
        #list = []
        self.nomFichier = nomFic

    def Record(self,val):
        self.record = val
    
    def messageArrived(self):# fonction vide à personnaliser.... dans l'instance.
        pass

