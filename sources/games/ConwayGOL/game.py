# Importation des librairies

import pygame
from os import path
from utils import loadAssetsFolder, RangeInput

WINDOW_WIDTH, WINDOW_HEIGHT = WINDOW_SIZE = (1600, 900)
FOLDER_PATH = path.dirname(__file__)  # Chemin absolu du dossier contenant ce script

mouse_pos = {"x": 0, "y": 0}
cam_x = 0
cam_y = 0
event_list = []  # Liste des évènements

surface = pygame.Surface(WINDOW_SIZE)  # La surface utilisée dans la fonction display

# Préciser le type de la variable est facultatif mais permet à l'éditeur de code de proposer l'auto-complétion
# Les variables initialisées à None sont des variables globales qui seront initialisées dans la fonction load



# On initialise les variables qui vont contenir les assets
background: pygame.Surface = None

# On définit les 5 fonctions principales

def load() -> None:
    """
    La fonction load charge les assets.
    """
    
    assets = {}
    loadAssetsFolder(assets, path.join(FOLDER_PATH, "assets"))  # On utilise la fonction utilitaire loadAssetsFolder définie dans sources/utils.py


def init() -> None:
    """
    Initialise/réinitialise le mini-jeu
    """
    global cam_x, cam_y
    event_list.clear()
    cam_x = cam_y = 0


def tick(keys: dict, mouse: dict) -> None:
    """
    Docstring for tick
    
    :param keys: Dictionnaire des touches pressées par l'utilisateur. Les valeurs correspondent à la durée de la pression de la touche. Exemple `{pygame.K_UP: 8, pygame.K_LEFT: 0, pygame.K_RIGHT: 1}`
    :type keys: dict
    :param mouse: Dictionnaire contenant les informations liées à la souris `{'x': int, 'y'; int, 'click': list[int, int, int]}`
    :type mouse: dict
    """
    global mouse_pos, cam_x, cam_y

    mouse_click = mouse["click"][0]  # On utilise une variable temporaire pour pouvoir stopper la propagation d'un clic si celui-ci est intercepté par un bouton
    
    # Simulation des boutons
    

    # Si le clic gauche de la souris est pressé, on compare sa position à la précédente pour faire déplacer la caméra
    if mouse_click > 0:
        cam_x += mouse_pos["x"] - mouse["x"]
        cam_y += mouse_pos["y"] - mouse["y"]

    # Mis à jour de la position de la souris

    mouse_pos["x"], mouse_pos["y"] = mouse["x"], mouse["y"]

    # Option pour mettre en pause

    if keys[pygame.K_ESCAPE]:
        event_list.append({"type": "pause"})


def display() -> pygame.Surface:
    """
    Docstring for display
    
    :return: L'affichage du mini-jeu
    :rtype: pygame.Surface
    """
    surface.fill((255, 255, 255))

    # On affiche les boutons
    
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
    