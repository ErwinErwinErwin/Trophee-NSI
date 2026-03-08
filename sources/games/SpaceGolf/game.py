# Importation des librairies

import pygame
from os import path
from .physics import CelestialBody, Vector
from utils import loadAssetsFolder

WINDOW_WIDTH, WINDOW_HEIGHT = WINDOW_SIZE = (1600, 900)
FOLDER_PATH = path.dirname(__file__)  # Chemin absolu du dossier contenant ce script

mouse_pos = {"x": 0, "y": 0}
cam_x = 0
cam_y = 0
event_list = []  # Liste des évènements

earth = CelestialBody(0, 0, 5.972e24)
sun = CelestialBody(1e8, 0, 1e27)
launched = False
launching = False
launch_start = None
launch_speed = Vector()

# On initie les variables qui vont contenir les assets
# Préciser le type de la variable est facultatif mais permet à l'éditeur de code de proposer l'auto-complétion
earth_image: pygame.Surface = None
background: pygame.Surface = None

# On définit les 5 fonctions principales

def load() -> None:
    """
    La fonction load charge les assets.
    """
    global earth_image, background
    
    assets = {}
    loadAssetsFolder(assets, path.join(FOLDER_PATH, "assets"))  # On utilise la fonction utilitaire loadAssetsFolder définie dans sources/utils.py
    
    earth_image = assets["images"]["earth.png"]
    background = assets["images"]["space.png"]

    # On adapte la taille des images
    earth_image = pygame.transform.scale_by(earth_image, 0.25)


def init() -> None:
    """
    Initialise/réinitialise le mini-jeu
    """
    global launched, launching
    earth.stop()
    launched = False
    launching = False
    launch_speed.magnitude = 0
    event_list.clear()


def tick(keys: dict, mouse: dict) -> None:
    """
    Docstring for tick
    
    :param keys: Dictionnaire des touches pressées par l'utilisateur. Les valeurs correspondent à la durée de la pression de la touche. Exemple `{pygame.K_UP: 8, pygame.K_LEFT: 0, pygame.K_RIGHT: 1}`
    :type keys: dict
    :param mouse: Dictionnaire contenant les informations liées à la souris `{'x': int, 'y'; int, 'click': list[int, int, int]}`
    :type mouse: dict
    """
    global mouse_pos, cam_x, cam_y, launch_start, launching, launched

    if not launched:
        if launching:
            launch_speed.coordinates = launch_start[0] - mouse["x"], launch_start[1] - mouse["y"]
            if mouse["click"][0] == 0:
                launched = True
                launching = False
                earth.speed.direction = launch_speed.direction
                earth.speed.magnitude = launch_speed.magnitude * 100
                earth.addInteraction(sun)
        else:
            # La souris vient dêtre cliquée et touche la Terre
            if mouse["click"][0] == 1 and (mouse["x"] - (WINDOW_WIDTH//2-cam_x+earth.x//100000))**2 + (mouse["y"] - (WINDOW_HEIGHT//2-cam_y+earth.y//100000))**2 < 130**2:
                launching = True
                launch_start = mouse["x"], mouse["y"]

    # Si le clic gauche de la souris est pressé, on compare sa position à la précédente pour faire déplacer la caméra
    if mouse["click"][0] > 0 and not launching:
        cam_x += mouse_pos["x"] - mouse["x"]
        cam_y += mouse_pos["y"] - mouse["y"]
    
    earth.move(1/40*1000)

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
    surface = pygame.Surface(WINDOW_SIZE)
    # On remplit le fond en dupliquant une image de l'espace
    for x in range(cam_x//-16%background.width-background.width, WINDOW_WIDTH, background.width):
        for y in range(cam_y//-16%background.height-background.height, WINDOW_HEIGHT, background.height):
            surface.blit(background, (x, y))
    pygame.draw.circle(surface, (255, 0, 0), (WINDOW_WIDTH//2-cam_x+1e8//100000, WINDOW_HEIGHT//2-cam_y), 100)
    if launching:
        pygame.draw.line(surface, (255, 0, 0), launch_start, (mouse_pos["x"], mouse_pos["y"]), 3)
    # On ajoute la planète Terre
    surface.blit(earth_image, (WINDOW_WIDTH//2-earth_image.width//2-cam_x+earth.x//100000, WINDOW_HEIGHT//2-earth_image.height//2-cam_y+earth.y//100000))
    
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
    