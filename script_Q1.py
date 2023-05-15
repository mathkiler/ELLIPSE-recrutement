#----#----# importations des modules #----#----#
from win32api import GetSystemMetrics   #module utile pour obtenir les dimensions de l'écran 
import requests    #module pour faire les requêtes à l'API
import pygame      #module pour l'interface graphique de Pygame
from pygame.locals import * #import des variables utiles pour le module pygame (exemple : K_ESCAPE signifie la touche echap)
import os
import sys
import threading
#----#----# variables/listes #----#----#
with open('api_key.txt', 'r') as f: #récupération de la clé dans le fichier api_key.txt (ce fichier n'est pas disponible dans le github)
    api_key = f.read()

size_screen = (GetSystemMetrics(0)//2,4*GetSystemMetrics(1)//5) #on force la taille de l'écran dans un format personnalisé
#on utilisera size_screen pour adapter la taille des objets en fonction de la taille de l'écran de l'utilisateur au démarrage de l'application
hold_clic = False #variable utilisée pour éviter de rester appuyer lors d'un clic sourie
all_processed_data = {  #Dictionnaire pour stocker les données de l'API exploitées (les calculs se feront dans la fonction calc_all_analytic_data())
    "Nombre de stations" : 0,
    "banking True" : 0,
    "banking False" : 0,
    "Bonus True" : 0,
    "Bonus False" : 0,
    "Status OPEN" : 0,
    "Status CLOSED" : 0,
    "Nombre station par ville" : {}, #à chaque nouvelle ville, on rajoute un objet de ce format : "lyon" : 0
    "Nombre de ville" : 0
}
jump_ville_scroll = 0 #variable utile pour dessendre dans les nombres de stations par villes (l'idée est de simuler une dessente des textes en n'affichant ou pas les premieres villes)
width_scroll_bar = 0 #variable utile pour la taille de la scroll bar 
position_y_scroll_bar = 0 #variable utile pour la position de la scroll bar
#variables des boucles pour l'interface graphique
main_loop = True
general_data = True
ranking_data = False





#----#----# initialisation de l'interface graphique pygame #----#----#
pygame.init()
pygame.display.set_caption("Analyse JCDecaux bike data") #titre de la fenêtre

#Ouverture de la fenêtre Pygame
window = pygame.display.set_mode((size_screen[0], size_screen[1])) #taille de la fenêtre
clock = pygame.time.Clock() #clock pour limiter la fréquence d'affichage des images (similaire à sleep du module time)


#font des textes 
font1 = pygame.font.SysFont("comicsansms", int(size_screen[0]/50))
font2 = pygame.font.SysFont("comicsansms", int(size_screen[0]/40))


#----#----# fonctions auxiliaire #----#----#

#fonction pour convertir une longueur du format 960x864 au format de l'écran de l'utilisateur
def conv_sizex(x):
    return int(size_screen[0]*x/960)
def conv_sizey(y):
    return int(size_screen[1]*y/864)

#fonction pour exploiter les données de l'API
def calc_all_analytic_data() :
    #on commence par réinitialiser les calculs précédent
    for key in all_processed_data.keys() :
        if key == "Nombre station par ville" :
            all_processed_data[key] = {}
        else :
            all_processed_data[key] = 0

    https = f"https://api.jcdecaux.com/vls/v1/stations?apiKey={api_key}" #URL
    data = requests.get(https).json() #On effectue une requête https avec get puis on le ransforme au format json
    for sub_data in data : #boucle qui parcoure toutes les stations
        all_processed_data["Nombre de stations"]+=1
        #compte des effectifs des stations. Le f string permet d'incrémenter directement la bonne variable "bonus False" ou "bonus True" par exemple
        all_processed_data[f"banking {sub_data['banking']}"]+=1
        all_processed_data[f"Bonus {sub_data['bonus']}"]+=1
        all_processed_data[f"Status {sub_data['status']}"]+=1
        if sub_data['contract_name'] not in all_processed_data["Nombre station par ville"].keys() : #on ajoute les nouvelles ville à mesure qu'on avance dans la boucle
            all_processed_data["Nombre station par ville"][sub_data['contract_name']] = 1
        else : #sinon, on incrémente de 1 le nombre de station dans la ville en question
            all_processed_data["Nombre station par ville"][sub_data['contract_name']]+=1

    all_processed_data["Nombre station par ville"] = dict( sorted(all_processed_data["Nombre station par ville"].items(), key=lambda x: x[0].lower())) #on arrange le disctionnaire du nombre station par ville dans l'ordre alphabétique des villes
    all_processed_data["Nombre de ville"] = len(all_processed_data["Nombre station par ville"])
    width_scroll_bar = ((15*conv_sizey(42))**2)/(all_processed_data["Nombre de ville"]*conv_sizey(42)) #produit en croix pour calculer la taille de la scroll bar
    return width_scroll_bar


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
    width_scroll_bar = calc_all_analytic_data() #calcule des données à chaque fois qu'on change de page 

#---------------# Boucle/page Classement des données #---------------#
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
                if event.type == pygame.MOUSEWHEEL : #si un event de ma molette est détécté. Celui-ci est défini par event.y = -1 pour un scroll vers le bas et  event.y = 1 pour un scroll vers le haut (il existe aussi les scroll vers les côté avec envent.x qu'on utilisera pas ici)
                    if jump_ville_scroll <= all_processed_data["Nombre de ville"]-15+1 and event.y < 0 : #on limite le nombre e scroll possible en fonction du nombre ville (il y a toujours 15 villes d'affichées)
                        jump_ville_scroll-=event.y
                        if jump_ville_scroll > all_processed_data["Nombre de ville"]-15+1 : #il est possible de dépasser le nombre max car si on scroll rapidement, event.y augmente aussi à -2, -3, -4... 
                            jump_ville_scroll = all_processed_data["Nombre de ville"]-15+1
                    elif jump_ville_scroll > 0 and event.y >= 0 : #même procédé que mais en remontant 
                        jump_ville_scroll-=event.y
                        if jump_ville_scroll < 0 :
                            jump_ville_scroll = 0
                    position_y_scroll_bar = (jump_ville_scroll*conv_sizey(42)*(15*conv_sizey(42)-width_scroll_bar//2))/(all_processed_data["Nombre de ville"]*conv_sizey(42)) #calcule de la position de la scroll bar avec un produit en croix
            else :
                color_scroll_bar = (110,110,110)


        #-#Event en relation avec la sourie
        if size_screen[0]//3-conv_sizex(85) < X < size_screen[0]//3-conv_sizex(85)+conv_sizex(170) and conv_sizey(50) < Y < conv_sizey(90) : #si la sourie est sur la bouton de la page "Données général"
            color_general_data_page = "SURVOLE"
            if pygame.mouse.get_pressed()[0] and hold_clic == False :
                width_scroll_bar = calc_all_analytic_data() #calcule des données à chaque fois qu'on clic sur le bouton de la page actuelle
        else : 
            color_general_data_page = "NORMAL"
        if 2*size_screen[0]//3-conv_sizex(110) < X < 2*size_screen[0]//3-conv_sizex(110)+conv_sizex(220) and conv_sizey(50) < Y < conv_sizey(90) :#si la sourie est sur la bouton de la page "Classement des données"
            color_ranking_data_page = "SURVOLE"
            if pygame.mouse.get_pressed()[0] and hold_clic == False : #si On clic, on change de page (de boucle while)
                general_data = False
                ranking_data = True
        else : 
            color_ranking_data_page = "NORMAL"




        #-#Affichage des éléments graphique
        #rectangle noir qui couvre toute la fenêtre pour recouvrir l'ancient affichage des éléments
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
        pygame.draw.rect(window, color2, pygame.Rect(size_screen[0]//3-conv_sizex(85), conv_sizey(50), conv_sizex(170), conv_sizey(40)), 2,3)
        
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
            if temp_jump_ville_scroll >= jump_ville_scroll : #pour simuler une dessente de la page, on n'afficha pas les premières villes jusqu'à jump_ville_scroll
                text_surf = font1.render(f"{key} : {all_processed_data['Nombre station par ville'][key]}", True, (255,255,255))
                window.blit(text_surf, text_surf.get_rect(center = (3*size_screen[0]//4, temp_y)))
                temp_y+=conv_sizey(42)
            temp_jump_ville_scroll+=1
        
        #affichage scroll bar
        pygame.draw.rect(window, color_scroll_bar, pygame.Rect(size_screen[0]-conv_sizex(85), conv_sizey(242)+position_y_scroll_bar, conv_sizey(25), width_scroll_bar), 0,3)


        #Rafraîchissement de l'écran
        pygame.display.flip()



#---------------# Boucle/page Classement des données #---------------#
    while ranking_data : #page general_data
        clock.tick(20) #20 images par secondes

        #-#Event en relation avec la clavier
        keys = pygame.key.get_pressed() # "dictionnaire" contenant un True si une touche est appuyé, sinon un False
        for event in pygame.event.get():   #On parcours la liste de tous les événements reçus
            if event.type == QUIT or keys[K_ESCAPE] :     #Si on ferme la page, ou appui sur la touche echap, on sort des deux boucles
                main_loop = False
                ranking_data = False

        #-#Event en relation avec la sourie
        X, Y = pygame.mouse.get_pos() #position en x et y de la sourie
        if size_screen[0]//3-conv_sizex(85) < X < size_screen[0]//3-conv_sizex(85)+conv_sizex(170) and conv_sizey(50) < Y < conv_sizey(90) : #si la sourie est sur la bouton de la page "Données général"
            color_general_data_page = "SURVOLE"
            if pygame.mouse.get_pressed()[0] and hold_clic == False : #si On clic, on change de page (de boucle while)
                general_data = True
                ranking_data = False
        else : 
            color_general_data_page = "NORMAL"
        if 2*size_screen[0]//3-conv_sizex(110) < X < 2*size_screen[0]//3-conv_sizex(110)+conv_sizex(220) and conv_sizey(50) < Y < conv_sizey(90) :#si la sourie est sur la bouton de la page "Classement des données"
            color_ranking_data_page = "SURVOLE"
            if pygame.mouse.get_pressed()[0] and hold_clic == False :
                width_scroll_bar = calc_all_analytic_data() #calcule des données à chaque fois qu'on change de page
        else : 
            color_ranking_data_page = "NORMAL"

        #-#Affichage des éléments graphique
        #rectangle noir qui couvre toute la fenêtre pour recouvrir l'ancient affichage des éléments
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
        if color_ranking_data_page == "NORMAL" : #choix de la couleur du bouton en fonction du survole ou non
            color1 = (63,72,204)
            color2 = (255,255,255)
        else :
            color1 = (255,255,255)
            color2 = (63,72,204)
        pygame.draw.rect(window, color1, pygame.Rect(2*size_screen[0]//3-conv_sizex(110), conv_sizey(50), conv_sizex(220), conv_sizey(40)), 0,3)
        text_surf = font1.render("Classement des données", True, color2)
        window.blit(text_surf, text_surf.get_rect(center = (2*size_screen[0]//3, conv_sizey(70))))
        pygame.draw.rect(window, color2, pygame.Rect(2*size_screen[0]//3-conv_sizex(110), conv_sizey(50), conv_sizex(220), conv_sizey(40)), 2,3)
        
        pygame.draw.rect(window, (155,155,155), pygame.Rect(conv_sizex(50), conv_sizey(170), size_screen[0]-conv_sizex(100), size_screen[1]-conv_sizey(160)), 0,3)
        

        #Rafraîchissement de l'écran
        pygame.display.flip()




os._exit(1)