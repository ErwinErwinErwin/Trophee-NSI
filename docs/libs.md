## Introduction
Cette documentation vise à expliquer l'utilisation de chacun des modules python utilisé dans ce projet, leur implication, et la raison de leurs choix.

**Pour rappel, voici la liste des librairies utilisées:**
- `pygame-ce`
- `PyOpenGL`
- `PyOpenGL_accelerate`
- `numpy`

---
### Pygame-ce
La librairie Pygame-ce (Pygame community edition) est très semblable à la librairie Pygame mais rajoute quelques fonctions utiles. Pygame permet initialement de faire de simple jeux/graphiques 2D, avec un système d'event assez complet, l'un des défauts étant néanmoins qu'elle ne prend aucunement (ou infiniment peu) en charge le GPU (perte de puissance crucial pour de la simulation physique de grande envergure), ou encore que le model de rendu est en mode "Immediate". 

**Notes sur le mode "Immediate";**\
c'est le fait que rien de ce qui est affiché est stocké en mémoire (=> dans le sens, le fait qu'il doit être affiché et comment), vous devez alors redessiner tout à chaque frame, même sans changement.

Par exemple:
```py
while running:
    screen.fill((0, 0, 0))          # Vous videz l'écran
    # Vous devez alors redessiner tout ce que vous voulez, même si rien ne bouge (c'est le cas dans cet exemple)
    pygame.draw.rect(screen, (255, 0, 0), (100, 100, 50, 50))
    # Vous affichez vos modifications, mais si vous ne ré-indiquez pas à pygame l'instruction ci dessus plus rien ne sera affiché.
    pygame.display.flip()
```

---
### Numpy
Numpy n'est ici utilisé que pour ses avantages par rapport à la librairie math standard de python, et aussi pour ses abilités à gérer les matrices.
