#----#----# import des modules #----#----#
from mpl_toolkits.basemap import Basemap
from win32api import GetSystemMetrics   #module utile pour obtenir les dimensions de l'écran 
from pygame.locals import * #import des variables utiles pour le module pygame (exemple : K_ESCAPE signifie la touche echap)
from random import choice
from time import time, sleep
import matplotlib.pyplot as plt #utile pour afficher la carte
import numpy as np
import threading
import pyautogui #utile pour obtenir la couleur du pixel que pointe la sourie
import keyboard  #utile pour savoir si on appui sur espace (lorsque la carte est affiché)
import requests    #module pour faire les requêtes à l'API
import pygame      #module pour l'interface graphique de Pygame
import sys
import os
#----#----# variables/listes #----#----#
with open('api_key.txt', 'r') as f: #récupération de la clé dans le fichier api_key.txt (ce fichier n'est pas disponible dans le github)
    api_key = f.read()

size_screen = (GetSystemMetrics(0)//2,4*GetSystemMetrics(1)//5) #on force la taille de l'écran dans un format personnalisé
#size_screen = (2100 //2,4*1181//5) #test avec d'autre taille d'écran 
#on utilisera size_screen pour adapter la taille des objets en fonction de la taille de l'écran de l'utilisateur au démarrage de l'application
hold_clic = False #variable utilisée pour éviter de rester appuyer lors d'un clic sourie
all_processed_data = {  #Dictionnaire pour stocker les données de l'API exploitées (les calculs se feront dans la fonction calc_all_analytic_data())
    "Nombre de ville" : 0,
    "Nombre de stations" : 0,
    "banking True" : 0,
    "banking False" : 0,
    "Bonus True" : 0,
    "Bonus False" : 0,
    "Status OPEN" : 0,
    "Status CLOSED" : 0,
    "Connecté True" : 0,
    "Connecté False" : 0,
    "Overflow True" : 0,
    "Overflow False" : 0,
    "Vélo" : 0,
    "Stands" : 0,
    "Vélo mécanique" : 0,
    "Vélo électrique" : 0,
    "Nombre station par ville" : {} #à chaque nouvelle ville, on rajoute un objet de ce format : "lyon" : 0
}
list_ranking_data = [] #dictionnaire qui va contenir le classement 
jump_ville_scroll = 0 #variable utile pour descendre dans les nombres de stations par villes (l'idée est de simuler une descente des textes en n'affichant ou pas les premières villes)
jump_station_scroll = 0 #variable utile pour descendre dans les nombres de stations par stations (l'idée est de simuler une descente des textes en n'affichant ou pas les premières stations)
jump_total_scroll = 0 
width_scroll_bar_general_data = 0 #variable utile pour la taille de la scroll bar pour la page general_data
position_y_scroll_bar_general_data = 0 #variable utile pour la position de la scroll bar pour la page general_data
width_scroll_bar_general_data_leftPart = 0 
position_y_scroll_bar_general_data_leftPart = 0
width_scroll_bar_ranking_data = 0 #variable utile pour la taille de la scroll bar pour la page ranking_data 
position_y_scroll_bar_ranking_data = 0 #variable utile pour la position de la scroll bar pour la page ranking_data
list_info_arrow_ranking = [] #liste qui contient les information pour les flèches de la page de classement des données
ind_choice_map_parameter_type_map = 0
ind_choice_map_parameter_resolution = 1
while_loading_map = [False]
info_map_loop = [False]
data_stations_map = []
data_colors_map = []
text_info_station = [ #information affiché lors d'une sélection de station sur la carte
    {"nom" : "Nom", "info" : ""},
    {"nom" : "Ville", "info" : ""},
    {"nom" : "Addresse", "info" : ""},
    {"nom" : "Banking", "info" : ""},
    {"nom" : "Bonus", "info" : ""},
    {"nom" : "Connecté", "info" : ""},
    {"nom" : "Overflow", "info" : ""},
    {"nom" : "Vélo", "info" : ""},
    {"nom" : "Stands", "info" : ""},
    {"nom" : "Vélo mécanique", "info" : ""},
    {"nom" : "Vélo électrique", "info" : ""},
    {"nom" : "Vélos électriques à batterie interne", "info" : ""},
    {"nom" : "vélos électriques à batterie amovible", "info" : ""},
    {"nom" : "Status", "info" : ""},
    {"nom" : "Date mis à jour", "info" : ""},
]
hexa_color_select_map = "------"
#variables des boucles pour l'interface graphique
main_loop = True
general_data = True
ranking_data = False
map_loop = False




#----#----# fonctions auxiliaire #----#----#
#fonction pour convertir une longueur du format 960x864 au format de l'écran de l'utilisateur
def conv_sizex(x):
    return int(size_screen[0]*x/960)
def conv_sizey(y):
    return int(size_screen[1]*y/864)

#fonction qui initialise la liste list_info_arrow_ranking
def calc_list_list_info_arrow_ranking() :
    list_info_arrow_ranking = [ #liste qui contient les information pour les flèches de la page de classement des données
        {
            "coordX_left" : conv_sizex(930)//8-conv_sizex(22), 
            "coordX_right" : conv_sizex(930)//8-conv_sizex(22)+size_screen[0]//76.8,
            "nom" : "name",
            "reverse" : False
        },
        {
            "coordX_left" : conv_sizex(930)//8-conv_sizex(7), 
            "coordX_right" : conv_sizex(930)//8-conv_sizex(7)+size_screen[0]//76.8,
            "nom" : "name",
            "reverse" : True
        },
        {
            "coordX_left" : 2*conv_sizex(930)//8+conv_sizex(5), 
            "coordX_right" : 2*conv_sizex(930)//8+conv_sizex(5)+size_screen[0]//76.8,
            "nom" : "contractName",
            "reverse" : False
        },
        {
            "coordX_left" : 2*conv_sizex(930)//8+conv_sizex(21), 
            "coordX_right" : 2*conv_sizex(930)//8+conv_sizex(21)+size_screen[0]//76.8,
            "nom" : "contractName",
            "reverse" : True
        },
        {
            "coordX_left" : 3*conv_sizex(930)//8-conv_sizex(46), 
            "coordX_right" : 3*conv_sizex(930)//8-conv_sizex(46)+size_screen[0]//76.8,
            "nom" : ["bikes"],
            "reverse" : False
        },
        {
            "coordX_left" : 3*conv_sizex(930)//8-conv_sizex(30), 
            "coordX_right" : 3*conv_sizex(930)//8-conv_sizex(30)+size_screen[0]//76.8,
            "nom" :  ["bikes"],
            "reverse" : True
        },
        {
            "coordX_left" : 4*conv_sizex(930)//8-conv_sizex(51), 
            "coordX_right" : 4*conv_sizex(930)//8-conv_sizex(51)+size_screen[0]//76.8,
            "nom" : ["stands"],
            "reverse" : False
        },
        {
            "coordX_left" : 4*conv_sizex(930)//8-conv_sizex(35), 
            "coordX_right" : 4*conv_sizex(930)//8-conv_sizex(35)+size_screen[0]//76.8,
            "nom" : ["stands"],
            "reverse" : True
        },
        {
            "coordX_left" : 5*conv_sizex(930)//8-conv_sizex(75), 
            "coordX_right" : 5*conv_sizex(930)//8-conv_sizex(75)+size_screen[0]//76.8,
            "nom" : ["mechanicalBikes"],
            "reverse" : False
        },
        {
            "coordX_left" : 5*conv_sizex(930)//8-conv_sizex(59), 
            "coordX_right" : 5*conv_sizex(930)//8-conv_sizex(59)+size_screen[0]//76.8,
            "nom" : ["mechanicalBikes"],
            "reverse" : True
        },
        {
            "coordX_left" : 6*conv_sizex(930)//8-conv_sizex(71), 
            "coordX_right" : 6*conv_sizex(930)//8-conv_sizex(71)+size_screen[0]//76.8,
            "nom" : ["electricalBikes"],
            "reverse" : False
        },
        {
            "coordX_left" : 6*conv_sizex(930)//8-conv_sizex(55), 
            "coordX_right" : 6*conv_sizex(930)//8-conv_sizex(55)+size_screen[0]//76.8,
            "nom" : ["electricalBikes"],
            "reverse" : True
        },
        {
            "coordX_left" : 7*conv_sizex(930)//8-conv_sizex(54), 
            "coordX_right" : 7*conv_sizex(930)//8-conv_sizex(54)+size_screen[0]//76.8,
            "nom" : "status",
            "reverse" : False
        },
        {
            "coordX_left" : 7*conv_sizex(930)//8-conv_sizex(38), 
            "coordX_right" : 7*conv_sizex(930)//8-conv_sizex(38)+size_screen[0]//76.8,
            "nom" : "status",
            "reverse" : True
        }
    ]
    return list_info_arrow_ranking

#fonction pour exploiter les données de l'API
def calc_all_analytic_data() :
    #on commence par réinitialiser les calculs précédent
    for key in all_processed_data.keys() :
        if key == "Nombre station par ville" :
            all_processed_data[key] = {}
        else :
            all_processed_data[key] = 0

    https = f"https://api.jcdecaux.com/vls/v3/stations?apiKey={api_key}" #URL
    data = requests.get(https).json() #On effectue une requête https avec get puis on le transforme au format json
    for sub_data in data : #boucle qui parcoure toutes les stations
        all_processed_data["Nombre de stations"]+=1
        #compte des effectifs des stations. Le f string permet d'incrémenter directement la bonne variable "bonus False" ou "bonus True" par exemple
        all_processed_data[f"banking {sub_data['banking']}"]+=1
        all_processed_data[f"Bonus {sub_data['bonus']}"]+=1
        all_processed_data[f"Status {sub_data['status']}"]+=1
        all_processed_data[f"Connecté {sub_data['connected']}"]+=1
        all_processed_data[f"Overflow {sub_data['overflow']}"]+=1
        all_processed_data["Vélo"]+=sub_data['totalStands']['availabilities']['bikes']
        all_processed_data["Stands"]+=sub_data['totalStands']['availabilities']['stands']
        all_processed_data["Vélo mécanique"]+=sub_data['totalStands']['availabilities']['mechanicalBikes']
        all_processed_data["Vélo électrique"]+=sub_data['totalStands']['availabilities']['electricalBikes']
        if sub_data['contractName'] not in all_processed_data["Nombre station par ville"].keys() : #on ajoute les nouvelles ville à mesure qu'on avance dans la boucle
            all_processed_data["Nombre station par ville"][sub_data['contractName']] = 1
        else : #sinon, on incrémente de 1 le nombre de station dans la ville en question
            all_processed_data["Nombre station par ville"][sub_data['contractName']]+=1

    all_processed_data["Nombre station par ville"] = dict( sorted(all_processed_data["Nombre station par ville"].items(), key=lambda x: x[0].lower())) #on arrange le dictionnaire du nombre station par ville dans l'ordre alphabétique des villes
    all_processed_data["Nombre de ville"] = len(all_processed_data["Nombre station par ville"])
    width_scroll_bar_general_data = ((15*conv_sizey(42))**2)/(all_processed_data["Nombre de ville"]*conv_sizey(42)) #produit en croix pour calculer la taille de la scroll bar
    width_scroll_bar_general_data_leftPart = ((15*conv_sizey(42))**2)/((len(all_processed_data))*conv_sizey(42)) #produit en croix pour calculer la taille de la scroll bar
    return width_scroll_bar_general_data, width_scroll_bar_general_data_leftPart

def calc_ranking_data(name_ranking, ranking_direction) :
    https = f"https://api.jcdecaux.com/vls/v3/stations?apiKey={api_key}" #URL
    data = requests.get(https).json() #On effectue une requête https avec get puis on le transforme au format json
    if type(name_ranking) == list :
        list_ranking_data_sorted = sorted(data, key=lambda d: d["totalStands"]["availabilities"][name_ranking[0]], reverse=ranking_direction)
    else :     
        list_ranking_data_sorted = sorted(data, key=lambda d: d[name_ranking], reverse=ranking_direction) 

    width_scroll_bar_ranking_data = ((15*conv_sizey(42))**2)/(len(list_ranking_data_sorted)*conv_sizey(42)) #produit en croix pour calculer la taille de la scroll bar
    return list_ranking_data_sorted, width_scroll_bar_ranking_data

def affichage_carte():
        global data_stations_map, data_colors_map
        resolution = ['c','l','i','h','f'] 
        map = Basemap(width=12300000,height=9000000,projection='lcc', #création de la carte
            resolution=resolution[ind_choice_map_parameter_resolution],lat_0=70, lon_0=65)
        if ind_choice_map_parameter_type_map == 0 :
            map.drawcoastlines()
            map.drawmapboundary(fill_color='aqua')
            map.fillcontinents(color='coral',lake_color='aqua')
        elif ind_choice_map_parameter_type_map == 1 :
            map.bluemarble() 
        elif ind_choice_map_parameter_type_map == 2 :
            map.shadedrelief()
        else :
            map.etopo()
        
        LATITUDES = [] #List de latitudes
        LONGITUDES = [] #List de longitudes
        https = f"https://api.jcdecaux.com/vls/v3/stations?apiKey={api_key}" #URL
        data_stations_map = requests.get(https).json() #On effectue une requête https avec get puis on le transforme au format json
        for sub_data in data_stations_map : #boucle qui parcoure toutes les stations
            LATITUDES.append(sub_data["position"]["latitude"])
            LONGITUDES.append(sub_data["position"]["longitude"])
        data_colors_map = []
        hex_color = ["1","2","3","4","5","6","7","8","9","a","b","c","d","e","f"] #valeur possible pour une couleur en hexadécimal
        for k in range(len(LATITUDES)) : #on parcours chaque station pour lui assigner une couleur et sa position en longitude et latitude
            x, y = map( LONGITUDES[k], LATITUDES[k] )
            colo = '#'+choice(hex_color)+choice(hex_color)+choice(hex_color)+choice(hex_color)+choice(hex_color)+choice(hex_color)
            while colo in data_colors_map : #boucle pour éviter d'avoir 2 fois la même couleur pour un point
                colo = '#'+choice(hex_color)+choice(hex_color)+choice(hex_color)+choice(hex_color)+choice(hex_color)+choice(hex_color)
            data_colors_map.append(colo)

            map.plot(x, y, "o", color = colo) #on créé le point sur la carte
        
        while_loading_map[0] = False #on arrête la boucle de chargement
        plt.show()
        info_map_loop[0] = False #une fois que la carte est fermé
        

#----#----# initialisation de l'interface graphique pygame #----#----#
pygame.init()
pygame.display.set_caption("Analyse JCDecaux bike data") #titre de la fenêtre

#Ouverture de la fenêtre Pygame
window = pygame.display.set_mode((size_screen[0], size_screen[1])) #taille de la fenêtre
clock = pygame.time.Clock() #clock pour limiter la fréquence d'affichage des images (similaire à sleep du module time)


#font des textes 
font1 = pygame.font.SysFont("comicsansms", int(size_screen[0]/50))
font2 = pygame.font.SysFont("comicsansms", int(size_screen[0]/40))
font3 = pygame.font.SysFont("comicsansms", int(size_screen[0]/20))

#import des images
icon = pygame.image.load("./assets/images/icon.png")
pygame.display.set_icon(icon)
img_arrow_up = pygame.transform.scale(pygame.image.load("./assets/images/object/arrow_up.png").convert(), (conv_sizex(20), conv_sizey(20)))
img_arrow_down = pygame.transform.scale(pygame.image.load("./assets/images/object/arrow_down.png").convert(), (conv_sizex(20), conv_sizey(20)))

#----#----# threads #----#----#

#thread pour éviter de rester appuyé lors d'un clic sourie à l'aide de la variable hold_clic
def anti_hold_clic():
    global hold_clic
    while main_loop :
        if pygame.mouse.get_pressed()[0] :
            hold_clic = True
            clock.tick(5)
            hold_clic = False
    sys.exit()
thread_anti_hold_clic = threading.Thread(target=anti_hold_clic)
thread_anti_hold_clic.start()

#fonction qui affiche les informations de la carte (on utilise un thread car matplotlib ne fonctionne prend et garde la tête de lecture et ne fonctionne que dans la boucle principal)
def func_while_map_open() :
    global hexa_color_select_map
    info_map_loop[0] = True
    while_loading_map[0] = True
    ind_loading_anim = [0, 0] #ind_loading_anim[0] permet de déclencher un changement de texte tout les ind_loading_anim[0] frame. ind_loading_anim[1] indique quel texte afficher entre '.', '..', et '...'
    for info in text_info_station :
        info["info"] = ""
    while info_map_loop[0] : #page info de la carte
        clock.tick(20) #20 images par secondes

        #-#Event en relation avec la clavier
        keys = pygame.key.get_pressed() # "dictionnaire" contenant un True si une touche est appuyé, sinon un False
        for event in pygame.event.get():   #On parcours la liste de tous les événements reçus
            if event.type == QUIT or keys[K_ESCAPE] :     #Si on ferme la page, ou appui sur la touche echap, on sort des deux boucles
                pass
        #event espace pour afficher les données d'une station
        if keyboard.is_pressed('space') == True : #on utilise un autre module (keyboard) pour détecter un event clavier même si la fenêtre de pygame n'a pas le focus
            try :
                x, y = pyautogui.position()
                r,g,b = pyautogui.pixel(x, y) #couleur RVB du pixel où est placé la sourie
                hexa_color_select_map = '#{:02x}{:02x}{:02x}'. format(r, g, b)
            except :
                hexa_color_select_map = "------" #s'il y a un problème pour obtenir la couleur, on enlève les textes des données de station
            if hexa_color_select_map not in data_colors_map :
                for info in text_info_station :
                    info["info"] = ""
            else :
                ind_station = data_colors_map.index(hexa_color_select_map)
                ind = 0
                for nom in ["name", "contractName", "address", "banking", "bonus", "connected", "overflow", ["bikes"], ["stands"], ["mechanicalBikes"], ["electricalBikes"], ["electricalInternalBatteryBikes"], ["electricalRemovableBatteryBikes"], "status", "lastUpdate"] :
                    if type(nom) == list :
                        text_info_station[ind]["info"] = data_stations_map[ind_station]["totalStands"]["availabilities"][nom[0]]
                    else :
                        text_info_station[ind]["info"] = data_stations_map[ind_station][nom]
                    ind+=1
  



        #-#Affichage des éléments graphique
        #rectangle noir qui couvre toute la fenêtre pour recouvrir l'ancien affichage des éléments
        pygame.draw.rect(window, (0,0,0), pygame.Rect(conv_sizex(0), conv_sizey(0), size_screen[0], size_screen[1]))
        #texte animé pendant le chargement de la carte
        if while_loading_map[0] and ind_loading_anim[0]%6 == 0:
            if ind_loading_anim[1] == 2 :
                ind_loading_anim[1] = 0
            else :
                ind_loading_anim[1] +=1
            #affichage des textes sur la partie droite (nombre station par ville)
            text_surf = font3.render(f"Chargement{['.', '..', '...'][ind_loading_anim[1]]}", True, (255,255,255))
            window.blit(text_surf, text_surf.get_rect(center = (size_screen[0]//2, size_screen[1]//2)))
            ind_loading_anim[0]+=1
        elif while_loading_map[0] :
            #affichage des textes sur la partie droite (nombre station par ville)
            text_surf = font3.render(f"Chargement{['.', '..', '...'][ind_loading_anim[1]]}", True, (255,255,255))
            window.blit(text_surf, text_surf.get_rect(center = (size_screen[0]//2, size_screen[1]//2)))
            ind_loading_anim[0]+=1
        else :
            #affichage du rectangle gris
            pygame.draw.rect(window, (155,155,155), pygame.Rect(conv_sizex(50), conv_sizey(140), size_screen[0]-conv_sizex(100), size_screen[1]), 0,3)

            text_surf = font2.render(f"Fermer la page de la carte pour revenir dans l'application", True, (255,255,255))
            window.blit(text_surf, text_surf.get_rect(center = (size_screen[0]//2, conv_sizey(50))))
            text_surf = font2.render(f"Pour obtenir des informations sur une station,", True, (255,255,255))
            window.blit(text_surf, text_surf.get_rect(center = (size_screen[0]//2, conv_sizey(155))))
            text_surf = font2.render(f"placez votre sourie sur un point, puis appuyez sur la touche espace", True, (255,255,255))
            window.blit(text_surf, text_surf.get_rect(center = (size_screen[0]//2, conv_sizey(175))))


            #affichage des informations d'une station
            temp_y = 242
            for txt in text_info_station :
                text_surf = font1.render(f"{txt['nom']} : {txt['info']}", True, (255,255,255))
                window.blit(text_surf, text_surf.get_rect(center = (size_screen[0]//2, conv_sizey(temp_y))))
                temp_y+=42
        #Rafraîchissement de l'écran
        pygame.display.flip()
    sys.exit()


#fonction qui tourne en continu et qui update les données de la page affichées toute les minutes (sachant que les données sont update par l'API toute les 10 minutes)
def update_data() :
    while main_loop :
        temps = time()
        while time()-temps < 60 : #on attend 1 minutes dans cette boucle
            sleep(0.5)
        if info_map_loop[0] :
            https = f"https://api.jcdecaux.com/vls/v3/stations?apiKey={api_key}" #URL
            data = requests.get(https).json() #On effectue une requête https avec get puis on le transforme au format json
            ind_station = 0
            for sub_data in data :
                for key in sub_data.keys() :
                    if sub_data[key] != data_stations_map[ind_station][key] : #s'il y a un changement entre les données affiché sur la carte et les nouvelles données qui viennent d'être récupérés
                        data_stations_map[ind_station][key] = sub_data[key]
                ind_station+=1
            if hexa_color_select_map not in data_colors_map : #on update les données affichées de la station sélectionnées
                for info in text_info_station :
                    info["info"] = ""
            else :
                ind_station = data_colors_map.index(hexa_color_select_map)
                ind = 0
                for nom in ["name", "contractName", "address", "banking", "bonus", "connected", "overflow", ["bikes"], ["stands"], ["mechanicalBikes"], ["electricalBikes"], ["electricalInternalBatteryBikes"], ["electricalRemovableBatteryBikes"], "status", "lastUpdate"] :
                    if type(nom) == list :
                        text_info_station[ind]["info"] = data_stations_map[ind_station]["totalStands"]["availabilities"][nom[0]]
                    else :
                        text_info_station[ind]["info"] = data_stations_map[ind_station][nom]
                    ind+=1
thread_update_data = threading.Thread(target=update_data)
thread_update_data.start()


#----#----# interface graphique #----#----#
#boucle principale
while main_loop :
#---------------# Boucle/page Classement des données #---------------#
    if general_data : #initialisation de la page général data
        width_scroll_bar_general_data, width_scroll_bar_general_data_leftPart = calc_all_analytic_data() #calcule des données à chaque fois qu'on change de page 
    while general_data : #page general_data
        clock.tick(20) #20 images par secondes
        X, Y = pygame.mouse.get_pos() #position en x et y de la sourie

        #-#Event en relation avec la clavier
        keys = pygame.key.get_pressed() # "dictionnaire" contenant un True si une touche est appuyé, sinon un False
        for event in pygame.event.get():   #On parcours la liste de tous les événements reçus
            if event.type == QUIT or keys[K_ESCAPE] :     #Si on ferme la page, ou appui sur la touche echap, on sort des deux boucles
                main_loop = False
                general_data = False
            #scroll bar de drite
            if size_screen[0]//2+conv_sizex(25) < X < size_screen[0]-conv_sizex(50) and conv_sizey(170) < Y < size_screen[1] : #si la sourie est dans le rectangle à gauche (Nombre station par ville)
                color_scroll_bar = (80,80,80) 
                if event.type == pygame.MOUSEWHEEL : #si un event de ma molette est détecté. Celui-ci est défini par event.y = -1 pour un scroll vers le bas et  event.y = 1 pour un scroll vers le haut (il existe aussi les scroll vers les côtés avec event.x qu'on n'utilisera pas ici)
                    if jump_ville_scroll <= all_processed_data["Nombre de ville"]-15+1 and event.y < 0 : #on limite le nombre e scroll possible en fonction du nombre ville (il y a toujours 15 villes d'affichées)
                        jump_ville_scroll-=event.y
                        if jump_ville_scroll > all_processed_data["Nombre de ville"]-15+1 : #il est possible de dépasser le nombre max car si on scroll rapidement, event.y augmente aussi à -2, -3, -4... 
                            jump_ville_scroll = all_processed_data["Nombre de ville"]-15+1
                    elif jump_ville_scroll > 0 and event.y >= 0 : #même procédé que mais en remontant 
                        jump_ville_scroll-=event.y
                        if jump_ville_scroll < 0 :
                            jump_ville_scroll = 0
                    position_y_scroll_bar_general_data = (jump_ville_scroll*conv_sizey(42)*(15*conv_sizey(42)-width_scroll_bar_general_data//2))/(all_processed_data["Nombre de ville"]*conv_sizey(42)) #calcule de la position de la scroll bar avec un produit en croix
            else :
                color_scroll_bar = (110,110,110)
            #scroll bar e gauche
            if conv_sizex(50) < X < size_screen[0]//2-conv_sizex(25) and conv_sizey(170) < Y < size_screen[1] : #si la sourie est dans le rectangle à gauche (Nombre station par ville)
                color_scroll_bar_leftPart = (80,80,80) 
                if event.type == pygame.MOUSEWHEEL : #si un event de ma molette est détecté. Celui-ci est défini par event.y = -1 pour un scroll vers le bas et  event.y = 1 pour un scroll vers le haut (il existe aussi les scroll vers les côtés avec event.x qu'on n'utilisera pas ici)
                    if jump_total_scroll <=(len( all_processed_data)-1)-15+1 and event.y < 0 : #on limite le nombre e scroll possible en fonction du nombre ville (il y a toujours 15 villes d'affichées)
                        jump_total_scroll-=event.y
                        if jump_total_scroll > (len(all_processed_data)-1)-15+1 : #il est possible de dépasser le nombre max car si on scroll rapidement, event.y augmente aussi à -2, -3, -4... 
                            jump_total_scroll = (len(all_processed_data)-1)-15+1
                    elif jump_total_scroll > 0 and event.y >= 0 : #même procédé que mais en remontant 
                        jump_total_scroll-=event.y
                        if jump_total_scroll < 0 :
                            jump_total_scroll = 0
                    position_y_scroll_bar_general_data_leftPart = (jump_total_scroll*conv_sizey(42)*(15*conv_sizey(42)-width_scroll_bar_general_data//2))/((len(all_processed_data)-1)*conv_sizey(42)) #calcule de la position de la scroll bar avec un produit en croix
            else :
                color_scroll_bar_leftPart = (110,110,110)


        #-#Event en relation avec la sourie
        if 2*size_screen[0]//4-conv_sizex(110) < X < 2*size_screen[0]//4-conv_sizex(110)+conv_sizex(220) and conv_sizey(50) < Y < conv_sizey(90) :#si la sourie est sur la bouton de la page "Classement des données"
            color_ranking_data_page = "SURVOLE"
            if pygame.mouse.get_pressed()[0] and hold_clic == False : #si On clic, on change de page (de boucle while)
                general_data = False
                ranking_data = True
                size_screen = (4*GetSystemMetrics(0)//5,4*GetSystemMetrics(1)//5)
                window = pygame.display.set_mode((size_screen[0], size_screen[1]))
        else : 
            color_ranking_data_page = "NORMAL"
        
        if 3*size_screen[0]//4-conv_sizex(110) < X < 3*size_screen[0]//4-conv_sizex(110)+conv_sizex(220) and conv_sizey(50) < Y < conv_sizey(90) :#si la sourie est sur la bouton de la page "Classement des données"
            color_map_data_page = "SURVOLE"
            if pygame.mouse.get_pressed()[0] and hold_clic == False : #si On clic, on change de page (de boucle while)
                general_data = False
                map_loop = True
        else : 
            color_map_data_page = "NORMAL"
            

        #-#Affichage des éléments graphique
        #rectangle noir qui couvre toute la fenêtre pour recouvrir l'ancien affichage des éléments
        pygame.draw.rect(window, (0,0,0), pygame.Rect(conv_sizex(0), conv_sizey(0), size_screen[0], size_screen[1]))
        
        #bouton pour "Donnée général"
        pygame.draw.rect(window, (63,72,204), pygame.Rect(size_screen[0]//4-conv_sizex(110), conv_sizey(50), conv_sizex(220), conv_sizey(40)), 0,3)
        text_surf = font1.render("Données général", True, (255,255,255))
        window.blit(text_surf, text_surf.get_rect(center = (size_screen[0]//4, conv_sizey(70))))
        pygame.draw.rect(window, (255,255,255), pygame.Rect(size_screen[0]//4-conv_sizex(110), conv_sizey(50), conv_sizex(220), conv_sizey(40)), 2,3)
        
        #texte et rectangle pour "Classement des données"
        if color_ranking_data_page == "NORMAL" : #choix de la couleur du bouton en fonction du survole ou non
            color1 = (63,72,204)
            color2 = (255,255,255)
        else :
            color1 = (255,255,255)
            color2 = (63,72,204)
        pygame.draw.rect(window, color1, pygame.Rect(2*size_screen[0]//4-conv_sizex(110), conv_sizey(50), conv_sizex(220), conv_sizey(40)), 0,3)
        text_surf = font1.render("Classement des données", True, color2)
        window.blit(text_surf, text_surf.get_rect(center = (2*size_screen[0]//4, conv_sizey(70))))

        #texte et rectangle pour "Carte"
        if color_map_data_page == "NORMAL" : #choix de la couleur du bouton en fonction du survole ou non
            color1 = (63,72,204)
            color2 = (255,255,255)
        else :
            color1 = (255,255,255)
            color2 = (63,72,204)
        pygame.draw.rect(window, color1, pygame.Rect(3*size_screen[0]//4-conv_sizex(110), conv_sizey(50), conv_sizex(220), conv_sizey(40)), 0,3)
        text_surf = font1.render("Carte", True, color2)
        window.blit(text_surf, text_surf.get_rect(center = (3*size_screen[0]//4, conv_sizey(70))))
        
        pygame.draw.rect(window, (155,155,155), pygame.Rect(conv_sizex(50), conv_sizey(170), size_screen[0]//2-conv_sizex(75), size_screen[1]-conv_sizey(160)), 0,3)
        pygame.draw.rect(window, (155,155,155), pygame.Rect(size_screen[0]//2+conv_sizex(25), conv_sizey(170), size_screen[0]//2-conv_sizex(75), size_screen[1]-conv_sizey(160)), 0,3)

        #affichage des textes sur la partie gauche
        text_surf = font2.render(f"Total : ", True, (255,255,255))
        window.blit(text_surf, text_surf.get_rect(center = (size_screen[0]//4, conv_sizey(200))))
        temp_y = conv_sizey(242)
        temp_jump_total_scroll = 0
        for key in all_processed_data.keys() :
            if key != "Nombre station par ville" :
                if temp_jump_total_scroll == 15+jump_total_scroll : #une fois que les 15 villes sont affiché à l'écran, on arrête la boucle car les autres villes ne seront pas visible 
                    break
                if temp_jump_total_scroll >= jump_total_scroll : #pour simuler une descente de la page, on n'afficha pas les premières villes jusqu'à jump_ville_scroll
                    text_surf = font1.render(f"{key} : {all_processed_data[key]}", True, (255,255,255))
                    window.blit(text_surf, text_surf.get_rect(center = (size_screen[0]//4, temp_y)))
                    temp_y+=conv_sizey(42)
                temp_jump_total_scroll+=1

        #affichage des textes sur la partie droite (nombre station par ville)
        text_surf = font2.render(f"Nombre de station par ville", True, (255,255,255))
        window.blit(text_surf, text_surf.get_rect(center = (3*size_screen[0]//4, conv_sizey(200))))
        temp_y = conv_sizey(242)
        temp_jump_ville_scroll = 0
        for key in all_processed_data["Nombre station par ville"].keys() :
            if temp_jump_ville_scroll == 15+jump_ville_scroll : #une fois que les 15 villes sont affiché à l'écran, on arrête la boucle car les autres villes ne seront pas visible 
                break
            if temp_jump_ville_scroll >= jump_ville_scroll : #pour simuler une descente de la page, on n'afficha pas les premières villes jusqu'à jump_ville_scroll
                text_surf = font1.render(f"{key} : {all_processed_data['Nombre station par ville'][key]}", True, (255,255,255))
                window.blit(text_surf, text_surf.get_rect(center = (3*size_screen[0]//4, temp_y)))
                temp_y+=conv_sizey(42)
            temp_jump_ville_scroll+=1
        
        #affichage scroll bar
        pygame.draw.rect(window, color_scroll_bar, pygame.Rect(size_screen[0]-conv_sizex(85), conv_sizey(242)+position_y_scroll_bar_general_data, conv_sizex(25), width_scroll_bar_general_data), 0,3)
        pygame.draw.rect(window, color_scroll_bar_leftPart, pygame.Rect(size_screen[0]//2-conv_sizex(60), conv_sizey(242)+position_y_scroll_bar_general_data_leftPart, conv_sizex(25), width_scroll_bar_general_data_leftPart), 0,3)


        #Rafraîchissement de l'écran
        pygame.display.flip()



#---------------# Boucle/page Classement des données #---------------#
    if ranking_data :  #initialisation de la page ranking data
        list_info_arrow_ranking = calc_list_list_info_arrow_ranking()
        list_ranking_data, width_scroll_bar_ranking_data = calc_ranking_data("name",False) #par défaut on classe selon le nom dans l'ordre alphabétique
    while ranking_data : #page general_data
        clock.tick(20) #20 images par secondes

        #-#Event en relation avec la clavier
        keys = pygame.key.get_pressed() # "dictionnaire" contenant un True si une touche est appuyé, sinon un False
        for event in pygame.event.get():   #On parcours la liste de tous les événements reçus
            if event.type == QUIT or keys[K_ESCAPE] :     #Si on ferme la page, ou appui sur la touche echap, on sort des deux boucles
                main_loop = False
                ranking_data = False
            if event.type == pygame.MOUSEWHEEL : #si un event de ma molette est détecté. Celui-ci est défini par event.y = -1 pour un scroll vers le bas et  event.y = 1 pour un scroll vers le haut (il existe aussi les scroll vers les côté avec event.x qu'on utilisera pas ici)
                if jump_station_scroll <= len(list_ranking_data)-15+1 and event.y < 0 : #on limite le nombre e scroll possible en fonction du nombre ville (il y a toujours 15 villes d'affichées)
                    jump_station_scroll-=event.y
                    if jump_station_scroll > len(list_ranking_data)-15+1 : #il est possible de dépasser le nombre max car si on scroll rapidement, event.y augmente aussi à -2, -3, -4... 
                        jump_station_scroll = len(list_ranking_data)-15+1
                elif jump_station_scroll > 0 and event.y >= 0 : #même procédé que mais en remontant 
                    jump_station_scroll-=event.y
                    if jump_station_scroll < 0 :
                        jump_station_scroll = 0
                position_y_scroll_bar_ranking_data = (jump_station_scroll*conv_sizey(42)*(15*conv_sizey(42)-width_scroll_bar_ranking_data//2))//(len(list_ranking_data)*conv_sizey(42)) #calcule de la position de la scroll bar avec un produit en croix
                
        #-#Event en relation avec la sourie
        X, Y = pygame.mouse.get_pos() #position en x et y de la sourie
        #si la sourie est sur la bouton de la page "Données général"
        if size_screen[0]//4-conv_sizex(110) < X < size_screen[0]//4-conv_sizex(110)+conv_sizex(220) and conv_sizey(50) < Y < conv_sizey(90) : 
            color_general_data_page = "SURVOLE"
            if pygame.mouse.get_pressed()[0] and hold_clic == False : #si On clic, on change de page (de boucle while)
                general_data = True
                ranking_data = False
                size_screen = (GetSystemMetrics(0)//2,4*GetSystemMetrics(1)//5)
                window = pygame.display.set_mode((size_screen[0], size_screen[1]))
        else : #sinon, aucun survole sur le bouton "Données général"
            color_general_data_page = "NORMAL"
        #si la sourie est sur la bouton de la page "Carte"
        if 3*size_screen[0]//4-conv_sizex(110) < X < 3*size_screen[0]//4-conv_sizex(110)+conv_sizex(220) and conv_sizey(50) < Y < conv_sizey(90) : 
            color_map_page = "SURVOLE"
            if pygame.mouse.get_pressed()[0] and hold_clic == False : #si On clic, on change de page (de boucle while)
                map_loop = True
                ranking_data = False
                size_screen = (GetSystemMetrics(0)//2,4*GetSystemMetrics(1)//5)
                window = pygame.display.set_mode((size_screen[0], size_screen[1]))
        else : #sinon, aucun survole sur le bouton "Données général"
            color_map_page = "NORMAL"
        #test clic sur les flèches pour changer le classement
        for info_arrow in list_info_arrow_ranking :
            if info_arrow["coordX_left"] < X < info_arrow["coordX_right"] and conv_sizey(190) < Y < conv_sizey(210) and pygame.mouse.get_pressed()[0] and hold_clic == False :
                list_ranking_data, width_scroll_bar_ranking_data = calc_ranking_data(info_arrow["nom"],info_arrow["reverse"])
                jump_station_scroll, position_y_scroll_bar_ranking_data = 0, 0


        #-#Affichage des éléments graphique
        #rectangle noir qui couvre toute la fenêtre pour recouvrir l'ancien affichage des éléments
        pygame.draw.rect(window, (0,0,0), pygame.Rect(conv_sizex(0), conv_sizey(0), size_screen[0], size_screen[1]))

        #texte et rectangles pour "Donnée général"
        if color_general_data_page == "NORMAL" : #choix de la couleur du bouton en fonction du survole ou non
            color1 = (63,72,204)
            color2 = (255,255,255)
        else :
            color1 = (255,255,255)
            color2 = (63,72,204)
        pygame.draw.rect(window, color1, pygame.Rect(size_screen[0]//4-conv_sizex(110), conv_sizey(50), conv_sizex(220), conv_sizey(40)), 0,3)
        text_surf = font1.render("Données général", True, color2)
        window.blit(text_surf, text_surf.get_rect(center = (size_screen[0]//4, conv_sizey(70))))
        #texte et rectangles pour "Carte"
        if color_map_page == "NORMAL" : #choix de la couleur du bouton en fonction du survole ou non
            color1 = (63,72,204)
            color2 = (255,255,255)
        else :
            color1 = (255,255,255)
            color2 = (63,72,204)
        pygame.draw.rect(window, color1, pygame.Rect(3*size_screen[0]//4-conv_sizex(110), conv_sizey(50), conv_sizex(220), conv_sizey(40)), 0,3)
        text_surf = font1.render("Carte", True, color2)
        window.blit(text_surf, text_surf.get_rect(center = (3*size_screen[0]//4, conv_sizey(70))))
        #texte et rectangle pour "Classement des données"
        pygame.draw.rect(window, (63,72,204), pygame.Rect(2*size_screen[0]//4-conv_sizex(110), conv_sizey(50), conv_sizex(220), conv_sizey(40)), 0,3)
        text_surf = font1.render("Classement des données", True, (255,255,255))
        window.blit(text_surf, text_surf.get_rect(center = (2*size_screen[0]//4, conv_sizey(70))))
        pygame.draw.rect(window, (255,255,255), pygame.Rect(2*size_screen[0]//4-conv_sizex(110), conv_sizey(50), conv_sizex(220), conv_sizey(40)), 2,3)
        
        pygame.draw.rect(window, (155,155,155), pygame.Rect(conv_sizex(15), conv_sizey(170), size_screen[0]-conv_sizex(30), size_screen[1]-conv_sizey(160)), 0,3)
        
        #texte des titres de classement
        text_surf = font1.render(f"Nom", True, (255,255,255))
        window.blit(text_surf, text_surf.get_rect(center = (conv_sizex(930)//8+conv_sizex(25), conv_sizey(200))))
        text_surf = font1.render(f"Ville", True, (255,255,255))
        window.blit(text_surf, text_surf.get_rect(center = (2*conv_sizex(930)//8+conv_sizex(50), conv_sizey(200))))
        text_surf = font1.render(f"Vélos", True, (255,255,255))
        window.blit(text_surf, text_surf.get_rect(center = (3*conv_sizex(930)//8, conv_sizey(200))))
        text_surf = font1.render(f"Stands", True, (255,255,255))
        window.blit(text_surf, text_surf.get_rect(center = (4*conv_sizex(930)//8, conv_sizey(200))))
        text_surf = font1.render(f"Vélo mecanique", True, (255,255,255))
        window.blit(text_surf, text_surf.get_rect(center = (5*conv_sizex(930)//8, conv_sizey(200))))
        text_surf = font1.render(f"Vélo électrique", True, (255,255,255))
        window.blit(text_surf, text_surf.get_rect(center = (6*conv_sizex(930)//8, conv_sizey(200))))
        text_surf = font1.render(f"Status", True, (255,255,255))
        window.blit(text_surf, text_surf.get_rect(center = (7*conv_sizex(930)//8, conv_sizey(200))))

        #affichage des flèches pour choisir le type de classement
        #flèches pour "Nom"
        window.blit(img_arrow_up, (conv_sizex(930)//8-conv_sizex(22), conv_sizey(190)))
        window.blit(img_arrow_down, (conv_sizex(930)//8-conv_sizex(7), conv_sizey(190)))
        #flèches pour "Ville"
        window.blit(img_arrow_up, (2*conv_sizex(930)//8+conv_sizex(5), conv_sizey(190)))
        window.blit(img_arrow_down, (2*conv_sizex(930)//8+conv_sizex(21), conv_sizey(190)))
        #flèches pour "bikes"
        window.blit(img_arrow_up, (3*conv_sizex(930)//8-conv_sizex(46), conv_sizey(190)))
        window.blit(img_arrow_down, (3*conv_sizex(930)//8-conv_sizex(30), conv_sizey(190)))
        #flèches pour "stands"
        window.blit(img_arrow_up, (4*conv_sizex(930)//8-conv_sizex(51), conv_sizey(190)))
        window.blit(img_arrow_down, (4*conv_sizex(930)//8-conv_sizex(35), conv_sizey(190)))
        #flèches pour "Vélo mécanique"
        window.blit(img_arrow_up, (5*conv_sizex(930)//8-conv_sizex(75), conv_sizey(190)))
        window.blit(img_arrow_down, (5*conv_sizex(930)//8-conv_sizex(59), conv_sizey(190)))
        #flèches pour "Vélo électrique"
        window.blit(img_arrow_up, (6*conv_sizex(930)//8-conv_sizex(71), conv_sizey(190)))
        window.blit(img_arrow_down, (6*conv_sizex(930)//8-conv_sizex(55), conv_sizey(190)))
        #flèches pour "Status"
        window.blit(img_arrow_up, (7*conv_sizex(930)//8-conv_sizex(54), conv_sizey(190)))
        window.blit(img_arrow_down, (7*conv_sizex(930)//8-conv_sizex(38), conv_sizey(190)))

        #affichage des textes du classement
        temp_y = conv_sizey(242)
        temp_jump_station_scroll = 0
        for station in list_ranking_data :
            if temp_jump_station_scroll == 15+jump_station_scroll : #une fois que les 15 villes sont affiché à l'écran, on arrête la boucle car les autres villes ne seront pas visible 
                break
            if temp_jump_station_scroll >= jump_station_scroll : #pour simuler une descente de la page, on n'afficha pas les premières villes jusqu'à jump_station_scroll
                if len(station["name"]) > 26 :
                    station["name"] = station["name"][:24]+"..."
                text_surf = font1.render(f'{station["name"]}', True, (255,255,255))
                window.blit(text_surf, text_surf.get_rect(center = (conv_sizex(930)//8++conv_sizex(25), temp_y)))
                text_surf = font1.render(f'{station["contractName"]}', True, (255,255,255))
                window.blit(text_surf, text_surf.get_rect(center = (2*conv_sizex(930)//8+conv_sizex(50), temp_y)))
                text_surf = font1.render(f'{station["totalStands"]["availabilities"]["bikes"]}', True, (255,255,255))
                window.blit(text_surf, text_surf.get_rect(center = (3*conv_sizex(930)//8, temp_y)))
                text_surf = font1.render(f'{station["totalStands"]["availabilities"]["stands"]}', True, (255,255,255))
                window.blit(text_surf, text_surf.get_rect(center = (4*conv_sizex(930)//8, temp_y)))
                text_surf = font1.render(f'{station["totalStands"]["availabilities"]["mechanicalBikes"]}', True, (255,255,255))
                window.blit(text_surf, text_surf.get_rect(center = (5*conv_sizex(930)//8, temp_y)))
                text_surf = font1.render(f'{station["totalStands"]["availabilities"]["electricalBikes"]}', True, (255,255,255))
                window.blit(text_surf, text_surf.get_rect(center = (6*conv_sizex(930)//8, temp_y)))
                text_surf = font1.render(f'{station["status"]}', True, (255,255,255))
                window.blit(text_surf, text_surf.get_rect(center = (7*conv_sizex(930)//8, temp_y)))
                temp_y+=conv_sizey(42)
            temp_jump_station_scroll+=1

        #affichage scroll bar
        pygame.draw.rect(window, (130,130,130), pygame.Rect(size_screen[0]-conv_sizex(52), conv_sizey(214), conv_sizex(29), conv_sizey(42)*15+conv_sizey(15)), 0,3)
        pygame.draw.rect(window, (80,80,80), pygame.Rect(size_screen[0]-conv_sizex(50), conv_sizey(227)+position_y_scroll_bar_ranking_data, conv_sizex(25), width_scroll_bar_ranking_data), 0,3)


        #Rafraîchissement de l'écran
        pygame.display.flip()


#---------------# Boucle/page Carte #---------------#
    while map_loop :
        clock.tick(20) #20 images par secondes

        #-#Event en relation avec la clavier
        keys = pygame.key.get_pressed() # "dictionnaire" contenant un True si une touche est appuyé, sinon un False
        for event in pygame.event.get():   #On parcours la liste de tous les événements reçus
            if event.type == QUIT or keys[K_ESCAPE] :     #Si on ferme la page, ou appui sur la touche echap, on sort des deux boucles
                main_loop = False
                map_loop = False
                
        #-#Event en relation avec la sourie
        X, Y = pygame.mouse.get_pos() #position en x et y de la sourie
        #si la sourie est sur la bouton de la page "Données général"
        if size_screen[0]//4-conv_sizex(110) < X < size_screen[0]//4-conv_sizex(110)+conv_sizex(220) and conv_sizey(50) < Y < conv_sizey(90) : 
            color_general_data_page = "SURVOLE"
            if pygame.mouse.get_pressed()[0] and hold_clic == False : #si On clic, on change de page (de boucle while)
                general_data = True
                map_loop = False
        else : #sinon, aucun survole sur le bouton "Données général"
            color_general_data_page = "NORMAL"

        if 2*size_screen[0]//4-conv_sizex(110) < X < 2*size_screen[0]//4-conv_sizex(110)+conv_sizex(220) and conv_sizey(50) < Y < conv_sizey(90) :#si la sourie est sur la bouton de la page "Classement des données"
            color_ranking_data_page = "SURVOLE"
            if pygame.mouse.get_pressed()[0] and hold_clic == False : #si On clic, on change de page (de boucle while)
                map_loop = False
                ranking_data = True
                size_screen = (4*GetSystemMetrics(0)//5,4*GetSystemMetrics(1)//5)
                window = pygame.display.set_mode((size_screen[0], size_screen[1]))
        else : 
            color_ranking_data_page = "NORMAL"

        if size_screen[0]//2-conv_sizex(110) < X < size_screen[0]//2-conv_sizex(110)+conv_sizex(220) and size_screen[1]-conv_sizey(90) < Y < size_screen[1]-conv_sizey(50) :#si la sourie est sur la bouton de la page "Générer la carte"
            color_create_map_page = "SURVOLE"
            if pygame.mouse.get_pressed()[0] and hold_clic == False : #si On clic, on change de page (de boucle while)
                thread_func_while_map_open = threading.Thread(target=func_while_map_open)   
                thread_func_while_map_open.start()
                affichage_carte()
        else : 
            color_create_map_page = "NORMAL"
        
        #test clic sur les boutons de sélection des paramètres (coté gauche, type de carte)
        coord = [k for k in range(280, 450, 50)]
        for ind in range(4) :
            if conv_sizex(930)//5-conv_sizex(106) < X < conv_sizex(930)//5-conv_sizex(96)+conv_sizex(202) and conv_sizey(coord[ind]) < Y < conv_sizey(coord[ind])+conv_sizey(26) and pygame.mouse.get_pressed()[0] and hold_clic == False :
                ind_choice_map_parameter_type_map = ind
                if ind != 0 :
                    ind_choice_map_parameter_resolution = 0

        if ind_choice_map_parameter_type_map == 0 :
            #test clic sur les boutons de sélection des paramètres (coté gauche, type de carte)
            coord = [k for k in range(280, 500, 50)]
            for ind in range(5) :
                if 4*conv_sizex(930)//5-conv_sizex(106) < X < 4*conv_sizex(930)//5-conv_sizex(96)+conv_sizex(202) and conv_sizey(coord[ind]) < Y < conv_sizey(coord[ind])+conv_sizey(26) and pygame.mouse.get_pressed()[0] and hold_clic == False :
                    ind_choice_map_parameter_resolution = ind

        #-#Affichage des éléments graphique
        #rectangle noir qui couvre toute la fenêtre pour recouvrir l'ancien affichage des éléments
        pygame.draw.rect(window, (0,0,0), pygame.Rect(conv_sizex(0), conv_sizey(0), size_screen[0], size_screen[1]))

        #texte et rectangles pour "Donnée général"
        if color_general_data_page == "NORMAL" : #choix de la couleur du bouton en fonction du survole ou non
            color1 = (63,72,204)
            color2 = (255,255,255)
        else :
            color1 = (255,255,255)
            color2 = (63,72,204)
        pygame.draw.rect(window, color1, pygame.Rect(size_screen[0]//4-conv_sizex(110), conv_sizey(50), conv_sizex(220), conv_sizey(40)), 0,3)
        text_surf = font1.render("Données général", True, color2)
        window.blit(text_surf, text_surf.get_rect(center = (size_screen[0]//4, conv_sizey(70))))

        #texte et rectangle pour "Classement des données"
        if color_ranking_data_page == "NORMAL" : #choix de la couleur du bouton en fonction du survole ou non
            color1 = (63,72,204)
            color2 = (255,255,255)
        else :
            color1 = (255,255,255)
            color2 = (63,72,204)
        pygame.draw.rect(window, color1, pygame.Rect(2*size_screen[0]//4-conv_sizex(110), conv_sizey(50), conv_sizex(220), conv_sizey(40)), 0,3)
        text_surf = font1.render("Classement des données", True, color2)
        window.blit(text_surf, text_surf.get_rect(center = (2*size_screen[0]//4, conv_sizey(70))))
        
        #texte et rectangle pour "Carte"
        pygame.draw.rect(window, (63,72,204), pygame.Rect(3*size_screen[0]//4-conv_sizex(110), conv_sizey(50), conv_sizex(220), conv_sizey(40)), 0,3)
        text_surf = font1.render("Carte", True, (255,255,255))
        window.blit(text_surf, text_surf.get_rect(center = (3*size_screen[0]//4, conv_sizey(70))))
        pygame.draw.rect(window, (255,255,255), pygame.Rect(3*size_screen[0]//4-conv_sizex(110), conv_sizey(50), conv_sizex(220), conv_sizey(40)), 2,3)
        #Bouton pour générer al carte
        if color_create_map_page == "NORMAL" : #choix de la couleur du bouton en fonction du survole ou non
            color1 = (63,72,204)
            color2 = (255,255,255)
        else :
            color1 = (255,255,255)
            color2 = (63,72,204)
        pygame.draw.rect(window, color1, pygame.Rect(size_screen[0]//2-conv_sizex(110), size_screen[1]-conv_sizey(90), conv_sizex(220), conv_sizey(40)), 0,3)
        text_surf = font1.render("Générer la carte", True, color2)
        window.blit(text_surf, text_surf.get_rect(center = (size_screen[0]//2, size_screen[1]-conv_sizey(70))))        

        #titre des paramètres
        text_surf = font2.render("Type d'affichage de la carte", True, (255,255,255))
        window.blit(text_surf, text_surf.get_rect(center = (conv_sizex(930)//5, conv_sizey(200))))
        if ind_choice_map_parameter_type_map == 0 : #la résolution change uniquement lors du premier type 
            text_surf = font2.render("Résolution de la carte", True, (255,255,255))
            window.blit(text_surf, text_surf.get_rect(center = (4*conv_sizex(930)//5, conv_sizey(200))))
        
        #texte des paramètres de gauche (Type d'affichage de la carte)
        for info in [["Frontières simple",280], ["vue satellite",330],["vue relief", 380], ["vue topographiques", 430]] :
            text_surf = font1.render(info[0], True, (255,255,255))
            window.blit(text_surf, (conv_sizex(930)//5-conv_sizex(80), conv_sizey(info[1])))
        if ind_choice_map_parameter_type_map == 0 :
            #texte des paramètres de droite (résolution de la carte) (utile uniquement pour le premier type de carte)
            for info in [["Très bas",280], ["Bas",330],["Intermédiaire", 380], ["Haut", 430], ["Très haut", 480]] :
                text_surf = font1.render(info[0], True, (255,255,255))
                window.blit(text_surf, (4*conv_sizex(930)//5-conv_sizex(80), conv_sizey(info[1])))

        #affichage des rond pour indiquer lequel est sélectionné (coté gauche, type de carte)
        coord = [k for k in range(294, 450, 50)]
        for ind in range(4) :
            if ind == ind_choice_map_parameter_type_map :
                pygame.draw.circle(window, (255,255,255), (conv_sizex(930)//5-conv_sizex(96), conv_sizey(coord[ind])), 4, 0)
            pygame.draw.circle(window, (255,255,255), (conv_sizex(930)//5-conv_sizex(96), conv_sizey(coord[ind])), 10, 2)
        if ind_choice_map_parameter_type_map == 0 :    
            #affichage des rond pour indiquer lequel est sélectionné (coté droit, résolution)
            coord = [k for k in range(294, 500, 50)]
            for ind in range(5) :
                if ind == ind_choice_map_parameter_resolution :
                    pygame.draw.circle(window, (255,255,255), (4*conv_sizex(930)//5-conv_sizex(96), conv_sizey(coord[ind])), 4, 0)
                pygame.draw.circle(window, (255,255,255), (4*conv_sizex(930)//5-conv_sizex(96), conv_sizey(coord[ind])), 10, 2)


        #Rafraîchissement de l'écran
        pygame.display.flip()


os._exit(1)