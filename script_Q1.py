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
    "nombre_station" : 0
}


#variables des boucles pour l'interface graphique
main_loop = True
general_data = True
clasment_data = False





#----#----# initialisation de l'interface graphique pygame #----#----#
pygame.init()
pygame.display.set_caption("Analyse JCDecaux bike data") #titre de la fenêtre

#Ouverture de la fenêtre Pygame
window = pygame.display.set_mode((size_screen[0], size_screen[1])) #taille de la fenêtre
clock = pygame.time.Clock() #clock pour limiter la fréquence d'affichage des images (similaire à sleep du module time)


#font des textes 
font1 = pygame.font.SysFont("comicsansms", int(size_screen[0]/50))
font2 = pygame.font.SysFont("comicsansms", int(size_screen[0]/39))


#----#----# fonctions auxiliaire #----#----#

#fonction pour convertir une longueur du format 960x864 au format de l'écran de l'utilisateur
def conv_sizex(x):
    return int(size_screen[0]*x/960)
def conv_sizey(y):
    return int(size_screen[1]*y/864)

#fonction pour exploiter les données de l'API
def calc_all_analytic_data() :
    https = f"https://api.jcdecaux.com/vls/v1/stations?apiKey={api_key}" #URL
    data = requests.get(https).json() #On effectue une requête https avec get puis on le ransforme au format json
    
    for sous_data in data : #boucle qui parcoure toutes les stations
        all_processed_data["nombre_station"]+=1



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
    calc_all_analytic_data() #calcule des données à chaque fois qu'on change de page 

#---------------# Boucle/page Classement des données #---------------#
    while general_data : #page general_data
        clock.tick(20) #20 images par secondes

        #-#Event en relation avec la clavier
        keys = pygame.key.get_pressed() # "dictionnaire" contenant un True si une touche est appuyé, sinon un False
        for event in pygame.event.get():   #On parcours la liste de tous les événements reçus
            if event.type == QUIT or keys[K_ESCAPE] :     #Si on ferme la page, ou appui sur la touche echap, on sort des deux boucles
                main_loop = False
                general_data = False

        #-#Event en relation avec la sourie
        X, Y = pygame.mouse.get_pos() #position en x et y de la sourie
        if size_screen[0]//3-conv_sizex(85) < X < size_screen[0]//3-conv_sizex(85)+conv_sizex(170) and conv_sizey(50) < Y < conv_sizey(90) : #si la sourie est sur la bouton de la page "Données général"
            color_general_data_page = "SURVOLE"
            if pygame.mouse.get_pressed()[0] and hold_clic == False :
                calc_all_analytic_data() #calcule des données à chaque fois qu'on clic sur le bouton de la page actuelle
        else : 
            color_general_data_page = "NORMAL"
        if 2*size_screen[0]//3-conv_sizex(110) < X < 2*size_screen[0]//3-conv_sizex(110)+conv_sizex(220) and conv_sizey(50) < Y < conv_sizey(90) :#si la sourie est sur la bouton de la page "Classement des données"
            color_clasment_data_page = "SURVOLE"
            if pygame.mouse.get_pressed()[0] and hold_clic == False : #si On clic, on change de page (de boucle while)
                general_data = False
                clasment_data = True
        else : 
            color_clasment_data_page = "NORMAL"

        #-#Affichage des éléments graphique
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
        if color_clasment_data_page == "NORMAL" : #choix de la couleur du bouton en fonction du survole ou non
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

        text_surf = font1.render(f"Nombre de stations : {all_processed_data['nombre_station']}", True, (255,255,255))
        window.blit(text_surf, text_surf.get_rect(center = (size_screen[0]//4, conv_sizey(200))))


        #Rafraîchissement de l'écran
        pygame.display.flip()



#---------------# Boucle/page Classement des données #---------------#
    while clasment_data : #page general_data
        clock.tick(20) #20 images par secondes

        #-#Event en relation avec la clavier
        keys = pygame.key.get_pressed() # "dictionnaire" contenant un True si une touche est appuyé, sinon un False
        for event in pygame.event.get():   #On parcours la liste de tous les événements reçus
            if event.type == QUIT or keys[K_ESCAPE] :     #Si on ferme la page, ou appui sur la touche echap, on sort des deux boucles
                main_loop = False
                clasment_data = False

        #-#Event en relation avec la sourie
        X, Y = pygame.mouse.get_pos() #position en x et y de la sourie
        if size_screen[0]//3-conv_sizex(85) < X < size_screen[0]//3-conv_sizex(85)+conv_sizex(170) and conv_sizey(50) < Y < conv_sizey(90) : #si la sourie est sur la bouton de la page "Données général"
            color_general_data_page = "SURVOLE"
            if pygame.mouse.get_pressed()[0] and hold_clic == False : #si On clic, on change de page (de boucle while)
                general_data = True
                clasment_data = False
        else : 
            color_general_data_page = "NORMAL"
        if 2*size_screen[0]//3-conv_sizex(110) < X < 2*size_screen[0]//3-conv_sizex(110)+conv_sizex(220) and conv_sizey(50) < Y < conv_sizey(90) :#si la sourie est sur la bouton de la page "Classement des données"
            color_clasment_data_page = "SURVOLE"
            if pygame.mouse.get_pressed()[0] and hold_clic == False :
                calc_all_analytic_data() #calcule des données à chaque fois qu'on change de page
        else : 
            color_clasment_data_page = "NORMAL"

        #-#Affichage des éléments graphique
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
        if color_clasment_data_page == "NORMAL" : #choix de la couleur du bouton en fonction du survole ou non
            color1 = (63,72,204)
            color2 = (255,255,255)
        else :
            color1 = (255,255,255)
            color2 = (63,72,204)
        pygame.draw.rect(window, color1, pygame.Rect(2*size_screen[0]//3-conv_sizex(110), conv_sizey(50), conv_sizex(220), conv_sizey(40)), 0,3)
        text_surf = font1.render("Classement des données", True, color2)
        window.blit(text_surf, text_surf.get_rect(center = (2*size_screen[0]//3, conv_sizey(70))))
        pygame.draw.rect(window, color2, pygame.Rect(2*size_screen[0]//3-conv_sizex(110), conv_sizey(50), conv_sizex(220), conv_sizey(40)), 2,3)
        
        pygame.draw.rect(window, (155,155,155), pygame.Rect(conv_sizex(50), conv_sizey(170), size_screen[0]//2-conv_sizex(100), size_screen[1]-conv_sizey(160)), 0,3)
        

        #Rafraîchissement de l'écran
        pygame.display.flip()




os._exit(1)