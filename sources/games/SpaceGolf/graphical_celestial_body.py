from .physics import CelestialBody
from pygame import Surface, transform
from typing import Callable
from utils import SpriteSheet

class GraphicalCelestialBody(CelestialBody):

    def __init__(self, x: int, y: int, mass: float, radius: int, image: Surface | SpriteSheet, surface: Surface, getPosition: Callable[[int, int], tuple[int, int]]):
        """
        Class héritant de CelestialBody et ajoutant des propriétés graphiques pour le rendu de l'astre.

        :param x: Abscisse de l'astre (en m)
        :type x: int
        :param y: Ordonnée de l'astre (en m)
        :type y: int
        :param mass: Masse de l'astre (en kg)
        :type mass: float
        :param radius: Rayon de l'astre (en m)
        :type radius: int
        :param image: Image de l'astre pour le rendu (peut être animée)
        :type image: pygame.Surface | utils.SpriteSheet
        :param surface: Surface sur laquelle afficher l'astre
        :type surface: pygame.Surface
        :param getPosition: Fonction permettant de convertir les coordonnées absolues (en m) en coordonnées relatives à l'écran (en px)
        :type getPosition: Callable[[int, int], tuple[int, int]]
        """
        super().__init__(x, y, mass, radius)
        self.original_image = image
        self.animated = isinstance(image, SpriteSheet)
        # Dictionnaire d'images de différentes tailles pour l'adaptation au zoom
        self.images: dict[int, Surface | list[Surface]] = {}
        self.angle = 0  # Angle de rotation de l'image en degrés
        self.surface = surface
        self.getPosition = getPosition
    
    def display(self, scale: int) -> None:
        """
        Affiche l'astre à sa position actuelle en prenant en compte la rotation de son image.

        :param scale: Échelle du rendu (en m/px)
        :type scale: int
        """
        x, y = self.getPosition(self.x, self.y)
        if self.animated:
            if scale in self.images:
                images = self.images[scale]
            else:
                images = [None] * len(self.original_image.frames)
                self.images[scale] = images
            current_frame = self.original_image.getCurrentSprite()
            frame = self.original_image.frame
            image = images[frame]
            if image is None:
                image = transform.scale_by(current_frame, self.radius*2 / scale / current_frame.width)
                images[frame] = image
        else:
            if scale in self.images:
                image = self.images[scale]
            else:
                image = transform.scale_by(self.original_image, self.radius*2 / scale / self.original_image.width)
                self.images[scale] = image
        if self.angle != 0:
            image = transform.rotate(image, self.angle)
        self.surface.blit(image, (x - image.width//2, y - image.height//2))
