"""
Implémentation du modèle SPH (Smoothed Particle Hydrodynamics) pour simuler des fluides dans le jeu WaterMaze
"""

import pygame
import math
from random import randint


class SPHParticle:
    """Représente une particule seul dans la simulation"""

    def __init__(self, x, y, mass=1.0, radius=3.0)-> None:
        self.position :pygame.Vector2 = pygame.Vector2(x, y)
        self.velocity :pygame.Vector2 = pygame.Vector2(0, 0)
        self.acceleration :pygame.Vector2 = pygame.Vector2(0, 0)
        self.mass = mass
        self.radius = radius
        self.density = 1.0
        self.pressure = 0.0
        self.color = (41, 220, 214)  # Cyan

    def reset_acceleration(self)-> None:
        """Remet l'acceleration à 0"""
        self.acceleration = pygame.Vector2(0, 0)

    def apply_force(self, force)-> None:
        """Applique une force à une particule"""
        self.acceleration += force / self.density
        # 2nd loi de Newton: F = ma

    def update(self, dt, gravity)-> None:
        """Met à jour la position de la particule en fonction de delta temps et de la gravité"""
        self.acceleration += gravity
        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt
        self.acceleration = pygame.Vector2(0, 0) #Remet à 0 l'acceleration pour le prochain tick

    def draw(self, surface, camera_x, camera_y)-> None:
        """Dessine une particule sur une surface avec l'offset de la caméra"""
        draw_x = int(self.position.x - camera_x) #Position sur l'écran en x
        draw_y = int(self.position.y - camera_y) #en y


        """Le rendu est fait sur tout l'écran visible avec un offset de 50 pour éviter tout effet de 'pop' lors du déplacement"""
        if -50 < draw_x < surface.get_width() + 50 and -50 < draw_y < surface.get_height() + 50:
            pygame.draw.circle(surface, self.color, (draw_x, draw_y), int(self.radius))
            
    def update_spatial_disc(self, spatial_lookup):
        spatial_lookup


class SPHSimulation:
    """Modèle d'implementation du système SPH"""

    def __init__(self, width=1600, height=900, particle_count=100)-> None:
        self.width = width
        self.height = height
        self.particles = []
        self.gravity = pygame.Vector2(0, 9.81)  # pixels/s²

        # Param de la sim
        self.smoothing_radius = 30.0 # Le rayon de dégradé
        self.rest_density = 0.0001 # La densité de repo
        self.gas_stiffness = 400 # La densité du gaz ambient
        self.viscosity = 0.2 # La viscosité du liquide
        self.surface_tension = 0.0728 # La tension de surface
        self.damping = 0.995
        
        #separation de l'espace
        
        self.Y_S = int(height/self.smoothing_radius)
        self.X_S = int(width/self.smoothing_radius)
        
        self.spatial_lookup={}
        


        #spatial operations
        self.operation = [
            (0,0),
            (1,0),
            (0,1),
            (1,-1),
            (-1,1),
            (-1,-1),
            (1,1),
            (-1,0),
            (0,-1)
            
        ]
        
        # Initialise les particules
        self._initialize_particles(particle_count)
        
        
        #Constants
        self.GRADIENT_FACTOR = -30 / (math.pi * self.smoothing_radius**5)
        
        self.KERNEL_FACTOR = 4 / (math.pi * self.smoothing_radius**8)


    
    def _initialize_particles(self, count:int)-> None:
        """Créer une population de particule dans une petite région

        Args:
            count (int): nombre de particules
        """
        

        particles_per_row = int(math.sqrt(count))
        spacing = 29.99999
        start_x = self.width // 2 - (particles_per_row * spacing) // 2
        start_y = self.height // 4 

        for i in range(particles_per_row):
            for j in range(particles_per_row):
                x = start_x + i * spacing
                y = start_y + j * spacing
                new_particle=SPHParticle(x, y)
                self.particles.append(new_particle)
                
                #ajouter au spatial lookup
                cell = (int(x/self.smoothing_radius),int(y/self.smoothing_radius))
                if not cell in self.spatial_lookup:
                    self.spatial_lookup[cell]=[]
                
                self.spatial_lookup[cell].append(new_particle)
                

    def _kernel(self, distance, h)->int:
        """Cette fonction retourne l'influence (W) d'une particule à une distance donnée dans un rayon d'influence h
        Poly6 kernel 2d

        Args:
            distance (int): distance
            h (int): rayon d'influence

        Returns:
            int: la valeur 
        """
        if distance >= h: # Si la particule est hors du rayon
            return 0.0

        term = h * h - distance * distance
        return self.KERNEL_FACTOR * (term ** 3)

    def _kernel_gradient(self, r:pygame.Vector2, h)->pygame.Vector2:
        """Fonction qui retourne la valeur de gradient pour une distance donnée avec un rayon d'influence h
        Spiky kernel 2d, gradient

        Args:
            r (Vector2): Le vecteur de déplacement de la particule
            h (int): Le rayon d'influence 

        Returns:
            int: La valeur de gradient
        """

        term = h - r.length()
        return self.GRADIENT_FACTOR * (r/r.length()) * (term ** 2)

    def _calculate_densities(self)-> None:
        """Met à jour les densités de chaque particule de la simulation
        """
        h = self.smoothing_radius

        
        
        for particle in self.particles:
            particle.density = 0.0
            idx=int(particle.position.x/h),int(particle.position.y/h)

            for opp in self.operation:
                for other in self.spatial_lookup.get((idx[0]+opp[0],idx[1]+opp[1]), []):
                    distance = particle.position.distance_to(other.position)
                    particle.density += other.mass * self._kernel(distance, h)

            



    def _calculate_pressures(self):
        """Calcule la pression de chaque particule à  partir de sa densité"""
        for particle in self.particles:
            particle.pressure = self.gas_stiffness*(particle.density-self.rest_density)

    def _calculate_apply_forces(self,dt):
        """Calcule les forces appliquées à chaque particules et les appliquent"""
        h = self.smoothing_radius

        #Remet à 0 le dictionnaire d'optimisation spatiale
        self.spatial_lookup.clear()
        
        for particle in self.particles:
            pressure_force = pygame.Vector2(0, 0)
            viscosity_force = pygame.Vector2(0, 0)

            
            for other in self.particles:
                if particle is other:
                    continue

                diff = particle.position - other.position
                distance = diff.length()

                if distance < h and distance > 0.001: #Empêche les particules de rentrer en collision totale
                    # Pressure force
                    pressure_component = (
                        -(other.mass * (particle.pressure + other.pressure) /
                          (2.0 * other.density)) *
                        self._kernel_gradient(diff, h)
                    )

                

                    pressure_force += pressure_component

                    # Viscosity force
                    velocity_diff = other.velocity - particle.velocity
                    viscosity_component = (
                        self.viscosity * other.mass / other.density *
                        self._kernel(distance, h)
                    )
                    viscosity_force += velocity_diff * viscosity_component
                    


            particle.apply_force(pressure_force)
            particle.apply_force(viscosity_force)
            
            particle.update(dt, self.gravity)
            particle.velocity *= self.damping
            

            
    
    def _update_spatial_lookup(self):
        for particle in self.particles:
            cell = ((int(particle.position.x/self.smoothing_radius),int(particle.position.y/self.smoothing_radius)))
            
            if not cell in self.spatial_lookup:
                self.spatial_lookup[cell]=[]
            self.spatial_lookup[cell].append(particle)


    def _boundary_handling(self):
        """Prend en charge les collision des particules entre les bords de la simulation"""
        damping = 0.60
        border = 10.0

        for particle in self.particles:
            # Gauche
            if particle.position.x < border:
                particle.position.x = border
                particle.velocity.x *= -damping

            # Droite
            if particle.position.x > self.width - border:
                particle.position.x = self.width - border
                particle.velocity.x *= -damping

            # Haut
            if particle.position.y < border:
                particle.position.y = border
                particle.velocity.y *= -damping

            # Bas
            if particle.position.y > self.height - border:
                particle.position.y = self.height - border
                particle.velocity.y *= -damping

   
    def step(self, dt)-> None:
        """Execute un step de la simulation"""
        
        
        self.spatial_lookup.clear()
        self._update_spatial_lookup()
        
        if not self.particles:
            return

        # Calcule les densité et pression
        self._calculate_densities()
        self._calculate_pressures()

        # Remet toute les forces et accelerations à 0
        for particle in self.particles:
            particle.reset_acceleration()

        self._calculate_apply_forces(dt) #Calcule et applique les forces



        # Handle boundaries
        self._boundary_handling()


    def add_particle(self, x, y):
        """Ajoute une nouvelle particule"""
        self.particles.append(SPHParticle(x, y))

    def draw(self, surface, camera_x, camera_y):
        """Dessine toutes les particules"""
        for particle in self.particles:
            particle.draw(surface, camera_x, camera_y)

    def get_particle_count(self):
        """Retourne le nombre de particules"""
        return len(self.particles)
