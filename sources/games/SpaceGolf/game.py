# Importation des librairies

import pygame
from os import path
from .physics import Vector, GraphicalCelestialBody, Earth
from utils import loadAssetsFolder, RangeInput, PopUp, SpriteSheet, Button, LoadedFont

WINDOW_WIDTH, WINDOW_HEIGHT = WINDOW_SIZE = (1600, 900)
FOLDER_PATH = path.dirname(__file__)  # Chemin absolu du dossier contenant ce script

mouse_pos = {"x": 0, "y": 0}
cam_x = 0
cam_y = 0
event_list = []  # Liste des évènements
scale = 100000  # 1 pixel = 100 000 mètres
time_scale = 6000  # 1 seconde dans la réalité correspond à 6000 seconde dans le jeu

surface = pygame.Surface(WINDOW_SIZE)  # La surface utilisée dans la fonction display

# Préciser le type de la variable est facultatif mais permet à l'éditeur de code de proposer l'auto-complétion
# Les variables initialisées à None sont des variables globales qui seront initialisées dans la fonction load

assets: dict = None
earth: Earth = None  # La planète Terre, initialisée dans la fonction load
suns: list[GraphicalCelestialBody] = []
black_holes: list[GraphicalCelestialBody] = []
worm_hole: GraphicalCelestialBody = None
launching = False
launch_speed = Vector()
zoom_input: RangeInput = None
time_input: RangeInput = None
level_end: PopUp = None
background: pygame.Surface = None
celestial_bodies: dict[str, pygame.Surface | SpriteSheet] = {}
levels: list[dict] = None
level = 0
max_trials = None
trials = None
fonts: LoadedFont = None
restart_button: Button = None
previous_button: Button = None
next_button: Button = None

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


def loadLevel(index: int) -> None:
    """
    Charge le niveau correspondant au paramètre index.

    :param index: Index du niveau commençant à 0
    :type index: int
    """
    global cam_x, cam_y, max_trials, trials, launching
    cam_x = cam_y = 0
    level = levels[index]
    max_trials = trials = level["trials"]
    launching = False

    earth.reset()
    earth.other_bodies.clear()
    earth.addInteraction(worm_hole)

    wx, wy = level["worm_hole"]
    worm_hole.x = wx
    worm_hole.y = wy
    
    suns.clear()
    for x, y, mass, radius, costume in level["suns"]:
        sun = GraphicalCelestialBody(x, y, mass, radius, celestial_bodies["suns"][costume], surface, screenPosition)
        earth.addInteraction(sun)
        suns.append(sun)
    
    black_holes.clear()
    for x, y, mass, radius, costume in level["black_holes"]:
        black_hole = GraphicalCelestialBody(x, y, mass, radius, celestial_bodies["black_holes"][costume], surface, screenPosition, True)
        earth.addInteraction(black_hole)
        black_holes.append(black_hole)
    

# On définit les 5 fonctions principales

def load() -> None:
    """
    La fonction load charge les assets.
    """

    # On définit les fonctions qui vont servir de callback dans les boutons

    def convertTime(value: int) -> str:
        if value >= 3600:
            return f"1s : {value//3600}h {(value%3600)//60}min"
        elif value >= 60:
            return f"1s : {value//60}min"
        else:
            return f"1s : {value}s"
    
    def convertDistance(value: int) -> str:
        if value >= 1e9:
            return f"1px : {round(value/1e9)} x 10^6 km"
        elif value >= 1e6:
            return f"1px : {round(value/1e6)} x 10^3 km"
        elif value >= 1000:
            return f"1px : {value//1000} km"
        else:
            return f"1px : {value} m"
    
    def onClickHome() -> None:
        level_end.displayed = False
        event_list.append({"type": "quit"})
    
    def onClickNext() -> None:
        global level
        level = min(level + 1, len(levels) - 1)
        level_end.displayed = False
        loadLevel(level)

    def onClickPrevious() -> None:
        global level
        level = max(level - 1, 0)
        level_end.displayed = False
        loadLevel(level)
    
    def onClickRestart() -> None:
        global cam_x, cam_y, trials
        cam_x = cam_y = 0
        trials = max_trials
        earth.reset()
    
    global background, zoom_input, time_input, earth, worm_hole, level_end, assets, levels, fonts, restart_button, previous_button, next_button
    
    assets = {}
    loadAssetsFolder(assets, path.join(FOLDER_PATH, "assets"))  # On utilise la fonction utilitaire loadAssetsFolder définie dans sources/utils.py
    levels = assets["json"]["levels.json"]

    # On charge les soleils
    suns = []
    celestial_bodies["suns"] = suns
    suns.append(assets["images"]["sun1[SPRITESHEET;500;10].png"])
    suns.append(assets["images"]["sun2[SPRITESHEET;465;10].png"])
    suns.append(assets["images"]["sun3[SPRITESHEET;333;10].png"])
    suns.append(assets["images"]["sun4[SPRITESHEET;156;10].png"])

    # On charge le trou de ver
    celestial_bodies["worm_hole"] = assets["images"]["worm_hole[SPRITESHEET;400;20].png"]

    # On charge le trou noir
    celestial_bodies["black_holes"] = [assets["images"]["black_hole[SPRITESHEET;498;30].png"]]

    # On créé le trou de ver
    worm_hole = GraphicalCelestialBody(0, 0, 1e33, 2e7, celestial_bodies["worm_hole"], surface, screenPosition, True)
    
    # On créé la Terre
    earth = Earth(0, 0, assets["images"]["earth.png"], surface, screenPosition, worm_hole)

    # On charge le fond
    background = assets["images"]["space.png"]

    level_end = PopUp(surface, WINDOW_WIDTH//2, WINDOW_HEIGHT//2, assets["images"]["popup.png"],
                      Button(230, 120, assets["images"]["home.png"], onClickHome),
                      Button(-212, 120, assets["images"]["next.png"], onClickNext))

    # Une fois les assets chargées on peut créer le RangeInput
    fonts = assets["fonts"]["inter.ttf"]
    font = fonts.getFont(24)
    zoom_input = RangeInput(36, WINDOW_HEIGHT-36, 160, (50000, 500000, 10000), surface, convertDistance, font, 12, 100000)
    time_input = RangeInput(230, WINDOW_HEIGHT-36, 160, (600, 14400, 600), surface, convertTime, font, 12, 5400)

    # On créé les boutons cliquables
    restart_button = Button(WINDOW_WIDTH//2, 30, assets["images"]["restart.png"], onClickRestart)
    previous_button = Button(WINDOW_WIDTH//2 - 60, 30, assets["images"]["previous_button.png"], onClickPrevious)
    next_button = Button(WINDOW_WIDTH//2 + 60, 30, assets["images"]["next_button.png"], onClickNext)


def init() -> None:
    """
    Initialise/réinitialise le mini-jeu
    """
    global level
    level = 0
    loadLevel(0)
    event_list.clear()
    level_end.displayed = False
    zoom_input.value = 100000
    time_input.value = 5400


def tick(keys: dict, mouse: dict) -> None:
    """
    Docstring for tick
    
    :param keys: Dictionnaire des touches pressées par l'utilisateur. Les valeurs correspondent à la durée de la pression de la touche. Exemple `{pygame.K_UP: 8, pygame.K_LEFT: 0, pygame.K_RIGHT: 1}`
    :type keys: dict
    :param mouse: Dictionnaire contenant les informations liées à la souris `{'x': int, 'y'; int, 'click': list[int, int, int]}`
    :type mouse: dict
    """
    global mouse_pos, cam_x, cam_y, launching, scale, time_scale, trials

    mouse_click = mouse["click"][0]  # On utilise une variable temporaire pour pouvoir stopper la propagation d'un clic si celui-ci est intercepté par un bouton

    # Simulation des pop-up
    if level_end.displayed:
        if level_end.tick(mouse["x"], mouse["y"], mouse_click):
            mouse_click = 0
    
    # Simulation des boutons
    zoom_input.tick((mouse["x"], mouse["y"]), mouse_click)
    setScale(zoom_input.value)
    time_input.tick((mouse["x"], mouse["y"]), mouse_click)
    time_scale = time_input.value
    if zoom_input.clicked or time_input.clicked:
        mouse_click = 0
    
    param = (mouse["x"], mouse["y"], mouse_click)
    if any((restart_button.tick(*param),
           previous_button.tick(*param),
           next_button.tick(*param))):
        mouse_click = 0

    if trials > 0:
        if launching:
            earth_x, earth_y = screenPosition(earth.x, earth.y)
            launch_speed.coordinates = earth_x - mouse["x"], earth_y - mouse["y"]
            if mouse_click == 0:
                launching = False
                earth.speed.direction = launch_speed.direction
                # On convertit la distance du lancement en une vitesse de lancement en m/s avec l'échelle suivante : 7500 m = 1 m/s
                earth.speed.magnitude = launch_speed.magnitude * scale / 7500
                earth.locked = False
                trials -= 1
        else:
            # La souris vient dêtre cliquée
            if mouse_click == 1:
                earth_x, earth_y = screenPosition(earth.x, earth.y)
                # La souris touche la Terre
                if (mouse["x"] - earth_x)**2 + (mouse["y"] - earth_y)**2 < (6.2e6/scale)**2:
                    earth.stop()
                    launching = True
                    earth.locked = True
                    mouse_click = 0

    # Si le clic gauche de la souris est pressé, on compare sa position à la précédente pour faire déplacer la caméra
    if mouse_click > 0 and not launching:
        cam_x += mouse_pos["x"] - mouse["x"]
        cam_y += mouse_pos["y"] - mouse["y"]
    
    earth.move(1/40, time_scale)
    if earth.fallen:  # Tombée dans un trou noir
        if earth.success:
            level_end.displayed = True
        else:
            earth.reset()

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

    if launching:
        pygame.draw.line(surface, (255, 0, 0), screenPosition(earth.x, earth.y), (mouse_pos["x"], mouse_pos["y"]), 4)
    
    # On ajoute la planète Terre, les soleils, le trou de ver et les trous noirs
    for sun in suns:
        sun.display(scale)
    for black_hole in black_holes:
        black_hole.display(scale)
    worm_hole.display(scale)
    if not earth.fallen:
        earth.display(scale)

    # On affiche les boutons
    zoom_input.display()
    time_input.display()

    restart_button.display(surface)
    previous_button.display(surface)
    next_button.display(surface)

    # On affiche le nombre d'essais restants
    font = fonts.getFont(26)
    text = font.render(f"Essais restants : {trials} sur {max_trials}", True, (255, 255, 255))
    surface.blit(text, (36, WINDOW_HEIGHT - text.height - 85))

    # On affiche les pop-up
    if level_end.displayed:
        level_end.display()
    
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
    