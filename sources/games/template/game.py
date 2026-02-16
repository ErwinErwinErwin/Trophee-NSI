"""
Ce mini-jeu 'template' sert à la fois d'exemple simple et documenté afin de comprendre la structure
d'un mini-jeu et de base facile à copier-coller afin de créer un nouveau jeu.

Voici le script principal du mini-jeu qui doit indispensablement contenir les 5 fonctions suivantes :

  - une fonction 'tick' :
    - Elle réalise toute la simulation du mini-jeu.
    - Elle ne retourne rien.
    - Le nombre d'exécutions de cette fonction par seconde doit être défini par la clé 'simulation_speed' du fichier 'config.json'.
    - Elle doit posséder les paramètres 'keys' et 'mouse' permettant d'obtenir les touches pressées et les informations liées à la souris:
      - 'keys' est un dictionnaire dont les clés sont des constantes de pygame (K_a, K_b, ..., K_z, K_UP, K_DOWN, etc) et les valeurs des entiers représentant la durée de la pression (0 = pas pressée, 1 = nouvellement pressée, >0 = pressée). Toutes les clés désirées du dictionnaire doivent être indiquées dans une liste associée à 'keys' dans 'config.json'
      - 'mouse' est un dictionnaire possèdant 3 clés-valeurs : {'x': int, 'y': int, 'click': bool}
  
  - une fonction 'display' :
    - Elle retourne un objet pygame.Surface correspondant à l'affichage du mini-jeu au moment de son exécution.
    - La taille de cette surface doit être constante et donnée dans 'config.json' avec les clés 'width' et 'height'.
    - Le nombre d'exécutions de cette fonction par seconde n'est pas défini à l'avance et dépendra du script principal et/ou des préférences de l'utilisateur.
  
  - une fonction 'events' :
    - Elle retourne la liste des évènements s'étant produit depuis la dernier appel de la fonction.
    - Un évènement est un dictionnaire contenant au moins la clé 'type' dont la valeur est une chaine de caractères parmi 'pause' et 'exit'.
  
  - une fonction 'init' qui doit initialiser/réinitialiser le mini-jeu.
  
  -  une fonction 'load':
    - Elle est exécutée seulement au 1er lancement du mini-jeu avant toutes les autres.
    - Elle charge les assets et ne renvoie rien.
    - Elle doit posséder un paramètre 'utils' de type dictionnaire :
      - Il permet de récupérer les fonctions utilitaires.
      - Les clés sont des str correspondant au nom des fonctions et la valeur est la fonction elle-même.
      - Les fonctions utilitaires se trouvent dans sources/utils.py
"""

# Pour cet exemple je vais coder un jeu de plateforme basique

import pygame
from os import path

WINDOW_SIZE = (800, 600)
FOLDER_PATH = path.dirname(__file__)  # Chemin absolu du dossier contenant ce script
x, y = 0, 0  # Coordonnées du joueur
spx, spy = 0, 0  # Vitesse du joueur
mouse_pos = {"x": 0, "y": 0}
falling = 0  # si vaut 0 : au sol, si supérieur à 0 : en l'air
event_list = []  # Liste des évènements

# On initie les variables qui vont contenir les assets
# Préciser le type de la variable est facultatif mais permet à l'éditeur de code de proposer l'auto-complétion
player_image: pygame.Surface = None
background: pygame.Surface = None
jump_sound: pygame.mixer.Sound = None

# On définit les 5 fonctions principales

def load(utils: dict) -> None:
    """
    load récupère les fonctions utilitaires et charge les assets.
    
    :param utils: Un dictionnaire contenant les fonctions utilitaires définies dans sources/utils.py
    :type utils: dict[str, function]
    """
    global player_image, background, jump_sound
    
    assets = {}
    utils["loadAssetsFolder"](assets, path.join(FOLDER_PATH, "assets"))  # On utilise la fonction utilitaire loadAssetsFolder définie dans sources/utils.py
    
    player_image = assets["images"]["player.png"]
    background = assets["images"]["background.png"]
    jump_sound = assets["sounds"]["jump.mp3"]

    # On adapte la taille des images
    player_image = pygame.transform.scale(player_image, (128, 128))
    background = pygame.transform.scale(background, (800, 600))


def init() -> None:
    """
    Initialise/réinitialise le mini-jeu
    """
    global x, y, spx, spy, falling
    x, y = 400, 300
    spx, spy = 0, 0
    falling = 0
    event_list.clear()


def tick(keys: dict, mouse: dict) -> None:  # Fonction indispensable qui va gérer le déplacement du joueur et l'option pour sortir du jeu dans cet example
    """
    Docstring for tick
    
    :param keys: Dictionnaire des touches pressées par l'utilisateur. Les valeurs correspondent à la durée de la pression de la touche. Exemple `{pygame.K_UP: 8, pygame.K_LEFT: 0, pygame.K_RIGHT: 1}`
    :type keys: dict
    :param mouse: Dictionnaire contenant les informations liées à la souris `{'x': int, 'y'; int, 'click': bool}`
    :type mouse: dict
    """
    global spx, spy, x, y, falling, mouse_pos

    # Mis à jour de la position de la souris

    mouse_pos["x"], mouse_pos["y"] = mouse["x"], mouse["y"]

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
    
    # On ajoute un point rouge à la position de la souris
    pygame.draw.circle(surface, (255, 0, 0), (mouse_pos["x"], mouse_pos["y"]), 4)
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
    