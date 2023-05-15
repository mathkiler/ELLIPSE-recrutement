#----#----# import des modules #----#----#
from win32api import GetSystemMetrics   #module utile pour obtenir les dimensions de l'écran 
import requests    #module pour faire les requêtes à l'API
import pygame      #module pour l'interface graphique de Pygame
from pygame.locals import * #import des variables utiles pour le module pygame (exemple : K_ESCAPE signifie la touche echap)
import threading
import os
import sys

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
    "bike stands" : 0,
    "available bike stands" : 0,
    "available bikes" : 0,
    "Nombre station par ville" : {} #à chaque nouvelle ville, on rajoute un objet de ce format : "lyon" : 0
}
list_ranking_data = [] #dictionnaire qui va contenir le classement 
jump_ville_scroll = 0 #variable utile pour descendre dans les nombres de stations par villes (l'idée est de simuler une descente des textes en n'affichant ou pas les premières villes)
jump_station_scroll = 0 #variable utile pour descendre dans les nombres de stations par stations (l'idée est de simuler une descente des textes en n'affichant ou pas les premières stations)
width_scroll_bar_general_data = 0 #variable utile pour la taille de la scroll bar pour la page general_data
position_y_scroll_bar_general_data = 0 #variable utile pour la position de la scroll bar pour la page general_data
width_scroll_bar_ranking_data = 0 #variable utile pour la taille de la scroll bar pour la page ranking_data 
position_y_scroll_bar_ranking_data = 0 #variable utile pour la position de la scroll bar pour la page ranking_data
list_info_arrow_ranking = [] #liste qui contient les information pour les flèches de la page de classement des données
#variables des boucles pour l'interface graphique
main_loop = True
general_data = True
ranking_data = False



#----#----# fonctions auxiliaire #----#----#

#utile pour le passage en .exe
def resource_path0(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(
        sys,
        '_MEIPASS',
        os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

#fonction pour convertir une longueur du format 960x864 au format de l'écran de l'utilisateur
def conv_sizex(x):
    return int(size_screen[0]*x/960)
def conv_sizey(y):
    return int(size_screen[1]*y/864)

#fonction qui initialise la liste 
def calc_list_list_info_arrow_ranking() :
    list_info_arrow_ranking = [ #liste qui contient les information pour les flèches de la page de classement des données
        {
            "coordX_left" : conv_sizex(930)//7-conv_sizex(46), 
            "coordX_right" : conv_sizex(930)//7-conv_sizex(46)+size_screen[0]//76.8,
            "nom" : "name",
            "reverse" : False
        },
        {
            "coordX_left" : conv_sizex(930)//7-conv_sizex(30), 
            "coordX_right" : conv_sizex(930)//7-conv_sizex(30)+size_screen[0]//76.8,
            "nom" : "name",
            "reverse" : True
        },
        {
            "coordX_left" : 2*conv_sizex(930)//7-conv_sizex(46), 
            "coordX_right" : 2*conv_sizex(930)//7-conv_sizex(46)+size_screen[0]//76.8,
            "nom" : "contract_name",
            "reverse" : False
        },
        {
            "coordX_left" : 2*conv_sizex(930)//7-conv_sizex(30), 
            "coordX_right" : 2*conv_sizex(930)//7-conv_sizex(30)+size_screen[0]//76.8,
            "nom" : "contract_name",
            "reverse" : True
        },
        {
            "coordX_left" : 3*conv_sizex(930)//7-conv_sizex(66), 
            "coordX_right" : 3*conv_sizex(930)//7-conv_sizex(66)+size_screen[0]//76.8,
            "nom" : "bike_stands",
            "reverse" : False
        },
        {
            "coordX_left" : 3*conv_sizex(930)//7-conv_sizex(66), 
            "coordX_right" : 3*conv_sizex(930)//7-conv_sizex(66)+size_screen[0]//76.8,
            "nom" : "bike_stands",
            "reverse" : False
        },
        {
            "coordX_left" : 3*conv_sizex(930)//7-conv_sizex(50), 
            "coordX_right" : 3*conv_sizex(930)//7-conv_sizex(50)+size_screen[0]//76.8,
            "nom" : "bike_stands",
            "reverse" : True
        },
        {
            "coordX_left" : 4*conv_sizex(930)//7-conv_sizex(92), 
            "coordX_right" : 4*conv_sizex(930)//7-conv_sizex(92)+size_screen[0]//76.8,
            "nom" : "available_bike_stands",
            "reverse" : False
        },
        {
            "coordX_left" : 4*conv_sizex(930)//7-conv_sizex(76), 
            "coordX_right" : 4*conv_sizex(930)//7-conv_sizex(76)+size_screen[0]//76.8,
            "nom" : "available_bike_stands",
            "reverse" : True
        },
        {
            "coordX_left" : 5*conv_sizex(930)//7-conv_sizex(71), 
            "coordX_right" : 5*conv_sizex(930)//7-conv_sizex(71)+size_screen[0]//76.8,
            "nom" : "available_bikes",
            "reverse" : False
        },
        {
            "coordX_left" : 5*conv_sizex(930)//7-conv_sizex(55), 
            "coordX_right" : 5*conv_sizex(930)//7-conv_sizex(55)+size_screen[0]//76.8,
            "nom" : "available_bikes",
            "reverse" : True
        },
        {
            "coordX_left" : 6*conv_sizex(930)//7-conv_sizex(54), 
            "coordX_right" : 6*conv_sizex(930)//7-conv_sizex(54)+size_screen[0]//76.8,
            "nom" : "status",
            "reverse" : False
        },
        {
            "coordX_left" : 6*conv_sizex(930)//7-conv_sizex(38), 
            "coordX_right" : 6*conv_sizex(930)//7-conv_sizex(38)+size_screen[0]//76.8,
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

    https = f"https://api.jcdecaux.com/vls/v1/stations?apiKey={api_key}" #URL
    data = requests.get(https).json() #On effectue une requête https avec get puis on le transforme au format json
    for sub_data in data : #boucle qui parcoure toutes les stations
        all_processed_data["Nombre de stations"]+=1
        #compte des effectifs des stations. Le f string permet d'incrémenter directement la bonne variable "bonus False" ou "bonus True" par exemple
        all_processed_data[f"banking {sub_data['banking']}"]+=1
        all_processed_data[f"Bonus {sub_data['bonus']}"]+=1
        all_processed_data[f"Status {sub_data['status']}"]+=1
        all_processed_data["bike stands"]+=sub_data['bike_stands']
        all_processed_data["available bike stands"]+=sub_data['available_bike_stands']
        all_processed_data["available bikes"]+=sub_data['available_bikes']
        if sub_data['contract_name'] not in all_processed_data["Nombre station par ville"].keys() : #on ajoute les nouvelles ville à mesure qu'on avance dans la boucle
            all_processed_data["Nombre station par ville"][sub_data['contract_name']] = 1
        else : #sinon, on incrémente de 1 le nombre de station dans la ville en question
            all_processed_data["Nombre station par ville"][sub_data['contract_name']]+=1

    all_processed_data["Nombre station par ville"] = dict( sorted(all_processed_data["Nombre station par ville"].items(), key=lambda x: x[0].lower())) #on arrange le dictionnaire du nombre station par ville dans l'ordre alphabétique des villes
    all_processed_data["Nombre de ville"] = len(all_processed_data["Nombre station par ville"])
    width_scroll_bar_general_data = ((15*conv_sizey(42))**2)/(all_processed_data["Nombre de ville"]*conv_sizey(42)) #produit en croix pour calculer la taille de la scroll bar
    return width_scroll_bar_general_data

def calc_ranking_data(name_ranking, ranking_direction) :
    https = f"https://api.jcdecaux.com/vls/v1/stations?apiKey={api_key}" #URL
    data = requests.get(https).json() #On effectue une requête https avec get puis on le transforme au format json
    list_ranking_data_sorted = sorted(data, key=lambda d: d[name_ranking], reverse=ranking_direction) 

    width_scroll_bar_ranking_data = ((15*conv_sizey(42))**2)/(len(list_ranking_data_sorted)*conv_sizey(42)) #produit en croix pour calculer la taille de la scroll bar
    return list_ranking_data_sorted, width_scroll_bar_ranking_data


#----#----# initialisation de l'interface graphique pygame #----#----#
pygame.init()
pygame.display.set_caption("Analyse JCDecaux bike data") #titre de la fenêtre

#Ouverture de la fenêtre Pygame
window = pygame.display.set_mode((size_screen[0], size_screen[1])) #taille de la fenêtre
clock = pygame.time.Clock() #clock pour limiter la fréquence d'affichage des images (similaire à sleep du module time)


#font des textes 
font1 = pygame.font.SysFont("comicsansms", int(size_screen[0]/50))
font2 = pygame.font.SysFont("comicsansms", int(size_screen[0]/40))

#import des images
img_arrow_up = pygame.transform.scale(pygame.image.load(resource_path0("./assets/images/object/arrow_up.png")).convert(), (conv_sizex(20), conv_sizey(20)))
img_arrow_down = pygame.transform.scale(pygame.image.load(resource_path0("./assets/images/object/arrow_down.png")).convert(), (conv_sizex(20), conv_sizey(20)))


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
#def threads
thread_anti_hold_clic = threading.Thread(target=anti_hold_clic)
thread_anti_hold_clic.start()
    


#----#----# interface graphique #----#----#
#boucle principale
while main_loop :
    

#---------------# Boucle/page Classement des données #---------------#
    if general_data : #initialisation de la page général data
        width_scroll_bar_general_data = calc_all_analytic_data() #calcule des données à chaque fois qu'on change de page 
    while general_data : #page general_data
        clock.tick(20) #20 images par secondes
        X, Y = pygame.mouse.get_pos() #position en x et y de la sourie

        #-#Event en relation avec la clavier
        keys = pygame.key.get_pressed() # "dictionnaire" contenant un True si une touche est appuyé, sinon un False
        for event in pygame.event.get():   #On parcours la liste de tous les événements reçus
            if event.type == QUIT or keys[K_ESCAPE] :     #Si on ferme la page, ou appui sur la touche echap, on sort des deux boucles
                main_loop = False
                general_data = False
            
            if size_screen[0]//2+conv_sizex(25) < X < size_screen[0]-conv_sizex(50) and conv_sizey(170) < Y < size_screen[1] : #si la sourie est dans le rectangle à gauche (Nombre station par ville)
                color_scroll_bar = (80,80,80) 
                if event.type == pygame.MOUSEWHEEL : #si un event de ma molette est détecté. Celui-ci est défini par event.y = -1 pour un scroll vers le bas et  event.y = 1 pour un scroll vers le haut (il existe aussi les scroll vers les côté avec event.x qu'on utilisera pas ici)
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


        #-#Event en relation avec la sourie
        if 2*size_screen[0]//3-conv_sizex(110) < X < 2*size_screen[0]//3-conv_sizex(110)+conv_sizex(220) and conv_sizey(50) < Y < conv_sizey(90) :#si la sourie est sur la bouton de la page "Classement des données"
            color_ranking_data_page = "SURVOLE"
            if pygame.mouse.get_pressed()[0] and hold_clic == False : #si On clic, on change de page (de boucle while)
                general_data = False
                ranking_data = True
                size_screen = (4*GetSystemMetrics(0)//5,4*GetSystemMetrics(1)//5)
                window = pygame.display.set_mode((size_screen[0], size_screen[1]))
        else : 
            color_ranking_data_page = "NORMAL"




        #-#Affichage des éléments graphique
        #rectangle noir qui couvre toute la fenêtre pour recouvrir l'ancien affichage des éléments
        pygame.draw.rect(window, (0,0,0), pygame.Rect(conv_sizex(0), conv_sizey(0), size_screen[0], size_screen[1]))
        
        #texte et rectangles pour "Donnée général"
        pygame.draw.rect(window, (63,72,204), pygame.Rect(size_screen[0]//3-conv_sizex(85), conv_sizey(50), conv_sizex(170), conv_sizey(40)), 0,3)
        text_surf = font1.render("Données général", True, (255,255,255))
        window.blit(text_surf, text_surf.get_rect(center = (size_screen[0]//3, conv_sizey(70))))
        pygame.draw.rect(window, (255,255,255), pygame.Rect(size_screen[0]//3-conv_sizex(85), conv_sizey(50), conv_sizex(170), conv_sizey(40)), 2,3)
        
        #texte et rectangle pour "Classement des données"
        if color_ranking_data_page == "NORMAL" : #choix de la couleur du bouton en fonction du survole ou non
            color1 = (63,72,204)
            color2 = (255,255,255)
        else :
            color1 = (255,255,255)
            color2 = (63,72,204)
        pygame.draw.rect(window, color1, pygame.Rect(2*size_screen[0]//3-conv_sizex(110), conv_sizey(50), conv_sizex(220), conv_sizey(40)), 0,3)
        text_surf = font1.render("Classement des données", True, color2)
        window.blit(text_surf, text_surf.get_rect(center = (2*size_screen[0]//3, conv_sizey(70))))
        
        pygame.draw.rect(window, (155,155,155), pygame.Rect(conv_sizex(50), conv_sizey(170), size_screen[0]//2-conv_sizex(75), size_screen[1]-conv_sizey(160)), 0,3)
        pygame.draw.rect(window, (155,155,155), pygame.Rect(size_screen[0]//2+conv_sizex(25), conv_sizey(170), size_screen[0]//2-conv_sizex(75), size_screen[1]-conv_sizey(160)), 0,3)

        #affichage des textes sur la partie gauche
        temp_y = conv_sizey(200)
        for key in all_processed_data.keys() :
            if key != "Nombre station par ville" :
                text_surf = font1.render(f"{key} : {all_processed_data[key]}", True, (255,255,255))
                window.blit(text_surf, text_surf.get_rect(center = (size_screen[0]//4, temp_y)))
                temp_y+=conv_sizey(42)

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
        if size_screen[0]//3-conv_sizex(85) < X < size_screen[0]//3-conv_sizex(85)+conv_sizex(170) and conv_sizey(50) < Y < conv_sizey(90) : 
            color_general_data_page = "SURVOLE"
            if pygame.mouse.get_pressed()[0] and hold_clic == False : #si On clic, on change de page (de boucle while)
                general_data = True
                ranking_data = False
                size_screen = (GetSystemMetrics(0)//2,4*GetSystemMetrics(1)//5)
                window = pygame.display.set_mode((size_screen[0], size_screen[1]))
        else : #sinon, aucun survole sur le bouton "Données général"
            color_general_data_page = "NORMAL"
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
        pygame.draw.rect(window, color1, pygame.Rect(size_screen[0]//3-conv_sizex(85), conv_sizey(50), conv_sizex(170), conv_sizey(40)), 0,3)
        text_surf = font1.render("Données général", True, color2)
        window.blit(text_surf, text_surf.get_rect(center = (size_screen[0]//3, conv_sizey(70))))
        
        #texte et rectangle pour "Classement des données"
        pygame.draw.rect(window, (63,72,204), pygame.Rect(2*size_screen[0]//3-conv_sizex(110), conv_sizey(50), conv_sizex(220), conv_sizey(40)), 0,3)
        text_surf = font1.render("Classement des données", True, (255,255,255))
        window.blit(text_surf, text_surf.get_rect(center = (2*size_screen[0]//3, conv_sizey(70))))
        pygame.draw.rect(window, (255,255,255), pygame.Rect(2*size_screen[0]//3-conv_sizex(110), conv_sizey(50), conv_sizex(220), conv_sizey(40)), 2,3)
        
        pygame.draw.rect(window, (155,155,155), pygame.Rect(conv_sizex(15), conv_sizey(170), size_screen[0]-conv_sizex(30), size_screen[1]-conv_sizey(160)), 0,3)
        
        #texte des titres de classement
        text_surf = font1.render(f"Nom", True, (255,255,255))
        window.blit(text_surf, text_surf.get_rect(center = (conv_sizex(930)//7, conv_sizey(200))))
        text_surf = font1.render(f"Ville", True, (255,255,255))
        window.blit(text_surf, text_surf.get_rect(center = (2*conv_sizex(930)//7, conv_sizey(200))))
        text_surf = font1.render(f"Bike stands", True, (255,255,255))
        window.blit(text_surf, text_surf.get_rect(center = (3*conv_sizex(930)//7, conv_sizey(200))))
        text_surf = font1.render(f"Available bike stands", True, (255,255,255))
        window.blit(text_surf, text_surf.get_rect(center = (4*conv_sizex(930)//7, conv_sizey(200))))
        text_surf = font1.render(f"Available bikes", True, (255,255,255))
        window.blit(text_surf, text_surf.get_rect(center = (5*conv_sizex(930)//7, conv_sizey(200))))
        text_surf = font1.render(f"Status", True, (255,255,255))
        window.blit(text_surf, text_surf.get_rect(center = (6*conv_sizex(930)//7, conv_sizey(200))))

        #affichage des flèches pour choisir le type de classement
        #flèches pour "Nom"
        window.blit(img_arrow_up, (conv_sizex(930)//7-conv_sizex(46), conv_sizey(190)))
        window.blit(img_arrow_down, (conv_sizex(930)//7-conv_sizex(30), conv_sizey(190)))
        #flèches pour "Ville"
        window.blit(img_arrow_up, (2*conv_sizex(930)//7-conv_sizex(46), conv_sizey(190)))
        window.blit(img_arrow_down, (2*conv_sizex(930)//7-conv_sizex(30), conv_sizey(190)))
        #flèches pour "Bike stands"
        window.blit(img_arrow_up, (3*conv_sizex(930)//7-conv_sizex(66), conv_sizey(190)))
        window.blit(img_arrow_down, (3*conv_sizex(930)//7-conv_sizex(50), conv_sizey(190)))
        #flèches pour "Available bike stands"
        window.blit(img_arrow_up, (4*conv_sizex(930)//7-conv_sizex(92), conv_sizey(190)))
        window.blit(img_arrow_down, (4*conv_sizex(930)//7-conv_sizex(76), conv_sizey(190)))
        #flèches pour "Available bikes"
        window.blit(img_arrow_up, (5*conv_sizex(930)//7-conv_sizex(71), conv_sizey(190)))
        window.blit(img_arrow_down, (5*conv_sizex(930)//7-conv_sizex(55), conv_sizey(190)))
        #flèches pour "Status"
        window.blit(img_arrow_up, (6*conv_sizex(930)//7-conv_sizex(54), conv_sizey(190)))
        window.blit(img_arrow_down, (6*conv_sizex(930)//7-conv_sizex(38), conv_sizey(190)))

        #affichage des textes du classement
        temp_y = conv_sizey(242)
        temp_jump_station_scroll = 0
        for station in list_ranking_data :
            if temp_jump_station_scroll == 15+jump_station_scroll : #une fois que les 15 villes sont affiché à l'écran, on arrête la boucle car les autres villes ne seront pas visible 
                break
            if temp_jump_station_scroll >= jump_station_scroll : #pour simuler une descente de la page, on n'afficha pas les premières villes jusqu'à jump_station_scroll
                if len(station["name"]) > 23 :
                    station["name"] = station["name"][:21]+"..."
                text_surf = font1.render(f'{station["name"]}', True, (255,255,255))
                window.blit(text_surf, text_surf.get_rect(center = (conv_sizex(930)//7, temp_y)))
                text_surf = font1.render(f'{station["contract_name"]}', True, (255,255,255))
                window.blit(text_surf, text_surf.get_rect(center = (2*conv_sizex(930)//7, temp_y)))
                text_surf = font1.render(f'{station["bike_stands"]}', True, (255,255,255))
                window.blit(text_surf, text_surf.get_rect(center = (3*conv_sizex(930)//7, temp_y)))
                text_surf = font1.render(f'{station["available_bike_stands"]}', True, (255,255,255))
                window.blit(text_surf, text_surf.get_rect(center = (4*conv_sizex(930)//7, temp_y)))
                text_surf = font1.render(f'{station["available_bikes"]}', True, (255,255,255))
                window.blit(text_surf, text_surf.get_rect(center = (5*conv_sizex(930)//7, temp_y)))
                text_surf = font1.render(f'{station["status"]}', True, (255,255,255))
                window.blit(text_surf, text_surf.get_rect(center = (6*conv_sizex(930)//7, temp_y)))
                temp_y+=conv_sizey(42)
            temp_jump_station_scroll+=1

        #affichage scroll bar
        pygame.draw.rect(window, (130,130,130), pygame.Rect(size_screen[0]-conv_sizex(52), conv_sizey(214), conv_sizex(29), conv_sizey(42)*15+conv_sizey(15)), 0,3)
        pygame.draw.rect(window, (80,80,80), pygame.Rect(size_screen[0]-conv_sizex(50), conv_sizey(227)+position_y_scroll_bar_ranking_data, conv_sizex(25), width_scroll_bar_ranking_data), 0,3)


        #Rafraîchissement de l'écran
        pygame.display.flip()




os._exit(1)