#importation des modules
from win32api import GetSystemMetrics   #mudule utile pour connaître la taille de l'écran 
import requests    #module pour faire les requests de l'API
import pygame      #module pour l'interface graphique
from pygame.locals import *

#variables/lists
with open('api_key.txt', 'r') as f:
    api_key = f.read()

size_screen = (GetSystemMetrics(0)//2,4*GetSystemMetrics(1)//5) #on force la taille de l'écran dans un format personnalisé
#on utilisera size_screen pour adapter la taille des objet en fonction de la taille de l'écran de l'utilisateur au démarrage de l'application
all_processed_data = {
    "nombre_station" : 0
}


#variables des loops
main_loop = True
general_data = True
clasment_data = False





####init pygame
pygame.init()
pygame.display.set_caption("Analyse JCDecaux bike data")

#Ouverture de la fenêtre Pygame
window = pygame.display.set_mode((size_screen[0], size_screen[1]))
clock = pygame.time.Clock()


#font des textes 
font1 = pygame.font.SysFont("comicsansms", int(size_screen[0]/55))
font2 = pygame.font.SysFont("comicsansms", int(size_screen[0]/39))


#fonctions auxillière

#fonction pour convertir une longeure du format 960x864 au format de l'écran de l'utilisateur
def conv_sizex(x):
    return int(size_screen[0]*x/960)
def conv_sizey(y):
    return int(size_screen[1]*y/864)

def calc_all_analytic_data() :
    https = f"https://api.jcdecaux.com/vls/v1/stations?apiKey={api_key}"
    data = requests.get(https).json()
    count_all_data = 0
    for sous_data in data :
        count_all_data+=1





    all_processed_data["nombre_station"] = count_all_data

    



#boucle principale
while main_loop :
    calc_all_analytic_data()
    while general_data :
        clock.tick(20) #20 images par secondes

        keys = pygame.key.get_pressed()
        for event in pygame.event.get():   #On parcours la liste de tous les événements reçus
            if event.type == QUIT or keys[K_ESCAPE] :     #Si un de ces événements est de type QUIT
                main_loop = False
                general_data = False

        X, Y = pygame.mouse.get_pos() #position en x et y de la sourie

        pygame.draw.rect(window, (63,72,204), pygame.Rect(size_screen[0]//3-conv_sizex(80), conv_sizey(50), conv_sizex(160), conv_sizey(40)), 0,3)
        text_surf = font1.render("Données général", True, (255,255,255))
        window.blit(text_surf, text_surf.get_rect(center = (size_screen[0]//3, conv_sizey(50)+conv_sizey(20))))
        pygame.draw.rect(window, (255,255,255), pygame.Rect(size_screen[0]//3-conv_sizex(80), conv_sizey(50), conv_sizex(160), conv_sizey(40)), 2,3)

        pygame.draw.rect(window, (63,72,204), pygame.Rect(2*size_screen[0]//3-conv_sizex(100), conv_sizey(50), conv_sizex(200), conv_sizey(40)), 0,3)
        text_surf = font1.render("Classement des données", True, (255,255,255))
        window.blit(text_surf, text_surf.get_rect(center = (2*size_screen[0]//3, conv_sizey(50)+conv_sizey(20))))


        text_surf = font1.render(f"Nombre de stations : {all_processed_data['nombre_station']}", True, (255,255,255))
        window.blit(text_surf, text_surf.get_rect(center = (size_screen[0]//2, conv_sizey(300)+conv_sizey(20))))


        #Rafraîchissement de l'écran
        pygame.display.flip()
