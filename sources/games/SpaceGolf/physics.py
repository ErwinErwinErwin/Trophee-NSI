from math import sin, cos, sqrt, atan, pi
from typing import Self

def getDirection(dx: float, dy: float) -> float:
    """
    Retourne une direction correspondant à celle d'un vecteur 2D dont les coordonnées sont dx et dy.

    :param dx: Coordonnée/mouvement x
    :type dx: float
    :param dy: Coordonnée/mouvement y
    :type dy: float
    :return: Une direction
    :rtype: rad
    """
    if dx == 0:
        return pi/2 if dy > 0 else -pi/2
    direction = atan(dy / dx)
    if dx < 0:
        if direction > 0:
            direction -= pi
        else:
            direction += pi
    return direction


class Vector:

    def __init__(self, coordinates: tuple = None, magnitude: float = None, direction: float = None):
        """
        Retourne un objet représentant un vecteur 2D soit à partir de sa direction et norme, soit à partir de ses coordonnées. 
        Si les 2 informations sont données, les coordonnées sont prioritaires. 
        Si aucune n'est donné, un vecteur nul est retourné.

        :param coordinates: Coordonnées du vecteur
        :type coordinates: tuple[float, float]
        :param magnitude: Norme du vecteur, va de pair avec la direction
        :type magnitude: float
        :param direction: Direction du vecteur (rad), va de pair avec la norme
        :type direction: float
        """
        self.magnitude = magnitude
        self.direction = direction
        if coordinates:
            self.coordinates = coordinates
        if not (self.magnitude != None and self.direction != None):
            self.magnitude = 0
            self.direction = 0
    
    @property
    def x(self) -> float:
        return self.magnitude * cos(self.direction)
    
    @property
    def y(self) -> float:
        return self.magnitude * sin(self.direction)
    
    @property
    def coordinates(self) -> tuple:
        return self.x, self.y
    
    @coordinates.setter
    def coordinates(self, xy: tuple | list):
        self.direction = getDirection(*xy)
        self.magnitude = sqrt(xy[0]**2 + xy[1]**2)
    
    def sum(self, *vectors: Self) -> Self:
        """
        Fait la somme du vecteur self et de tous les autres vecteurs passés en paramètre à la suite 
        et renvoie un nouvel objet Vector.

        :param vectors: Les vecteurs à additionner
        :type vectors: Vector
        :return: Un nouvel objet Vector
        :rtype: Vector
        """
        sum_x = self.x + sum(vector.x for vector in vectors)
        sum_y = self.y + sum(vector.y for vector in vectors)
        return Vector((sum_x, sum_y))
    
    def __add__(self, other: Self) -> Self:
        # Méthode spéciale (appelée dunder method) qui permet d'additioner des objets
        return self.sum(other)

    def __mul__(self, product: float) -> Self:
        # Dunder qui permet de multiplier un objet par un nombre
        return Vector((self.x*product, self.y*product))
        

class CelestialBody:
    """
    Cette class représente un astre et permet de calculer les forces qui s'exercent sur celui-ci 
    et d'en déduire son accélération ainsi que sa vitesse en utilisant la 2e loi de Newton et le 
    calcul de la force gravitationelle.
    """

    def __init__(self, x: int, y: int, weight: float):
        """
        :param x: Abscisse de l'astre (en m)
        :type x: int
        :param y: Ordonnée de l'astre (en m)
        :type y: int
        :param weight: Masse de l'astre (en kg)
        :type weight: int
        """
        self.x = x
        self.y = y
        self.weight = weight
        self.other_bodies = []
        self.acceleration = Vector()  # Vecteur accélération en m/s^2
        self.speed = Vector()  # Vecteur vitesse en m/s
    
    def stop(self) -> None:
        """
        Remet à zéro la vitesse et l'accélération de l'astre.
        """
        self.acceleration.magnitude = 0
        self.speed.magnitude = 0
    
    def addInteraction(self, body: Self) -> None:
        self.other_bodies.append(body)
    
    def calculateForce(self, body) -> Vector:
        # On utilise le calcul de la force gravitationnelle
        dx = body.x - self.x
        dy = body.y - self.y
        distance = sqrt(dx**2 + dy**2)
        value = 6.6743e-11 * self.weight * body.weight / distance**2
        return Vector(magnitude=value, direction=getDirection(dx, dy))
    
    def calculateForces(self, bodies: tuple | list) -> Vector:
        """
        Retourne la somme des forces s'exerçant sur cet astre à partir de 
        la liste d'astres bodies.

        :param bodies: Les astres intéragissant avec celui-ci
        :type bodies: tuple[CelestialBody] | list[celestialBody]
        :return: Un vecteur force
        :rtype: Vector
        """
        if len(bodies) == 0:
            return Vector()  # Vecteur nul
        # On calcule la force que chaque astre dans bodies exerce sur cet astre et on fait la somme
        return Vector.sum(*(self.calculateForce(body) for body in bodies))
    
    def calculateAcceleration(self) -> None:
        sum_forces = self.calculateForces(self.other_bodies)
        # D'après la 2e loi de Newton : l'accélération est le quotient de la somme des forces par la masse
        # De plus le vecteur de la somme des forces a la même direction que le vecteur accélération
        self.acceleration.direction = sum_forces.direction
        self.acceleration.magnitude = sum_forces.magnitude / self.weight
    
    def move(self, dt: float) -> None:
        """
        Calcule les forces s'exerçant sur l'astre, son accélération et sa vitesse puis actualise sa position.

        :param dt: Temps écoulé entre chaque appel de la fonction (s)
        :type dt: float
        """
        self.calculateAcceleration()
        # Le vecteur variation de vitesse est le produit du vecteur accélération et du temps
        speed_variation = self.acceleration * dt
        # Le vecteur vitesse actuelle est la somme du vecteur vitesse précédent et du vecteur variation de vitesse
        self.speed += speed_variation
        # On actualise la position à partir de la vitesse et du temps écoulé depuis le dernier appel de la fonction
        self.x += self.speed.x * dt
        self.y += self.speed.y * dt
