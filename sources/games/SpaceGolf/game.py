# Importation des librairies

import pygame
from os import path
from .physics import CelestialBody, Vector
from utils import loadAssetsFolder, RangeInput

WINDOW_WIDTH, WINDOW_HEIGHT = WINDOW_SIZE = (1600, 900)
FOLDER_PATH = path.dirname(__file__)  # Chemin absolu du dossier contenant ce script

mouse_pos = {"x": 0, "y": 0}
cam_x = 0
cam_y = 0
event_list = []  # Liste des évènements
scale = 100000  # 1 pixel = 100 000 mètres
time_scale = 600  # 1 seconde dans la réalité correspond à 600 seconde dans le jeu

surface = pygame.Surface(WINDOW_SIZE)  # La surface utilisée dans la fonction display

earth = CelestialBody(0, 0, 5.972e24, 6.4e6)
sun = CelestialBody(1.5e9, 0, 1e27, 7e8)
launched = False
launching = False
launch_start = None
launch_speed = Vector()
zoom_input: RangeInput = None
time_input: RangeInput = None

# On initie les variables qui vont contenir les assets
# Préciser le type de la variable est facultatif mais permet à l'éditeur de code de proposer l'auto-complétion
earth_images: dict[int, pygame.Surface] = {}
background: pygame.Surface = None

# On définit les fonctions secondaires

def setScale(value: int) -> None:
    """
    Change l'échelle du rendu en gardant la caméra centré au même endroit.

    :param value: Nouvelle valeur de scale
    :type value: int
    """
    global scale, cam_x, cam_y
    x = scale * cam_x  # cam_x est en pixels, x est en mètres
    y = scale * cam_y  # cam_y est en pixels, y est en mètres
    scale = value
    cam_x = x // scale
    cam_y = y // scale


def screenPosition(x: int, y: int) -> tuple:
    """
    Retourne la position d'un élément relative à l'écran depuis sa position 
    absolue (en m) et en prenant en compte le zoom et la position de la caméra.

    :param x: Abscisse absolue de l'élément
    :type x: int (m)
    :param y: Ordonnée absolue de l'élément
    :type y: int (m)
    :return: La position relative au coin supérieur gauche de l'écran
    :rtype: tuple[int, int]
    """
    return WINDOW_WIDTH//2-cam_x+x//scale, WINDOW_HEIGHT//2-cam_y+y//scale

# On définit les 5 fonctions principales

def load() -> None:
    """
    La fonction load charge les assets.
    """
    def convertTime(value: int) -> str:
        if value >= 3600:
            return f"1s : {value//3600}h"
        elif value >= 60:
            return f"1s : {value//60}min"
        else:
            return f"1s : {value}s"
    
    global background, zoom_input, time_input
    
    assets = {}
    loadAssetsFolder(assets, path.join(FOLDER_PATH, "assets"))  # On utilise la fonction utilitaire loadAssetsFolder définie dans sources/utils.py
    
    earth_image = assets["images"]["earth.png"]
    background = assets["images"]["space.png"]

    # On adapte la taille des images
    earth_images[50000] = pygame.transform.scale_by(earth_image, 0.5)

    # Une fois les assets chargées on peut créer le RangeInput
    font = assets["fonts"]["inter.ttf"].getFont(24)
    zoom_input = RangeInput(36, WINDOW_HEIGHT-36, 160, (50000, 500000, 10000), surface, lambda value: f"1px : {value}m", font, 12, 100000)
    time_input = RangeInput(230, WINDOW_HEIGHT-36, 160, (60, 1200, 60), surface, convertTime, font, 12, 600)


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
    global mouse_pos, cam_x, cam_y, launch_start, launching, launched, scale, time_scale

    if not launched:
        if launching:
            launch_speed.coordinates = launch_start[0] - mouse["x"], launch_start[1] - mouse["y"]
            if mouse["click"][0] == 0:
                # launched = True
                launching = False
                earth.speed.direction = launch_speed.direction
                # On convertit la distance du lancement en une vitesse de lancement en m/s avec l'échelle suivante : 750 m = 1 m/s
                earth.speed.magnitude = launch_speed.magnitude * scale / 750
                earth.addInteraction(sun)
        else:
            # La souris vient dêtre cliquée
            if mouse["click"][0] == 1:
                earth_x, earth_y = screenPosition(earth.x, earth.y)
                # La souris touche la Terre
                if (mouse["x"] - earth_x)**2 + (mouse["y"] - earth_y)**2 < (6.2e6/scale)**2:
                    earth.stop()
                    launching = True
                    launch_start = mouse["x"], mouse["y"]
    
    # Simulation des boutons
    zoom_input.tick((mouse["x"], mouse["y"]), mouse["click"][0])
    setScale(zoom_input.value)
    time_input.tick((mouse["x"], mouse["y"]), mouse["click"][0])
    time_scale = time_input.value

    # Si le clic gauche de la souris est pressé, on compare sa position à la précédente pour faire déplacer la caméra
    if mouse["click"][0] > 0 and not launching and not (zoom_input.clicked or time_input.clicked):
        cam_x += mouse_pos["x"] - mouse["x"]
        cam_y += mouse_pos["y"] - mouse["y"]
    
    earth.move(1/40*time_scale)

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
    surface.fill((0, 0, 0))
    # On remplit le fond en dupliquant une image de l'espace
    for x in range(round(cam_x*scale*-1.5e-7)%background.width-background.width, WINDOW_WIDTH, background.width):
        for y in range(round(cam_y*scale*-1.5e-7)%background.height-background.height, WINDOW_HEIGHT, background.height):
            surface.blit(background, (x, y))
    
    # On affiche le soleil
    sun_x, sun_y = screenPosition(sun.x, sun.y)
    pygame.draw.circle(surface, (255, 0, 0), (sun_x, sun_y), round(sun.radius/scale))

    if launching:
        pygame.draw.line(surface, (255, 0, 0), launch_start, (mouse_pos["x"], mouse_pos["y"]), 3)
    
    # On ajoute la planète Terre
    if scale in earth_images:
        earth_image = earth_images[scale]
    else:
        earth_image = pygame.transform.scale_by(earth_images[50000], 50000/scale)
        earth_images[scale] = earth_image
    
    earth_x, earth_y = screenPosition(earth.x, earth.y)
    surface.blit(earth_image, (earth_x - earth_image.width//2, earth_y - earth_image.width//2))

    # On affiche les boutons
    zoom_input.display()
    time_input.display()
    
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
    