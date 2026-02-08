"""
Voici le script principal du mini-jeu qui doit indispensablement contenir les 4 fonctions suivantes :

  - une fonction 'tick' :
    - Elle réalise toute la simulation du mini-jeu.
    - Elle ne retourne rien.
    - Le nombre d'exécutions de cette fonction par seconde doit être défini par la clé 'simulation_speed' du fichier 'config.json'.
    - Elle doit posséder les paramètres 'keys' et 'mouse' permettant d'obtenir les touches pressées et les informations liées à la souris:
      - 'keys' est un dictionnaire dont les clés sont des constantes de pygame (K_a, K_b, ..., K_z, K_UP, K_DOWN, etc) et les valeurs des booléens. Toutes les clés désirées du dictionnaire doivent être indiquées dans une liste associée à 'keys' dans 'config.json'
      - 'mouse' est un dictionnaire possèdant 3 clés-valeurs : {'x': int, 'y': int, 'click': bool}
  
  - une fonction 'display' :
    - Elle retourne un objet pygame.Surface correspondant à l'affichage du mini-jeu au moment de son exécution.
    - La taille de cette surface doit être constante et donnée dans 'config.json' avec les clés 'width' et 'height'.
    - Le nombre d'exécutions de cette fonction par seconde n'est pas défini à l'avance et dépendra du script principal et/ou des préférences de l'utilisateur.
  
  - une fonction 'events' :
    - Elle retourne la liste des évènements s'étant produit depuis la dernier appel de la fonction.
    - Un évènement est un dictionnaire contenant au moins la clé 'type' dont la valeur est une chaine de caractères parmi 'pause' et 'exit'.
  
  - une fonction 'init' qui doit initialiser/réinitialiser le mini-jeu 
"""

# Pour cet exemple je vais coder un jeu de plateforme basique

import pygame
from os import path

pygame.mixer.init()  # Afin de jouer des sons plus tard

def init() -> None:
    """
    Initialise/réinitialise le mini-jeu
    """
    global x, y, spx, spy, falling
    x, y = 400, 300
    spx, spy = 0, 0
    falling = 0
    event_list.clear()


WINDOW_SIZE = (800, 600)
FOLDER_PATH = path.dirname(__file__)  # Chemin absolu du dossier contenant ce script
x, y = 0, 0  # Coordonnées du joueur
spx, spy = 0, 0  # Vitesse du joueur
falling = 0  # si vaut 0 : au sol, si supérieur à 0 : en l'air
event_list = []  # Liste des évènements
init()

# Chargement des assets

def loadImage(image_name: str, size: tuple[int] | None = None) -> pygame.Surface:
    """
    Charge une image contenue dans `./assets/images` et lève une erreur si celle-ci n'existe pas
    
    :param image_name: Nom de l'image avec son format
    :type image_name: str
    :param size: Taille de l'image retournée (par défaut la taille de l'image en entrée)
    :type size: (int, int) | None
    :return: Une surface correspondant à l'image
    :rtype: pygame.Surface
    """
    img = pygame.image.load(path.join(FOLDER_PATH, "assets", "images", image_name))
    if size == None:
        return img
    return pygame.transform.scale(img, size)


player_image = loadImage("player.png", (128, 128))
background = loadImage("background.png", (800, 600))
jump_sound = pygame.mixer.Sound(path.join(FOLDER_PATH, "assets", "sounds", "jump.mp3"))

def tick(keys: dict, mouse: dict) -> None:  # Fonction indispensable qui va gérer le déplacement du joueur et l'option pour sortir du jeu dans cet example
    """
    Docstring for tick
    
    :param keys: Dictionnaire des touches pressées par l'utilisateur. Exemple `{pygame.K_UP: False, pygame.K_LEFT: True, pygame.K_RIGHT: False}`
    :type keys: dict
    :param mouse: Dictionnaire contenant les informations liées à la souris `{'x': int, 'y'; int, 'click': bool}`
    :type mouse: dict
    """
    global spx, spy, x, y, falling

    # Simulation de la physique (simple) du joueur

    spx += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * 2  # On fait varier la vitesse x du joueur selon les touches flèche gauche et droite
    spx *= 0.8
    spy += 1.5  # Action de la gravité
    if keys[pygame.K_UP] and falling == 0:
        spy = -20  # On fait sauter le joueur
        jump_sound.play()  # On joue le son 'jump'
    
    x += spx
    if x < 30:  # Bord gauche
        x = 30
        spx = 0
    elif x > 770:  # Bord droit
        x = 770
        spx = 0
    
    y += spy
    falling += 1
    if y > 450 - 64:  # Sol
        y = 450 - 64
        spy = 0
        falling = 0

    # Option pour sortir du jeu avec la touche 'q'

    if keys[pygame.K_q]:
        event_list.append({"type": "quit"})


def display() -> pygame.Surface:
    """
    Docstring for display
    
    :return: L'affichage du mini-jeu
    :rtype: pygame.Surface
    """
    surface = pygame.Surface(WINDOW_SIZE)
    surface.blit(background, (0, 0))  # On ajoute l'arrière-plan
    # On ajoute le joueur
    if spx >= 0:
        surface.blit(player_image, (x-64, y-64))
    else:
        surface.blit(pygame.transform.flip(player_image, True, False), (x-64, y-64))
    return surface


def events() -> list:
    """
    Docstring for events
    
    :return: Retourne la liste des évènements s'étant produit dans le mini-jeu. Exemple `['quit']`
    :rtype: list[str]
    """
    events_copy = event_list.copy()
    event_list.clear()  # On vide la liste des évènements pour ne pas les renvoyer à nouveau au prochain appel
    return events_copy
    