"""
Ce fichier contient toutes les fonctions utilitaires du programme.
Certaines de ces fonctions peuvent être utilisées par les mini-jeux en configurant la clé 'utils' du fichier 'config.json' puis
en les récupérant via le paramètre 'utils' de la fonction 'load' du mini-jeu (voir l'exemple 'template')
"""

from os import scandir, path
from json import load
import pygame

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


# Définition des class utilisées dans les fonctions utilitaires

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
        

# Fonctions utilitaires disponibles pour les mini-jeux

def loadAssetsFolder(assets: dict, folder_path: str) -> None:
    """
    loadAssetsFolder va scanner récursivement tous les sous dossiers de dossier passé en paramètre et charger toutes les images, les sons et les polices qui s'y trouvent.
    
    :param assets: Le dictionnaire qui va contenir l'arborescence du dossier scanné, les sous dossiers étant des dictionnaires, 
    les images des objets pygame.Surface, les sons des objets pygame.mixer.Sound et les polices des objets pygame.font.Font
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
