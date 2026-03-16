"""
Ce fichier contient toutes les fonctions utilitaires du programme.
Certaines de ces fonctions peuvent être utilisées par les mini-jeux en configurant la clé 'utils' du fichier 'config.json' puis
en les récupérant via le paramètre 'utils' de la fonction 'load' du mini-jeu (voir l'exemple 'template')
"""

from os import scandir, path
from json import load
import pygame
from typing import Callable
from time import time
from re import search

# Fonctions uniquement utilisées par le script main.py

def loadGame(folder: str, folder_path: str) -> dict | None:
    """
    Docstring for loadGame
    
    :param folder: Nom du dossier du mini-jeu
    :type folder: str
    :param folder_path: Chemin absolu du dossier contenant ce script
    :type folder_path: str
    :return: Un dictionnaire contenant les 5 fonctions `tick`, `display`, `events`, `init` et `load` ainsi que le contenu de
    'config.json' ou None s'il manquait des données
    :rtype: dict | None
    """
    game = {"loaded": False}
    
    # On ouvre le fichier config.json du mini-jeu pour récupérer son contenu
    with open(path.join(folder_path, "games", folder, "config.json"), "r") as f:
        game["config"] = load(f)
    
    # On vérifie que toutes les clés nécessaires existes
    NEEDED_KEYS = ("name", "description", "simulation_speed", "keys", "width", "height")
    if not all(key in game["config"] for key in NEEDED_KEYS):
        return None

    # On charge l'arrière-plan affiché dans le menu des mini-jeux
    game["menu_background"] = pygame.image.load(path.join(folder_path, "games", folder, "menu_background.png")).convert()
    
    # On importe dynamiquement les fonctions principales du fichier game.py
    module = __import__(f"games.{folder}.game", fromlist=["tick", "display", "events", "init", "load"])
    
    # On stocke les 4 fonctions principales dans le dictionnaire
    try:
        game["tick"] = module.tick
        game["display"] = module.display
        game["events"] = module.events
        game["init"] = module.init
        game["load"] = module.load
    except AttributeError:
        return None
    return game


# Définition des class

class LoadedFont:
    """
    LoadedFont représente une police chargée à partir d'un fichier .ttf. 
    Elle permet de générer facilement un objet pygame.font.Font avec la taille désirée.
    """
    
    def __init__(self, filepath: str) -> None:
        
        # On gère les cas d'erreurs
        if not path.exists(filepath):
            raise FileNotFoundError
        
        self.filepath = filepath
        self.sizes = {}
    
    def getFont(self, size: int) -> pygame.font.Font:
        """
        getFont renvoie un objet Font de la taille désirée.
        
        :param size: La taille de la police
        :type size: int
        :return: La police de la taille désirée
        :rtype: pygame.font.Font
        """
        # Si la taille demandée à déjà été chargée on la renvoie
        if size in self.sizes:
            return self.sizes[size]
        
        font = pygame.font.Font(self.filepath, size)
        self.sizes[size] = font
        return font


class SpriteSheet:
    
    def __init__(self, image: pygame.Surface, sprite_width: int, animation_speed: float = 1.0) -> None:
        """
        SpriteSheet représente une image animée.

        :param image: L'image horizontale contenant les sprites
        :type image: pygame.Surface
        :param sprite_width: La largeur de chaque sprite (en px)
        :type sprite_width: int
        :param animation_speed: La vitesse de l'animation (en sprites/s)
        :type animation_speed: float
        """
        self.frames = []
        for x in range(0, image.width, sprite_width):
            self.frames.append(image.subsurface(x, 0, sprite_width, image.height))
        self.animation_speed = animation_speed
        self.frame = 0
        self.last_update = time()

    def getCurrentSprite(self) -> pygame.Surface:
        """
        getCurrentSprite renvoie le sprite actuel de l'animation en fonction du temps écoulé.

        :return: Le sprite actuel de l'animation
        :rtype: pygame.Surface
        """
        now = time()
        if now - self.last_update >= 1 / self.animation_speed:
            self.frame = (self.frame + 1) % len(self.frames)
            self.last_update = now
        return self.frames[self.frame]


class RangeInput:

    def __init__(self, x: int, y: int, width: int, range: tuple, surface: pygame.Surface, title: Callable[[int], str], font: pygame.Font, radius: int, default: float,
                 background_color: tuple = (180, 180, 180), color: tuple = (220, 220, 220), title_color: tuple = (230, 230, 230), title_gap_y: int = 5):
        """
        Cette class permet de facilement créer des entrées numériques avec un bouton à 
        aggriper et défiler à l'horizontal. Les seules méthodes à appeler régulièrement sont 'tick' 
        que le bouton fonctionne et 'display' pour l'afficher.

        :param x: Coté gauche du bouton
        :type x: int
        :param y: Haut du bouton (titre exclus)
        :type y: int
        :param width: Largeur graphique du bouton
        :type width: int
        :param range: Les valeurs que peuvent prendre le bouton (minimum, maximum, pas)
        :type range: tuple[max] | tuple[min, max] | tuple[min, max, pas]
        :param surface: La surface sur laquelle sera dessinée le bouton
        :type surface: pygame.Surface
        :param title: Une fonction qui possède un paramètre value et qui retourne le texte affiché au dessus du bouton
        :type title: function(value: int) -> str
        :param font: Police utilisée pour afficher le titre
        :type font: pygame.Font
        :param radius: Taille du rayon du bouton
        :type radius: int
        :param default: Valeur par défaut
        :type default: int | float
        :param background_color: Couleur de la barre sur laquelle se trouve le bouton
        :type background_color: tuple[r, g, b]
        :param color: Couleur du bouton
        :type color: tuple[r, g, b]
        :param title_color: Couleur du titre
        :type title_color: tuple[r, g, b]
        :param title_gap_y: Espace entre le bas du titre et le haut du bouton
        :type title_gap_y: int
        """
        self.x = x
        self.y = y
        self.width = width
        self.clicked = False
        self.diff_x = 0
        self.title = title
        self.font = font
        self.step = 1
        self.minimum = 0
        self.value = default
        self.surface = surface
        self.radius = radius
        self.is_touching_mouse = False
        self.background_color = background_color
        self.color = color
        self.title_color = title_color
        self.title_gap_y = title_gap_y
        match len(range):
            case 1:
                self.maximum = range[0]
            case 2:
                self.minimum, self.maximum = range
            case 3:
                self.minimum, self.maximum, self.step = range
            case _:
                raise ValueError
        self.range = self.maximum - self.minimum
    
    @property
    def button_x(self) -> int:
        return round((self.value - self.minimum) * self.width / self.range) + self.x
    
    def touchingMouse(self, mouse_pos) -> bool:
        """
        touchingMouse retourne True si le bouton touche la souris sinon False.

        :param mouse_pos: Position de la souris
        :return: True si le bouton touche la souris sinon False
        :rtype: bool
        """
        return (mouse_pos[0] - self.button_x) ** 2 + (mouse_pos[1] - self.y - self.radius) ** 2 <= (self.radius + 2) ** 2
        
    def tick(self, mouse_pos: tuple, click_duration: int) -> None:
        """
        La fonction tick doit être appelée régulièrement afin que le bouton 
        soit fonctionnelle pour l'utilisateur.

        :param mouse_pos: Position de la souris
        :type mouse_pos: tuple[int, int]
        :param click_duration: Durée du clic de la souris
        :type click_duration: int
        """
        self.is_touching_mouse = self.touchingMouse(mouse_pos)
        if self.clicked:
            if click_duration == 0:
                self.clicked = False
                return
            # On calcule la valeur numérique correspondant à la position du bouton
            self.value = (mouse_pos[0] - self.diff_x - self.x) * self.range / self.width + self.minimum
            # On arrondit au pas le plus proche
            self.value = round(self.value / self.step) * self.step
            # On encadre la valeur par le minimum et le maximum
            self.value = min(self.maximum, max(self.minimum, self.value))
        elif click_duration == 1 and self.is_touching_mouse:
            self.clicked = True
            self.diff_x = mouse_pos[0] - self.button_x

    def display(self) -> None:
        """
        Affiche le bouton avec son titre.
        """
        rect = (self.x - self.radius, self.y, self.width + 2 * self.radius, 2 * self.radius)
        pygame.draw.rect(self.surface, self.background_color, rect, border_radius=self.radius)
        color = tuple(min(255, c+20) for c in self.color) if self.is_touching_mouse or self.clicked else self.color
        pygame.draw.circle(self.surface, color, (self.button_x, self.y + self.radius), self.radius + 2)
        title_txt = self.title(self.value)
        title = self.font.render(title_txt, True, self.title_color)
        self.surface.blit(title, (self.x +self.width//2-title.width//2, self.y-title.height-self.title_gap_y))


# Fonctions utilitaires disponibles pour les mini-jeux

def loadAssetsFolder(assets: dict, folder_path: str) -> None:
    """
    loadAssetsFolder va scanner récursivement tous les sous dossiers de dossier passé en paramètre 
    et charger toutes les images, les sons, les polices et les feuilles de sprite qui s'y trouvent.
    
    :param assets: Le dictionnaire qui va contenir l'arborescence du dossier scanné, les sous dossiers 
        étant des dictionnaires, les images des objets pygame.Surface, les sons des objets pygame.mixer.Sound, 
        les polices des objets utils.LoadedFont et les feuilles de sprite des objets utils.SpriteSheet
    :type assets: dict
    :param folder_path: Chemin du dossier à scanner
    :type folder_path: str
    """
    for element in scandir(folder_path):
        if element.is_dir():
            # On créé un nouveau dictionnaire dans le précédent pour représenter le sous dossier puis la fonction s'appelle elle même sur ce sous dossier
            assets[element.name] = {}
            loadAssetsFolder(assets[element.name], element.path)
        else:
            format = path.splitext(element.name)[1]
            if format in (".bmp", ".jpeg", ".jpg", ".png", ".svg", ".webp"):
                try:
                    img = pygame.image.load(element.path)
                    # Les méthodes convert et convert_alpha servent à optimiser l'image afin de l'estampiller plus rapidement
                    if img.get_alpha() != None:  # L'image possède de la transparence
                        img = img.convert_alpha()
                    else:
                        img = img.convert()
                    match = search(r"\[SPRITESHEET;(\d+)\]", element.name)
                    if match:
                        width = int(match.group(1))
                        assets[element.name] = SpriteSheet(img, width)
                    else:
                        assets[element.name] = img
                except:
                    print(f"[Erreur] Impossible de charger l'image '{element.path}'")
            elif format in (".mp3", ".wav", ".ogg"):
                try:
                    assets[element.name] = pygame.mixer.Sound(element.path)
                except:
                    print(f"[Erreur] Impossible de charger l'image '{element.path}'")
            elif format == ".ttf":
                try:
                    assets[element.name] = LoadedFont(element.path)
                except:
                    print(f"[Erreur] Impossible de charger la police '{element.path}'")
