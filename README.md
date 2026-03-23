# Physics.play

Physics.play est un jeu vidéo qui vous propose de jouer à des mini-jeux ou sandbox pour vous faire découvrir le monde de la physique du quotidien , le tout avec une simulation la plus fidèle possible, utilisant des algorithmes avancés pour vous proposer un résultat balancé entre réalisme et visuel

---

## ⚒️ Pré-requis

### Configuration logicielle minimale
- **OS:** Windows ≥ 10 || Linux (testé sur une version du kernel ≥ 6)
- **Python:** `≥ 3.12`
- **Modules:** Voir `requirements.txt` (ou [Installation](#installation))

### Configuration hardware minimale
Pour la majorité des mini-jeux, une configuration minimum n'est pas recommandée car ils devraient tourner sur un peu près toutes les plateformes modernes.

Il est à noter que pour faire tourner la simulation "WaterBox" la recommendation suivante est a prendre en compte pour une experience optimale;

| #          	| Minimum                          	| Recommendation                         	|
|------------	|----------------------------------	|----------------------------------------	|
| Processeur 	| `Intel i3-3100` / `AMD Ryzen 3 1200` 	| `Intel Core i5-10400` / `AMD Ryzen 5 3600` 	|

Ces recommendations sont basées sur l'idée de pouvoir faire tourner la simulation à 500-600 particules dans des conditions de stabilité totale, elles sont dû principalement à la nature single-core, et surtout dans notre cas au fait que les shaders OpenGL en GLSL sont hors programme. Les choix des processeurs sont dû à leurs haute fréquence et à leurs cache qui permet de faire tourner la boucle à un nombre de TPS plus élevé.

### Installation
Pour le bon fonctionnement du programme, plusieurs librairies sont nécessaires, pour les installer, deux scripts sont fournis;

🐧**Debian (ou debian-based distros)**\
-> Bash/ZSH: `chmod +x install.sh && ./install.sh`\

-> Fish: `chmod +x install.fish && ./install.fish`\
L'un des developpeurs utilise un shell fish, c'était pour lui faire plaisir :)

**Windows (10+)**\
-> Invite de commande `./install.bat`


## ▶️ Démarrage 
Pour lancer le programme, il vous suffit d'executer le fichier `./sources/main.py` avec les [prérequis](#️-pré-requis) installés.

**Si vous avez utilisez le script d’installation**
- **Linux:**
  - Bash/ZSH: `source ./.venv/bin/activate && python3 ./sources/main.py`
  - Fish: `source ./.venv/bin/activate.fish && python3 ./sources/main.py`


- **Windows** `.venv\Scripts\python.exe sources\main.py`



## Auteurs
Le projet a été réalisé par un groupe de quatres élèves de première, tous passionnés d'informatique.

**Maxime Noé -** Développement du système de gestion des mini-jeux ainsi que des minijeux/sandbox "SpaceGolf" et le "Conway Game of Life"

**Lubin Tschirhart -** Rédaction des documents et documentations du dossier technique, ainsi que le développement la sandbox "WaterBox"

**Line Vacher--Drevet -** Aide  à l'organisation du dossier, réalisations graphiques et aide au design et concept des jeux.

**Erwan Goasdoue -** Supervision graphique du projet, aide au design, et responsable des tests.

## 🔏 License

Ce projet est sous licence GPL-3.0 - voir le fichier [LICENSE](LICENSE) pour plus d'informations
