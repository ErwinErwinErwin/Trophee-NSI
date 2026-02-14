# Importation des librairies

import pygame
from os import scandir, path
from sys import exit
from json import load

# Lecture des mini-jeux

def loadGame(folder: str) -> dict:
    """
    Docstring for loadGame
    
    :param folder: Nom du dossier du mini-jeu
    :type folder: str
    :return: Un dictionnaire contenant les 4 fonctions `tick`, `display`, `events` et `init` ainsi que le contenu de config.json
    :rtype: dict
    """
    game = {}
    # On ouvre le fichier config.json du mini-jeu pour récupérer son contenu
    with open(path.join(FOLDER_PATH, "games", folder, "config.json"), "r") as f:
        game["config"] = load(f)

    # On charge l'arrière-plan affiché dans le menu des mini-jeux
    game["menu_background"] = pygame.image.load(path.join(FOLDER_PATH, "games", folder, "menu_background.png"))
    
    # On importe dynamiquement les fonctions principales du fichier game.py
    module = __import__(f"games.{folder}.game", fromlist=["tick", "display", "events", "init"])
    # On stocke les 3 fonctions principales dans le dictionnaire
    game["tick"] = module.tick
    game["display"] = module.display
    game["events"] = module.events
    game["init"] = module.init
    return game


games: list[dict] = []
NEEDED_FILES = ("game.py", "config.json", "menu_background.png")  # Fichiers indispensables dans un dossier de mini-jeu
FOLDER_PATH = path.dirname(__file__)  # Chemin absolu du dossier contenant ce script
print()

for element in scandir(path.join(FOLDER_PATH, "games")):
    if element.is_dir():
        # On vérifie que tous les fichiers indispensables existent
        if all(path.exists(path.join(element.path, needed_file)) for needed_file in NEEDED_FILES):
            print("[Info] Dossier de mini-jeu détecté :", element.name)
            games.append(loadGame(element.name))
        else:
            print(f"[Erreur] Le dossier '{element.name}' ne contient pas tous les fichiers indispensables")
            print("[Rappel] les fichiers indispensables sont :", ", ".join(NEEDED_FILES))

if len(games) == 0:
    print("[Erreur] Aucun jeu n'a été chargé : arrêt du programme")
    exit()

print("\nChargement des mini-jeux terminé :", len(games), "mini-jeu(x) chargé(s)")

# Création de la fenêtre pygame

window_size = (800, 600)
window = pygame.display.set_mode(window_size, pygame.RESIZABLE)
pygame.display.set_caption("Physics.play")
icon = pygame.image.load(path.join(FOLDER_PATH, "assets", "images", "icon.png"))
pygame.display.set_icon(icon)

clock = pygame.time.Clock()  # Pour réguler la vitesse de la boucle principale

def playGame(game: dict, window: pygame.Surface) -> None:
    """
    playGame est une fonction bloquante qui va lancer le jeu passé en paramètre puis gérer tous
    les échanges de données entre ce script et le mini-jeu.
    La fonction s'arrêtera quand le mini-jeu renverra l'évènement de type 'quit' ou quand l'utilisateur fermera la fenêtre.
    
    :param game: Un dictionnaire contenant les clés 'config', 'menu_background', 'tick', 'display' et 'events'
    :type game: dict
    :param window: La fenêtre sur laquelle va être affiché le mini-jeu
    :type window: pygame.Surface
    :return: True si l'utilisateur a fermé la fenêtre sinon False
    :rtype: bool
    """
    CONFIG = game["config"]
    SPEED = CONFIG["simulation_speed"]
    RENDERING_WIDTH = CONFIG["width"]
    RENDERING_HEIGHT = CONFIG["height"]
    KEYS = [getattr(pygame, key, -1) for key in CONFIG["keys"]]  # On passe d'une liste de str (ex : 'K_a') à une liste de constante de pygame (ex : pygame.K_a)

    # On affecte les fonctions principales à des variables pour faciliter leur utilisation
    tick = game["tick"]
    display = game["display"]
    events = game["events"]
    init = game["init"]

    init()  # On initialise le mini-jeu

    keys_to_send = {key: False for key in KEYS}  # Dictionnaire qui va être envoyé à la fonction tick du mini-jeu
    mouse = {"x": 0, "y": 0, "click": False}

    fps = SPEED  # Nombre de rafraichissement de l'écran par seconde, varie de 1 à SPEED
    cooldown_before_render = 0  # Augmente de fps/SPEED à chaque itération de la boucle. L'écran sera actualisé à chaque fois qu'il atteint 1

    while True:

        # Gestion des évènements de la fenêtre

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # L'utilisateur a fermé la fenêtre
                return True
            if event.type == pygame.KEYDOWN:  # Une touche a été pressée
                if event.key in KEYS:
                    keys_to_send[event.key] = True
            elif event.type == pygame.KEYUP:  # Une touche a été relachée
                if event.key in KEYS:
                    keys_to_send[event.key] = False
        
        window_size = window.get_size()

        # On calcule le ratio à appliquer sur le rendu afin de l'adapter à la taille de la fenêtre
        scale_x = window_size[0] / RENDERING_WIDTH
        scale_y = window_size[1] / RENDERING_HEIGHT
        scale = min(scale_x, scale_y)
        
        # On convertit la position de la souris sur la fenêtre pour qu'elle s'adapte à la taille du mini-jeu
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_x -= window_size[0]//2 - RENDERING_WIDTH//2 * scale
        mouse_x = round(mouse_x / scale)
        mouse_y -= window_size[1]//2 - RENDERING_HEIGHT//2 * scale
        mouse_y = round(mouse_y / scale)
        mouse_x = min(RENDERING_WIDTH-1, max(0, mouse_x))
        mouse_y = min(RENDERING_HEIGHT-1, max(0, mouse_y))
        mouse["x"], mouse["y"] = mouse_x, mouse_y
        mouse["click"] = pygame.mouse.get_pressed()[0]

        tick(keys=keys_to_send, mouse=mouse)  # On simule le mini-jeu

        for event in events():
            if event["type"] == "quit":  # Le mini-jeu est fini
                return False

        cooldown_before_render += fps / SPEED
        if cooldown_before_render >= 1:
            cooldown_before_render -= 1
            game_rendering = display()  # On récupère le rendu du mini-jeu
            if game_rendering.get_size() != (RENDERING_WIDTH, RENDERING_HEIGHT):
                print(f"[Erreur] La taille du rendu graphique du mini-jeu '{CONFIG["name"]}' ne correspond pas à sa configuration")
                return False
            
            color = CONFIG.get("background_color", (0, 0, 0))
            window.fill(color)  # On efface la fenêtre avec la couleur donnée dans la configuration, par défaut du noir

            # On adapte le rendu à la taille de la fenêtre en préservant son ratio
            game_rendering = pygame.transform.scale_by(game_rendering, scale)

            rendering_size = game_rendering.get_size()
            window.blit(game_rendering, (window_size[0]//2-rendering_size[0]//2, window_size[1]//2-rendering_size[1]//2))  # On applique le rendu en le centrant
            pygame.display.flip()  # On actualise la fenêtre
            
        clock.tick(SPEED)  # On limite la boucle à SPEED tours par seconde


# Initialisation des variables pour le menu des mini-jeux
game_idx = 0

playGame(games[0], window)

pygame.quit()
