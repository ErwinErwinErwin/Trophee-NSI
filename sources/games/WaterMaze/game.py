# Importation des librairies

import pygame
from os import path
from games.WaterMaze.sph_water import SPHSimulation

WINDOW_WIDTH, WINDOW_HEIGHT = WINDOW_SIZE = (1600, 900)
FOLDER_PATH = path.dirname(__file__)  # Chemin absolu du dossier contenant ce script

mouse_pos = {"x": 0, "y": 0}
cam_x = 0
cam_y = 0
event_list = []  # Liste des évènements
l_fps = -1 #fps du dernier tick

# On initie les variables qui vont contenir les assets
background: pygame.Surface = None

# SPH Water Simulation
sph_sim: SPHSimulation = None

# On définit les 5 fonctions principales

def load(utils: dict) -> None:
    """
    load récupère les fonctions utilitaires et charge les assets.

    :param utils: Un dictionnaire contenant les fonctions utilitaires définies dans sources/utils.py
    :type utils: dict[str, function]
    """
    global background

    assets = {}
    utils["loadAssetsFolder"](assets, path.join(FOLDER_PATH, "assets"))  # On utilise la fonction utilitaire loadAssetsFolder définie dans sources/utils.py

    background = assets["images"]["space.png"]


    
i = 0

def init() -> None:
    """
    Initialise/réinitialise le mini-jeu
    """
    
    global sph_sim
    
    event_list.clear()
    # Initialise la simulation avec 150 particules
    sph_sim = SPHSimulation(width=800, height=600, particle_count=150)


def tick(keys: dict, mouse: dict, fps:float) -> None:
    """
    Met à jour le jeu, execute un tick

    :param keys: Dictionnaire des touches pressées par l'utilisateur. Les valeurs correspondent à la durée de la pression de la touche. Exemple `{pygame.K_UP: 8, pygame.K_LEFT: 0, pygame.K_RIGHT: 1}`
    :type keys: dict
    :param mouse: Dictionnaire contenant les informations liées à la souris `{'x': int, 'y'; int, 'click': bool}`
    :type mouse: dict
    """
    global mouse_pos, cam_x, cam_y, sph_sim, l_fps, i
    

    
    if l_fps == -1:
        fps = 40
    l_fps = fps
    
    
    
    # Si la souris est cliquée, on compare sa position à la précédente pour faire déplacer la caméra
    if mouse["click"]:
        cam_x += mouse_pos["x"] - mouse["x"]
        cam_y += mouse_pos["y"] - mouse["y"]
        # Add water particle at mouse position for interaction
        world_x = mouse["x"] + cam_x
        world_y = mouse["y"] + cam_y
        if sph_sim and (0 < mouse['x'] < sph_sim.width and 0 < mouse['y'] < sph_sim.height):
            sph_sim.add_particle(world_x, world_y)

    # Mis à jour de la position de la souris
    mouse_pos["x"], mouse_pos["y"] = mouse["x"], mouse["y"]

    # Option pour mettre en pause
    if keys[pygame.K_ESCAPE]:
        event_list.append({"type": "pause"})

    if i < 10:
        sph_sim.step(dt=0.0001)  # fps timestep
    
    # Met à jour la simulation
    if sph_sim:
        sph_sim.step(dt=(1/(fps+1))) # fps timestep
        
    
    i+=1


def display() -> pygame.Surface:
    """
    Rendu du jeu

    :return: L'affichage du mini-jeu
    :rtype: pygame.Surface
    """
    surface = pygame.Surface(WINDOW_SIZE)
    surface.fill((100,100,100))
    
    # Dessiner les particules d'eau
    if sph_sim:
        sph_sim.draw(surface, cam_x, cam_y)

        # Afficher les informations
        font = pygame.font.Font(None, 24)
        text = font.render(f"Particules: {sph_sim.get_particle_count()}", True, (0, 0, 0))
        surface.blit(text, (10, 10))
        help_text = font.render("Cliquez et bouger pour vous déplacer, cliquer ajoute des particules", True, (0, 0, 0))
        surface.blit(help_text, (10, 40))
        
        global l_fps
        
        #afficher les fps
        surface.blit(font.render(f"FPS: {l_fps}", True, (0,0,0)), (10,60))

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
    