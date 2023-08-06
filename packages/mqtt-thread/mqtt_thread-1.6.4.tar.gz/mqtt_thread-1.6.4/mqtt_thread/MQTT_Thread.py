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
import datetime
import os
import csv

def creationFichier(nomFichier,key,erase): # exemple nomFichier = 'donnees' pas d'extension
    if (len(key)==1):
        if (not os.path.exists(nomFichier + ".csv") or erase):
            with open(nomFichier + ".csv", 'w', newline='') as file:
                writer = csv.writer(file, delimiter=';',quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
                #date = [datetime.datetime.now()]
                champs = ["date"]
                for j in range(0,len(key[0])):
                    champs.append(key[0][j])
                champs.append("tps-secondes")
                writer.writerow(champs)
    else:
        for i in range(0,len(key)):
            if (not os.path.exists(nomFichier + "_" + str(i)+ ".csv") or erase):
                with open(nomFichier + str(i)+ "csv", 'w', newline='') as file:
                    writer = csv.writer(file, delimiter=';',quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
                    #date = [datetime.datetime.now()]
                    champs = ["date"]
                    for j in range(0,len(key[i])):
                        champs.append(key[i][j])
                    champs.append("tps-secondes")
                    writer.writerow(champs)

def enregistreFichier(nomFichierComplet,tab1): # exemple nomFichier = 'donnees0.csv' key_i est une liste par ex : ["ecl","temps"]    
    with open(nomFichierComplet, 'a', newline='') as file:
            writer = csv.writer(file, delimiter=';',quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(tab1)

# fonction qui retourne une chaine aléatoire
def randomword(length):
    lettresEtChiffres = string.ascii_letters + string.digits
    chaineAleatoire = ''.join((random.choice(lettresEtChiffres) for i in range(length)))
    return chaineAleatoire

# fonction qui retourne une liste de listes pour les données à afficher. mytab est une liste de listes. 
# exemple : mytab = [["ecl","temps"],["pression",temperature,humidite]]
def createData(mytab):
        mydata = [[] for i in range(0,len(mytab))]
        for i in range(len(mytab)):
            mydata[i] = [[] for i in range(0,len(mytab[i])+1)] # ajout du temps de reception en dernier
        return mydata

class MQTT_Thread (threading.Thread):
    def __init__(self, url, port, user, pwd,proto ="websockets"):      # données supplémentaires
        threading.Thread.__init__(self)  # ne pas oublier cette ligne
        # (appel au constructeur de la classe mère)
        self.url = url           # donnée supplémentaire ajoutée à la classe
        self.port = port
        self.user = user
        self.pwd = pwd
        self.data = [] # contient les données sous forme de listes
        self.msg = '' # dernier json message reçu
        self.lastLinedata = "" # contient la dernière ligne des données selectionnées
        self.nomFichier = "donnees" # sans extension csv
        self.record = False
        self.eraseFile = True
        self.verbose = True
        self.maxData = 500 # nombre de données à afficher
        self.transport = proto #'websockets' # ou "tcp"
        self.Key = []
        self.tempsDepart = time.time() #en secondes
        self.temps = 0 # en secondes
        #self.topic = "/#"
        self.topic = []
        self.client = mqtt.Client(client_id= randomword(8),clean_session=True,protocol=mqtt.MQTTv311,transport=self.transport) # transport="tcp" pour ssl)
        self.client.username_pw_set(username=self.user,password=self.pwd)
        self.client.tls_set(tls_version=ssl.PROTOCOL_TLSv1_2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        

    def run(self):
        if self.record == True:
            creationFichier(self.nomFichier,self.Key,self.eraseFile)
        self.client.connect(self.url, self.port, 60)
        self.client.loop_forever()
        
    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        if self.verbose:
            print("Connected with result code "+str(rc))
        # Subscribing in on_connect()
        for i in range(len(self.topic)): 
            self.client.subscribe(self.topic[i])

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        Msg = msg.payload.decode("utf-8").strip('\r\n') # decode et enlève les \r \n
        #print("message reçu")
        
        try:
            y = json.loads(Msg)
            self.msg = y
            for i in range(0,len(self.Key)):
                tab = []
                temps_lu = False # pour rajouter le temps de reception une seule fois
                for j in range(0,len(self.Key[i])):
                    if self.Key[i][j] in y:
                        tab.append(y[self.Key[i][j]])
                        self.data[i][j].append(y[self.Key[i][j]])# prends la valeur des clés
                        
                        if temps_lu == False:
                            self.temps = round(time.time()-self.tempsDepart,2) # en secondes
                            #print("temps",self.temps)
                            self.data[i][len(self.Key[i])].append(self.temps) # ajout dutemps de reception en secondes
                            temps_lu = True

                        if (len(self.data[i][0]) > self.maxData) :
                            self.data[i][j].pop(0) # enlève le 1er élément de la liste self.data[i] 
                            self.data[i][len(self.Key[i])].pop(0)
                #print("tab",tab)
                if tab != []:
                    tab.append(self.temps)
                    date = [datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")]
                    tab1 = date + tab
                    self.lastLinedata = tab1
                    if self.record:
                        #print(tab)
                        if (len(self.Key)==1):
                            enregistreFichier(self.nomFichier + ".csv",self.lastLinedata)
                        else:
                            enregistreFichier(self.nomFichier+"_"+str(i) +".csv",self.lastLinedata)
                    self.messageArrived()# fonction qui est lancée quand un message arrive et qui peut être personnalisée pour l'instance
                    # par défaut cette fonction self.messageArrived() ne fait rien

        except:
            if self.verbose:
                print("pas de clé demandée sur -> ",self.msg)
        else:
            if self.verbose:
                print(self.msg)

        """ self.messageArrived()# fonction qui est lancée quand un message arrive et qui peut être personnalisée pour l'instance
         # par défaut cette fonction self.messageArrived() ne fait rien """

    def selectTopic(self,top):
        self.topic = top
    
    def selectKey(self,tab): # exemple : tab = [["ecl","temps"],["pression",temperature,humidite]]
        #list = []
        self.data = createData(tab) # création de data liste de listes vide
        self.Key = tab # clés à récupérer
    
    def reset_time(self):
        self.tempsDepart = time.time() #en secondes
    
    def selectMaxData(self,Nbmax):
        self.maxData = Nbmax
        
    def selectNomFichier(self,nomFic):
        #list = []
        self.nomFichier = nomFic

    def Record(self,val):
        self.record = val

    def messageArrived(self):# fonction vide à personnaliser.... dans l'instance.
        pass

    def stop(self):
        print('La connexion MQTT est fermée.')
        self.client.disconnect()
        print('Le thread va être arrêté !')
