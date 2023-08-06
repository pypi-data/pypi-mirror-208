#mqtt_Thread <br />

Connexion à un server mqtt via un thread <br />
Envoi et réception des messages mqtt en Python <br />
Sauvegarde des données reçues au format csv <br />

INSTALLATION :<br />
		py -m pip install mqtt_thread<br />
		ou <br />
		py -m pip install mqtt_thread==x.x.x (mettre numéro de version)<br />

exemple :<br />
Trace de graphe mathPlotlib temps réel<br />

---------------------<br />
import matplotlib.pyplot as plt<br />
import matplotlib.animation as animation<br />
from matplotlib import style<br />
from matplotlib.ticker import FormatStrFormatter<br />
import numpy as np<br />
import time<br />
import mqtt_thread as MQTT # bibliothèque pypi<br />

# Creation de la figure pour la charge<br />
fig = plt.figure(num=1, figsize=(10, 6), dpi=120, facecolor='w', edgecolor='k')# configuration du graphe<br /> 
ax = fig.add_subplot(1, 1, 1)<br />
labelGraphe = "Titre du graphe"<br />


def messageArrived(): # fonction appelée par le thread MQTT quand un message arrive<br />
    if m.verbose:<br />
        print("msg arrivé")<br />
        try:<br />
            print("temp : ",m.lastLinedata[1])<br />
        except:   <br /> 
            print("pas de dernière ligne")<br />

def acquisition(i, xs, ys):<br />
    # Dessine les graphes<br />
        ax.clear()<br />
        ax.plot(xs, ys, 'r-o', label=labelGraphe)<br />
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))<br />
    # Format du graphe<br />
        plt.xticks(rotation=45, ha='right')# rotation et alignement du texte axe x<br />
        plt.subplots_adjust(bottom=0.20)<br />
        plt.title('Graphe temps réel avec Python')<br />
        plt.ylabel('Valeur 1')<br />
        plt.xlabel('temps (s)')<br />
        plt.legend()<br />
        plt.grid()# la grille sera affichée<br />

m = MQTT.MQTT_Thread("mqtt.url.fr",443,"login","pwd")        # crée le thread<br />
m.selectTopic(["node_iot2020/#","FABLAB_21_22/contes/bureau/temperature/out/"])  # topics auxquels on s'abonne<br />
m.selectKey([["ecl","temps"],["temp","pression"]]) # selection des clés des données voulues , les données seront dans m.data[0][], m.data[1][],... <br />
# le dernier élement de m.data[i] est le temps de réception du message en secondes (donné par python avec la fonction time)<br />
m.messageArrived = messageArrived # personnalisation fonction qui sera appelée à chaque réception de message<br />
m.nomFichier = "donnees" # nom du fichier csv sans extension qui enregistrera les données<br />
m.record = True # enregistre les données dans un fichier csv<br />
m.eraseFile = True # efface le fichier csv avant d'enregistrer les données<br />
m.verbose = True # affiche les messages MQTT<br />
m.start()                  # démarre le thread, (exécution indépendante du programme principal)<br />
time.sleep(1)<br />
#m.client.publish("node_iot2020/test/in",payload="{\"pression\":1024}",qos=0)#publication d'un message vers MQTT <br />

# Appelle la fonction animation périodiquement <br />
#m.data[0][1] est une liste !!!<br />
ani = animation.FuncAnimation(fig, acquisition, fargs=(m.data[1][2], m.data[1][0]), frames=20,interval=1000,repeat=True)# intervall temps en ms entre 2 animations<br />
plt.show()<br />


